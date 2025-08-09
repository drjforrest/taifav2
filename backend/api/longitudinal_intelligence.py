"""
Longitudinal Intelligence API
Phase 2 of Citations Expansion Strategy: Historical Trends & Weak Signals

API endpoints for accessing historical trend analysis and weak signal detection.
"""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address

from services.historical_trend_service import HistoricalTrendService
from services.weak_signal_detection_service import WeakSignalDetectionService

# Initialize services
historical_service = HistoricalTrendService()
weak_signals_service = WeakSignalDetectionService()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/longitudinal-intelligence", tags=["Longitudinal Intelligence"])


@router.get("/innovation-lifecycle")
@limiter.limit("20/minute")
async def get_innovation_lifecycle_analysis(request: Request):
    """
    Track projects from research paper to market implementation
    """
    try:
        lifecycle_data = await historical_service.analyze_innovation_lifecycle()
        return {
            "status": "success",
            "data": lifecycle_data,
            "description": "Innovation lifecycle analysis from research to market"
        }
    except Exception as e:
        logger.error(f"Error analyzing innovation lifecycle: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze innovation lifecycle")


@router.get("/domain-evolution")
@limiter.limit("20/minute")
async def get_domain_evolution_analysis(request: Request):
    """
    Map how AI application areas mature over time
    """
    try:
        evolution_data = await historical_service.analyze_domain_evolution()
        return {
            "status": "success",
            "data": evolution_data,
            "description": "Domain evolution and maturity analysis over time"
        }
    except Exception as e:
        logger.error(f"Error analyzing domain evolution: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze domain evolution")


@router.get("/success-patterns")
@limiter.limit("20/minute")
async def get_success_patterns_analysis(request: Request):
    """
    Identify common characteristics of breakthrough innovations
    """
    try:
        success_data = await historical_service.identify_success_patterns()
        return {
            "status": "success",
            "data": success_data,
            "description": "Success patterns and failure analysis for innovations"
        }
    except Exception as e:
        logger.error(f"Error analyzing success patterns: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze success patterns")


@router.get("/emergence-indicators")
@limiter.limit("20/minute")
async def get_emergence_indicators(request: Request):
    """
    Detect early signs of new AI application areas emerging
    """
    try:
        emergence_data = await weak_signals_service.detect_emergence_indicators()
        return {
            "status": "success",
            "data": emergence_data,
            "description": "Early indicators of emerging AI domains and technologies"
        }
    except Exception as e:
        logger.error(f"Error detecting emergence indicators: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect emergence indicators")


@router.get("/geographic-shifts")
@limiter.limit("20/minute")
async def get_geographic_shifts(request: Request):
    """
    Detect innovation activity migrating between countries
    """
    try:
        shift_data = await weak_signals_service.detect_geographic_shifts()
        return {
            "status": "success",
            "data": shift_data,
            "description": "Geographic shifts in innovation activity and collaboration"
        }
    except Exception as e:
        logger.error(f"Error detecting geographic shifts: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect geographic shifts")


@router.get("/technology-convergence")
@limiter.limit("20/minute")
async def get_technology_convergence(request: Request):
    """
    Analyze AI combining with other domains and technologies
    """
    try:
        convergence_data = await weak_signals_service.detect_technology_convergence()
        return {
            "status": "success",
            "data": convergence_data,
            "description": "Technology convergence patterns and hybrid innovations"
        }
    except Exception as e:
        logger.error(f"Error detecting technology convergence: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect technology convergence")


@router.get("/funding-anomalies")
@limiter.limit("15/minute")
async def get_funding_anomalies(request: Request):
    """
    Detect unusual investment activity signaling opportunities
    """
    try:
        anomaly_data = await weak_signals_service.detect_funding_pattern_anomalies()
        return {
            "status": "success",
            "data": anomaly_data,
            "description": "Unusual funding patterns and investment anomalies"
        }
    except Exception as e:
        logger.error(f"Error detecting funding anomalies: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect funding anomalies")


@router.get("/longitudinal-summary")
@limiter.limit("20/minute")
async def get_longitudinal_summary(
    request: Request,
    include_lifecycle: bool = Query(True, description="Include lifecycle analysis"),
    include_evolution: bool = Query(True, description="Include domain evolution"),
    include_signals: bool = Query(True, description="Include weak signals"),
    include_funding: bool = Query(False, description="Include funding anomalies")
):
    """
    Get comprehensive longitudinal intelligence summary
    """
    try:
        summary = {}
        
        if include_lifecycle:
            lifecycle_data = await historical_service.analyze_innovation_lifecycle()
            summary["lifecycle"] = {
                "stages_distribution": lifecycle_data.get("stages_distribution", {}),
                "key_insights": [
                    "Innovation lifecycle patterns identified",
                    f"Success rate: {lifecycle_data.get('stage_transitions', {}).get('overall_success_rate', 0)*100}%"
                ]
            }
        
        if include_evolution:
            evolution_data = await historical_service.analyze_domain_evolution()
            summary["evolution"] = {
                "maturity_scores": evolution_data.get("maturity_scores", {}),
                "emerging_domains": evolution_data.get("emergence_timeline", {}),
                "key_insights": [
                    "Domain maturity levels analyzed",
                    "Emerging and declining domains identified"
                ]
            }
        
        if include_signals:
            signals_data = await weak_signals_service.detect_emergence_indicators()
            summary["weak_signals"] = {
                "new_domains": len(signals_data.get("new_domains", [])),
                "growing_niches": len(signals_data.get("growing_niches", [])),
                "emerging_keywords": len(signals_data.get("keyword_emergence", [])),
                "key_insights": [
                    f"{len(signals_data.get('new_domains', []))} new domains detected",
                    f"{len(signals_data.get('growing_niches', []))} growing niches identified"
                ]
            }
        
        if include_funding:
            funding_data = await weak_signals_service.detect_funding_pattern_anomalies()
            summary["funding_signals"] = {
                "funding_spikes": len(funding_data.get("unusual_funding_spikes", [])),
                "geographic_anomalies": len(funding_data.get("geographic_funding_shifts", [])),
                "key_insights": [
                    f"{len(funding_data.get('unusual_funding_spikes', []))} funding spikes detected",
                    "Geographic funding pattern shifts analyzed"
                ]
            }
        
        return {
            "status": "success",
            "data": summary,
            "description": "Comprehensive longitudinal intelligence summary",
            "included_analyses": [
                analysis for analysis, include in [
                    ("lifecycle", include_lifecycle),
                    ("evolution", include_evolution), 
                    ("signals", include_signals),
                    ("funding", include_funding)
                ] if include
            ]
        }
        
    except Exception as e:
        logger.error(f"Error generating longitudinal summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate longitudinal summary")


