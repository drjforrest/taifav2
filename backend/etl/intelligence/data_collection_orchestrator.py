"""
TAIFA-FIALA Data Collection Orchestrator
========================================

Mission: Coordinate all data collectors with clear missions for comprehensive
African AI innovation discovery and documentation.

This orchestrator manages the entire data collection pipeline, from intelligence
synthesis through deep extraction to database population.
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from services.database_service import DatabaseService
from services.deduplication_service import DeduplicationService
from services.citations_analysis_service import CitationsAnalysisService
from services.enhanced_publication_service import EnhancedPublicationService
from services.ai_backfill_service import AIBackfillService
from services.advanced_ai_deduplication_service import AdvancedAIDeduplicationService
from services.vector_service import VectorService, get_vector_service
from services.serper_service import SerperService
from services.historical_trend_service import HistoricalTrendService
from services.weak_signal_detection_service import WeakSignalDetectionService
from services.coauthorship_extraction_service import CoauthorshipExtractionService
from services.entity_relationship_service import EntityRelationshipService

from services.etl_deduplication import (
    check_and_handle_innovation_duplicates,
    check_and_handle_publication_duplicates,
)

from .enhanced_crawl4ai import (
    ContentType,
    InnovationExtractionResult,
    IntelligentCrawl4AIOrchestrator,
)
from .perplexity_african_ai import IntelligenceType, PerplexityAfricanAIModule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollectorType(Enum):
    INTELLIGENCE_SYNTHESIS = "intelligence_synthesis"
    ACADEMIC_DISCOVERY = "academic_discovery" 
    INNOVATION_DISCOVERY = "innovation_discovery"
    NEWS_MONITORING = "news_monitoring"
    COMMUNITY_SIGNALS = "community_signals"
    CITATIONS_ANALYSIS = "citations_analysis"
    ENHANCED_PUBLICATION_PROCESSING = "enhanced_publication_processing"
    AI_BACKFILL = "ai_backfill"
    ADVANCED_DEDUPLICATION = "advanced_deduplication"
    VECTOR_DATABASE_UPDATE = "vector_database_update"
    SERPER_DISCOVERY = "serper_discovery"
    COAUTHORSHIP_EXTRACTION = "coauthorship_extraction"
    ENTITY_RELATIONSHIP_MINING = "entity_relationship_mining"
    HISTORICAL_TRENDS = "historical_trends"
    WEAK_SIGNAL_DETECTION = "weak_signal_detection"


class PriorityLevel(Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BATCH = "batch"


@dataclass
class CollectionTarget:
    """Represents a target for data collection"""
    id: str
    url: str
    content_type: ContentType
    priority: PriorityLevel
    source_collector: CollectorType
    metadata: Dict[str, Any]
    discovered_at: datetime
    processed_at: Optional[datetime] = None
    extraction_result: Optional[InnovationExtractionResult] = None


@dataclass
class CollectionCycleResult:
    """Results from a complete collection cycle"""
    cycle_id: str
    start_time: datetime
    end_time: datetime
    targets_discovered: int
    targets_processed: int
    innovations_extracted: int
    database_records_created: int
    citations_analyzed: int
    publications_enhanced: int
    records_backfilled: int
    advanced_duplicates_resolved: int
    vectors_updated: int
    serper_discoveries: int
    coauthorships_extracted: int
    entity_relationships_mined: int
    trends_analyzed: int
    signals_detected: int
    errors_encountered: List[str]
    recommendations: List[str]


class DataCollectionOrchestrator:
    """Master orchestrator for all TAIFA-FIALA data collection activities"""
    
    def __init__(self, perplexity_api_key: str, openai_api_key: str):
        self.perplexity_api_key = perplexity_api_key
        self.openai_api_key = openai_api_key
        
        # Initialize core modules
        self.intelligence_module = None
        self.extraction_orchestrator = None
        
        # Initialize database and deduplication services
        self.db_service = DatabaseService()
        self.dedup_service = DeduplicationService()
        self.advanced_dedup_service = AdvancedAIDeduplicationService()
        
        # Initialize Phase 1 services (Citations Expansion Strategy)
        self.citations_service = CitationsAnalysisService()
        self.enhanced_publication_service = EnhancedPublicationService()
        
        # Initialize AI and search services
        self.ai_backfill_service = AIBackfillService()
        self.serper_service = SerperService()
        self.vector_service = None  # Will be initialized in __aenter__
        
        # Initialize entity relationship mining services  
        self.coauthorship_service = CoauthorshipExtractionService()
        self.entity_relationship_service = EntityRelationshipService()
        
        # Initialize longitudinal intelligence services
        self.historical_trends_service = HistoricalTrendService()
        self.weak_signals_service = WeakSignalDetectionService()
        
        # Collection state
        self.active_targets: List[CollectionTarget] = []
        self.collection_history: List[CollectionCycleResult] = []
        
        # Content type mapping
        self.content_type_mapping = {
            "github.com": ContentType.GITHUB_REPOSITORY,
            "arxiv.org": ContentType.RESEARCH_PAPER,
            "scholar.google": ContentType.ACADEMIC_PROFILE,
            "crunchbase.com": ContentType.STARTUP_PROFILE,
            "techpoint.africa": ContentType.NEWS_ARTICLE,
            "techcabal.com": ContentType.NEWS_ARTICLE
        }
    
    async def __aenter__(self):
        """Initialize async components"""
        self.intelligence_module = PerplexityAfricanAIModule(self.perplexity_api_key)
        self.extraction_orchestrator = IntelligentCrawl4AIOrchestrator(self.openai_api_key)
        
        # Initialize vector service
        self.vector_service = await get_vector_service()
        
        await self.intelligence_module.__aenter__()
        await self.extraction_orchestrator.__aenter__()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup async components"""
        if self.intelligence_module:
            await self.intelligence_module.__aexit__(exc_type, exc_val, exc_tb)
        if self.extraction_orchestrator:
            await self.extraction_orchestrator.__aexit__(exc_type, exc_val, exc_tb)
    
    async def run_collection_cycle(self) -> CollectionCycleResult:
        """Execute a complete data collection cycle"""
        
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        logger.info(f"Starting collection cycle {cycle_id}")
        
        try:
            # Phase 1: Intelligence Synthesis
            intelligence_targets = await self._run_intelligence_synthesis()
            self.active_targets.extend(intelligence_targets)
            
            # Phase 2: Prioritize and Process
            priority_targets = self._prioritize_targets(self.active_targets[:10])  # Limit for demo
            
            # Phase 3: Deep Extraction
            extraction_results = await self._process_extraction_queue(priority_targets)
            
            # Phase 4: Validate and Store
            validated_innovations = await self._validate_innovations(extraction_results)
            
            # Phase 5: Store in Database
            stored_records = await self._store_innovations_in_database(validated_innovations)
            logger.info(f"Stored {len(stored_records)} innovations in database")
            
            # Phase 6: Citations Analysis 
            citations_analyzed = await self._analyze_citations()
            
            # Phase 7: Enhanced Publication Processing
            publications_enhanced = await self._enhance_publications()
            
            # Phase 8: Advanced Deduplication
            advanced_duplicates_resolved = await self._resolve_advanced_duplicates()
            
            # Phase 9: AI Backfill
            records_backfilled = await self._run_ai_backfill()
            
            # Phase 10: Vector Database Update
            vectors_updated = await self._update_vector_database()
            
            # Phase 11: Serper Discovery (for next cycle)
            serper_discoveries = await self._discover_new_targets_via_serper()
            
            # Phase 12: Co-authorship Extraction
            coauthorships_extracted = await self._extract_coauthorships()
            
            # Phase 13: Entity Relationship Mining
            entity_relationships_mined = await self._mine_entity_relationships()
            
            # Phase 14: Historical Trend Analysis
            trends_analyzed = await self._analyze_historical_trends()
            
            # Phase 15: Weak Signal Detection
            signals_detected = await self._detect_weak_signals()
            
            end_time = datetime.now()
            
            cycle_result = CollectionCycleResult(
                cycle_id=cycle_id,
                start_time=start_time,
                end_time=end_time,
                targets_discovered=len(intelligence_targets),
                targets_processed=len(extraction_results),
                innovations_extracted=len([r for r in extraction_results if r.success]),
                database_records_created=len(validated_innovations),
                citations_analyzed=citations_analyzed,
                publications_enhanced=publications_enhanced,
                records_backfilled=records_backfilled,
                advanced_duplicates_resolved=advanced_duplicates_resolved,
                vectors_updated=vectors_updated,
                serper_discoveries=serper_discoveries,
                coauthorships_extracted=coauthorships_extracted,
                entity_relationships_mined=entity_relationships_mined,
                trends_analyzed=trends_analyzed,
                signals_detected=signals_detected,
                errors_encountered=[],
                recommendations=self._generate_recommendations(extraction_results)
            )
            
            self.collection_history.append(cycle_result)
            
            logger.info(f"Collection cycle {cycle_id} completed successfully")
            return cycle_result
            
        except Exception as e:
            logger.error(f"Collection cycle {cycle_id} failed: {e}")
            return CollectionCycleResult(
                cycle_id=cycle_id,
                start_time=start_time,
                end_time=datetime.now(),
                targets_discovered=0,
                targets_processed=0,
                innovations_extracted=0,
                database_records_created=0,
                citations_analyzed=0,
                publications_enhanced=0,
                records_backfilled=0,
                advanced_duplicates_resolved=0,
                vectors_updated=0,
                serper_discoveries=0,
                coauthorships_extracted=0,
                entity_relationships_mined=0,
                trends_analyzed=0,
                signals_detected=0,
                errors_encountered=[str(e)],
                recommendations=[]
            )
    
    async def _run_intelligence_synthesis(self) -> List[CollectionTarget]:
        """Run Perplexity intelligence synthesis"""
        
        logger.info("Running intelligence synthesis")
        
        # Generate intelligence reports
        reports = await self.intelligence_module.synthesize_intelligence(
            intelligence_types=[IntelligenceType.INNOVATION_DISCOVERY],
            time_period='last_7_days'
        )
        
        targets = []
        for report in reports:
            for innovation in report.innovations_mentioned:
                if 'company_name' in innovation:
                    target = await self._create_target_from_innovation(innovation)
                    if target:
                        targets.append(target)
        
        logger.info(f"Intelligence synthesis discovered {len(targets)} targets")
        return targets
    
    async def _create_target_from_innovation(self, innovation: Dict[str, Any]) -> Optional[CollectionTarget]:
        """Create collection target from intelligence mention"""
        
        company_name = innovation.get('company_name', '')
        if not company_name:
            return None
        
        # Simple URL discovery strategy
        url = await self._discover_innovation_url(company_name)
        if not url:
            return None
        
        content_type = self._determine_content_type(url)
        priority = PriorityLevel.MEDIUM
        
        return CollectionTarget(
            id=f"intel_{company_name}_{datetime.now().timestamp()}",
            url=url,
            content_type=content_type,
            priority=priority,
            source_collector=CollectorType.INTELLIGENCE_SYNTHESIS,
            metadata={
                'company_name': company_name,
                'original_mention': innovation
            },
            discovered_at=datetime.now()
        )
    
    async def _discover_innovation_url(self, company_name: str) -> Optional[str]:
        """Discover URL for innovation using search"""
        
        try:
            # Use Perplexity to find official website
            search_query = f"{company_name} official website African AI startup"
            response = await self.intelligence_module._query_perplexity(search_query)
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Extract URLs from response
            import re
            urls = re.findall(r'https?://[^\s]+', content)
            
            # Return first valid URL (simplified)
            for url in urls:
                if not any(excluded in url for excluded in ['google.com', 'facebook.com', 'twitter.com']):
                    return url.rstrip('.,)')  # Clean up punctuation
            
        except Exception as e:
            logger.warning(f"Could not search for {company_name} website: {e}")
        
        return None
    
    def _determine_content_type(self, url: str) -> ContentType:
        """Determine content type based on URL"""
        
        for pattern, content_type in self.content_type_mapping.items():
            if pattern in url:
                return content_type
        
        return ContentType.INNOVATION_PROFILE
    
    def _prioritize_targets(self, targets: List[CollectionTarget]) -> List[CollectionTarget]:
        """Prioritize targets for processing"""
        
        priority_order = {
            PriorityLevel.URGENT: 0,
            PriorityLevel.HIGH: 1,
            PriorityLevel.MEDIUM: 2,
            PriorityLevel.LOW: 3,
            PriorityLevel.BATCH: 4
        }
        
        return sorted(targets, key=lambda t: priority_order[t.priority])
    
    async def _process_extraction_queue(self, targets: List[CollectionTarget]) -> List[InnovationExtractionResult]:
        """Process extraction queue with concurrency control"""
        
        logger.info(f"Processing {len(targets)} targets")
        
        extraction_results = []
        
        for target in targets:
            try:
                logger.info(f"Extracting: {target.url}")
                
                result = await self.extraction_orchestrator.extract_innovation_data(
                    url=target.url,
                    content_type=target.content_type,
                    follow_links=False,  # Simplified for demo
                    max_depth=1
                )
                
                target.extraction_result = result
                target.processed_at = datetime.now()
                extraction_results.append(result)
                
                # Rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to extract {target.url}: {e}")
                
                # Create failed result
                failed_result = InnovationExtractionResult(
                    url=target.url,
                    content_type=target.content_type,
                    extraction_timestamp=datetime.now(),
                    success=False,
                    validation_flags=[f"Extraction failed: {str(e)}"]
                )
                extraction_results.append(failed_result)
        
        return extraction_results
    
    async def _validate_innovations(self, results: List[InnovationExtractionResult]) -> List[Dict[str, Any]]:
        """Validate extraction results"""
        
        validated = []
        
        for result in results:
            if (result.success and 
                result.data_completeness_score >= 0.3 and 
                result.confidence_score >= 0.5):
                
                innovation_record = {
                    'title': result.title,
                    'description': result.description,
                    'innovation_type': result.innovation_type,
                    'location': result.location,
                    'source_url': result.url,
                    'completeness_score': result.data_completeness_score,
                    'confidence_score': result.confidence_score,
                    'extracted_at': result.extraction_timestamp
                }
                
                validated.append(innovation_record)
                logger.info(f"Validated innovation: {result.title}")
        
        logger.info(f"Validated {len(validated)} innovations")
        return validated
    
    def _generate_recommendations(self, results: List[InnovationExtractionResult]) -> List[str]:
        """Generate recommendations for next cycle"""
        
        recommendations = []
        
        success_rate = len([r for r in results if r.success]) / len(results) if results else 0
        
        if success_rate < 0.7:
            recommendations.append("Improve URL discovery and validation")
        
        avg_completeness = sum(r.data_completeness_score for r in results if r.success) / len([r for r in results if r.success]) if any(r.success for r in results) else 0
        
        if avg_completeness < 0.5:
            recommendations.append("Enhance extraction schemas for better data capture")
        
        return recommendations
    
    async def _store_innovations_in_database(self, validated_innovations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Store validated innovations in Supabase database"""
        
        stored_records = []
        
        for innovation in validated_innovations:
            try:
                # Convert to database format
                db_innovation = {
                    'title': innovation.get('title', ''),
                    'description': innovation.get('description', ''),
                    'innovation_type': innovation.get('innovation_type', 'startup'),
                    'creation_date': None,  # Will be inferred if possible
                    'verification_status': 'pending',
                    'visibility': 'public',
                    'source_type': 'intelligence_synthesis',
                    'source_url': innovation.get('source_url'),
                    'extraction_metadata': {
                        'completeness_score': innovation.get('completeness_score'),
                        'confidence_score': innovation.get('confidence_score'),
                        'extracted_at': innovation.get('extracted_at').isoformat() if innovation.get('extracted_at') else None,
                        'location': innovation.get('location')
                    }
                }
                
                # Store in database with deduplication
                success, stored_record, action = await check_and_handle_innovation_duplicates(
                    db_innovation,
                    self.db_service,
                    self.dedup_service,
                    action='reject'  # Can be configured: reject, merge, update, link
                )
                
                if success and stored_record:
                    stored_records.append(stored_record)
                    logger.info(f"✅ Stored innovation ({action}): {innovation.get('title', 'Unknown')[:50]}...")
                elif not success:
                    logger.info(f"ℹ️ Innovation handling ({action}): {innovation.get('title', 'Unknown')[:50]}...")
                    
            except Exception as e:
                logger.error(f"❌ Error storing innovation {innovation.get('title', 'Unknown')}: {e}")
                continue
        
        logger.info(f"📊 Database storage complete: {len(stored_records)}/{len(validated_innovations)} innovations stored")
        return stored_records
    
    async def _analyze_citations(self) -> int:
        """Analyze citation networks and reference patterns"""
        
        logger.info("Analyzing citation networks")
        
        try:
            # Run citation network analysis
            citation_networks = await self.citations_service.analyze_citation_networks()
            
            # Extract references from publications  
            reference_data = await self.citations_service.extract_references_from_publications()
            
            # Calculate impact scores
            impact_scores = await self.citations_service.calculate_impact_scores()
            
            # Count total citations analyzed
            citations_count = (
                len(citation_networks.get('citation_pairs', [])) +
                len(reference_data.get('extracted_references', [])) +
                len(impact_scores.get('publication_scores', {}))
            )
            
            logger.info(f"Citations analysis completed: {citations_count} citations analyzed")
            return citations_count
            
        except Exception as e:
            logger.error(f"Error in citations analysis: {e}")
            return 0
    
    async def _enhance_publications(self) -> int:
        """Enhanced processing of publication metadata"""
        
        logger.info("Enhancing publication metadata")
        
        try:
            # Extract enhanced author affiliations
            affiliations = await self.enhanced_publication_service.extract_author_affiliations()
            
            # Detect business models and development stages
            business_data = await self.enhanced_publication_service.detect_business_models_and_stages()
            
            # Map institutional connections
            institutional_connections = await self.enhanced_publication_service.map_institutional_connections()
            
            # Count publications enhanced
            enhanced_count = (
                len(affiliations.get('author_affiliations', [])) +
                len(business_data.get('business_stage_classifications', [])) +
                len(institutional_connections.get('institutional_network', {}))
            )
            
            logger.info(f"Publication enhancement completed: {enhanced_count} publications enhanced")
            return enhanced_count
            
        except Exception as e:
            logger.error(f"Error in publication enhancement: {e}")
            return 0
    
    async def _resolve_advanced_duplicates(self) -> int:
        """Advanced AI-powered deduplication"""
        
        logger.info("Running advanced deduplication")
        
        try:
            # Detect complex relationships
            relationships = await self.advanced_dedup_service.detect_complex_relationships()
            
            # Resolve duplicate clusters
            resolved_clusters = await self.advanced_dedup_service.resolve_duplicate_clusters()
            
            # Link related entities
            linked_entities = await self.advanced_dedup_service.link_related_entities()
            
            # Count duplicates resolved
            duplicates_count = (
                len(relationships.get('related_groups', [])) +
                len(resolved_clusters.get('merged_records', [])) +
                len(linked_entities.get('entity_links', []))
            )
            
            logger.info(f"Advanced deduplication completed: {duplicates_count} relationships resolved")
            return duplicates_count
            
        except Exception as e:
            logger.error(f"Error in advanced deduplication: {e}")
            return 0
    
    async def _run_ai_backfill(self) -> int:
        """Run AI-powered backfilling of missing data"""
        
        logger.info("Running AI backfill")
        
        try:
            # Get innovations needing backfill
            backfill_jobs = await self.ai_backfill_service.create_backfill_jobs_for_recent_innovations()
            
            if not backfill_jobs:
                logger.info("No records need backfilling")
                return 0
            
            # Process backfill jobs (limit to avoid overwhelming the system)
            processed_jobs = await self.ai_backfill_service.run_scheduled_backfill(
                max_jobs=min(10, len(backfill_jobs))
            )
            
            # Apply results back to database
            await self._apply_backfill_results(processed_jobs)
            
            backfilled_count = len([job for job in processed_jobs if job.status.value == "completed"])
            
            logger.info(f"AI backfill completed: {backfilled_count} records backfilled")
            return backfilled_count
            
        except Exception as e:
            logger.error(f"Error in AI backfill: {e}")
            return 0
    
    async def _update_vector_database(self) -> int:
        """Update vector database with new innovations and publications"""
        
        logger.info("Updating vector database")
        
        try:
            if not self.vector_service:
                logger.warning("Vector service not initialized")
                return 0
            
            # Get recent innovations not yet in vector DB
            from config.database import get_supabase
            supabase = get_supabase()
            
            # Get recent innovations (last hour to avoid reprocessing)
            recent_innovations = supabase.table("innovations").select("*").gte(
                "created_at", 
                (datetime.now() - timedelta(hours=1)).isoformat()
            ).execute()
            
            vectors_added = 0
            
            if recent_innovations.data:
                for innovation in recent_innovations.data:
                    try:
                        success = await self.vector_service.add_innovation(
                            innovation_id=innovation["id"],
                            title=innovation.get("title", ""),
                            description=innovation.get("description", ""),
                            innovation_type=innovation.get("innovation_type", ""),
                            country=innovation.get("country", "")
                        )
                        
                        if success:
                            vectors_added += 1
                            
                    except Exception as vector_error:
                        logger.warning(f"Failed to add innovation {innovation['id']} to vector DB: {vector_error}")
                        continue
            
            logger.info(f"Vector database update completed: {vectors_added} vectors added")
            return vectors_added
            
        except Exception as e:
            logger.error(f"Error updating vector database: {e}")
            return 0
    
    async def _discover_new_targets_via_serper(self) -> int:
        """Use Serper to discover new innovation targets for next cycle"""
        
        logger.info("Discovering new targets via Serper")
        
        try:
            # Search for recent African AI innovations
            african_countries = ["Nigeria", "Kenya", "South Africa", "Ghana", "Egypt"]
            innovation_types = ["AI startup", "machine learning", "fintech AI", "healthtech AI"]
            
            discoveries = []
            
            for country in african_countries[:2]:  # Limit to 2 countries per cycle
                for innovation_type in innovation_types[:2]:  # Limit to 2 types per country
                    try:
                        query = f"{innovation_type} {country} 2024"
                        results = await self.serper_service.search_african_innovations(
                            query=query,
                            num_results=5
                        )
                        discoveries.extend(results)
                        
                        # Rate limiting
                        await asyncio.sleep(1)
                        
                    except Exception as search_error:
                        logger.warning(f"Serper search failed for {query}: {search_error}")
                        continue
            
            # Convert search results to collection targets for next cycle
            new_targets = []
            for result in discoveries:
                if hasattr(result, 'link') and result.link:
                    target = CollectionTarget(
                        id=f"serper_{datetime.now().timestamp()}_{len(new_targets)}",
                        url=str(result.link),
                        content_type=ContentType.INNOVATION_PROFILE,
                        priority=PriorityLevel.MEDIUM,
                        source_collector=CollectorType.SERPER_DISCOVERY,
                        metadata={
                            'title': getattr(result, 'title', ''),
                            'snippet': getattr(result, 'snippet', ''),
                            'source': 'serper_discovery'
                        },
                        discovered_at=datetime.now()
                    )
                    new_targets.append(target)
            
            # Add to active targets for next cycle
            self.active_targets.extend(new_targets)
            
            logger.info(f"Serper discovery completed: {len(new_targets)} new targets discovered")
            return len(new_targets)
            
        except Exception as e:
            logger.error(f"Error in Serper discovery: {e}")
            return 0
    
    async def _apply_backfill_results(self, processed_jobs):
        """Apply backfill results to database"""
        try:
            from config.database import get_supabase
            supabase = get_supabase()
            
            for job in processed_jobs:
                if job.status.value == "completed" and job.results:
                    try:
                        updates = {}
                        
                        # Convert job results to database updates
                        for field_name, result in job.results.items():
                            if isinstance(result, dict) and "error" not in result:
                                confidence = result.get("confidence_score", 0.0)
                                if confidence >= 0.6:  # Only apply high-confidence results
                                    value = result.get("new_value")
                                    if value and field_name in ["website_url", "github_url", "demo_url"]:
                                        updates[field_name] = value
                        
                        if updates:
                            supabase.table("innovations").update(updates).eq(
                                "id", job.innovation_id
                            ).execute()
                            
                            logger.info(f"Applied backfill updates for innovation {job.innovation_id}")
                            
                    except Exception as update_error:
                        logger.error(f"Error applying backfill for {job.innovation_id}: {update_error}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error applying backfill results: {e}")
    
    async def _extract_coauthorships(self) -> int:
        """Extract co-authorship networks from publications"""
        
        logger.info("Extracting co-authorship networks")
        
        try:
            # Extract co-authorship networks from all publications
            networks_data = await self.coauthorship_service.extract_coauthorship_networks()
            
            # Count networks, researchers, and clusters extracted
            coauthorships_count = (
                networks_data.get('collaboration_networks', {}).get('total_collaborations', 0) +
                len(networks_data.get('key_researchers', [])) +
                len(networks_data.get('research_clusters', []))
            )
            
            logger.info(f"Co-authorship extraction completed: {coauthorships_count} relationships extracted")
            return coauthorships_count
            
        except Exception as e:
            logger.error(f"Error in co-authorship extraction: {e}")
            return 0
    
    async def _mine_entity_relationships(self) -> int:
        """Mine entity relationships from innovations and publications"""
        
        logger.info("Mining entity relationships")
        
        try:
            # Analyze organization relationships
            org_relationships = await self.entity_relationship_service.analyze_organization_relationships()
            
            # Analyze geographic collaboration
            geo_collaboration = await self.entity_relationship_service.analyze_geographic_collaboration()
            
            # Analyze temporal relationships
            temporal_relationships = await self.entity_relationship_service.analyze_temporal_relationships()
            
            # Extract entities from text
            entity_extraction = await self.entity_relationship_service.extract_entities_from_text()
            
            # Count total relationships mined
            relationships_count = (
                len(org_relationships.get('university_industry_partnerships', [])) +
                len(org_relationships.get('cross_institutional_projects', [])) +
                len(geo_collaboration.get('collaboration_hubs', [])) +
                len(temporal_relationships.get('long_term_partnerships', [])) +
                entity_extraction.get('organization_entities', {}).get('total_organization_mentions', 0)
            )
            
            logger.info(f"Entity relationship mining completed: {relationships_count} relationships mined")
            return relationships_count
            
        except Exception as e:
            logger.error(f"Error in entity relationship mining: {e}")
            return 0
    
    async def _analyze_historical_trends(self) -> int:
        """Run historical trend analysis on collected data"""
        
        logger.info("Running historical trend analysis")
        
        try:
            # Analyze innovation lifecycles
            lifecycle_data = await self.historical_trends_service.analyze_innovation_lifecycle()
            
            # Analyze domain evolution
            evolution_data = await self.historical_trends_service.analyze_domain_evolution()
            
            # Identify success patterns
            success_patterns = await self.historical_trends_service.identify_success_patterns()
            
            # Count total trends analyzed
            trends_count = (
                len(lifecycle_data.get('stage_transitions', {})) +
                len(evolution_data.get('maturity_scores', {})) +
                len(success_patterns.get('breakthrough_patterns', []))
            )
            
            logger.info(f"Historical trend analysis completed: {trends_count} trends analyzed")
            return trends_count
            
        except Exception as e:
            logger.error(f"Error in historical trend analysis: {e}")
            return 0
    
    async def _detect_weak_signals(self) -> int:
        """Run weak signal detection on collected data"""
        
        logger.info("Running weak signal detection")
        
        try:
            # Detect emergence indicators
            emergence_data = await self.weak_signals_service.detect_emergence_indicators()
            
            # Detect geographic shifts
            geographic_shifts = await self.weak_signals_service.detect_geographic_shifts()
            
            # Detect technology convergence
            convergence_data = await self.weak_signals_service.detect_technology_convergence()
            
            # Detect funding anomalies
            funding_anomalies = await self.weak_signals_service.detect_funding_pattern_anomalies()
            
            # Count total signals detected
            signals_count = (
                len(emergence_data.get('new_domains', [])) +
                len(emergence_data.get('growing_niches', [])) +
                len(geographic_shifts.get('activity_migration', [])) +
                len(convergence_data.get('technology_fusion', [])) +
                len(funding_anomalies.get('unusual_funding_spikes', []))
            )
            
            logger.info(f"Weak signal detection completed: {signals_count} signals detected")
            return signals_count
            
        except Exception as e:
            logger.error(f"Error in weak signal detection: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        
        if not self.collection_history:
            return {"message": "No collection cycles completed yet"}
        
        latest = self.collection_history[-1]
        
        return {
            "latest_cycle_id": latest.cycle_id,
            "total_cycles": len(self.collection_history),
            "last_performance": {
                "targets_discovered": latest.targets_discovered,
                "targets_processed": latest.targets_processed,
                "innovations_extracted": latest.innovations_extracted,
                "citations_analyzed": latest.citations_analyzed,
                "publications_enhanced": latest.publications_enhanced,
                "records_backfilled": latest.records_backfilled,
                "advanced_duplicates_resolved": latest.advanced_duplicates_resolved,
                "vectors_updated": latest.vectors_updated,
                "serper_discoveries": latest.serper_discoveries,
                "coauthorships_extracted": latest.coauthorships_extracted,
                "entity_relationships_mined": latest.entity_relationships_mined,
                "trends_analyzed": latest.trends_analyzed,
                "signals_detected": latest.signals_detected,
                "success_rate": latest.innovations_extracted / latest.targets_processed if latest.targets_processed > 0 else 0
            },
            "active_targets": len(self.active_targets),
            "recommendations": latest.recommendations
        }


# Example usage
async def main():
    """Example usage of Data Collection Orchestrator"""
    
    # Replace with actual API keys
    perplexity_key = "your_perplexity_api_key"
    openai_key = "your_openai_api_key"
    
    async with DataCollectionOrchestrator(perplexity_key, openai_key) as orchestrator:
        
        # Run collection cycle
        result = await orchestrator.run_collection_cycle()
        
        logger.info(f"Cycle completed: {result.cycle_id}")
        logger.info(f"Discovered: {result.targets_discovered}")
        logger.info(f"Processed: {result.targets_processed}")
        logger.info(f"Extracted: {result.innovations_extracted}")
        
        # Get stats
        stats = orchestrator.get_stats()
        logger.info(f"Stats: {json.dumps(stats, indent=2, default=str)}")


if __name__ == "__main__":
    asyncio.run(main())
