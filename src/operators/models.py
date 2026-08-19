from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.models import TimestampMixin, UUIDMixin


class Operator(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "operators"
    __table_args__ = (UniqueConstraint("prefix", name="uq_operator_prefix"),)

    prefix: Mapped[str] = mapped_column(String(15), index=True)
    country_iso: Mapped[str] = mapped_column(String(2))
    mcc: Mapped[str] = mapped_column(String(3))
    mnc: Mapped[str] = mapped_column(String(3))
    name: Mapped[str] = mapped_column(String(100))
