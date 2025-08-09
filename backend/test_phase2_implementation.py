#!/usr/bin/env python3
"""
Phase 2 Implementation Test Script
Tests all Longitudinal Intelligence and Historical Trend Analysis endpoints

Usage: python test_phase2_implementation.py
"""

import asyncio
import logging
import sys
from datetime import datetime

import httpx

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "http://localhost:8030"  # Adjust based on your setup
TEST_TIMEOUT = 30.0


class Phase2Tester:
    """Test runner for Phase 2 APIs"""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.results = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {message}")
        self.results.append(
            {
                "test": test_name,
                "success": success,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def test_health_endpoints(self):
        """Test basic health and connectivity"""
        logger.info("🏥 Testing Health Endpoints...")

        # Test main health endpoint
        try:
            response = await self.client.get(f"{self.base_url}/health")
            success = response.status_code == 200
            self.log_test_result(
                "Main Health Check", success, f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_test_result("Main Health Check", False, str(e))

        # Test longitudinal intelligence health
        try:
            response = await self.client.get(
                f"{self.base_url}/api/longitudinal-intelligence/health"
            )
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_test_result(
                "Longitudinal Intelligence Health",
                success,
                f"Available endpoints: {len(data.get('available_endpoints', []))}",
            )
        except Exception as e:
            self.log_test_result("Longitudinal Intelligence Health", False, str(e))

    async def test_historical_trend_analysis(self):
        """Test Historical Trend Analysis endpoints"""
        logger.info("📈 Testing Historical Trend Analysis...")

        # Test innovation lifecycle analysis
        try:
            response = await self.client.get(
                f"{self.base_url}/api/longitudinal-intelligence/innovation-lifecycle"
            )
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_test_result(
                "Innovation Lifecycle Analysis",
                success,
                f"Status: {data.get('status', 'unknown')}",
            )
        except Exception as e:
            self.log_test_result("Innovation Lifecycle Analysis", False, str(e))

        # Test domain evolution analysis
        try:
            response = await self.client.get(
                f"{self.base_url}/api/longitudinal-intelligence/domain-evolution"
            )
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_test_result(
                "Domain Evolution Analysis",
                success,
                f"Status: {data.get('status', 'unknown')}",
            )
        except Exception as e:
            self.log_test_result("Domain Evolution Analysis", False, str(e))

        # Test success patterns analysis
        try:
            response = await self.client.get(
                f"{self.base_url}/api/longitudinal-intelligence/success-patterns"
            )
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_test_result(
                "Success Patterns Analysis",
                success,
                f"Status: {data.get('status', 'unknown')}",
            )
        except Exception as e:
            self.log_test_result("Success Patterns Analysis", False, str(e))

    async def test_weak_signal_detection(self):
        """Test Weak Signal Detection endpoints"""
        logger.info("🔍 Testing Weak Signal Detection...")

        # Test emergence indicators
        try:
            response = await self.client.get(
                f"{self.base_url}/api/longitudinal-intelligence/emergence-indicators"
            )
            success = response.status_code == 200
            data = response.json() if success else {}
            emergence_data = data.get("data", {})
            indicators_count = sum(
                len(emergence_data.get(key, []))
                for key in ["new_domains", "growing_niches", "emerging_keywords"]
            )
            self.log_test_result(
                "Emergence Indicators Detection",
                success,
                f"Found {indicators_count} emergence signals",
            )
        except Exception as e:
            self.log_test_result("Emergence Indicators Detection", False, str(e))

        # Test geographic shifts
        try:
            response = await self.client.get(
                f"{self.base_url}/api/longitudinal-intelligence/geographic-shifts"
            )
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_test_result(
                "Geographic Shifts Detection",
                success,
                f"Status: {data.get('status', 'unknown')}",
            )
        except Exception as e:
            self.log_test_result("Geographic Shifts Detection", False, str(e))

        # Test technology convergence
        try:
            response = await self.client.get(
                f"{self.base_url}/api/longitudinal-intelligence/technology-convergence"
            )
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_test_result(
                "Technology Convergence Analysis",
                success,
                f"Status: {data.get('status', 'unknown')}",
            )
        except Exception as e:
            self.log_test_result("Technology Convergence Analysis", False, str(e))

        # Test funding anomalies
        try:
            response = await self.client.get(
                f"{self.base_url}/api/longitudinal-intelligence/funding-anomalies"
            )
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_test_result(
                "Funding Anomalies Detection",
                success,
                f"Status: {data.get('status', 'unknown')}",
            )
        except Exception as e:
            self.log_test_result("Funding Anomalies Detection", False, str(e))

    async def test_trends_api(self):
        """Test Trends API endpoints"""
        logger.info("📊 Testing Trends API...")

        # Test lifecycle analytics
        try:
            response = await self.client.get(f"{self.base_url}/api/trends/lifecycles")
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_test_result(
                "Lifecycle Analytics",
                success,
                f"Records analyzed: {data.get('total_records', 0)}",
            )
        except Exception as e:
            self.log_test_result("Lifecycle Analytics", False, str(e))

        # Test time-to-market analysis
        try:
            response = await self.client.get(
                f"{self.base_url}/api/trends/time-to-market"
            )
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_test_result(
                "Time-to-Market Analysis",
                success,
                f"Innovations analyzed: {data.get('total_innovations', 0)}",
            )
        except Exception as e:
            self.log_test_result("Time-to-Market Analysis", False, str(e))

        # Test domain evolution endpoints
        try:
            response = await self.client.get(f"{self.base_url}/api/trends/domains")
            success = response.status_code == 200
            domains_count = len(response.json()) if success else 0
            self.log_test_result(
                "Domain Evolution Records", success, f"Domains tracked: {domains_count}"
            )
        except Exception as e:
            self.log_test_result("Domain Evolution Records", False, str(e))

        # Test emerging domains
        try:
            response = await self.client.get(
                f"{self.base_url}/api/trends/domains/emerging"
            )
            success = response.status_code == 200
            emerging_count = len(response.json()) if success else 0
            self.log_test_result(
                "Emerging Domains Detection",
                success,
                f"Emerging domains: {emerging_count}",
            )
        except Exception as e:
            self.log_test_result("Emerging Domains Detection", False, str(e))

        # Test success patterns
        try:
            response = await self.client.get(
                f"{self.base_url}/api/trends/patterns/success"
            )
            success = response.status_code == 200
            patterns_count = len(response.json()) if success else 0
            self.log_test_result(
                "Success Patterns Retrieval",
                success,
                f"Patterns found: {patterns_count}",
            )
        except Exception as e:
            self.log_test_result("Success Patterns Retrieval", False, str(e))

    async def test_longitudinal_summary(self):
        """Test comprehensive longitudinal intelligence summary"""
        logger.info("📋 Testing Longitudinal Summary...")

        try:
            params = {
                "include_lifecycle": "true",
                "include_evolution": "true",
                "include_signals": "true",
                "include_funding": "true",
            }
            response = await self.client.get(
                f"{self.base_url}/api/longitudinal-intelligence/longitudinal-summary",
                params=params,
            )
            success = response.status_code == 200
            data = response.json() if success else {}
            summary_data = data.get("data", {})
            analyses_included = data.get("included_analyses", [])

            self.log_test_result(
                "Comprehensive Longitudinal Summary",
                success,
                f"Analyses included: {len(analyses_included)}",
            )

            # Test individual components of summary
            if success and summary_data:
                for analysis_type in [
                    "lifecycle",
                    "evolution",
                    "weak_signals",
                    "funding_signals",
                ]:
                    has_component = analysis_type in summary_data
                    self.log_test_result(
                        f"Summary Component: {analysis_type}",
                        has_component,
                        "Present" if has_component else "Missing",
                    )

        except Exception as e:
            self.log_test_result("Comprehensive Longitudinal Summary", False, str(e))

    async def test_trend_alerts(self):
        """Test trend alerts system"""
        logger.info("🚨 Testing Trend Alerts...")

        alert_types = ["emergence", "geographic", "convergence", "funding", "all"]

        for alert_type in alert_types:
            try:
                params = {"alert_type": alert_type, "threshold": "0.3"}
                response = await self.client.get(
                    f"{self.base_url}/api/longitudinal-intelligence/trend-alerts",
                    params=params,
                )
                success = response.status_code == 200
                data = response.json() if success else {}
                alerts_data = data.get("data", {})
                total_alerts = alerts_data.get("total_alerts", 0)

                self.log_test_result(
                    f"Trend Alerts: {alert_type}",
                    success,
                    f"Alerts generated: {total_alerts}",
                )
            except Exception as e:
                self.log_test_result(f"Trend Alerts: {alert_type}", False, str(e))

    async def test_data_integration(self):
        """Test data integration and consistency"""
        logger.info("🔗 Testing Data Integration...")

        # Test if services can integrate with existing data
        try:
            # Get some sample data first
            innovations_response = await self.client.get(
                f"{self.base_url}/api/innovations?limit=5"
            )
            innovations_success = innovations_response.status_code == 200
            innovations = (
                innovations_response.json().get("innovations", [])
                if innovations_success
                else []
            )

            self.log_test_result(
                "Base Data Availability",
                innovations_success,
                f"Sample innovations: {len(innovations)}",
            )

            # Test if lifecycle tracking works with existing innovations
            if innovations:
                sample_innovation_id = innovations[0].get("id")
                if sample_innovation_id:
                    lifecycle_response = await self.client.get(
                        f"{self.base_url}/api/trends/lifecycles/{sample_innovation_id}"
                    )
                    lifecycle_success = lifecycle_response.status_code in [
                        200,
                        404,
                    ]  # 404 is ok, means no lifecycle data yet
                    self.log_test_result(
                        "Lifecycle Integration Test",
                        lifecycle_success,
                        f"Response code: {lifecycle_response.status_code}",
                    )
        except Exception as e:
            self.log_test_result("Data Integration Test", False, str(e))

    async def run_all_tests(self):
        """Run all Phase 2 tests"""
        logger.info("🚀 Starting Phase 2 Implementation Tests...")
        start_time = datetime.now()

        try:
            await self.test_health_endpoints()
            await self.test_historical_trend_analysis()
            await self.test_weak_signal_detection()
            await self.test_trends_api()
            await self.test_longitudinal_summary()
            await self.test_trend_alerts()
            await self.test_data_integration()
        except Exception as e:
            logger.error(f"Test suite error: {e}")

        end_time = datetime.now()
        duration = end_time - start_time

        # Generate summary
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        logger.info("\n" + "=" * 60)
        logger.info("📊 PHASE 2 IMPLEMENTATION TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Pass Rate: {pass_rate:.1f}%")
        logger.info(f"Duration: {duration.total_seconds():.2f}s")
        logger.info("=" * 60)

        if failed_tests > 0:
            logger.info("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    logger.info(f"  - {result['test']}: {result['message']}")

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": pass_rate,
            "duration_seconds": duration.total_seconds(),
            "results": self.results,
        }


async def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = BASE_URL

    logger.info(f"Testing Phase 2 implementation at: {base_url}")

    async with Phase2Tester(base_url) as tester:
        results = await tester.run_all_tests()

        # Exit with appropriate code
        if results["failed_tests"] > 0:
            sys.exit(1)
        else:
            logger.info("🎉 All tests passed!")
            sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
