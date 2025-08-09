#!/usr/bin/env python3
"""
Funding Enrichment Solutions Activation Script
==============================================

This script activates all available solutions to address the critical data gaps:
- 68% missing funding information for publications 
- 87% missing market size data for innovations

Solutions activated:
1. AI Backfill Service for funding gaps
2. Scheduled enrichment for funding data
3. Market-focused intelligence gathering
4. Enhanced extraction of existing records
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.funding_enrichment_activator import FundingEnrichmentActivator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('funding_enrichment_activation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main activation script"""
    
    logger.info("🚀 Starting Funding Enrichment Solutions Activation")
    logger.info("=" * 60)
    
    try:
        # Initialize the activator
        activator = FundingEnrichmentActivator()
        
        # Run all immediate solutions
        results = await activator.activate_immediate_solutions()
        
        # Display results
        logger.info("✅ ACTIVATION COMPLETE")
        logger.info("=" * 60)
        
        logger.info(f"📊 Activation Summary:")
        logger.info(f"   Timestamp: {results['activation_timestamp']}")
        logger.info(f"   Solutions Activated: {len(results['solutions_activated'])}")
        
        for solution in results['solutions_activated']:
            logger.info(f"   ✓ {solution}")
        
        # Display detailed statistics
        logger.info(f"\n📈 Detailed Statistics:")
        for category, stats in results['statistics'].items():
            logger.info(f"   {category.upper()}:")
            if isinstance(stats, dict):
                for key, value in stats.items():
                    logger.info(f"     - {key}: {value}")
            else:
                logger.info(f"     {stats}")
        
        # Display any errors
        if results['errors']:
            logger.warning(f"\n⚠️  Errors encountered:")
            for error in results['errors']:
                logger.warning(f"   - {error}")
        
        logger.info("\n🎯 Next Steps:")
        logger.info("   1. Monitor the ETL pipelines for increased funding data collection")
        logger.info("   2. Check the AI backfill service queue for processing progress")
        logger.info("   3. Review intelligence reports for market sizing insights")
        logger.info("   4. Validate funding extraction improvements in new records")
        
        logger.info("\n📚 Monitoring URLs:")
        logger.info("   - ETL Status: /api/etl/status")
        logger.info("   - Funding Enrichment Status: /api/funding-enrichment/status")
        logger.info("   - AI Backfill Stats: /api/funding-enrichment/trigger-backfill")
        
    except Exception as e:
        logger.error(f"❌ ACTIVATION FAILED: {str(e)}")
        logger.error("Please check your configuration and try again.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
