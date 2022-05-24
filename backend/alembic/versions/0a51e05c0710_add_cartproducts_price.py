"""add cartproducts.price

Revision ID: 0a51e05c0710
Revises: 77d5a369b1da
Create Date: 2022-06-02 11:32:33.401597

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0a51e05c0710"
down_revision = "77d5a369b1da"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "cartproducts",
        sa.Column("price", sa.DECIMAL(precision=4, scale=2), nullable=True),
    )
    op.alter_column(
        "cartproducts", "quantity", existing_type=sa.INTEGER(), nullable=True
    )


def downgrade():
    op.alter_column(
        "cartproducts", "quantity", existing_type=sa.INTEGER(), nullable=False
    )
    op.drop_column("cartproducts", "price")
