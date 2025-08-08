"""
Enhanced Data Completeness API for TAIFA-FIALA
Provides detailed record-level analysis and pattern detection for missing data
"""

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List

from config.database import get_supabase
from fastapi import APIRouter, HTTPException, Query, Request
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix="/api/enhanced-data-completeness", tags=["Enhanced Data Completeness"]
)


@router.get("/record-level-analysis")
@limiter.limit("10/minute")
async def get_record_level_analysis(
    request: Request,
    table_name: str = Query(..., description="Table to analyze"),
    limit: int = Query(100, description="Maximum records to analyze"),
    include_patterns: bool = Query(True, description="Include pattern analysis"),
):
    """Get detailed record-level missing data analysis with pattern detection"""
    try:
        supabase = get_supabase()

        # Define expected fields for each table
        table_schemas = {
            "publications": {
                "core_fields": ["title", "abstract", "publication_date", "authors"],
                "enrichment_fields": [
                    "development_stage",
                    "stage_confidence",
                    "stage_indicators",
                    "business_model",
                    "business_model_confidence",
                    "target_markets",
                    "extracted_technologies",
                    "impact_metrics",
                    "african_relevance_score",
                    "ai_relevance_score",
                ],
                "temporal_field": "publication_date",
                "id_field": "id",
            },
            "innovations": {
                "core_fields": ["title", "description", "domain", "development_stage"],
                "enrichment_fields": [
                    "ai_techniques_used",
                    "target_beneficiaries",
                    "problem_addressed",
                    "technical_approach",
                    "performance_metrics",
                    "funding_sources",
                    "impact_data",
                    "verification_status",
                    "countries_deployed",
                ],
                "temporal_field": "created_at",
                "id_field": "id",
            },
            "intelligence_reports": {
                "core_fields": ["title", "report_type", "summary"],
                "enrichment_fields": [
                    "key_findings",
                    "innovations_mentioned",
                    "funding_updates",
                    "confidence_score",
                    "sources",
                    "geographic_focus",
                    "follow_up_actions",
                    "validation_flags",
                ],
                "temporal_field": "generation_timestamp",
                "id_field": "id",
            },
        }

        if table_name not in table_schemas:
            raise HTTPException(
                status_code=400, detail=f"Unsupported table: {table_name}"
            )

        schema = table_schemas[table_name]
        all_fields = schema["core_fields"] + schema["enrichment_fields"]

        # Fetch records
        try:
            response = supabase.table(table_name).select("*").limit(limit).execute()
            records = response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching records from {table_name}: {e}")
            records = []

        if not records:
            return {
                "table_name": table_name,
                "total_records": 0,
                "record_analysis": [],
                "pattern_analysis": {},
                "error": f"No records found in {table_name}",
            }

        # Analyze each record
        record_analysis = []
        for record in records:
            analysis = analyze_single_record(record, schema, all_fields)
            record_analysis.append(analysis)

        # Pattern analysis
        pattern_analysis = {}
        if include_patterns:
            pattern_analysis = detect_missingness_patterns(record_analysis, schema)

        return {
            "table_name": table_name,
            "total_records": len(records),
            "record_analysis": record_analysis,
            "pattern_analysis": pattern_analysis,
            "analysis_timestamp": datetime.now().isoformat(),
            "schema_info": {
                "core_fields": schema["core_fields"],
                "enrichment_fields": schema["enrichment_fields"],
                "total_fields": len(all_fields),
            },
        }

    except Exception as e:
        logger.error(f"Error in record-level analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/pattern-detection")
@limiter.limit("10/minute")
async def get_pattern_detection(
    request: Request,
    table_name: str = Query(..., description="Table to analyze"),
    pattern_type: str = Query(
        "all", description="Type of pattern to detect: correlation, temporal, or all"
    ),
):
    """Detect patterns in missing data that might indicate systematic issues"""
    try:
        # Get record analysis first
        record_response = await get_record_level_analysis(
            request, table_name=table_name, limit=500, include_patterns=False
        )

        if record_response["total_records"] == 0:
            return {
                "table_name": table_name,
                "patterns": {},
                "error": "No records to analyze",
            }

        record_analysis = record_response["record_analysis"]
        schema = record_response["schema_info"]

        patterns = {}

        if pattern_type in ["correlation", "all"]:
            patterns["field_correlations"] = detect_field_correlations(record_analysis)
            patterns["missing_clusters"] = detect_missing_clusters(record_analysis)

        if pattern_type in ["temporal", "all"]:
            patterns["temporal_patterns"] = detect_temporal_patterns(record_analysis)

        if pattern_type in ["systematic", "all"]:
            patterns["systematic_issues"] = detect_systematic_issues(
                record_analysis, schema
            )

        return {
            "table_name": table_name,
            "patterns": patterns,
            "analysis_timestamp": datetime.now().isoformat(),
            "recommendations": generate_pattern_recommendations(patterns),
        }

    except Exception as e:
        logger.error(f"Error in pattern detection: {e}")
        raise HTTPException(
            status_code=500, detail=f"Pattern detection failed: {str(e)}"
        )


