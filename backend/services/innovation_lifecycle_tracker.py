"""
Innovation Lifecycle Tracker Service for TAIFA-FIALA
Implements Phase 2 Historical Trend Analysis features:

- Track projects from research paper to market implementation
- Follow lifecycle stages: Research → Prototype → Pilot → Scaling → Commercial
- Integrate with existing publication and innovation data
- Provide methods to query lifecycle status of innovations
- Calculate time-to-market metrics

This service integrates with:
- backend/services/enhanced_publication_service.py
- backend/services/citations_analysis_service.py
"""

import asyncio
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from config.database import get_supabase
from loguru import logger


class LifecycleStage(str, Enum):
    """Lifecycle stages for innovation tracking"""
    RESEARCH = "research"
    PROTOTYPE = "prototype"
    PILOT = "pilot"
    PRODUCTION = "production"
    SCALING = "scaling"
    COMMERCIAL = "commercial"


@dataclass
class LifecycleStageData:
    """Data for a single lifecycle stage"""
    stage: LifecycleStage
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    duration_days: Optional[int] = None
    key_milestones: Optional[List[str]] = None
    resources_invested: Optional[Dict[str, Any]] = None
    challenges_encountered: Optional[List[str]] = None
    success_indicators: Optional[List[str]] = None


@dataclass
class LifecycleMetrics:
    """Metrics for innovation lifecycle analysis"""
    total_duration_days: Optional[int] = None
    time_to_market_days: Optional[int] = None
    current_stage: Optional[LifecycleStage] = None
    stage_durations: Optional[Dict[LifecycleStage, int]] = None
    has_completed_cycle: bool = False


