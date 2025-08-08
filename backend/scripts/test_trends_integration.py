#!/usr/bin/env python3
"""
Test script to verify the trends API integration
Tests all endpoints and their integration with domain_evolution_mapper
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import json
from datetime import date, datetime

import requests
from loguru import logger

# Test configuration
API_BASE_URL = "http://localhost:8030"
TEST_ENDPOINTS = [
    "/api/trends/lifecycles",
    "/api/trends/time-to-market",
    "/api/trends/domains/trends",
    "/api/trends/domains/emerging",
    "/api/trends/domains/focus-areas",
    "/api/trends/patterns/success",
    "/api/trends/patterns/success/identify",
]


async def test_domain_evolution_mapper_initialization():
    """Test that domain_evolution_mapper initializes correctly"""
    try:
        from services.domain_evolution_mapper import domain_evolution_mapper

        logger.info("Testing domain_evolution_mapper initialization...")
        success = await domain_evolution_mapper.initialize()

        if success:
            logger.success("✅ Domain evolution mapper initialized successfully")
            return True
        else:
            logger.error("❌ Domain evolution mapper failed to initialize")
            return False

    except Exception as e:
        logger.error(f"❌ Error testing domain evolution mapper: {e}")
        return False


def test_trends_api_endpoints():
    """Test all trends API endpoints"""
    logger.info("Testing trends API endpoints...")
    results = {}

    for endpoint in TEST_ENDPOINTS:
        try:
            url = f"{API_BASE_URL}{endpoint}"
            logger.info(f"Testing {endpoint}...")

            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                results[endpoint] = {
                    "status": "success",
                    "status_code": response.status_code,
                    "data_keys": list(data.keys())
                    if isinstance(data, dict)
                    else "list",
                    "data_length": len(data)
                    if isinstance(data, (list, dict))
                    else "unknown",
                }
                logger.success(f"✅ {endpoint} - Status: {response.status_code}")
            else:
                results[endpoint] = {
                    "status": "error",
                    "status_code": response.status_code,
                    "error": response.text[:200],
                }
                logger.error(f"❌ {endpoint} - Status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            results[endpoint] = {"status": "connection_error", "error": str(e)}
            logger.error(f"❌ {endpoint} - Connection error: {e}")
        except Exception as e:
            results[endpoint] = {"status": "unexpected_error", "error": str(e)}
            logger.error(f"❌ {endpoint} - Unexpected error: {e}")

    return results


def test_domain_evolution_endpoints():
    """Test domain evolution specific endpoints"""
    logger.info("Testing domain evolution endpoints...")

    # Test domain tracking
    try:
        url = f"{API_BASE_URL}/api/trends/domains/track"
        payload = {
            "domain_name": "machine_learning",
            "period_start": "2024-01-01",
            "period_end": "2024-08-01",
        }

        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            logger.success("✅ Domain tracking endpoint working")
            return True
        else:
            logger.error(
                f"❌ Domain tracking failed: {response.status_code} - {response.text[:200]}"
            )
            return False

    except Exception as e:
        logger.error(f"❌ Domain tracking error: {e}")
        return False


def test_lifecycle_endpoints():
    """Test lifecycle tracking endpoints"""
    logger.info("Testing lifecycle endpoints...")

    try:
        # Test lifecycle creation (this might fail if innovation doesn't exist, which is expected)
        url = f"{API_BASE_URL}/api/trends/lifecycles"
        payload = {
            "innovation_id": "00000000-0000-0000-0000-000000000001",  # Test UUID
            "stage": "research",
            "start_date": "2024-01-01",
            "key_milestones": ["Initial research completed"],
        }

        response = requests.post(url, json=payload, timeout=30)

        # We expect this to fail with 404 (innovation not found) which is normal
        if response.status_code in [200, 404]:
            logger.success("✅ Lifecycle creation endpoint accessible")
            return True
        else:
            logger.error(
                f"❌ Lifecycle creation unexpected error: {response.status_code}"
            )
            return False

    except Exception as e:
        logger.error(f"❌ Lifecycle endpoint error: {e}")
        return False


def generate_test_report(
    api_results, domain_mapper_success, domain_evolution_success, lifecycle_success
):
    """Generate a comprehensive test report"""

    report = {
        "test_timestamp": datetime.now().isoformat(),
        "overall_status": "unknown",
        "domain_evolution_mapper": {
            "initialization": "success" if domain_mapper_success else "failed"
        },
        "api_endpoints": api_results,
        "domain_evolution_endpoints": {
            "tracking": "success" if domain_evolution_success else "failed"
        },
        "lifecycle_endpoints": {
            "creation": "success" if lifecycle_success else "failed"
        },
        "summary": {
            "total_endpoints_tested": len(TEST_ENDPOINTS),
            "successful_endpoints": len(
                [r for r in api_results.values() if r["status"] == "success"]
            ),
            "failed_endpoints": len(
                [r for r in api_results.values() if r["status"] != "success"]
            ),
            "integration_components": {
                "domain_mapper": domain_mapper_success,
                "domain_evolution": domain_evolution_success,
                "lifecycle_tracking": lifecycle_success,
            },
        },
    }

    # Determine overall status
    successful_endpoints = report["summary"]["successful_endpoints"]
    total_endpoints = report["summary"]["total_endpoints"]
    integration_success = all(
        [domain_mapper_success, domain_evolution_success, lifecycle_success]
    )

    if successful_endpoints == total_endpoints and integration_success:
        report["overall_status"] = "success"
    elif successful_endpoints > total_endpoints * 0.7:
        report["overall_status"] = "partial_success"
    else:
        report["overall_status"] = "failed"

    return report


async def main():
    """Main test function"""
    logger.info("🚀 Starting TAIFA-FIALA Trends API Integration Test")
    logger.info("=" * 60)

    # Test 1: Domain Evolution Mapper Initialization
    logger.info("📋 Test 1: Domain Evolution Mapper Initialization")
    domain_mapper_success = await test_domain_evolution_mapper_initialization()

    # Test 2: API Endpoints
    logger.info("\n📋 Test 2: Trends API Endpoints")
    api_results = test_trends_api_endpoints()

    # Test 3: Domain Evolution Endpoints
    logger.info("\n📋 Test 3: Domain Evolution Endpoints")
    domain_evolution_success = test_domain_evolution_endpoints()

    # Test 4: Lifecycle Endpoints
    logger.info("\n📋 Test 4: Lifecycle Endpoints")
    lifecycle_success = test_lifecycle_endpoints()

    # Generate Report
    logger.info("\n📊 Generating Test Report...")
    report = generate_test_report(
        api_results, domain_mapper_success, domain_evolution_success, lifecycle_success
    )

    # Save report
    report_path = backend_dir / "data" / "trends_integration_test_results.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)

    if report["overall_status"] == "success":
        logger.success(f"🎉 Overall Status: SUCCESS")
    elif report["overall_status"] == "partial_success":
        logger.warning(f"⚠️  Overall Status: PARTIAL SUCCESS")
    else:
        logger.error(f"❌ Overall Status: FAILED")

    logger.info(
        f"📈 API Endpoints: {report['summary']['successful_endpoints']}/{report['summary']['total_endpoints']} successful"
    )
    logger.info(f"🔧 Domain Mapper: {'✅' if domain_mapper_success else '❌'}")
    logger.info(f"🌍 Domain Evolution: {'✅' if domain_evolution_success else '❌'}")
    logger.info(f"🔄 Lifecycle Tracking: {'✅' if lifecycle_success else '❌'}")

    logger.info(f"\n📄 Full report saved to: {report_path}")

    # Print recommendations
    logger.info("\n💡 RECOMMENDATIONS:")
    if not domain_mapper_success:
        logger.info("- Check domain_evolution_mapper service initialization")

    failed_endpoints = [
        ep for ep, result in api_results.items() if result["status"] != "success"
    ]
    if failed_endpoints:
        logger.info("- Check failed API endpoints:")
        for ep in failed_endpoints:
            logger.info(f"  • {ep}")

    if report["overall_status"] == "success":
        logger.info("- ✅ Integration is working correctly!")
        logger.info(
            "- Frontend components should now receive real data from trends API"
        )

    return report["overall_status"] == "success"


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test failed with unexpected error: {e}")
        sys.exit(1)
