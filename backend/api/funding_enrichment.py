"""
Funding Enrichment API
=====================

API endpoints for activating and monitoring funding information and market sizing
enrichment solutions to address the critical data gaps.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging

from services.funding_enrichment_activator import (
    activate_funding_solutions,
    get_funding_enrichment_status,
    funding_activator
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/funding-enrichment", tags=["Funding Enrichment"])


@router.post("/activate")
async def activate_enrichment_solutions(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Activate immediate solutions for funding information and market sizing data gaps.
    
    This endpoint triggers:
    1. AI Backfill Service configuration for funding gaps
    2. Scheduled enrichment activation for funding data
    3. Immediate market-focused intelligence gathering  
    4. Enhanced extraction processing of existing records
    """
    try:
        logger.info("🚀 API request to activate funding enrichment solutions")
        
        # Run activation in background to avoid timeout
        background_tasks.add_task(activate_funding_solutions)
        
        return {
            "status": "activation_started",
            "message": "Funding enrichment solutions activation initiated",
            "timestamp": "2024-01-01T00:00:00Z",  # Will be updated by the actual activation
            "expected_solutions": [
                "ai_backfill_service",
                "scheduled_enrichment", 
                "market_intelligence_gathering",
                "enhanced_extraction"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error initiating funding enrichment activation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to activate enrichment solutions: {str(e)}"
        )


@router.get("/status")
async def get_enrichment_status() -> Dict[str, Any]:
    """
    Get current status of funding enrichment across the platform.
    
    Returns:
    - Data completeness percentages for funding and market sizing
    - AI backfill service statistics
    - Scheduled enrichment status
    - Gap analysis and recommendations
    """
    try:
        status = await get_funding_enrichment_status()
        
        # Add recommendations based on current status
        data_completeness = status.get("data_completeness", {})
        funding_percent = data_completeness.get("funding_completeness_percent", 0)
        market_percent = data_completeness.get("market_sizing_completeness_percent", 0)
        
        recommendations = []
        if funding_percent < 50:
            recommendations.append("🔴 CRITICAL: Activate AI backfill service for funding data")
        elif funding_percent < 80:
            recommendations.append("🟠 HIGH: Increase funding data collection frequency")
        
        if market_percent < 50:
            recommendations.append("🔴 CRITICAL: Enable market analysis intelligence gathering")
        elif market_percent < 80:
            recommendations.append("🟠 HIGH: Enhance market sizing extraction patterns")
        
        if not status.get("scheduled_enrichment", {}).get("enabled", False):
            recommendations.append("⚠️ MEDIUM: Enable scheduled enrichment for continuous updates")
        
        status["recommendations"] = recommendations
        status["overall_health"] = "healthy" if funding_percent > 80 and market_percent > 80 else "needs_attention"
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting enrichment status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get enrichment status: {str(e)}"
        )


@router.post("/trigger-backfill")
async def trigger_manual_backfill(max_jobs: int = 10) -> Dict[str, Any]:
    """
    Trigger manual AI backfill job processing for funding and market data.
    
    Args:
        max_jobs: Maximum number of backfill jobs to process (default: 10)
    """
    try:
        logger.info(f"🤖 Manual backfill triggered for {max_jobs} jobs")
        
        # Import the backfill service
        from services.ai_backfill_service import run_backfill_batch
        
        # Process backfill jobs
        completed_jobs = await run_backfill_batch(max_jobs)
        
        # Calculate statistics
        successful_jobs = [job for job in completed_jobs if job.status.value == "completed"]
        failed_jobs = [job for job in completed_jobs if job.status.value == "failed"]
        
        return {
            "status": "completed",
            "jobs_processed": len(completed_jobs),
            "successful": len(successful_jobs),
            "failed": len(failed_jobs),
            "job_details": [
                {
                    "job_id": job.job_id,
                    "innovation_id": job.innovation_id,
                    "status": job.status.value,
                    "fields_processed": len(job.missing_fields),
                    "cost": job.total_cost
                }
                for job in completed_jobs
            ]
        }
        
    except Exception as e:
        logger.error(f"Error running manual backfill: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run backfill: {str(e)}"
        )


@router.get("/data-gaps")
async def analyze_data_gaps() -> Dict[str, Any]:
    """
    Analyze current data gaps in funding and market sizing information.
    
    Returns detailed analysis of missing data patterns and recommendations.
    """
    try:
        # Get current status
        status = await get_funding_enrichment_status()
        data_completeness = status.get("data_completeness", {})
        
        # Calculate gap analysis
        total_innovations = data_completeness.get("total_innovations", 0)
        funding_gap = data_completeness.get("funding_gap_count", 0)
        market_gap = data_completeness.get("market_sizing_gap_count", 0)
        
        # Estimate backfill effort
        estimated_backfill_cost = (funding_gap * 0.10) + (market_gap * 0.12)  # Cost per field
        estimated_processing_time = max(funding_gap, market_gap) * 0.5  # 0.5 minutes per record
        
        return {
            "analysis_timestamp": status.get("timestamp"),
            "gap_analysis": {
                "total_innovations": total_innovations,
                "funding_gaps": {
                    "count": funding_gap,
                    "percentage": round((funding_gap / total_innovations * 100) if total_innovations > 0 else 0, 1)
                },
                "market_sizing_gaps": {
                    "count": market_gap,
                    "percentage": round((market_gap / total_innovations * 100) if total_innovations > 0 else 0, 1)
                }
            },
            "backfill_estimates": {
                "estimated_cost_usd": round(estimated_backfill_cost, 2),
                "estimated_processing_minutes": round(estimated_processing_time),
                "recommended_batch_size": 50,
                "estimated_batches": max(1, (max(funding_gap, market_gap) // 50))
            },
            "priority_actions": [
                {
                    "action": "activate_ai_backfill",
                    "impact": "high",
                    "effort": "low",
                    "description": "Enable automated AI backfill service"
                },
                {
                    "action": "enable_scheduled_enrichment", 
                    "impact": "high",
                    "effort": "low",
                    "description": "Start regular intelligence gathering"
                },
                {
                    "action": "process_existing_records",
                    "impact": "medium",
                    "effort": "medium", 
                    "description": "Re-process existing data with enhanced extractor"
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing data gaps: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze data gaps: {str(e)}"
        )


@router.post("/test-extraction")
async def test_funding_extraction(text: str) -> Dict[str, Any]:
    """
    Test the enhanced funding extractor on provided text.
    
    Args:
        text: Text content to analyze for funding and market sizing information
    """
    try:
        # Extract funding and market info
        funding_info = funding_activator.funding_extractor.extract_funding_info(text)
        
        return {
            "status": "success",
            "input_text_length": len(text),
            "extraction_results": funding_info,
            "patterns_detected": {
                "funding_type": funding_info.get("funding_type"),
                "has_market_sizing": bool(funding_info.get("market_sizing")),
                "target_audiences": len(funding_info.get("target_audience", [])),
                "ai_subsectors": len(funding_info.get("ai_subsectors", [])),
                "focus_indicators": sum(1 for v in funding_info.get("focus_indicators", {}).values() if v)
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing extraction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test extraction: {str(e)}"
        )