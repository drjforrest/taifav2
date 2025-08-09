#!/usr/bin/env python3
"""
Document Processor Test Script
=============================

Test script to process a single PDF document and validate the extraction results.

Usage:
    python scripts/test_document_processor.py path/to/document.pdf [options]

Examples:
    python scripts/test_document_processor.py top_40_african_ai_startups.pdf --type startup_list
    python scripts/test_document_processor.py funding_report.pdf --type funding_announcement --instructions "Focus on Series A and B rounds"
"""

import asyncio
import argparse
import logging
import sys
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.manual_document_processor import process_single_document, DocumentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main test function"""
    
    parser = argparse.ArgumentParser(description="Test document processing")
    parser.add_argument(
        "file_path",
        help="Path to PDF file to process"
    )
    parser.add_argument(
        "--type",
        default="pdf_report",
        choices=[doc_type.value for doc_type in DocumentType],
        help="Document type (default: pdf_report)"
    )
    parser.add_argument(
        "--instructions",
        help="Custom processing instructions"
    )
    parser.add_argument(
        "--prompt",
        help="Custom LLM prompt"
    )
    parser.add_argument(
        "--output-file",
        help="Save results to JSON file"
    )
    
    args = parser.parse_args()
    
    # Validate file exists
    file_path = Path(args.file_path)
    if not file_path.exists():
        logger.error(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    if not file_path.suffix.lower() == '.pdf':
        logger.error(f"❌ File must be a PDF: {file_path}")
        sys.exit(1)
    
    logger.info("🧪 Testing Document Processor")
    logger.info("=" * 50)
    logger.info(f"📄 File: {file_path}")
    logger.info(f"📋 Type: {args.type}")
    if args.instructions:
        logger.info(f"📝 Instructions: {args.instructions}")
    if args.prompt:
        logger.info(f"🤖 Custom Prompt: {args.prompt[:100]}...")
    logger.info("=" * 50)
    
    try:
        # Process the document
        logger.info("🔄 Processing document...")
        
        result = await process_single_document(
            file_path=str(file_path),
            document_type=args.type,
            instructions=args.instructions,
            custom_prompt=args.prompt
        )
        
        # Display results
        logger.info("✅ Processing completed!")
        logger.info("=" * 50)
        logger.info("📊 RESULTS SUMMARY:")
        logger.info(f"   Status: {result.status.value}")
        logger.info(f"   Processing Time: {result.processing_duration_seconds:.1f}s")
        logger.info(f"   Confidence Score: {result.confidence_score:.2f}")
        logger.info(f"   LLM Provider: {result.llm_provider}")
        
        if result.error_message:
            logger.error(f"   Error: {result.error_message}")
        
        logger.info(f"\n📄 EXTRACTED TEXT PREVIEW:")
        logger.info(f"   Length: {len(result.extracted_text)} characters")
        if result.extracted_text:
            preview = result.extracted_text[:300]
            logger.info(f"   Preview: {preview}...")
        
        logger.info(f"\n🔍 STRUCTURED DATA:")
        if result.structured_data:
            for key, value in result.structured_data.items():
                if isinstance(value, list):
                    logger.info(f"   {key}: {len(value)} items")
                elif isinstance(value, dict):
                    logger.info(f"   {key}: {len(value)} keys")
                else:
                    logger.info(f"   {key}: {str(value)[:100]}")
        else:
            logger.info("   No structured data extracted")
        
        logger.info(f"\n🏢 INNOVATIONS FOUND: {len(result.innovations_found)}")
        for i, innovation in enumerate(result.innovations_found[:3], 1):
            logger.info(f"   {i}. {innovation.get('title', 'Untitled')}")
            if innovation.get('description'):
                logger.info(f"      Description: {innovation['description'][:100]}...")
            if innovation.get('location'):
                logger.info(f"      Location: {innovation['location']}")
        
        if len(result.innovations_found) > 3:
            logger.info(f"   ... and {len(result.innovations_found) - 3} more")
        
        logger.info(f"\n💰 FUNDING INFO: {len(result.funding_info_found)} items found")
        for funding in result.funding_info_found[:2]:
            if funding.get('funding_type'):
                logger.info(f"   Type: {funding['funding_type']}")
            if funding.get('total_funding_pool'):
                logger.info(f"   Pool: ${funding['total_funding_pool']:,.0f}")
        
        # Save to file if requested
        if args.output_file:
            output_data = {
                "document_id": result.document_id,
                "status": result.status.value,
                "processing_duration_seconds": result.processing_duration_seconds,
                "confidence_score": result.confidence_score,
                "llm_provider": result.llm_provider,
                "error_message": result.error_message,
                "extracted_text": result.extracted_text,
                "structured_data": result.structured_data,
                "innovations_found": result.innovations_found,
                "funding_info_found": result.funding_info_found,
                "processing_timestamp": result.processing_timestamp.isoformat()
            }
            
            output_path = Path(args.output_file)
            with open(output_path, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            
            logger.info(f"\n💾 Results saved to: {output_path}")
        
        # Summary recommendation
        logger.info("\n🎯 RECOMMENDATIONS:")
        if result.confidence_score > 0.8:
            logger.info("   ✅ High confidence extraction - results look good!")
        elif result.confidence_score > 0.6:
            logger.info("   ⚠️  Medium confidence - consider reviewing results")
        else:
            logger.info("   🔴 Low confidence - may need custom prompt or instructions")
        
        if len(result.innovations_found) > 10:
            logger.info("   📈 Great extraction rate - document type well matched")
        elif len(result.innovations_found) > 0:
            logger.info("   📊 Some innovations found - good baseline extraction")
        else:
            logger.info("   📉 No innovations extracted - try different document type or custom prompt")
        
        logger.info("\n🔄 To reprocess with different settings:")
        logger.info(f"   python scripts/test_document_processor.py {file_path} --type {args.type} --instructions 'your custom instructions'")
        
    except Exception as e:
        logger.error(f"❌ Processing failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
