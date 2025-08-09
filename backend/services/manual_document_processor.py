"""
Manual Document Processing Service
=================================

This service provides folder watching capabilities for manually added documents
(PDFs, reports, news articles) with LLM-assisted extraction.

Features:
- Folder watching for automatic processing
- PDF extraction with marker-pdf or pymupdf
- LLM-assisted structured data extraction
- Specialized instruction support
- Integration with existing ETL pipeline
- Support for various document types

Usage:
1. Drop PDF + instructions.txt in watch folder
2. System automatically processes document
3. Extracted data flows into ETL pipeline
4. Results stored in database
"""

import asyncio
import logging
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

# File system monitoring
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# PDF processing libraries
try:
    import pymupdf  # PyMuPDF - good for complex PDFs
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import marker  # marker-pdf for LLM-assisted extraction
    MARKER_AVAILABLE = True
except ImportError:
    MARKER_AVAILABLE = False

import PyPDF2  # Fallback PDF reader
from io import BytesIO

# LLM integration
from openai import AsyncOpenAI
import anthropic

from config.database import get_supabase
from scripts.examples.enhanced_funding_extractor import EnhancedFundingExtractor

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    PDF_REPORT = "pdf_report"
    NEWS_ARTICLE = "news_article"
    RESEARCH_PAPER = "research_paper"
    STARTUP_LIST = "startup_list"
    FUNDING_ANNOUNCEMENT = "funding_announcement"
    MARKET_REPORT = "market_report"
    UNKNOWN = "unknown"


class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DocumentMetadata:
    """Metadata for manually added documents"""
    file_path: str
    file_name: str
    file_size: int
    file_hash: str
    document_type: DocumentType
    processing_instructions: Optional[str] = None
    custom_extraction_prompt: Optional[str] = None
    priority: int = 1  # 1-5, higher is more priority
    added_timestamp: datetime = None
    
    def __post_init__(self):
        if self.added_timestamp is None:
            self.added_timestamp = datetime.now()


@dataclass
class ProcessingResult:
    """Result of document processing"""
    document_id: str
    status: ProcessingStatus
    extracted_text: str
    structured_data: Dict[str, Any]
    innovations_found: List[Dict[str, Any]]
    funding_info_found: List[Dict[str, Any]]
    processing_timestamp: datetime
    processing_duration_seconds: float
    llm_provider: str
    error_message: Optional[str] = None
    confidence_score: float = 0.0


