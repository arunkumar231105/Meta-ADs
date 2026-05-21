import uuid
from typing import Optional, List
from sqlalchemy import String, Text, Integer, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TimestampedBase


class Competitor(TimestampedBase):
    __tablename__ = "competitors"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority_tier: Mapped[str] = mapped_column(String(10), default="Medium", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Active", nullable=False, index=True)
    niches: Mapped[List[str]] = mapped_column(ARRAY(Text), default=list, nullable=False)
    region: Mapped[str] = mapped_column(String(50), default="Global", nullable=False)
    tier: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    creator = relationship("User", back_populates="competitors_created", foreign_keys=[created_by])
    ads = relationship("Ad", back_populates="competitor", cascade="all, delete-orphan")