"""
ArXiv Academic Paper Scraper for TAIFA-FIALA
Specialized ETL for academic publications related to African AI research
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import aiohttp
import feedparser
from config.settings import settings
from loguru import logger
from pydantic import BaseModel
from services.database_service import DatabaseService
from services.deduplication_service import DeduplicationService

from services.etl_deduplication import check_and_handle_publication_duplicates


class ArxivPaper(BaseModel):
    """Pydantic model for ArXiv paper data"""
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    url: str
    published_date: datetime
    updated_date: datetime
    categories: List[str]
    keywords: List[str]
    african_relevance_score: float
    african_entities: List[str]  # Countries, institutions, etc.
    ai_relevance_score: float


class ArxivScraper:
    """ArXiv scraper for African AI research papers"""

    def __init__(self):
        self.base_url = settings.ARXIV_BASE_URL
        self.session = None
        self.african_countries = set(settings.AFRICAN_COUNTRIES)
        self.african_institutions = set(settings.AFRICAN_INSTITUTIONS)
        self.ai_keywords = settings.AFRICAN_AI_KEYWORDS
        
        # Initialize database and deduplication services
        self.db_service = DatabaseService()
        self.dedup_service = DeduplicationService()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.CRAWL4AI_TIMEOUT)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def build_search_query(self, keywords: List[str], max_results: int = 100,
                          days_back: int = 30) -> str:
        """Build ArXiv API search query"""
        # Combine keywords with OR
        keyword_query = " OR ".join([f'all:"{kw}"' for kw in keywords])

        # Add African country/institution filters
        african_terms = []
        for country in list(self.african_countries)[:10]:  # Limit to avoid URL length issues
            african_terms.append(f'all:"{country}"')

        for institution in list(self.african_institutions)[:10]:
            african_terms.append(f'all:"{institution}"')

        african_query = " OR ".join(african_terms)

        # Combine all terms
        full_query = f"({keyword_query}) AND ({african_query})"

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Build URL parameters
        params = {
            'search_query': full_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'lastUpdatedDate',
            'sortOrder': 'descending'
        }

        query_string = "&".join([f"{k}={quote(str(v))}" for k, v in params.items()])
        return f"{self.base_url}?{query_string}"

    async def fetch_papers(self, query_url: str) -> List[Dict[str, Any]]:
        """Fetch papers from ArXiv API"""
        try:
            async with self.session.get(query_url) as response:
                if response.status == 200:
                    content = await response.text()
                    return self.parse_arxiv_response(content)
                else:
                    logger.error(f"ArXiv API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching from ArXiv: {e}")
            return []

    def parse_arxiv_response(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse ArXiv XML response"""
        papers = []

        try:
            # Use feedparser to parse Atom feed
            feed = feedparser.parse(xml_content)

            for entry in feed.entries:
                try:
                    paper_data = self.extract_paper_data(entry)
                    if paper_data:
                        papers.append(paper_data)
                except Exception as e:
                    logger.error(f"Error parsing paper entry: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error parsing ArXiv response: {e}")

        return papers

    def extract_paper_data(self, entry) -> Optional[Dict[str, Any]]:
        """Extract paper data from ArXiv entry"""
        try:
            # Extract basic information
            title = getattr(entry, 'title', '').replace('\n', ' ').strip()
            abstract = getattr(entry, 'summary', '').replace('\n', ' ').strip()

            # Check if essential fields are present
            if not title or not abstract or not hasattr(entry, 'id'):
                logger.warning("Missing essential fields in entry, skipping")
                return None

            # Extract ArXiv ID from URL
            arxiv_id = entry.id.split('/')[-1]

            # Extract authors - handle different possible structures
            authors = []
            if hasattr(entry, 'authors') and entry.authors:
                authors = [getattr(author, 'name', str(author)) for author in entry.authors]
            elif hasattr(entry, 'author') and entry.author:
                authors = [entry.author]

            # Extract dates with error handling
            try:
                published_date = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ')
            except (ValueError, AttributeError):
                published_date = datetime.now()

            try:
                updated_date = datetime.strptime(entry.updated, '%Y-%m-%dT%H:%M:%SZ')
            except (ValueError, AttributeError):
                updated_date = published_date

            # Extract categories
            categories = []
            if hasattr(entry, 'tags') and entry.tags:
                categories = [getattr(tag, 'term', str(tag)) for tag in entry.tags]

            # Calculate relevance scores
            african_score, african_entities = self.calculate_african_relevance(title, abstract, authors)
            ai_score = self.calculate_ai_relevance(title, abstract, categories)

            # Extract keywords from title and abstract
            keywords = self.extract_keywords(title, abstract)

            return {
                'arxiv_id': arxiv_id,
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'url': entry.id,
                'published_date': published_date,
                'updated_date': updated_date,
                'categories': categories,
                'keywords': keywords,
                'african_relevance_score': african_score,
                'african_entities': african_entities,
                'ai_relevance_score': ai_score
            }

        except Exception as e:
            logger.error(f"Error extracting paper data: {e}")
            return None

    def calculate_african_relevance(self, title: str, abstract: str, authors: List[str]) -> tuple[float, List[str]]:
        """Calculate African relevance score and extract African entities"""
        # Handle None values
        title = title or ""
        abstract = abstract or ""
        authors = authors or []

        text = f"{title} {abstract} {' '.join(authors)}".lower()

        found_entities = []
        score = 0.0

        # Check for African countries
        for country in self.african_countries:
            if country.lower() in text:
                found_entities.append(country)
                score += 0.3

        # Check for African institutions
        for institution in self.african_institutions:
            if institution.lower() in text:
                found_entities.append(institution)
                score += 0.4

        # Check for African-specific terms
        african_terms = [
            'africa', 'african', 'sub-saharan', 'sahel', 'maghreb',
            'east africa', 'west africa', 'north africa', 'southern africa'
        ]

        for term in african_terms:
            if term in text:
                score += 0.2
                found_entities.append(term.title())

        # Check author affiliations (approximate)
        for author in authors:
            if author:  # Check if author is not None
                author_lower = author.lower()
                for country in self.african_countries:
                    if country.lower() in author_lower:
                        score += 0.5
                        found_entities.append(f"Author from {country}")

        return min(score, 1.0), list(set(found_entities))

    def calculate_ai_relevance(self, title: str, abstract: str, categories: List[str]) -> float:
        """Calculate AI relevance score"""
        # Handle None values
        title = title or ""
        abstract = abstract or ""
        categories = categories or []

        text = f"{title} {abstract}".lower()

        ai_terms = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'computer vision', 'natural language processing',
            'nlp', 'ai', 'ml', 'dl', 'cnn', 'rnn', 'lstm', 'transformer',
            'reinforcement learning', 'supervised learning', 'unsupervised learning',
            'classification', 'regression', 'clustering', 'recommendation system',
            'data mining', 'big data', 'predictive analytics', 'automation',
            'robotics', 'expert system', 'knowledge representation'
        ]

        score = 0.0
        for term in ai_terms:
            if term in text:
                if term in ['artificial intelligence', 'machine learning', 'deep learning']:
                    score += 0.3  # High-value terms
                elif term in ['ai', 'ml', 'dl']:
                    score += 0.2  # Common abbreviations
                else:
                    score += 0.1  # Other AI terms

        # Check categories
        ai_categories = ['cs.AI', 'cs.LG', 'cs.CV', 'cs.CL', 'cs.RO', 'stat.ML']
        for cat in categories:
            if cat and cat in ai_categories:  # Check if cat is not None
                score += 0.4

        return min(score, 1.0)

    def extract_keywords(self, title: str, abstract: str) -> List[str]:
        """Extract keywords from title and abstract"""
        # Handle None values
        title = title or ""
        abstract = abstract or ""

        text = f"{title} {abstract}".lower()

        # Simple keyword extraction based on AI and African terms
        keywords = []

        # AI keywords
        ai_keywords = [
            'machine learning', 'deep learning', 'neural network', 'computer vision',
            'natural language processing', 'reinforcement learning', 'classification',
            'regression', 'clustering', 'recommendation', 'automation', 'robotics'
        ]

        for keyword in ai_keywords:
            if keyword in text:
                keywords.append(keyword.title())

        # Domain-specific keywords
        domain_keywords = [
            'healthcare', 'agriculture', 'finance', 'education', 'transportation',
            'energy', 'environment', 'security', 'governance', 'development'
        ]

        for keyword in domain_keywords:
            if keyword in text:
                keywords.append(keyword.title())

        return list(set(keywords))

    async def scrape_recent_papers(self, days_back: int = 7, max_results: int = 100) -> List[ArxivPaper]:
        """Scrape recent papers related to African AI research"""
        logger.info(f"Starting ArXiv scrape for last {days_back} days...")

        papers = []

        # Search with different keyword combinations
        keyword_groups = [
            settings.AFRICAN_AI_KEYWORDS[:3],  # General AI terms
            ['healthcare AI africa', 'medical AI africa'],  # HealthTech
            ['agriculture AI africa', 'farming AI africa'],  # AgriTech
            ['financial AI africa', 'fintech africa'],  # FinTech
            ['education AI africa', 'edtech africa']  # EdTech
        ]

        for keywords in keyword_groups:
            try:
                query_url = self.build_search_query(keywords, max_results // len(keyword_groups), days_back)
                paper_data = await self.fetch_papers(query_url)

                for data in paper_data:
                    # Filter papers with minimum relevance scores
                    if (data['african_relevance_score'] >= 0.3 and
                        data['ai_relevance_score'] >= 0.2):

                        try:
                            paper = ArxivPaper(**data)
                            papers.append(paper)
                        except Exception as e:
                            logger.error(f"Error creating ArxivPaper model: {e}")
                            continue

                # Add delay between requests to be respectful
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error in keyword group search: {e}")
                continue

        # Remove duplicates based on arxiv_id
        unique_papers = {}
        for paper in papers:
            if paper.arxiv_id not in unique_papers:
                unique_papers[paper.arxiv_id] = paper

        result_papers = list(unique_papers.values())
        logger.info(f"Found {len(result_papers)} unique relevant papers")
        
        # Store papers in database
        if result_papers:
            stored_papers = await self._store_papers_in_database(result_papers)
            logger.info(f"✅ Stored {len(stored_papers)} papers in database")

        return result_papers
    
    async def _store_papers_in_database(self, papers: List[ArxivPaper]) -> List[Dict[str, Any]]:
        """Store ArXiv papers in Supabase database as publications"""
        
        stored_records = []
        
        for paper in papers:
            try:
                # Convert ArXiv paper to publication format
                publication_data = {
                    'title': paper.title,
                    'publication_type': 'preprint',
                    'publication_date': paper.published_date.date() if paper.published_date else None,
                    'year': paper.published_date.year if paper.published_date else None,
                    'url': paper.url,
                    'venue': 'arXiv',
                    'abstract': paper.abstract,
                    'keywords': paper.keywords + paper.categories,
                    'source': 'arxiv',
                    'source_id': paper.arxiv_id,
                    'african_relevance_score': paper.african_relevance_score,
                    'ai_relevance_score': paper.ai_relevance_score,
                    'african_entities': paper.african_entities,
                    'data_type': 'Academic Paper'
                }
                
                # Store in database with deduplication
                success, stored_record = await check_and_handle_publication_duplicates(publication_data)
                action = 'processed'
                
                if success and stored_record:
                    stored_records.append(stored_record)
                    logger.info(f"✅ Stored ArXiv paper ({action}): {paper.title[:50]}...")
                elif not success:
                    logger.info(f"ℹ️ ArXiv paper handling ({action}): {paper.title[:50]}...")
                    
            except Exception as e:
                logger.error(f"❌ Error storing ArXiv paper {paper.title[:50]}: {e}")
                continue
        
        logger.info(f"📊 ArXiv database storage complete: {len(stored_records)}/{len(papers)} papers stored")
        return stored_records


async def scrape_arxiv_papers(days_back: int = 7, max_results: int = 100) -> List[ArxivPaper]:
    """Main function to scrape ArXiv papers with monitoring"""
    from services.etl_context import ETLJobContext

    with ETLJobContext("academic_pipeline") as job:
        try:
            async with ArxivScraper() as scraper:
                papers = await scraper.scrape_recent_papers(days_back, max_results)
                job.add_processed_items(len(papers))
                logger.info(f"ArXiv scraper found {len(papers)} papers")
                return papers
        except Exception as e:
            logger.error(f"ArXiv scraper failed: {e}")
            raise


if __name__ == "__main__":
    # Test the scraper
    async def test_scraper():
        papers = await scrape_arxiv_papers(days_back=30, max_results=50)

        print(f"Found {len(papers)} papers:")
        for paper in papers[:5]:  # Show first 5
            print(f"\nTitle: {paper.title}")
            print(f"Authors: {', '.join(paper.authors[:3])}...")
            print(f"African Score: {paper.african_relevance_score:.2f}")
            print(f"AI Score: {paper.ai_relevance_score:.2f}")
            print(f"Entities: {paper.african_entities}")

    asyncio.run(test_scraper())
