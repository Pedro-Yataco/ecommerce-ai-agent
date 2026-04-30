from __future__ import annotations

import argparse
import asyncio
import csv
import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import asyncpg

from src.db.connection import get_database_settings

logger = logging.getLogger(__name__)


CsvRow = dict[str, str | None]
DbRow = tuple[object, ...]
RowParser = Callable[[CsvRow], DbRow]


@dataclass(frozen=True)
class TableLoadConfig:
    table_name: str
    csv_filename: str
    columns: tuple[str, ...]
    parse_row: RowParser


def _empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None

    stripped = value.strip()
    return stripped if stripped else None


def _parse_int(value: str | None) -> int | None:
    cleaned = _empty_to_none(value)
    return int(cleaned) if cleaned is not None else None


def _parse_decimal(value: str | None) -> Decimal | None:
    cleaned = _empty_to_none(value)
    return Decimal(cleaned) if cleaned is not None else None


def _parse_datetime(value: str | None) -> datetime | None:
    cleaned = _empty_to_none(value)
    if cleaned is None:
        return None

    return datetime.fromisoformat(cleaned)


def _parse_customers(row: CsvRow) -> DbRow:
    return (
        row["customer_id"],
        row["customer_unique_id"],
        _parse_int(row["customer_zip_code_prefix"]),
        row["customer_city"],
        row["customer_state"],
    )


def _parse_sellers(row: CsvRow) -> DbRow:
    return (
        row["seller_id"],
        _parse_int(row["seller_zip_code_prefix"]),
        row["seller_city"],
        row["seller_state"],
    )


def _parse_products(row: CsvRow) -> DbRow:
    return (
        row["product_id"],
        _empty_to_none(row["product_category_name"]),
        _parse_int(row["product_name_lenght"]),
        _parse_int(row["product_description_lenght"]),
        _parse_int(row["product_photos_qty"]),
        _parse_int(row["product_weight_g"]),
        _parse_int(row["product_length_cm"]),
        _parse_int(row["product_height_cm"]),
        _parse_int(row["product_width_cm"]),
    )


def _parse_category_translation(row: CsvRow) -> DbRow:
    return (
        row["product_category_name"],
        row["product_category_name_english"],
    )


def _parse_orders(row: CsvRow) -> DbRow:
    return (
        row["order_id"],
        row["customer_id"],
        row["order_status"],
        _parse_datetime(row["order_purchase_timestamp"]),
        _parse_datetime(row["order_approved_at"]),
        _parse_datetime(row["order_delivered_carrier_date"]),
        _parse_datetime(row["order_delivered_customer_date"]),
        _parse_datetime(row["order_estimated_delivery_date"]),
    )


def _parse_order_items(row: CsvRow) -> DbRow:
    return (
        row["order_id"],
        _parse_int(row["order_item_id"]),
        row["product_id"],
        row["seller_id"],
        _parse_datetime(row["shipping_limit_date"]),
        _parse_decimal(row["price"]),
        _parse_decimal(row["freight_value"]),
    )


def _parse_order_payments(row: CsvRow) -> DbRow:
    return (
        row["order_id"],
        _parse_int(row["payment_sequential"]),
        row["payment_type"],
        _parse_int(row["payment_installments"]),
        _parse_decimal(row["payment_value"]),
    )


def _parse_order_reviews(row: CsvRow) -> DbRow:
    return (
        row["review_id"],
        row["order_id"],
        _parse_int(row["review_score"]),
        _empty_to_none(row["review_comment_title"]),
        _empty_to_none(row["review_comment_message"]),
        _parse_datetime(row["review_creation_date"]),
        _parse_datetime(row["review_answer_timestamp"]),
    )


