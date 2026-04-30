"""fix order reviews primary key

Revision ID: 5e36276d89e9
Revises: ad4800dd0318
Create Date: 2026-04-30 18:22:29.158577

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5e36276d89e9"
down_revision: str | Sequence[str] | None = "ad4800dd0318"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("order_reviews_pkey", "order_reviews", type_="primary")
    op.create_primary_key(
        "order_reviews_pkey",
        "order_reviews",
        ["review_id", "order_id"],
    )


def downgrade() -> None:
    op.drop_constraint("order_reviews_pkey", "order_reviews", type_="primary")
    op.create_primary_key(
        "order_reviews_pkey",
        "order_reviews",
        ["review_id"],
    )
