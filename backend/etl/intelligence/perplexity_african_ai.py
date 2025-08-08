"""
TAIFA-FIALA Perplexity African AI Intelligence Module
====================================================

Advanced AI-powered intelligence synthesis for African AI innovation discovery.
Uses Perplexity AI to generate comprehensive intelligence reports on African AI ecosystem.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import json
import aiohttp

from services.unified_cache import (
    cache_api_response, get_cached_response, cache_null_response, 
    is_null_cached, DataSource
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntelligenceType(Enum):
    INNOVATION_DISCOVERY = "innovation_discovery"
    FUNDING_LANDSCAPE = "funding_landscape"
    RESEARCH_BREAKTHROUGH = "research_breakthrough"
    POLICY_DEVELOPMENT = "policy_development"
    TALENT_ECOSYSTEM = "talent_ecosystem"
    MARKET_ANALYSIS = "market_analysis"


@dataclass
class IntelligenceReport:
    """Comprehensive intelligence report from Perplexity AI"""
    report_id: str
    report_type: IntelligenceType
    title: str
    summary: str
    key_findings: List[str]
    innovations_mentioned: List[Dict[str, Any]]
    funding_updates: List[Dict[str, Any]]
    policy_developments: List[Dict[str, Any]]
    validation_flags: List[str]
    confidence_score: float
    sources: List[str]
    geographic_focus: List[str]
    follow_up_actions: List[str]
    generation_timestamp: datetime
    time_period_analyzed: str
    # NEW: Structured citations for snowball sampling
    extracted_citations: List[Dict[str, Any]] = None

    def to_json(self) -> str:
        """Convert report to JSON string"""
        data = asdict(self)
        data['generation_timestamp'] = self.generation_timestamp.isoformat()
        data['report_type'] = self.report_type.value
        return json.dumps(data, indent=2)

    def save_report(self, filepath: str):
        """Save report to file"""
        with open(filepath, 'w') as f:
            f.write(self.to_json())


class PerplexityAfricanAIModule:
    """Advanced AI intelligence synthesis using Perplexity API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def synthesize_intelligence(self,
                                    intelligence_types: List[IntelligenceType],
                                    time_period: str = "last_7_days",
                                    geographic_focus: List[str] = None) -> List[IntelligenceReport]:
        """Generate comprehensive intelligence reports"""

        if geographic_focus is None:
            geographic_focus = ["Nigeria", "Kenya", "South Africa", "Ghana", "Egypt", "Morocco", "Rwanda", "Uganda"]

        reports = []

        for intel_type in intelligence_types:
            try:
                report = await self._generate_intelligence_report(intel_type, time_period, geographic_focus)
                reports.append(report)
                logger.info(f"Generated {intel_type.value} report: {report.confidence_score:.2f} confidence")

            except Exception as e:
                logger.error(f"Failed to generate {intel_type.value} report: {e}")

        return reports

    async def _generate_intelligence_report(self,
                                          intel_type: IntelligenceType,
                                          time_period: str,
                                          geographic_focus: List[str]) -> IntelligenceReport:
        """Generate a specific type of intelligence report"""

        prompt = self._create_intelligence_prompt(intel_type, time_period, geographic_focus)

        # Make API call to Perplexity
        response_data = await self._call_perplexity_api(prompt)

        # Parse and structure the response
        report = await self._parse_intelligence_response(response_data, intel_type, time_period, geographic_focus)

        return report

    def _create_intelligence_prompt(self,
                                  intel_type: IntelligenceType,
                                  time_period: str,
                                  geographic_focus: List[str]) -> str:
        """Create targeted prompts for different intelligence types"""

        base_context = f"""
        You are an expert AI researcher specializing in African artificial intelligence innovation.
        Focus on developments in: {', '.join(geographic_focus)}
        Time period: {time_period}

        Provide comprehensive, factual information with specific company names, funding amounts,
        research breakthroughs, and policy developments. Include source URLs when possible.
        """

        if intel_type == IntelligenceType.INNOVATION_DISCOVERY:
            return base_context + """
            MISSION: Discover and analyze recent AI innovations, startups, and breakthrough technologies
            emerging from African countries.

            Please provide:
            1. New AI startups launched or gaining traction
            2. Innovative AI applications and use cases
            3. Technology breakthroughs and product launches
            4. Key founders, researchers, and team information
            5. Technical details about innovations when available
            6. Market traction and early adoption signals

            Format your response with clear sections and specific, verifiable details.
            """

        elif intel_type == IntelligenceType.FUNDING_LANDSCAPE:
            return base_context + """
            MISSION: Analyze investment flows, funding rounds, and financial developments in African AI.

            Please provide:
            1. Recent funding rounds with specific amounts and investors
            2. New venture capital firms or investment initiatives
            3. Government funding programs and grants
            4. International investment in African AI
            5. Valuation trends and market dynamics
            6. Notable acquisitions or partnerships

            Include exact funding amounts, investor names, and deal structures when available.
            """

        elif intel_type == IntelligenceType.RESEARCH_BREAKTHROUGH:
            return base_context + """
            MISSION: Identify cutting-edge AI research, academic publications, and scientific breakthroughs.

            Please provide:
            1. Notable research papers and publications
            2. University research initiatives and labs
            3. International research collaborations
            4. Conference presentations and academic recognition
            5. Open source projects and technical contributions
            6. Research-to-industry translation efforts

            Focus on high-impact research with practical applications.
            """

        elif intel_type == IntelligenceType.POLICY_DEVELOPMENT:
            return base_context + """
            MISSION: Track policy developments, regulatory changes, and government initiatives in AI.

            Please provide:
            1. New AI policies and regulatory frameworks
            2. Government AI strategy announcements
            3. Digital transformation initiatives
            4. International AI cooperation agreements
            5. Data protection and AI ethics developments
            6. Public-private partnership announcements

            Include specific policy details and implementation timelines.
            """

        else:
            return base_context + f"""
            MISSION: Analyze developments related to {intel_type.value} in African AI ecosystem.

            Provide comprehensive analysis with specific examples, key players, and measurable impacts.
            """

    async def _call_perplexity_api(self, prompt: str) -> Dict[str, Any]:
        """Make API call to Perplexity (with caching)"""
        
        # Create cache key parameters
        cache_params = {
            'prompt': prompt,
            'model': "llama-3.1-sonar-large-128k-online",
            'temperature': 0.2,
            'max_tokens': 4000
        }
        
        # Check if response is cached
        try:
            cached_response = await get_cached_response(DataSource.PERPLEXITY, cache_params)
            if cached_response:
                logger.info("Using cached Perplexity response")
                return cached_response
        except Exception as e:
            logger.warning(f"Error checking Perplexity cache: {e}")
        
        # Check if this is a known null result
        try:
            if await is_null_cached(DataSource.PERPLEXITY, cache_params):
                logger.info("Perplexity request cached as null, skipping API call")
                raise Exception("Cached null result - skipping API call")
        except Exception as e:
            logger.warning(f"Error checking null cache: {e}")

        payload = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a precise AI research analyst. Provide factual, well-sourced information with specific details."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 4000
        }

        try:
            async with self.session.post(f"{self.base_url}/chat/completions", json=payload) as response:
                if response.status == 200:
                    response_data = await response.json()
                    
                    # Check if response has meaningful content
                    content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    
                    if len(content.strip()) < 50:
                        # Cache as null if content is too short
                        await cache_null_response(DataSource.PERPLEXITY, cache_params, 
                                                "insufficient_content", 2.0)  # 2 hour cache
                        logger.warning("Perplexity returned insufficient content")
                        return response_data
                    
                    # Cache successful response for 24 hours
                    await cache_api_response(DataSource.PERPLEXITY, cache_params, response_data, 24.0)
                    logger.info("Cached Perplexity response for 24 hours")
                    
                    return response_data
                elif response.status == 429:
                    # Rate limited - cache as null for shorter period
                    await cache_null_response(DataSource.PERPLEXITY, cache_params, 
                                            "rate_limited", 0.5)  # 30 minute cache
                    raise Exception(f"Perplexity API rate limited: {response.status}")
                else:
                    # Other API errors - cache for short period
                    await cache_null_response(DataSource.PERPLEXITY, cache_params, 
                                            "api_error", 1.0)  # 1 hour cache
                    raise Exception(f"Perplexity API error: {response.status}")
                    
        except aiohttp.ClientError as e:
            # Network/client errors - cache for short period
            await cache_null_response(DataSource.PERPLEXITY, cache_params, 
                                    "network_error", 0.5)  # 30 minute cache
            raise Exception(f"Perplexity API network error: {e}")
        except Exception as e:
            # Other errors - don't cache, might be temporary
            logger.error(f"Perplexity API unexpected error: {e}")
            raise

    async def _parse_intelligence_response(self,
                                         response_data: Dict[str, Any],
                                         intel_type: IntelligenceType,
                                         time_period: str,
                                         geographic_focus: List[str]) -> IntelligenceReport:
        """Parse Perplexity response into structured intelligence report"""

        content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')

        # Extract structured data from the response
        findings = await self._extract_structured_findings(content, intel_type)

        # Generate summary and key findings
        summary = self._generate_summary(content, intel_type)
        key_findings = self._extract_key_findings(content)

        # Extract specific entity types
        innovations = self._extract_innovations(findings)
        funding_updates = self._extract_funding_updates(findings)
        policy_developments = self._extract_policy_developments(findings)

        # Extract sources and citations
        sources = self._extract_sources(content)
        
        # NEW: Extract structured citations for snowball sampling
        try:
            from services.citation_extractor import enhance_perplexity_response_with_citations
            enhanced_content, extracted_citations = await enhance_perplexity_response_with_citations(
                content, response_data.get('id', f"perplexity_{datetime.now().isoformat()}")
            )
            logger.info(f"Extracted {len(extracted_citations)} citations for snowball sampling")
        except Exception as e:
            logger.warning(f"Citation extraction failed: {e}")
            extracted_citations = []

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(content, findings)

        # Generate follow-up actions
        follow_up_actions = self._generate_follow_up_actions(intel_type, findings)

        return IntelligenceReport(
            report_id=f"{intel_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            report_type=intel_type,
            title=f"African AI {intel_type.value} synthesis",
            summary=summary,
            key_findings=key_findings,
            innovations_mentioned=innovations,
            funding_updates=funding_updates,
            policy_developments=policy_developments,
            validation_flags=self._generate_validation_flags(findings),
            confidence_score=confidence_score,
            sources=list(set(sources)),  # Deduplicate sources
            geographic_focus=geographic_focus,
            follow_up_actions=follow_up_actions,
            generation_timestamp=datetime.now(),
            time_period_analyzed=time_period,
            extracted_citations=extracted_citations or []
        )

    def _generate_follow_up_actions(self, intel_type: IntelligenceType, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable follow-up items based on findings"""

        actions = []

        if intel_type == IntelligenceType.INNOVATION_DISCOVERY:
            for innovation in [f for f in findings if f.get('type') == 'innovation_discovery']:
                if 'company_name' in innovation:
                    actions.append(f"Deep crawl {innovation['company_name']} for technical details and team information")
                    actions.append(f"Cross-reference {innovation['company_name']} against GitHub and LinkedIn for validation")

        elif intel_type == IntelligenceType.FUNDING_LANDSCAPE:
            actions.append("Verify funding amounts through multiple sources")
            actions.append("Contact startups directly for validation of funding claims")
            actions.append("Track funding impact on innovation development milestones")

        elif intel_type == IntelligenceType.RESEARCH_BREAKTHROUGH:
            actions.append("Extract full paper details for academic validation")
            actions.append("Map research collaboration networks")
            actions.append("Track citation patterns and research impact")

        return actions

    def _generate_validation_flags(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate validation flags for quality assurance"""

        flags = []

        # Check for unverified claims
        for finding in findings:
            if 'funding_amount' in finding and not finding.get('source_verified'):
                flags.append(f"Unverified funding claim: {finding.get('funding_amount')}")

            if 'company_name' in finding and not finding.get('website_verified'):
                flags.append(f"Company website needs verification: {finding.get('company_name')}")

        # Check for missing critical information
        innovation_count = len([f for f in findings if f.get('type') == 'innovation_discovery'])
        if innovation_count == 0:
            flags.append("No innovation discoveries found - may need broader search")

        return flags

    async def cross_validate_with_sources(self, report: IntelligenceReport) -> IntelligenceReport:
        """Cross-validate report findings with additional sources"""

        validated_innovations = []

        for innovation in report.innovations_mentioned:
            if 'company_name' in innovation:
                # Try to validate company existence and details
                validation_result = await self._validate_company_info(innovation['company_name'])
                innovation['validation_result'] = validation_result
                validated_innovations.append(innovation)

        # Update report with validation results
        report.innovations_mentioned = validated_innovations

        # Recalculate confidence score based on validation
        validated_count = sum(1 for inv in validated_innovations
                            if inv.get('validation_result', {}).get('validated', False))
        if validated_innovations:
            validation_boost = (validated_count / len(validated_innovations)) * 0.2
            report.confidence_score = min(1.0, report.confidence_score + validation_boost)

        return report

    async def _validate_company_info(self, company_name: str) -> Dict[str, Any]:
        """Validate company information through web search"""

        try:
            # Simple validation through search
            search_prompt = f"Verify the existence of AI company '{company_name}' in Africa. Provide website, location, and key details."

            response_data = await self._call_perplexity_api(search_prompt)
            content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')

            return {
                'validated': len(content) > 100,  # Basic validation
                'details': content[:200],
                'validation_timestamp': datetime.now()
            }

        except Exception as e:
            return {
                'validated': False,
                'error': str(e),
                'validation_timestamp': datetime.now()
            }

    async def generate_trend_analysis(self, reports: List[IntelligenceReport]) -> Dict[str, Any]:
        """Generate trend analysis across multiple intelligence reports"""

        trend_analysis = {
            'analysis_timestamp': datetime.now(),
            'reports_analyzed': len(reports),
            'time_span': self._calculate_time_span(reports),
            'geographic_coverage': list(set().union(*[r.geographic_focus for r in reports])),
            'funding_trends': self._analyze_funding_trends(reports),
            'innovation_hotspots': self._analyze_geographic_trends(reports),
            'emerging_themes': self._extract_emerging_themes(reports),
            'recommendations': self._generate_trend_recommendations(reports)
        }

        return trend_analysis

    def _calculate_time_span(self, reports: List[IntelligenceReport]) -> Dict[str, Any]:
        """Calculate time span covered by reports"""

        timestamps = [r.generation_timestamp for r in reports]

        return {
            'earliest_report': min(timestamps),
            'latest_report': max(timestamps),
            'total_days': (max(timestamps) - min(timestamps)).days
        }

    def _analyze_funding_trends(self, reports: List[IntelligenceReport]) -> Dict[str, Any]:
        """Analyze funding patterns across reports"""

        # This would implement more sophisticated funding analysis
        return {
            'total_funding_mentioned': 0,  # Would calculate from actual data
            'average_deal_size': 0,
            'most_active_investors': []
        }

    def _analyze_geographic_trends(self, reports: List[IntelligenceReport]) -> Dict[str, Any]:
        """Analyze geographic distribution of innovations"""

        country_mentions = {}
        for report in reports:
            for country in report.geographic_focus:
                country_mentions[country] = country_mentions.get(country, 0) + 1

        return {
            'most_active_countries': sorted(country_mentions.items(),
                                          key=lambda x: x[1], reverse=True)[:5],
            'geographic_distribution': country_mentions
        }

    def _generate_trend_recommendations(self, reports: List[IntelligenceReport]) -> List[str]:
        """Generate strategic recommendations based on trends"""

        recommendations = [
            "Focus data collection on emerging innovation hotspots",
            "Increase monitoring frequency for high-activity regions",
            "Develop deeper validation pipelines for funding claims"
        ]

        return recommendations
    
    async def _extract_structured_findings(self, content: str, intel_type: IntelligenceType) -> List[Dict[str, Any]]:
        """Extract structured findings from content"""
        findings = []
        
        # Split content into paragraphs for analysis
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        for paragraph in paragraphs:
            if len(paragraph) > 50:  # Skip very short paragraphs
                finding = {
                    'type': intel_type.value,
                    'content': paragraph,
                    'extracted_at': datetime.now().isoformat()
                }
                
                # Extract entities based on intelligence type
                if intel_type == IntelligenceType.INNOVATION_DISCOVERY:
                    finding.update(self._extract_innovation_entities(paragraph))
                elif intel_type == IntelligenceType.FUNDING_LANDSCAPE:
                    finding.update(self._extract_funding_entities(paragraph))
                elif intel_type == IntelligenceType.RESEARCH_BREAKTHROUGH:
                    finding.update(self._extract_research_entities(paragraph))
                
                findings.append(finding)
        
        return findings
    
    def _generate_summary(self, content: str, intel_type: IntelligenceType) -> str:
        """Generate summary from content"""
        # Simple extractive summary - take first few sentences
        sentences = content.split('. ')
        if len(sentences) > 3:
            summary = '. '.join(sentences[:3]) + '.'
        else:
            summary = content[:200] + '...' if len(content) > 200 else content
        
        return summary.strip()
    
    def _extract_key_findings(self, content: str) -> List[str]:
        """Extract key findings from content"""
        findings = []
        
        # Look for numbered lists or bullet points
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if (line.startswith(('1.', '2.', '3.', '•', '-', '*')) and 
                len(line) > 10 and len(line) < 200):
                # Clean up the finding
                clean_finding = line.lstrip('123456789.•-* ').strip()
                if clean_finding:
                    findings.append(clean_finding)
        
        # If no structured findings, extract important sentences
        if not findings:
            import re
            sentences = re.split(r'[.!?]+', content)
            for sentence in sentences[:5]:  # Take first 5 sentences
                sentence = sentence.strip()
                if (len(sentence) > 20 and len(sentence) < 200 and
                    any(keyword in sentence.lower() for keyword in ['ai', 'innovation', 'startup', 'funding', 'research'])):
                    findings.append(sentence)
        
        return findings[:10]  # Limit to 10 findings
    
    def _extract_innovations(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract innovation mentions from findings"""
        innovations = []
        
        for finding in findings:
            if finding.get('type') in ['innovation_discovery', 'startup_mention']:
                innovation = {
                    'company_name': finding.get('company_name', ''),
                    'description': finding.get('content', '')[:200],
                    'location': finding.get('location', ''),
                    'confidence': finding.get('confidence_score', 0.7)
                }
                
                # Only add if we have a company name
                if innovation['company_name']:
                    innovations.append(innovation)
        
        return innovations
    
    def _extract_funding_updates(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract funding updates from findings"""
        funding_updates = []
        
        for finding in findings:
            if finding.get('type') == 'funding_landscape' or finding.get('funding_amount'):
                update = {
                    'company': finding.get('company_name', ''),
                    'amount': finding.get('funding_amount', ''),
                    'investors': finding.get('investors', []),
                    'round_type': finding.get('round_type', ''),
                    'description': finding.get('content', '')[:200]
                }
                
                # Only add if we have funding information
                if update['amount'] or update['investors']:
                    funding_updates.append(update)
        
        return funding_updates
    
    def _extract_policy_developments(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract policy developments from findings"""
        policy_developments = []
        
        for finding in findings:
            if (finding.get('type') == 'policy_development' or 
                any(keyword in finding.get('content', '').lower() 
                    for keyword in ['policy', 'regulation', 'government', 'law'])):
                
                development = {
                    'title': finding.get('policy_title', ''),
                    'description': finding.get('content', '')[:200],
                    'country': finding.get('country', ''),
                    'type': finding.get('policy_type', 'regulation')
                }
                
                policy_developments.append(development)
        
        return policy_developments
    
    def _extract_sources(self, content: str) -> List[str]:
        """Extract source URLs from content"""
        import re
        
        # Look for URLs in the content
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'  
        urls = re.findall(url_pattern, content)
        
        # Clean and deduplicate
        clean_urls = []
        for url in urls:
            # Remove trailing punctuation
            url = url.rstrip('.,;:!?")')
            if url not in clean_urls and len(url) > 10:
                clean_urls.append(url)
        
        return clean_urls[:20]  # Limit to 20 sources
    
    def _extract_innovation_entities(self, text: str) -> Dict[str, Any]:
        """Extract innovation-specific entities from text"""
        import re
        
        entities = {}
        
        # Look for company names (capitalized words)
        company_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        potential_companies = re.findall(company_pattern, text)
        
        # Filter for likely company names (basic heuristic)
        for company in potential_companies:
            if (len(company.split()) <= 3 and 
                any(keyword in text.lower() for keyword in ['startup', 'company', 'founded', 'launched'])):
                entities['company_name'] = company
                break
        
        # Look for locations
        african_countries = ['Nigeria', 'Kenya', 'South Africa', 'Ghana', 'Egypt', 
                           'Morocco', 'Rwanda', 'Uganda', 'Tanzania', 'Senegal']
        for country in african_countries:
            if country in text:
                entities['location'] = country
                break
        
        return entities
    
    def _extract_funding_entities(self, text: str) -> Dict[str, Any]:
        """Extract funding-specific entities from text"""
        import re
        
        entities = {}
        
        # Look for funding amounts
        funding_pattern = r'\$([\d,]+(?:\.\d+)?)\s*(million|billion|M|B)'
        funding_match = re.search(funding_pattern, text, re.IGNORECASE)
        
        if funding_match:
            entities['funding_amount'] = funding_match.group(0)
        
        # Look for round types
        round_pattern = r'(seed|series [A-Z]|pre-seed|bridge|debt)\s+(?:funding|round)'
        round_match = re.search(round_pattern, text, re.IGNORECASE)
        
        if round_match:
            entities['round_type'] = round_match.group(1)
        
        # Look for investors
        if 'investor' in text.lower():
            # Simple extraction - could be improved
            entities['investors'] = ['Investment firm mentioned']
        
        return entities
    
    def _extract_research_entities(self, text: str) -> Dict[str, Any]:
        """Extract research-specific entities from text"""
        entities = {}
        
        # Look for universities
        if 'university' in text.lower():
            import re
            uni_pattern = r'University of [A-Z][a-z]+'
            uni_match = re.search(uni_pattern, text)
            if uni_match:
                entities['institution'] = uni_match.group(0)
        
        # Look for research topics
        research_keywords = ['machine learning', 'artificial intelligence', 'deep learning', 
                           'computer vision', 'nlp', 'robotics']
        for keyword in research_keywords:
            if keyword in text.lower():
                entities['research_area'] = keyword
                break
        
        return entities
    
    def _calculate_confidence_score(self, content: str, findings: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for intelligence report"""
        base_score = 0.5
        
        # Boost score for content length (more content = higher confidence)
        if len(content) > 1000:
            base_score += 0.1
        elif len(content) > 500:
            base_score += 0.05
        
        # Boost score for structured findings
        if len(findings) > 3:
            base_score += 0.15
        elif len(findings) > 1:
            base_score += 0.1
        
        # Boost score for specific entity mentions
        entity_types = set()
        for finding in findings:
            if finding.get('company_name'):
                entity_types.add('company')
            if finding.get('funding_amount'):
                entity_types.add('funding')
            if finding.get('location'):
                entity_types.add('location')
        
        base_score += len(entity_types) * 0.05
        
        # Boost score for URLs/sources
        url_count = content.lower().count('http')
        if url_count > 0:
            base_score += min(0.1, url_count * 0.02)
        
        return min(1.0, base_score)
    
    def _extract_emerging_themes(self, reports: List[IntelligenceReport]) -> List[str]:
        """Extract emerging themes from multiple reports"""
        themes = []
        
        # Combine all key findings
        all_findings = []
        for report in reports:
            all_findings.extend(report.key_findings)
        
        # Simple theme extraction - look for common keywords
        theme_keywords = ['blockchain', 'fintech', 'healthtech', 'agritech', 
                         'edtech', 'climate', 'sustainability', 'mobile', 'payments']
        
        for keyword in theme_keywords:
            if any(keyword in finding.lower() for finding in all_findings):
                themes.append(keyword.title())
        
        return themes[:10]  # Top 10 themes
    
    def to_json(self) -> str:
        """Convert trend analysis to JSON"""
        return json.dumps(self, indent=2, default=str)
    
    def save_report(self, filepath: str):
        """Save trend analysis to file"""
        with open(filepath, 'w') as f:
            f.write(self.to_json())


async def main():
    """Test the Perplexity African AI module"""

    import os

    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("Please set PERPLEXITY_API_KEY environment variable")
        return

    print("🤖 Testing Perplexity African AI Intelligence Module")

    async with PerplexityAfricanAIModule(api_key) as intel_module:

        # Generate intelligence reports
        reports = await intel_module.synthesize_intelligence(
            intelligence_types=[
                IntelligenceType.INNOVATION_DISCOVERY,
                IntelligenceType.FUNDING_LANDSCAPE
            ],
            time_period='last_7_days',
            geographic_focus=['Nigeria', 'Kenya', 'South Africa']
        )

        print(f"\n📊 Generated {len(reports)} intelligence reports")

        for report in reports:
            print(f"\n📋 Report: {report.report_type.value}")
            print(f"   Title: {report.title}")
            print(f"   Confidence: {report.confidence_score:.2f}")
            print(f"   Key findings: {len(report.key_findings)}")
            print(f"   Innovations: {len(report.innovations_mentioned)}")
            print(f"   Sources: {len(report.sources)}")

            # Cross-validate
            validated_report = await intel_module.cross_validate_with_sources(report)
            print(f"   Post-validation confidence: {validated_report.confidence_score:.2f}")

        # Generate trend analysis
        if reports:
            trends = await intel_module.generate_trend_analysis(reports)
            print(f"\n📈 Trend Analysis:")
            print(f"   Time span: {trends['time_span']['total_days']} days")
            print(f"   Geographic coverage: {len(trends['geographic_coverage'])} countries")
            print(f"   Recommendations: {len(trends['recommendations'])}")


if __name__ == "__main__":
    asyncio.run(main())


# Additional helper methods that were in the corrupted portion

def _map_json_to_result(data: Dict[str, Any]) -> Dict[str, Any]:
    """Map JSON response to structured result"""

    mapped_result = {
        'type': 'intelligence_synthesis',
        'timestamp': datetime.now(),
        'raw_data': data
    }

    # Extract structured information
    if 'content' in data:
        content = data['content']

        # Look for funding information
        if any(keyword in content.lower() for keyword in ['funding', 'investment', 'raised', 'million', 'series']):
            mapped_result['funding_signals'] = True

        # Look for innovation signals
        if any(keyword in content.lower() for keyword in ['ai', 'artificial intelligence', 'machine learning', 'startup']):
            mapped_result['innovation_signals'] = True

        # Look for research signals
        if any(keyword in content.lower() for keyword in ['research', 'university', 'paper', 'study']):
            mapped_result['research_signals'] = True

    return mapped_result


def _pattern_based_extraction(content: str, extraction_type: str) -> Dict[str, Any]:
    """Extract information using pattern matching"""

    import re

    extracted = {
        'extraction_type': extraction_type,
        'patterns_found': [],
        'entities': []
    }

    if extraction_type == 'funding':
        # Look for funding patterns
        funding_patterns = [
            r'\$(\d+(?:\.\d+)?)\s*(million|billion|M|B)',
            r'raised\s+\$?(\d+(?:\.\d+)?)\s*(million|billion|M|B)',
            r'funding\s+of\s+\$?(\d+(?:\.\d+)?)\s*(million|billion|M|B)'
        ]

        for pattern in funding_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                extracted['patterns_found'].append({
                    'pattern': pattern,
                    'match': match.group(),
                    'amount': match.group(1),
                    'unit': match.group(2)
                })

    return extracted


def _extract_github_patterns(content: str) -> List[Dict[str, Any]]:
    """Extract GitHub-related patterns"""

    import re

    github_patterns = [
        r'github\.com/([^/\s]+/[^/\s]+)',
        r'open[- ]?source',
        r'repository',
        r'code[- ]?base'
    ]

    github_findings = []

    for pattern in github_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            github_findings.append({
                'pattern': pattern,
                'match': match.group(),
                'context': content[max(0, match.start()-50):match.end()+50]
            })

    return github_findings


def _extract_research_patterns(content: str) -> List[Dict[str, Any]]:
    """Extract research-related patterns"""

    import re

    research_patterns = [
        r'university\s+of\s+\w+',
        r'research\s+paper',
        r'published\s+in',
        r'conference\s+on',
        r'journal\s+of'
    ]

    research_findings = []

    for pattern in research_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            research_findings.append({
                'pattern': pattern,
                'match': match.group(),
                'context': content[max(0, match.start()-50):match.end()+50]
            })

    return research_findings


def _extract_startup_patterns(content: str) -> List[Dict[str, Any]]:
    """Extract startup-related patterns"""

    import re

    startup_patterns = [
        r'startup\s+\w+',
        r'founded\s+by',
        r'co-?founder',
        r'entrepreneur',
        r'launched\s+in\s+\d{4}'
    ]

    startup_findings = []

    for pattern in startup_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            startup_findings.append({
                'pattern': pattern,
                'match': match.group(),
                'context': content[max(0, match.start()-50):match.end()+50]
            })

    return startup_findings


def _merge_pattern_data(github_data: List[Dict], research_data: List[Dict],
                       startup_data: List[Dict]) -> Dict[str, Any]:
    """Merge different pattern extraction results"""

    merged = {
        'github_signals': len(github_data),
        'research_signals': len(research_data),
        'startup_signals': len(startup_data),
        'total_signals': len(github_data) + len(research_data) + len(startup_data),
        'detailed_findings': {
            'github': github_data,
            'research': research_data,
            'startup': startup_data
        }
    }

    return merged


async def _follow_related_links(result: Any, content_type: Any, max_depth: int) -> Dict[str, Any]:
    """Follow related links for additional context"""

    additional_data = {
        'followed_links': [],
        'additional_context': [],
        'extraction_depth': max_depth
    }

    # This would implement actual link following logic
    # For now, return placeholder data

    return additional_data


def _merge_extraction_data(primary_data: Any, additional_data: Dict[str, Any]) -> Any:
    """Merge primary extraction data with additional context"""

    # This would implement sophisticated data merging
    # For now, just return the primary data

    if hasattr(primary_data, 'additional_context'):
        primary_data.additional_context = additional_data.get('additional_context', [])

    return primary_data


def _calculate_completeness_score(extracted_data: Any) -> float:
    """Calculate data completeness score"""

    score = 0.0
    max_score = 1.0

    # Check for required fields
    if hasattr(extracted_data, 'url') and extracted_data.url:
        score += 0.2

    if hasattr(extracted_data, 'content_type') and extracted_data.content_type:
        score += 0.2

    if hasattr(extracted_data, 'success') and extracted_data.success:
        score += 0.3

    if hasattr(extracted_data, 'structured_data') and extracted_data.structured_data:
        score += 0.3

    return min(score, max_score)


def _calculate_confidence_score(extracted_data: Any, result: Any) -> float:
    """Calculate confidence score for extraction"""

    base_score = 0.5

    # Boost score based on successful extraction
    if hasattr(extracted_data, 'success') and extracted_data.success:
        base_score += 0.3

    # Boost score based on data richness
    if hasattr(extracted_data, 'structured_data') and extracted_data.structured_data:
        data_richness = len(str(extracted_data.structured_data)) / 1000  # Normalize
        base_score += min(0.2, data_richness)

    return min(1.0, base_score)


def _generate_validation_flags(extracted_data: Any) -> List[str]:
    """Generate validation flags for extracted data"""

    flags = []

    if not hasattr(extracted_data, 'success') or not extracted_data.success:
        flags.append("Extraction failed")

    if hasattr(extracted_data, 'url') and not extracted_data.url:
        flags.append("Missing URL")

    if hasattr(extracted_data, 'structured_data') and not extracted_data.structured_data:
        flags.append("No structured data extracted")

    return flags


def to_json(obj: Any) -> str:
    """Convert object to JSON string"""
    if hasattr(obj, '__dict__'):
        return json.dumps(obj.__dict__, indent=2, default=str)
    else:
        return json.dumps(obj, indent=2, default=str)


def save_extraction(obj: Any, filepath: str):
    """Save extraction to file"""
    with open(filepath, 'w') as f:
        f.write(to_json(obj))


async def main():
    """Test main function"""
    print("🧪 Testing perplexity_african_ai module")

    # Test pattern extraction
    test_content = """
    Nigerian startup Flutterwave raised $250 million in Series C funding.
    The company was founded by Olugbenga Agboola and is based in Lagos.
    Their open source project is available on github.com/flutterwave/flutterwave.
    Research from University of Lagos shows promising results.
    """

    github_patterns = _extract_github_patterns(test_content)
    research_patterns = _extract_research_patterns(test_content)
    startup_patterns = _extract_startup_patterns(test_content)

    merged_data = _merge_pattern_data(github_patterns, research_patterns, startup_patterns)

    print(f"✅ Pattern extraction test completed")
    print(f"   GitHub signals: {merged_data['github_signals']}")
    print(f"   Research signals: {merged_data['research_signals']}")
    print(f"   Startup signals: {merged_data['startup_signals']}")
    print(f"   Total signals: {merged_data['total_signals']}")
