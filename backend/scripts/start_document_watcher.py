#!/usr/bin/env python3
"""
Document Watcher Service Starter
================================

This script starts the folder watching service for manual document processing.
It watches for PDF files dropped in the manual_documents folder and processes them automatically.

Usage:
    python scripts/start_document_watcher.py [options]

Example folder structure:
    manual_documents/
    ├── top_40_african_ai_startups.pdf
    ├── top_40_african_ai_startups.txt  # Optional instructions
    ├── processing/                     # Documents being processed
    ├── completed/                      # Successfully processed
    └── failed/                         # Failed processing
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.manual_document_processor import start_document_watching

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_example_instructions_file(watch_dir: Path):
    """Create example instructions file for reference"""
    
    example_file = watch_dir / "EXAMPLE_INSTRUCTIONS.txt"
    
    if not example_file.exists():
        example_content = """# Example Instructions File
# ========================
# 
# To process a PDF with custom instructions, create a .txt file 
# with the same name as your PDF file.
#
# For example:
# - PDF file: top_40_african_ai_startups.pdf  
# - Instructions file: top_40_african_ai_startups.txt
#
# Format:
# TYPE: startup_list
# INSTRUCTIONS: Extract company names, funding amounts, locations, and brief descriptions
# PROMPT: You are analyzing a comprehensive list of the top African AI startups. Focus on extracting structured data including company names, funding amounts, founders, locations, and technology focus areas.

# Available document types:
# - startup_list: Lists of companies/startups
# - funding_announcement: Funding round announcements
# - market_report: Market analysis and sizing reports
# - research_paper: Academic research papers
# - news_article: News articles and press releases
# - pdf_report: General PDF reports

# Example for startup list:
TYPE: startup_list
INSTRUCTIONS: Extract company name, description, funding raised, location, domain, and founders from each startup mentioned
PROMPT: You are analyzing a list of African AI startups. Extract structured information for each company including name, brief description, total funding raised, headquarters location, AI domain/focus area, and founder names if mentioned. Return as JSON with confidence scores.
"""
        
        example_file.write_text(example_content)
        logger.info(f"📝 Created example instructions file: {example_file}")


def setup_directories(watch_dir: Path):
    """Setup required directories for document processing"""
    
    directories = [
        watch_dir,
        watch_dir / "processing",
        watch_dir / "completed", 
        watch_dir / "failed"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Directory ready: {directory}")
    
    # Create example instructions
    create_example_instructions_file(watch_dir)
    
    # Create README
    readme_file = watch_dir / "README.md"
    if not readme_file.exists():
        readme_content = """# Manual Document Processing
## How to Use

### 1. Drop PDF files here
Simply copy your PDF files to this directory.

### 2. Add instructions (optional)
Create a `.txt` file with the same name as your PDF to provide custom processing instructions.

Example:
- `african_ai_report.pdf` 
- `african_ai_report.txt` ← Instructions file

### 3. Processing happens automatically
- Files move to `processing/` during processing
- Completed files move to `completed/`
- Failed files move to `failed/`

### 4. Check results
- Use the API endpoints to check processing status
- View extracted data in the database
- Monitor logs for processing updates

## Supported Document Types
- `startup_list` - Lists of companies/startups
- `funding_announcement` - Funding rounds and investments  
- `market_report` - Market analysis and sizing
- `research_paper` - Academic papers
- `news_article` - News and press releases
- `pdf_report` - General reports

## Example Instructions File Format
```
TYPE: startup_list
INSTRUCTIONS: Extract company names, funding, and locations
PROMPT: Custom LLM prompt for specialized extraction...
```
"""
        readme_file.write_text(readme_content)
        logger.info(f"📖 Created README: {readme_file}")


async def main():
    """Main function"""
    
    parser = argparse.ArgumentParser(description="Start document watching service")
    parser.add_argument(
        "--watch-dir",
        default="manual_documents",
        help="Directory to watch for PDF files (default: manual_documents)"
    )
    parser.add_argument(
        "--llm-provider",
        default="openai",
        choices=["openai", "anthropic"],
        help="LLM provider for extraction (default: openai)"
    )
    
    args = parser.parse_args()
    
    watch_dir = Path(args.watch_dir)
    
    # Setup directories and examples
    setup_directories(watch_dir)
    
    logger.info("🚀 Starting Manual Document Processing Service")
    logger.info("=" * 60)
    logger.info(f"📁 Watching directory: {watch_dir.absolute()}")
    logger.info(f"🤖 LLM Provider: {args.llm_provider}")
    logger.info("=" * 60)
    
    # Instructions for user
    logger.info("💡 How to use:")
    logger.info(f"   1. Drop PDF files in: {watch_dir.absolute()}")
    logger.info(f"   2. Optional: Create .txt instructions file with same name")
    logger.info(f"   3. Files will be processed automatically")
    logger.info(f"   4. Check completed/ folder for results")
    logger.info("   5. Use API endpoints to view extracted data")
    
    logger.info("\n📋 Supported document types:")
    from services.manual_document_processor import DocumentType
    for doc_type in DocumentType:
        logger.info(f"   - {doc_type.value}")
    
    logger.info("\n🌐 API Endpoints (when FastAPI is running):")
    logger.info("   - GET /api/manual-documents/status - Processing status")
    logger.info("   - POST /api/manual-documents/upload - Upload via API") 
    logger.info("   - GET /api/manual-documents/{id} - Document details")
    logger.info("   - GET /api/manual-documents/stats/summary - Statistics")
    
    logger.info(f"\n📖 Check {watch_dir}/README.md for detailed instructions")
    logger.info(f"📝 Example instructions: {watch_dir}/EXAMPLE_INSTRUCTIONS.txt")
    
    logger.info("\n🔄 Starting folder watcher... (Press Ctrl+C to stop)")
    
    try:
        # Start the document watching service
        await start_document_watching(watch_dir=str(watch_dir))
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  Document watcher stopped by user")
    except Exception as e:
        logger.error(f"❌ Error starting document watcher: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
