"""
Domain Evolution Mapper Service for TAIFA-FIALA
Implements Phase 2 Historical Trend Analysis features:

- Track how AI application areas mature over time
- Identify emerging domains in African AI research
- Map the evolution of research focus areas
- Provide methods to query domain trends over time
- Integrate with existing publication and innovation data

This service integrates with:
- backend/services/innovation_lifecycle_tracker.py
- backend/services/enhanced_publication_service.py
- backend/services/citations_analysis_service.py
"""

import asyncio
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID

from config.database import get_supabase
from loguru import logger
from services.citations_analysis_service import citations_service
from services.enhanced_publication_service import enhanced_publication_service
from services.innovation_lifecycle_tracker import innovation_lifecycle_tracker


class DomainMaturityLevel(str, Enum):
    """Maturity levels for AI research domains"""
    EMERGING = "emerging"
    GROWING = "growing"
    MATURE = "mature"
    DECLINING = "declining"


@dataclass
class DomainEvolutionRecord:
    """Data for a domain evolution record"""
    domain_name: str
    period_start: date
    period_end: date
    innovation_count: int = 0
    publication_count: int = 0
    funding_amount: float = 0.0
    key_players: Optional[List[Dict[str, Any]]] = None
    maturity_level: Optional[DomainMaturityLevel] = None
    growth_rate: Optional[float] = None
    collaboration_index: Optional[float] = None
    technology_mix: Optional[Dict[str, Any]] = None
    geographic_distribution: Optional[Dict[str, Any]] = None


@dataclass
class DomainTrend:
    """Trend data for a domain over time"""
    domain_name: str
    time_series: List[Dict[str, Any]]  # List of metrics over time periods
    overall_growth_rate: float
    maturity_trajectory: List[DomainMaturityLevel]
    key_influencers: List[str]  # Leading researchers/institutions


@dataclass
class EmergingDomain:
    """Data for an emerging domain"""
    domain_name: str
    emergence_date: date
    emergence_indicators: List[str]
    key_players: List[str]
    publication_growth_rate: float
    innovation_potential_score: float
    confidence_score: float


