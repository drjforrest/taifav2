"""
Manual Documents API
===================

API endpoints for manual document processing service.
Supports uploading, monitoring, and managing manually processed documents.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile
import shutil

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from loguru import logger

from services.manual_document_processor import (
    manual_document_processor, 
    process_single_document,
    DocumentType,
    ProcessingStatus
)
from config.database import get_supabase

router = APIRouter(prefix="/api/manual-documents", tags=["Manual Documents"])


class DocumentUploadResponse(BaseModel):
    """Response for document upload"""
    success: bool
    message: str
    document_id: Optional[str] = None
    file_name: str
    file_size: int
    document_type: str
    estimated_processing_time: str


class ProcessingStatusResponse(BaseModel):
    """Response for processing status"""
    document_id: str
    file_name: str
    status: str
    progress: float  # 0.0 to 1.0
    processing_duration_seconds: Optional[float]
    confidence_score: Optional[float]
    error_message: Optional[str]
    innovations_found: int
    created_at: str


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: str = Form(default="pdf_report"),
    instructions: Optional[str] = Form(default=None),
    custom_prompt: Optional[str] = Form(default=None),
    priority: int = Form(default=1)
):
    """
    Upload a document for manual processing
    
    Args:
        file: PDF file to process
        document_type: Type of document (startup_list, funding_announcement, etc.)
        instructions: Custom instructions for extraction
        custom_prompt: Custom LLM prompt for specialized extraction
        priority: Processing priority (1-5, higher is more urgent)
    """
    
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Validate document type
        try:
            doc_type_enum = DocumentType(document_type)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid document type. Must be one of: {[t.value for t in DocumentType]}"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process document in background
        background_tasks.add_task(
            _process_uploaded_document,
            temp_file_path,
            file.filename,
            document_type,
            instructions,
            custom_prompt,
            priority
        )
        
        # Estimate processing time based on file size and type
        file_size = len(content)
        estimated_time = _estimate_processing_time(file_size, doc_type_enum)
        
        return DocumentUploadResponse(
            success=True,
            message=f"Document uploaded successfully. Processing started.",
            file_name=file.filename,
            file_size=file_size,
            document_type=document_type,
            estimated_processing_time=estimated_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


async def _process_uploaded_document(
    file_path: str,
    file_name: str, 
    document_type: str,
    instructions: Optional[str],
    custom_prompt: Optional[str],
    priority: int
):
    """Process uploaded document in background"""
    try:
        result = await process_single_document(
            file_path=file_path,
            document_type=document_type,
            instructions=instructions,
            custom_prompt=custom_prompt
        )
        
        logger.info(f"Successfully processed uploaded document: {file_name}")
        
    except Exception as e:
        logger.error(f"Error processing uploaded document {file_name}: {e}")
    finally:
        # Clean up temporary file
        try:
            Path(file_path).unlink()
        except Exception:
            pass


def _estimate_processing_time(file_size: int, doc_type: DocumentType) -> str:
    """Estimate processing time based on file size and type"""
    
    # Base time estimates in seconds
    base_time = {
        DocumentType.STARTUP_LIST: 30,
        DocumentType.FUNDING_ANNOUNCEMENT: 20,
        DocumentType.MARKET_REPORT: 45,
        DocumentType.RESEARCH_PAPER: 35,
        DocumentType.NEWS_ARTICLE: 15,
        DocumentType.PDF_REPORT: 25,
        DocumentType.UNKNOWN: 30
    }
    
    # Adjust for file size (rough estimate: 1MB = +10 seconds)
    size_factor = (file_size / 1024 / 1024) * 10  # Convert to MB and multiply by 10
    estimated_seconds = base_time.get(doc_type, 30) + size_factor
    
    if estimated_seconds < 60:
        return f"{int(estimated_seconds)} seconds"
    else:
        return f"{int(estimated_seconds / 60)} minutes"


@router.get("/status", response_model=List[ProcessingStatusResponse])
async def get_processing_status(
    limit: int = Query(20, le=100),
    status_filter: Optional[str] = Query(None),
    document_type_filter: Optional[str] = Query(None)
):
    """Get processing status of documents"""
    
    try:
        supabase = get_supabase()
        
        # Build query
        query = supabase.table("manual_documents").select("*")
        
        if status_filter:
            query = query.eq("processing_status", status_filter)
        
        if document_type_filter:
            query = query.eq("document_type", document_type_filter)
        
        # Execute query
        response = query.order("created_at", desc=True).limit(limit).execute()
        documents = response.data or []
        
        # Convert to response format
        status_list = []
        for doc in documents:
            # Count innovations from this document
            innovations_response = supabase.table("innovations").select("id").eq("source_document_id", doc["id"]).execute()
            innovations_count = len(innovations_response.data or [])
            
            # Calculate progress
            progress = 1.0 if doc["processing_status"] == "completed" else 0.0
            if doc["processing_status"] == "processing":
                progress = 0.5
            elif doc["processing_status"] == "failed":
                progress = 0.0
            
            status_list.append(ProcessingStatusResponse(
                document_id=doc["id"],
                file_name=doc["file_name"],
                status=doc["processing_status"],
                progress=progress,
                processing_duration_seconds=doc.get("processing_duration_seconds"),
                confidence_score=doc.get("confidence_score"),
                error_message=doc.get("error_message"),
                innovations_found=innovations_count,
                created_at=doc["created_at"]
            ))
        
        return status_list
        
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get processing status")


@router.get("/{document_id}")
async def get_document_details(document_id: str):
    """Get detailed information about a processed document"""
    
    try:
        supabase = get_supabase()
        
        # Get document
        doc_response = supabase.table("manual_documents").select("*").eq("id", document_id).execute()
        
        if not doc_response.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = doc_response.data[0]
        
        # Get related innovations
        innovations_response = supabase.table("innovations").select("*").eq("source_document_id", document_id).execute()
        innovations = innovations_response.data or []
        
        return {
            "document": document,
            "innovations_extracted": innovations,
            "extraction_summary": {
                "total_innovations": len(innovations),
                "processing_status": document["processing_status"],
                "confidence_score": document.get("confidence_score", 0.0),
                "processing_time": document.get("processing_duration_seconds"),
                "structured_data_keys": list(document.get("structured_data", {}).keys()) if document.get("structured_data") else []
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get document details")


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    instructions: Optional[str] = Form(default=None),
    custom_prompt: Optional[str] = Form(default=None)
):
    """Reprocess a document with new instructions"""
    
    try:
        supabase = get_supabase()
        
        # Get document
        doc_response = supabase.table("manual_documents").select("*").eq("id", document_id).execute()
        
        if not doc_response.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = doc_response.data[0]
        
        # Check if document is in completed or failed directory
        completed_path = Path("manual_documents/completed") / document["file_name"]
        failed_path = Path("manual_documents/failed") / document["file_name"]
        
        source_path = None
        if completed_path.exists():
            source_path = str(completed_path)
        elif failed_path.exists():
            source_path = str(failed_path)
        else:
            raise HTTPException(status_code=400, detail="Original document file not found")
        
        # Update processing status
        supabase.table("manual_documents").update({
            "processing_status": "processing",
            "processing_instructions": instructions,
            "custom_extraction_prompt": custom_prompt,
            "updated_at": datetime.now().isoformat()
        }).eq("id", document_id).execute()
        
        # Reprocess in background
        background_tasks.add_task(
            _reprocess_existing_document,
            source_path,
            document["document_type"],
            instructions,
            custom_prompt,
            document_id
        )
        
        return {
            "success": True,
            "message": "Document queued for reprocessing",
            "document_id": document_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reprocessing document: {e}")
        raise HTTPException(status_code=500, detail="Failed to reprocess document")


async def _reprocess_existing_document(
    file_path: str,
    document_type: str,
    instructions: Optional[str],
    custom_prompt: Optional[str],
    document_id: str
):
    """Reprocess existing document"""
    try:
        # Create temporary copy
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            with open(file_path, 'rb') as source_file:
                temp_file.write(source_file.read())
            temp_file_path = temp_file.name
        
        # Process document
        result = await process_single_document(
            file_path=temp_file_path,
            document_type=document_type,
            instructions=instructions,
            custom_prompt=custom_prompt
        )
        
        # Update existing record with new results
        supabase = get_supabase()
        supabase.table("manual_documents").update({
            "processing_status": result.status.value,
            "structured_data": result.structured_data,
            "confidence_score": result.confidence_score,
            "processing_duration_seconds": result.processing_duration_seconds,
            "error_message": result.error_message,
            "updated_at": datetime.now().isoformat()
        }).eq("id", document_id).execute()
        
        logger.info(f"Successfully reprocessed document: {document_id}")
        
    except Exception as e:
        logger.error(f"Error reprocessing document {document_id}: {e}")
        
        # Update status to failed
        try:
            supabase = get_supabase()
            supabase.table("manual_documents").update({
                "processing_status": "failed",
                "error_message": str(e),
                "updated_at": datetime.now().isoformat()
            }).eq("id", document_id).execute()
        except Exception:
            pass
    finally:
        # Clean up temporary file
        try:
            Path(temp_file_path).unlink()
        except Exception:
            pass


@router.get("/stats/summary")
async def get_processing_stats():
    """Get processing statistics summary"""
    
    try:
        supabase = get_supabase()
        
        # Get all documents
        response = supabase.table("manual_documents").select("*").execute()
        documents = response.data or []
        
        # Calculate statistics
        stats = {
            "total_documents": len(documents),
            "by_status": {},
            "by_type": {},
            "processing_metrics": {
                "avg_processing_time": 0,
                "avg_confidence_score": 0,
                "total_innovations_extracted": 0
            },
            "recent_activity": []
        }
        
        # Group by status and type
        processing_times = []
        confidence_scores = []
        
        for doc in documents:
            # Status counts
            status = doc["processing_status"]
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Type counts
            doc_type = doc["document_type"]
            stats["by_type"][doc_type] = stats["by_type"].get(doc_type, 0) + 1
            
            # Metrics
            if doc.get("processing_duration_seconds"):
                processing_times.append(doc["processing_duration_seconds"])
            
            if doc.get("confidence_score"):
                confidence_scores.append(doc["confidence_score"])
        
        # Calculate averages
        if processing_times:
            stats["processing_metrics"]["avg_processing_time"] = sum(processing_times) / len(processing_times)
        
        if confidence_scores:
            stats["processing_metrics"]["avg_confidence_score"] = sum(confidence_scores) / len(confidence_scores)
        
        # Get total innovations extracted
        innovations_response = supabase.table("innovations").select("id").not_.is_("source_document_id", "null").execute()
        stats["processing_metrics"]["total_innovations_extracted"] = len(innovations_response.data or [])
        
        # Recent activity (last 5 documents)
        recent_docs = sorted(documents, key=lambda x: x["created_at"], reverse=True)[:5]
        stats["recent_activity"] = [
            {
                "file_name": doc["file_name"],
                "status": doc["processing_status"],
                "document_type": doc["document_type"],
                "created_at": doc["created_at"]
            }
            for doc in recent_docs
        ]
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting processing stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get processing statistics")


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a processed document and its extracted data"""
    
    try:
        supabase = get_supabase()
        
        # Get document info
        doc_response = supabase.table("manual_documents").select("*").eq("id", document_id).execute()
        
        if not doc_response.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = doc_response.data[0]
        
        # Delete related innovations
        supabase.table("innovations").delete().eq("source_document_id", document_id).execute()
        
        # Delete document record
        supabase.table("manual_documents").delete().eq("id", document_id).execute()
        
        # Try to delete physical file
        for directory in ["completed", "failed", "processing"]:
            file_path = Path(f"manual_documents/{directory}") / document["file_name"]
            if file_path.exists():
                file_path.unlink()
                break
        
        return {
            "success": True,
            "message": f"Document {document['file_name']} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for manual documents service"""
    
    try:
        # Check if watch directory exists
        watch_dir = Path("manual_documents")
        directory_status = {
            "watch_directory_exists": watch_dir.exists(),
            "processing_queue_size": len(manual_document_processor.processing_queue) if hasattr(manual_document_processor, 'processing_queue') else 0,
            "is_processing": getattr(manual_document_processor, 'is_processing', False)
        }
        
        return {
            "status": "healthy",
            "service": "manual_documents",
            "directory_status": directory_status,
            "supported_types": [doc_type.value for doc_type in DocumentType],
            "endpoints": [
                "POST /upload - Upload document for processing",
                "GET /status - Get processing status",  
                "GET /{id} - Get document details",
                "POST /{id}/reprocess - Reprocess document",
                "DELETE /{id} - Delete document",
                "GET /stats/summary - Get statistics"
            ]
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
