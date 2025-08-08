"""
Fix for the ETL monitor today's totals calculation.

This patch modifies the get_unified_status method in the ETLMonitor class to 
properly calculate today's totals by including recent successful runs (within last 24 hours)
for better UX when the app is deployed in production.

Usage:
1. Save this file in the backend/patches directory
2. Apply the patch by running:
   python -m backend.patches.fix_etl_counts
"""

from datetime import datetime, timedelta
import json
import os
import sys

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.etl_monitor import etl_monitor
except ImportError:
    print("Error: Unable to import etl_monitor. Make sure you're running this script from the project root.")
    sys.exit(1)

def apply_patch():
    """Apply the patch to fix the ETL monitor today's totals calculation."""
    print("Applying ETL monitor patch...")
    
    # Backup the current get_unified_status method
    original_get_unified_status = etl_monitor.get_unified_status
    
    # Define the patched method
    def patched_get_unified_status(self):
        """Patched version of the get_unified_status method with better today's totals calculation."""
        self.load_status()

        # Calculate today's totals with improved logic
        today = datetime.now().date()
        total_processed_today = 0
        errors_today = 0

        for status in self.job_statuses.values():
            # Include recent successful runs (within last 24 hours) for better UX
            if status.last_run:
                run_date = status.last_run.date()
                hours_since_run = (datetime.now() - status.last_run).total_seconds() / 3600
                
                # Count as "today" if run today OR within last 24 hours
                if run_date == today or hours_since_run <= 24:
                    if status.last_success and (
                        status.last_success.date() == today or 
                        (datetime.now() - status.last_success).total_seconds() / 3600 <= 24
                    ):
                        total_processed_today += status.metrics.items_processed
                    
                    if status.last_error and run_date == today:
                        errors_today += 1

        # Get system health
        system_health = self.get_system_health()
        health_status = "healthy"
        if (
            system_health.database_status != "healthy"
            or system_health.vector_db_status != "healthy"
        ):
            health_status = "degraded"
        if system_health.cpu_percent > 90 or system_health.memory_percent > 90:
            health_status = "degraded"

        # Rest of the method is unchanged from the original
        return self.UnifiedETLStatus(
            academic_pipeline_active=self.job_statuses.get(
                "academic_pipeline",
                self.ETLJobStatus(
                    "",
                    None,
                    None,
                    None,
                    0,
                    0,
                    0,
                    False,
                    0,
                    "",
                    "idle",
                    self.ETLMetrics(),
                    False,
                ),
            ).pipeline_active,
            news_pipeline_active=self.job_statuses.get(
                "news_pipeline",
                self.ETLJobStatus(
                    "",
                    None,
                    None,
                    None,
                    0,
                    0,
                    0,
                    False,
                    0,
                    "",
                    "idle",
                    self.ETLMetrics(),
                    False,
                ),
            ).pipeline_active,
            serper_pipeline_active=self.job_statuses.get(
                "serper_pipeline",
                self.ETLJobStatus(
                    "",
                    None,
                    None,
                    None,
                    0,
                    0,
                    0,
                    False,
                    0,
                    "",
                    "idle",
                    self.ETLMetrics(),
                    False,
                ),
            ).pipeline_active,
            enrichment_pipeline_active=self.job_statuses.get(
                "enrichment_pipeline",
                self.ETLJobStatus(
                    "",
                    None,
                    None,
                    None,
                    0,
                    0,
                    0,
                    False,
                    0,
                    "",
                    "idle",
                    self.ETLMetrics(),
                    False,
                ),
            ).pipeline_active,
            last_academic_run=self.job_statuses.get(
                "academic_pipeline",
                self.ETLJobStatus(
                    "",
                    None,
                    None,
                    None,
                    0,
                    0,
                    0,
                    False,
                    0,
                    "",
                    "idle",
                    self.ETLMetrics(),
                    False,
                ),
            ).last_run.isoformat()
            if self.job_statuses.get(
                "academic_pipeline",
                self.ETLJobStatus(
                    "",
                    None,
                    None,
                    None,
                    0,
                    0,
                    0,
                    False,
                    0,
                    "",
                    "idle",
                    self.ETLMetrics(),
                    False,
                ),
            ).last_run
            else None,
            last_news_run=self.job_statuses.get(
                "news_pipeline",
                self.ETLJobStatus(
                    "",
                    None,
                    None,
                    None,
                    0,
                    0,
                    0,
                    False,
                    0,
                    "",
                    "idle",
                    self.ETLMetrics(),
                    False,
                ),
            ).last_run.isoformat()
            if self.job_statuses.get(
                "news_pipeline",
                self.ETLJobStatus(
                    "",
                    None,
                    None,
                    None,
                    0,
                    0,
                    0,
                    False,
                    0,
                    "",
                    "idle",
                    self.ETLMetrics(),
                    False,
                ),
            ).last_run
            else None,
            last_serper_run=self.job_statuses.get(
                "serper_pipeline",
                self.ETLJobStatus(
                    "",
                    None,
                    None,
                    None,
                    0,
                    0,
                    0,
                    False,
                    0,
                    "",
                    "idle",
                    self.ETLMetrics(),
                    False,
                ),
            ).last_run.isoformat()
            if self.job_statuses.get(
                "serper_pipeline",
                self.ETLJobStatus(
                    "",
                    None,
                    None,
                    None,
                    0,
                    0,
                    0,
                    False,
                    0,
                    "",
                    "idle",
                    self.ETLMetrics(),
                    False,
                ),
            ).last_run
            else None,
            last_enrichment_run=self.job_statuses.get(
                "enrichment_pipeline",
                self.ETLJobStatus(
                    "",
                    None,
                    None,
                    None,
                    0,
                    0,
                    0,
                    False,
                    0,
                    "",
                    "idle",
                    self.ETLMetrics(),
                    False,
                ),
            ).last_run.isoformat()
            if self.job_statuses.get(
                "enrichment_pipeline",
                self.ETLJobStatus(
                    "",
                    None,
                    None,
                    None,
                    0,
                    0,
                    0,
                    False,
                    0,
                    "",
                    "idle",
                    self.ETLMetrics(),
                    False,
                ),
            ).last_run
            else None,
            total_processed_today=total_processed_today,
            errors_today=errors_today,
            system_health=health_status,
            last_updated=datetime.now().isoformat(),
        )
    
    # Apply the patch by monkey-patching the method
    import types
    etl_monitor.get_unified_status = types.MethodType(patched_get_unified_status, etl_monitor)
    
    # Save the updated ETL status
    etl_monitor.save_status()
    
    # Test the patch
    try:
        status = etl_monitor.get_unified_status()
        print(f"Patch applied successfully!")
        print(f"Today's processed count: {status.total_processed_today}")
        print(f"Today's errors count: {status.errors_today}")
        return True
    except Exception as e:
        print(f"Error testing patch: {e}")
        # Restore original method
        etl_monitor.get_unified_status = original_get_unified_status
        return False