@router.get("/problematic-records")
@limiter.limit("10/minute")
async def get_problematic_records(
    request: Request,
    table_name: str = Query(..., description="Table to analyze"),
    min_missing_fields: int = Query(
        3, description="Minimum missing fields to be considered problematic"
    ),
    sort_by: str = Query(
        "missing_count",
        description="Sort by: missing_count, missing_percentage, or record_id",
    ),
):
    """Get records with the most missing data for investigation"""
    try:
        # Get record analysis
        record_response = await get_record_level_analysis(
            request, table_name=table_name, limit=1000, include_patterns=False
        )

        if record_response["total_records"] == 0:
            return {
                "table_name": table_name,
                "problematic_records": [],
                "error": "No records to analyze",
            }

        record_analysis = record_response["record_analysis"]

        # Filter problematic records
        problematic = [
            record
            for record in record_analysis
            if record["missing_fields_count"] >= min_missing_fields
        ]

        # Sort records
        if sort_by == "missing_count":
            problematic.sort(key=lambda x: x["missing_fields_count"], reverse=True)
        elif sort_by == "missing_percentage":
            problematic.sort(key=lambda x: x["missing_percentage"], reverse=True)
        elif sort_by == "record_id":
            problematic.sort(key=lambda x: x["record_id"])

        return {
            "table_name": table_name,
            "total_records_analyzed": len(record_analysis),
            "problematic_records": problematic,
            "summary": {
                "total_problematic": len(problematic),
                "percentage_problematic": (len(problematic) / len(record_analysis))
                * 100,
                "avg_missing_fields": sum(
                    r["missing_fields_count"] for r in problematic
                )
                / len(problematic)
                if problematic
                else 0,
            },
            "analysis_timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error finding problematic records: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to find problematic records: {str(e)}"
        )


def analyze_single_record(
    record: Dict, schema: Dict, all_fields: List[str]
) -> Dict[str, Any]:
    """Analyze a single record for missing data"""
    record_id = record.get(schema["id_field"], "unknown")
    missing_fields = []
    present_fields = []

    for field in all_fields:
        has_data = field in record and record[field] is not None

        # Enhanced data presence check
        if has_data:
            value = record[field]
            if isinstance(value, str) and not value.strip():
                has_data = False
            elif isinstance(value, list) and len(value) == 0:
                has_data = False
            elif isinstance(value, dict) and len(value) == 0:
                has_data = False
            elif (
                isinstance(value, (int, float))
                and value == 0
                and field.endswith("_score")
            ):
                # Special case: scores of 0 might indicate missing data
                has_data = False

        if has_data:
            present_fields.append(field)
        else:
            missing_fields.append(field)

    # Categorize missing fields
    missing_core = [f for f in missing_fields if f in schema["core_fields"]]
    missing_enrichment = [f for f in missing_fields if f in schema["enrichment_fields"]]

    # Calculate temporal info if available
    temporal_info = None
    if schema.get("temporal_field") and record.get(schema["temporal_field"]):
        try:
            temporal_value = record[schema["temporal_field"]]
            if isinstance(temporal_value, str):
                temporal_info = {
                    "date": temporal_value,
                    "days_ago": (
                        datetime.now()
                        - datetime.fromisoformat(temporal_value.replace("Z", "+00:00"))
                    ).days,
                }
        except Exception:
            pass

    return {
        "record_id": record_id,
        "missing_fields": missing_fields,
        "missing_fields_count": len(missing_fields),
        "missing_percentage": (len(missing_fields) / len(all_fields)) * 100,
        "missing_core_fields": missing_core,
        "missing_enrichment_fields": missing_enrichment,
        "present_fields": present_fields,
        "completeness_score": (len(present_fields) / len(all_fields)) * 100,
        "temporal_info": temporal_info,
        "field_analysis": {
            field: {
                "present": field in present_fields,
                "value_type": type(record.get(field)).__name__
                if field in record
                else None,
                "value_length": len(str(record.get(field, "")))
                if field in record
                else 0,
            }
            for field in all_fields
        },
    }


