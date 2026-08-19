"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-19

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

sender_status = postgresql.ENUM("pending", "active", "rejected", "suspended", name="sender_status")
message_status = postgresql.ENUM(
    "queued", "submitted", "sent", "delivered", "undelivered", "rejected", "programmed",
    name="message_status",
)


def upgrade() -> None:
    # CITEXT permet une comparaison de sender.name insensible à la casse
    # directement au niveau de l'index unique (owner_id, name) — pas besoin
    # de LOWER()/ILIKE côté application.
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")

    bind = op.get_bind()
    sender_status.create(bind, checkfirst=True)
    message_status.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("api_key", sa.String(64), nullable=False),
        sa.Column("balance", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("is_test", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_api_key", "users", ["api_key"], unique=True)

    op.create_table(
        "operators",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("prefix", sa.String(15), nullable=False),
        sa.Column("country_iso", sa.String(2), nullable=False),
        sa.Column("mcc", sa.String(3), nullable=False),
        sa.Column("mnc", sa.String(3), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
    )
    op.create_index("ix_operators_prefix", "operators", ["prefix"], unique=True)

    op.create_table(
        "senders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", postgresql.CITEXT(), nullable=False),
        sa.Column("status", sender_status, nullable=False, server_default="pending"),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.UniqueConstraint("owner_id", "name", name="uq_sender_owner_name"),
    )
    op.create_index("ix_senders_owner_id", "senders", ["owner_id"])
    op.create_index("ix_senders_status", "senders", ["status"])

    op.create_table(
        "user_prices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("operators.id", ondelete="CASCADE"), nullable=False),
        sa.Column("price", sa.Numeric(10, 4), nullable=False),
        sa.UniqueConstraint("user_id", "operator_id", name="uq_price_user_operator"),
    )
    op.create_index("ix_user_prices_user_id", "user_prices", ["user_id"])

    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_name", sa.String(11), nullable=False),
        sa.Column("to_number", sa.String(20), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("status", message_status, nullable=False, server_default="queued"),
        sa.Column("price", sa.Numeric(10, 4), nullable=False),
        sa.Column("pages", sa.Integer(), nullable=False),
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("operators.id", ondelete="SET NULL"), nullable=True),
        sa.Column("provider_message_id", sa.String(64), nullable=True),
        sa.Column("dlr_url", sa.String(500), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
    )
    op.create_index("ix_messages_owner_id", "messages", ["owner_id"])
    # Index composite pour la pagination "mes messages, plus récents d'abord".
    op.create_index("ix_messages_owner_created_at", "messages", ["owner_id", "created_at"])
    op.create_index("ix_messages_status", "messages", ["status"])
    op.create_index("ix_messages_to_number", "messages", ["to_number"])
    op.create_index("ix_messages_provider_message_id", "messages", ["provider_message_id"])

    op.execute(
        """
        CREATE VIEW daily_message_stats AS
        SELECT
            date_trunc('day', created_at)::date AS day,
            sender_name,
            status,
            COUNT(*) AS total,
            SUM(pages) AS total_pages,
            SUM(price * pages) AS total_amount
        FROM messages
        GROUP BY date_trunc('day', created_at), sender_name, status
        ORDER BY day DESC
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS daily_message_stats")
    op.drop_table("messages")
    op.drop_table("user_prices")
    op.drop_table("senders")
    op.drop_table("operators")
    op.drop_table("users")
    sender_status.drop(op.get_bind(), checkfirst=True)
    message_status.drop(op.get_bind(), checkfirst=True)
