"""empty message

Revision ID: 8527b528c4c0
Revises: e633b396cec6
Create Date: 2021-08-24 16:41:03.980828

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "8527b528c4c0"
down_revision = "e633b396cec6"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("employee", sa.Column("auth_service_id", UUID()))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("employee", "auth_service_id")
    # ### end Alembic commands ###
