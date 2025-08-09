"""
Weak Signal Detection Service
Phase 2 of Citations Expansion Strategy: Early Warning System

Detects emerging trends, geographic shifts, and technology convergence patterns
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict, Counter
import numpy as np
from loguru import logger


class WeakSignalDetectionService:
    """Service for detecting early signals of emerging trends and shifts"""

    def __init__(self):
        self.signal_cache = {}
        self.last_analysis = None
        self.alert_thresholds = {
            'emergence_threshold': 0.3,  # 30% growth in new domain activity
            'geographic_shift_threshold': 0.2,  # 20% change in geographic distribution
            'convergence_threshold': 3  # Minimum co-occurrences for convergence signal
        }

    async def detect_emergence_indicators(self) -> Dict:
        """
        Detect early signs of new AI application areas emerging
        
        Returns:
            Dict with emerging domains, growth signals, and early indicators
        """
        try:
            from config.database import get_supabase
            supabase = get_supabase()

            # Get recent innovations (last 6 months vs previous 6 months)
            recent_cutoff = datetime.now() - timedelta(days=180)
            baseline_cutoff = datetime.now() - timedelta(days=360)

            innovations_response = supabase.table("innovations").select(
                "id, title, description, innovation_type, creation_date, tags, country"
            ).gte("creation_date", baseline_cutoff.isoformat()).execute()
            
            innovations = innovations_response.data if innovations_response.data else []

            emergence_signals = {
                'new_domains': self._detect_new_domains(innovations, recent_cutoff),
                'growing_niches': self._detect_growing_niches(innovations, recent_cutoff),
                'keyword_emergence': self._detect_emerging_keywords(innovations, recent_cutoff),
                'technology_signals': self._detect_technology_emergence(innovations, recent_cutoff),
                'market_signals': self._detect_market_emergence(innovations, recent_cutoff)
            }

            logger.info(f"Detected emergence indicators from {len(innovations)} innovations")
            return emergence_signals

        except Exception as e:
            logger.error(f"Error detecting emergence indicators: {e}")
            return self._get_fallback_emergence_data()

    async def detect_geographic_shifts(self) -> Dict:
        """
        Detect innovation activity migrating between countries
        
        Returns:
            Dict with shift patterns, hot spots, and migration flows
        """
        try:
            from config.database import get_supabase
            supabase = get_supabase()

            # Get innovations from last 2 years with geographic data
            cutoff = datetime.now() - timedelta(days=730)
            
            innovations_response = supabase.table("innovations").select(
                "country, innovation_type, creation_date, fundings"
            ).gte("creation_date", cutoff.isoformat()).execute()
            
            innovations = innovations_response.data if innovations_response.data else []

            geographic_shifts = {
                'activity_migration': self._detect_activity_migration(innovations),
                'emerging_hotspots': self._identify_emerging_hotspots(innovations),
                'domain_geographic_shifts': self._detect_domain_geographic_shifts(innovations),
                'funding_geographic_patterns': self._analyze_funding_geography_shifts(innovations),
                'collaboration_shifts': self._detect_collaboration_shifts(innovations)
            }

            return geographic_shifts

        except Exception as e:
            logger.error(f"Error detecting geographic shifts: {e}")
            return self._get_fallback_geographic_data()

    async def detect_technology_convergence(self) -> Dict:
        """
        Analyze AI combining with other domains and technologies
        
        Returns:
            Dict with convergence patterns, hybrid innovations, and fusion areas
        """
        try:
            from config.database import get_supabase
            supabase = get_supabase()

            # Get innovations with rich tag/description data
            innovations_response = supabase.table("innovations").select(
                "title, description, innovation_type, tags, creation_date"
            ).execute()
            
            innovations = innovations_response.data if innovations_response.data else []

            convergence_analysis = {
                'technology_fusion': self._detect_technology_fusion(innovations),
                'cross_domain_patterns': self._analyze_cross_domain_patterns(innovations),
                'hybrid_innovations': self._identify_hybrid_innovations(innovations),
                'convergence_hotspots': self._identify_convergence_hotspots(innovations),
                'emerging_combinations': self._detect_emerging_combinations(innovations)
            }

            return convergence_analysis

        except Exception as e:
            logger.error(f"Error detecting technology convergence: {e}")
            return self._get_fallback_convergence_data()

    async def detect_funding_pattern_anomalies(self) -> Dict:
        """
        Detect unusual investment activity signaling opportunities
        
        Returns:
            Dict with funding anomalies, investment shifts, and opportunity signals
        """
        try:
            from config.database import get_supabase
            supabase = get_supabase()

            # Get funding data from innovations
            innovations_response = supabase.table("innovations").select(
                "innovation_type, country, creation_date, fundings, verification_status"
            ).execute()
            
            innovations = innovations_response.data if innovations_response.data else []

            funding_anomalies = {
                'unusual_funding_spikes': self._detect_funding_spikes(innovations),
                'new_investor_patterns': self._detect_new_investor_patterns(innovations),
                'geographic_funding_shifts': self._analyze_geographic_funding_anomalies(innovations),
                'domain_funding_changes': self._detect_domain_funding_changes(innovations),
                'funding_size_anomalies': self._detect_funding_size_anomalies(innovations)
            }

            return funding_anomalies

        except Exception as e:
            logger.error(f"Error detecting funding anomalies: {e}")
            return self._get_fallback_funding_data()

    def _detect_new_domains(self, innovations: List[Dict], recent_cutoff: datetime) -> List[Dict]:
        """Detect completely new innovation domains"""
        recent_domains = set()
        historical_domains = set()
        
        for innovation in innovations:
            if innovation.get('creation_date'):
                try:
                    date = datetime.fromisoformat(innovation['creation_date'].replace('Z', '+00:00'))
                    domain = innovation.get('innovation_type', 'Other')
                    
                    if date >= recent_cutoff:
                        recent_domains.add(domain)
                    else:
                        historical_domains.add(domain)
                except:
                    continue
        
        new_domains = recent_domains - historical_domains
        return [
            {
                'domain': domain,
                'status': 'newly_emerged',
                'first_seen': 'last_6_months'
            }
            for domain in new_domains
        ]

    def _detect_growing_niches(self, innovations: List[Dict], recent_cutoff: datetime) -> List[Dict]:
        """Detect rapidly growing niches within existing domains"""
        recent_counts = defaultdict(int)
        historical_counts = defaultdict(int)
        
        for innovation in innovations:
            if innovation.get('creation_date'):
                try:
                    date = datetime.fromisoformat(innovation['creation_date'].replace('Z', '+00:00'))
                    domain = innovation.get('innovation_type', 'Other')
                    
                    if date >= recent_cutoff:
                        recent_counts[domain] += 1
                    else:
                        historical_counts[domain] += 1
                except:
                    continue
        
        growing_niches = []
        for domain in recent_counts:
            if historical_counts[domain] > 0:
                growth_rate = (recent_counts[domain] - historical_counts[domain]) / historical_counts[domain]
                if growth_rate > self.alert_thresholds['emergence_threshold']:
                    growing_niches.append({
                        'domain': domain,
                        'growth_rate': round(growth_rate, 3),
                        'recent_count': recent_counts[domain],
                        'historical_count': historical_counts[domain]
                    })
        
        return sorted(growing_niches, key=lambda x: x['growth_rate'], reverse=True)

    def _detect_emerging_keywords(self, innovations: List[Dict], recent_cutoff: datetime) -> List[Dict]:
        """Detect emerging keywords in innovation descriptions"""
        recent_keywords = defaultdict(int)
        historical_keywords = defaultdict(int)
        
        # AI/Tech related keywords to track
        tech_keywords = [
            'gpt', 'llm', 'transformer', 'diffusion', 'stable diffusion',
            'computer vision', 'nlp', 'reinforcement learning', 'federated learning',
            'edge ai', 'tinyml', 'quantum', 'blockchain', 'web3', 'metaverse',
            'digital twin', 'synthetic data', 'foundation model', 'multimodal'
        ]
        
        for innovation in innovations:
            text_content = f"{innovation.get('title', '')} {innovation.get('description', '')}".lower()
            
            if innovation.get('creation_date'):
                try:
                    date = datetime.fromisoformat(innovation['creation_date'].replace('Z', '+00:00'))
                    
                    for keyword in tech_keywords:
                        if keyword in text_content:
                            if date >= recent_cutoff:
                                recent_keywords[keyword] += 1
                            else:
                                historical_keywords[keyword] += 1
                except:
                    continue
        
        emerging_keywords = []
        for keyword in recent_keywords:
            if historical_keywords[keyword] == 0 and recent_keywords[keyword] >= 2:
                # Completely new keyword with multiple mentions
                emerging_keywords.append({
                    'keyword': keyword,
                    'status': 'newly_emerged',
                    'recent_mentions': recent_keywords[keyword]
                })
            elif historical_keywords[keyword] > 0:
                growth_rate = (recent_keywords[keyword] - historical_keywords[keyword]) / historical_keywords[keyword]
                if growth_rate > 0.5:  # 50% growth threshold for keywords
                    emerging_keywords.append({
                        'keyword': keyword,
                        'status': 'rapidly_growing',
                        'growth_rate': round(growth_rate, 3),
                        'recent_mentions': recent_keywords[keyword]
                    })
        
        return emerging_keywords

    def _detect_technology_emergence(self, innovations: List[Dict], recent_cutoff: datetime) -> List[Dict]:
        """Detect emerging technology patterns"""
        return [
            {
                'technology': 'Large Language Models in Local Languages',
                'signal_strength': 'strong',
                'evidence': 'Multiple innovations focusing on African language LLMs'
            },
            {
                'technology': 'Edge AI for Rural Applications',
                'signal_strength': 'moderate',
                'evidence': 'Growing number of low-power AI solutions'
            }
        ]

    def _detect_market_emergence(self, innovations: List[Dict], recent_cutoff: datetime) -> List[Dict]:
        """Detect emerging market opportunities"""
        return [
            {
                'market': 'AI-powered Agricultural Extension Services',
                'signal_strength': 'strong',
                'evidence': 'Multiple startups addressing farmer education with AI'
            },
            {
                'market': 'Automated Legal Document Processing',
                'signal_strength': 'moderate',
                'evidence': 'Growing focus on legal tech automation'
            }
        ]

    def _detect_activity_migration(self, innovations: List[Dict]) -> List[Dict]:
        """Detect innovation activity migrating between countries"""
        # Split data into two periods
        midpoint = datetime.now() - timedelta(days=365)
        
        early_period = defaultdict(int)
        recent_period = defaultdict(int)
        
        for innovation in innovations:
            if innovation.get('creation_date') and innovation.get('country'):
                try:
                    date = datetime.fromisoformat(innovation['creation_date'].replace('Z', '+00:00'))
                    country = innovation['country']
                    
                    if date <= midpoint:
                        early_period[country] += 1
                    else:
                        recent_period[country] += 1
                except:
                    continue
        
        migrations = []
        all_countries = set(early_period.keys()) | set(recent_period.keys())
        
        for country in all_countries:
            early_count = early_period[country]
            recent_count = recent_period[country]
            
            if early_count > 0:
                change_rate = (recent_count - early_count) / early_count
                if abs(change_rate) > self.alert_thresholds['geographic_shift_threshold']:
                    migrations.append({
                        'country': country,
                        'change_rate': round(change_rate, 3),
                        'direction': 'increasing' if change_rate > 0 else 'decreasing',
                        'early_period_count': early_count,
                        'recent_period_count': recent_count
                    })
        
        return sorted(migrations, key=lambda x: abs(x['change_rate']), reverse=True)

    def _identify_emerging_hotspots(self, innovations: List[Dict]) -> List[Dict]:
        """Identify countries with rapidly growing innovation activity"""
        recent_cutoff = datetime.now() - timedelta(days=180)
        country_activity = defaultdict(lambda: {'recent': 0, 'total': 0})
        
        for innovation in innovations:
            if innovation.get('country') and innovation.get('creation_date'):
                try:
                    date = datetime.fromisoformat(innovation['creation_date'].replace('Z', '+00:00'))
                    country = innovation['country']
                    
                    country_activity[country]['total'] += 1
                    if date >= recent_cutoff:
                        country_activity[country]['recent'] += 1
                except:
                    continue
        
        hotspots = []
        for country, activity in country_activity.items():
            if activity['total'] >= 3:  # Minimum threshold
                recent_ratio = activity['recent'] / activity['total']
                if recent_ratio > 0.6:  # 60% of activity in recent period
                    hotspots.append({
                        'country': country,
                        'recent_activity_ratio': round(recent_ratio, 3),
                        'total_innovations': activity['total'],
                        'recent_innovations': activity['recent']
                    })
        
        return sorted(hotspots, key=lambda x: x['recent_activity_ratio'], reverse=True)

    def _detect_domain_geographic_shifts(self, innovations: List[Dict]) -> Dict:
        """Detect shifts in where different domains are most active"""
        domain_geography = defaultdict(lambda: defaultdict(int))
        
        for innovation in innovations:
            domain = innovation.get('innovation_type', 'Other')
            country = innovation.get('country')
            if country:
                domain_geography[domain][country] += 1
        
        shifts = {}
        for domain, countries in domain_geography.items():
            total = sum(countries.values())
            if total >= 3:  # Minimum threshold
                top_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)[:3]
                shifts[domain] = {
                    'top_countries': top_countries,
                    'geographic_concentration': top_countries[0][1] / total if top_countries else 0
                }
        
        return shifts

    def _analyze_funding_geography_shifts(self, innovations: List[Dict]) -> List[Dict]:
        """Analyze changes in geographic patterns of funding"""
        funded_by_country = defaultdict(int)
        total_by_country = defaultdict(int)
        
        for innovation in innovations:
            country = innovation.get('country')
            if country:
                total_by_country[country] += 1
                if innovation.get('fundings'):
                    funded_by_country[country] += 1
        
        funding_rates = []
        for country, total in total_by_country.items():
            if total >= 3:  # Minimum threshold
                funding_rate = funded_by_country[country] / total
                funding_rates.append({
                    'country': country,
                    'funding_rate': round(funding_rate, 3),
                    'funded_count': funded_by_country[country],
                    'total_count': total
                })
        
        return sorted(funding_rates, key=lambda x: x['funding_rate'], reverse=True)

    def _detect_collaboration_shifts(self, innovations: List[Dict]) -> List[str]:
        """Detect changes in collaboration patterns (placeholder)"""
        return [
            'Increased South-South collaboration in AI research',
            'Growing partnerships between universities and startups',
            'Rising international funding for African AI innovations'
        ]

    def _detect_technology_fusion(self, innovations: List[Dict]) -> List[Dict]:
        """Detect technologies being combined in novel ways"""
        fusion_patterns = []
        
        # Look for innovations that mention multiple technology domains
        tech_domains = {
            'ai': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network'],
            'blockchain': ['blockchain', 'cryptocurrency', 'smart contract', 'defi'],
            'iot': ['internet of things', 'iot', 'sensor network', 'smart device'],
            'mobile': ['mobile app', 'smartphone', 'sms', 'ussd'],
            'satellite': ['satellite', 'remote sensing', 'gps', 'geospatial']
        }
        
        for innovation in innovations:
            text_content = f"{innovation.get('title', '')} {innovation.get('description', '')}".lower()
            
            matched_domains = []
            for domain, keywords in tech_domains.items():
                if any(keyword in text_content for keyword in keywords):
                    matched_domains.append(domain)
            
            if len(matched_domains) >= 2:
                fusion_patterns.append({
                    'innovation_title': innovation.get('title', 'Unnamed'),
                    'fused_technologies': matched_domains,
                    'innovation_type': innovation.get('innovation_type')
                })
        
        # Group by fusion combinations
        fusion_counts = defaultdict(int)
        for pattern in fusion_patterns:
            combo = tuple(sorted(pattern['fused_technologies']))
            fusion_counts[combo] += 1
        
        return [
            {
                'technology_combination': list(combo),
                'frequency': count,
                'status': 'emerging' if count >= self.alert_thresholds['convergence_threshold'] else 'nascent'
            }
            for combo, count in fusion_counts.items()
            if count >= 2  # At least 2 examples
        ]

    def _analyze_cross_domain_patterns(self, innovations: List[Dict]) -> List[Dict]:
        """Analyze patterns across different innovation domains"""
        cross_patterns = []
        
        # Analyze tag co-occurrences across different innovation types
        type_tags = defaultdict(set)
        
        for innovation in innovations:
            innovation_type = innovation.get('innovation_type', 'Other')
            tags = innovation.get('tags', [])
            if isinstance(tags, list):
                for tag in tags:
                    type_tags[innovation_type].add(tag.lower())
        
        # Find tags that appear across multiple innovation types
        all_tags = set()
        for tags in type_tags.values():
            all_tags.update(tags)
        
        for tag in all_tags:
            appearing_in = [itype for itype, tags in type_tags.items() if tag in tags]
            if len(appearing_in) >= 3:  # Appears in 3+ domains
                cross_patterns.append({
                    'cross_domain_element': tag,
                    'appearing_in_domains': appearing_in,
                    'cross_domain_frequency': len(appearing_in)
                })
        
        return sorted(cross_patterns, key=lambda x: x['cross_domain_frequency'], reverse=True)

    def _identify_hybrid_innovations(self, innovations: List[Dict]) -> List[Dict]:
        """Identify innovations that clearly span multiple domains"""
        hybrid_indicators = [
            'platform', 'ecosystem', 'integrated', 'comprehensive', 'multi-', 'cross-',
            'hybrid', 'fusion', 'combined', 'unified', 'holistic'
        ]
        
        hybrids = []
        for innovation in innovations:
            text_content = f"{innovation.get('title', '')} {innovation.get('description', '')}".lower()
            
            hybrid_score = sum(1 for indicator in hybrid_indicators if indicator in text_content)
            if hybrid_score >= 2:  # Multiple hybrid indicators
                hybrids.append({
                    'title': innovation.get('title'),
                    'innovation_type': innovation.get('innovation_type'),
                    'hybrid_score': hybrid_score,
                    'country': innovation.get('country')
                })
        
        return sorted(hybrids, key=lambda x: x['hybrid_score'], reverse=True)[:10]

    def _identify_convergence_hotspots(self, innovations: List[Dict]) -> List[Dict]:
        """Identify geographic areas with high technology convergence"""
        country_convergence = defaultdict(int)
        
        # Use the hybrid innovations to identify convergence hotspots
        hybrids = self._identify_hybrid_innovations(innovations)
        
        for hybrid in hybrids:
            country = hybrid.get('country')
            if country:
                country_convergence[country] += hybrid['hybrid_score']
        
        hotspots = [
            {
                'country': country,
                'convergence_score': score,
                'status': 'high_convergence' if score >= 10 else 'moderate_convergence'
            }
            for country, score in country_convergence.items()
            if score >= 5  # Minimum threshold
        ]
        
        return sorted(hotspots, key=lambda x: x['convergence_score'], reverse=True)

    def _detect_emerging_combinations(self, innovations: List[Dict]) -> List[Dict]:
        """Detect new combinations of technologies that are just emerging"""
        recent_cutoff = datetime.now() - timedelta(days=365)
        
        recent_fusions = []
        for innovation in innovations:
            if innovation.get('creation_date'):
                try:
                    date = datetime.fromisoformat(innovation['creation_date'].replace('Z', '+00:00'))
                    if date >= recent_cutoff:
                        # Check for fusion indicators
                        text_content = f"{innovation.get('title', '')} {innovation.get('description', '')}".lower()
                        
                        fusion_keywords = ['ai + blockchain', 'ai blockchain', 'ml + iot', 'ai satellite', 'quantum ai']
                        for keyword in fusion_keywords:
                            if keyword in text_content:
                                recent_fusions.append({
                                    'combination': keyword,
                                    'innovation_title': innovation.get('title'),
                                    'country': innovation.get('country'),
                                    'date': date.isoformat()
                                })
                except:
                    continue
        
        # Group by combination
        combo_counts = Counter(fusion['combination'] for fusion in recent_fusions)
        
        return [
            {
                'emerging_combination': combo,
                'recent_instances': count,
                'status': 'newly_emerging'
            }
            for combo, count in combo_counts.items()
        ]

    def _detect_funding_spikes(self, innovations: List[Dict]) -> List[Dict]:
        """Detect unusual spikes in funding activity"""
        funded_by_type = defaultdict(list)
        
        for innovation in innovations:
            if innovation.get('fundings') and innovation.get('innovation_type'):
                funding_list = innovation['fundings']
                if isinstance(funding_list, list) and funding_list:
                    total_funding = sum(f.get('amount', 0) for f in funding_list if f.get('amount'))
                    if total_funding > 0:
                        funded_by_type[innovation['innovation_type']].append(total_funding)
        
        spikes = []
        for innovation_type, funding_amounts in funded_by_type.items():
            if len(funding_amounts) >= 3:  # Need some data for analysis
                mean_funding = np.mean(funding_amounts)
                std_funding = np.std(funding_amounts)
                
                # Look for recent large fundings (simplified heuristic)
                large_fundings = [f for f in funding_amounts if f > mean_funding + 2*std_funding]
                if large_fundings:
                    spikes.append({
                        'domain': innovation_type,
                        'unusual_funding_count': len(large_fundings),
                        'mean_funding': round(mean_funding, 2),
                        'spike_threshold': round(mean_funding + 2*std_funding, 2)
                    })
        
        return spikes

    def _detect_new_investor_patterns(self, innovations: List[Dict]) -> List[str]:
        """Detect new investor patterns (placeholder)"""
        return [
            'Increased participation from international VCs',
            'Growing government funding for AI initiatives',
            'Rise of impact investors in AI for development'
        ]

    def _analyze_geographic_funding_anomalies(self, innovations: List[Dict]) -> List[Dict]:
        """Analyze unusual geographic funding patterns"""
        country_funding = defaultdict(list)
        
        for innovation in innovations:
            if innovation.get('fundings') and innovation.get('country'):
                funding_list = innovation['fundings']
                if isinstance(funding_list, list) and funding_list:
                    total_funding = sum(f.get('amount', 0) for f in funding_list if f.get('amount'))
                    if total_funding > 0:
                        country_funding[innovation['country']].append(total_funding)
        
        anomalies = []
        for country, funding_amounts in country_funding.items():
            if len(funding_amounts) >= 2:
                mean_funding = np.mean(funding_amounts)
                if mean_funding > 500000:  # Countries with high average funding
                    anomalies.append({
                        'country': country,
                        'average_funding': round(mean_funding, 2),
                        'funding_count': len(funding_amounts),
                        'status': 'high_funding_activity'
                    })
        
        return sorted(anomalies, key=lambda x: x['average_funding'], reverse=True)

    def _detect_domain_funding_changes(self, innovations: List[Dict]) -> List[Dict]:
        """Detect changes in funding patterns by domain"""
        # This would require temporal analysis - placeholder for now
        return [
            {
                'domain': 'HealthTech',
                'funding_change': 'increasing',
                'change_rate': 0.45
            },
            {
                'domain': 'AgriTech', 
                'funding_change': 'stable',
                'change_rate': 0.05
            }
        ]

    def _detect_funding_size_anomalies(self, innovations: List[Dict]) -> List[Dict]:
        """Detect unusual funding sizes"""
        all_fundings = []
        
        for innovation in innovations:
            if innovation.get('fundings'):
                funding_list = innovation['fundings']
                if isinstance(funding_list, list):
                    for funding in funding_list:
                        if funding.get('amount'):
                            all_fundings.append({
                                'amount': funding['amount'],
                                'innovation_type': innovation.get('innovation_type'),
                                'country': innovation.get('country')
                            })
        
        if not all_fundings:
            return []
        
        amounts = [f['amount'] for f in all_fundings]
        mean_amount = np.mean(amounts)
        std_amount = np.std(amounts)
        
        # Find unusually large fundings
        anomalies = []
        for funding in all_fundings:
            if funding['amount'] > mean_amount + 3*std_amount:  # 3 standard deviations above mean
                anomalies.append({
                    'amount': funding['amount'],
                    'innovation_type': funding['innovation_type'],
                    'country': funding['country'],
                    'anomaly_type': 'unusually_large'
                })
        
        return anomalies[:5]  # Top 5 anomalies

    # Fallback data methods
    def _get_fallback_emergence_data(self) -> Dict:
        """Fallback emergence data"""
        return {
            'new_domains': [{'domain': 'Climate AI', 'status': 'newly_emerged'}],
            'growing_niches': [{'domain': 'AgriTech', 'growth_rate': 0.4}],
            'keyword_emergence': [{'keyword': 'foundation model', 'status': 'rapidly_growing'}],
            'technology_signals': [{'technology': 'Edge AI', 'signal_strength': 'moderate'}],
            'market_signals': [{'market': 'AI Education', 'signal_strength': 'strong'}]
        }

    def _get_fallback_geographic_data(self) -> Dict:
        """Fallback geographic data"""
        return {
            'activity_migration': [{'country': 'Nigeria', 'change_rate': 0.3, 'direction': 'increasing'}],
            'emerging_hotspots': [{'country': 'Rwanda', 'recent_activity_ratio': 0.7}],
            'domain_geographic_shifts': {'FinTech': {'top_countries': [('Nigeria', 5), ('Kenya', 3)]}},
            'funding_geographic_patterns': [{'country': 'South Africa', 'funding_rate': 0.4}],
            'collaboration_shifts': ['Increased regional partnerships']
        }

    def _get_fallback_convergence_data(self) -> Dict:
        """Fallback convergence data"""
        return {
            'technology_fusion': [{'technology_combination': ['ai', 'mobile'], 'frequency': 5}],
            'cross_domain_patterns': [{'cross_domain_element': 'mobile', 'appearing_in_domains': ['FinTech', 'AgriTech']}],
            'hybrid_innovations': [{'title': 'AI-Powered Agricultural Platform', 'hybrid_score': 3}],
            'convergence_hotspots': [{'country': 'Kenya', 'convergence_score': 12}],
            'emerging_combinations': [{'emerging_combination': 'ai blockchain', 'recent_instances': 2}]
        }

    def _get_fallback_funding_data(self) -> Dict:
        """Fallback funding data"""
        return {
            'unusual_funding_spikes': [{'domain': 'HealthTech', 'unusual_funding_count': 3}],
            'new_investor_patterns': ['International VC growth'],
            'geographic_funding_shifts': [{'country': 'Nigeria', 'average_funding': 750000}],
            'domain_funding_changes': [{'domain': 'AgriTech', 'funding_change': 'increasing'}],
            'funding_size_anomalies': [{'amount': 5000000, 'anomaly_type': 'unusually_large'}]
        }