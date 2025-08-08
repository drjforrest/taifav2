"""
Data Completeness API Endpoints for TAIFA-FIALA
Provides visualization and analysis of missing data across all tables
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from config.database import get_supabase

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/data-completeness", tags=["Data Completeness"])


@router.get("/intelligence-enrichment/missing-data-map")
@limiter.limit("10/minute")
async def get_intelligence_missing_data_map(request: Request):
    """Get comprehensive missing data visualization for intelligence enrichment"""
    try:
        supabase = get_supabase()
        
        # Expected enrichment fields for each table
        enrichment_schema = {
            "publications": {
                "core_fields": ["title", "abstract", "publication_date", "authors"],
                "enrichment_fields": [
                    "development_stage", "stage_confidence", "stage_indicators",
                    "business_model", "business_model_confidence", "target_markets",
                    "extracted_technologies", "impact_metrics",
                    "african_relevance_score", "ai_relevance_score"
                ]
            },
            "innovations": {
                "core_fields": ["title", "description", "domain", "development_stage"],
                "enrichment_fields": [
                    "ai_techniques_used", "target_beneficiaries", "problem_addressed",
                    "technical_approach", "performance_metrics", "funding_sources",
                    "impact_data", "verification_status", "countries_deployed"
                ]
            },
            "intelligence_reports": {
                "core_fields": ["title", "report_type", "summary"],
                "enrichment_fields": [
                    "key_findings", "innovations_mentioned", "funding_updates",
                    "confidence_score", "sources", "geographic_focus",
                    "follow_up_actions", "validation_flags"
                ]
            }
        }
        
        missing_data_map = {}
        
        for table_name, schema in enrichment_schema.items():
            try:
                # Check if table exists and get data
                if table_name == "intelligence_reports":
                    # This table might not exist yet
                    try:
                        response = supabase.table(table_name).select("*").limit(100).execute()
                        records = response.data if response.data else []
                    except Exception:
                        # Table doesn't exist, create placeholder
                        records = []
                        logger.info(f"Table {table_name} doesn't exist yet")
                else:
                    response = supabase.table(table_name).select("*").limit(100).execute()
                    records = response.data if response.data else []
                
                # Analyze missing data for this table
                table_analysis = analyze_table_completeness(records, schema)
                missing_data_map[table_name] = table_analysis
                
            except Exception as e:
                logger.error(f"Error analyzing table {table_name}: {e}")
                missing_data_map[table_name] = {
                    "error": str(e),
                    "total_records": 0,
                    "completeness_matrix": [],
                    "field_completeness": {},
                    "overall_completeness": 0.0
                }
        
        # Generate recommendations
        recommendations = generate_enrichment_recommendations(missing_data_map)
        
        return {
            "missing_data_map": missing_data_map,
            "recommendations": recommendations,
            "analysis_timestamp": datetime.now().isoformat(),
            "summary": {
                "tables_analyzed": len(missing_data_map),
                "total_records_analyzed": sum(
                    table.get("total_records", 0) 
                    for table in missing_data_map.values()
                ),
                "intelligence_table_exists": "intelligence_reports" in missing_data_map and 
                                           missing_data_map["intelligence_reports"].get("total_records", 0) > 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating missing data map: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate missing data map: {str(e)}")


@router.get("/enrichment-gaps/analysis")
@limiter.limit("10/minute") 
async def get_enrichment_gaps_analysis(request: Request):
    """Get detailed analysis of enrichment gaps and their impact"""
    try:
        supabase = get_supabase()
        
        # Analyze publications enrichment gaps
        publications_response = supabase.table('publications').select(
            'id, title, development_stage, business_model, extracted_technologies, impact_metrics, african_relevance_score'
        ).execute()
        
        publications = publications_response.data if publications_response.data else []
        
        # Analyze innovations enrichment gaps
        innovations_response = supabase.table('innovations').select(
            'id, title, ai_techniques_used, technical_approach, performance_metrics, impact_data'
        ).execute()
        
        innovations = innovations_response.data if innovations_response.data else []
        
        # Check for intelligence reports
        intelligence_reports = []
        try:
            reports_response = supabase.table('intelligence_reports').select('*').execute()
            intelligence_reports = reports_response.data if reports_response.data else []
        except Exception:
            pass  # Table doesn't exist
        
        # Analyze gaps
        gaps_analysis = {
            "publications_gaps": analyze_publication_enrichment_gaps(publications),
            "innovations_gaps": analyze_innovation_enrichment_gaps(innovations),
            "intelligence_gaps": analyze_intelligence_gaps(intelligence_reports),
            "critical_missing_data": identify_critical_missing_data(publications, innovations, intelligence_reports),
            "enrichment_priority": calculate_enrichment_priority(publications, innovations)
        }
        
        return {
            "gaps_analysis": gaps_analysis,
            "analysis_timestamp": datetime.now().isoformat(),
            "actionable_insights": generate_actionable_insights(gaps_analysis)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing enrichment gaps: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze enrichment gaps: {str(e)}")


def analyze_table_completeness(records: List[Dict], schema: Dict) -> Dict[str, Any]:
    """Analyze completeness for a single table"""
    if not records:
        return {
            "total_records": 0,
            "completeness_matrix": [],
            "field_completeness": {},
            "overall_completeness": 0.0,
            "missing_data_patterns": []
        }
    
    all_fields = schema["core_fields"] + schema["enrichment_fields"]
    completeness_matrix = []
    field_completeness = {}
    
    # Analyze each record
    for record in records:
        record_completeness = {}
        for field in all_fields:
            has_data = field in record and record[field] is not None
            
            # Special handling for different data types
            if has_data:
                value = record[field]
                if isinstance(value, str) and not value.strip():
                    has_data = False
                elif isinstance(value, list) and len(value) == 0:
                    has_data = False
                elif isinstance(value, dict) and len(value) == 0:
                    has_data = False
            
            record_completeness[field] = has_data
        
        completeness_matrix.append(record_completeness)
    
    # Calculate field-level completeness
    for field in all_fields:
        complete_count = sum(1 for record in completeness_matrix if record.get(field, False))
        field_completeness[field] = {
            "completeness_percentage": (complete_count / len(records)) * 100,
            "complete_records": complete_count,
            "missing_records": len(records) - complete_count,
            "field_type": "core" if field in schema["core_fields"] else "enrichment"
        }
    
    # Calculate overall completeness
    total_possible_values = len(records) * len(all_fields)
    total_complete_values = sum(
        sum(1 for field, has_data in record.items() if has_data)
        for record in completeness_matrix
    )
    overall_completeness = (total_complete_values / total_possible_values) * 100 if total_possible_values > 0 else 0
    
    return {
        "total_records": len(records),
        "completeness_matrix": completeness_matrix,
        "field_completeness": field_completeness,
        "overall_completeness": overall_completeness,
        "core_fields_completeness": calculate_section_completeness(field_completeness, schema["core_fields"]),
        "enrichment_fields_completeness": calculate_section_completeness(field_completeness, schema["enrichment_fields"])
    }


def calculate_section_completeness(field_completeness: Dict, fields: List[str]) -> float:
    """Calculate average completeness for a section of fields"""
    if not fields:
        return 0.0
    
    total_completeness = sum(
        field_completeness.get(field, {}).get("completeness_percentage", 0) 
        for field in fields
    )
    return total_completeness / len(fields)


def analyze_publication_enrichment_gaps(publications: List[Dict]) -> Dict[str, Any]:
    """Analyze specific gaps in publication enrichment"""
    gaps = {
        "development_stage_missing": 0,
        "business_model_missing": 0,
        "technologies_missing": 0,
        "impact_metrics_missing": 0,
        "african_relevance_missing": 0,
        "total_publications": len(publications)
    }
    
    for pub in publications:
        if not pub.get("development_stage"):
            gaps["development_stage_missing"] += 1
        if not pub.get("business_model"):
            gaps["business_model_missing"] += 1
        if not pub.get("extracted_technologies") or len(pub.get("extracted_technologies", [])) == 0:
            gaps["technologies_missing"] += 1
        if not pub.get("impact_metrics") or len(pub.get("impact_metrics", {})) == 0:
            gaps["impact_metrics_missing"] += 1
        if pub.get("african_relevance_score", 0) == 0:
            gaps["african_relevance_missing"] += 1
    
    # Calculate percentages
    total = gaps["total_publications"]
    if total > 0:
        for key in gaps:
            if key.endswith("_missing"):
                gaps[f"{key}_percentage"] = (gaps[key] / total) * 100
    
    return gaps


def analyze_innovation_enrichment_gaps(innovations: List[Dict]) -> Dict[str, Any]:
    """Analyze specific gaps in innovation enrichment"""
    gaps = {
        "ai_techniques_missing": 0,
        "technical_approach_missing": 0,
        "performance_metrics_missing": 0,
        "impact_data_missing": 0,
        "total_innovations": len(innovations)
    }
    
    for innovation in innovations:
        if not innovation.get("ai_techniques_used") or len(innovation.get("ai_techniques_used", [])) == 0:
            gaps["ai_techniques_missing"] += 1
        if not innovation.get("technical_approach"):
            gaps["technical_approach_missing"] += 1
        if not innovation.get("performance_metrics") or len(innovation.get("performance_metrics", {})) == 0:
            gaps["performance_metrics_missing"] += 1
        if not innovation.get("impact_data") or len(innovation.get("impact_data", {})) == 0:
            gaps["impact_data_missing"] += 1
    
    # Calculate percentages
    total = gaps["total_innovations"]
    if total > 0:
        for key in gaps:
            if key.endswith("_missing"):
                gaps[f"{key}_percentage"] = (gaps[key] / total) * 100
    
    return gaps


def analyze_intelligence_gaps(intelligence_reports: List[Dict]) -> Dict[str, Any]:
    """Analyze gaps in intelligence reports"""
    return {
        "reports_exist": len(intelligence_reports) > 0,
        "total_reports": len(intelligence_reports),
        "recent_reports": len([
            r for r in intelligence_reports 
            if r.get("generation_timestamp") and 
               datetime.fromisoformat(r["generation_timestamp"]) > datetime.now() - timedelta(days=7)
        ]) if intelligence_reports else 0,
        "intelligence_gap_severity": "critical" if len(intelligence_reports) == 0 else "moderate"
    }


def identify_critical_missing_data(publications: List[Dict], innovations: List[Dict], reports: List[Dict]) -> List[Dict[str, Any]]:
    """Identify the most critical missing data points"""
    critical_gaps = []
    
    # Critical gap: No intelligence reports
    if len(reports) == 0:
        critical_gaps.append({
            "type": "intelligence_reports",
            "severity": "critical",
            "description": "No AI intelligence reports found - enrichment pipeline not functioning",
            "impact": "Cannot track AI ecosystem trends, funding, or innovation patterns",
            "affected_records": 0,
            "recommended_action": "Configure and run intelligence enrichment pipeline"
        })
    
    # Critical gap: High percentage of publications without enrichment
    if publications:
        enriched_publications = sum(1 for p in publications if p.get("development_stage") or p.get("extracted_technologies"))
        enrichment_rate = (enriched_publications / len(publications)) * 100
        
        if enrichment_rate < 30:
            critical_gaps.append({
                "type": "publication_enrichment",
                "severity": "high",
                "description": f"Only {enrichment_rate:.1f}% of publications have enrichment data",
                "impact": "Cannot identify commercialization potential or technology trends",
                "affected_records": len(publications) - enriched_publications,
                "recommended_action": "Run metadata enhancement on publications"
            })
    
    # Critical gap: Innovations without technical details
    if innovations:
        technical_innovations = sum(1 for i in innovations if i.get("ai_techniques_used") or i.get("technical_approach"))
        technical_rate = (technical_innovations / len(innovations)) * 100
        
        if technical_rate < 50:
            critical_gaps.append({
                "type": "innovation_technical_data",
                "severity": "medium",
                "description": f"Only {technical_rate:.1f}% of innovations have technical details",
                "impact": "Limited ability to analyze innovation patterns and technical approaches",
                "affected_records": len(innovations) - technical_innovations,
                "recommended_action": "Enhance innovation data collection and processing"
            })
    
    return critical_gaps


def calculate_enrichment_priority(publications: List[Dict], innovations: List[Dict]) -> List[Dict[str, Any]]:
    """Calculate priority scores for enrichment tasks"""
    priorities = []
    
    # Publication enrichment priority
    if publications:
        recent_publications = [
            p for p in publications 
            if p.get("publication_date") and 
               datetime.strptime(p["publication_date"], "%Y-%m-%d") > datetime.now() - timedelta(days=365)
        ]
        
        priorities.append({
            "task": "publication_metadata_enhancement",
            "priority_score": min(100, len(recent_publications) * 2),
            "justification": f"{len(recent_publications)} recent publications need enrichment",
            "estimated_effort": "Medium",
            "expected_impact": "High - enables commercialization analysis"
        })
    
    # Intelligence synthesis priority
    priorities.append({
        "task": "intelligence_synthesis",
        "priority_score": 95,
        "justification": "Critical for ecosystem monitoring and trend analysis",
        "estimated_effort": "High",
        "expected_impact": "Critical - enables comprehensive AI ecosystem insights"
    })
    
    return sorted(priorities, key=lambda x: x["priority_score"], reverse=True)


def generate_enrichment_recommendations(missing_data_map: Dict) -> List[str]:
    """Generate actionable recommendations based on missing data analysis"""
    recommendations = []
    
    # Check intelligence reports
    intelligence_data = missing_data_map.get("intelligence_reports", {})
    if intelligence_data.get("total_records", 0) == 0:
        recommendations.append(
            "🔴 CRITICAL: Create intelligence_reports table and run intelligence enrichment pipeline"
        )
        recommendations.append(
            "Configure PERPLEXITY_API_KEY and set DISABLE_AI_ENRICHMENT=false in production"
        )
    
    # Check publication enrichment
    publications_data = missing_data_map.get("publications", {})
    if publications_data.get("enrichment_fields_completeness", 0) < 30:
        recommendations.append(
            "🟡 HIGH: Run metadata enhancement on publications to extract development stages and business models"
        )
    
    # Check innovation enrichment
    innovations_data = missing_data_map.get("innovations", {})
    if innovations_data.get("enrichment_fields_completeness", 0) < 50:
        recommendations.append(
            "🟠 MEDIUM: Enhance innovation data with technical approaches and performance metrics"
        )
    
    if len(recommendations) == 0:
        recommendations.append("✅ Data enrichment appears to be functioning well!")
    
    return recommendations


def generate_actionable_insights(gaps_analysis: Dict) -> List[str]:
    """Generate actionable insights from gaps analysis"""
    insights = []
    
    intelligence_gaps = gaps_analysis.get("intelligence_gaps", {})
    if intelligence_gaps.get("intelligence_gap_severity") == "critical":
        insights.append(
            "The intelligence enrichment pipeline is not running - this is blocking ecosystem trend analysis"
        )
    
    critical_gaps = gaps_analysis.get("critical_missing_data", [])
    for gap in critical_gaps:
        if gap.get("severity") == "critical":
            insights.append(f"Critical: {gap.get('description')} - {gap.get('recommended_action')}")
    
    enrichment_priorities = gaps_analysis.get("enrichment_priority", [])
    if enrichment_priorities:
        top_priority = enrichment_priorities[0]
        insights.append(f"Top Priority: {top_priority.get('task')} - {top_priority.get('justification')}")
    
    return insights