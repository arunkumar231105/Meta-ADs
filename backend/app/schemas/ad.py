from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


# ---------- Request bodies ----------

class AdCreate(BaseModel):
    competitor_id: UUID
    platform: str = Field(..., max_length=20)
    headline: Optional[str] = None
    primary_text: Optional[str] = None
    cta: Optional[str] = Field(default=None, max_length=100)
    ad_url: Optional[str] = None
    landing_url: Optional[str] = None
    media_url: Optional[str] = None
    is_video: bool = False
    ad_library_id: Optional[str] = Field(default=None, max_length=100)
    variants: int = 0
    notes: Optional[str] = None


class AdUpdate(BaseModel):
    headline: Optional[str] = None
    primary_text: Optional[str] = None
    cta: Optional[str] = None
    ad_url: Optional[str] = None
    landing_url: Optional[str] = None
    media_url: Optional[str] = None
    is_video: Optional[bool] = None
    status: Optional[str] = None
    variants: Optional[int] = None
    notes: Optional[str] = None


# ---------- Nested response objects ----------

class CompetitorRef(BaseModel):
    id: UUID
    name: str
    domain: str
    logo_url: Optional[str] = None
    tier: int
    region: str

    model_config = ConfigDict(from_attributes=True)


class AIInsights(BaseModel):
    hook_text: Optional[str] = None
    hook_type: Optional[str] = None
    angle: Optional[str] = None
    angle_detail: Optional[str] = None
    offer_type: Optional[str] = None
    offer_value: Optional[str] = None
    creative_format: Optional[str] = None
    product_line: Optional[str] = None
    audience_type: Optional[str] = None
    usp_detected: Optional[str] = None
    confidence_score: float = 0.0
    hook_confidence: float = 0.0
    angle_confidence: float = 0.0
    offer_confidence: float = 0.0
    ai_notes: Optional[str] = None
    summary: Optional[str] = None
    suggested_angle: Optional[str] = None
    suggested_hook: Optional[str] = None
    model_version: Optional[str] = None
    analyzed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ---------- Main ad response ----------

class AdResponse(BaseModel):
    id: UUID
    competitor: CompetitorRef
    platform: str
    headline: Optional[str] = None
    primary_text: Optional[str] = None
    cta: Optional[str] = None
    ad_url: Optional[str] = None
    landing_url: Optional[str] = None
    media_url: Optional[str] = None
    is_video: bool
    ad_library_id: Optional[str] = None
    status: str
    first_seen: datetime
    last_seen: datetime
    captured_at: datetime
    variants: int
    notes: Optional[str] = None
    ai_insights: Optional[AIInsights] = None
    created_at: datetime
    updated_at: datetime


# ---------- Pagination ----------

class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int


class AdListResponse(BaseModel):
    data: List[AdResponse]
    meta: PaginationMeta


# ---------- Summary ----------

class AdsSummary(BaseModel):
    total_ads: int
    pending_analysis: int
    analyzed: int
    approved: int
    flagged: int
    avg_confidence: float
    by_platform: dict