class ManualDocumentProcessor:
    """Main service for processing manually added documents"""
    
    def __init__(self, watch_directory: str = "manual_documents", llm_provider: str = "openai"):
        self.watch_directory = Path(watch_directory)
        self.processing_directory = self.watch_directory / "processing"
        self.completed_directory = self.watch_directory / "completed"
        self.failed_directory = self.watch_directory / "failed"
        
        # Create directories if they don't exist
        for directory in [self.watch_directory, self.processing_directory, 
                         self.completed_directory, self.failed_directory]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.llm_provider = llm_provider
        self.supabase = get_supabase()
        self.funding_extractor = EnhancedFundingExtractor()
        
        # Initialize LLM clients
        self._init_llm_clients()
        
        # Processing queue
        self.processing_queue: List[DocumentMetadata] = []
        self.is_processing = False
        
        logger.info(f"Manual Document Processor initialized - watching: {self.watch_directory}")
    
    def _init_llm_clients(self):
        """Initialize LLM clients"""
        try:
            if self.llm_provider == "openai":
                self.openai_client = AsyncOpenAI()
            elif self.llm_provider == "anthropic":
                self.anthropic_client = anthropic.AsyncAnthropic()
        except Exception as e:
            logger.warning(f"Could not initialize LLM client: {e}")
    
    async def start_folder_watching(self):
        """Start watching the folder for new documents"""
        
        event_handler = DocumentWatchHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.watch_directory), recursive=False)
        observer.start()
        
        logger.info(f"📁 Folder watching started: {self.watch_directory}")
        
        # Process any existing files
        await self._process_existing_files()
        
        try:
            # Start processing queue
            await self._process_queue_loop()
        except KeyboardInterrupt:
            observer.stop()
            logger.info("Folder watching stopped")
        
        observer.join()
    
    async def _process_existing_files(self):
        """Process any files that were already in the directory"""
        
        for file_path in self.watch_directory.glob("*.pdf"):
            if file_path.is_file():
                await self.add_document_to_queue(str(file_path))
    
    async def add_document_to_queue(self, file_path: str):
        """Add a document to the processing queue"""
        
        try:
            path_obj = Path(file_path)
            if not path_obj.exists():
                logger.error(f"File does not exist: {file_path}")
                return
            
            # Calculate file hash to avoid duplicates
            file_hash = self._calculate_file_hash(file_path)
            
            # Check if already processed
            if await self._is_already_processed(file_hash):
                logger.info(f"Document already processed: {path_obj.name}")
                return
            
            # Determine document type and load instructions
            doc_type, instructions, custom_prompt = await self._analyze_document_context(path_obj)
            
            metadata = DocumentMetadata(
                file_path=file_path,
                file_name=path_obj.name,
                file_size=path_obj.stat().st_size,
                file_hash=file_hash,
                document_type=doc_type,
                processing_instructions=instructions,
                custom_extraction_prompt=custom_prompt
            )
            
            self.processing_queue.append(metadata)
            logger.info(f"📄 Added to queue: {path_obj.name} (type: {doc_type.value})")
            
        except Exception as e:
            logger.error(f"Error adding document to queue: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    async def _is_already_processed(self, file_hash: str) -> bool:
        """Check if document was already processed"""
        try:
            response = self.supabase.table("manual_documents").select("id").eq("file_hash", file_hash).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.warning(f"Error checking processed documents: {e}")
            return False
    
    async def _analyze_document_context(self, file_path: Path) -> tuple[DocumentType, Optional[str], Optional[str]]:
        """Analyze document context and load instructions"""
        
        # Look for instructions file
        instructions_file = file_path.with_suffix('.txt')
        instructions = None
        custom_prompt = None
        
        if instructions_file.exists():
            try:
                content = instructions_file.read_text(encoding='utf-8')
                lines = content.strip().split('\n')
                
                # Parse instructions format:
                # TYPE: startup_list
                # INSTRUCTIONS: Extract company names, funding amounts, and descriptions
                # PROMPT: You are analyzing a list of African AI startups...
                
                doc_type = DocumentType.UNKNOWN
                for line in lines:
                    if line.startswith('TYPE:'):
                        type_str = line.split(':', 1)[1].strip()
                        try:
                            doc_type = DocumentType(type_str)
                        except ValueError:
                            pass
                    elif line.startswith('INSTRUCTIONS:'):
                        instructions = line.split(':', 1)[1].strip()
                    elif line.startswith('PROMPT:'):
                        custom_prompt = line.split(':', 1)[1].strip()
                
            except Exception as e:
                logger.warning(f"Error reading instructions file: {e}")
                doc_type = DocumentType.UNKNOWN
        else:
            # Auto-detect document type from filename
            filename_lower = file_path.name.lower()
            if 'startup' in filename_lower or 'company' in filename_lower:
                doc_type = DocumentType.STARTUP_LIST
            elif 'funding' in filename_lower or 'investment' in filename_lower:
                doc_type = DocumentType.FUNDING_ANNOUNCEMENT
            elif 'market' in filename_lower:
                doc_type = DocumentType.MARKET_REPORT
            elif 'news' in filename_lower:
                doc_type = DocumentType.NEWS_ARTICLE
            else:
                doc_type = DocumentType.PDF_REPORT
        
        return doc_type, instructions, custom_prompt
    
    async def _process_queue_loop(self):
        """Main processing loop"""
        
        while True:
            if not self.is_processing and self.processing_queue:
                self.is_processing = True
                
                # Sort by priority
                self.processing_queue.sort(key=lambda x: x.priority, reverse=True)
                
                # Process next document
                document_metadata = self.processing_queue.pop(0)
                await self._process_single_document(document_metadata)
                
                self.is_processing = False
            
            # Wait before checking queue again
            await asyncio.sleep(2)
    
    async def _process_single_document(self, metadata: DocumentMetadata) -> ProcessingResult:
        """Process a single document"""
        
        start_time = datetime.now()
        document_id = str(uuid.uuid4())
        
        logger.info(f"🔄 Processing: {metadata.file_name}")
        
        try:
            # Move to processing directory
            processing_path = self.processing_directory / metadata.file_name
            original_path = Path(metadata.file_path)
            processing_path.write_bytes(original_path.read_bytes())
            
            # Extract text from PDF
            extracted_text = await self._extract_text_from_pdf(str(processing_path))
            
            if not extracted_text.strip():
                raise Exception("No text could be extracted from PDF")
            
            # LLM-assisted structured extraction
            structured_data = await self._llm_extract_structured_data(
                extracted_text, metadata.document_type, 
                metadata.processing_instructions, metadata.custom_extraction_prompt
            )
            
            # Extract innovations and funding info using existing extractors
            innovations_found = await self._extract_innovations(structured_data, extracted_text)
            funding_info_found = await self._extract_funding_info(extracted_text)
            
            # Calculate processing duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = ProcessingResult(
                document_id=document_id,
                status=ProcessingStatus.COMPLETED,
                extracted_text=extracted_text[:5000],  # Truncate for storage
                structured_data=structured_data,
                innovations_found=innovations_found,
                funding_info_found=funding_info_found,
                processing_timestamp=datetime.now(),
                processing_duration_seconds=duration,
                llm_provider=self.llm_provider,
                confidence_score=structured_data.get('confidence_score', 0.8)
            )
            
            # Store in database
            await self._store_processing_result(metadata, result)
            
            # Move to completed directory
            completed_path = self.completed_directory / metadata.file_name
            completed_path.write_bytes(processing_path.read_bytes())
            processing_path.unlink()  # Remove from processing
            original_path.unlink()   # Remove original
            
            # Remove instructions file if exists
            instructions_file = original_path.with_suffix('.txt')
            if instructions_file.exists():
                instructions_file.unlink()
            
            logger.info(f"✅ Completed: {metadata.file_name} ({duration:.1f}s)")
            return result
            
        except Exception as e:
            # Handle failure
            duration = (datetime.now() - start_time).total_seconds()
            
            result = ProcessingResult(
                document_id=document_id,
                status=ProcessingStatus.FAILED,
                extracted_text="",
                structured_data={},
                innovations_found=[],
                funding_info_found=[],
                processing_timestamp=datetime.now(),
                processing_duration_seconds=duration,
                llm_provider=self.llm_provider,
                error_message=str(e)
            )
            
            # Move to failed directory
            try:
                failed_path = self.failed_directory / metadata.file_name
                processing_path = self.processing_directory / metadata.file_name
                if processing_path.exists():
                    failed_path.write_bytes(processing_path.read_bytes())
                    processing_path.unlink()
            except Exception:
                pass
            
            logger.error(f"❌ Failed: {metadata.file_name} - {str(e)}")
            return result
    
    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using best available method"""
        
        text = ""
        
        # Try PyMuPDF first (best for complex PDFs)
        if PYMUPDF_AVAILABLE:
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text += page.get_text()
                doc.close()
                if text.strip():
                    return text
            except Exception as e:
                logger.warning(f"PyMuPDF extraction failed: {e}")
        
        # Try marker-pdf if available (LLM-assisted)
        if MARKER_AVAILABLE:
            try:
                # This would need marker-pdf implementation
                # text = await marker.extract_text(file_path)
                pass
            except Exception as e:
                logger.warning(f"Marker-pdf extraction failed: {e}")
        
        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            raise Exception(f"All PDF extraction methods failed: {e}")
    
    async def _llm_extract_structured_data(
        self, 
        text: str, 
        doc_type: DocumentType, 
        instructions: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Use LLM to extract structured data"""
        
        # Build extraction prompt based on document type
        if custom_prompt:
            system_prompt = custom_prompt
        else:
            system_prompt = self._build_extraction_prompt(doc_type, instructions)
        
        try:
            if self.llm_provider == "openai":
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",  # Cost-effective for extraction
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Extract structured data from this document:\n\n{text[:8000]}"}  # Limit text length
                    ],
                    temperature=0.1,
                    max_tokens=2000
                )
                
                extracted_json = response.choices[0].message.content
                
            elif self.llm_provider == "anthropic":
                response = await self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",  # Cost-effective
                    max_tokens=2000,
                    temperature=0.1,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": f"Extract structured data from this document:\n\n{text[:8000]}"}
                    ]
                )
                
                extracted_json = response.content[0].text
            
            # Parse JSON response
            try:
                structured_data = json.loads(extracted_json)
                return structured_data
            except json.JSONDecodeError:
                # If not valid JSON, return as text with basic structure
                return {
                    "extraction_method": "llm_text",
                    "content": extracted_json,
                    "confidence_score": 0.6
                }
                
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return {
                "extraction_method": "fallback",
                "raw_text": text[:1000],
                "error": str(e),
                "confidence_score": 0.3
            }
    
    def _build_extraction_prompt(self, doc_type: DocumentType, instructions: Optional[str]) -> str:
        """Build extraction prompt based on document type"""
        
        base_prompt = """You are an expert data extraction assistant. Extract structured information from documents and return it as valid JSON.

Focus on extracting:
- Company/startup names
- Funding amounts and types
- Market sizing information
- Key people and roles
- Locations/countries
- Technology domains
- Business models

"""
        
        if doc_type == DocumentType.STARTUP_LIST:
            specific_prompt = """This document contains a list of startups. Extract:
{
  "startups": [
    {
      "name": "Company Name",
      "description": "Brief description",
      "funding_raised": "Amount and currency",
      "location": "Country/City",
      "domain": "Technology domain",
      "founders": ["Founder names"],
      "website": "URL if mentioned"
    }
  ],
  "confidence_score": 0.8
}"""
        
        elif doc_type == DocumentType.FUNDING_ANNOUNCEMENT:
            specific_prompt = """This document contains funding announcements. Extract:
{
  "funding_rounds": [
    {
      "company": "Company name",
      "amount": "Funding amount",
      "currency": "Currency",
      "round_type": "Seed/Series A/etc",
      "investors": ["Investor names"],
      "date": "Funding date",
      "use_of_funds": "How funds will be used"
    }
  ],
  "confidence_score": 0.8
}"""
        
        elif doc_type == DocumentType.MARKET_REPORT:
            specific_prompt = """This document contains market analysis. Extract:
{
  "market_data": [
    {
      "sector": "Market sector",
      "market_size": "Size and currency",
      "growth_rate": "Annual growth rate",
      "key_players": ["Company names"],
      "geographic_focus": ["Countries/regions"],
      "trends": ["Key trends"]
    }
  ],
  "confidence_score": 0.8
}"""
        
        else:
            specific_prompt = """Extract key information as structured JSON:
{
  "key_entities": [
    {
      "type": "company/person/amount/location",
      "value": "Extracted value",
      "context": "Brief context"
    }
  ],
  "confidence_score": 0.8
}"""
        
        # Add custom instructions if provided
        if instructions:
            specific_prompt += f"\n\nAdditional instructions: {instructions}"
        
        return base_prompt + specific_prompt
    
    async def _extract_innovations(self, structured_data: Dict[str, Any], full_text: str) -> List[Dict[str, Any]]:
        """Extract innovations using structured data and existing extractors"""
        
        innovations = []
        
        # Extract from structured data
        if 'startups' in structured_data:
            for startup in structured_data['startups']:
                innovation = {
                    'title': startup.get('name', ''),
                    'description': startup.get('description', ''),
                    'domain': startup.get('domain', ''),
                    'location': startup.get('location', ''),
                    'founders': startup.get('founders', []),
                    'website_url': startup.get('website', ''),
                    'source': 'manual_document_extraction',
                    'verification_status': 'needs_review'
                }
                
                # Add funding info if available
                if startup.get('funding_raised'):
                    innovation['fundings'] = [{
                        'amount': startup.get('funding_raised', ''),
                        'source': 'document_extraction'
                    }]
                
                innovations.append(innovation)
        
        return innovations
    
    async def _extract_funding_info(self, text: str) -> List[Dict[str, Any]]:
        """Extract funding information using existing extractor"""
        
        try:
            funding_info = self.funding_extractor.extract_funding_info(text)
            return [funding_info] if funding_info else []
        except Exception as e:
            logger.warning(f"Funding extraction failed: {e}")
            return []
    
    async def _store_processing_result(self, metadata: DocumentMetadata, result: ProcessingResult):
        """Store processing result in database"""
        
        try:
            # Store document record
            document_record = {
                'id': result.document_id,
                'file_name': metadata.file_name,
                'file_hash': metadata.file_hash,
                'file_size': metadata.file_size,
                'document_type': metadata.document_type.value,
                'processing_status': result.status.value,
                'processing_instructions': metadata.processing_instructions,
                'extracted_text_preview': result.extracted_text,
                'structured_data': result.structured_data,
                'processing_duration_seconds': result.processing_duration_seconds,
                'llm_provider': result.llm_provider,
                'confidence_score': result.confidence_score,
                'error_message': result.error_message,
                'created_at': result.processing_timestamp.isoformat(),
                'added_timestamp': metadata.added_timestamp.isoformat()
            }
            
            self.supabase.table('manual_documents').insert(document_record).execute()
            
            # Store extracted innovations
            for innovation in result.innovations_found:
                innovation.update({
                    'id': str(uuid.uuid4()),
                    'source_document_id': result.document_id,
                    'extraction_method': 'manual_document_llm',
                    'created_at': datetime.now().isoformat()
                })
                
                self.supabase.table('innovations').insert(innovation).execute()
            
            logger.info(f"💾 Stored: {len(result.innovations_found)} innovations from {metadata.file_name}")
            
        except Exception as e:
            logger.error(f"Database storage failed: {e}")


