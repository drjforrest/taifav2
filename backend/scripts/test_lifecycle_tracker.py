#!/usr/bin/env python3
"""
Test script for Innovation Lifecycle Tracker Service
"""

import asyncio
import uuid
from datetime import date

from config.database import get_supabase
from services.innovation_lifecycle_tracker import (
    LifecycleStage,
    innovation_lifecycle_tracker,
)


async def test_lifecycle_tracker():
    """Test the innovation lifecycle tracker service"""
    print("Testing Innovation Lifecycle Tracker Service...")
    
    # Initialize the service
    success = await innovation_lifecycle_tracker.initialize()
    if not success:
        print("Failed to initialize service")
        return
    
    print("Service initialized successfully")
    
    # Create a test innovation (if needed)
    supabase = get_supabase()
    
    # Check if we have any innovations
    response = supabase.table('innovations').select('id').limit(1).execute()
    
    if not response.data:
        print("No innovations found in database. Please add some test data first.")
        return
    
    innovation_id = uuid.UUID(response.data[0]['id'])
    print(f"Using innovation ID: {innovation_id}")
    
    # Test creating lifecycle records
    print("\nTesting lifecycle record creation...")
    
    # Create research stage
    success = await innovation_lifecycle_tracker.create_lifecycle_record(
        innovation_id=innovation_id,
        stage=LifecycleStage.RESEARCH,
        start_date=date(2023, 1, 1),
        end_date=date(2023, 6, 1),
        key_milestones=["Literature review completed", "Research proposal approved"],
        resources_invested={"funding": 50000, "personnel": 2},
        challenges_encountered=["Data access issues", "Equipment delays"],
        success_indicators=["Paper published", "Grant awarded"]
    )
    
    if success:
        print("Research stage record created successfully")
    else:
        print("Failed to create research stage record")
    
    # Create prototype stage
    success = await innovation_lifecycle_tracker.create_lifecycle_record(
        innovation_id=innovation_id,
        stage=LifecycleStage.PROTOTYPE,
        start_date=date(2023, 6, 1),
        end_date=date(2023, 12, 1),
        key_milestones=["MVP developed", "Initial testing completed"],
        resources_invested={"funding": 100000, "personnel": 3},
        challenges_encountered=["Technical implementation issues"],
        success_indicators=["Working prototype", "Positive user feedback"]
    )
    
    if success:
        print("Prototype stage record created successfully")
    else:
        print("Failed to create prototype stage record")
    
    # Test getting lifecycle data
    print("\nTesting lifecycle data retrieval...")
    lifecycle_stages = await innovation_lifecycle_tracker.get_innovation_lifecycle(innovation_id)
    print(f"Retrieved {len(lifecycle_stages)} lifecycle stages")
    
    for stage in lifecycle_stages:
        print(f"  - Stage: {stage.stage.value}")
        print(f"    Duration: {stage.duration_days} days")
        print(f"    Milestones: {stage.key_milestones}")
    
    # Test metrics calculation
    print("\nTesting metrics calculation...")
    metrics = await innovation_lifecycle_tracker.get_lifecycle_metrics(innovation_id)
    print(f"Total duration: {metrics.total_duration_days} days")
    print(f"Time to market: {metrics.time_to_market_days} days")
    print(f"Current stage: {metrics.current_stage.value if metrics.current_stage else 'None'}")
    print(f"Completed cycle: {metrics.has_completed_cycle}")
    
    if metrics.stage_durations:
        print("Stage durations:")
        for stage, duration in metrics.stage_durations.items():
            print(f"  - {stage.value}: {duration} days")
    
    # Test analytics
    print("\nTesting lifecycle analytics...")
    analytics = await innovation_lifecycle_tracker.get_lifecycle_analytics()
    print(f"Total lifecycle records: {analytics['total_records']}")
    print(f"Stage distribution: {analytics['stage_distribution']}")
    print(f"Average duration by stage: {analytics['avg_duration_by_stage']}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_lifecycle_tracker())