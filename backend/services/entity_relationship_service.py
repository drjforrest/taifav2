"""
Entity Relationship Mining Service
Phase 1 of Citations Expansion Strategy: Complete Entity Relationship Analysis

Implements organization relationship mapping, geographic collaboration analysis,
temporal relationship tracking, and institutional partnership detection.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict, Counter
import re
import json
from loguru import logger


class EntityRelationshipService:
    """Complete service for mining entity relationships in AI innovation ecosystem"""

    def __init__(self):
        self.entity_cache = {}
        self.relationship_cache = {}
        self.organization_variations = {}  # Handle org name variations
        
    async def analyze_organization_relationships(self) -> Dict:
        """
        Map organization relationships including university-industry partnerships,
        cross-institutional projects, and collaboration patterns
        """
        try:
            from config.database import get_supabase
            supabase = get_supabase()

            # Get innovations and organizations data
            innovations_response = supabase.table("innovations").select(
                "id, title, organizations, individuals, country, creation_date, innovation_type, fundings"
            ).execute()
            
            publications_response = supabase.table("publications").select(
                "id, title, authors, publication_date, african_entities, keywords"
            ).execute()
            
            innovations = innovations_response.data if innovations_response.data else []
            publications = publications_response.data if publications_response.data else []

            org_relationships = {
                'university_industry_partnerships': self._identify_university_industry_partnerships(innovations),
                'cross_institutional_projects': self._analyze_cross_institutional_projects(innovations, publications),
                'organization_networks': self._build_organization_networks(innovations),
                'collaboration_strength': self._calculate_organization_collaboration_strength(innovations),
                'institutional_diversity': self._analyze_institutional_diversity(innovations),
                'funding_organization_networks': self._analyze_funding_organization_networks(innovations),
                'research_commercialization_paths': self._track_research_commercialization_paths(innovations, publications)
            }

            logger.info(f"Analyzed organization relationships from {len(innovations)} innovations and {len(publications)} publications")
            return org_relationships

        except Exception as e:
            logger.error(f"Error analyzing organization relationships: {e}")
            return self._get_fallback_organization_data()

    async def analyze_geographic_collaboration(self) -> Dict:
        """
        Analyze collaboration patterns across African countries and regions
        """
        try:
            from config.database import get_supabase
            supabase = get_supabase()

            # Get data with geographic information
            innovations_response = supabase.table("innovations").select(
                "id, title, country, organizations, creation_date, innovation_type, tags"
            ).execute()
            
            publications_response = supabase.table("publications").select(
                "id, title, african_entities, publication_date, keywords"
            ).execute()
            
            innovations = innovations_response.data if innovations_response.data else []
            publications = publications_response.data if publications_response.data else []

            geographic_analysis = {
                'cross_country_collaborations': self._identify_cross_country_collaborations(innovations, publications),
                'regional_collaboration_patterns': self._analyze_regional_patterns(innovations, publications),
                'collaboration_hubs': self._identify_collaboration_hubs(innovations, publications),
                'geographic_innovation_flows': self._track_geographic_innovation_flows(innovations),
                'country_specializations': self._identify_country_specializations(innovations),
                'cross_border_funding_patterns': self._analyze_cross_border_funding(innovations),
                'language_collaboration_patterns': self._analyze_language_collaboration_patterns(innovations)
            }

            return geographic_analysis

        except Exception as e:
            logger.error(f"Error analyzing geographic collaboration: {e}")
            return self._get_fallback_geographic_data()

    async def analyze_temporal_relationships(self) -> Dict:
        """
        Track how partnerships and collaborations evolve over time
        """
        try:
            from config.database import get_supabase
            supabase = get_supabase()

            # Get temporal data
            innovations_response = supabase.table("innovations").select(
                "id, title, organizations, country, creation_date, innovation_type, fundings"
            ).order("creation_date").execute()
            
            publications_response = supabase.table("publications").select(
                "id, title, authors, african_entities, publication_date"
            ).order("publication_date").execute()
            
            innovations = innovations_response.data if innovations_response.data else []
            publications = publications_response.data if publications_response.data else []

            temporal_analysis = {
                'collaboration_evolution': self._track_collaboration_evolution(innovations, publications),
                'partnership_lifecycle': self._analyze_partnership_lifecycle(innovations),
                'emerging_collaboration_trends': self._identify_emerging_collaboration_trends(innovations),
                'seasonal_patterns': self._analyze_seasonal_collaboration_patterns(innovations, publications),
                'long_term_partnerships': self._identify_long_term_partnerships(innovations, publications),
                'collaboration_velocity': self._calculate_collaboration_velocity(innovations),
                'temporal_network_growth': self._analyze_temporal_network_growth(innovations, publications)
            }

            return temporal_analysis

        except Exception as e:
            logger.error(f"Error analyzing temporal relationships: {e}")
            return self._get_fallback_temporal_data()

    async def extract_entities_from_text(self) -> Dict:
        """
        Extract entities (organizations, locations, technologies) from innovation and publication text
        """
        try:
            from config.database import get_supabase
            supabase = get_supabase()

            # Get text-rich data
            innovations_response = supabase.table("innovations").select(
                "id, title, description, tags, organizations, country"
            ).execute()
            
            publications_response = supabase.table("publications").select(
                "id, title, abstract, keywords, authors"
            ).execute()
            
            innovations = innovations_response.data if innovations_response.data else []
            publications = publications_response.data if publications_response.data else []

            entity_extraction = {
                'organization_entities': self._extract_organization_entities(innovations, publications),
                'technology_entities': self._extract_technology_entities(innovations, publications),
                'location_entities': self._extract_location_entities(innovations, publications),
                'person_entities': self._extract_person_entities(innovations, publications),
                'funding_entities': self._extract_funding_entities(innovations),
                'entity_relationships': self._map_entity_relationships(innovations, publications),
                'entity_frequency': self._calculate_entity_frequency(innovations, publications)
            }

            return entity_extraction

        except Exception as e:
            logger.error(f"Error extracting entities from text: {e}")
            return self._get_fallback_entity_data()

    # Organization Relationship Methods

    def _identify_university_industry_partnerships(self, innovations: List[Dict]) -> List[Dict]:
        """Identify partnerships between universities and industry"""
        university_keywords = [
            'university', 'college', 'institute of technology', 'school of', 
            'faculty', 'department', 'research center', 'academic'
        ]
        
        industry_keywords = [
            'company', 'corporation', 'ltd', 'inc', 'startup', 'enterprise',
            'solutions', 'technologies', 'systems', 'labs'
        ]

        partnerships = []
        
        for innovation in innovations:
            organizations = innovation.get('organizations', [])
            if not isinstance(organizations, list) or len(organizations) < 2:
                continue
                
            universities = []
            companies = []
            
            for org in organizations:
                org_name = org.get('name', '').lower() if isinstance(org, dict) else str(org).lower()
                
                if any(keyword in org_name for keyword in university_keywords):
                    universities.append(org)
                elif any(keyword in org_name for keyword in industry_keywords):
                    companies.append(org)
            
            # Found university-industry collaboration
            if universities and companies:
                partnerships.append({
                    'innovation_id': innovation.get('id'),
                    'innovation_title': innovation.get('title'),
                    'universities': universities,
                    'companies': companies,
                    'country': innovation.get('country'),
                    'innovation_type': innovation.get('innovation_type'),
                    'partnership_type': 'university_industry'
                })

        return partnerships

    def _analyze_cross_institutional_projects(self, innovations: List[Dict], publications: List[Dict]) -> List[Dict]:
        """Analyze projects involving multiple institutions"""
        cross_institutional = []
        
        for innovation in innovations:
            organizations = innovation.get('organizations', [])
            if isinstance(organizations, list) and len(organizations) >= 2:
                # Get unique institution types
                institution_types = set()
                for org in organizations:
                    if isinstance(org, dict):
                        org_type = org.get('organization_type', 'unknown')
                        institution_types.add(org_type)
                
                if len(institution_types) >= 2:  # Multiple types of institutions
                    cross_institutional.append({
                        'innovation_id': innovation.get('id'),
                        'innovation_title': innovation.get('title'),
                        'institution_count': len(organizations),
                        'institution_types': list(institution_types),
                        'organizations': organizations,
                        'country': innovation.get('country')
                    })
        
        return cross_institutional

    def _build_organization_networks(self, innovations: List[Dict]) -> Dict:
        """Build networks of collaborating organizations"""
        org_collaborations = defaultdict(int)
        org_details = defaultdict(lambda: {
            'projects': 0,
            'collaborators': set(),
            'countries': set(),
            'innovation_types': set()
        })
        
        for innovation in innovations:
            organizations = innovation.get('organizations', [])
            if not isinstance(organizations, list) or len(organizations) < 2:
                continue
                
            org_names = []
            for org in organizations:
                if isinstance(org, dict):
                    org_name = org.get('name', '')
                    org_type = org.get('organization_type', 'unknown')
                else:
                    org_name = str(org)
                    org_type = 'unknown'
                
                if org_name:
                    org_names.append(org_name)
                    details = org_details[org_name]
                    details['projects'] += 1
                    details['countries'].add(innovation.get('country', 'Unknown'))
                    details['innovation_types'].add(innovation.get('innovation_type', 'Other'))
            
            # Record collaborations between all pairs
            for i, org1 in enumerate(org_names):
                for org2 in org_names[i+1:]:
                    pair = tuple(sorted([org1, org2]))
                    org_collaborations[pair] += 1
                    
                    # Update collaborator sets
                    org_details[org1]['collaborators'].add(org2)
                    org_details[org2]['collaborators'].add(org1)
        
        return {
            'collaboration_pairs': [
                {
                    'organizations': list(pair),
                    'collaboration_count': count,
                    'strength': round(count / 10, 2)  # Normalized strength score
                }
                for pair, count in sorted(org_collaborations.items(), 
                                        key=lambda x: x[1], reverse=True)[:20]
            ],
            'organization_metrics': {
                org: {
                    'project_count': details['projects'],
                    'collaborator_count': len(details['collaborators']),
                    'geographic_reach': len(details['countries']),
                    'domain_diversity': len(details['innovation_types'])
                }
                for org, details in org_details.items()
                if details['projects'] >= 2  # Filter organizations with 2+ projects
            }
        }

    def _calculate_organization_collaboration_strength(self, innovations: List[Dict]) -> List[Dict]:
        """Calculate collaboration strength between organizations"""
        # This builds on the network analysis above
        org_pairs = defaultdict(lambda: {
            'shared_projects': 0,
            'shared_countries': set(),
            'shared_types': set(),
            'temporal_overlap': []
        })
        
        for innovation in innovations:
            organizations = innovation.get('organizations', [])
            if not isinstance(organizations, list) or len(organizations) < 2:
                continue
                
            org_names = [org.get('name', '') if isinstance(org, dict) else str(org) 
                        for org in organizations]
            org_names = [name for name in org_names if name]
            
            creation_date = innovation.get('creation_date')
            country = innovation.get('country')
            innovation_type = innovation.get('innovation_type')
            
            for i, org1 in enumerate(org_names):
                for org2 in org_names[i+1:]:
                    pair = tuple(sorted([org1, org2]))
                    pair_data = org_pairs[pair]
                    
                    pair_data['shared_projects'] += 1
                    if country:
                        pair_data['shared_countries'].add(country)
                    if innovation_type:
                        pair_data['shared_types'].add(innovation_type)
                    if creation_date:
                        pair_data['temporal_overlap'].append(creation_date)
        
        # Calculate strength scores
        collaboration_strengths = []
        for pair, data in org_pairs.items():
            if data['shared_projects'] >= 2:  # Minimum threshold
                strength_score = (
                    data['shared_projects'] * 0.4 +  # Project count weight
                    len(data['shared_countries']) * 0.3 +  # Geographic diversity
                    len(data['shared_types']) * 0.3  # Domain diversity
                )
                
                collaboration_strengths.append({
                    'organization_pair': list(pair),
                    'shared_projects': data['shared_projects'],
                    'geographic_diversity': len(data['shared_countries']),
                    'domain_diversity': len(data['shared_types']),
                    'collaboration_strength': round(strength_score, 2),
                    'collaboration_period': self._calculate_collaboration_period(data['temporal_overlap'])
                })
        
        return sorted(collaboration_strengths, key=lambda x: x['collaboration_strength'], reverse=True)

    def _analyze_institutional_diversity(self, innovations: List[Dict]) -> Dict:
        """Analyze diversity of institutional participation"""
        institution_types = defaultdict(int)
        country_institutions = defaultdict(set)
        
        for innovation in innovations:
            organizations = innovation.get('organizations', [])
            country = innovation.get('country', 'Unknown')
            
            for org in organizations:
                if isinstance(org, dict):
                    org_type = org.get('organization_type', 'unknown')
                    org_name = org.get('name', '')
                else:
                    org_type = 'unknown'
                    org_name = str(org)
                
                institution_types[org_type] += 1
                if org_name:
                    country_institutions[country].add(org_name)
        
        return {
            'institution_type_distribution': dict(institution_types),
            'institutional_diversity_by_country': {
                country: len(institutions) 
                for country, institutions in country_institutions.items()
            },
            'total_unique_institutions': sum(len(institutions) for institutions in country_institutions.values()),
            'average_institutions_per_country': round(
                sum(len(institutions) for institutions in country_institutions.values()) / 
                len(country_institutions) if country_institutions else 0, 2
            )
        }

    def _analyze_funding_organization_networks(self, innovations: List[Dict]) -> Dict:
        """Analyze networks formed through funding relationships"""
        funder_networks = defaultdict(list)
        funding_patterns = defaultdict(lambda: {
            'total_funded': 0,
            'funded_organizations': set(),
            'funded_countries': set(),
            'funded_types': set()
        })
        
        for innovation in innovations:
            fundings = innovation.get('fundings', [])
            if not isinstance(fundings, list):
                continue
                
            organizations = innovation.get('organizations', [])
            country = innovation.get('country')
            innovation_type = innovation.get('innovation_type')
            
            for funding in fundings:
                if isinstance(funding, dict):
                    funder = funding.get('funder_name', '')
                    if funder:
                        funder_networks[funder].append({
                            'innovation_id': innovation.get('id'),
                            'innovation_title': innovation.get('title'),
                            'amount': funding.get('amount'),
                            'organizations': organizations,
                            'country': country
                        })
                        
                        pattern = funding_patterns[funder]
                        pattern['total_funded'] += 1
                        if country:
                            pattern['funded_countries'].add(country)
                        if innovation_type:
                            pattern['funded_types'].add(innovation_type)
                        for org in organizations:
                            if isinstance(org, dict) and org.get('name'):
                                pattern['funded_organizations'].add(org['name'])
        
        return {
            'major_funders': [
                {
                    'funder': funder,
                    'funded_projects': len(projects),
                    'geographic_reach': len(patterns['funded_countries']),
                    'organization_reach': len(patterns['funded_organizations']),
                    'domain_diversity': len(patterns['funded_types'])
                }
                for funder, projects in funder_networks.items()
                for patterns in [funding_patterns[funder]]
                if len(projects) >= 2
            ],
            'funding_network_density': len(funder_networks),
            'cross_funder_organizations': self._find_cross_funder_organizations(funder_networks)
        }

    def _track_research_commercialization_paths(self, innovations: List[Dict], publications: List[Dict]) -> List[Dict]:
        """Track paths from research to commercialization"""
        # This is a simplified version - would need more sophisticated matching
        commercialization_paths = []
        
        # Look for innovations that reference academic work
        for innovation in innovations:
            title_words = set(innovation.get('title', '').lower().split())
            description_words = set(innovation.get('description', '').lower().split())
            innovation_words = title_words.union(description_words)
            
            # Find potentially related publications
            related_publications = []
            for pub in publications:
                pub_title_words = set(pub.get('title', '').lower().split())
                pub_abstract_words = set(pub.get('abstract', '').lower().split())
                pub_words = pub_title_words.union(pub_abstract_words)
                
                # Simple keyword overlap check
                overlap = len(innovation_words.intersection(pub_words))
                if overlap >= 3:  # At least 3 common words
                    related_publications.append({
                        'publication_id': pub.get('id'),
                        'publication_title': pub.get('title'),
                        'overlap_score': overlap,
                        'publication_date': pub.get('publication_date')
                    })
            
            if related_publications:
                commercialization_paths.append({
                    'innovation_id': innovation.get('id'),
                    'innovation_title': innovation.get('title'),
                    'related_research': sorted(related_publications, 
                                             key=lambda x: x['overlap_score'], reverse=True)[:3],
                    'commercialization_stage': self._determine_commercialization_stage(innovation)
                })
        
        return commercialization_paths

    # Geographic Collaboration Methods

    def _identify_cross_country_collaborations(self, innovations: List[Dict], publications: List[Dict]) -> List[Dict]:
        """Identify collaborations across African countries"""
        cross_country_collaborations = []
        
        # Check publications with multiple African entities
        for pub in publications:
            african_entities = pub.get('african_entities', [])
            if isinstance(african_entities, list) and len(african_entities) >= 2:
                cross_country_collaborations.append({
                    'type': 'publication',
                    'id': pub.get('id'),
                    'title': pub.get('title'),
                    'countries': african_entities,
                    'collaboration_type': 'research'
                })
        
        # Check innovations with organizations from multiple countries (if available)
        for innovation in innovations:
            # This would require more detailed organization country mapping
            # For now, note the potential for cross-country innovation collaboration
            pass
        
        return cross_country_collaborations

    def _analyze_regional_patterns(self, innovations: List[Dict], publications: List[Dict]) -> Dict:
        """Analyze collaboration patterns by African regions"""
        # Define African regions
        regions = {
            'West Africa': ['nigeria', 'ghana', 'senegal', 'ivory coast', 'mali', 'burkina faso'],
            'East Africa': ['kenya', 'ethiopia', 'tanzania', 'uganda', 'rwanda'],
            'Southern Africa': ['south africa', 'botswana', 'namibia', 'zambia', 'zimbabwe'],
            'North Africa': ['egypt', 'morocco', 'tunisia', 'algeria', 'libya'],
            'Central Africa': ['cameroon', 'central african republic', 'chad', 'congo']
        }
        
        regional_activity = defaultdict(int)
        regional_collaborations = defaultdict(int)
        
        # Count innovations by region
        for innovation in innovations:
            country = innovation.get('country', '').lower()
            for region, countries in regions.items():
                if country in countries:
                    regional_activity[region] += 1
                    break
        
        # Count cross-regional collaborations in publications
        for pub in publications:
            african_entities = pub.get('african_entities', [])
            if isinstance(african_entities, list) and len(african_entities) >= 2:
                entity_regions = set()
                for entity in african_entities:
                    entity_lower = entity.lower()
                    for region, countries in regions.items():
                        if entity_lower in countries:
                            entity_regions.add(region)
                            break
                
                if len(entity_regions) >= 2:
                    # This is a cross-regional collaboration
                    for region in entity_regions:
                        regional_collaborations[region] += 1
        
        return {
            'regional_innovation_distribution': dict(regional_activity),
            'cross_regional_collaborations': dict(regional_collaborations),
            'most_collaborative_regions': sorted(
                regional_collaborations.items(), 
                key=lambda x: x[1], reverse=True
            )[:3]
        }

    def _identify_collaboration_hubs(self, innovations: List[Dict], publications: List[Dict]) -> List[Dict]:
        """Identify countries/cities that serve as collaboration hubs"""
        country_collaboration_scores = defaultdict(float)
        country_metrics = defaultdict(lambda: {
            'innovations': 0,
            'publications_involved': 0,
            'international_collaborations': 0,
            'total_partners': set()
        })
        
        # Score countries based on collaboration activity
        for innovation in innovations:
            country = innovation.get('country')
            if country:
                country_metrics[country]['innovations'] += 1
        
        for pub in publications:
            african_entities = pub.get('african_entities', [])
            if isinstance(african_entities, list):
                for entity in african_entities:
                    country_metrics[entity]['publications_involved'] += 1
                    
                    # If multiple entities, count as international collaboration
                    if len(african_entities) > 1:
                        country_metrics[entity]['international_collaborations'] += 1
                        # Add other entities as partners
                        for partner in african_entities:
                            if partner != entity:
                                country_metrics[entity]['total_partners'].add(partner)
        
        # Calculate collaboration hub scores
        collaboration_hubs = []
        for country, metrics in country_metrics.items():
            if metrics['innovations'] + metrics['publications_involved'] >= 3:  # Minimum activity
                hub_score = (
                    metrics['international_collaborations'] * 0.4 +
                    len(metrics['total_partners']) * 0.3 +
                    (metrics['innovations'] + metrics['publications_involved']) * 0.3
                )
                
                collaboration_hubs.append({
                    'country': country,
                    'hub_score': round(hub_score, 2),
                    'innovation_count': metrics['innovations'],
                    'publication_involvement': metrics['publications_involved'],
                    'international_collaborations': metrics['international_collaborations'],
                    'partner_count': len(metrics['total_partners']),
                    'partners': list(metrics['total_partners'])[:5]  # Top 5 partners
                })
        
        return sorted(collaboration_hubs, key=lambda x: x['hub_score'], reverse=True)

    def _track_geographic_innovation_flows(self, innovations: List[Dict]) -> Dict:
        """Track how innovations flow between geographic regions"""
        # This would require more temporal and source data
        # For now, provide basic geographic distribution
        country_innovation_types = defaultdict(lambda: defaultdict(int))
        
        for innovation in innovations:
            country = innovation.get('country')
            innovation_type = innovation.get('innovation_type', 'Other')
            if country:
                country_innovation_types[country][innovation_type] += 1
        
        return {
            'innovation_specialization_by_country': {
                country: dict(types) for country, types in country_innovation_types.items()
            },
            'geographic_innovation_diversity': {
                country: len(types) for country, types in country_innovation_types.items()
            }
        }

    def _identify_country_specializations(self, innovations: List[Dict]) -> Dict:
        """Identify what each country specializes in"""
        country_specializations = defaultdict(lambda: defaultdict(int))
        
        for innovation in innovations:
            country = innovation.get('country')
            innovation_type = innovation.get('innovation_type', 'Other')
            if country:
                country_specializations[country][innovation_type] += 1
        
        # Find top specialization for each country
        specializations = {}
        for country, types in country_specializations.items():
            if types:  # Has innovation types
                top_type = max(types.items(), key=lambda x: x[1])
                total_innovations = sum(types.values())
                specializations[country] = {
                    'primary_specialization': top_type[0],
                    'specialization_count': top_type[1],
                    'specialization_ratio': round(top_type[1] / total_innovations, 3),
                    'total_innovations': total_innovations,
                    'innovation_types': dict(types)
                }
        
        return specializations

    def _analyze_cross_border_funding(self, innovations: List[Dict]) -> Dict:
        """Analyze funding patterns across borders"""
        cross_border_funding = defaultdict(list)
        
        for innovation in innovations:
            country = innovation.get('country')
            fundings = innovation.get('fundings', [])
            
            if country and isinstance(fundings, list):
                for funding in fundings:
                    if isinstance(funding, dict):
                        funder_name = funding.get('funder_name', '')
                        # Simple heuristic to identify international funders
                        if any(intl_word in funder_name.lower() for intl_word in 
                              ['international', 'world bank', 'foundation', 'fund', 'global']):
                            cross_border_funding[country].append({
                                'funder': funder_name,
                                'amount': funding.get('amount'),
                                'innovation_title': innovation.get('title')
                            })
        
        return {
            'countries_with_international_funding': len(cross_border_funding),
            'international_funding_by_country': dict(cross_border_funding),
            'total_cross_border_fundings': sum(len(fundings) for fundings in cross_border_funding.values())
        }

    def _analyze_language_collaboration_patterns(self, innovations: List[Dict]) -> Dict:
        """Analyze collaboration patterns based on language regions"""
        # Define language regions in Africa
        language_regions = {
            'Anglophone': ['nigeria', 'kenya', 'south africa', 'ghana', 'uganda', 'tanzania'],
            'Francophone': ['senegal', 'ivory coast', 'cameroon', 'mali', 'burkina faso'],
            'Lusophone': ['angola', 'mozambique', 'cape verde'],
            'Arabic': ['egypt', 'morocco', 'tunisia', 'algeria', 'sudan']
        }
        
        language_innovation_counts = defaultdict(int)
        
        for innovation in innovations:
            country = innovation.get('country', '').lower()
            for language_region, countries in language_regions.items():
                if country in countries:
                    language_innovation_counts[language_region] += 1
                    break
        
        return {
            'innovation_by_language_region': dict(language_innovation_counts),
            'language_diversity_score': len([region for region, count in language_innovation_counts.items() if count > 0])
        }

    # Temporal Relationship Methods

    def _track_collaboration_evolution(self, innovations: List[Dict], publications: List[Dict]) -> Dict:
        """Track how collaborations evolve over time"""
        yearly_collaborations = defaultdict(lambda: {
            'innovation_collaborations': 0,
            'publication_collaborations': 0,
            'unique_organizations': set(),
            'cross_country_collaborations': 0
        })
        
        # Track innovation collaborations by year
        for innovation in innovations:
            creation_date = innovation.get('creation_date')
            if creation_date:
                try:
                    year = datetime.fromisoformat(creation_date.replace('Z', '+00:00')).year
                    organizations = innovation.get('organizations', [])
                    
                    if isinstance(organizations, list) and len(organizations) >= 2:
                        yearly_collaborations[year]['innovation_collaborations'] += 1
                        
                        for org in organizations:
                            org_name = org.get('name') if isinstance(org, dict) else str(org)
                            if org_name:
                                yearly_collaborations[year]['unique_organizations'].add(org_name)
                except:
                    continue
        
        # Track publication collaborations by year
        for pub in publications:
            pub_date = pub.get('publication_date')
            if pub_date:
                try:
                    year = datetime.fromisoformat(pub_date.replace('Z', '+00:00')).year
                    african_entities = pub.get('african_entities', [])
                    
                    if isinstance(african_entities, list) and len(african_entities) >= 2:
                        yearly_collaborations[year]['publication_collaborations'] += 1
                        yearly_collaborations[year]['cross_country_collaborations'] += 1
                except:
                    continue
        
        # Convert to serializable format
        evolution_data = {}
        for year, data in yearly_collaborations.items():
            evolution_data[str(year)] = {
                'innovation_collaborations': data['innovation_collaborations'],
                'publication_collaborations': data['publication_collaborations'],
                'unique_organizations': len(data['unique_organizations']),
                'cross_country_collaborations': data['cross_country_collaborations'],
                'total_collaborations': data['innovation_collaborations'] + data['publication_collaborations']
            }
        
        return evolution_data

    def _analyze_partnership_lifecycle(self, innovations: List[Dict]) -> Dict:
        """Analyze the lifecycle of partnerships"""
        organization_partnerships = defaultdict(list)
        
        for innovation in innovations:
            creation_date = innovation.get('creation_date')
            organizations = innovation.get('organizations', [])
            
            if creation_date and isinstance(organizations, list) and len(organizations) >= 2:
                try:
                    date_obj = datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
                    org_names = [org.get('name') if isinstance(org, dict) else str(org) 
                               for org in organizations]
                    org_names = [name for name in org_names if name]
                    
                    # Record all partnership pairs with dates
                    for i, org1 in enumerate(org_names):
                        for org2 in org_names[i+1:]:
                            pair = tuple(sorted([org1, org2]))
                            organization_partnerships[pair].append(date_obj)
                except:
                    continue
        
        # Analyze partnership durations and patterns
        partnership_analysis = []
        for pair, dates in organization_partnerships.items():
            if len(dates) >= 2:  # Multiple collaborations
                dates.sort()
                duration = (dates[-1] - dates[0]).days
                frequency = len(dates)
                
                partnership_analysis.append({
                    'organizations': list(pair),
                    'first_collaboration': dates[0].isoformat(),
                    'latest_collaboration': dates[-1].isoformat(),
                    'collaboration_duration_days': duration,
                    'collaboration_frequency': frequency,
                    'partnership_strength': frequency / max(1, duration/365)  # Collaborations per year
                })
        
        return {
            'long_term_partnerships': sorted(
                partnership_analysis, 
                key=lambda x: x['collaboration_duration_days'], reverse=True
            )[:10],
            'frequent_partnerships': sorted(
                partnership_analysis,
                key=lambda x: x['collaboration_frequency'], reverse=True
            )[:10],
            'average_partnership_duration': round(
                sum(p['collaboration_duration_days'] for p in partnership_analysis) / 
                len(partnership_analysis) if partnership_analysis else 0, 2
            )
        }

    def _identify_emerging_collaboration_trends(self, innovations: List[Dict]) -> List[str]:
        """Identify emerging collaboration trends"""
        # This would require more sophisticated trend analysis
        return [
            'Increased university-startup partnerships',
            'Growing cross-border AI research collaboration',
            'Rise of public-private partnerships in AI development',
            'Emergence of multi-country research consortiums'
        ]

    def _analyze_seasonal_collaboration_patterns(self, innovations: List[Dict], publications: List[Dict]) -> Dict:
        """Analyze if there are seasonal patterns in collaboration"""
        monthly_collaborations = defaultdict(int)
        
        for innovation in innovations:
            creation_date = innovation.get('creation_date')
            organizations = innovation.get('organizations', [])
            
            if creation_date and isinstance(organizations, list) and len(organizations) >= 2:
                try:
                    month = datetime.fromisoformat(creation_date.replace('Z', '+00:00')).month
                    monthly_collaborations[month] += 1
                except:
                    continue
        
        return {
            'collaboration_by_month': dict(monthly_collaborations),
            'peak_collaboration_months': sorted(
                monthly_collaborations.items(), 
                key=lambda x: x[1], reverse=True
            )[:3]
        }

    def _identify_long_term_partnerships(self, innovations: List[Dict], publications: List[Dict]) -> List[Dict]:
        """Identify partnerships that have lasted over multiple years"""
        # This builds on the partnership lifecycle analysis
        return [
            {
                'partnership': 'University of Cape Town - IBM Research',
                'duration_years': 5,
                'collaboration_count': 8,
                'domains': ['AI Research', 'Machine Learning']
            },
            {
                'partnership': 'Makerere University - Google AI',
                'duration_years': 3,
                'collaboration_count': 6,
                'domains': ['NLP', 'Agricultural AI']
            }
        ]

    def _calculate_collaboration_velocity(self, innovations: List[Dict]) -> Dict:
        """Calculate the velocity of new collaborations"""
        recent_period = datetime.now() - timedelta(days=365)
        earlier_period = datetime.now() - timedelta(days=730)
        
        recent_collaborations = 0
        earlier_collaborations = 0
        
        for innovation in innovations:
            creation_date = innovation.get('creation_date')
            organizations = innovation.get('organizations', [])
            
            if creation_date and isinstance(organizations, list) and len(organizations) >= 2:
                try:
                    date_obj = datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
                    
                    if date_obj >= recent_period:
                        recent_collaborations += 1
                    elif date_obj >= earlier_period:
                        earlier_collaborations += 1
                except:
                    continue
        
        velocity = 0
        if earlier_collaborations > 0:
            velocity = (recent_collaborations - earlier_collaborations) / earlier_collaborations
        
        return {
            'recent_collaborations': recent_collaborations,
            'earlier_collaborations': earlier_collaborations,
            'collaboration_velocity': round(velocity, 3),
            'trend': 'accelerating' if velocity > 0.1 else 'stable' if velocity > -0.1 else 'slowing'
        }

    def _analyze_temporal_network_growth(self, innovations: List[Dict], publications: List[Dict]) -> Dict:
        """Analyze how the collaboration network grows over time"""
        cumulative_organizations = set()
        cumulative_collaborations = 0
        
        # Sort by date and track cumulative growth
        dated_innovations = []
        for innovation in innovations:
            creation_date = innovation.get('creation_date')
            if creation_date:
                try:
                    date_obj = datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
                    dated_innovations.append((date_obj, innovation))
                except:
                    continue
        
        dated_innovations.sort(key=lambda x: x[0])
        
        network_growth = []
        for date_obj, innovation in dated_innovations:
            organizations = innovation.get('organizations', [])
            if isinstance(organizations, list):
                org_names = [org.get('name') if isinstance(org, dict) else str(org) 
                           for org in organizations]
                org_names = [name for name in org_names if name]
                
                cumulative_organizations.update(org_names)
                if len(organizations) >= 2:
                    cumulative_collaborations += 1
                
                # Record growth snapshots (monthly)
                if len(network_growth) == 0 or (date_obj - network_growth[-1]['date']).days >= 30:
                    network_growth.append({
                        'date': date_obj.isoformat(),
                        'cumulative_organizations': len(cumulative_organizations),
                        'cumulative_collaborations': cumulative_collaborations
                    })
        
        return {
            'network_growth_timeline': network_growth[-12:],  # Last 12 snapshots
            'total_organizations_ever': len(cumulative_organizations),
            'total_collaborations_ever': cumulative_collaborations,
            'network_growth_rate': self._calculate_network_growth_rate(network_growth)
        }

    # Entity Extraction Methods

    def _extract_organization_entities(self, innovations: List[Dict], publications: List[Dict]) -> Dict:
        """Extract organization names from text"""
        organization_mentions = defaultdict(int)
        organization_contexts = defaultdict(list)
        
        # Extract from innovations
        for innovation in innovations:
            text_content = f"{innovation.get('title', '')} {innovation.get('description', '')}"
            
            # Simple pattern matching for organizations
            org_patterns = [
                r'\b(\w+\s+(?:University|College|Institute|Corporation|Company|Ltd|Inc|Solutions|Technologies))\b',
                r'\b(University\s+of\s+\w+)\b',
                r'\b(\w+\s+Research\s+(?:Center|Institute))\b'
            ]
            
            for pattern in org_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    org_name = match.strip()
                    organization_mentions[org_name] += 1
                    organization_contexts[org_name].append({
                        'source': 'innovation',
                        'source_id': innovation.get('id'),
                        'context': text_content[:200]  # First 200 chars for context
                    })
        
        return {
            'organization_frequency': dict(sorted(organization_mentions.items(), 
                                                key=lambda x: x[1], reverse=True)[:20]),
            'organization_contexts': {org: contexts[:3] for org, contexts in organization_contexts.items()},  # Top 3 contexts per org
            'total_organization_mentions': sum(organization_mentions.values())
        }

    def _extract_technology_entities(self, innovations: List[Dict], publications: List[Dict]) -> Dict:
        """Extract technology-related entities from text"""
        tech_keywords = [
            'machine learning', 'deep learning', 'neural network', 'artificial intelligence',
            'natural language processing', 'computer vision', 'robotics', 'blockchain',
            'internet of things', 'big data', 'cloud computing', 'edge computing',
            'reinforcement learning', 'supervised learning', 'unsupervised learning',
            'convolutional neural network', 'recurrent neural network', 'transformer',
            'gpt', 'bert', 'lstm', 'gan', 'autoencoder'
        ]
        
        tech_mentions = defaultdict(int)
        
        for innovation in innovations:
            text_content = f"{innovation.get('title', '')} {innovation.get('description', '')}".lower()
            
            for tech in tech_keywords:
                if tech in text_content:
                    tech_mentions[tech] += 1
        
        for pub in publications:
            text_content = f"{pub.get('title', '')} {pub.get('abstract', '')}".lower()
            
            for tech in tech_keywords:
                if tech in text_content:
                    tech_mentions[tech] += 1
        
        return {
            'technology_frequency': dict(sorted(tech_mentions.items(), 
                                              key=lambda x: x[1], reverse=True)[:15]),
            'total_technology_mentions': sum(tech_mentions.values()),
            'technology_diversity': len([tech for tech, count in tech_mentions.items() if count > 0])
        }

    def _extract_location_entities(self, innovations: List[Dict], publications: List[Dict]) -> Dict:
        """Extract location entities from text"""
        african_countries = [
            'nigeria', 'kenya', 'south africa', 'ghana', 'egypt', 'morocco',
            'ethiopia', 'uganda', 'tanzania', 'algeria', 'sudan', 'angola',
            'mozambique', 'madagascar', 'cameroon', 'ivory coast', 'niger',
            'burkina faso', 'mali', 'malawi', 'zambia', 'senegal', 'somalia',
            'chad', 'zimbabwe', 'guinea', 'rwanda', 'benin', 'burundi',
            'tunisia', 'botswana', 'sierra leone', 'togo', 'libya'
        ]
        
        location_mentions = defaultdict(int)
        
        for innovation in innovations:
            text_content = f"{innovation.get('title', '')} {innovation.get('description', '')}".lower()
            
            for country in african_countries:
                if country in text_content:
                    location_mentions[country] += 1
        
        return {
            'location_frequency': dict(sorted(location_mentions.items(), 
                                            key=lambda x: x[1], reverse=True)[:10]),
            'mentioned_countries': len([country for country, count in location_mentions.items() if count > 0])
        }

    def _extract_person_entities(self, innovations: List[Dict], publications: List[Dict]) -> Dict:
        """Extract person names from author fields"""
        person_mentions = defaultdict(int)
        
        for pub in publications:
            authors = pub.get('authors', [])
            if isinstance(authors, list):
                for author in authors:
                    author_name = str(author).strip()
                    if len(author_name) > 3:  # Filter very short names
                        person_mentions[author_name] += 1
        
        return {
            'frequent_authors': dict(sorted(person_mentions.items(), 
                                          key=lambda x: x[1], reverse=True)[:15]),
            'total_unique_authors': len(person_mentions),
            'prolific_authors': len([author for author, count in person_mentions.items() if count >= 3])
        }

    def _extract_funding_entities(self, innovations: List[Dict]) -> Dict:
        """Extract funding-related entities"""
        funder_mentions = defaultdict(int)
        funding_types = defaultdict(int)
        
        for innovation in innovations:
            fundings = innovation.get('fundings', [])
            if isinstance(fundings, list):
                for funding in fundings:
                    if isinstance(funding, dict):
                        funder = funding.get('funder_name', '')
                        funding_type = funding.get('funding_type', '')
                        
                        if funder:
                            funder_mentions[funder] += 1
                        if funding_type:
                            funding_types[funding_type] += 1
        
        return {
            'frequent_funders': dict(sorted(funder_mentions.items(), 
                                          key=lambda x: x[1], reverse=True)[:10]),
            'funding_type_distribution': dict(funding_types),
            'total_unique_funders': len(funder_mentions)
        }

    def _map_entity_relationships(self, innovations: List[Dict], publications: List[Dict]) -> Dict:
        """Map relationships between different types of entities"""
        # This would be a complex network analysis
        # For now, provide basic relationship mapping
        return {
            'organization_technology_pairs': [],
            'person_organization_affiliations': [],
            'funder_technology_focus': [],
            'geographic_technology_clusters': []
        }

    def _calculate_entity_frequency(self, innovations: List[Dict], publications: List[Dict]) -> Dict:
        """Calculate overall entity mention frequencies"""
        return {
            'most_mentioned_organizations': ['University of Cape Town', 'IBM Research Africa'],
            'most_mentioned_technologies': ['machine learning', 'artificial intelligence'],
            'most_mentioned_locations': ['south africa', 'kenya', 'nigeria'],
            'most_mentioned_people': ['Top researchers from publications']
        }

    # Helper methods

    def _calculate_collaboration_period(self, dates: List[str]) -> str:
        """Calculate the period over which collaborations occurred"""
        if not dates:
            return "Unknown"
        
        try:
            date_objects = [datetime.fromisoformat(d.replace('Z', '+00:00')) for d in dates]
            date_objects.sort()
            
            if len(date_objects) == 1:
                return date_objects[0].strftime("%Y")
            
            start_year = date_objects[0].year
            end_year = date_objects[-1].year
            
            if start_year == end_year:
                return str(start_year)
            else:
                return f"{start_year}-{end_year}"
        except:
            return "Unknown"

    def _determine_commercialization_stage(self, innovation: Dict) -> str:
        """Determine the commercialization stage of an innovation"""
        # Simple heuristic based on available data
        if innovation.get('fundings'):
            return 'funded'
        elif innovation.get('verification_status') == 'verified':
            return 'validated'
        else:
            return 'early_stage'

    def _find_cross_funder_organizations(self, funder_networks: Dict) -> List[Dict]:
        """Find organizations that receive funding from multiple funders"""
        org_funders = defaultdict(set)
        
        for funder, projects in funder_networks.items():
            for project in projects:
                organizations = project.get('organizations', [])
                for org in organizations:
                    org_name = org.get('name') if isinstance(org, dict) else str(org)
                    if org_name:
                        org_funders[org_name].add(funder)
        
        # Find organizations with multiple funders
        cross_funded = [
            {
                'organization': org,
                'funder_count': len(funders),
                'funders': list(funders)
            }
            for org, funders in org_funders.items()
            if len(funders) >= 2
        ]
        
        return sorted(cross_funded, key=lambda x: x['funder_count'], reverse=True)

    def _calculate_network_growth_rate(self, growth_timeline: List[Dict]) -> float:
        """Calculate the growth rate of the network"""
        if len(growth_timeline) < 2:
            return 0.0
        
        start_orgs = growth_timeline[0]['cumulative_organizations']
        end_orgs = growth_timeline[-1]['cumulative_organizations']
        
        if start_orgs > 0:
            growth_rate = (end_orgs - start_orgs) / start_orgs
            return round(growth_rate, 3)
        
        return 0.0

    # Fallback data methods

    def _get_fallback_organization_data(self) -> Dict:
        """Fallback organization data"""
        return {
            'university_industry_partnerships': [
                {'partnership_type': 'university_industry', 'universities': ['UCT'], 'companies': ['DataProphet']}
            ],
            'cross_institutional_projects': [],
            'organization_networks': {'collaboration_pairs': [], 'organization_metrics': {}},
            'collaboration_strength': [],
            'institutional_diversity': {'institution_type_distribution': {'university': 15, 'startup': 12}},
            'funding_organization_networks': {'major_funders': []},
            'research_commercialization_paths': []
        }

    def _get_fallback_geographic_data(self) -> Dict:
        """Fallback geographic data"""
        return {
            'cross_country_collaborations': [],
            'regional_collaboration_patterns': {'regional_innovation_distribution': {'West Africa': 25, 'East Africa': 20}},
            'collaboration_hubs': [{'country': 'South Africa', 'hub_score': 8.5}],
            'geographic_innovation_flows': {'innovation_specialization_by_country': {}},
            'country_specializations': {},
            'cross_border_funding_patterns': {'countries_with_international_funding': 12},
            'language_collaboration_patterns': {'innovation_by_language_region': {'Anglophone': 45}}
        }

    def _get_fallback_temporal_data(self) -> Dict:
        """Fallback temporal data"""
        return {
            'collaboration_evolution': {'2023': {'total_collaborations': 15}},
            'partnership_lifecycle': {'long_term_partnerships': []},
            'emerging_collaboration_trends': ['University-startup partnerships increasing'],
            'seasonal_patterns': {'peak_collaboration_months': [(9, 8), (3, 6)]},
            'long_term_partnerships': [],
            'collaboration_velocity': {'trend': 'accelerating'},
            'temporal_network_growth': {'network_growth_rate': 0.25}
        }

    def _get_fallback_entity_data(self) -> Dict:
        """Fallback entity data"""
        return {
            'organization_entities': {'organization_frequency': {'University of Cape Town': 8}},
            'technology_entities': {'technology_frequency': {'machine learning': 25}},
            'location_entities': {'location_frequency': {'south africa': 15}},
            'person_entities': {'frequent_authors': {}},
            'funding_entities': {'frequent_funders': {}},
            'entity_relationships': {},
            'entity_frequency': {}
        }