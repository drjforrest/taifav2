"""
Cross-Table Deduplication API Endpoints
Provides endpoints for managing duplicates across publications, articles, and innovations
"""

from typing import Dict, List, Optional
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address

from services.cross_table_deduplication import (
    get_cross_table_deduplication_service,
    CrossTableDeduplicationService,
)
from config.database import get_supabase


# Initialize router and limiter
router = APIRouter(prefix="/api/deduplication", tags=["deduplication"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/stats")
@limiter.limit("20/minute")
async def get_deduplication_stats(
    request: Request,
    dedup_service: CrossTableDeduplicationService = Depends(get_cross_table_deduplication_service)
):
    """Get comprehensive deduplication statistics"""
    try:
        stats = await dedup_service.get_duplicate_stats()
        
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting deduplication stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get deduplication statistics")


@router.post("/scan")
@limiter.limit("3/minute")  # Limited because this is a heavy operation
async def trigger_deduplication_scan(
    request: Request,
    background_tasks: BackgroundTasks,
    tables: Optional[List[str]] = Query(None, description="Tables to scan (default: all)"),
    max_records_per_table: int = Query(1000, ge=100, le=5000, description="Max records per table"),
    dedup_service: CrossTableDeduplicationService = Depends(get_cross_table_deduplication_service)
):
    """Trigger a full deduplication scan across specified tables"""
    try:
        if tables is None:
            tables = ['publications', 'articles', 'innovations']
        
        # Validate table names
        valid_tables = ['publications', 'articles', 'innovations']
        invalid_tables = [t for t in tables if t not in valid_tables]
        if invalid_tables:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid table names: {invalid_tables}. Valid options: {valid_tables}"
            )
        
        # Run scan in background
        background_tasks.add_task(
            run_deduplication_scan_task,
            tables,
            max_records_per_table
        )
        
        logger.info(f"Deduplication scan triggered for tables: {tables}")
        
        return {
            "status": "started",
            "message": f"Deduplication scan started for {len(tables)} tables",
            "tables": tables,
            "max_records_per_table": max_records_per_table,
            "estimated_duration": f"{len(tables) * 2}-{len(tables) * 5} minutes"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering deduplication scan: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger deduplication scan")


@router.post("/check-record")
@limiter.limit("30/minute")
async def check_record_for_duplicates(
    request: Request,
    record_id: str,
    table: str,
    auto_mark: bool = Query(True, description="Automatically mark found duplicates"),
    dedup_service: CrossTableDeduplicationService = Depends(get_cross_table_deduplication_service)
):
    """Check a specific record for duplicates across other tables"""
    try:
        # Validate table name
        valid_tables = ['publications', 'articles', 'innovations']
        if table not in valid_tables:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid table name: {table}. Valid options: {valid_tables}"
            )
        
        # Get record from database
        supabase = get_supabase()
        response = supabase.table(table).select('*').eq('id', record_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Record not found in {table}")
        
        record = response.data[0]
        
        # Check for duplicates
        duplicates = await dedup_service.process_record_for_duplicates(
            record, table, auto_mark=auto_mark
        )
        
        result = {
            "record_id": record_id,
            "table": table,
            "duplicates_found": len(duplicates),
            "duplicates": [
                {
                    "target_table": dup.target_table,
                    "target_id": dup.target_id,
                    "match_type": dup.match_type,
                    "confidence_score": dup.confidence_score,
                    "matching_fields": dup.matching_fields,
                    "marked": auto_mark
                }
                for dup in duplicates
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        if duplicates:
            logger.info(f"Found {len(duplicates)} duplicates for {table}:{record_id}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking record for duplicates: {e}")
        raise HTTPException(status_code=500, detail="Failed to check record for duplicates")


@router.get("/records/{record_id}")
@limiter.limit("60/minute")
async def get_record_duplicate_info(
    record_id: str,
    table: str,
    request: Request,
):
    """Get duplicate information for a specific record"""
    try:
        valid_tables = ['publications', 'articles', 'innovations']
        if table not in valid_tables:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid table name: {table}. Valid options: {valid_tables}"
            )
        
        supabase = get_supabase()
        
        # Get the record's duplicate metadata
        record_response = supabase.table(table).select('duplicate_metadata').eq('id', record_id).execute()
        
        if not record_response.data:
            raise HTTPException(status_code=404, detail=f"Record not found in {table}")
        
        duplicate_metadata = record_response.data[0].get('duplicate_metadata')
        
        # Get duplicate tracking records where this record is involved
        as_source = supabase.table('duplicate_records').select('*').eq('source_table', table).eq('source_id', record_id).execute()
        as_target = supabase.table('duplicate_records').select('*').eq('target_table', table).eq('target_id', record_id).execute()
        
        return {
            "record_id": record_id,
            "table": table,
            "is_duplicate": duplicate_metadata is not None,
            "duplicate_metadata": duplicate_metadata,
            "duplicate_relationships": {
                "as_source": as_source.data or [],
                "as_target": as_target.data or [],
                "total_relationships": len(as_source.data or []) + len(as_target.data or [])
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting record duplicate info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get record duplicate information")


@router.put("/records/{duplicate_record_id}/status")
@limiter.limit("20/minute")
async def update_duplicate_status(
    duplicate_record_id: str,
    new_status: str,
    request: Request,
):
    """Update the status of a duplicate record"""
    try:
        valid_statuses = ['active', 'resolved', 'false_positive']
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status: {new_status}. Valid options: {valid_statuses}"
            )
        
        supabase = get_supabase()
        
        # Update the duplicate record status
        response = supabase.table('duplicate_records').update({
            'status': new_status,
            'updated_at': datetime.now().isoformat()
        }).eq('id', duplicate_record_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Duplicate record not found")
        
        updated_record = response.data[0]
        
        # If marking as resolved or false positive, optionally clear the duplicate_metadata
        if new_status in ['resolved', 'false_positive']:
            # Clear duplicate metadata from the source record
            source_table = updated_record.get('source_table')
            source_id = updated_record.get('source_id')
            
            if source_table and source_id:
                supabase.table(source_table).update({
                    'duplicate_metadata': None
                }).eq('id', source_id).execute()
        
        return {
            "duplicate_record_id": duplicate_record_id,
            "old_status": "active",  # Could track this if needed
            "new_status": new_status,
            "updated_record": updated_record,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating duplicate status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update duplicate status")


@router.get("/duplicates")
@limiter.limit("30/minute")
async def get_duplicate_records(
    request: Request,
    table: Optional[str] = Query(None, description="Filter by source table"),
    match_type: Optional[str] = Query(None, description="Filter by match type"),
    status: str = Query('active', description="Filter by status"),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="Minimum confidence score"),
    limit: int = Query(50, ge=1, le=200, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Get a list of duplicate records with filtering options"""
    try:
        supabase = get_supabase()
        
        # Build query
        query = supabase.table('duplicate_records').select('*')
        
        # Apply filters
        if table:
            valid_tables = ['publications', 'articles', 'innovations']
            if table not in valid_tables:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid table name: {table}. Valid options: {valid_tables}"
                )
            query = query.eq('source_table', table)
        
        if match_type:
            valid_types = ['exact', 'metadata', 'semantic', 'fuzzy']
            if match_type not in valid_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid match type: {match_type}. Valid options: {valid_types}"
                )
            query = query.eq('match_type', match_type)
        
        query = query.eq('status', status)
        query = query.gte('confidence_score', min_confidence)
        
        # Apply ordering and pagination
        query = query.order('confidence_score', desc=True)
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        # Get total count for pagination
        count_query = supabase.table('duplicate_records').select('id', count='exact')
        if table:
            count_query = count_query.eq('source_table', table)
        if match_type:
            count_query = count_query.eq('match_type', match_type)
        count_query = count_query.eq('status', status)
        count_query = count_query.gte('confidence_score', min_confidence)
        
        count_response = count_query.execute()
        total = count_response.count or 0
        
        return {
            "duplicates": response.data or [],
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            },
            "filters": {
                "table": table,
                "match_type": match_type,
                "status": status,
                "min_confidence": min_confidence
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting duplicate records: {e}")
        raise HTTPException(status_code=500, detail="Failed to get duplicate records")


@router.get("/analysis")
@limiter.limit("10/minute")
async def get_duplicate_analysis(request: Request):
    """Get aggregated duplicate analysis and patterns"""
    try:
        supabase = get_supabase()
        
        # Use the duplicate_analysis view we created
        analysis_response = supabase.from_('duplicate_analysis').select('*').execute()
        
        # Get some additional statistics
        stats_response = supabase.table('duplicate_records').select('*').execute()
        duplicate_records = stats_response.data or []
        
        # Calculate additional metrics
        total_duplicates = len(duplicate_records)
        
        confidence_distribution = {
            'high_confidence': len([r for r in duplicate_records if r.get('confidence_score', 0) >= 0.9]),
            'medium_confidence': len([r for r in duplicate_records if 0.7 <= r.get('confidence_score', 0) < 0.9]),
            'low_confidence': len([r for r in duplicate_records if r.get('confidence_score', 0) < 0.7])
        }
        
        status_distribution = {}
        for record in duplicate_records:
            status = record.get('status', 'unknown')
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        return {
            "analysis_view": analysis_response.data or [],
            "summary": {
                "total_duplicate_relationships": total_duplicates,
                "confidence_distribution": confidence_distribution,
                "status_distribution": status_distribution,
                "duplicate_detection_rate": {
                    "high_precision": len([r for r in duplicate_records if r.get('confidence_score', 0) >= 0.95]),
                    "medium_precision": len([r for r in duplicate_records if 0.8 <= r.get('confidence_score', 0) < 0.95]),
                    "needs_review": len([r for r in duplicate_records if r.get('confidence_score', 0) < 0.8])
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting duplicate analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to get duplicate analysis")


@router.get("/count/{table}")
@limiter.limit("60/minute")
async def get_non_duplicate_count(
    table: str,
    request: Request,
    dedup_service: CrossTableDeduplicationService = Depends(get_cross_table_deduplication_service)
):
    """Get count of non-duplicate records in a table"""
    try:
        valid_tables = ['publications', 'articles', 'innovations']
        if table not in valid_tables:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid table name: {table}. Valid options: {valid_tables}"
            )
        
        non_duplicate_count = await dedup_service.get_non_duplicate_count(table)
        
        # Also get total count for comparison
        supabase = get_supabase()
        total_response = supabase.table(table).select('id', count='exact').execute()
        total_count = total_response.count or 0
        
        duplicate_count = total_count - non_duplicate_count
        
        return {
            "table": table,
            "counts": {
                "total_records": total_count,
                "non_duplicate_records": non_duplicate_count,
                "duplicate_records": duplicate_count,
                "duplicate_percentage": round((duplicate_count / max(1, total_count)) * 100, 2)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting non-duplicate count: {e}")
        raise HTTPException(status_code=500, detail="Failed to get record counts")


async def run_deduplication_scan_task(tables: List[str], max_records_per_table: int):
    """Background task to run deduplication scan"""
    try:
        dedup_service = await get_cross_table_deduplication_service()
        
        logger.info(f"Starting deduplication scan for tables: {tables}")
        
        results = await dedup_service.run_full_deduplication_scan(
            tables=tables,
            max_records_per_table=max_records_per_table
        )
        
        total_duplicates = sum(results.values())
        
        logger.info(
            f"Deduplication scan completed. Results: {results}. "
            f"Total duplicates found: {total_duplicates}"
        )
        
    except Exception as e:
        logger.error(f"Deduplication scan task failed: {e}")


# Include this router in main.py by adding:
# from api.deduplication import router as deduplication_router
# app.include_router(deduplication_router)
