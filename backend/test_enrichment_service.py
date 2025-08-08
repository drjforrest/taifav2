#!/usr/bin/env python3
"""
Test script to verify the enrichment service is working properly
"""

import asyncio
import os
from pathlib import Path
import sys

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


async def test_enrichment_service():
    """Test the enrichment service components"""
    
    print("🔍 Testing TAIFA-FIALA Enrichment Service")
    print("=" * 50)
    
    # Test 1: Check environment variables
    print("\n1. Checking environment variables...")
    
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    if perplexity_key:
        print(f"✅ PERPLEXITY_API_KEY found (length: {len(perplexity_key)})")
    else:
        print("❌ PERPLEXITY_API_KEY not found")
        print("   Set it with: export PERPLEXITY_API_KEY='your_key_here'")
    
    # Test 2: Test database connection
    print("\n2. Testing database connection...")
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        response = supabase.table('innovations').select('id').limit(1).execute()
        print("✅ Database connection working")
        print(f"   Sample data available: {len(response.data) > 0 if response.data else False}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    # Test 3: Test enrichment scheduler
    print("\n3. Testing enrichment scheduler...")
    try:
        from services.enrichment_scheduler import get_enrichment_scheduler
        scheduler = get_enrichment_scheduler()
        schedule_info = scheduler.get_schedule_info()
        print("✅ Enrichment scheduler initialized")
        print(f"   Enabled: {schedule_info['enabled']}")
        print(f"   Provider: {schedule_info['provider']}")
        print(f"   Interval: {schedule_info['interval_hours']} hours")
        print(f"   Intelligence types: {schedule_info['intelligence_types']}")
        print(f"   Geographic focus: {schedule_info['geographic_focus']}")
        print(f"   Next run: {schedule_info['next_run']}")
        print(f"   Running: {schedule_info['running']}")
    except Exception as e:
        print(f"❌ Enrichment scheduler test failed: {e}")
    
    # Test 4: Test Perplexity AI module (if API key available)
    if perplexity_key:
        print("\n4. Testing Perplexity AI module...")
        try:
            from etl.intelligence.perplexity_african_ai import PerplexityAfricanAIModule, IntelligenceType
            
            async with PerplexityAfricanAIModule(perplexity_key) as perplexity:
                # Test with minimal parameters to avoid hitting rate limits
                reports = await perplexity.synthesize_intelligence(
                    intelligence_types=[IntelligenceType.INNOVATION_DISCOVERY],
                    time_period="last_3_days",
                    geographic_focus=["Nigeria"]
                )
                print("✅ Perplexity AI module working")
                print(f"   Generated {len(reports)} reports")
                
                if reports:
                    report = reports[0]
                    print(f"   Sample report: {report.title}")
                    print(f"   Confidence score: {report.confidence_score}")
                    print(f"   Key findings: {len(report.key_findings)}")
                    print(f"   Sources: {len(report.sources)}")
                    print(f"   Innovations mentioned: {len(report.innovations_mentioned)}")
        except Exception as e:
            print(f"❌ Perplexity AI module test failed: {e}")
    else:
        print("\n4. Skipping Perplexity AI test (no API key)")
    
    # Test 5: Test vector service
    print("\n5. Testing vector service...")
    try:
        from services.vector_service import get_vector_service
        vector_service = await get_vector_service()
        stats = await vector_service.get_stats()
        print("✅ Vector service working")
        print(f"   Total vectors: {stats.get('total_vectors', 0)}")
        print(f"   Collections: {stats.get('collections', [])}")
    except Exception as e:
        print(f"❌ Vector service test failed: {e}")
    
    # Test 6: Test unified cache
    print("\n6. Testing unified cache...")
    try:
        from services.unified_cache import get_cache_stats, DataSource
        stats = await get_cache_stats()
        print("✅ Unified cache working")
        print(f"   Cache hits: {stats.get('hits', 0)}")
        print(f"   Cache misses: {stats.get('misses', 0)}")
        print(f"   Hit rate: {stats.get('hit_rate', 0):.2%}")
    except Exception as e:
        print(f"❌ Unified cache test failed: {e}")
    
    # Test 7: Test snowball sampler
    print("\n7. Testing snowball sampler...")
    try:
        from services.snowball_sampler import SnowballSampler
        sampler = SnowballSampler()
        print("✅ Snowball sampler initialized")
        print(f"   Max depth: {sampler.max_depth}")
        print(f"   Rate limit delay: {sampler.rate_limit_delay}")
    except Exception as e:
        print(f"❌ Snowball sampler test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Enrichment service test completed!")
    
    # Summary and recommendations
    print("\n📋 RECOMMENDATIONS:")
    if not perplexity_key:
        print("• Set PERPLEXITY_API_KEY environment variable to enable AI enrichment")
    
    print("• Start the main application with: python main.py")
    print("• Check scheduler status at: GET /api/etl/scheduler/status")
    print("• Trigger manual enrichment at: POST /api/etl/enrichment")
    print("• Configure scheduler at: POST /api/etl/scheduler/configure")


if __name__ == "__main__":
    asyncio.run(test_enrichment_service())
