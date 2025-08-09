"""
Entity Relationship Mining API
Phase 1 of Citations Expansion Strategy: Complete Entity Analysis

API endpoints for accessing co-authorship networks, organization relationships,
geographic collaboration patterns, and temporal relationship analysis.
"""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional, List
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address

from services.coauthorship_extraction_service import CoauthorshipExtractionService
from services.entity_relationship_service import EntityRelationshipService

# Initialize services
coauthorship_service = CoauthorshipExtractionService()
entity_service = EntityRelationshipService()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/entity-relationships", tags=["Entity Relationships"])


@router.get("/coauthorship-networks")
@limiter.limit("20/minute")
async def get_coauthorship_networks(request: Request):
    """
    Extract and analyze co-authorship networks from publications
    
    Returns detailed collaboration networks, key researchers, and research clusters
    """
    try:
        networks = await coauthorship_service.extract_coauthorship_networks()
        return {
            "status": "success",
            "data": networks,
            "description": "Co-authorship networks extracted from publication data"
        }
    except Exception as e:
        logger.error(f"Error retrieving coauthorship networks: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract coauthorship networks")


@router.get("/organization-relationships")
@limiter.limit("20/minute")
async def get_organization_relationships(request: Request):
    """
    Analyze organization relationships including university-industry partnerships
    and cross-institutional collaborations
    """
    try:
        relationships = await entity_service.analyze_organization_relationships()
        return {
            "status": "success",
            "data": relationships,
            "description": "Organization relationship analysis including partnerships and networks"
        }
    except Exception as e:
        logger.error(f"Error analyzing organization relationships: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze organization relationships")


@router.get("/geographic-collaboration")
@limiter.limit("20/minute")
async def get_geographic_collaboration(request: Request):
    """
    Analyze collaboration patterns across African countries and regions
    """
    try:
        geographic_data = await entity_service.analyze_geographic_collaboration()
        return {
            "status": "success",
            "data": geographic_data,
            "description": "Geographic collaboration patterns across African countries"
        }
    except Exception as e:
        logger.error(f"Error analyzing geographic collaboration: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze geographic collaboration")


@router.get("/temporal-relationships")
@limiter.limit("20/minute")
async def get_temporal_relationships(request: Request):
    """
    Track how partnerships and collaborations evolve over time
    """
    try:
        temporal_data = await entity_service.analyze_temporal_relationships()
        return {
            "status": "success",
            "data": temporal_data,
            "description": "Temporal analysis of partnership and collaboration evolution"
        }
    except Exception as e:
        logger.error(f"Error analyzing temporal relationships: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze temporal relationships")


@router.get("/entity-extraction")
@limiter.limit("20/minute")
async def get_entity_extraction(request: Request):
    """
    Extract entities (organizations, technologies, locations, people) from text
    """
    try:
        entities = await entity_service.extract_entities_from_text()
        return {
            "status": "success",
            "data": entities,
            "description": "Entities extracted from innovation and publication text"
        }
    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract entities")


@router.get("/collaboration-summary")
@limiter.limit("30/minute")
async def get_collaboration_summary(
    request: Request,
    include_coauthorship: bool = Query(True, description="Include co-authorship data"),
    include_organizations: bool = Query(True, description="Include organization data"),
    include_geographic: bool = Query(True, description="Include geographic data"),
    include_temporal: bool = Query(False, description="Include temporal data")
):
    """
    Get a comprehensive summary of collaboration patterns
    
    Allows selective inclusion of different data types for performance optimization
    """
    try:
        summary = {}
        
        if include_coauthorship:
            logger.info("Fetching coauthorship data for summary")
            coauthorship_data = await coauthorship_service.extract_coauthorship_networks()
            summary["coauthorship"] = {
                "key_metrics": {
                    "total_authors": coauthorship_data.get("collaboration_networks", {}).get("total_authors", 0),
                    "total_collaborations": coauthorship_data.get("collaboration_networks", {}).get("total_collaborations", 0),
                    "top_researchers": coauthorship_data.get("key_researchers", [])[:5]
                }
            }
        
        if include_organizations:
            logger.info("Fetching organization data for summary")
            org_data = await entity_service.analyze_organization_relationships()
            summary["organizations"] = {
                "key_metrics": {
                    "university_industry_partnerships": len(org_data.get("university_industry_partnerships", [])),
                    "cross_institutional_projects": len(org_data.get("cross_institutional_projects", [])),
                    "top_collaboration_pairs": org_data.get("collaboration_strength", [])[:3]
                }
            }
        
        if include_geographic:
            logger.info("Fetching geographic data for summary")
            geo_data = await entity_service.analyze_geographic_collaboration()
            summary["geographic"] = {
                "key_metrics": {
                    "collaboration_hubs": geo_data.get("collaboration_hubs", [])[:3],
                    "cross_country_collaborations": len(geo_data.get("cross_country_collaborations", [])),
                    "regional_patterns": geo_data.get("regional_collaboration_patterns", {})
                }
            }
        
        if include_temporal:
            logger.info("Fetching temporal data for summary")
            temporal_data = await entity_service.analyze_temporal_relationships()
            summary["temporal"] = {
                "key_metrics": {
                    "collaboration_velocity": temporal_data.get("collaboration_velocity", {}),
                    "long_term_partnerships": len(temporal_data.get("long_term_partnerships", [])),
                    "emerging_trends": temporal_data.get("emerging_collaboration_trends", [])[:3]
                }
            }
        
        return {
            "status": "success",
            "data": summary,
            "description": "Comprehensive collaboration patterns summary",
            "included_analyses": [
                analysis for analysis, include in [
                    ("coauthorship", include_coauthorship),
                    ("organizations", include_organizations), 
                    ("geographic", include_geographic),
                    ("temporal", include_temporal)
                ] if include
            ]
        }
        
    except Exception as e:
        logger.error(f"Error generating collaboration summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate collaboration summary")


