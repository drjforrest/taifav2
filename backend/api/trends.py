"""
Trends API Endpoints
====================

Provides API endpoints for Historical Trend Analysis including:
- Innovation Lifecycle Tracking
- Domain Evolution Mapping
- Pattern Analysis

Part of Phase 2 Implementation
"""

import asyncio
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from config.database import get_supabase
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from loguru import logger
from services.innovation_lifecycle_tracker import (
    LifecycleMetrics,
    LifecycleStage,
    innovation_lifecycle_tracker,
)
from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/trends", tags=["Trends Analysis"])

# LIFECYCLE TRACKING ENDPOINTS


@router.get("/lifecycles")
@limiter.limit("30/minute")
async def get_lifecycles(
    request: Request,
    stage: Optional[LifecycleStage] = Query(
        None, description="Filter by lifecycle stage"
    ),
    country: Optional[str] = Query(None, description="Filter by country"),
    innovation_type: Optional[str] = Query(
        None, description="Filter by innovation type"
    ),
):
    """Get lifecycle records with optional filtering"""
    try:
        analytics = await innovation_lifecycle_tracker.get_lifecycle_analytics(
            stage=stage, country=country, innovation_type=innovation_type
        )
        return JSONResponse(content=analytics)
    except Exception as e:
        logger.error(f"Error getting lifecycle analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get lifecycle analytics")