@router.get("/trend-alerts")
@limiter.limit("30/minute")
async def get_trend_alerts(
    request: Request,
    alert_type: str = Query("all", description="Type: 'emergence', 'geographic', 'convergence', 'funding', or 'all'"),
    threshold: float = Query(0.3, ge=0.0, le=1.0, description="Alert threshold (0.0-1.0)")
):
    """
    Get trend alerts based on weak signal detection
    """
    try:
        alerts = []
        
        if alert_type in ["emergence", "all"]:
            emergence_data = await weak_signals_service.detect_emergence_indicators()
            
            # Convert emergence data to alerts
            for domain in emergence_data.get("new_domains", []):
                alerts.append({
                    "type": "new_domain_emergence",
                    "domain": domain.get("domain"),
                    "severity": "high",
                    "description": f"New domain emerged: {domain.get('domain')}"
                })
            
            for niche in emergence_data.get("growing_niches", []):
                if niche.get("growth_rate", 0) >= threshold:
                    alerts.append({
                        "type": "growing_niche",
                        "domain": niche.get("domain"),
                        "growth_rate": niche.get("growth_rate"),
                        "severity": "medium",
                        "description": f"Rapid growth in {niche.get('domain')}: {niche.get('growth_rate')*100}%"
                    })
        
        if alert_type in ["geographic", "all"]:
            geo_data = await weak_signals_service.detect_geographic_shifts()
            
            for migration in geo_data.get("activity_migration", []):
                if abs(migration.get("change_rate", 0)) >= threshold:
                    alerts.append({
                        "type": "geographic_shift",
                        "country": migration.get("country"),
                        "change_rate": migration.get("change_rate"),
                        "direction": migration.get("direction"),
                        "severity": "high" if abs(migration.get("change_rate", 0)) > 0.5 else "medium",
                        "description": f"Innovation activity {migration.get('direction')} in {migration.get('country')}"
                    })
        
        if alert_type in ["convergence", "all"]:
            convergence_data = await weak_signals_service.detect_technology_convergence()
            
            for fusion in convergence_data.get("technology_fusion", []):
                if fusion.get("frequency", 0) >= 3:  # Multiple instances
                    alerts.append({
                        "type": "technology_convergence",
                        "technologies": fusion.get("technology_combination", []),
                        "frequency": fusion.get("frequency"),
                        "severity": "medium",
                        "description": f"Technology fusion detected: {' + '.join(fusion.get('technology_combination', []))}"
                    })
        
        if alert_type in ["funding", "all"]:
            funding_data = await weak_signals_service.detect_funding_pattern_anomalies()
            
            for spike in funding_data.get("unusual_funding_spikes", []):
                alerts.append({
                    "type": "funding_spike",
                    "domain": spike.get("domain"),
                    "unusual_count": spike.get("unusual_funding_count"),
                    "severity": "high",
                    "description": f"Unusual funding activity in {spike.get('domain')}"
                })
        
        # Sort by severity
        severity_order = {"high": 3, "medium": 2, "low": 1}
        alerts.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 1), reverse=True)
        
        return {
            "status": "success",
            "data": {
                "alerts": alerts,
                "total_alerts": len(alerts),
                "high_severity": len([a for a in alerts if a.get("severity") == "high"]),
                "medium_severity": len([a for a in alerts if a.get("severity") == "medium"]),
                "low_severity": len([a for a in alerts if a.get("severity") == "low"])
            },
            "description": f"Trend alerts for type: {alert_type}",
            "parameters": {
                "alert_type": alert_type,
                "threshold": threshold
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting trend alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trend alerts")


@router.get("/health")
async def health_check():
    """Health check endpoint for longitudinal intelligence API"""
    return {
        "status": "healthy",
        "service": "longitudinal-intelligence",
        "available_endpoints": [
            "/innovation-lifecycle",
            "/domain-evolution",
            "/success-patterns",
            "/emergence-indicators",
            "/geographic-shifts", 
            "/technology-convergence",
            "/funding-anomalies",
            "/longitudinal-summary",
            "/trend-alerts"
        ]
    }