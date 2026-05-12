from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# ---------- Request bodies ----------

class CompetitorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    domain: str = Field(..., min_length=1, max_length=255)
    priority_tier: str = Field(default="Medium")
    niches: List[str] = Field(default_factory=list)
    region: str = Field(default="Global", max_length=50)
    tier: int = Field(default=2, ge=1, le=3)
    logo_url: Optional[str] = None


class CompetitorUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    priority_tier: Optional[str] = None
    niches: Optional[List[str]] = None
    region: Optional[str] = None
    tier: Optional[int] = Field(default=None, ge=1, le=3)
    logo_url: Optional[str] = None
    status: Optional[str] = None


# ---------- Response shapes ----------

class CompetitorStats(BaseModel):
    total_ads: int = 0
    existing_ads: int = 0
    existing_ads_pct: float = 0.0
    removed_ads: int = 0
    removed_ads_pct: float = 0.0
    avg_duration: float = 0.0
    running_7_plus: int = 0
    running_7_plus_pct: float = 0.0
    winning_ads: int = 0
    winning_ads_pct: float = 0.0
    variants: int = 0
    last_activity: Optional[datetime] = None


class CompetitorResponse(BaseModel):
    id: UUID
    name: str
    domain: str
    logo_url: Optional[str] = None
    niches: List[str]
    priority_tier: str
    status: str
    region: str
    tier: int
    stats: CompetitorStats
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompetitorSummary(BaseModel):
    total_competitors: int
    active_competitors: int
    total_ads_analyzed: int
    existing_ads: int
    removed_ads: int
    avg_winning_pct: float