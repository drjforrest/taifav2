#!/usr/bin/env python3
"""
Test script for Domain Evolution Mapper Service
"""

import asyncio
from datetime import date, datetime
from uuid import UUID

from config.database import get_supabase
from services.domain_evolution_mapper import (
    DomainMaturityLevel,
    domain_evolution_mapper,
)


async def test_domain_evolution_mapper():
    """Test the domain evolution mapper service"""
    print("Testing Domain Evolution Mapper Service...")

    # Initialize the service
    success = await domain_evolution_mapper.initialize()
    if not success:
        print("Failed to initialize service")
        return

    print("Service initialized successfully")

    # Test tracking domain evolution for a sample period
    print("\nTesting domain evolution tracking...")

    # Track machine learning domain evolution for 2023
    success = await domain_evolution_mapper.track_domain_evolution(
        domain_name="machine_learning",
        period_start=date(2023, 1, 1),
        period_end=date(2023, 12, 31),
    )

    if success:
        print("Machine learning domain evolution tracked successfully for 2023")
    else:
        print("Failed to track machine learning domain evolution for 2023")

    # Track computer vision domain evolution for 2023
    success = await domain_evolution_mapper.track_domain_evolution(
        domain_name="computer_vision",
        period_start=date(2023, 1, 1),
        period_end=date(2023, 12, 31),
    )

    if success:
        print("Computer vision domain evolution tracked successfully for 2023")
    else:
        print("Failed to track computer vision domain evolution for 2023")

    # Test identifying emerging domains
    print("\nTesting emerging domain identification...")
    emerging_domains = await domain_evolution_mapper.identify_emerging_domains(
        period_start=date(2023, 1, 1), period_end=date(2023, 12, 31)
    )

    print(f"Found {len(emerging_domains)} emerging domains:")
    for domain in emerging_domains:
        print(f"  - {domain.domain_name} (confidence: {domain.confidence_score}%)")

    # Test mapping research focus areas
    print("\nTesting research focus area mapping...")
    focus_areas = await domain_evolution_mapper.map_research_focus_areas(
        period_start=date(2023, 1, 1), period_end=date(2023, 12, 31)
    )

    if focus_areas:
        print(
            f"Analyzed {focus_areas.get('total_publications_analyzed', 0)} publications"
        )
        print("Top focus areas:")
        for area, percentage in list(focus_areas.get("focus_areas", {}).items())[:5]:
            print(f"  - {area}: {percentage}%")
    else:
        print("No focus areas data found")

    # Test getting domain trends
    print("\nTesting domain trends retrieval...")
    ml_trends = await domain_evolution_mapper.get_domain_trends("machine_learning")

    if ml_trends.time_series:
        print(f"Machine learning domain trends:")
        print(f"  Overall growth rate: {ml_trends.overall_growth_rate}%")
        print(
            f"  Maturity trajectory: {[m.value for m in ml_trends.maturity_trajectory]}"
        )
        print(f"  Key influencers: {ml_trends.key_influencers}")
    else:
        print("No machine learning trends data found")

    # Test getting all domain trends
    print("\nTesting all domain trends retrieval...")
    all_trends = await domain_evolution_mapper.get_all_domain_trends()

    print(f"Found data for {len(all_trends)} domains:")
    for trend in all_trends[:5]:  # Show top 5
        print(f"  - {trend.domain_name}: {trend.overall_growth_rate}% growth")

    print("\nTest completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_domain_evolution_mapper())