TABLE_LOAD_ORDER: tuple[TableLoadConfig, ...] = (
    TableLoadConfig(
        table_name="customers",
        csv_filename="olist_customers_dataset.csv",
        columns=(
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ),
        parse_row=_parse_customers,
    ),
    TableLoadConfig(
        table_name="sellers",
        csv_filename="olist_sellers_dataset.csv",
        columns=(
            "seller_id",
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state",
        ),
        parse_row=_parse_sellers,
    ),
    TableLoadConfig(
        table_name="products",
        csv_filename="olist_products_dataset.csv",
        columns=(
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ),
        parse_row=_parse_products,
    ),
    TableLoadConfig(
        table_name="product_category_name_translation",
        csv_filename="product_category_name_translation.csv",
        columns=(
            "product_category_name",
            "product_category_name_english",
        ),
        parse_row=_parse_category_translation,
    ),
    TableLoadConfig(
        table_name="orders",
        csv_filename="olist_orders_dataset.csv",
        columns=(
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ),
        parse_row=_parse_orders,
    ),
    TableLoadConfig(
        table_name="order_items",
        csv_filename="olist_order_items_dataset.csv",
        columns=(
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ),
        parse_row=_parse_order_items,
    ),
    TableLoadConfig(
        table_name="order_payments",
        csv_filename="olist_order_payments_dataset.csv",
        columns=(
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
        ),
        parse_row=_parse_order_payments,
    ),
    TableLoadConfig(
        table_name="order_reviews",
        csv_filename="olist_order_reviews_dataset.csv",
        columns=(
            "review_id",
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
            "review_creation_date",
            "review_answer_timestamp",
        ),
        parse_row=_parse_order_reviews,
    ),
)


def _iter_csv_rows(file_path: Path, parse_row: RowParser) -> Iterable[DbRow]:
    with file_path.open(mode="r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError(f"CSV file has no header: {file_path}")

        normalized_fieldnames = [field.strip() for field in reader.fieldnames]
        reader.fieldnames = normalized_fieldnames

        for row in reader:
            normalized_row = {
                key.strip() if key is not None else key: value
                for key, value in row.items()
            }
            yield parse_row(normalized_row)


def _validate_required_files(data_dir: Path) -> None:
    missing_files = [
        config.csv_filename
        for config in TABLE_LOAD_ORDER
        if not (data_dir / config.csv_filename).exists()
    ]

    if missing_files:
        missing = ", ".join(missing_files)
        raise FileNotFoundError(
            f"Missing required Olist CSV files in {data_dir}: {missing}"
        )


async def _truncate_tables(connection: asyncpg.Connection) -> None:
    table_names = ", ".join(config.table_name for config in reversed(TABLE_LOAD_ORDER))

    logger.info("Truncating existing Olist tables")
    await connection.execute(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE")


async def _load_table(
    connection: asyncpg.Connection,
    data_dir: Path,
    config: TableLoadConfig,
) -> int:
    file_path = data_dir / config.csv_filename
    rows = list(_iter_csv_rows(file_path, config.parse_row))

    logger.info(
        "Loading table %s from %s with %s rows",
        config.table_name,
        config.csv_filename,
        len(rows),
    )

    await connection.copy_records_to_table(
        config.table_name,
        records=rows,
        columns=list(config.columns),
    )

    return len(rows)


async def load_olist_data(data_dir: Path) -> None:
    _validate_required_files(data_dir)

    database_settings = get_database_settings()
    database_url = database_settings.database_url.replace(
        "postgresql+asyncpg://",
        "postgresql://",
    )

    connection = await asyncpg.connect(database_url)

    try:
        async with connection.transaction():
            await _truncate_tables(connection)

            total_rows = 0
            for config in TABLE_LOAD_ORDER:
                total_rows += await _load_table(connection, data_dir, config)

        logger.info("Olist data loaded successfully. Total rows: %s", total_rows)

    finally:
        await connection.close()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load Olist CSV files into PostgreSQL.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/raw/olist"),
        help="Directory containing Olist CSV files.",
    )

    return parser.parse_args()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    args = _parse_args()
    asyncio.run(load_olist_data(args.data_dir))


if __name__ == "__main__":
    main()