class InnovationLifecycleTracker:
    """Service for tracking innovation lifecycles and analyzing trends"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.lifecycle_stages = [
            LifecycleStage.RESEARCH,
            LifecycleStage.PROTOTYPE,
            LifecycleStage.PILOT,
            LifecycleStage.PRODUCTION,
            LifecycleStage.SCALING,
            LifecycleStage.COMMERCIAL
        ]
    
    async def initialize(self) -> bool:
        """Initialize the service"""
        try:
            logger.info("Innovation Lifecycle Tracker service initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Innovation Lifecycle Tracker service: {e}")
            return False
    
    # LIFECYCLE TRACKING METHODS
    async def create_lifecycle_record(self, innovation_id: UUID, 
                                    stage: LifecycleStage,
                                    start_date: Optional[date] = None,
                                    end_date: Optional[date] = None,
                                    key_milestones: Optional[List[str]] = None,
                                    resources_invested: Optional[Dict[str, Any]] = None,
                                    challenges_encountered: Optional[List[str]] = None,
                                    success_indicators: Optional[List[str]] = None) -> bool:
        """Create a new lifecycle stage record for an innovation"""
        try:
            # Calculate duration if both dates are provided
            duration_days = None
            if start_date and end_date:
                duration_days = (end_date - start_date).days
            
            # Prepare record data
            record_data = {
                'innovation_id': str(innovation_id),
                'stage': stage.value,
                'stage_start_date': start_date.isoformat() if start_date else None,
                'stage_end_date': end_date.isoformat() if end_date else None,
                'duration_days': duration_days,
                'key_milestones': key_milestones or [],
                'resources_invested': resources_invested or {},
                'challenges_encountered': challenges_encountered or [],
                'success_indicators': success_indicators or []
            }
            
            # Insert record into database
            response = self.supabase.table('innovation_lifecycles').insert(record_data).execute()
            
            if response.data:
                logger.info(f"Created lifecycle record for innovation {innovation_id}, stage {stage.value}")
                return True
            else:
                logger.error(f"Failed to create lifecycle record for innovation {innovation_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating lifecycle record for innovation {innovation_id}: {e}")
            return False
    
    async def update_lifecycle_record(self, record_id: UUID,
                                    stage: Optional[LifecycleStage] = None,
                                    start_date: Optional[date] = None,
                                    end_date: Optional[date] = None,
                                    key_milestones: Optional[List[str]] = None,
                                    resources_invested: Optional[Dict[str, Any]] = None,
                                    challenges_encountered: Optional[List[str]] = None,
                                    success_indicators: Optional[List[str]] = None) -> bool:
        """Update an existing lifecycle stage record"""
        try:
            # Prepare update data
            update_data = {}
            
            if stage is not None:
                update_data['stage'] = stage.value
            
            if start_date is not None:
                update_data['stage_start_date'] = start_date.isoformat()
            
            if end_date is not None:
                update_data['stage_end_date'] = end_date.isoformat()
            
            # Calculate duration if both dates are provided
            if start_date is not None and end_date is not None:
                update_data['duration_days'] = (end_date - start_date).days
            elif start_date is not None and 'stage_end_date' in update_data:
                # If only start_date is updated, recalculate with existing end_date
                pass  # Would need to fetch existing end_date
            elif end_date is not None and 'stage_start_date' in update_data:
                # If only end_date is updated, recalculate with existing start_date
                pass  # Would need to fetch existing start_date
            
            if key_milestones is not None:
                update_data['key_milestones'] = key_milestones
            
            if resources_invested is not None:
                update_data['resources_invested'] = resources_invested
            
            if challenges_encountered is not None:
                update_data['challenges_encountered'] = challenges_encountered
            
            if success_indicators is not None:
                update_data['success_indicators'] = success_indicators
            
            # Update record in database
            response = self.supabase.table('innovation_lifecycles').update(update_data).eq('id', str(record_id)).execute()
            
            if response.data:
                logger.info(f"Updated lifecycle record {record_id}")
                return True
            else:
                logger.error(f"Failed to update lifecycle record {record_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating lifecycle record {record_id}: {e}")
            return False
    
    async def get_innovation_lifecycle(self, innovation_id: UUID) -> List[LifecycleStageData]:
        """Get all lifecycle records for a specific innovation"""
        try:
            response = self.supabase.table('innovation_lifecycles').select('*').eq('innovation_id', str(innovation_id)).order('stage_start_date').execute()
            
            if not response.data:
                return []
            
            lifecycle_stages = []
            for record in response.data:
                stage_data = LifecycleStageData(
                    stage=LifecycleStage(record['stage']),
                    start_date=datetime.fromisoformat(record['stage_start_date']).date() if record.get('stage_start_date') else None,
                    end_date=datetime.fromisoformat(record['stage_end_date']).date() if record.get('stage_end_date') else None,
                    duration_days=record.get('duration_days'),
                    key_milestones=record.get('key_milestones', []),
                    resources_invested=record.get('resources_invested', {}),
                    challenges_encountered=record.get('challenges_encountered', []),
                    success_indicators=record.get('success_indicators', [])
                )
                lifecycle_stages.append(stage_data)
            
            return lifecycle_stages
            
        except Exception as e:
            logger.error(f"Error getting lifecycle for innovation {innovation_id}: {e}")
            return []
    
    async def get_lifecycle_metrics(self, innovation_id: UUID) -> LifecycleMetrics:
        """Calculate lifecycle metrics for an innovation"""
        try:
            lifecycle_stages = await self.get_innovation_lifecycle(innovation_id)
            
            if not lifecycle_stages:
                return LifecycleMetrics()
            
            # Calculate metrics
            stage_durations = {}
            total_duration = 0
            current_stage = None
            has_completed_cycle = False
            
            # Get innovation creation date for time-to-market calculation
            innovation_response = self.supabase.table('innovations').select('creation_date').eq('id', str(innovation_id)).execute()
            creation_date = None
            if innovation_response.data and innovation_response.data[0].get('creation_date'):
                creation_date = datetime.fromisoformat(innovation_response.data[0]['creation_date']).date()
            
            # Process each stage
            for stage_data in lifecycle_stages:
                stage_durations[stage_data.stage] = stage_data.duration_days or 0
                total_duration += stage_data.duration_days or 0
                
                # Track current stage (last stage in the lifecycle)
                current_stage = stage_data.stage
                
                # Check if cycle is completed
                if stage_data.stage == LifecycleStage.COMMERCIAL and stage_data.end_date:
                    has_completed_cycle = True
            
            # Calculate time-to-market if we have creation date and commercial stage end date
            time_to_market = None
            if creation_date and lifecycle_stages:
                last_stage = lifecycle_stages[-1]
                if last_stage.end_date:
                    time_to_market = (last_stage.end_date - creation_date).days
                elif last_stage.start_date:
                    time_to_market = (last_stage.start_date - creation_date).days
            
            return LifecycleMetrics(
                total_duration_days=total_duration,
                time_to_market_days=time_to_market,
                current_stage=current_stage,
                stage_durations=stage_durations,
                has_completed_cycle=has_completed_cycle
            )
            
        except Exception as e:
            logger.error(f"Error calculating lifecycle metrics for innovation {innovation_id}: {e}")
            return LifecycleMetrics()
    
    # INTEGRATION METHODS
    async def link_publication_to_innovation_lifecycle(self, publication_id: UUID, innovation_id: UUID) -> bool:
        """Link a publication to an innovation's lifecycle (for research stage tracking)"""
        try:
            # Check if publication exists
            pub_response = self.supabase.table('publications').select('id, publication_date').eq('id', str(publication_id)).execute()
            if not pub_response.data:
                logger.error(f"Publication {publication_id} not found")
                return False
            
            publication = pub_response.data[0]
            pub_date = None
            if publication.get('publication_date'):
                pub_date = datetime.fromisoformat(publication['publication_date']).date()
            
            # Check if innovation lifecycle already has a research stage
            lifecycle_response = self.supabase.table('innovation_lifecycles').select('id').eq('innovation_id', str(innovation_id)).eq('stage', 'research').execute()
            
            if lifecycle_response.data:
                # Update existing research stage
                update_data = {
                    'key_milestones': ['Research paper published']
                }
                if pub_date:
                    update_data['stage_start_date'] = pub_date.isoformat()
                
                response = self.supabase.table('innovation_lifecycles').update(update_data).eq('id', lifecycle_response.data[0]['id']).execute()
            else:
                # Create new research stage
                record_data = {
                    'innovation_id': str(innovation_id),
                    'stage': 'research',
                    'stage_start_date': pub_date.isoformat() if pub_date else None,
                    'key_milestones': ['Research paper published']
                }
                response = self.supabase.table('innovation_lifecycles').insert(record_data).execute()
            
            if response.data:
                logger.info(f"Linked publication {publication_id} to innovation {innovation_id} lifecycle")
                return True
            else:
                logger.error(f"Failed to link publication {publication_id} to innovation {innovation_id} lifecycle")
                return False
                
        except Exception as e:
            logger.error(f"Error linking publication {publication_id} to innovation {innovation_id}: {e}")
            return False
    
    async def get_lifecycle_analytics(self, stage: Optional[LifecycleStage] = None, 
                                    country: Optional[str] = None,
                                    innovation_type: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics on innovation lifecycles across the platform"""
        try:
            # Build base query for lifecycle data
            query = self.supabase.table('innovation_lifecycles').select('*, innovations(country, innovation_type)').eq('innovations.visibility', 'public')
            
            # Apply filters
            if stage:
                query = query.eq('stage', stage.value)
            
            lifecycle_response = query.execute()
            
            if not lifecycle_response.data:
                return {
                    'total_records': 0,
                    'stage_distribution': {},
                    'avg_duration_by_stage': {},
                    'completion_rates': {}
                }
            
            # Process data
            stage_counts = defaultdict(int)
            stage_durations = defaultdict(list)
            country_counts = defaultdict(int)
            innovation_type_counts = defaultdict(int)
            completed_cycles = 0
            total_innovations = len(set(record['innovation_id'] for record in lifecycle_response.data))
            
            # Get all innovations for completion rate calculation
            innovation_ids = [record['innovation_id'] for record in lifecycle_response.data]
            if innovation_ids:
                innovation_response = self.supabase.table('innovations').select('id').in_('id', innovation_ids).eq('visibility', 'public').execute()
                total_innovations = len(innovation_response.data) if innovation_response.data else 0
            
            for record in lifecycle_response.data:
                stage_val = record['stage']
                stage_counts[stage_val] += 1
                
                if record.get('duration_days'):
                    stage_durations[stage_val].append(record['duration_days'])
                
                # Get innovation details if available
                if record.get('innovations'):
                    innovation = record['innovations']
                    if innovation.get('country'):
                        country_counts[innovation['country']] += 1
                    if innovation.get('innovation_type'):
                        innovation_type_counts[innovation['innovation_type']] += 1
                
                # Check for completed cycles
                if stage_val == 'commercial' and record.get('stage_end_date'):
                    completed_cycles += 1
            
            # Calculate averages
            avg_duration_by_stage = {}
            for stage_name, durations in stage_durations.items():
                if durations:
                    avg_duration_by_stage[stage_name] = round(sum(durations) / len(durations), 1)
            
            # Calculate completion rates
            completion_rate = (completed_cycles / max(1, total_innovations)) * 100 if total_innovations > 0 else 0
            
            return {
                'total_records': len(lifecycle_response.data),
                'total_innovations_tracked': total_innovations,
                'stage_distribution': dict(stage_counts),
                'avg_duration_by_stage': avg_duration_by_stage,
                'completion_rates': {
                    'completed_cycles': completed_cycles,
                    'total_innovations': total_innovations,
                    'completion_rate_percent': round(completion_rate, 1)
                },
                'by_country': dict(country_counts),
                'by_innovation_type': dict(innovation_type_counts)
            }
            
        except Exception as e:
            logger.error(f"Error getting lifecycle analytics: {e}")
            return {
                'total_records': 0,
                'stage_distribution': {},
                'avg_duration_by_stage': {},
                'completion_rates': {},
                'by_country': {},
                'by_innovation_type': {}
            }
    
    async def get_time_to_market_analysis(self, country: Optional[str] = None,
                                        innovation_type: Optional[str] = None) -> Dict[str, Any]:
        """Analyze time-to-market metrics across innovations"""
        try:
            # Get all innovations with their lifecycles
            query = self.supabase.table('innovations').select('id, creation_date, country, innovation_type, innovation_lifecycles(*)').eq('visibility', 'public')
            
            if country:
                query = query.eq('country', country)
            
            if innovation_type:
                query = query.eq('innovation_type', innovation_type)
            
            response = query.execute()
            
            if not response.data:
                return {
                    'total_innovations': 0,
                    'avg_time_to_market': 0,
                    'median_time_to_market': 0,
                    'min_time_to_market': 0,
                    'max_time_to_market': 0,
                    'completion_rate': 0
                }
            
            time_to_market_values = []
            completed_innovations = 0
            
            for innovation in response.data:
                creation_date = None
                if innovation.get('creation_date'):
                    creation_date = datetime.fromisoformat(innovation['creation_date']).date()
                
                # Get lifecycle records
                lifecycles = innovation.get('innovation_lifecycles', [])
                if not lifecycles or not creation_date:
                    continue
                
                # Find the end date of the last stage
                last_stage_end = None
                last_stage_start = None
                
                for lifecycle in lifecycles:
                    if lifecycle.get('stage') == 'commercial':
                        if lifecycle.get('stage_end_date'):
                            last_stage_end = datetime.fromisoformat(lifecycle['stage_end_date']).date()
                        elif lifecycle.get('stage_start_date'):
                            last_stage_start = datetime.fromisoformat(lifecycle['stage_start_date']).date()
                
                # Calculate time to market
                if last_stage_end:
                    time_to_market = (last_stage_end - creation_date).days
                    time_to_market_values.append(time_to_market)
                    completed_innovations += 1
                elif last_stage_start:
                    time_to_market = (last_stage_start - creation_date).days
                    time_to_market_values.append(time_to_market)
            
            if not time_to_market_values:
                return {
                    'total_innovations': len(response.data),
                    'avg_time_to_market': 0,
                    'median_time_to_market': 0,
                    'min_time_to_market': 0,
                    'max_time_to_market': 0,
                    'completion_rate': 0
                }
            
            # Calculate statistics
            time_to_market_values.sort()
            avg_time = sum(time_to_market_values) / len(time_to_market_values)
            median_time = time_to_market_values[len(time_to_market_values) // 2]
            min_time = min(time_to_market_values)
            max_time = max(time_to_market_values)
            completion_rate = (completed_innovations / len(response.data)) * 100
            
            return {
                'total_innovations': len(response.data),
                'innovations_with_lifecycle_data': len(time_to_market_values),
                'avg_time_to_market_days': round(avg_time, 1),
                'median_time_to_market_days': median_time,
                'min_time_to_market_days': min_time,
                'max_time_to_market_days': max_time,
                'completion_rate_percent': round(completion_rate, 1),
                'by_country': country,
                'by_innovation_type': innovation_type
            }
            
        except Exception as e:
            logger.error(f"Error analyzing time-to-market: {e}")
            return {
                'total_innovations': 0,
                'avg_time_to_market': 0,
                'median_time_to_market': 0,
                'min_time_to_market': 0,
                'max_time_to_market': 0,
                'completion_rate': 0
            }


# Global service instance
innovation_lifecycle_tracker = InnovationLifecycleTracker()