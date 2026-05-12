import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TimestampedBase


class Ad(TimestampedBase):
    __tablename__ = "ads"

    competitor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competitors.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    platform: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    headline: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    primary_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cta: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ad_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    landing_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    media_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_video: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ad_library_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    variants: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    embedding_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    competitor = relationship("Competitor", back_populates="ads")
    analysis = relationship(
        "AdAnalysis", back_populates="ad", uselist=False, cascade="all, delete-orphan"
    )
    review_items = relationship(
        "ReviewQueue", back_populates="ad", cascade="all, delete-orphan"
    )