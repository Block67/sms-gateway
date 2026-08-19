import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.messages.constants import MessageStatus
from src.models import TimestampMixin, UUIDMixin


class Message(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "messages"
    __table_args__ = (
        # Index composite pour la requête la plus fréquente : "mes messages,
        # les plus récents d'abord" (pagination du dashboard client).
        Index("ix_messages_owner_created_at", "owner_id", "created_at"),
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    sender_name: Mapped[str] = mapped_column(String(11))
    to_number: Mapped[str] = mapped_column(String(20), index=True)
    text: Mapped[str] = mapped_column(Text())
    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus, name="message_status"),
        default=MessageStatus.QUEUED,
        server_default=MessageStatus.QUEUED.value,
        index=True,
    )
    price: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    pages: Mapped[int] = mapped_column(Integer())
    operator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("operators.id", ondelete="SET NULL"), nullable=True
    )
    provider_message_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    dlr_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[str | None] = mapped_column(Text(), nullable=True)