@router.get("/lifecycles/{innovation_id}")
@limiter.limit("60/minute")
async def get_innovation_lifecycle(request: Request, innovation_id: UUID):
    """Get complete lifecycle for a specific innovation"""
    try:
        # Validate innovation exists and is public
        supabase = get_supabase()
        response = (
            supabase.table("innovations")
            .select("id, title, description")
            .eq("id", str(innovation_id))
            .eq("visibility", "public")
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404, detail="Innovation not found or not accessible"
            )

        # Get lifecycle data
        lifecycle_stages = await innovation_lifecycle_tracker.get_innovation_lifecycle(
            innovation_id
        )
        metrics = await innovation_lifecycle_tracker.get_lifecycle_metrics(
            innovation_id
        )

        return JSONResponse(
            content={
                "innovation": response.data[0],
                "lifecycle_stages": [
                    {
                        "stage": stage.stage.value,
                        "start_date": stage.start_date.isoformat()
                        if stage.start_date
                        else None,
                        "end_date": stage.end_date.isoformat()
                        if stage.end_date
                        else None,
                        "duration_days": stage.duration_days,
                        "key_milestones": stage.key_milestones,
                        "resources_invested": stage.resources_invested,
                        "challenges_encountered": stage.challenges_encountered,
                        "success_indicators": stage.success_indicators,
                    }
                    for stage in lifecycle_stages
                ],
                "metrics": {
                    "total_duration_days": metrics.total_duration_days,
                    "time_to_market_days": metrics.time_to_market_days,
                    "current_stage": metrics.current_stage.value
                    if metrics.current_stage
                    else None,
                    "stage_durations": {
                        stage.value: duration
                        for stage, duration in metrics.stage_durations.items()
                    }
                    if metrics.stage_durations
                    else {},
                    "has_completed_cycle": metrics.has_completed_cycle,
                },
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lifecycle for innovation {innovation_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get innovation lifecycle"
        )


@router.post("/lifecycles")
@limiter.limit("20/minute")
async def create_lifecycle_record(
    request: Request,
    innovation_id: UUID,
    stage: LifecycleStage,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    key_milestones: Optional[List[str]] = None,
    resources_invested: Optional[Dict[str, Any]] = None,
    challenges_encountered: Optional[List[str]] = None,
    success_indicators: Optional[List[str]] = None,
):
    """Create a new lifecycle stage record for an innovation"""
    try:
        # Validate innovation exists
        supabase = get_supabase()
        response = (
            supabase.table("innovations")
            .select("id")
            .eq("id", str(innovation_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Innovation not found")

        # Create lifecycle record
        success = await innovation_lifecycle_tracker.create_lifecycle_record(
            innovation_id=innovation_id,
            stage=stage,
            start_date=start_date,
            end_date=end_date,
            key_milestones=key_milestones,
            resources_invested=resources_invested,
            challenges_encountered=challenges_encountered,
            success_indicators=success_indicators,
        )

        if success:
            return JSONResponse(
                content={
                    "status": "success",
                    "message": f"Lifecycle record created for innovation {innovation_id}, stage {stage.value}",
                }
            )
        else:
            raise HTTPException(
                status_code=500, detail="Failed to create lifecycle record"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating lifecycle record: {e}")
        raise HTTPException(status_code=500, detail="Failed to create lifecycle record")


@router.put("/lifecycles/{record_id}")
@limiter.limit("20/minute")
async def update_lifecycle_record(
    request: Request,
    record_id: UUID,
    stage: Optional[LifecycleStage] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    key_milestones: Optional[List[str]] = None,
    resources_invested: Optional[Dict[str, Any]] = None,
    challenges_encountered: Optional[List[str]] = None,
    success_indicators: Optional[List[str]] = None,
):
    """Update an existing lifecycle stage record"""
    try:
        success = await innovation_lifecycle_tracker.update_lifecycle_record(
            record_id=record_id,
            stage=stage,
            start_date=start_date,
            end_date=end_date,
            key_milestones=key_milestones,
            resources_invested=resources_invested,
            challenges_encountered=challenges_encountered,
            success_indicators=success_indicators,
        )

        if success:
            return JSONResponse(
                content={
                    "status": "success",
                    "message": f"Lifecycle record {record_id} updated",
                }
            )
        else:
            raise HTTPException(
                status_code=500, detail="Failed to update lifecycle record"
            )
    except Exception as e:
        logger.error(f"Error updating lifecycle record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update lifecycle record")


@router.delete("/lifecycles/{record_id}")
@limiter.limit("10/minute")
async def delete_lifecycle_record(request: Request, record_id: UUID):
    """Delete a lifecycle stage record"""
    try:
        supabase = get_supabase()
        response = (
            supabase.table("innovation_lifecycles")
            .delete()
            .eq("id", str(record_id))
            .execute()
        )

        if response.data:
            return JSONResponse(
                content={
                    "status": "success",
                    "message": f"Lifecycle record {record_id} deleted",
                }
            )
        else:
            raise HTTPException(status_code=404, detail="Lifecycle record not found")
    except Exception as e:
        logger.error(f"Error deleting lifecycle record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete lifecycle record")


# TIME-TO-MARKET ANALYSIS ENDPOINTS


@router.get("/time-to-market")
@limiter.limit("20/minute")
async def get_time_to_market_analysis(
    request: Request,
    country: Optional[str] = Query(None, description="Filter by country"),
    innovation_type: Optional[str] = Query(
        None, description="Filter by innovation type"
    ),
):
    """Get time-to-market analysis across innovations"""
    try:
        analysis = await innovation_lifecycle_tracker.get_time_to_market_analysis(
            country=country, innovation_type=innovation_type
        )
        return JSONResponse(content=analysis)
    except Exception as e:
        logger.error(f"Error getting time-to-market analysis: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get time-to-market analysis"
        )


# INTEGRATION ENDPOINTS


@router.post("/link-publication")
@limiter.limit("20/minute")
async def link_publication_to_lifecycle(
    request: Request, publication_id: UUID, innovation_id: UUID
):
    """Link a publication to an innovation's lifecycle (typically for research stage)"""
    try:
        success = (
            await innovation_lifecycle_tracker.link_publication_to_innovation_lifecycle(
                publication_id=publication_id, innovation_id=innovation_id
            )
        )

        if success:
            return JSONResponse(
                content={
                    "status": "success",
                    "message": f"Publication {publication_id} linked to innovation {innovation_id} lifecycle",
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to link publication to innovation lifecycle",
            )
    except Exception as e:
        logger.error(
            f"Error linking publication {publication_id} to innovation {innovation_id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to link publication to innovation lifecycle"
        )


# DOMAIN EVOLUTION ENDPOINTS


@router.get("/domains")
@limiter.limit("30/minute")
async def get_domain_evolution(
    request: Request,
    domain_name: Optional[str] = Query(None, description="Filter by domain name"),
    period_start: Optional[date] = Query(
        None, description="Filter by period start date"
    ),
    period_end: Optional[date] = Query(None, description="Filter by period end date"),
):
    """Get domain evolution records with optional filtering"""
    try:
        from services.domain_evolution_mapper import domain_evolution_mapper

        # Build query for domain evolution records
        supabase = get_supabase()
        query = supabase.table("domain_evolution").select("*")

        if domain_name:
            query = query.eq("domain_name", domain_name)

        if period_start:
            query = query.gte("period_start", period_start.isoformat())

        if period_end:
            query = query.lte("period_end", period_end.isoformat())

        response = query.execute()

        return JSONResponse(content=response.data if response.data else [])
    except Exception as e:
        logger.error(f"Error getting domain evolution: {e}")
        raise HTTPException(status_code=500, detail="Failed to get domain evolution")


@router.get("/domains/trends")
@limiter.limit("20/minute")
async def get_domain_trends(
    request: Request,
    domain_name: Optional[str] = Query(
        None, description="Get trends for specific domain"
    ),
    period_start: Optional[date] = Query(
        None, description="Filter by period start date"
    ),
    period_end: Optional[date] = Query(None, description="Filter by period end date"),
):
    """Get trend data for domains"""
    try:
        from services.domain_evolution_mapper import domain_evolution_mapper

        if domain_name:
            # Get trends for specific domain
            trends = await domain_evolution_mapper.get_domain_trends(
                domain_name=domain_name,
                period_start=period_start,
                period_end=period_end,
            )

            # Convert to dict for JSON serialization
            trends_dict = {
                "domain_name": trends.domain_name,
                "time_series": trends.time_series,
                "overall_growth_rate": trends.overall_growth_rate,
                "maturity_trajectory": [m.value for m in trends.maturity_trajectory],
                "key_influencers": trends.key_influencers,
            }

            return JSONResponse(content=trends_dict)
        else:
            # Get trends for all domains
            all_trends = await domain_evolution_mapper.get_all_domain_trends(
                period_start=period_start, period_end=period_end
            )

            # Convert to dict for JSON serialization
            all_trends_dict = []
            for trend in all_trends:
                all_trends_dict.append(
                    {
                        "domain_name": trend.domain_name,
                        "time_series": trend.time_series,
                        "overall_growth_rate": trend.overall_growth_rate,
                        "maturity_trajectory": [
                            m.value for m in trend.maturity_trajectory
                        ],
                        "key_influencers": trend.key_influencers,
                    }
                )

            return JSONResponse(content=all_trends_dict)
    except Exception as e:
        logger.error(f"Error getting domain trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get domain trends")


@router.get("/domains/emerging")
@limiter.limit("15/minute")
async def get_emerging_domains(
    request: Request,
    period_start: Optional[date] = Query(
        None, description="Analysis period start date"
    ),
    period_end: Optional[date] = Query(None, description="Analysis period end date"),
):
    """Get emerging domains in African AI research"""
    try:
        from services.domain_evolution_mapper import domain_evolution_mapper

        # Set default period if not provided (last 2 years)
        if not period_end:
            period_end = date.today()
        if not period_start:
            period_start = date(period_end.year - 2, period_end.month, period_end.day)

        emerging_domains = await domain_evolution_mapper.identify_emerging_domains(
            period_start=period_start, period_end=period_end
        )

        # Convert to dict for JSON serialization
        emerging_domains_dict = []
        for domain in emerging_domains:
            domain_dict = {
                "domain_name": domain.domain_name,
                "emergence_date": domain.emergence_date.isoformat(),
                "emergence_indicators": domain.emergence_indicators,
                "key_players": domain.key_players,
                "publication_growth_rate": domain.publication_growth_rate,
                "innovation_potential_score": domain.innovation_potential_score,
                "confidence_score": domain.confidence_score,
            }
            emerging_domains_dict.append(domain_dict)

        return JSONResponse(content=emerging_domains_dict)
    except Exception as e:
        logger.error(f"Error getting emerging domains: {e}")
        raise HTTPException(status_code=500, detail="Failed to get emerging domains")


@router.get("/domains/focus-areas")
@limiter.limit("15/minute")
async def get_research_focus_areas(
    request: Request,
    period_start: Optional[date] = Query(
        None, description="Analysis period start date"
    ),
    period_end: Optional[date] = Query(None, description="Analysis period end date"),
):
    """Get research focus area mapping"""
    try:
        from services.domain_evolution_mapper import domain_evolution_mapper

        # Set default period if not provided (last 1 year)
        if not period_end:
            period_end = date.today()
        if not period_start:
            period_start = date(period_end.year - 1, period_end.month, period_end.day)

        focus_areas = await domain_evolution_mapper.map_research_focus_areas(
            period_start=period_start, period_end=period_end
        )

        return JSONResponse(content=focus_areas)
    except Exception as e:
        logger.error(f"Error getting research focus areas: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get research focus areas"
        )


@router.post("/domains/track")
@limiter.limit("10/minute")
async def track_domain_evolution_endpoint(
    request: Request, domain_name: str, period_start: date, period_end: date
):
    """Track domain evolution for a specific period"""
    try:
        from services.domain_evolution_mapper import domain_evolution_mapper

        success = await domain_evolution_mapper.track_domain_evolution(
            domain_name=domain_name, period_start=period_start, period_end=period_end
        )

        if success:
            return JSONResponse(
                content={
                    "status": "success",
                    "message": f"Domain evolution tracked for {domain_name} from {period_start} to {period_end}",
                }
            )
        else:
            raise HTTPException(
                status_code=500, detail="Failed to track domain evolution"
            )
    except Exception as e:
        logger.error(f"Error tracking domain evolution: {e}")
        raise HTTPException(status_code=500, detail="Failed to track domain evolution")


# SUCCESS PATTERN ENDPOINTS


@router.get("/patterns/success")
@limiter.limit("20/minute")
async def get_success_patterns(
    request: Request,
    pattern_type: Optional[str] = Query(None, description="Filter by pattern type"),
    domain_specific: Optional[bool] = Query(
        None, description="Filter by domain specificity"
    ),
    min_confidence: Optional[float] = Query(
        None, description="Filter by minimum confidence score"
    ),
):
    """Get success patterns with optional filtering"""
    try:
        from services.success_pattern_identifier import (
            PatternType,
            success_pattern_identifier,
        )

        # Convert pattern_type string to enum if provided
        pattern_type_enum = None
        if pattern_type:
            try:
                pattern_type_enum = PatternType(pattern_type)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid pattern type")

        patterns = await success_pattern_identifier.get_success_patterns(
            pattern_type=pattern_type_enum,
            domain_specific=domain_specific,
            min_confidence=min_confidence,
        )

        # Convert to dict for JSON serialization
        patterns_dict = []
        for pattern in patterns:
            pattern_dict = {
                "id": str(pattern.id) if pattern.id else None,
                "pattern_name": pattern.pattern_name,
                "pattern_description": pattern.pattern_description,
                "pattern_type": pattern.pattern_type.value,
                "associated_features": pattern.associated_features,
                "success_rate": pattern.success_rate,
                "domain_specific": pattern.domain_specific,
                "geographic_scope": pattern.geographic_scope,
                "temporal_scope": pattern.temporal_scope,
                "supporting_evidence": pattern.supporting_evidence,
                "confidence_score": pattern.confidence_score,
                "last_validated": pattern.last_validated.isoformat()
                if pattern.last_validated
                else None,
            }
            patterns_dict.append(pattern_dict)

        return JSONResponse(content=patterns_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting success patterns: {e}")
        raise HTTPException(status_code=500, detail="Failed to get success patterns")


@router.get("/patterns/success/identify")
@limiter.limit("10/minute")
async def identify_success_patterns(
    request: Request,
    period_start: Optional[date] = Query(
        None, description="Analysis period start date"
    ),
    period_end: Optional[date] = Query(None, description="Analysis period end date"),
    domain: Optional[str] = Query(None, description="Specific domain to analyze"),
):
    """Identify success patterns in African AI research"""
    try:
        from services.success_pattern_identifier import success_pattern_identifier

        patterns = await success_pattern_identifier.identify_success_patterns(
            period_start=period_start, period_end=period_end, domain=domain
        )

        # Convert to dict for JSON serialization
        patterns_dict = []
        for pattern in patterns:
            pattern_dict = {
                "id": str(pattern.id) if pattern.id else None,
                "pattern_name": pattern.pattern_name,
                "pattern_description": pattern.pattern_description,
                "pattern_type": pattern.pattern_type.value,
                "associated_features": pattern.associated_features,
                "success_rate": pattern.success_rate,
                "domain_specific": pattern.domain_specific,
                "geographic_scope": pattern.geographic_scope,
                "temporal_scope": pattern.temporal_scope,
                "supporting_evidence": pattern.supporting_evidence,
                "confidence_score": pattern.confidence_score,
                "last_validated": pattern.last_validated.isoformat()
                if pattern.last_validated
                else None,
            }
            patterns_dict.append(pattern_dict)

        return JSONResponse(content=patterns_dict)
    except Exception as e:
        logger.error(f"Error identifying success patterns: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to identify success patterns"
        )


@router.get("/patterns/success/analysis/{innovation_id}")
@limiter.limit("30/minute")
async def get_innovation_success_analysis(request: Request, innovation_id: UUID):
    """Get comprehensive success analysis for an innovation"""
    try:
        from services.success_pattern_identifier import success_pattern_identifier

        # Validate innovation exists and is public
        supabase = get_supabase()
        response = (
            supabase.table("innovations")
            .select("id")
            .eq("id", str(innovation_id))
            .eq("visibility", "public")
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404, detail="Innovation not found or not accessible"
            )

        analysis = await success_pattern_identifier.get_innovation_success_analysis(
            innovation_id
        )

        if not analysis:
            raise HTTPException(
                status_code=404,
                detail="Success analysis not available for this innovation",
            )

        return JSONResponse(content=analysis)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting success analysis for innovation {innovation_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Failed to get success analysis")
