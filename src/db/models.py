from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.connection import Base


class Customer(Base):
    """Olist customers dataset."""

    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    customer_unique_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    customer_zip_code_prefix: Mapped[int | None] = mapped_column(Integer, nullable=True)
    customer_city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    customer_state: Mapped[str | None] = mapped_column(String(2), nullable=True)

    orders: Mapped[list["Order"]] = relationship(back_populates="customer")


class Seller(Base):
    """Olist sellers dataset."""

    __tablename__ = "sellers"

    seller_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    seller_zip_code_prefix: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seller_city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    seller_state: Mapped[str | None] = mapped_column(String(2), nullable=True)

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="seller")


class Product(Base):
    """Olist products dataset."""

    __tablename__ = "products"

    product_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    product_category_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    product_name_lenght: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_description_lenght: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_photos_qty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_weight_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_length_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_width_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")


class Order(Base):
    """Olist orders dataset."""

    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    customer_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("customers.customer_id"),
        nullable=False,
        index=True,
    )
    order_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    order_purchase_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True
    )
    order_approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    order_delivered_carrier_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    order_delivered_customer_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    order_estimated_delivery_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")
    payments: Mapped[list["OrderPayment"]] = relationship(back_populates="order")
    reviews: Mapped[list["OrderReview"]] = relationship(back_populates="order")


class OrderItem(Base):
    """Olist order items dataset."""

    __tablename__ = "order_items"

    order_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("orders.order_id"),
        primary_key=True,
    )
    order_item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("products.product_id"),
        nullable=False,
        index=True,
    )
    seller_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("sellers.seller_id"),
        nullable=False,
        index=True,
    )
    shipping_limit_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    freight_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")
    seller: Mapped["Seller"] = relationship(back_populates="order_items")


class OrderPayment(Base):
    """Olist order payments dataset."""

    __tablename__ = "order_payments"

    order_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("orders.order_id"),
        primary_key=True,
    )
    payment_sequential: Mapped[int] = mapped_column(Integer, primary_key=True)
    payment_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    payment_installments: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payment_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    order: Mapped["Order"] = relationship(back_populates="payments")


class OrderReview(Base):
    """Olist order reviews dataset."""

    __tablename__ = "order_reviews"

    review_id: Mapped[str] = mapped_column(String, primary_key=True)
    order_id: Mapped[str] = mapped_column(
        ForeignKey("orders.order_id"),
        primary_key=True,
    )
    review_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    review_comment_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_comment_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_creation_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    review_answer_timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    order: Mapped["Order"] = relationship(back_populates="reviews")


class ProductCategoryNameTranslation(Base):
    """Olist product category translation dataset."""

    __tablename__ = "product_category_name_translation"

    product_category_name: Mapped[str] = mapped_column(String(120), primary_key=True)
    product_category_name_english: Mapped[str | None] = mapped_column(String(120), nullable=True)