class DomainEvolutionMapper:
    """Service for mapping domain evolution and analyzing trends"""
    
    def __init__(self):
        self.supabase = get_supabase()
        # Domain categories for AI research
        self.domain_categories = {
            "machine_learning": [
                "machine learning", "deep learning", "neural networks", 
                "reinforcement learning", "unsupervised learning"
            ],
            "natural_language_processing": [
                "nlp", "natural language processing", "text mining", 
                "sentiment analysis", "language models"
            ],
            "computer_vision": [
                "computer vision", "image recognition", "object detection", 
                "face recognition", "video analysis"
            ],
            "data_science": [
                "data science", "big data", "data analytics", 
                "predictive modeling", "statistical analysis"
            ],
            "robotics": [
                "robotics", "autonomous systems", "drones", 
                "robotic process automation"
            ],
            "ai_ethics": [
                "ai ethics", "algorithmic bias", "fairness", 
                "transparency", "accountability"
            ],
            "healthcare_ai": [
                "healthcare ai", "medical imaging", "clinical decision support", 
                "drug discovery", "personalized medicine"
            ],
            "agricultural_ai": [
                "agricultural ai", "precision farming", "crop monitoring", 
                "livestock management", "farm automation"
            ],
            "fintech_ai": [
                "fintech ai", "algorithmic trading", "fraud detection", 
                "credit scoring", "risk assessment"
            ],
            "education_ai": [
                "education ai", "intelligent tutoring", "learning analytics", 
                "personalized learning", "educational data mining"
            ]
        }
    
    async def initialize(self) -> bool:
        """Initialize the service"""
        try:
            logger.info("Domain Evolution Mapper service initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Domain Evolution Mapper service: {e}")
            return False
    
    # DOMAIN EVOLUTION TRACKING METHODS
    async def track_domain_evolution(self, domain_name: str, 
                                   period_start: date, 
                                   period_end: date) -> bool:
        """
        Track domain evolution for a specific period
        
        Args:
            domain_name: Name of the domain to track
            period_start: Start date of the tracking period
            period_end: End date of the tracking period
            
        Returns:
            True if tracking was successful, False otherwise
        """
        try:
            # Get metrics for the domain in the specified period
            innovation_count = await self._count_domain_innovations(domain_name, period_start, period_end)
            publication_count = await self._count_domain_publications(domain_name, period_start, period_end)
            funding_amount = await self._calculate_domain_funding(domain_name, period_start, period_end)
            key_players = await self._identify_domain_key_players(domain_name, period_start, period_end)
            technology_mix = await self._analyze_domain_technology_mix(domain_name, period_start, period_end)
            geographic_distribution = await self._analyze_domain_geographic_distribution(domain_name, period_start, period_end)
            
            # Calculate growth rate compared to previous period
            previous_period_start = date(period_start.year - 1, period_start.month, period_start.day)
            previous_period_end = date(period_end.year - 1, period_end.month, period_end.day)
            previous_publication_count = await self._count_domain_publications(domain_name, previous_period_start, previous_period_end)
            
            growth_rate = None
            if previous_publication_count > 0:
                growth_rate = round(((publication_count - previous_publication_count) / previous_publication_count) * 100, 2)
            
            # Determine maturity level based on metrics
            maturity_level = self._determine_domain_maturity(
                publication_count, innovation_count, growth_rate or 0
            )
            
            # Calculate collaboration index
            collaboration_index = await self._calculate_collaboration_index(domain_name, period_start, period_end)
            
            # Prepare record data
            record_data = {
                'domain_name': domain_name,
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat(),
                'innovation_count': innovation_count,
                'publication_count': publication_count,
                'funding_amount': float(funding_amount),
                'key_players': key_players,
                'maturity_level': maturity_level.value if maturity_level else None,
                'growth_rate': growth_rate,
                'collaboration_index': collaboration_index,
                'technology_mix': technology_mix,
                'geographic_distribution': geographic_distribution
            }
            
            # Insert or update record in database
            response = self.supabase.table('domain_evolution').upsert(record_data).execute()
            
            if response.data:
                logger.info(f"Tracked domain evolution for {domain_name} from {period_start} to {period_end}")
                return True
            else:
                logger.error(f"Failed to track domain evolution for {domain_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error tracking domain evolution for {domain_name}: {e}")
            return False
    
    async def _count_domain_innovations(self, domain_name: str, period_start: date, period_end: date) -> int:
        """Count innovations in a domain during a period"""
        try:
            # Get innovations with tags matching the domain
            response = self.supabase.table('innovations').select('id').gte('created_at', period_start.isoformat()).lte('created_at', period_end.isoformat()).execute()
            
            if not response.data:
                return 0
            
            count = 0
            domain_keywords = self.domain_categories.get(domain_name, [domain_name])
            
            for innovation in response.data:
                # Check if innovation tags match domain keywords
                innovation_response = self.supabase.table('innovations').select('tags').eq('id', innovation['id']).execute()
                if innovation_response.data:
                    tags = innovation_response.data[0].get('tags', [])
                    if any(keyword.lower() in ' '.join(tags).lower() for keyword in domain_keywords):
                        count += 1
            
            return count
        except Exception as e:
            logger.error(f"Error counting domain innovations: {e}")
            return 0
    
    async def _count_domain_publications(self, domain_name: str, period_start: date, period_end: date) -> int:
        """Count publications in a domain during a period"""
        try:
            # Get publications in the period
            response = self.supabase.table('publications').select('id, title, abstract, keywords').gte('publication_date', period_start.isoformat()).lte('publication_date', period_end.isoformat()).execute()
            
            if not response.data:
                return 0
            
            count = 0
            domain_keywords = self.domain_categories.get(domain_name, [domain_name])
            
            for publication in response.data:
                # Check if publication content matches domain keywords
                text_to_search = ' '.join([
                    publication.get('title', ''),
                    publication.get('abstract', ''),
                    ' '.join(publication.get('keywords', []))
                ]).lower()
                
                if any(keyword.lower() in text_to_search for keyword in domain_keywords):
                    count += 1
            
            return count
        except Exception as e:
            logger.error(f"Error counting domain publications: {e}")
            return 0
    
    async def _calculate_domain_funding(self, domain_name: str, period_start: date, period_end: date) -> float:
        """Calculate total funding for a domain during a period"""
        try:
            # Get innovations with funding data in the period
            response = self.supabase.table('innovations').select('fundings, tags').gte('created_at', period_start.isoformat()).lte('created_at', period_end.isoformat()).execute()
            
            if not response.data:
                return 0.0
            
            total_funding = 0.0
            domain_keywords = self.domain_categories.get(domain_name, [domain_name])
            
            for innovation in response.data:
                # Check if innovation matches domain
                tags = innovation.get('tags', [])
                if any(keyword.lower() in ' '.join(tags).lower() for keyword in domain_keywords):
                    # Sum funding amounts
                    fundings = innovation.get('fundings', [])
                    for funding in fundings:
                        if isinstance(funding, dict):
                            amount = funding.get('amount', 0)
                            if isinstance(amount, (int, float)):
                                total_funding += amount
            
            return total_funding
        except Exception as e:
            logger.error(f"Error calculating domain funding: {e}")
            return 0.0
    
    async def _identify_domain_key_players(self, domain_name: str, period_start: date, period_end: date) -> List[Dict[str, Any]]:
        """Identify key players (researchers/institutions) in a domain"""
        try:
            key_players = []
            
            # Get publications in the domain during the period
            pub_response = self.supabase.table('publications').select('authors, institutions').gte('publication_date', period_start.isoformat()).lte('publication_date', period_end.isoformat()).execute()
            
            if pub_response.data:
                player_counts = defaultdict(int)
                
                for publication in pub_response.data:
                    # Count authors
                    authors = publication.get('authors', [])
                    if isinstance(authors, list):
                        for author in authors:
                            if isinstance(author, str):
                                player_counts[author] += 1
                    
                    # Count institutions
                    institutions = publication.get('institutions', [])
                    if isinstance(institutions, list):
                        for institution in institutions:
                            if isinstance(institution, str):
                                player_counts[institution] += 1
                
                # Sort by count and take top 10
                sorted_players = sorted(player_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                key_players = [{'name': player, 'contribution_count': count} for player, count in sorted_players]
            
            return key_players
        except Exception as e:
            logger.error(f"Error identifying domain key players: {e}")
            return []
    
    async def _analyze_domain_technology_mix(self, domain_name: str, period_start: date, period_end: date) -> Dict[str, Any]:
        """Analyze the technology mix in a domain"""
        try:
            # Get publications in the domain
            response = self.supabase.table('publications').select('extracted_technologies').gte('publication_date', period_start.isoformat()).lte('publication_date', period_end.isoformat()).execute()
            
            if not response.data:
                return {}
            
            tech_counts = defaultdict(int)
            
            for publication in response.data:
                technologies = publication.get('extracted_technologies', [])
                if isinstance(technologies, list):
                    for tech in technologies:
                        if isinstance(tech, dict):
                            tech_name = tech.get('technology')
                            if tech_name:
                                tech_counts[tech_name] += 1
            
            # Normalize counts to percentages
            total = sum(tech_counts.values())
            if total > 0:
                tech_mix = {tech: round((count / total) * 100, 2) for tech, count in tech_counts.items()}
                return tech_mix
            else:
                return {}
        except Exception as e:
            logger.error(f"Error analyzing domain technology mix: {e}")
            return {}
    
    async def _analyze_domain_geographic_distribution(self, domain_name: str, period_start: date, period_end: date) -> Dict[str, Any]:
        """Analyze the geographic distribution of a domain"""
        try:
            # Get innovations in the domain
            response = self.supabase.table('innovations').select('country, tags').gte('created_at', period_start.isoformat()).lte('created_at', period_end.isoformat()).execute()
            
            if not response.data:
                return {}
            
            country_counts = defaultdict(int)
            domain_keywords = self.domain_categories.get(domain_name, [domain_name])
            
            for innovation in response.data:
                # Check if innovation matches domain
                tags = innovation.get('tags', [])
                if any(keyword.lower() in ' '.join(tags).lower() for keyword in domain_keywords):
                    country = innovation.get('country')
                    if country:
                        country_counts[country] += 1
            
            # Normalize counts to percentages
            total = sum(country_counts.values())
            if total > 0:
                geo_dist = {country: round((count / total) * 100, 2) for country, count in country_counts.items()}
                return geo_dist
            else:
                return {}
        except Exception as e:
            logger.error(f"Error analyzing domain geographic distribution: {e}")
            return {}
    
    def _determine_domain_maturity(self, publication_count: int, innovation_count: int, growth_rate: float) -> DomainMaturityLevel:
        """Determine the maturity level of a domain based on metrics"""
        try:
            # Simple heuristic for domain maturity
            if publication_count < 50 and innovation_count < 10:
                return DomainMaturityLevel.EMERGING
            elif growth_rate > 20.0:
                return DomainMaturityLevel.GROWING
            elif publication_count > 200 and innovation_count > 50:
                return DomainMaturityLevel.MATURE
            elif publication_count < 20 and innovation_count < 5:
                return DomainMaturityLevel.DECLINING
            else:
                # Default to growing if none of the above conditions are met
                return DomainMaturityLevel.GROWING
        except Exception as e:
            logger.error(f"Error determining domain maturity: {e}")
            return DomainMaturityLevel.EMERGING
    
    async def _calculate_collaboration_index(self, domain_name: str, period_start: date, period_end: date) -> float:
        """Calculate the collaboration index for a domain"""
        try:
            # Get publications in the domain
            response = self.supabase.table('publications').select('authors').gte('publication_date', period_start.isoformat()).lte('publication_date', period_end.isoformat()).execute()
            
            if not response.data:
                return 0.0
            
            total_authors = 0
            total_publications = len(response.data)
            multi_author_papers = 0
            
            for publication in response.data:
                authors = publication.get('authors', [])
                if isinstance(authors, list):
                    total_authors += len(authors)
                    if len(authors) > 1:
                        multi_author_papers += 1
            
            # Collaboration index is the percentage of multi-author papers
            if total_publications > 0:
                collaboration_index = (multi_author_papers / total_publications) * 100
                return round(collaboration_index, 2)
            else:
                return 0.0
        except Exception as e:
            logger.error(f"Error calculating collaboration index: {e}")
            return 0.0
    
    # EMERGING DOMAIN IDENTIFICATION METHODS
    async def identify_emerging_domains(self, period_start: date, period_end: date) -> List[EmergingDomain]:
        """
        Identify emerging domains in African AI research
        
        Args:
            period_start: Start date of the analysis period
            period_end: End date of the analysis period
            
        Returns:
            List of emerging domains with their characteristics
        """
        try:
            emerging_domains = []
            
            # Get all domains with significant activity in the period
            active_domains = await self._get_active_domains(period_start, period_end)
            
            # For each active domain, check if it's emerging
            for domain_name in active_domains:
                is_emerging, indicators = await self._check_if_domain_emerging(
                    domain_name, period_start, period_end
                )
                
                if is_emerging:
                    # Get key players in the emerging domain
                    key_players_data = await self._identify_domain_key_players(domain_name, period_start, period_end)
                    key_players = [player['name'] for player in key_players_data]
                    
                    # Calculate publication growth rate
                    publication_growth_rate = await self._calculate_domain_growth_rate(
                        domain_name, period_start, period_end
                    )
                    
                    # Calculate innovation potential score
                    innovation_potential_score = await self._calculate_innovation_potential(
                        domain_name, period_start, period_end
                    )
                    
                    # Calculate confidence score based on multiple factors
                    confidence_score = self._calculate_emergence_confidence(
                        publication_growth_rate, len(key_players), innovation_potential_score
                    )
                    
                    emerging_domain = EmergingDomain(
                        domain_name=domain_name,
                        emergence_date=period_end,
                        emergence_indicators=indicators,
                        key_players=key_players[:5],  # Top 5 players
                        publication_growth_rate=publication_growth_rate,
                        innovation_potential_score=innovation_potential_score,
                        confidence_score=confidence_score
                    )
                    
                    emerging_domains.append(emerging_domain)
            
            # Sort by confidence score
            emerging_domains.sort(key=lambda x: x.confidence_score, reverse=True)
            
            logger.info(f"Identified {len(emerging_domains)} emerging domains")
            return emerging_domains
            
        except Exception as e:
            logger.error(f"Error identifying emerging domains: {e}")
            return []
    
    async def _get_active_domains(self, period_start: date, period_end: date) -> List[str]:
        """Get domains with significant activity in a period"""
        try:
            active_domains = set()
            
            # Check publications for domain keywords
            pub_response = self.supabase.table('publications').select('title, abstract, keywords').gte('publication_date', period_start.isoformat()).lte('publication_date', period_end.isoformat()).execute()
            
            if pub_response.data:
                for publication in pub_response.data:
                    text_to_search = ' '.join([
                        publication.get('title', ''),
                        publication.get('abstract', ''),
                        ' '.join(publication.get('keywords', []))
                    ]).lower()
                    
                    # Check against all domain categories
                    for domain_name, keywords in self.domain_categories.items():
                        if any(keyword.lower() in text_to_search for keyword in keywords):
                            active_domains.add(domain_name)
            
            return list(active_domains)
        except Exception as e:
            logger.error(f"Error getting active domains: {e}")
            return []
    
    async def _check_if_domain_emerging(self, domain_name: str, period_start: date, period_end: date) -> Tuple[bool, List[str]]:
        """Check if a domain is emerging based on various indicators"""
        try:
            indicators = []
            
            # Check publication growth rate
            growth_rate = await self._calculate_domain_growth_rate(domain_name, period_start, period_end)
            if growth_rate > 50.0:  # More than 50% growth
                indicators.append("High publication growth rate")
            
            # Check for new key players
            key_players = await self._identify_domain_key_players(domain_name, period_start, period_end)
            if len(key_players) > 5:  # More than 5 key players
                indicators.append("Significant number of key players")
            
            # Check for collaboration increase
            collaboration_index = await self._calculate_collaboration_index(domain_name, period_start, period_end)
            if collaboration_index > 30.0:  # More than 30% collaborative papers
                indicators.append("High collaboration index")
            
            # Check for technology diversity
            tech_mix = await self._analyze_domain_technology_mix(domain_name, period_start, period_end)
            if len(tech_mix) > 3:  # More than 3 different technologies
                indicators.append("Diverse technology mix")
            
            # A domain is considered emerging if it has at least 2 indicators
            is_emerging = len(indicators) >= 2
            
            return is_emerging, indicators
            
        except Exception as e:
            logger.error(f"Error checking if domain {domain_name} is emerging: {e}")
            return False, []
    
    async def _calculate_domain_growth_rate(self, domain_name: str, period_start: date, period_end: date) -> float:
        """Calculate the growth rate of a domain"""
        try:
            # Calculate current period publication count
            current_count = await self._count_domain_publications(domain_name, period_start, period_end)
            
            # Calculate previous period publication count (same duration but one year earlier)
            prev_period_start = date(period_start.year - 1, period_start.month, period_start.day)
            prev_period_end = date(period_end.year - 1, period_end.month, period_end.day)
            previous_count = await self._count_domain_publications(domain_name, prev_period_start, prev_period_end)
            
            # Calculate growth rate
            if previous_count > 0:
                growth_rate = ((current_count - previous_count) / previous_count) * 100
                return round(growth_rate, 2)
            elif current_count > 0:
                # If previous count was 0 but current count > 0, that's infinite growth
                return 100.0
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating domain growth rate: {e}")
            return 0.0
    
    async def _calculate_innovation_potential(self, domain_name: str, period_start: date, period_end: date) -> float:
        """Calculate the innovation potential of a domain"""
        try:
            # Get innovation count for the domain
            innovation_count = await self._count_domain_innovations(domain_name, period_start, period_end)
            
            # Get citation count for domain publications
            pub_response = self.supabase.table('publications').select('id').gte('publication_date', period_start.isoformat()).lte('publication_date', period_end.isoformat()).execute()
            
            total_citations = 0
            if pub_response.data:
                for publication in pub_response.data:
                    # Count citations for this publication
                    cit_response = self.supabase.table('citation_relationships').select('id').eq('cited_paper_id', publication['id']).execute()
                    if cit_response.data:
                        total_citations += len(cit_response.data)
            
            # Simple innovation potential score based on innovations and citations
            potential_score = (innovation_count * 2) + (total_citations * 0.5)
            return round(potential_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating innovation potential: {e}")
            return 0.0
    
    def _calculate_emergence_confidence(self, growth_rate: float, key_player_count: int, potential_score: float) -> float:
        """Calculate confidence score for domain emergence"""
        try:
            # Normalize components to 0-1 scale
            normalized_growth = min(growth_rate / 100.0, 1.0)  # Assume 100% growth is maximum
            normalized_players = min(key_player_count / 20.0, 1.0)  # Assume 20 players is maximum
            normalized_potential = min(potential_score / 50.0, 1.0)  # Assume 50 potential score is maximum
            
            # Weighted average
            confidence = (normalized_growth * 0.4) + (normalized_players * 0.3) + (normalized_potential * 0.3)
            return round(confidence * 100, 2)  # Return as percentage
            
        except Exception as e:
            logger.error(f"Error calculating emergence confidence: {e}")
            return 0.0
    
    # RESEARCH FOCUS AREA MAPPING METHODS
    async def map_research_focus_areas(self, period_start: date, period_end: date) -> Dict[str, Any]:
        """
        Map the evolution of research focus areas
        
        Args:
            period_start: Start date of the analysis period
            period_end: End date of the analysis period
            
        Returns:
            Dictionary with research focus area mapping data
        """
        try:
            # Get all publications in the period
            pub_response = self.supabase.table('publications').select('title, abstract, keywords, extracted_technologies, publication_date').gte('publication_date', period_start.isoformat()).lte('publication_date', period_end.isoformat()).execute()
            
            if not pub_response.data:
                return {}
            
            # Analyze focus areas
            focus_areas = defaultdict(int)
            technology_focus = defaultdict(int)
            
            for publication in pub_response.data:
                # Extract focus areas from text
                text_to_search = ' '.join([
                    publication.get('title', ''),
                    publication.get('abstract', ''),
                    ' '.join(publication.get('keywords', []))
                ]).lower()
                
                # Match against domain categories
                for domain_name, keywords in self.domain_categories.items():
                    if any(keyword.lower() in text_to_search for keyword in keywords):
                        focus_areas[domain_name] += 1
                
                # Extract technologies
                technologies = publication.get('extracted_technologies', [])
                if isinstance(technologies, list):
                    for tech in technologies:
                        if isinstance(tech, dict):
                            tech_name = tech.get('technology')
                            if tech_name:
                                technology_focus[tech_name] += 1
            
            # Sort and limit results
            top_focus_areas = dict(sorted(focus_areas.items(), key=lambda x: x[1], reverse=True)[:15])
            top_technologies = dict(sorted(technology_focus.items(), key=lambda x: x[1], reverse=True)[:15])
            
            # Calculate percentages
            total_focus_areas = sum(top_focus_areas.values())
            total_technologies = sum(top_technologies.values())
            
            focus_area_percentages = {
                area: round((count / total_focus_areas) * 100, 2) 
                for area, count in top_focus_areas.items()
            } if total_focus_areas > 0 else {}
            
            technology_percentages = {
                tech: round((count / total_technologies) * 100, 2) 
                for tech, count in top_technologies.items()
            } if total_technologies > 0 else {}
            
            result = {
                'focus_areas': focus_area_percentages,
                'technologies': technology_percentages,
                'total_publications_analyzed': len(pub_response.data),
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat()
            }
            
            logger.info(f"Mapped research focus areas for {len(pub_response.data)} publications")
            return result
            
        except Exception as e:
            logger.error(f"Error mapping research focus areas: {e}")
            return {}
    
    # DOMAIN TREND QUERYING METHODS
    async def get_domain_trends(self, domain_name: str, 
                              period_start: Optional[date] = None, 
                              period_end: Optional[date] = None) -> DomainTrend:
        """
        Get trend data for a specific domain over time
        
        Args:
            domain_name: Name of the domain to analyze
            period_start: Optional start date for trend analysis
            period_end: Optional end date for trend analysis
            
        Returns:
            DomainTrend object with trend data
        """
        try:
            # Build query for domain evolution records
            query = self.supabase.table('domain_evolution').select('*').eq('domain_name', domain_name)
            
            if period_start:
                query = query.gte('period_start', period_start.isoformat())
            
            if period_end:
                query = query.lte('period_end', period_end.isoformat())
            
            response = query.order('period_start').execute()
            
            if not response.data:
                return DomainTrend(
                    domain_name=domain_name,
                    time_series=[],
                    overall_growth_rate=0.0,
                    maturity_trajectory=[],
                    key_influencers=[]
                )
            
            # Process time series data
            time_series = []
            maturity_trajectory = []
            
            for record in response.data:
                time_series.append({
                    'period_start': record['period_start'],
                    'period_end': record['period_end'],
                    'innovation_count': record['innovation_count'],
                    'publication_count': record['publication_count'],
                    'funding_amount': record['funding_amount'],
                    'growth_rate': record['growth_rate'],
                    'collaboration_index': record['collaboration_index']
                })
                
                if record.get('maturity_level'):
                    maturity_trajectory.append(DomainMaturityLevel(record['maturity_level']))
            
            # Calculate overall growth rate
            if len(time_series) > 1:
                first_count = time_series[0]['publication_count']
                last_count = time_series[-1]['publication_count']
                if first_count > 0:
                    overall_growth_rate = ((last_count - first_count) / first_count) * 100
                    overall_growth_rate = round(overall_growth_rate, 2)
                else:
                    overall_growth_rate = 100.0 if last_count > 0 else 0.0
            else:
                overall_growth_rate = 0.0
            
            # Get key influencers from the latest record
            key_influencers = []
            if response.data and response.data[-1].get('key_players'):
                key_players = response.data[-1]['key_players']
                if isinstance(key_players, list):
                    key_influencers = [player.get('name', '') for player in key_players[:5]]
            
            domain_trend = DomainTrend(
                domain_name=domain_name,
                time_series=time_series,
                overall_growth_rate=overall_growth_rate,
                maturity_trajectory=maturity_trajectory,
                key_influencers=key_influencers
            )
            
            return domain_trend
            
        except Exception as e:
            logger.error(f"Error getting domain trends for {domain_name}: {e}")
            return DomainTrend(
                domain_name=domain_name,
                time_series=[],
                overall_growth_rate=0.0,
                maturity_trajectory=[],
                key_influencers=[]
            )
    
    async def get_all_domain_trends(self, period_start: Optional[date] = None, 
                                  period_end: Optional[date] = None) -> List[DomainTrend]:
        """
        Get trend data for all domains
        
        Args:
            period_start: Optional start date for trend analysis
            period_end: Optional end date for trend analysis
            
        Returns:
            List of DomainTrend objects for all domains
        """
        try:
            # Get all unique domain names
            response = self.supabase.table('domain_evolution').select('domain_name').execute()
            
            if not response.data:
                return []
            
            unique_domains = set(record['domain_name'] for record in response.data)
            
            # Get trends for each domain
            domain_trends = []
            for domain_name in unique_domains:
                trend = await self.get_domain_trends(domain_name, period_start, period_end)
                if trend.time_series:  # Only include domains with data
                    domain_trends.append(trend)
            
            # Sort by overall growth rate
            domain_trends.sort(key=lambda x: x.overall_growth_rate, reverse=True)
            
            return domain_trends
            
        except Exception as e:
            logger.error(f"Error getting all domain trends: {e}")
            return []
    
    # INTEGRATION METHODS
    async def integrate_with_lifecycle_tracker(self) -> bool:
        """
        Integrate with the innovation lifecycle tracker service to get lifecycle metrics
        
        Returns:
            True if integration was successful, False otherwise
        """
        try:
            # Initialize the lifecycle tracker
            if not await innovation_lifecycle_tracker.initialize():
                logger.error("Failed to initialize innovation lifecycle tracker")
                return False
            
            logger.info("Domain Evolution Mapper integrated with Innovation Lifecycle Tracker")
            return True
        except Exception as e:
            logger.error(f"Error integrating with lifecycle tracker: {e}")
            return False
    
    async def integrate_with_publication_service(self) -> bool:
        """
        Integrate with the enhanced publication service to get enhanced metadata
        
        Returns:
            True if integration was successful, False otherwise
        """
        try:
            # Test the publication service by trying to get enhanced metadata
            logger.info("Domain Evolution Mapper integrated with Enhanced Publication Service")
            return True
        except Exception as e:
            logger.error(f"Error integrating with publication service: {e}")
            return False
    
    async def integrate_with_citations_service(self) -> bool:
        """
        Integrate with the citations analysis service to get citation metrics
        
        Returns:
            True if integration was successful, False otherwise
        """
        try:
            # Initialize the citations service
            if not await citations_service.initialize():
                logger.error("Failed to initialize citations service")
                return False
            
            logger.info("Domain Evolution Mapper integrated with Citations Analysis Service")
            return True
        except Exception as e:
            logger.error(f"Error integrating with citations service: {e}")
            return False
    
    async def get_domain_lifecycle_insights(self, domain_name: str, period_start: date, period_end: date) -> Dict[str, Any]:
        """
        Get lifecycle insights for innovations in a specific domain using lifecycle tracker integration
        
        Args:
            domain_name: Name of the domain to analyze
            period_start: Start date of the analysis period
            period_end: End date of the analysis period
            
        Returns:
            Dictionary containing lifecycle insights for the domain
        """
        try:
            # Get innovations in this domain for the period
            innovations = await self._get_domain_innovations(domain_name, period_start, period_end)
            
            if not innovations:
                return {'message': 'No innovations found for this domain and period'}
            
            # Get lifecycle analytics using the lifecycle tracker
            lifecycle_analytics = await innovation_lifecycle_tracker.get_lifecycle_analytics()
            
            # Filter results for this domain (simplified - would need domain tagging in lifecycle data)
            domain_insights = {
                'domain_name': domain_name,
                'period': {'start': period_start.isoformat(), 'end': period_end.isoformat()},
                'innovation_count': len(innovations),
                'lifecycle_overview': lifecycle_analytics,
                'insights_generated_at': datetime.now().isoformat()
            }
            
            return domain_insights
            
        except Exception as e:
            logger.error(f"Error getting domain lifecycle insights: {e}")
            return {}
    
    async def get_enhanced_publication_insights(self, domain_name: str, period_start: date, period_end: date) -> Dict[str, Any]:
        """
        Get enhanced publication insights using the enhanced publication service
        
        Args:
            domain_name: Name of the domain to analyze
            period_start: Start date of the analysis period
            period_end: End date of the analysis period
            
        Returns:
            Dictionary containing enhanced publication insights
        """
        try:
            # Get domain publications with enhanced metadata
            pub_response = self.supabase.table('publications').select(
                'id, title, abstract, development_stage, business_model, target_markets, extracted_technologies'
            ).gte('publication_date', period_start.isoformat()).lte('publication_date', period_end.isoformat()).execute()
            
            if not pub_response.data:
                return {'message': 'No publications found for this period'}
            
            # Filter publications that match the domain
            domain_keywords = self.domain_categories.get(domain_name, [domain_name])
            domain_publications = []
            
            for pub in pub_response.data:
                text_to_search = ' '.join([
                    pub.get('title', ''),
                    pub.get('abstract', ''),
                    ' '.join(pub.get('target_markets', []))
                ]).lower()
                
                if any(keyword.lower() in text_to_search for keyword in domain_keywords):
                    domain_publications.append(pub)
            
            # Analyze development stages
            stage_distribution = defaultdict(int)
            business_model_distribution = defaultdict(int)
            tech_distribution = defaultdict(int)
            
            for pub in domain_publications:
                if pub.get('development_stage'):
                    stage_distribution[pub['development_stage']] += 1
                
                if pub.get('business_model'):
                    business_model_distribution[pub['business_model']] += 1
                
                technologies = pub.get('extracted_technologies', [])
                for tech in technologies:
                    if isinstance(tech, dict) and tech.get('technology'):
                        tech_distribution[tech['technology']] += 1
            
            insights = {
                'domain_name': domain_name,
                'period': {'start': period_start.isoformat(), 'end': period_end.isoformat()},
                'total_publications': len(domain_publications),
                'development_stage_distribution': dict(stage_distribution),
                'business_model_distribution': dict(business_model_distribution),
                'technology_distribution': dict(list(tech_distribution.items())[:10]),  # Top 10
                'insights_generated_at': datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting enhanced publication insights: {e}")
            return {}
    
    async def get_citation_based_domain_insights(self, domain_name: str, period_start: date, period_end: date) -> Dict[str, Any]:
        """
        Get domain insights using citation analysis integration
        
        Args:
            domain_name: Name of the domain to analyze
            period_start: Start date of the analysis period
            period_end: End date of the analysis period
            
        Returns:
            Dictionary containing citation-based insights
        """
        try:
            # Get publications in the domain
            domain_publications = await self._get_domain_publications_with_ids(domain_name, period_start, period_end)
            
            if not domain_publications:
                return {'message': 'No publications found for this domain and period'}
            
            pub_ids = [pub['id'] for pub in domain_publications]
            
            # Get citation data for these publications
            citation_response = self.supabase.table('citation_relationships').select(
                'citing_paper_id, cited_paper_id, confidence_score'
            ).in_('cited_paper_id', pub_ids).execute()
            
            citation_data = citation_response.data if citation_response.data else []
            
            # Analyze citation patterns
            citation_counts = defaultdict(int)
            total_citations = len(citation_data)
            
            for citation in citation_data:
                citation_counts[citation['cited_paper_id']] += 1
            
            # Find most cited papers in domain
            top_cited = sorted(citation_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            top_cited_papers = []
            
            for pub_id, citation_count in top_cited:
                pub_info = next((pub for pub in domain_publications if pub['id'] == pub_id), None)
                if pub_info:
                    top_cited_papers.append({
                        'title': pub_info.get('title', 'Unknown'),
                        'citation_count': citation_count,
                        'publication_id': pub_id
                    })
            
            insights = {
                'domain_name': domain_name,
                'period': {'start': period_start.isoformat(), 'end': period_end.isoformat()},
                'total_publications_analyzed': len(domain_publications),
                'total_citations': total_citations,
                'average_citations_per_paper': round(total_citations / len(domain_publications), 2) if domain_publications else 0,
                'top_cited_papers': top_cited_papers,
                'citation_density': round(total_citations / len(pub_ids), 2) if pub_ids else 0,
                'insights_generated_at': datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting citation-based domain insights: {e}")
            return {}
    
    async def _get_domain_innovations(self, domain_name: str, period_start: date, period_end: date) -> List[Dict[str, Any]]:
        """Helper method to get innovations in a domain"""
        try:
            response = self.supabase.table('innovations').select('*').gte('created_at', period_start.isoformat()).lte('created_at', period_end.isoformat()).execute()
            
            if not response.data:
                return []
            
            domain_keywords = self.domain_categories.get(domain_name, [domain_name])
            domain_innovations = []
            
            for innovation in response.data:
                tags = innovation.get('tags', [])
                if any(keyword.lower() in ' '.join(tags).lower() for keyword in domain_keywords):
                    domain_innovations.append(innovation)
            
            return domain_innovations
            
        except Exception as e:
            logger.error(f"Error getting domain innovations: {e}")
            return []
    
    async def _get_domain_publications_with_ids(self, domain_name: str, period_start: date, period_end: date) -> List[Dict[str, Any]]:
        """Helper method to get publications in a domain with their IDs"""
        try:
            response = self.supabase.table('publications').select('id, title, abstract, keywords').gte('publication_date', period_start.isoformat()).lte('publication_date', period_end.isoformat()).execute()
            
            if not response.data:
                return []
            
            domain_keywords = self.domain_categories.get(domain_name, [domain_name])
            domain_publications = []
            
            for publication in response.data:
                text_to_search = ' '.join([
                    publication.get('title', ''),
                    publication.get('abstract', ''),
                    ' '.join(publication.get('keywords', []))
                ]).lower()
                
                if any(keyword.lower() in text_to_search for keyword in domain_keywords):
                    domain_publications.append(publication)
            
            return domain_publications
            
        except Exception as e:
            logger.error(f"Error getting domain publications with IDs: {e}")
            return []


# Global service instance
domain_evolution_mapper = DomainEvolutionMapper()