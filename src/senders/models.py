import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import CITEXT, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.models import TimestampMixin, UUIDMixin
from src.senders.constants import SenderStatus


class Sender(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "senders"
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_sender_owner_name"),)

    # owner_id scope + CITEXT sur name = un client ne peut jamais utiliser
    # le sender ID d'un autre, même en cas de collision de nom (insensible à la casse).
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(CITEXT(), nullable=False)
    status: Mapped[SenderStatus] = mapped_column(
        Enum(SenderStatus, name="sender_status"),
        default=SenderStatus.PENDING,
        server_default=SenderStatus.PENDING.value,
        index=True,
    )
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
