#!/usr/bin/env python3
"""
Funding and Market Sizing Data Gap Analysis
===========================================

This script provides a comprehensive analysis of the current funding and market sizing
data completeness issues in the TAIFA-FIALA database.

Analysis includes:
1. Publication funding information gaps (target: reduce from 68% missing)
2. Innovation market sizing gaps (target: reduce from 87% missing)
3. Identification of records suitable for AI backfill
4. Recommendations for enrichment strategies
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import json

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from config.database import get_supabase
from scripts.examples.enhanced_funding_extractor import EnhancedFundingExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FundingGapAnalyzer:
    """Analyzes funding and market sizing data gaps"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.funding_extractor = EnhancedFundingExtractor()
        self.analysis_results = {}
    
    async def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run complete funding and market sizing gap analysis"""
        
        logger.info("🔍 Starting Comprehensive Funding Gap Analysis")
        logger.info("=" * 60)
        
        # Analyze publications funding gaps
        pub_analysis = await self._analyze_publication_funding_gaps()
        
        # Analyze innovations market sizing gaps
        innovation_analysis = await self._analyze_innovation_market_gaps()
        
        # Identify backfill opportunities
        backfill_opportunities = await self._identify_backfill_opportunities()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            pub_analysis, innovation_analysis, backfill_opportunities
        )
        
        self.analysis_results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "publication_funding_gaps": pub_analysis,
            "innovation_market_gaps": innovation_analysis,
            "backfill_opportunities": backfill_opportunities,
            "recommendations": recommendations,
            "summary": self._generate_summary()
        }
        
        return self.analysis_results
    
    async def _analyze_publication_funding_gaps(self) -> Dict[str, Any]:
        """Analyze funding information gaps in publications"""
        
        logger.info("📚 Analyzing Publication Funding Gaps...")
        
        try:
            # Get all publications
            response = self.supabase.table("publications").select("*").execute()
            publications = response.data if response.data else []
            
            total_publications = len(publications)
            funding_present = 0
            funding_extractable = 0
            funding_details = []
            
            for pub in publications:
                # Check if funding info already exists
                has_funding = bool(pub.get("fundings") and len(pub.get("fundings", [])) > 0)
                
                if has_funding:
                    funding_present += 1
                    continue
                
                # Check if funding can be extracted from content
                full_text = f"{pub.get('title', '')} {pub.get('abstract', '')} {pub.get('content', '')}"
                
                if len(full_text) > 50:  # Ensure there's meaningful content
                    funding_info = self.funding_extractor.extract_funding_info(full_text)
                    
                    # Check if extraction found meaningful funding data
                    has_extractable_funding = (
                        funding_info.get('funding_type') != 'per_project_range' or
                        funding_info.get('total_funding_pool') or
                        funding_info.get('exact_amount_per_project') or
                        (funding_info.get('min_amount_per_project') and funding_info.get('max_amount_per_project'))
                    )
                    
                    if has_extractable_funding:
                        funding_extractable += 1
                        funding_details.append({
                            "publication_id": pub.get("id"),
                            "title": pub.get("title", "")[:100],
                            "extracted_funding": funding_info,
                            "confidence": "medium"
                        })
            
            funding_missing = total_publications - funding_present
            funding_gap_percentage = (funding_missing / total_publications * 100) if total_publications > 0 else 0
            
            return {
                "total_publications": total_publications,
                "publications_with_funding": funding_present,
                "publications_missing_funding": funding_missing,
                "funding_gap_percentage": round(funding_gap_percentage, 1),
                "publications_with_extractable_funding": funding_extractable,
                "potential_recovery_rate": round((funding_extractable / funding_missing * 100) if funding_missing > 0 else 0, 1),
                "sample_extractable_funding": funding_details[:5]  # Show first 5 examples
            }
            
        except Exception as e:
            logger.error(f"Error analyzing publication funding gaps: {e}")
            return {"error": str(e)}
    
    async def _analyze_innovation_market_gaps(self) -> Dict[str, Any]:
        """Analyze market sizing gaps in innovations - REALISTIC ASSESSMENT"""
        
        logger.info("💡 Analyzing Innovation Market Sizing Gaps... (Realistic Assessment)")
        
        try:
            # Get all innovations
            response = self.supabase.table("innovations").select("*").execute()
            innovations = response.data if response.data else []
            
            total_innovations = len(innovations)
            market_sizing_present = 0
            potential_sources = {
                "has_business_plan_url": 0,
                "has_pitch_deck_url": 0, 
                "has_investment_docs": 0,
                "has_detailed_description": 0,
                "has_revenue_model": 0,
                "is_funded_startup": 0  # Funded startups might have disclosed market size
            }
            market_indicators = []
            
            for innovation in innovations:
                # Check if market sizing already exists
                has_market_sizing = bool(innovation.get("market_sizing"))
                
                if has_market_sizing:
                    market_sizing_present += 1
                    continue
                
                # Identify realistic sources for market data
                has_funding = bool(innovation.get("fundings") and len(innovation.get("fundings", [])) > 0)
                description = innovation.get("description", "")
                
                # Check for potential market data sources
                if has_funding:
                    potential_sources["is_funded_startup"] += 1
                    
                if len(description) > 500:  # Detailed descriptions might contain business model info
                    potential_sources["has_detailed_description"] += 1
                    
                # Look for business model indicators in description
                business_indicators = [
                    "revenue model", "business model", "monetization", "pricing", 
                    "customers", "market size", "addressable market", "target market",
                    "million users", "billion market", "market opportunity"
                ]
                
                description_lower = description.lower()
                has_business_indicators = any(indicator in description_lower for indicator in business_indicators)
                
                if has_business_indicators:
                    potential_sources["has_revenue_model"] += 1
                    market_indicators.append({
                        "innovation_id": innovation.get("id"),
                        "title": innovation.get("title", "")[:100],
                        "has_funding": has_funding,
                        "description_length": len(description),
                        "business_indicators_found": has_business_indicators,
                        "confidence": "low"  # Realistic expectation
                    })
            
            market_missing = total_innovations - market_sizing_present
            market_gap_percentage = (market_missing / total_innovations * 100) if total_innovations > 0 else 0
            
            # Realistic recovery estimate - much lower
            realistic_recovery_count = potential_sources["is_funded_startup"] + (potential_sources["has_revenue_model"] // 3)
            realistic_recovery_rate = (realistic_recovery_count / market_missing * 100) if market_missing > 0 else 0
            
            return {
                "total_innovations": total_innovations,
                "innovations_with_market_sizing": market_sizing_present,
                "innovations_missing_market_sizing": market_missing,
                "market_gap_percentage": round(market_gap_percentage, 1),
                "realistic_assessment": {
                    "note": "Market sizing data is typically in confidential business plans/pitch decks",
                    "funded_startups_with_potential": potential_sources["is_funded_startup"],
                    "innovations_with_business_indicators": potential_sources["has_revenue_model"],
                    "realistic_recovery_estimate": realistic_recovery_count,
                    "realistic_recovery_rate": round(realistic_recovery_rate, 1)
                },
                "alternative_data_sources": {
                    "funded_startups": "May have disclosed market size during funding rounds",
                    "detailed_descriptions": "Some contain business model information", 
                    "sector_estimates": "Use industry-wide market size estimates",
                    "company_websites": "About pages sometimes mention market opportunity"
                },
                "sample_potential_candidates": market_indicators[:5]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing innovation market gaps: {e}")
            return {"error": str(e)}
    
    async def _identify_backfill_opportunities(self) -> Dict[str, Any]:
        """Identify records most suitable for AI backfill"""
        
        logger.info("🤖 Identifying AI Backfill Opportunities...")
        
        backfill_candidates = []
        
        try:
            # Get recent innovations without comprehensive funding/market data
            response = self.supabase.table("innovations").select("*").limit(200).execute()
            innovations = response.data if response.data else []
            
            high_priority = []
            medium_priority = []
            low_priority = []
            
            for innovation in innovations:
                # Determine backfill priority
                has_funding = bool(innovation.get("fundings") and len(innovation.get("fundings", [])) > 0)
                has_market_sizing = bool(innovation.get("market_sizing"))
                has_description = bool(innovation.get("description") and len(innovation.get("description", "")) > 100)
                is_verified = innovation.get("verification_status") == "verified"
                
                missing_fields = []
                if not has_funding:
                    missing_fields.append("funding")
                if not has_market_sizing:
                    missing_fields.append("market_sizing")
                
                if missing_fields and has_description:
                    candidate = {
                        "innovation_id": innovation.get("id"),
                        "title": innovation.get("title", "")[:100],
                        "missing_fields": missing_fields,
                        "description_length": len(innovation.get("description", "")),
                        "verification_status": innovation.get("verification_status", "pending"),
                        "estimated_backfill_success_rate": 0.7 if is_verified else 0.5
                    }
                    
                    # Categorize by priority
                    if is_verified and len(missing_fields) >= 2:
                        high_priority.append(candidate)
                    elif has_description and len(missing_fields) >= 1:
                        medium_priority.append(candidate)
                    else:
                        low_priority.append(candidate)
            
            return {
                "total_backfill_candidates": len(high_priority) + len(medium_priority) + len(low_priority),
                "high_priority": len(high_priority),
                "medium_priority": len(medium_priority),
                "low_priority": len(low_priority),
                "estimated_processing_time_hours": (len(high_priority) * 0.1) + (len(medium_priority) * 0.05),
                "estimated_cost_usd": (len(high_priority) * 0.15) + (len(medium_priority) * 0.08),
                "sample_high_priority": high_priority[:3],
                "sample_medium_priority": medium_priority[:3]
            }
            
        except Exception as e:
            logger.error(f"Error identifying backfill opportunities: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, pub_analysis: Dict, innovation_analysis: Dict, backfill_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analysis"""
        
        recommendations = []
        
        # Publication funding recommendations
        if pub_analysis.get("funding_gap_percentage", 0) > 50:
            recommendations.append({
                "priority": "HIGH",
                "category": "Publication Funding",
                "action": "Activate AI backfill for publications with extractable funding data",
                "impact": f"Could recover funding data for {pub_analysis.get('publications_with_extractable_funding', 0)} publications",
                "effort": "Medium",
                "timeline": "1-2 weeks"
            })
        
        # Innovation market sizing recommendations - REALISTIC
        realistic_assessment = innovation_analysis.get("realistic_assessment", {})
        if innovation_analysis.get("market_gap_percentage", 0) > 70:
            recommendations.append({
                "priority": "MEDIUM",  # Lowered from CRITICAL
                "category": "Innovation Market Sizing (Realistic Approach)",
                "action": "Apply sector proxy estimates and analyze funded startups for business model data",
                "impact": f"Could provide market context for ~{realistic_assessment.get('realistic_recovery_rate', 20):.0f}% of innovations via sector estimates",
                "effort": "Medium",
                "timeline": "3-6 weeks",
                "note": "Market sizing data (TAM/SAM/SOM) is typically in confidential business plans - using realistic alternatives"
            })
        
        # AI Backfill recommendations
        if backfill_analysis.get("high_priority", 0) > 0:
            recommendations.append({
                "priority": "HIGH",
                "category": "AI Backfill",
                "action": "Process high-priority backfill candidates immediately",
                "impact": f"Complete data for {backfill_analysis.get('high_priority', 0)} verified innovations",
                "effort": "Low",
                "timeline": "3-5 days",
                "cost": f"~${backfill_analysis.get('estimated_cost_usd', 0):.2f}"
            })
        
        # Intelligence gathering recommendations
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Intelligence Gathering",
            "action": "Enable scheduled market analysis intelligence",
            "impact": "Continuous market sizing data collection",
            "effort": "Low",
            "timeline": "1 day"
        })
        
        return recommendations
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate executive summary of analysis"""
        
        pub_analysis = self.analysis_results.get("publication_funding_gaps", {})
        innovation_analysis = self.analysis_results.get("innovation_market_gaps", {})
        backfill_analysis = self.analysis_results.get("backfill_opportunities", {})
        
        return {
            "current_funding_gap_severity": "CRITICAL" if pub_analysis.get("funding_gap_percentage", 0) > 60 else "HIGH",
            "current_market_gap_severity": "CRITICAL" if innovation_analysis.get("market_gap_percentage", 0) > 80 else "HIGH",
            "immediate_recovery_potential": {
                "funding_data_recoverable": pub_analysis.get("publications_with_extractable_funding", 0),
                "market_data_recoverable": innovation_analysis.get("innovations_with_extractable_market_data", 0)
            },
            "recommended_immediate_actions": [
                "Activate funding enrichment solutions",
                "Process high-priority AI backfill queue",
                "Deploy enhanced extraction patterns"
            ],
            "expected_improvement_timeline": "2-4 weeks for significant gap reduction"
        }
    
    def save_analysis(self, filepath: str = None):
        """Save analysis results to file"""
        
        if not filepath:
            filepath = f"funding_gap_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filepath, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        
        logger.info(f"💾 Analysis results saved to: {filepath}")


async def main():
    """Main analysis script"""
    
    analyzer = FundingGapAnalyzer()
    
    try:
        # Run comprehensive analysis
        results = await analyzer.run_comprehensive_analysis()
        
        # Display results
        logger.info("📊 FUNDING GAP ANALYSIS COMPLETE")
        logger.info("=" * 60)
        
        # Publication funding gaps
        pub_gaps = results["publication_funding_gaps"]
        logger.info("📚 PUBLICATION FUNDING GAPS:")
        logger.info(f"   Total Publications: {pub_gaps.get('total_publications', 0)}")
        logger.info(f"   Missing Funding Data: {pub_gaps.get('publications_missing_funding', 0)} ({pub_gaps.get('funding_gap_percentage', 0)}%)")
        logger.info(f"   Extractable Funding Data: {pub_gaps.get('publications_with_extractable_funding', 0)} ({pub_gaps.get('potential_recovery_rate', 0)}% recovery potential)")
        
        # Innovation market gaps
        innovation_gaps = results["innovation_market_gaps"]
        logger.info(f"\n💡 INNOVATION MARKET SIZING GAPS:")
        logger.info(f"   Total Innovations: {innovation_gaps.get('total_innovations', 0)}")
        logger.info(f"   Missing Market Data: {innovation_gaps.get('innovations_missing_market_sizing', 0)} ({innovation_gaps.get('market_gap_percentage', 0)}%)")
        logger.info(f"   Extractable Market Data: {innovation_gaps.get('innovations_with_extractable_market_data', 0)} ({innovation_gaps.get('potential_recovery_rate', 0)}% recovery potential)")
        
        # Backfill opportunities
        backfill = results["backfill_opportunities"]
        logger.info(f"\n🤖 AI BACKFILL OPPORTUNITIES:")
        logger.info(f"   High Priority Candidates: {backfill.get('high_priority', 0)}")
        logger.info(f"   Medium Priority Candidates: {backfill.get('medium_priority', 0)}")
        logger.info(f"   Estimated Cost: ${backfill.get('estimated_cost_usd', 0):.2f}")
        logger.info(f"   Estimated Processing Time: {backfill.get('estimated_processing_time_hours', 0):.1f} hours")
        
        # Recommendations
        recommendations = results["recommendations"]
        logger.info(f"\n🎯 TOP RECOMMENDATIONS:")
        for rec in recommendations[:3]:
            logger.info(f"   {rec['priority']}: {rec['action']}")
            logger.info(f"      Impact: {rec['impact']}")
            logger.info(f"      Timeline: {rec['timeline']}")
        
        # Summary
        summary = results["summary"]
        logger.info(f"\n📋 EXECUTIVE SUMMARY:")
        logger.info(f"   Funding Gap Severity: {summary['current_funding_gap_severity']}")
        logger.info(f"   Market Gap Severity: {summary['current_market_gap_severity']}")
        logger.info(f"   Expected Improvement Timeline: {summary['expected_improvement_timeline']}")
        
        # Save results
        analyzer.save_analysis()
        
        logger.info(f"\n🚀 NEXT STEPS:")
        logger.info(f"   1. Run: python scripts/activate_funding_solutions.py")
        logger.info(f"   2. Monitor: /api/funding-enrichment/status")
        logger.info(f"   3. Trigger: /api/funding-enrichment/trigger-backfill")
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
