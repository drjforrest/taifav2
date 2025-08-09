#!/usr/bin/env python3
"""
Apply database schema fixes for TAIFA-FIALA
Fixes the missing authors column and other schema issues
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
script_dir = Path(__file__).parent
backend_dir = script_dir.parent / "backend"
sys.path.insert(0, str(backend_dir))

from config.database import get_supabase
from loguru import logger


async def apply_schema_fixes():
    """Apply database schema fixes"""
    logger.info("🔧 Applying database schema fixes...")
    
    try:
        # Get Supabase client
        supabase = get_supabase()
        
        # Read the schema fix SQL
        schema_fix_path = Path(__file__).parent.parent / "data" / "schemas" / "fix_publications_schema.sql"
        
        if not schema_fix_path.exists():
            logger.error(f"❌ Schema fix file not found: {schema_fix_path}")
            return False
            
        with open(schema_fix_path, 'r') as f:
            sql_content = f.read()
            
        logger.info("📄 Executing database schema fix...")
        
        # Execute the SQL (Note: Supabase Python client doesn't support direct SQL execution)
        # You would need to run this SQL directly in the Supabase SQL editor
        logger.warning("⚠️ Please run the following SQL in your Supabase SQL editor:")
        logger.info("=" * 60)
        logger.info(sql_content)
        logger.info("=" * 60)
        
        # Alternative: Check if the authors column exists
        try:
            # Try to query the publications table to see current schema
            result = supabase.table("publications").select("*").limit(1).execute()
            
            if result.data:
                sample_record = result.data[0]
                if 'authors' in sample_record:
                    logger.info("✅ Authors column already exists in publications table")
                else:
                    logger.warning("❌ Authors column missing - please run the SQL fix above")
                    
            logger.info("📊 Current publications table sample:")
            logger.info(f"Available columns: {list(sample_record.keys()) if result.data else 'No data'}")
            
        except Exception as e:
            logger.error(f"❌ Error checking publications table schema: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error applying schema fixes: {e}")
        return False


def main():
    """Main function"""
    logger.info("🚀 Starting database schema fix...")
    success = asyncio.run(apply_schema_fixes())
    
    if success:
        logger.info("✅ Schema fix process completed!")
        logger.info("📝 Next steps:")
        logger.info("   1. Run the SQL script in Supabase SQL editor")
        logger.info("   2. Verify the authors column exists")
        logger.info("   3. Test the academic pipeline")
    else:
        logger.error("❌ Schema fix process failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
