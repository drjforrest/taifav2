"""
Funding Enrichment Activator Service
===================================

This service integrates the enhanced funding extractor and market sizing
capabilities into the main TAIFA-FIALA ETL pipeline to address the critical
data gaps in funding information (68% missing) and market sizing (87% missing).
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from config.database import get_supabase
from services.ai_backfill_service import ai_backfill_service, create_backfill_jobs_for_innovations
from services.enrichment_scheduler import get_enrichment_scheduler
from etl.intelligence.perplexity_african_ai import PerplexityAfricanAIModule, IntelligenceType
from scripts.examples.enhanced_funding_extractor import EnhancedFundingExtractor

logger = logging.getLogger(__name__)


class FundingEnrichmentActivator:
    """Activates funding and market sizing enrichment across the platform"""

    def __init__(self):
        self.funding_extractor = EnhancedFundingExtractor()
        self.supabase = get_supabase()

    async def activate_immediate_solutions(self) -> Dict[str, Any]:
        """Implement all immediate solutions for funding and market sizing gaps"""
        
        results = {
            "activation_timestamp": datetime.now().isoformat(),
            "solutions_activated": [],
            "statistics": {},
            "errors": []
        }

        try:
            # Solution 1: Configure AI Backfill Service for funding gaps
            logger.info("🚀 Activating AI Backfill Service for funding gaps...")
            backfill_stats = await self._activate_ai_backfill()
            results["solutions_activated"].append("ai_backfill_service")
            results["statistics"]["backfill"] = backfill_stats
            
            # Solution 2: Enable scheduled enrichment for funding data
            logger.info("📅 Enabling scheduled enrichment for funding data...")
            scheduler_stats = await self._enable_scheduled_enrichment()
            results["solutions_activated"].append("scheduled_enrichment")
            results["statistics"]["scheduler"] = scheduler_stats
            
            # Solution 3: Run immediate intelligence gathering with market focus
            logger.info("🧠 Running immediate intelligence gathering with market sizing focus...")
            intelligence_stats = await self._run_market_focused_intelligence()
            results["solutions_activated"].append("market_intelligence_gathering")
            results["statistics"]["intelligence"] = intelligence_stats
            
            # Solution 4: Process existing data with enhanced extractor
            logger.info("🔍 Processing existing records with enhanced funding extractor...")
            processing_stats = await self._process_existing_records()
            results["solutions_activated"].append("enhanced_extraction")
            results["statistics"]["processing"] = processing_stats
            
            logger.info(f"✅ Successfully activated {len(results['solutions_activated'])} solutions")
            
        except Exception as e:
            error_msg = f"Error during activation: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            
        return results

    async def _activate_ai_backfill(self) -> Dict[str, Any]:
        """Activate AI backfill service specifically for funding and market data gaps"""
        
        try:
            # Get innovations with missing funding/market data
            innovations = await self._get_innovations_missing_funding_data()
            
            if not innovations:
                return {"status": "no_innovations_found", "count": 0}
            
            # Create backfill jobs for these innovations
            jobs = await create_backfill_jobs_for_innovations(innovations[:50])  # Process 50 at a time
            
            logger.info(f"Created {len(jobs)} backfill jobs for funding/market data")
            
            # Get service statistics
            stats = ai_backfill_service.get_backfill_stats()
            stats["new_jobs_created"] = len(jobs)
            stats["innovations_queued"] = len(innovations)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error activating AI backfill: {e}")
            return {"status": "error", "error": str(e)}

    async def _enable_scheduled_enrichment(self) -> Dict[str, Any]:
        """Enable and configure scheduled enrichment for funding landscape"""
        
        try:
            scheduler = get_enrichment_scheduler()
            
            # Update schedule to focus on funding and market analysis
            scheduler.update_schedule(
                interval_hours=6,  # Run every 6 hours
                enabled=True,
                intelligence_types=["funding_landscape", "market_analysis"],
                provider="perplexity"
            )
            
            # Start the scheduler if not running
            if not scheduler.running:
                await scheduler.start_scheduler()
            
            schedule_info = scheduler.get_schedule_info()
            schedule_info["status"] = "activated"
            
            logger.info("✅ Scheduled enrichment activated for funding and market data")
            return schedule_info
            
        except Exception as e:
            logger.error(f"Error enabling scheduled enrichment: {e}")
            return {"status": "error", "error": str(e)}

    async def _run_market_focused_intelligence(self) -> Dict[str, Any]:
        """Run immediate Perplexity intelligence gathering focused on market sizing"""
        
        try:
            # Get API key from environment
            import os
            api_key = os.getenv("PERPLEXITY_API_KEY")
            if not api_key:
                return {"status": "skipped", "reason": "no_api_key"}
            
            # Run focused intelligence gathering
            async with PerplexityAfricanAIModule(api_key) as perplexity:
                reports = await perplexity.synthesize_intelligence(
                    intelligence_types=[
                        IntelligenceType.FUNDING_LANDSCAPE,
                        IntelligenceType.MARKET_ANALYSIS
                    ],
                    time_period="last_30_days",
                    geographic_focus=["Nigeria", "Kenya", "South Africa", "Ghana", "Egypt"]
                )
                
                # Store reports in database
                stored_reports = 0
                for report in reports:
                    try:
                        report_data = {
                            "id": report.report_id,
                            "title": report.title,
                            "provider": "perplexity",
                            "source": "funding_activator",
                            "report_type": report.report_type.value,
                            "summary": report.summary,
                            "key_findings": report.key_findings,
                            "funding_updates": report.funding_updates,
                            "confidence_score": report.confidence_score,
                            "sources": report.sources,
                            "generation_timestamp": report.generation_timestamp.isoformat(),
                        }
                        
                        self.supabase.table("intelligence_reports").insert(report_data).execute()
                        stored_reports += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to store report {report.report_id}: {e}")
                
                return {
                    "status": "completed",
                    "reports_generated": len(reports),
                    "reports_stored": stored_reports,
                    "intelligence_types": ["funding_landscape", "market_analysis"]
                }
                
        except Exception as e:
            logger.error(f"Error running market-focused intelligence: {e}")
            return {"status": "error", "error": str(e)}

    async def _process_existing_records(self) -> Dict[str, Any]:
        """Process existing innovation records with enhanced funding extractor"""
        
        try:
            # Get recent innovations without funding data
            response = self.supabase.table("innovations").select("*").limit(100).execute()
            innovations = response.data if response.data else []
            
            processed_count = 0
            enhanced_count = 0
            
            for innovation in innovations:
                try:
                    # Check if already has comprehensive funding/market data
                    if (innovation.get("fundings") and 
                        len(innovation.get("fundings", [])) > 0 and 
                        innovation.get("market_sizing")):
                        continue
                    
                    # Extract funding and market info from description
                    full_text = f"{innovation.get('title', '')} {innovation.get('description', '')}"
                    funding_info = self.funding_extractor.extract_funding_info(full_text)
                    
                    # Update record if new data found
                    updates = {}
                    if funding_info.get("market_sizing"):
                        updates["market_sizing"] = funding_info["market_sizing"]
                        enhanced_count += 1
                    
                    if funding_info.get("funding_type") != "per_project_range" or funding_info.get("total_funding_pool"):
                        # Store funding info in metadata for now
                        current_metadata = innovation.get("metadata", {})
                        current_metadata["extracted_funding"] = funding_info
                        updates["metadata"] = current_metadata
                        enhanced_count += 1
                    
                    if updates:
                        self.supabase.table("innovations").update(updates).eq("id", innovation["id"]).execute()
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing innovation {innovation.get('id')}: {e}")
            
            return {
                "status": "completed",
                "processed_count": processed_count,
                "enhanced_count": enhanced_count,
                "total_innovations": len(innovations)
            }
            
        except Exception as e:
            logger.error(f"Error processing existing records: {e}")
            return {"status": "error", "error": str(e)}

    async def _get_innovations_missing_funding_data(self) -> List[Dict[str, Any]]:
        """Get innovations that are missing funding or market sizing data"""
        
        try:
            # Query for innovations with missing funding data
            response = self.supabase.table("innovations").select("*").execute()
            innovations = response.data if response.data else []
            
            missing_funding_data = []
            for innovation in innovations:
                has_funding = bool(innovation.get("fundings") and len(innovation.get("fundings", [])) > 0)
                has_market_sizing = bool(innovation.get("market_sizing"))
                
                if not has_funding or not has_market_sizing:
                    missing_funding_data.append(innovation)
            
            logger.info(f"Found {len(missing_funding_data)} innovations missing funding/market data")
            return missing_funding_data
            
        except Exception as e:
            logger.error(f"Error querying innovations: {e}")
            return []

    async def get_enrichment_status(self) -> Dict[str, Any]:
        """Get current status of funding enrichment across the platform"""
        
        try:
            # Get innovation statistics
            response = self.supabase.table("innovations").select("id, fundings, market_sizing").execute()
            innovations = response.data if response.data else []
            
            total_innovations = len(innovations)
            has_funding = sum(1 for i in innovations if i.get("fundings") and len(i.get("fundings", [])) > 0)
            has_market_sizing = sum(1 for i in innovations if i.get("market_sizing"))
            
            funding_completeness = (has_funding / total_innovations * 100) if total_innovations > 0 else 0
            market_completeness = (has_market_sizing / total_innovations * 100) if total_innovations > 0 else 0
            
            # Get AI backfill service stats
            backfill_stats = ai_backfill_service.get_backfill_stats()
            
            # Get scheduler status
            scheduler = get_enrichment_scheduler()
            scheduler_info = scheduler.get_schedule_info()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "data_completeness": {
                    "total_innovations": total_innovations,
                    "funding_completeness_percent": round(funding_completeness, 1),
                    "market_sizing_completeness_percent": round(market_completeness, 1),
                    "funding_gap_count": total_innovations - has_funding,
                    "market_sizing_gap_count": total_innovations - has_market_sizing
                },
                "backfill_service": backfill_stats,
                "scheduled_enrichment": scheduler_info,
                "status": "active" if scheduler.running else "inactive"
            }
            
        except Exception as e:
            logger.error(f"Error getting enrichment status: {e}")
            return {"status": "error", "error": str(e)}


# Global activator instance
funding_activator = FundingEnrichmentActivator()


async def activate_funding_solutions():
    """Convenience function to activate all funding enrichment solutions"""
    return await funding_activator.activate_immediate_solutions()


async def get_funding_enrichment_status():
    """Convenience function to get current enrichment status"""
    return await funding_activator.get_enrichment_status()


if __name__ == "__main__":
    # Test the activation
    async def main():
        print("🚀 Activating Funding Enrichment Solutions...")
        
        # Activate solutions
        results = await activate_funding_solutions()
        print("✅ Activation Results:")
        print(json.dumps(results, indent=2))
        
        # Check status
        status = await get_funding_enrichment_status()
        print("\n📊 Current Status:")
        print(json.dumps(status, indent=2))
    
    asyncio.run(main())