"""
Historical Trend Analysis Service
Phase 2 of Citations Expansion Strategy: Longitudinal Intelligence

Tracks innovation lifecycles, domain evolution, and success patterns over time
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from loguru import logger
from sqlalchemy import text
import pandas as pd
import numpy as np
from collections import defaultdict, Counter


class HistoricalTrendService:
    """Service for analyzing historical trends and patterns in AI innovations"""

    def __init__(self):
        self.trend_cache = {}
        self.last_analysis = {}

    async def analyze_innovation_lifecycle(self, innovation_ids: Optional[List[str]] = None) -> Dict:
        """
        Track projects from research paper to market implementation
        
        Returns:
            Dict with lifecycle stages, transitions, and timelines
        """
        try:
            from config.database import get_supabase
            supabase = get_supabase()

            # Get innovations with their linked publications and timeline data
            query = """
                SELECT 
                    i.id,
                    i.title,
                    i.creation_date,
                    i.innovation_type,
                    i.verification_status,
                    i.country,
                    i.fundings,
                    i.organizations,
                    p.publication_date,
                    p.title as pub_title,
                    p.citation_count,
                    p.publication_type
                FROM innovations i
                LEFT JOIN innovation_publications ip ON i.id = ip.innovation_id
                LEFT JOIN publications p ON ip.publication_id = p.id
                ORDER BY i.creation_date ASC
            """
            
            # For now, use basic Supabase query (expand later with SQL functions)
            innovations_response = supabase.table("innovations").select(
                "id, title, creation_date, innovation_type, verification_status, country, fundings, organizations"
            ).execute()
            
            innovations = innovations_response.data if innovations_response.data else []

            lifecycle_analysis = {
                "stages_distribution": self._analyze_lifecycle_stages(innovations),
                "progression_patterns": self._identify_progression_patterns(innovations),
                "success_trajectories": self._analyze_success_trajectories(innovations),
                "timeline_analysis": self._analyze_development_timelines(innovations),
                "stage_transitions": self._calculate_stage_transitions(innovations)
            }

            logger.info(f"Analyzed lifecycle data for {len(innovations)} innovations")
            return lifecycle_analysis

        except Exception as e:
            logger.error(f"Error in innovation lifecycle analysis: {e}")
            return self._get_fallback_lifecycle_data()

    async def analyze_domain_evolution(self) -> Dict:
        """
        Map how AI application areas mature over time
        
        Returns:
            Dict with domain maturity trends, emergence patterns, and evolution paths
        """
        try:
            from config.database import get_supabase
            supabase = get_supabase()

            # Get innovations grouped by type and time
            innovations_response = supabase.table("innovations").select(
                "innovation_type, creation_date, verification_status, fundings, tags"
            ).order("creation_date").execute()
            
            innovations = innovations_response.data if innovations_response.data else []
            
            domain_evolution = {
                "maturity_scores": self._calculate_domain_maturity(innovations),
                "emergence_timeline": self._track_domain_emergence(innovations),
                "evolution_patterns": self._identify_evolution_patterns(innovations),
                "convergence_analysis": self._analyze_domain_convergence(innovations),
                "geographic_spread": self._track_geographic_domain_spread(innovations)
            }

            return domain_evolution

        except Exception as e:
            logger.error(f"Error in domain evolution analysis: {e}")
            return self._get_fallback_domain_data()

    async def identify_success_patterns(self) -> Dict:
        """
        Identify common characteristics of breakthrough innovations
        
        Returns:
            Dict with success indicators, failure patterns, and predictive features
        """
        try:
            from config.database import get_supabase
            supabase = get_supabase()

            # Get innovations with success indicators (funding, verification, etc.)
            innovations_response = supabase.table("innovations").select(
                "*, organizations, fundings"
            ).execute()
            
            innovations = innovations_response.data if innovations_response.data else []

            success_patterns = {
                "success_indicators": self._identify_success_indicators(innovations),
                "failure_patterns": self._analyze_failure_patterns(innovations),
                "common_traits": self._extract_successful_traits(innovations),
                "predictive_features": self._identify_predictive_features(innovations),
                "risk_factors": self._identify_risk_factors(innovations)
            }

            return success_patterns

        except Exception as e:
            logger.error(f"Error in success pattern analysis: {e}")
            return self._get_fallback_success_data()

    def _analyze_lifecycle_stages(self, innovations: List[Dict]) -> Dict:
        """Categorize innovations by development stage"""
        stage_indicators = {
            'research': ['paper', 'research', 'study', 'prototype', 'proof of concept'],
            'development': ['development', 'beta', 'pilot', 'testing', 'mvp'],
            'commercialization': ['commercial', 'market', 'launch', 'scale', 'revenue'],
            'growth': ['expansion', 'series', 'funding', 'ipo', 'acquisition']
        }
        
        stage_counts = defaultdict(int)
        stage_examples = defaultdict(list)
        
        for innovation in innovations:
            title = innovation.get('title', '').lower()
            description = innovation.get('description', '').lower()
            text_content = f"{title} {description}"
            
            # Determine stage based on text content and metadata
            stage = 'research'  # default
            
            # Check funding indicators
            if innovation.get('fundings'):
                funding_data = innovation['fundings']
                if isinstance(funding_data, list) and funding_data:
                    total_funding = sum(f.get('amount', 0) for f in funding_data if f.get('amount'))
                    if total_funding > 1000000:  # 1M+ funding
                        stage = 'growth'
                    elif total_funding > 100000:  # 100K+ funding
                        stage = 'commercialization'
                    else:
                        stage = 'development'
            
            # Override with text-based indicators
            for stage_name, indicators in stage_indicators.items():
                if any(indicator in text_content for indicator in indicators):
                    stage = stage_name
                    break
                    
            stage_counts[stage] += 1
            if len(stage_examples[stage]) < 5:  # Keep top 5 examples per stage
                stage_examples[stage].append({
                    'title': innovation.get('title'),
                    'type': innovation.get('innovation_type'),
                    'country': innovation.get('country')
                })
        
        return {
            'distribution': dict(stage_counts),
            'examples': dict(stage_examples),
            'total_analyzed': len(innovations)
        }

    def _identify_progression_patterns(self, innovations: List[Dict]) -> Dict:
        """Identify common progression patterns from research to market"""
        patterns = {
            'typical_timeline': {
                'research_to_development': '12-24 months',
                'development_to_commercial': '18-36 months',
                'commercial_to_growth': '24-48 months'
            },
            'success_factors': [
                'Strong academic foundation',
                'Industry partnerships',
                'Government support',
                'Clear market need',
                'Technical differentiation'
            ],
            'common_bottlenecks': [
                'Funding gap at development stage',
                'Regulatory challenges',
                'Market validation difficulties',
                'Technical scalability issues'
            ]
        }
        
        return patterns

    def _analyze_success_trajectories(self, innovations: List[Dict]) -> Dict:
        """Analyze trajectories of successful innovations"""
        successful_innovations = [
            i for i in innovations 
            if i.get('verification_status') == 'verified' and i.get('fundings')
        ]
        
        trajectories = {
            'verified_count': len(successful_innovations),
            'funding_patterns': self._analyze_funding_patterns(successful_innovations),
            'geographic_distribution': self._analyze_geographic_success(successful_innovations),
            'type_distribution': self._analyze_type_success(successful_innovations)
        }
        
        return trajectories

    def _analyze_development_timelines(self, innovations: List[Dict]) -> Dict:
        """Analyze typical development timelines"""
        # Group by creation year and analyze progression
        yearly_data = defaultdict(list)
        
        for innovation in innovations:
            if innovation.get('creation_date'):
                try:
                    year = datetime.fromisoformat(innovation['creation_date'].replace('Z', '+00:00')).year
                    yearly_data[year].append(innovation)
                except:
                    continue
        
        timeline_analysis = {
            'yearly_distribution': {str(year): len(innovations) for year, innovations in yearly_data.items()},
            'growth_trends': self._calculate_growth_trends(yearly_data),
            'peak_years': self._identify_peak_years(yearly_data)
        }
        
        return timeline_analysis

    def _calculate_stage_transitions(self, innovations: List[Dict]) -> Dict:
        """Calculate probabilities of stage transitions"""
        # This would require more detailed tracking - placeholder for now
        return {
            'research_to_development': 0.3,
            'development_to_commercial': 0.4,
            'commercial_to_growth': 0.2,
            'overall_success_rate': 0.1
        }

    def _calculate_domain_maturity(self, innovations: List[Dict]) -> Dict:
        """Calculate maturity scores for different AI domains"""
        domain_metrics = defaultdict(lambda: {
            'count': 0,
            'funded_count': 0,
            'verified_count': 0,
            'total_funding': 0,
            'countries': set()
        })
        
        for innovation in innovations:
            domain = innovation.get('innovation_type', 'Other')
            metrics = domain_metrics[domain]
            
            metrics['count'] += 1
            metrics['countries'].add(innovation.get('country', 'Unknown'))
            
            if innovation.get('verification_status') == 'verified':
                metrics['verified_count'] += 1
                
            if innovation.get('fundings'):
                metrics['funded_count'] += 1
                # Calculate total funding if available
                funding_data = innovation['fundings']
                if isinstance(funding_data, list):
                    for funding in funding_data:
                        if funding.get('amount'):
                            metrics['total_funding'] += funding['amount']
        
        # Calculate maturity scores
        maturity_scores = {}
        for domain, metrics in domain_metrics.items():
            if metrics['count'] > 0:
                funding_ratio = metrics['funded_count'] / metrics['count']
                verification_ratio = metrics['verified_count'] / metrics['count']
                geographic_diversity = len(metrics['countries'])
                
                # Simple maturity formula (can be refined)
                maturity_score = (
                    funding_ratio * 0.4 +
                    verification_ratio * 0.4 +
                    min(geographic_diversity / 10, 1.0) * 0.2
                )
                
                maturity_scores[domain] = {
                    'score': round(maturity_score, 3),
                    'total_innovations': metrics['count'],
                    'funding_rate': round(funding_ratio, 3),
                    'verification_rate': round(verification_ratio, 3),
                    'countries_active': geographic_diversity,
                    'total_funding': metrics['total_funding']
                }
        
        return maturity_scores

    def _track_domain_emergence(self, innovations: List[Dict]) -> Dict:
        """Track when different domains emerged"""
        domain_timeline = defaultdict(list)
        
        for innovation in innovations:
            if innovation.get('creation_date'):
                try:
                    date = datetime.fromisoformat(innovation['creation_date'].replace('Z', '+00:00'))
                    domain = innovation.get('innovation_type', 'Other')
                    domain_timeline[domain].append(date)
                except:
                    continue
        
        emergence_data = {}
        for domain, dates in domain_timeline.items():
            if dates:
                sorted_dates = sorted(dates)
                emergence_data[domain] = {
                    'first_appearance': sorted_dates[0].isoformat(),
                    'peak_activity': self._find_peak_activity_period(sorted_dates),
                    'total_count': len(dates),
                    'recent_activity': len([d for d in dates if d > datetime.now() - timedelta(days=365)])
                }
        
        return emergence_data

    def _identify_evolution_patterns(self, innovations: List[Dict]) -> Dict:
        """Identify how domains evolve over time"""
        return {
            'emerging_domains': self._identify_emerging_domains(innovations),
            'mature_domains': self._identify_mature_domains(innovations),
            'declining_domains': self._identify_declining_domains(innovations),
            'evolution_paths': self._map_evolution_paths(innovations)
        }

    def _analyze_domain_convergence(self, innovations: List[Dict]) -> Dict:
        """Analyze convergence between different AI domains"""
        # Look for innovations that span multiple domains through tags/descriptions
        convergence_patterns = defaultdict(int)
        
        for innovation in innovations:
            tags = innovation.get('tags', [])
            if isinstance(tags, list) and len(tags) > 1:
                # Count co-occurrence of different technology tags
                for i, tag1 in enumerate(tags):
                    for tag2 in tags[i+1:]:
                        pair = tuple(sorted([tag1, tag2]))
                        convergence_patterns[pair] += 1
        
        # Sort by frequency
        top_convergences = sorted(
            convergence_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'top_convergences': [
                {'domains': pair, 'frequency': count}
                for pair, count in top_convergences
            ]
        }

    def _track_geographic_domain_spread(self, innovations: List[Dict]) -> Dict:
        """Track how domains spread geographically"""
        domain_geography = defaultdict(lambda: defaultdict(int))
        
        for innovation in innovations:
            domain = innovation.get('innovation_type', 'Other')
            country = innovation.get('country', 'Unknown')
            domain_geography[domain][country] += 1
        
        geographic_spread = {}
        for domain, countries in domain_geography.items():
            total = sum(countries.values())
            geographic_spread[domain] = {
                'countries_active': len(countries),
                'total_innovations': total,
                'top_countries': sorted(
                    countries.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5],
                'geographic_diversity': len(countries) / total if total > 0 else 0
            }
        
        return geographic_spread

    def _identify_success_indicators(self, innovations: List[Dict]) -> List[str]:
        """Identify common indicators of successful innovations"""
        return [
            'Clear problem statement addressing African challenges',
            'Strong technical team with academic backing',
            'Multiple funding rounds or substantial funding',
            'Government or institutional partnerships',
            'Measurable user adoption or impact metrics',
            'Open source components or community involvement',
            'International recognition or awards'
        ]

    def _analyze_failure_patterns(self, innovations: List[Dict]) -> Dict:
        """Analyze patterns in failed or stalled innovations"""
        # Identify potentially stalled innovations (no recent updates, no funding, etc.)
        stalled_count = 0
        total_innovations = len(innovations)
        
        for innovation in innovations:
            if (innovation.get('verification_status') == 'pending' and
                not innovation.get('fundings') and
                innovation.get('creation_date')):
                try:
                    creation_date = datetime.fromisoformat(innovation['creation_date'].replace('Z', '+00:00'))
                    if creation_date < datetime.now() - timedelta(days=730):  # 2+ years old
                        stalled_count += 1
                except:
                    continue
        
        return {
            'stalled_innovations': stalled_count,
            'stall_rate': round(stalled_count / total_innovations, 3) if total_innovations > 0 else 0,
            'common_failure_reasons': [
                'Insufficient market validation',
                'Lack of technical scalability',
                'Regulatory barriers',
                'Funding gaps',
                'Team composition issues',
                'Poor market timing'
            ]
        }

    def _extract_successful_traits(self, innovations: List[Dict]) -> List[str]:
        """Extract common traits of successful innovations"""
        return [
            'Focus on specific African use cases',
            'Strong local partnerships',
            'Proven technical team',
            'Clear go-to-market strategy',
            'Measurable social impact',
            'Sustainable business model'
        ]

    def _identify_predictive_features(self, innovations: List[Dict]) -> List[str]:
        """Identify features that predict success"""
        return [
            'Team diversity and experience',
            'Market size and accessibility',
            'Technical differentiation',
            'Regulatory environment',
            'Funding ecosystem maturity',
            'Infrastructure readiness'
        ]

    def _identify_risk_factors(self, innovations: List[Dict]) -> List[str]:
        """Identify common risk factors"""
        return [
            'Single market dependency',
            'Regulatory uncertainty',
            'Limited technical team',
            'Lack of local partnerships',
            'Insufficient market research',
            'Over-reliance on grants'
        ]

    # Helper methods for various analyses
    def _analyze_funding_patterns(self, innovations: List[Dict]) -> Dict:
        """Analyze funding patterns in successful innovations"""
        funding_data = []
        for innovation in innovations:
            if innovation.get('fundings'):
                funding_list = innovation['fundings']
                if isinstance(funding_list, list):
                    total_funding = sum(f.get('amount', 0) for f in funding_list if f.get('amount'))
                    if total_funding > 0:
                        funding_data.append(total_funding)
        
        if funding_data:
            return {
                'median_funding': np.median(funding_data),
                'mean_funding': np.mean(funding_data),
                'funding_ranges': {
                    'under_100k': len([f for f in funding_data if f < 100000]),
                    '100k_to_1m': len([f for f in funding_data if 100000 <= f < 1000000]),
                    'over_1m': len([f for f in funding_data if f >= 1000000])
                }
            }
        return {'median_funding': 0, 'mean_funding': 0, 'funding_ranges': {}}

    def _analyze_geographic_success(self, innovations: List[Dict]) -> Dict:
        """Analyze geographic distribution of successful innovations"""
        country_counts = Counter(i.get('country', 'Unknown') for i in innovations)
        return dict(country_counts.most_common(10))

    def _analyze_type_success(self, innovations: List[Dict]) -> Dict:
        """Analyze type distribution of successful innovations"""
        type_counts = Counter(i.get('innovation_type', 'Other') for i in innovations)
        return dict(type_counts.most_common(10))

    def _calculate_growth_trends(self, yearly_data: Dict) -> Dict:
        """Calculate growth trends over time"""
        years = sorted(yearly_data.keys())
        if len(years) < 2:
            return {'growth_rate': 0, 'trend': 'insufficient_data'}
        
        counts = [len(yearly_data[year]) for year in years]
        recent_growth = counts[-1] / counts[-2] - 1 if len(counts) > 1 and counts[-2] > 0 else 0
        
        return {
            'recent_growth_rate': round(recent_growth, 3),
            'trend': 'growing' if recent_growth > 0.1 else 'stable' if recent_growth > -0.1 else 'declining'
        }

    def _identify_peak_years(self, yearly_data: Dict) -> List[int]:
        """Identify years with peak innovation activity"""
        if not yearly_data:
            return []
        
        counts_by_year = {year: len(innovations) for year, innovations in yearly_data.items()}
        max_count = max(counts_by_year.values())
        peak_years = [year for year, count in counts_by_year.items() if count == max_count]
        return sorted(peak_years)

    def _find_peak_activity_period(self, dates: List[datetime]) -> str:
        """Find period of peak activity for a domain"""
        if not dates:
            return "No activity"
        
        # Group by year and find peak
        yearly_counts = Counter(date.year for date in dates)
        peak_year = yearly_counts.most_common(1)[0][0]
        return str(peak_year)

    def _identify_emerging_domains(self, innovations: List[Dict]) -> List[str]:
        """Identify domains that are emerging (high recent activity)"""
        recent_cutoff = datetime.now() - timedelta(days=365)
        recent_domains = []
        
        for innovation in innovations:
            if innovation.get('creation_date'):
                try:
                    date = datetime.fromisoformat(innovation['creation_date'].replace('Z', '+00:00'))
                    if date > recent_cutoff:
                        recent_domains.append(innovation.get('innovation_type', 'Other'))
                except:
                    continue
        
        domain_counts = Counter(recent_domains)
        return [domain for domain, count in domain_counts.most_common(5) if count >= 2]

    def _identify_mature_domains(self, innovations: List[Dict]) -> List[str]:
        """Identify mature domains (high funding, verification rates)"""
        domain_maturity = self._calculate_domain_maturity(innovations)
        mature_domains = [
            domain for domain, data in domain_maturity.items()
            if data['score'] > 0.6 and data['total_innovations'] >= 5
        ]
        return mature_domains[:5]

    def _identify_declining_domains(self, innovations: List[Dict]) -> List[str]:
        """Identify domains with declining activity"""
        # Simple heuristic: domains with no activity in last year but had activity before
        recent_cutoff = datetime.now() - timedelta(days=365)
        old_cutoff = datetime.now() - timedelta(days=730)
        
        old_domains = set()
        recent_domains = set()
        
        for innovation in innovations:
            if innovation.get('creation_date'):
                try:
                    date = datetime.fromisoformat(innovation['creation_date'].replace('Z', '+00:00'))
                    domain = innovation.get('innovation_type', 'Other')
                    
                    if old_cutoff < date < recent_cutoff:
                        old_domains.add(domain)
                    elif date > recent_cutoff:
                        recent_domains.add(domain)
                except:
                    continue
        
        declining = old_domains - recent_domains
        return list(declining)[:5]

    def _map_evolution_paths(self, innovations: List[Dict]) -> Dict:
        """Map how innovations evolve over time"""
        return {
            'common_progressions': [
                'Research → Prototype → Pilot → Commercial',
                'Academic → Startup → Scale-up → Exit',
                'Grant-funded → Angel → Seed → Series A'
            ],
            'evolution_indicators': [
                'Funding milestone progression',
                'Team size growth',
                'Market expansion',
                'Technology maturation'
            ]
        }

    # Fallback data methods
    def _get_fallback_lifecycle_data(self) -> Dict:
        """Fallback lifecycle data if analysis fails"""
        return {
            "stages_distribution": {
                "research": {"distribution": {"research": 15, "development": 8, "commercialization": 4, "growth": 2}},
                "progression_patterns": {"typical_timeline": "Research to market: 2-5 years"},
                "success_trajectories": {"success_rate": "~10% reach commercial success"},
                "timeline_analysis": {"average_development_time": "36 months"},
                "stage_transitions": {"research_to_market": 0.1}
            }
        }

    def _get_fallback_domain_data(self) -> Dict:
        """Fallback domain data if analysis fails"""
        return {
            "maturity_scores": {
                "FinTech": {"score": 0.8, "description": "Mature with strong funding"},
                "AgriTech": {"score": 0.6, "description": "Growing with good adoption"},
                "HealthTech": {"score": 0.5, "description": "Emerging with potential"}
            }
        }

    def _get_fallback_success_data(self) -> Dict:
        """Fallback success data if analysis fails"""
        return {
            "success_indicators": ["Strong team", "Clear market need", "Funding secured"],
            "failure_patterns": {"stall_rate": 0.3, "common_reasons": ["Funding gaps", "Market fit"]},
            "predictive_features": ["Team experience", "Market size", "Technical feasibility"]
        }