def detect_missingness_patterns(
    record_analysis: List[Dict], schema: Dict
) -> Dict[str, Any]:
    """Detect patterns in missing data across records"""
    patterns = {}

    # Field correlation patterns
    patterns["field_correlations"] = detect_field_correlations(record_analysis)

    # Missing data clusters
    patterns["missing_clusters"] = detect_missing_clusters(record_analysis)

    # Temporal patterns
    patterns["temporal_patterns"] = detect_temporal_patterns(record_analysis)

    # Systematic issues
    patterns["systematic_issues"] = detect_systematic_issues(record_analysis, schema)

    return patterns


def detect_field_correlations(record_analysis: List[Dict]) -> Dict[str, Any]:
    """Detect which fields tend to be missing together"""
    field_pairs = defaultdict(int)
    total_records = len(record_analysis)

    # Count co-occurrences of missing fields
    for record in record_analysis:
        missing = record["missing_fields"]
        for i, field1 in enumerate(missing):
            for field2 in missing[i + 1 :]:
                pair = tuple(sorted([field1, field2]))
                field_pairs[pair] += 1

    # Calculate correlation strength
    strong_correlations = []
    for (field1, field2), count in field_pairs.items():
        correlation_strength = count / total_records
        if correlation_strength > 0.3:  # 30% or more records missing both
            strong_correlations.append(
                {
                    "field1": field1,
                    "field2": field2,
                    "co_missing_count": count,
                    "correlation_strength": correlation_strength,
                    "likely_systematic": correlation_strength > 0.7,
                }
            )

    return {
        "strong_correlations": sorted(
            strong_correlations, key=lambda x: x["correlation_strength"], reverse=True
        ),
        "total_pairs_analyzed": len(field_pairs),
        "systematic_threshold": 0.7,
    }


def detect_missing_clusters(record_analysis: List[Dict]) -> Dict[str, Any]:
    """Detect clusters of records with similar missing data patterns"""
    pattern_counts = Counter()

    for record in record_analysis:
        # Create a signature of missing fields
        missing_signature = tuple(sorted(record["missing_fields"]))
        pattern_counts[missing_signature] += 1

    # Find common patterns
    common_patterns = []
    total_records = len(record_analysis)

    for pattern, count in pattern_counts.most_common(10):
        if count > 1:  # Only patterns that occur multiple times
            common_patterns.append(
                {
                    "missing_fields": list(pattern),
                    "record_count": count,
                    "percentage": (count / total_records) * 100,
                    "likely_systematic": count
                    > total_records * 0.1,  # More than 10% of records
                }
            )

    return {
        "common_patterns": common_patterns,
        "unique_patterns": len(pattern_counts),
        "most_common_pattern_count": pattern_counts.most_common(1)[0][1]
        if pattern_counts
        else 0,
    }


def detect_temporal_patterns(record_analysis: List[Dict]) -> Dict[str, Any]:
    """Detect temporal patterns in missing data"""
    temporal_patterns = {"has_temporal_data": False, "patterns": []}

    # Group records by time periods
    records_with_time = [r for r in record_analysis if r.get("temporal_info")]

    if not records_with_time:
        return temporal_patterns

    temporal_patterns["has_temporal_data"] = True

    # Group by time periods (monthly)
    monthly_stats = defaultdict(
        lambda: {"total": 0, "missing_counts": defaultdict(int)}
    )

    for record in records_with_time:
        try:
            date_str = record["temporal_info"]["date"]
            date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            month_key = f"{date_obj.year}-{date_obj.month:02d}"

            monthly_stats[month_key]["total"] += 1
            for field in record["missing_fields"]:
                monthly_stats[month_key]["missing_counts"][field] += 1
        except Exception:
            continue

    # Analyze trends
    patterns = []
    for month, stats in monthly_stats.items():
        if stats["total"] > 0:
            avg_missing = sum(stats["missing_counts"].values()) / stats["total"]
            patterns.append(
                {
                    "period": month,
                    "total_records": stats["total"],
                    "avg_missing_fields": avg_missing,
                    "most_missing_field": max(
                        stats["missing_counts"].items(), key=lambda x: x[1]
                    )[0]
                    if stats["missing_counts"]
                    else None,
                }
            )

    temporal_patterns["patterns"] = sorted(patterns, key=lambda x: x["period"])

    return temporal_patterns