class DocumentWatchHandler(FileSystemEventHandler):
    """File system event handler for document watching"""
    
    def __init__(self, processor: ManualDocumentProcessor):
        self.processor = processor
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.pdf'):
            asyncio.create_task(self.processor.add_document_to_queue(event.src_path))
    
    def on_moved(self, event):
        if not event.is_directory and event.dest_path.endswith('.pdf'):
            asyncio.create_task(self.processor.add_document_to_queue(event.dest_path))


# Global processor instance
manual_document_processor = ManualDocumentProcessor()


# Convenience functions
async def start_document_watching(watch_dir: str = "manual_documents"):
    """Start the document watching service"""
    processor = ManualDocumentProcessor(watch_directory=watch_dir)
    await processor.start_folder_watching()


async def process_single_document(file_path: str, document_type: str = "pdf_report", 
                                instructions: str = None, custom_prompt: str = None) -> ProcessingResult:
    """Process a single document manually"""
    
    processor = ManualDocumentProcessor()
    
    metadata = DocumentMetadata(
        file_path=file_path,
        file_name=Path(file_path).name,
        file_size=Path(file_path).stat().st_size,
        file_hash=processor._calculate_file_hash(file_path),
        document_type=DocumentType(document_type),
        processing_instructions=instructions,
        custom_extraction_prompt=custom_prompt
    )
    
    return await processor._process_single_document(metadata)


if __name__ == "__main__":
    # Test the document processor
    async def main():
        print("🔄 Starting Manual Document Processor...")
        await start_document_watching()
    
    asyncio.run(main())