@router.get("/key-researchers")
@limiter.limit("30/minute") 
async def get_key_researchers(
    request: Request,
    limit: int = Query(20, ge=1, le=50, description="Maximum number of researchers to return"),
    min_publications: int = Query(2, ge=1, description="Minimum number of publications"),
    focus_african: bool = Query(False, description="Focus on researchers with high African relevance")
):
    """
    Get key researchers based on various criteria
    """
    try:
        coauthorship_data = await coauthorship_service.extract_coauthorship_networks()
        key_researchers = coauthorship_data.get("key_researchers", [])
        
        # Filter by minimum publications
        filtered_researchers = [
            researcher for researcher in key_researchers 
            if researcher.get("publication_count", 0) >= min_publications
        ]
        
        # Filter by African focus if requested
        if focus_african:
            filtered_researchers = [
                researcher for researcher in filtered_researchers
                if researcher.get("african_focus_ratio", 0) > 0.3  # 30% African focus threshold
            ]
        
        # Apply limit
        limited_researchers = filtered_researchers[:limit]
        
        return {
            "status": "success",
            "data": {
                "researchers": limited_researchers,
                "total_found": len(filtered_researchers),
                "filters_applied": {
                    "min_publications": min_publications,
                    "focus_african": focus_african,
                    "limit": limit
                }
            },
            "description": f"Key researchers with at least {min_publications} publications"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving key researchers: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve key researchers")


@router.get("/collaboration-hubs")
@limiter.limit("30/minute")
async def get_collaboration_hubs(
    request: Request,
    hub_type: str = Query("geographic", description="Type of hubs: 'geographic' or 'organizational'"),
    min_score: float = Query(0.0, ge=0.0, description="Minimum hub score threshold")
):
    """
    Get collaboration hubs by type (geographic or organizational)
    """
    try:
        if hub_type == "geographic":
            geo_data = await entity_service.analyze_geographic_collaboration()
            hubs = geo_data.get("collaboration_hubs", [])
            
            # Filter by minimum score
            filtered_hubs = [
                hub for hub in hubs 
                if hub.get("hub_score", 0) >= min_score
            ]
            
            return {
                "status": "success", 
                "data": {
                    "hubs": filtered_hubs,
                    "hub_type": "geographic",
                    "description": "Countries/regions serving as collaboration hubs"
                }
            }
            
        elif hub_type == "organizational":
            org_data = await entity_service.analyze_organization_relationships()
            org_networks = org_data.get("organization_networks", {})
            org_metrics = org_networks.get("organization_metrics", {})
            
            # Convert to hub format and filter
            org_hubs = [
                {
                    "organization": org_name,
                    "hub_score": metrics.get("collaborator_count", 0) + 
                               metrics.get("geographic_reach", 0) +
                               metrics.get("domain_diversity", 0),
                    "collaborator_count": metrics.get("collaborator_count", 0),
                    "geographic_reach": metrics.get("geographic_reach", 0),
                    "domain_diversity": metrics.get("domain_diversity", 0)
                }
                for org_name, metrics in org_metrics.items()
                if (metrics.get("collaborator_count", 0) + 
                   metrics.get("geographic_reach", 0) +
                   metrics.get("domain_diversity", 0)) >= min_score
            ]
            
            # Sort by hub score
            org_hubs.sort(key=lambda x: x["hub_score"], reverse=True)
            
            return {
                "status": "success",
                "data": {
                    "hubs": org_hubs,
                    "hub_type": "organizational", 
                    "description": "Organizations serving as collaboration hubs"
                }
            }
            
        else:
            raise HTTPException(status_code=400, detail="hub_type must be 'geographic' or 'organizational'")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving collaboration hubs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve collaboration hubs")


@router.get("/research-clusters")
@limiter.limit("20/minute")
async def get_research_clusters(
    request: Request,
    min_size: int = Query(3, ge=2, description="Minimum cluster size"),
    max_clusters: int = Query(10, ge=1, le=20, description="Maximum number of clusters to return")
):
    """
    Get research clusters based on co-authorship patterns
    """
    try:
        coauthorship_data = await coauthorship_service.extract_coauthorship_networks()
        clusters = coauthorship_data.get("research_clusters", [])
        
        # Filter by minimum size
        filtered_clusters = [
            cluster for cluster in clusters 
            if cluster.get("size", 0) >= min_size
        ]
        
        # Apply maximum limit
        limited_clusters = filtered_clusters[:max_clusters]
        
        return {
            "status": "success",
            "data": {
                "clusters": limited_clusters,
                "total_clusters": len(filtered_clusters),
                "filters_applied": {
                    "min_size": min_size,
                    "max_clusters": max_clusters
                }
            },
            "description": f"Research clusters with at least {min_size} members"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving research clusters: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve research clusters")


@router.get("/partnership-analysis")
@limiter.limit("20/minute")
async def get_partnership_analysis(
    request: Request,
    partnership_type: str = Query("all", description="Type: 'university_industry', 'cross_institutional', or 'all'"),
    country: Optional[str] = Query(None, description="Filter by specific country")
):
    """
    Analyze different types of partnerships
    """
    try:
        org_data = await entity_service.analyze_organization_relationships()
        
        partnerships = {}
        
        if partnership_type in ["university_industry", "all"]:
            ui_partnerships = org_data.get("university_industry_partnerships", [])
            if country:
                ui_partnerships = [
                    p for p in ui_partnerships 
                    if p.get("country", "").lower() == country.lower()
                ]
            partnerships["university_industry"] = ui_partnerships
        
        if partnership_type in ["cross_institutional", "all"]:
            ci_partnerships = org_data.get("cross_institutional_projects", [])
            if country:
                ci_partnerships = [
                    p for p in ci_partnerships 
                    if p.get("country", "").lower() == country.lower()
                ]
            partnerships["cross_institutional"] = ci_partnerships
        
        # Add collaboration strength data
        partnerships["collaboration_strength"] = org_data.get("collaboration_strength", [])
        
        return {
            "status": "success",
            "data": partnerships,
            "description": f"Partnership analysis for type: {partnership_type}",
            "filters_applied": {
                "partnership_type": partnership_type,
                "country": country
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing partnerships: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze partnerships")


@router.get("/entity-frequency")
@limiter.limit("30/minute")
async def get_entity_frequency(
    request: Request,
    entity_type: str = Query("all", description="Type: 'organizations', 'technologies', 'locations', 'people', or 'all'"),
    top_n: int = Query(10, ge=1, le=50, description="Number of top entities to return")
):
    """
    Get frequency analysis of different entity types
    """
    try:
        entity_data = await entity_service.extract_entities_from_text()
        
        result = {}
        
        if entity_type in ["organizations", "all"]:
            org_entities = entity_data.get("organization_entities", {})
            result["organizations"] = {
                "frequency": dict(list(org_entities.get("organization_frequency", {}).items())[:top_n]),
                "total_mentions": org_entities.get("total_organization_mentions", 0)
            }
        
        if entity_type in ["technologies", "all"]:
            tech_entities = entity_data.get("technology_entities", {})
            result["technologies"] = {
                "frequency": dict(list(tech_entities.get("technology_frequency", {}).items())[:top_n]),
                "total_mentions": tech_entities.get("total_technology_mentions", 0),
                "diversity": tech_entities.get("technology_diversity", 0)
            }
        
        if entity_type in ["locations", "all"]:
            location_entities = entity_data.get("location_entities", {})
            result["locations"] = {
                "frequency": dict(list(location_entities.get("location_frequency", {}).items())[:top_n]),
                "mentioned_countries": location_entities.get("mentioned_countries", 0)
            }
        
        if entity_type in ["people", "all"]:
            person_entities = entity_data.get("person_entities", {})
            result["people"] = {
                "frequency": dict(list(person_entities.get("frequent_authors", {}).items())[:top_n]),
                "total_unique_authors": person_entities.get("total_unique_authors", 0),
                "prolific_authors": person_entities.get("prolific_authors", 0)
            }
        
        return {
            "status": "success",
            "data": result,
            "description": f"Entity frequency analysis for type: {entity_type}",
            "parameters": {
                "entity_type": entity_type,
                "top_n": top_n
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting entity frequency: {e}")
        raise HTTPException(status_code=500, detail="Failed to get entity frequency")


@router.get("/health")
async def health_check():
    """Health check endpoint for entity relationships API"""
    return {
        "status": "healthy",
        "service": "entity-relationships",
        "available_endpoints": [
            "/coauthorship-networks",
            "/organization-relationships", 
            "/geographic-collaboration",
            "/temporal-relationships",
            "/entity-extraction",
            "/collaboration-summary",
            "/key-researchers",
            "/collaboration-hubs",
            "/research-clusters",
            "/partnership-analysis",
            "/entity-frequency"
        ]
    }