def detect_systematic_issues(
    record_analysis: List[Dict], schema: Dict
) -> Dict[str, Any]:
    """Detect systematic issues that might indicate code problems"""
    issues = []
    total_records = len(record_analysis)

    # Check for fields that are missing in most records
    field_missing_counts = defaultdict(int)
    for record in record_analysis:
        for field in record["missing_fields"]:
            field_missing_counts[field] += 1

    for field, missing_count in field_missing_counts.items():
        missing_percentage = (missing_count / total_records) * 100

        if missing_percentage > 90:
            issues.append(
                {
                    "type": "almost_always_missing",
                    "field": field,
                    "missing_percentage": missing_percentage,
                    "severity": "critical",
                    "description": f"Field '{field}' is missing in {missing_percentage:.1f}% of records",
                    "likely_cause": "Field not being populated by ETL process or data source issue",
                }
            )
        elif missing_percentage > 70 and field in schema["core_fields"]:
            issues.append(
                {
                    "type": "core_field_mostly_missing",
                    "field": field,
                    "missing_percentage": missing_percentage,
                    "severity": "high",
                    "description": f"Core field '{field}' is missing in {missing_percentage:.1f}% of records",
                    "likely_cause": "Data extraction or processing issue",
                }
            )

    # Check for records with no enrichment data at all
    no_enrichment_count = sum(
        1
        for record in record_analysis
        if all(
            field in record["missing_fields"] for field in schema["enrichment_fields"]
        )
    )

    if no_enrichment_count > total_records * 0.5:
        issues.append(
            {
                "type": "enrichment_pipeline_failure",
                "field": "all_enrichment_fields",
                "missing_percentage": (no_enrichment_count / total_records) * 100,
                "severity": "critical",
                "description": f"{no_enrichment_count} records have no enrichment data at all",
                "likely_cause": "Enrichment pipeline not running or failing systematically",
            }
        )

    return {
        "issues": sorted(issues, key=lambda x: x["missing_percentage"], reverse=True),
        "total_issues": len(issues),
        "critical_issues": len([i for i in issues if i["severity"] == "critical"]),
        "high_issues": len([i for i in issues if i["severity"] == "high"]),
    }


def generate_pattern_recommendations(patterns: Dict) -> List[str]:
    """Generate actionable recommendations based on detected patterns"""
    recommendations = []

    # Field correlation recommendations
    correlations = patterns.get("field_correlations", {}).get("strong_correlations", [])
    for corr in correlations[:3]:  # Top 3 correlations
        if corr["likely_systematic"]:
            recommendations.append(
                f"🔴 SYSTEMATIC: Fields '{corr['field1']}' and '{corr['field2']}' are missing together in "
                f"{corr['correlation_strength']:.1%} of records - check data pipeline"
            )

    # Systematic issues recommendations
    systematic = patterns.get("systematic_issues", {}).get("issues", [])
    for issue in systematic[:3]:  # Top 3 issues
        if issue["severity"] == "critical":
            recommendations.append(
                f"🔴 CRITICAL: {issue['description']} - {issue['likely_cause']}"
            )
        elif issue["severity"] == "high":
            recommendations.append(
                f"🟠 HIGH: {issue['description']} - {issue['likely_cause']}"
            )

    # Temporal pattern recommendations
    temporal = patterns.get("temporal_patterns", {})
    if temporal.get("has_temporal_data") and temporal.get("patterns"):
        recent_patterns = [p for p in temporal["patterns"] if p["period"] >= "2024-01"]
        if recent_patterns:
            avg_recent_missing = sum(
                p["avg_missing_fields"] for p in recent_patterns
            ) / len(recent_patterns)
            if avg_recent_missing > 5:
                recommendations.append(
                    f"🟡 TEMPORAL: Recent records have {avg_recent_missing:.1f} missing fields on average - "
                    "data quality may be declining"
                )

    if not recommendations:
        recommendations.append(
            "✅ No major systematic patterns detected in missing data"
        )

    return recommendations
