"""add cartproducts.rank

Revision ID: 77d5a369b1da
Revises: 200f1c0b3617
Create Date: 2022-05-11 21:17:06.006610

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func

from groceryaid.db import cartproducts, products

# revision identifiers, used by Alembic.
revision = "77d5a369b1da"
down_revision = "200f1c0b3617"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "cartproducts",
        sa.Column("rank", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )
    op.alter_column("cartproducts", "rank", server_default=None)
    inner_select = (
        sa.select(
            [
                cartproducts.c.storevisit_id,
                cartproducts.c.product_id,
                func.row_number().over(
                    partition_by=cartproducts.c.storevisit_id, order_by=products.c.ean
                ),
            ]
        )
        .select_from(cartproducts.join(products))
        .subquery()
    )
    update_stmt = (
        cartproducts.update()
        .values(rank=inner_select.c[2])
        .where(
            cartproducts.c.storevisit_id == inner_select.c.storevisit_id,
            cartproducts.c.product_id == inner_select.c.product_id,
        )
    )
    op.execute(update_stmt)
    op.drop_constraint("cartproducts_pkey", "cartproducts")
    op.create_primary_key(
        "cartproducts_pkey", "cartproducts", ["storevisit_id", "rank"]
    )


def downgrade():
    op.drop_constraint("cartproducts_pkey", "cartproducts")
    op.create_primary_key(
        "cartproducts_pkey", "cartproducts", ["storevisit_id", "product_id"]
    )
    op.drop_column("cartproducts", "rank")
