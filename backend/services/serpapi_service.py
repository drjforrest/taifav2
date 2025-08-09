"""
SerpAPI Google Scholar Service for TAIFA-FIALA
Cost-effective Google Scholar search service using SerpAPI
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
from config.settings import settings
from loguru import logger
from pydantic import BaseModel, HttpUrl
from services.unified_cache import (
    DataSource,
    cache_api_response,
    cache_null_response,
    get_cached_response,
    is_null_cached,
)


class ScholarResult(BaseModel):
    """Individual Google Scholar result from SerpAPI"""

    title: str
    link: Optional[HttpUrl] = None
    snippet: str
    cited_by: Optional[int] = None
    year: Optional[int] = None
    authors: Optional[List[str]] = []
    publication: Optional[str] = None
    position: int


class SerpAPIScholarResponse(BaseModel):
    """Response from SerpAPI Google Scholar search"""

    query: str
    results: List[ScholarResult]
    total_results: int
    search_time: float
    timestamp: datetime


class SerpAPIService:
    """Cost-effective Google Scholar search service using SerpAPI"""

    def __init__(self):
        self.api_key = settings.SERP_API_KEY
        self.base_url = "https://serpapi.com/search"
        self.session = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def search_google_scholar(
        self,
        query: str,
        num_results: int = 20,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
    ) -> SerpAPIScholarResponse:
        """Search Google Scholar using SerpAPI (with caching)"""

        # Create cache parameters
        cache_params = {
            "query": query,
            "num_results": num_results,
            "year_from": year_from,
            "year_to": year_to,
            "search_type": "google_scholar",
        }

        # Check cache first
        try:
            cached_response = await get_cached_response(
                DataSource.SERPAPI, cache_params
            )
            if cached_response:
                logger.info(f"Using cached SerpAPI Scholar search for: {query}")
                if "timestamp" in cached_response and isinstance(
                    cached_response["timestamp"], str
                ):
                    cached_response["timestamp"] = datetime.fromisoformat(
                        cached_response["timestamp"]
                    )
                return SerpAPIScholarResponse(**cached_response)
        except Exception as e:
            logger.warning(f"Error checking SerpAPI cache: {e}")

        # Check if null cached
        try:
            if await is_null_cached(DataSource.SERPAPI, cache_params):
                logger.info(f"SerpAPI Scholar search cached as null: {query}")
                return SerpAPIScholarResponse(
                    query=query,
                    results=[],
                    total_results=0,
                    search_time=0.0,
                    timestamp=datetime.now(),
                )
        except Exception as e:
            logger.warning(f"Error checking null cache: {e}")

        try:
            params = {
                "engine": "google_scholar",
                "q": query,
                "api_key": self.api_key,
                "num": min(num_results, 20),  # SerpAPI Scholar limit
                "hl": "en",
            }

            # Add year filter
            if year_from or year_to:
                year_filter = ""
                if year_from:
                    year_filter += f"{year_from}-"
                if year_to:
                    year_filter += f"{year_to}"
                else:
                    year_filter += "2025"
                params["as_ylo"] = year_from if year_from else None
                params["as_yhi"] = year_to if year_to else None

            start_time = datetime.now()

            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    search_time = (datetime.now() - start_time).total_seconds()

                    search_response = self.parse_scholar_results(
                        query, data, search_time
                    )

                    # Cache successful response
                    if search_response.results:
                        # Cache for 24 hours if we have results (Scholar data is stable)
                        response_dict = search_response.dict()
                        for result in response_dict["results"]:
                            if "link" in result and hasattr(result["link"], "__str__"):
                                result["link"] = str(result["link"])
                        if "timestamp" in response_dict:
                            response_dict["timestamp"] = response_dict[
                                "timestamp"
                            ].isoformat()

                        await cache_api_response(
                            DataSource.SERPAPI, cache_params, response_dict, 24.0
                        )
                        logger.info(
                            f"Cached SerpAPI Scholar search with {len(search_response.results)} results"
                        )
                    else:
                        # Cache null result for 12 hours
                        await cache_null_response(
                            DataSource.SERPAPI, cache_params, "no_results", 12.0
                        )
                        logger.info(f"Cached null SerpAPI result for query: {query}")

                    return search_response

                elif response.status == 429:
                    # Rate limited - cache for shorter period
                    await cache_null_response(
                        DataSource.SERPAPI, cache_params, "rate_limited", 1.0
                    )
                    logger.error(
                        f"SerpAPI Scholar search rate limited: {response.status}"
                    )
                else:
                    # Other API errors
                    await cache_null_response(
                        DataSource.SERPAPI, cache_params, "api_error", 2.0
                    )
                    logger.error(f"SerpAPI Scholar search error: {response.status}")

                return SerpAPIScholarResponse(
                    query=query,
                    results=[],
                    total_results=0,
                    search_time=0.0,
                    timestamp=datetime.now(),
                )

        except aiohttp.ClientError as e:
            await cache_null_response(
                DataSource.SERPAPI, cache_params, "network_error", 1.0
            )
            logger.error(f"SerpAPI network error: {e}")
        except Exception as e:
            logger.error(f"Error in SerpAPI Scholar search: {e}")

        # Return empty response
        return SerpAPIScholarResponse(
            query=query,
            results=[],
            total_results=0,
            search_time=0.0,
            timestamp=datetime.now(),
        )

    def parse_scholar_results(
        self, query: str, data: Dict[str, Any], search_time: float
    ) -> SerpAPIScholarResponse:
        """Parse Google Scholar results from SerpAPI response"""
        results = []

        if "organic_results" in data:
            for i, result in enumerate(data["organic_results"]):
                try:
                    # Extract authors
                    authors = []
                    if (
                        "publication_info" in result
                        and "authors" in result["publication_info"]
                    ):
                        authors = [
                            author["name"]
                            for author in result["publication_info"]["authors"]
                        ]

                    # Extract year
                    year = None
                    if (
                        "publication_info" in result
                        and "summary" in result["publication_info"]
                    ):
                        summary = result["publication_info"]["summary"]
                        # Try to extract year from summary (e.g., "Nature, 2023")
                        import re

                        year_match = re.search(r"\b(19|20)\d{2}\b", summary)
                        if year_match:
                            year = int(year_match.group())

                    # Extract cited by count
                    cited_by = None
                    if "inline_links" in result:
                        for link in result["inline_links"]:
                            if "cited_by" in link and "total" in link["cited_by"]:
                                cited_by = link["cited_by"]["total"]
                                break

                    scholar_result = ScholarResult(
                        title=result.get("title", ""),
                        link=result.get("link"),
                        snippet=result.get("snippet", ""),
                        cited_by=cited_by,
                        year=year,
                        authors=authors,
                        publication=result.get("publication_info", {}).get("summary"),
                        position=i + 1,
                    )
                    results.append(scholar_result)

                except Exception as e:
                    logger.warning(f"Error parsing SerpAPI Scholar result: {e}")
                    continue

        return SerpAPIScholarResponse(
            query=query,
            results=results,
            total_results=len(results),
            search_time=search_time,
            timestamp=datetime.now(),
        )

    async def search_african_ai_research(
        self,
        innovation_type: Optional[str] = None,
        country: Optional[str] = None,
        year_from: int = 2020,
        num_results: int = 50,
    ) -> List[ScholarResult]:
        """Search for African AI research papers using targeted queries"""
        logger.info(
            f"Searching for African AI research: type={innovation_type}, country={country}"
        )

        # Build targeted research queries
        base_queries = [
            "artificial intelligence Africa OR African",
            "machine learning Africa OR African",
            "AI development Africa OR African",
            "deep learning Africa OR African",
        ]

        # Add innovation type specific queries
        if innovation_type:
            type_queries = [
                f"{innovation_type} artificial intelligence Africa",
                f"{innovation_type} machine learning African",
                f"AI {innovation_type} Africa research",
            ]
            base_queries.extend(type_queries)

        # Add country specific queries
        if country:
            country_queries = [
                f"artificial intelligence {country}",
                f"machine learning {country}",
                f"AI research {country}",
            ]
            base_queries.extend(country_queries)

        all_results = []
        results_per_query = max(5, num_results // len(base_queries))

        for query in base_queries:
            try:
                scholar_results = await self.search_google_scholar(
                    query, results_per_query, year_from=year_from
                )
                all_results.extend(scholar_results.results)

                # Rate limiting for cost control
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error searching Scholar query '{query}': {e}")
                continue

        # Remove duplicates and filter for African relevance
        unique_results = self.deduplicate_results(all_results)
        filtered_results = self.filter_african_research_results(unique_results)

        # Sort by relevance (cited_by + year + African relevance)
        sorted_results = sorted(
            filtered_results, key=self.calculate_research_relevance_score, reverse=True
        )

        return sorted_results[:num_results]

    def deduplicate_results(self, results: List[ScholarResult]) -> List[ScholarResult]:
        """Remove duplicate results based on title similarity"""
        seen_titles = set()
        unique_results = []

        for result in results:
            title_key = result.title.lower().strip()[
                :50
            ]  # First 50 chars for similarity
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_results.append(result)

        return unique_results

    def filter_african_research_results(
        self, results: List[ScholarResult]
    ) -> List[ScholarResult]:
        """Filter results for African research relevance"""
        filtered = []

        african_countries = [
            "africa",
            "african",
            "nigeria",
            "kenya",
            "south africa",
            "ghana",
            "ethiopia",
            "morocco",
            "egypt",
            "tunisia",
            "uganda",
            "tanzania",
            "rwanda",
            "senegal",
            "botswana",
            "zambia",
            "zimbabwe",
            "cameroon",
            "ivory coast",
            "mali",
        ]

        for result in results:
            text = f"{result.title} {result.snippet}".lower()

            # Check for African relevance
            if any(country in text for country in african_countries):
                filtered.append(result)

        return filtered

    def calculate_research_relevance_score(self, result: ScholarResult) -> float:
        """Calculate research relevance score for ranking"""
        score = 0.0

        # Citation count (normalized)
        if result.cited_by:
            score += min(result.cited_by / 100.0, 1.0) * 0.4

        # Recency (2020-2025)
        if result.year:
            year_score = max(0, (result.year - 2020) / 5.0)
            score += year_score * 0.3

        # African relevance in title
        text = f"{result.title} {result.snippet}".lower()
        if "africa" in text or "african" in text:
            score += 0.3

        return score


# Convenience functions
async def search_african_ai_papers(
    innovation_type: Optional[str] = None,
    country: Optional[str] = None,
    year_from: int = 2020,
    num_results: int = 50,
) -> List[ScholarResult]:
    """Search for African AI research papers"""
    async with SerpAPIService() as serpapi:
        return await serpapi.search_african_ai_research(
            innovation_type, country, year_from, num_results
        )


async def search_scholar_papers(
    query: str, num_results: int = 20, year_from: Optional[int] = None
) -> SerpAPIScholarResponse:
    """Search Google Scholar papers"""
    async with SerpAPIService() as serpapi:
        return await serpapi.search_google_scholar(query, num_results, year_from)


if __name__ == "__main__":
    # Test the service
    async def test_serpapi():
        print("Testing SerpAPI Google Scholar service...")

        # Test African AI research search
        papers = await search_african_ai_papers(
            innovation_type="FinTech", country="Kenya", num_results=10
        )

        print(f"\nFound {len(papers)} research papers:")
        for paper in papers[:3]:
            print(f"- {paper.title}")
            print(f"  Authors: {', '.join(paper.authors) if paper.authors else 'N/A'}")
            print(f"  Year: {paper.year}, Cited by: {paper.cited_by}")
            print(f"  Link: {paper.link}")

    asyncio.run(test_serpapi())
