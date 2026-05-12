from datetime import datetime, timezone, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.competitor import Competitor
from app.models.ad import Ad
from app.models.ad_analysis import AdAnalysis
from app.schemas.competitor import (
    CompetitorCreate,
    CompetitorUpdate,
    CompetitorResponse,
    CompetitorStats,
    CompetitorSummary,
)


router = APIRouter(prefix="/competitors", tags=["competitors"])


# ---------- Helper to compute stats for one competitor ----------

async def _compute_stats_for_competitor(db: AsyncSession, competitor_id: UUID) -> CompetitorStats:
    """Compute aggregate stats for a single competitor."""
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

    # Aggregated query over ads + ad_analyses
    stmt = (
        select(
            func.count(Ad.id).label("total_ads"),
            func.count(case((Ad.last_seen >= seven_days_ago, 1))).label("existing_ads"),
            func.count(case((Ad.last_seen < seven_days_ago, 1))).label("removed_ads"),
            func.coalesce(
                func.avg(
                    func.extract("epoch", Ad.last_seen - Ad.first_seen) / 86400.0
                ),
                0.0,
            ).label("avg_duration"),
            func.count(
                case(
                    (func.extract("epoch", Ad.last_seen - Ad.first_seen) / 86400.0 >= 7, 1)
                )
            ).label("running_7_plus"),
            func.count(case((AdAnalysis.confidence_score >= 75, 1))).label("winning_ads"),
            func.coalesce(func.sum(Ad.variants), 0).label("variants"),
            func.max(Ad.last_seen).label("last_activity"),
        )
        .select_from(Ad)
        .outerjoin(AdAnalysis, AdAnalysis.ad_id == Ad.id)
        .where(Ad.competitor_id == competitor_id)
    )

    result = (await db.execute(stmt)).one()

    total = result.total_ads or 0
    existing = result.existing_ads or 0
    removed = result.removed_ads or 0
    running_7_plus = result.running_7_plus or 0
    winning = result.winning_ads or 0

    def pct(num, denom):
        return round((num / denom) * 100, 1) if denom else 0.0

    return CompetitorStats(
        total_ads=total,
        existing_ads=existing,
        existing_ads_pct=pct(existing, total),
        removed_ads=removed,
        removed_ads_pct=pct(removed, total),
        avg_duration=round(float(result.avg_duration or 0), 1),
        running_7_plus=running_7_plus,
        running_7_plus_pct=pct(running_7_plus, total),
        winning_ads=winning,
        winning_ads_pct=pct(winning, total),
        variants=int(result.variants or 0),
        last_activity=result.last_activity,
    )


def _competitor_to_response(c: Competitor, stats: CompetitorStats) -> CompetitorResponse:
    return CompetitorResponse(
        id=c.id,
        name=c.name,
        domain=c.domain,
        logo_url=c.logo_url,
        niches=c.niches or [],
        priority_tier=c.priority_tier,
        status=c.status,
        region=c.region,
        tier=c.tier,
        stats=stats,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


# ---------- Endpoints ----------

@router.get("/summary", response_model=CompetitorSummary)
async def get_competitors_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aggregate KPIs across all active competitors."""
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

    stmt = (
        select(
            func.count(func.distinct(Competitor.id)).label("total_competitors"),
            func.count(
                func.distinct(case((Competitor.status == "Active", Competitor.id)))
            ).label("active_competitors"),
            func.count(Ad.id).label("total_ads_analyzed"),
            func.count(case((Ad.last_seen >= seven_days_ago, 1))).label("existing_ads"),
            func.count(case((Ad.last_seen < seven_days_ago, 1))).label("removed_ads"),
        )
        .select_from(Competitor)
        .outerjoin(Ad, Ad.competitor_id == Competitor.id)
    )
    row = (await db.execute(stmt)).one()

    # Winning percentage: ads with confidence_score >= 75 / total analyzed
    winning_stmt = select(
        func.count(case((AdAnalysis.confidence_score >= 75, 1))).label("winning"),
        func.count(AdAnalysis.id).label("analyzed"),
    )
    winning_row = (await db.execute(winning_stmt)).one()
    winning_pct = (
        round(winning_row.winning / winning_row.analyzed * 100, 1)
        if winning_row.analyzed
        else 0.0
    )

    return CompetitorSummary(
        total_competitors=row.total_competitors or 0,
        active_competitors=row.active_competitors or 0,
        total_ads_analyzed=row.total_ads_analyzed or 0,
        existing_ads=row.existing_ads or 0,
        removed_ads=row.removed_ads or 0,
        avg_winning_pct=winning_pct,
    )


@router.get("", response_model=List[CompetitorResponse])
async def list_competitors(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all competitors with computed stats. Optionally filter by status."""
    stmt = select(Competitor).order_by(Competitor.created_at.desc())
    if status_filter:
        stmt = stmt.where(Competitor.status == status_filter)

    competitors = (await db.execute(stmt)).scalars().all()

    responses = []
    for c in competitors:
        stats = await _compute_stats_for_competitor(db, c.id)
        responses.append(_competitor_to_response(c, stats))
    return responses


@router.get("/{competitor_id}", response_model=CompetitorResponse)
async def get_competitor(
    competitor_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single competitor by ID with full stats."""
    competitor = await db.get(Competitor, competitor_id)
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    stats = await _compute_stats_for_competitor(db, competitor.id)
    return _competitor_to_response(competitor, stats)


@router.post("", response_model=CompetitorResponse, status_code=status.HTTP_201_CREATED)
async def create_competitor(
    payload: CompetitorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new competitor."""
    competitor = Competitor(
        name=payload.name,
        domain=payload.domain,
        priority_tier=payload.priority_tier,
        niches=payload.niches,
        region=payload.region,
        tier=payload.tier,
        logo_url=payload.logo_url,
        status="Active",
        created_by=current_user.id,
    )
    db.add(competitor)
    await db.commit()
    await db.refresh(competitor)

    stats = CompetitorStats()  # zero stats for brand-new competitor
    return _competitor_to_response(competitor, stats)


@router.put("/{competitor_id}", response_model=CompetitorResponse)
async def update_competitor(
    competitor_id: UUID,
    payload: CompetitorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a competitor's fields. Only provided fields are changed."""
    competitor = await db.get(Competitor, competitor_id)
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(competitor, field, value)

    await db.commit()
    await db.refresh(competitor)

    stats = await _compute_stats_for_competitor(db, competitor.id)
    return _competitor_to_response(competitor, stats)


@router.delete("/{competitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_competitor(
    competitor_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft-delete a competitor by setting status to 'Inactive'."""
    competitor = await db.get(Competitor, competitor_id)
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    competitor.status = "Inactive"
    await db.commit()
    return None