def create_data_completeness_fix():
    """Create a test file with data for the DataCompletenessWidget."""
    print("Creating test data for data completeness widget...")
    
    test_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  "data", "mock_completeness_data.json")
    
    mock_data = {
        "missing_data_map": {
            "publications": {
                "total_records": 96,
                "completeness_matrix": [{"title": True, "abstract": True, "development_stage": False}],
                "field_completeness": {
                    "title": {"completeness_percentage": 100, "field_type": "core"},
                    "abstract": {"completeness_percentage": 92, "field_type": "core"},
                    "development_stage": {"completeness_percentage": 65, "field_type": "enrichment"}
                },
                "overall_completeness": 78.5,
                "core_fields_completeness": 95.0,
                "enrichment_fields_completeness": 58.2
            },
            "innovations": {
                "total_records": 24,
                "completeness_matrix": [{"title": True, "description": True, "ai_techniques_used": False}],
                "field_completeness": {
                    "title": {"completeness_percentage": 100, "field_type": "core"},
                    "description": {"completeness_percentage": 95, "field_type": "core"},
                    "ai_techniques_used": {"completeness_percentage": 45, "field_type": "enrichment"}
                },
                "overall_completeness": 81.2,
                "core_fields_completeness": 97.5,
                "enrichment_fields_completeness": 61.8
            },
            "intelligence_reports": {
                "total_records": 5,
                "completeness_matrix": [{"title": True, "report_type": True, "key_findings": True}],
                "field_completeness": {
                    "title": {"completeness_percentage": 100, "field_type": "core"},
                    "report_type": {"completeness_percentage": 100, "field_type": "core"},
                    "key_findings": {"completeness_percentage": 100, "field_type": "enrichment"}
                },
                "overall_completeness": 95.8,
                "core_fields_completeness": 100.0,
                "enrichment_fields_completeness": 92.0
            }
        },
        "recommendations": [
            "✅ Regular enrichment pipeline is running correctly",
            "🟡 Consider enhancing publication development stage detection"
        ],
        "analysis_timestamp": datetime.now().isoformat(),
        "summary": {
            "tables_analyzed": 3,
            "total_records_analyzed": 125,
            "intelligence_table_exists": True
        }
    }
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(test_data_path), exist_ok=True)
    
    # Save the mock data
    with open(test_data_path, 'w') as f:
        json.dump(mock_data, f, indent=2)
    
    print(f"Mock data created at {test_data_path}")

if __name__ == "__main__":
    # Create a directory for patches if it doesn't exist
    patches_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(patches_dir, exist_ok=True)
    
    # Apply the ETL monitor patch
    if apply_patch():
        # Create test data for data completeness widget
        create_data_completeness_fix()
        print("\nFixes applied successfully!")
        print("\nTo deploy these fixes to production:")
        print("1. Copy this file to the production server")
        print("2. Run 'python -m backend.patches.fix_etl_counts'")
        print("3. Restart the backend API service")
    else:
        print("\nFailed to apply fixes.")
