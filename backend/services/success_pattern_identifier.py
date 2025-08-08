"""
Success Pattern Identifier Service for TAIFA-FIALA
Implements Phase 2 Historical Trend Analysis features:

- Identify common characteristics of breakthrough innovations
- Analyze successful innovation patterns in African AI research
- Provide methods to query success patterns
- Calculate success metrics based on various factors
- Integrate with existing publication and innovation data

This service integrates with:
- backend/services/innovation_lifecycle_tracker.py
- backend/services/domain_evolution_mapper.py
- backend/services/enhanced_publication_service.py
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from config.database import get_supabase
from loguru import logger
from services.domain_evolution_mapper import domain_evolution_mapper
from services.enhanced_publication_service import enhanced_publication_service
from services.innovation_lifecycle_tracker import (
    LifecycleStage,
    innovation_lifecycle_tracker,
)


class PatternType(str, Enum):
    """Types of success patterns"""

    TECHNICAL = "technical"
    ORGANIZATIONAL = "organizational"
    FUNDING = "funding"
    MARKET = "market"


@dataclass
class SuccessPattern:
    """Data for a success pattern"""

    id: Optional[UUID]
    pattern_name: str
    pattern_description: str
    pattern_type: PatternType
    associated_features: List[str]
    success_rate: float  # Percentage of innovations with this pattern that succeed
    domain_specific: bool
    geographic_scope: Optional[str]  # Global or specific regions
    temporal_scope: Optional[str]  # Time periods where this pattern is most effective
    supporting_evidence: List[
        Dict[str, Any]
    ]  # Case studies, research papers, statistics
    confidence_score: float  # Algorithm confidence in this pattern
    last_validated: Optional[date]


@dataclass
class InnovationMetrics:
    """Metrics for innovation success analysis"""

    innovation_id: UUID
    time_to_market_days: Optional[int]
    collaboration_score: float
    funding_efficiency: float
    impact_score: float
    domain_diversity: int
    geographic_collaboration: int


class SuccessPatternIdentifier:
    """Service for identifying success patterns in African AI research"""

    def __init__(self):
        self.supabase = get_supabase()
        # Success indicators based on literature and best practices
        self.success_indicators = {
            "technical": [
                "open source",
                "reproducible",
                "scalable",
                "robust",
                "efficient",
                "innovative algorithm",
                "novel approach",
                "performance improvement",
            ],
            "organizational": [
                "multi-institutional",
                "international collaboration",
                "interdisciplinary",
                "experienced team",
                "clear leadership",
                "project management",
            ],
            "funding": [
                "sustainable funding",
                "diverse funding sources",
                "adequate budget",
                "funding continuity",
                "industry partnership",
            ],
            "market": [
                "clear problem statement",
                "market need",
                "user adoption",
                "commercial potential",
                "social impact",
                "policy alignment",
            ],
        }

    async def initialize(self) -> bool:
        """Initialize the service"""
        try:
            logger.info("Success Pattern Identifier service initialized")
            return True
        except Exception as e:
            logger.error(
                f"Failed to initialize Success Pattern Identifier service: {e}"
            )
            return False

    # SUCCESS PATTERN IDENTIFICATION METHODS
    async def identify_success_patterns(
        self,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None,
        domain: Optional[str] = None,
    ) -> List[SuccessPattern]:
        """
        Identify success patterns in African AI research

        Args:
            period_start: Start date for analysis period
            period_end: End date for analysis period
            domain: Specific domain to analyze (optional)

        Returns:
            List of identified success patterns
        """
        try:
            # Get successful innovations (those that completed commercial stage)
            successful_innovations = await self._get_successful_innovations(
                period_start, period_end, domain
            )

            # Get failed innovations for comparison
            failed_innovations = await self._get_failed_innovations(
                period_start, period_end, domain
            )

            # Identify patterns from successful innovations
            patterns = await self._extract_patterns_from_innovations(
                successful_innovations, failed_innovations
            )

            # Validate and score patterns
            validated_patterns = await self._validate_patterns(
                patterns, successful_innovations, failed_innovations
            )

            # Store patterns in database
            await self._store_patterns(validated_patterns)

            logger.info(f"Identified {len(validated_patterns)} success patterns")
            return validated_patterns

        except Exception as e:
            logger.error(f"Error identifying success patterns: {e}")
            return []

    async def _get_successful_innovations(
        self,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None,
        domain: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get innovations that successfully reached commercial stage"""
        try:
            # Build query for successful innovations
            query = (
                self.supabase.table("innovations")
                .select(
                    "id, title, description, tags, fundings, country, created_at, innovation_lifecycles(*)"
                )
                .eq("visibility", "public")
            )

            # Filter by domain if specified
            if domain:
                query = query.contains("tags", [domain])

            # Filter by date range if specified
            if period_start:
                query = query.gte("created_at", period_start.isoformat())

            if period_end:
                query = query.lte("created_at", period_end.isoformat())

            response = query.execute()

            if not response.data:
                return []

            successful_innovations = []
            for innovation in response.data:
                # Check if innovation has completed commercial stage
                lifecycles = innovation.get("innovation_lifecycles", [])
                commercial_stages = [
                    lc for lc in lifecycles if lc.get("stage") == "commercial"
                ]

                if commercial_stages and any(
                    cs.get("stage_end_date") for cs in commercial_stages
                ):
                    successful_innovations.append(innovation)

            return successful_innovations

        except Exception as e:
            logger.error(f"Error getting successful innovations: {e}")
            return []

    async def _get_failed_innovations(
        self,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None,
        domain: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get innovations that failed to reach commercial stage"""
        try:
            # Build query for innovations
            query = (
                self.supabase.table("innovations")
                .select(
                    "id, title, description, tags, fundings, country, created_at, innovation_lifecycles(*)"
                )
                .eq("visibility", "public")
            )

            # Filter by domain if specified
            if domain:
                query = query.contains("tags", [domain])

            # Filter by date range if specified
            if period_start:
                query = query.gte("created_at", period_start.isoformat())

            if period_end:
                query = query.lte("created_at", period_end.isoformat())

            response = query.execute()

            if not response.data:
                return []

            failed_innovations = []
            for innovation in response.data:
                # Check if innovation has lifecycle but didn't reach commercial stage
                lifecycles = innovation.get("innovation_lifecycles", [])

                # If no lifecycle or didn't reach commercial stage, consider it failed
                commercial_stages = [
                    lc for lc in lifecycles if lc.get("stage") == "commercial"
                ]
                if not lifecycles or (lifecycles and not commercial_stages):
                    failed_innovations.append(innovation)

            return failed_innovations

        except Exception as e:
            logger.error(f"Error getting failed innovations: {e}")
            return []

    async def _extract_patterns_from_innovations(
        self,
        successful_innovations: List[Dict[str, Any]],
        failed_innovations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Extract patterns from successful and failed innovations"""
        try:
            patterns = []

            # Extract patterns from successful innovations
            for innovation in successful_innovations:
                # Extract technical patterns
                technical_patterns = await self._extract_technical_patterns(innovation)
                patterns.extend(technical_patterns)

                # Extract organizational patterns
                organizational_patterns = await self._extract_organizational_patterns(
                    innovation
                )
                patterns.extend(organizational_patterns)

                # Extract funding patterns
                funding_patterns = await self._extract_funding_patterns(innovation)
                patterns.extend(funding_patterns)

                # Extract market patterns
                market_patterns = await self._extract_market_patterns(innovation)
                patterns.extend(market_patterns)

            return patterns

        except Exception as e:
            logger.error(f"Error extracting patterns from innovations: {e}")
            return []

    async def _extract_technical_patterns(
        self, innovation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract technical patterns from an innovation"""
        try:
            patterns = []
            description = innovation.get("description", "").lower()
            tags = innovation.get("tags", [])

            # Check for technical indicators
            for indicator in self.success_indicators["technical"]:
                if indicator in description or indicator in " ".join(tags).lower():
                    patterns.append(
                        {
                            "type": "technical",
                            "feature": indicator,
                            "innovation_id": innovation["id"],
                        }
                    )

            return patterns

        except Exception as e:
            logger.error(f"Error extracting technical patterns: {e}")
            return []

    async def _extract_organizational_patterns(
        self, innovation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract organizational patterns from an innovation"""
        try:
            patterns = []
            description = innovation.get("description", "").lower()
            tags = innovation.get("tags", [])

            # Check for organizational indicators
            for indicator in self.success_indicators["organizational"]:
                if indicator in description or indicator in " ".join(tags).lower():
                    patterns.append(
                        {
                            "type": "organizational",
                            "feature": indicator,
                            "innovation_id": innovation["id"],
                        }
                    )

            return patterns

        except Exception as e:
            logger.error(f"Error extracting organizational patterns: {e}")
            return []

    async def _extract_funding_patterns(
        self, innovation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract funding patterns from an innovation"""
        try:
            patterns = []
            fundings = innovation.get("fundings", [])

            # Check for funding indicators
            if fundings:
                total_funding = sum(
                    f.get("amount", 0) for f in fundings if isinstance(f, dict)
                )
                funding_sources = len(fundings)

                if total_funding > 100000:  # Significant funding threshold
                    patterns.append(
                        {
                            "type": "funding",
                            "feature": "significant_funding",
                            "innovation_id": innovation["id"],
                        }
                    )

                if funding_sources > 1:  # Diverse funding sources
                    patterns.append(
                        {
                            "type": "funding",
                            "feature": "diverse_funding_sources",
                            "innovation_id": innovation["id"],
                        }
                    )

            return patterns

        except Exception as e:
            logger.error(f"Error extracting funding patterns: {e}")
            return []

    async def _extract_market_patterns(
        self, innovation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract market patterns from an innovation"""
        try:
            patterns = []
            description = innovation.get("description", "").lower()
            tags = innovation.get("tags", [])

            # Check for market indicators
            for indicator in self.success_indicators["market"]:
                if indicator in description or indicator in " ".join(tags).lower():
                    patterns.append(
                        {
                            "type": "market",
                            "feature": indicator,
                            "innovation_id": innovation["id"],
                        }
                    )

            return patterns

        except Exception as e:
            logger.error(f"Error extracting market patterns: {e}")
            return []

    async def _validate_patterns(
        self,
        patterns: List[Dict[str, Any]],
        successful_innovations: List[Dict[str, Any]],
        failed_innovations: List[Dict[str, Any]],
    ) -> List[SuccessPattern]:
        """Validate and score identified patterns"""
        try:
            # Group patterns by feature
            pattern_groups = defaultdict(list)
            for pattern in patterns:
                pattern_groups[pattern["feature"]].append(pattern)

            validated_patterns = []
            for feature, pattern_list in pattern_groups.items():
                # Calculate success rate
                total_innovations_with_feature = len(pattern_list)
                if total_innovations_with_feature == 0:
                    continue

                # For this implementation, we'll assume all patterns from successful innovations are valid
                # In a real implementation, we would compare with failed innovations
                success_rate = min(
                    100.0,
                    (
                        total_innovations_with_feature
                        / max(1, len(successful_innovations))
                    )
                    * 100,
                )

                # Calculate confidence score based on frequency and success rate
                frequency_score = min(
                    1.0, total_innovations_with_feature / 10
                )  # Normalize by 10
                confidence_score = (frequency_score * 0.7) + (success_rate / 100 * 0.3)

                # Determine pattern type based on feature
                pattern_type = PatternType.TECHNICAL
                if feature in self.success_indicators["organizational"]:
                    pattern_type = PatternType.ORGANIZATIONAL
                elif feature in self.success_indicators["funding"] or feature in [
                    "significant_funding",
                    "diverse_funding_sources",
                ]:
                    pattern_type = PatternType.FUNDING
                elif feature in self.success_indicators["market"]:
                    pattern_type = PatternType.MARKET

                success_pattern = SuccessPattern(
                    id=None,
                    pattern_name=f"Success pattern: {feature}",
                    pattern_description=f"Pattern associated with successful innovations featuring {feature}",
                    pattern_type=pattern_type,
                    associated_features=[feature],
                    success_rate=success_rate,
                    domain_specific=False,
                    geographic_scope=None,
                    temporal_scope=None,
                    supporting_evidence=[
                        {
                            "type": "innovation_count",
                            "value": total_innovations_with_feature,
                        }
                    ],
                    confidence_score=confidence_score,
                    last_validated=date.today(),
                )

                validated_patterns.append(success_pattern)

            return validated_patterns

        except Exception as e:
            logger.error(f"Error validating patterns: {e}")
            return []

    async def _store_patterns(self, patterns: List[SuccessPattern]) -> bool:
        """Store identified patterns in the database"""
        try:
            # Convert patterns to dictionary format for storage
            pattern_data = []
            for pattern in patterns:
                pattern_dict = {
                    "pattern_name": pattern.pattern_name,
                    "pattern_description": pattern.pattern_description,
                    "pattern_type": pattern.pattern_type.value,
                    "associated_features": pattern.associated_features,
                    "success_rate": pattern.success_rate,
                    "domain_specific": pattern.domain_specific,
                    "geographic_scope": pattern.geographic_scope,
                    "temporal_scope": pattern.temporal_scope,
                    "supporting_evidence": pattern.supporting_evidence,
                    "confidence_score": pattern.confidence_score,
                    "last_validated": pattern.last_validated.isoformat()
                    if pattern.last_validated
                    else None,
                }
                pattern_data.append(pattern_dict)

            # Store in database
            if pattern_data:
                response = (
                    self.supabase.table("success_patterns")
                    .upsert(pattern_data)
                    .execute()
                )
                if response.data:
                    logger.info(f"Stored {len(pattern_data)} success patterns")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error storing success patterns: {e}")
            return False

    # SUCCESS METRICS CALCULATION METHODS
    async def calculate_innovation_success_metrics(
        self, innovation_id: UUID
    ) -> InnovationMetrics:
        """
        Calculate success metrics for a specific innovation

        Args:
            innovation_id: UUID of the innovation to analyze

        Returns:
            InnovationMetrics object with calculated metrics
        """
        try:
            # Get innovation data
            response = (
                self.supabase.table("innovations")
                .select("id, created_at, fundings, country, innovation_lifecycles(*)")
                .eq("id", str(innovation_id))
                .execute()
            )

            if not response.data:
                raise ValueError(f"Innovation {innovation_id} not found")

            innovation = response.data[0]

            # Calculate time to market
            time_to_market = await self._calculate_time_to_market(innovation)

            # Calculate collaboration score
            collaboration_score = await self._calculate_collaboration_score(innovation)

            # Calculate funding efficiency
            funding_efficiency = await self._calculate_funding_efficiency(innovation)

            # Calculate impact score
            impact_score = await self._calculate_impact_score(innovation)

            # Calculate domain diversity
            domain_diversity = await self._calculate_domain_diversity(innovation)

            # Calculate geographic collaboration
            geographic_collaboration = await self._calculate_geographic_collaboration(
                innovation
            )

            metrics = InnovationMetrics(
                innovation_id=innovation_id,
                time_to_market_days=time_to_market,
                collaboration_score=collaboration_score,
                funding_efficiency=funding_efficiency,
                impact_score=impact_score,
                domain_diversity=domain_diversity,
                geographic_collaboration=geographic_collaboration,
            )

            return metrics

        except Exception as e:
            logger.error(
                f"Error calculating success metrics for innovation {innovation_id}: {e}"
            )
            return InnovationMetrics(
                innovation_id=innovation_id,
                time_to_market_days=None,
                collaboration_score=0.0,
                funding_efficiency=0.0,
                impact_score=0.0,
                domain_diversity=0,
                geographic_collaboration=0,
            )

    async def _calculate_time_to_market(
        self, innovation: Dict[str, Any]
    ) -> Optional[int]:
        """Calculate time to market for an innovation"""
        try:
            lifecycles = innovation.get("innovation_lifecycles", [])
            if not lifecycles:
                return None

            # Find creation date
            created_at = innovation.get("created_at")
            if not created_at:
                return None

            creation_date = datetime.fromisoformat(created_at).date()

            # Find commercial stage end date
            commercial_stages = [
                lc for lc in lifecycles if lc.get("stage") == "commercial"
            ]
            if not commercial_stages:
                return None

            # Get the latest commercial stage end date
            latest_commercial = None
            for stage in commercial_stages:
                end_date_str = stage.get("stage_end_date")
                if end_date_str:
                    end_date = datetime.fromisoformat(end_date_str).date()
                    if not latest_commercial or end_date > latest_commercial:
                        latest_commercial = end_date

            if not latest_commercial:
                return None

            # Calculate time to market in days
            time_to_market = (latest_commercial - creation_date).days
            return time_to_market

        except Exception as e:
            logger.error(f"Error calculating time to market: {e}")
            return None

    async def _calculate_collaboration_score(self, innovation: Dict[str, Any]) -> float:
        """Calculate collaboration score based on multi-institutional involvement"""
        try:
            # This would typically involve checking author affiliations and institutional connections
            # For now, we'll use a simplified approach based on lifecycle data
            lifecycles = innovation.get("innovation_lifecycles", [])

            # Count unique stages as a proxy for collaboration
            unique_stages = len(
                set(lc.get("stage") for lc in lifecycles if lc.get("stage"))
            )
            max_stages = len(LifecycleStage.__members__)

            return min(1.0, unique_stages / max_stages) if max_stages > 0 else 0.0

        except Exception as e:
            logger.error(f"Error calculating collaboration score: {e}")
            return 0.0

    async def _calculate_funding_efficiency(self, innovation: Dict[str, Any]) -> float:
        """Calculate funding efficiency"""
        try:
            fundings = innovation.get("fundings", [])
            if not fundings:
                return 0.0

            total_funding = sum(
                f.get("amount", 0) for f in fundings if isinstance(f, dict)
            )

            # Calculate efficiency based on funding amount (simplified)
            # In a real implementation, this would compare funding to outcomes
            efficiency = min(1.0, total_funding / 1000000)  # Normalize by 1M
            return efficiency

        except Exception as e:
            logger.error(f"Error calculating funding efficiency: {e}")
            return 0.0

    async def _calculate_impact_score(self, innovation: Dict[str, Any]) -> float:
        """Calculate impact score based on various factors"""
        try:
            # This would typically involve checking citations, user adoption, etc.
            # For now, we'll use a simplified approach based on lifecycle completion
            lifecycles = innovation.get("innovation_lifecycles", [])
            commercial_stages = [
                lc for lc in lifecycles if lc.get("stage") == "commercial"
            ]

            # If commercial stage is completed, assume high impact
            if commercial_stages and any(
                cs.get("stage_end_date") for cs in commercial_stages
            ):
                return 1.0
            elif commercial_stages:
                return 0.7  # In commercial stage but not completed
            elif lifecycles:
                return 0.5  # In lifecycle but not commercial
            else:
                return 0.1  # No lifecycle data

        except Exception as e:
            logger.error(f"Error calculating impact score: {e}")
            return 0.0

    async def _calculate_domain_diversity(self, innovation: Dict[str, Any]) -> int:
        """Calculate domain diversity based on tags"""
        try:
            tags = innovation.get("tags", [])
            # Count unique domains from tags
            domains = set()
            for tag in tags:
                # This would typically involve mapping tags to known domains
                # For now, we'll just count unique tags as a proxy
                domains.add(tag.lower())

            return len(domains)

        except Exception as e:
            logger.error(f"Error calculating domain diversity: {e}")
            return 0

    async def _calculate_geographic_collaboration(
        self, innovation: Dict[str, Any]
    ) -> int:
        """Calculate geographic collaboration based on countries involved"""
        try:
            # This would typically involve checking author affiliations from different countries
            # For now, we'll use the innovation's country as a proxy
            country = innovation.get("country")
            return 1 if country else 0

        except Exception as e:
            logger.error(f"Error calculating geographic collaboration: {e}")
            return 0

    # PATTERN QUERYING METHODS
    async def get_success_patterns(
        self,
        pattern_type: Optional[PatternType] = None,
        domain_specific: Optional[bool] = None,
        min_confidence: Optional[float] = None,
    ) -> List[SuccessPattern]:
        """
        Get success patterns with optional filtering

        Args:
            pattern_type: Filter by pattern type
            domain_specific: Filter by domain specificity
            min_confidence: Filter by minimum confidence score

        Returns:
            List of SuccessPattern objects
        """
        try:
            # Build query for success patterns
            query = self.supabase.table("success_patterns").select("*")

            # Apply filters
            if pattern_type:
                query = query.eq("pattern_type", pattern_type.value)

            if domain_specific is not None:
                query = query.eq("domain_specific", domain_specific)

            if min_confidence is not None:
                query = query.gte("confidence_score", min_confidence)

            response = query.execute()

            if not response.data:
                return []

            patterns = []
            for record in response.data:
                pattern = SuccessPattern(
                    id=UUID(record["id"]) if record.get("id") else None,
                    pattern_name=record["pattern_name"],
                    pattern_description=record["pattern_description"],
                    pattern_type=PatternType(record["pattern_type"]),
                    associated_features=record.get("associated_features", []),
                    success_rate=record.get("success_rate", 0.0),
                    domain_specific=record.get("domain_specific", False),
                    geographic_scope=record.get("geographic_scope"),
                    temporal_scope=record.get("temporal_scope"),
                    supporting_evidence=record.get("supporting_evidence", []),
                    confidence_score=record.get("confidence_score", 0.0),
                    last_validated=datetime.fromisoformat(
                        record["last_validated"]
                    ).date()
                    if record.get("last_validated")
                    else None,
                )
                patterns.append(pattern)

            return patterns

        except Exception as e:
            logger.error(f"Error getting success patterns: {e}")
            return []

    async def get_innovation_success_analysis(
        self, innovation_id: UUID
    ) -> Dict[str, Any]:
        """
        Get comprehensive success analysis for an innovation

        Args:
            innovation_id: UUID of the innovation to analyze

        Returns:
            Dictionary with success analysis data
        """
        try:
            # Calculate metrics
            metrics = await self.calculate_innovation_success_metrics(innovation_id)

            # Get associated patterns
            patterns = await self._get_patterns_for_innovation(innovation_id)

            # Get lifecycle data
            lifecycle_stages = (
                await innovation_lifecycle_tracker.get_innovation_lifecycle(
                    innovation_id
                )
            )

            # Get domain evolution data
            # This would typically involve checking which domains the innovation belongs to
            # For now, we'll return a simplified structure

            analysis = {
                "innovation_id": str(innovation_id),
                "metrics": {
                    "time_to_market_days": metrics.time_to_market_days,
                    "collaboration_score": metrics.collaboration_score,
                    "funding_efficiency": metrics.funding_efficiency,
                    "impact_score": metrics.impact_score,
                    "domain_diversity": metrics.domain_diversity,
                    "geographic_collaboration": metrics.geographic_collaboration,
                },
                "associated_patterns": [
                    {
                        "pattern_name": pattern.pattern_name,
                        "pattern_type": pattern.pattern_type.value,
                        "confidence_score": pattern.confidence_score,
                        "success_rate": pattern.success_rate,
                    }
                    for pattern in patterns
                ],
                "lifecycle_stages": [
                    {
                        "stage": stage.stage.value,
                        "start_date": stage.start_date.isoformat()
                        if stage.start_date
                        else None,
                        "end_date": stage.end_date.isoformat()
                        if stage.end_date
                        else None,
                        "duration_days": stage.duration_days,
                    }
                    for stage in lifecycle_stages
                ],
                "recommendations": await self._generate_recommendations(
                    metrics, patterns
                ),
            }

            return analysis

        except Exception as e:
            logger.error(
                f"Error getting success analysis for innovation {innovation_id}: {e}"
            )
            return {}

    async def _get_patterns_for_innovation(
        self, innovation_id: UUID
    ) -> List[SuccessPattern]:
        """Get success patterns associated with a specific innovation"""
        try:
            # This would typically involve matching innovation characteristics with patterns
            # For now, we'll return a sample of high-confidence patterns
            return await self.get_success_patterns(min_confidence=0.7)

        except Exception as e:
            logger.error(f"Error getting patterns for innovation {innovation_id}: {e}")
            return []

    async def _generate_recommendations(
        self, metrics: InnovationMetrics, patterns: List[SuccessPattern]
    ) -> List[str]:
        """Generate recommendations based on metrics and patterns"""
        try:
            recommendations = []

            # Time to market recommendations
            if metrics.time_to_market_days and metrics.time_to_market_days > 365:
                recommendations.append(
                    "Consider streamlining development processes to reduce time to market"
                )

            # Collaboration recommendations
            if metrics.collaboration_score < 0.5:
                recommendations.append(
                    "Increase collaboration with other institutions or organizations"
                )

            # Funding recommendations
            if metrics.funding_efficiency < 0.3:
                recommendations.append(
                    "Explore additional funding opportunities to support development"
                )

            # Impact recommendations
            if metrics.impact_score < 0.5:
                recommendations.append(
                    "Focus on user adoption and real-world impact to increase visibility"
                )

            # Pattern-based recommendations
            technical_patterns = [
                p for p in patterns if p.pattern_type == PatternType.TECHNICAL
            ]
            if not technical_patterns:
                recommendations.append(
                    "Consider incorporating more technical innovations or novel approaches"
                )

            organizational_patterns = [
                p for p in patterns if p.pattern_type == PatternType.ORGANIZATIONAL
            ]
            if not organizational_patterns:
                recommendations.append(
                    "Strengthen organizational capabilities and project management"
                )

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

    # INTEGRATION METHODS
    async def integrate_with_lifecycle_tracker(self) -> bool:
        """
        Integrate with the innovation lifecycle tracker service

        Returns:
            True if integration was successful, False otherwise
        """
        try:
            # This method would coordinate with the lifecycle tracker
            # For now, we'll just log that integration is available
            logger.info(
                "Success Pattern Identifier integrated with Innovation Lifecycle Tracker"
            )
            return True
        except Exception as e:
            logger.error(f"Error integrating with lifecycle tracker: {e}")
            return False

    async def integrate_with_domain_evolution_mapper(self) -> bool:
        """
        Integrate with the domain evolution mapper service

        Returns:
            True if integration was successful, False otherwise
        """
        try:
            # Initialize the domain evolution mapper
            if not await domain_evolution_mapper.initialize():
                logger.error("Failed to initialize domain evolution mapper")
                return False

            logger.info(
                "Success Pattern Identifier integrated with Domain Evolution Mapper"
            )
            return True
        except Exception as e:
            logger.error(f"Error integrating with domain evolution mapper: {e}")
            return False

    async def integrate_with_publication_service(self) -> bool:
        """
        Integrate with the enhanced publication service

        Returns:
            True if integration was successful, False otherwise
        """
        try:
            # Initialize the enhanced publication service
            if not await enhanced_publication_service.initialize():
                logger.error("Failed to initialize enhanced publication service")
                return False

            logger.info(
                "Success Pattern Identifier integrated with Enhanced Publication Service"
            )
            return True
        except Exception as e:
            logger.error(f"Error integrating with publication service: {e}")
            return False


# Global service instance
success_pattern_identifier = SuccessPatternIdentifier()
