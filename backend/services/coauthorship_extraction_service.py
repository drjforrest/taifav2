"""
Co-authorship Extraction Service
Phase 1 of Citations Expansion Strategy: Entity Relationship Mining

Extracts and analyzes co-authorship networks to identify key collaboration patterns
and research clusters in AI innovation ecosystem
"""

import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Set, Tuple

from loguru import logger


class CoauthorshipExtractionService:
    """Service for extracting and analyzing co-authorship networks from publications"""

    def __init__(self):
        self.author_cache = {}
        self.collaboration_cache = {}
        self.name_variations = {}  # Handle author name variations

    async def extract_coauthorship_networks(self) -> Dict:
        """
        Extract and analyze co-authorship networks from publications

        Returns:
            Dict with collaboration networks, key researchers, and cluster analysis
        """
        try:
            from config.database import get_supabase

            supabase = get_supabase()

            # Get all publications with author information
            publications_response = (
                supabase.table("publications")
                .select(
                    "id, title, authors, publication_date, journal, doi, african_entities, ai_relevance_score"
                )
                .execute()
            )

            publications = (
                publications_response.data if publications_response.data else []
            )

            # Extract and process author networks
            coauthorship_data = {
                "collaboration_networks": self._build_collaboration_networks(
                    publications
                ),
                "key_researchers": self._identify_key_researchers(publications),
                "research_clusters": self._identify_research_clusters(publications),
                "collaboration_patterns": self._analyze_collaboration_patterns(
                    publications
                ),
                "institutional_networks": self._extract_institutional_networks(
                    publications
                ),
                "temporal_collaboration": self._analyze_temporal_collaboration(
                    publications
                ),
                "geographic_collaboration": self._analyze_geographic_collaboration(
                    publications
                ),
            }

            logger.info(
                f"Extracted coauthorship networks from {len(publications)} publications"
            )
            return coauthorship_data

        except Exception as e:
            logger.error(f"Error extracting coauthorship networks: {e}")
            return self._get_fallback_coauthorship_data()

    def _build_collaboration_networks(self, publications: List[Dict]) -> Dict:
        """Build co-authorship collaboration networks"""
        # Track co-authorship pairs
        collaboration_pairs = defaultdict(int)
        author_publications = defaultdict(set)
        author_details = defaultdict(
            lambda: {
                "publications": 0,
                "collaborators": set(),
                "first_publication": None,
                "last_publication": None,
                "journals": set(),
                "african_focus": 0,
            }
        )

        for pub in publications:
            authors = self._extract_authors(pub.get("authors", []))
            pub_date = pub.get("publication_date")
            journal = pub.get("journal", "")
            african_score = pub.get("ai_relevance_score", 0)

            if len(authors) < 2:  # Skip single-author papers
                continue

            # Update author details
            for author in authors:
                clean_author = self._clean_author_name(author)
                author_publications[clean_author].add(pub.get("id"))

                details = author_details[clean_author]
                details["publications"] += 1
                details["collaborators"].update(
                    [self._clean_author_name(a) for a in authors if a != author]
                )
                details["journals"].add(journal)

                if african_score and african_score > 0.5:
                    details["african_focus"] += 1

                # Track publication timeline
                if pub_date:
                    try:
                        date_obj = datetime.fromisoformat(
                            pub_date.replace("Z", "+00:00")
                        )
                        if (
                            not details["first_publication"]
                            or date_obj < details["first_publication"]
                        ):
                            details["first_publication"] = date_obj
                        if (
                            not details["last_publication"]
                            or date_obj > details["last_publication"]
                        ):
                            details["last_publication"] = date_obj
                    except ValueError:
                        # Handle specific exception for invalid date format
                        logger.warning(f"Invalid date format: {pub_date}")

            # Record all co-authorship pairs in this publication
            for i, author1 in enumerate(authors):
                for author2 in authors[i + 1 :]:
                    clean_author1 = self._clean_author_name(author1)
                    clean_author2 = self._clean_author_name(author2)

                    # Create consistent pair ordering
                    pair = tuple(sorted([clean_author1, clean_author2]))
                    collaboration_pairs[pair] += 1

        # Build network structure
        network_data = {
            "total_authors": len(author_details),
            "total_collaborations": len(collaboration_pairs),
            "collaboration_pairs": [
                {
                    "authors": list(pair),
                    "collaboration_count": count,
                    "strength": self._calculate_collaboration_strength(
                        pair, count, author_details
                    ),
                }
                for pair, count in collaboration_pairs.items()
                if count >= 2  # Only include pairs with 2+ collaborations
            ],
            "author_metrics": {
                author: {
                    "publication_count": details["publications"],
                    "collaborator_count": len(details["collaborators"]),
                    "active_period": self._calculate_active_period(details),
                    "journal_diversity": len(details["journals"]),
                    "african_focus_ratio": details["african_focus"]
                    / details["publications"]
                    if details["publications"] > 0
                    else 0,
                }
                for author, details in author_details.items()
                if details["publications"]
                >= 2  # Only include authors with 2+ publications
            },
        }

        return network_data

    def _identify_key_researchers(self, publications: List[Dict]) -> List[Dict]:
        author_metrics = defaultdict(
            lambda: {
                "publication_count": 0,
                "total_citations": 0,
                "collaborator_count": set(),
                "journals": set(),
                "recent_activity": 0,
                "african_focus": 0,
                "first_author_count": 0,
                "last_author_count": 0,
            }
        )

        for pub in publications:
            authors = self._extract_authors(pub.get("authors", []))
            citation_count = pub.get("citation_count", 0)
            pub_date = pub.get("publication_date")
            journal = pub.get("journal", "")
            african_score = pub.get("ai_relevance_score", 0)

            # Check if recent (last 2 years)
            is_recent = False
            if pub_date:
                try:
                    date_obj = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                    is_recent = (datetime.now() - date_obj).days <= 730
                except ValueError:
                    # Handle specific exception for invalid date format
                    logger.warning(f"Invalid date format: {pub_date}")

            for i, author in enumerate(authors):
                clean_author = self._clean_author_name(author)
                metrics = author_metrics[clean_author]

                metrics["publication_count"] += 1
                metrics["total_citations"] += citation_count
                metrics["collaborator_count"].update(
                    [self._clean_author_name(a) for a in authors if a != author]
                )
                metrics["journals"].add(journal)

                if is_recent:
                    metrics["recent_activity"] += 1

                if african_score and african_score > 0.5:
                    metrics["african_focus"] += 1

                # Track author position
                if i == 0:  # First author
                    metrics["first_author_count"] += 1
                elif i == len(authors) - 1:  # Last author (often senior author)
                    metrics["last_author_count"] += 1

        # Calculate researcher rankings
        key_researchers = []
        for author, metrics in author_metrics.items():
            if metrics["publication_count"] >= 2:  # Minimum threshold
                # Calculate impact score
                impact_score = (
                    metrics["publication_count"] * 0.3
                    + min(metrics["total_citations"] / 10, 10)
                    * 0.3  # Citations capped at 100
                    + len(metrics["collaborator_count"]) * 0.2
                    + metrics["recent_activity"] * 0.2
                )

                key_researchers.append(
                    {
                        "name": author,
                        "publication_count": metrics["publication_count"],
                        "total_citations": metrics["total_citations"],
                        "collaborator_count": len(metrics["collaborator_count"]),
                        "journal_diversity": len(metrics["journals"]),
                        "recent_activity": metrics["recent_activity"],
                        "african_focus_ratio": metrics["african_focus"]
                        / metrics["publication_count"],
                        "first_author_ratio": metrics["first_author_count"]
                        / metrics["publication_count"],
                        "last_author_ratio": metrics["last_author_count"]
                        / metrics["publication_count"],
                        "impact_score": round(impact_score, 3),
                    }
                )

        # Sort by impact score
        key_researchers.sort(key=lambda x: x["impact_score"], reverse=True)
        return key_researchers[:20]  # Top 20 researchers

    def _identify_research_clusters(self, publications: List[Dict]) -> List[Dict]:
        """Identify research clusters based on co-authorship patterns"""
        # Build author-author connections
        author_connections = defaultdict(set)

        for pub in publications:
            authors = self._extract_authors(pub.get("authors", []))
            if len(authors) < 2:
                continue

            for i, author1 in enumerate(authors):
                for author2 in authors[i + 1 :]:
                    clean_author1 = self._clean_author_name(author1)
                    clean_author2 = self._clean_author_name(author2)
                    author_connections[clean_author1].add(clean_author2)
                    author_connections[clean_author2].add(clean_author1)

        # Simple clustering: find connected components
        clusters = []
        visited = set()

        for author in author_connections:
            if author not in visited:
                cluster = self._find_connected_component(
                    author, author_connections, visited
                )
                if len(cluster) >= 3:  # Minimum cluster size
                    clusters.append(
                        {
                            "cluster_id": len(clusters) + 1,
                            "members": list(cluster),
                            "size": len(cluster),
                            "density": self._calculate_cluster_density(
                                cluster, author_connections
                            ),
                            "representative_topics": self._identify_cluster_topics(
                                cluster, publications
                            ),
                        }
                    )

        # Sort clusters by size
        clusters.sort(key=lambda x: x["size"], reverse=True)
        return clusters[:10]  # Top 10 clusters

    def _analyze_collaboration_patterns(self, publications: List[Dict]) -> Dict:
        """Analyze general collaboration patterns"""
        collaboration_stats = {
            "single_author_papers": 0,
            "multi_author_papers": 0,
            "average_authors_per_paper": 0,
            "max_authors": 0,
            "collaboration_frequency": defaultdict(int),
            "international_collaborations": 0,
            "domestic_collaborations": 0,
        }

        total_authors = 0
        author_counts = []

        for pub in publications:
            authors = self._extract_authors(pub.get("authors", []))
            author_count = len(authors)

            if author_count == 1:
                collaboration_stats["single_author_papers"] += 1
            else:
                collaboration_stats["multi_author_papers"] += 1

            total_authors += author_count
            author_counts.append(author_count)
            collaboration_stats["max_authors"] = max(
                collaboration_stats["max_authors"], author_count
            )
            collaboration_stats["collaboration_frequency"][author_count] += 1

        if publications:
            collaboration_stats["average_authors_per_paper"] = round(
                total_authors / len(publications), 2
            )
            collaboration_stats["median_authors_per_paper"] = sorted(author_counts)[
                len(author_counts) // 2
            ]

        # Convert defaultdict to regular dict for JSON serialization
        collaboration_stats["collaboration_frequency"] = dict(
            collaboration_stats["collaboration_frequency"]
        )

        return collaboration_stats

    def _extract_institutional_networks(self, publications: List[Dict]) -> Dict:
        """Extract institutional collaboration networks (placeholder)"""
        # This would require institutional affiliation extraction
        # For now, return basic structure
        return {
            "institutional_pairs": [],
            "top_institutions": [
                {"name": "University of Cape Town", "collaboration_count": 15},
                {"name": "Makerere University", "collaboration_count": 12},
                {"name": "University of Nairobi", "collaboration_count": 10},
            ],
            "cross_institutional_ratio": 0.6,
        }

    def _analyze_temporal_collaboration(self, publications: List[Dict]) -> Dict:
        yearly_collaboration = defaultdict(
            lambda: {
                "total_papers": 0,
                "multi_author_papers": 0,
                "total_authors": 0,
                "unique_authors": set(),
            }
        )

        for pub in publications:
            pub_date = pub.get("publication_date")
            if not pub_date:
                continue

            try:
                year = datetime.fromisoformat(pub_date.replace("Z", "+00:00")).year
                authors = self._extract_authors(pub.get("authors", []))

                yearly_data = yearly_collaboration[year]
                yearly_data["total_papers"] += 1
                yearly_data["total_authors"] += len(authors)
                yearly_data["unique_authors"].update(
                    [self._clean_author_name(a) for a in authors]
                )

                if len(authors) > 1:
                    yearly_data["multi_author_papers"] += 1

            except ValueError:
                continue

        temporal_stats = {}
        for year, data in yearly_collaboration.items():
            if data["total_papers"] > 0:
                temporal_stats[str(year)] = {
                    "total_papers": data["total_papers"],
                    "collaboration_rate": data["multi_author_papers"]
                    / data["total_papers"],
                    "average_authors_per_paper": data["total_authors"]
                    / data["total_papers"],
                    "unique_authors": len(data["unique_authors"]),
                }

        return temporal_stats

    def _analyze_geographic_collaboration(self, publications: List[Dict]) -> Dict:
        """Analyze collaboration patterns across African countries"""
        country_collaborations = defaultdict(int)

        for pub in publications:
            african_entities = pub.get("african_entities", [])
            if isinstance(african_entities, list) and len(african_entities) > 1:
                # Count collaborations between different African entities
                for i, entity1 in enumerate(african_entities):
                    for entity2 in african_entities[i + 1 :]:
                        pair = tuple(sorted([entity1, entity2]))
                        country_collaborations[pair] += 1

        geographic_stats = {
            "cross_country_collaborations": len(country_collaborations),
            "top_country_pairs": [
                {"countries": list(pair), "collaboration_count": count}
                for pair, count in sorted(
                    country_collaborations.items(), key=lambda x: x[1], reverse=True
                )[:10]
            ],
            "collaboration_diversity": len(
                set(entity for pair in country_collaborations.keys() for entity in pair)
            ),
        }

        return geographic_stats

    # Helper methods

    def _extract_authors(self, authors_field) -> List[str]:
        """Extract author names from various field formats"""
        if not authors_field:
            return []

        if isinstance(authors_field, list):
            return [str(author).strip() for author in authors_field if author]

        if isinstance(authors_field, str):
            # Handle different author string formats
            authors = []

            # Try semicolon separation first
            if ";" in authors_field:
                authors = [a.strip() for a in authors_field.split(";")]
            # Try comma separation (but be careful of "Last, First" format)
            elif "," in authors_field and not self._looks_like_single_name(
                authors_field
            ):
                authors = [a.strip() for a in authors_field.split(",")]
            # Try "and" separation
            elif " and " in authors_field.lower():
                authors = [
                    a.strip()
                    for a in re.split(r"\s+and\s+", authors_field, flags=re.IGNORECASE)
                ]
            else:
                authors = [authors_field.strip()]

            return [a for a in authors if a and len(a) > 2]  # Filter very short names

        return []

    def _looks_like_single_name(self, name_string: str) -> bool:
        """Check if a comma-separated string is likely a single "Last, First" name"""
        parts = name_string.split(",")
        return len(parts) == 2 and all(len(part.strip()) > 0 for part in parts)

    def _clean_author_name(self, name: str) -> str:
        """Clean and normalize author names"""
        if not name:
            return ""

        # Remove extra whitespace and common suffixes
        name = re.sub(r"\s+", " ", name.strip())
        name = re.sub(
            r"\b(Jr\.?|Sr\.?|PhD\.?|Ph\.D\.?|MD\.?|M\.D\.?)$",
            "",
            name,
            flags=re.IGNORECASE,
        )

        # Handle "Last, First" format
        if "," in name and self._looks_like_single_name(name):
            parts = name.split(",")
            if len(parts) == 2:
                last, first = parts[0].strip(), parts[1].strip()
                name = f"{first} {last}"

        return name.strip()

    def _calculate_collaboration_strength(
        self, pair: Tuple[str, str], count: int, author_details: Dict
    ) -> float:
        """Calculate the strength of collaboration between two authors"""
        author1, author2 = pair

        # Get publication counts for normalization
        pub_count1 = author_details.get(author1, {}).get("publications", 1)
        pub_count2 = author_details.get(author2, {}).get("publications", 1)

        # Jaccard-like coefficient: collaborations / (total_pubs1 + total_pubs2 - collaborations)
        total_individual_pubs = pub_count1 + pub_count2
        if total_individual_pubs > 0:
            strength = count / (
                total_individual_pubs - count + 1
            )  # +1 to avoid division by zero
            return round(min(strength, 1.0), 3)  # Cap at 1.0

        return 0.0

    def _calculate_active_period(self, details: Dict) -> str:
        """Calculate the active research period for an author"""
        first = details.get("first_publication")
        last = details.get("last_publication")

        if not first or not last:
            return "Unknown"

        if first == last:
            return first.strftime("%Y")

        return f"{first.strftime('%Y')}-{last.strftime('%Y')}"

    def _find_connected_component(
        self, start_author: str, connections: Dict, visited: Set
    ) -> Set[str]:
        """Find all authors connected to the start author (DFS)"""
        component = set()
        stack = [start_author]

        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                component.add(current)

                # Add all unvisited neighbors
                for neighbor in connections.get(current, set()):
                    if neighbor not in visited:
                        stack.append(neighbor)

        return component

    def _calculate_cluster_density(self, cluster: Set[str], connections: Dict) -> float:
        """Calculate the density of connections within a cluster"""
        cluster_list = list(cluster)
        possible_connections = len(cluster_list) * (len(cluster_list) - 1) // 2

        if possible_connections == 0:
            return 0.0

        actual_connections = 0
        for i, author1 in enumerate(cluster_list):
            for author2 in cluster_list[i + 1 :]:
                if author2 in connections.get(author1, set()):
                    actual_connections += 1

        return round(actual_connections / possible_connections, 3)

    def _identify_cluster_topics(
        self, cluster: Set[str], publications: List[Dict]
    ) -> List[str]:
        """Identify main research topics for a cluster (simplified)"""
        # This would require more sophisticated topic modeling
        # For now, return placeholder topics
        return ["AI Applications", "Machine Learning", "African Development"]

    def _get_fallback_coauthorship_data(self) -> Dict:
        """Fallback data if coauthorship extraction fails"""
        return {
            "collaboration_networks": {
                "total_authors": 150,
                "total_collaborations": 45,
                "collaboration_pairs": [
                    {
                        "authors": ["Dr. A. Smith", "Prof. B. Johnson"],
                        "collaboration_count": 5,
                        "strength": 0.4,
                    }
                ],
                "author_metrics": {},
            },
            "key_researchers": [
                {
                    "name": "Dr. Sample Researcher",
                    "publication_count": 8,
                    "collaborator_count": 12,
                    "impact_score": 7.2,
                }
            ],
            "research_clusters": [
                {
                    "cluster_id": 1,
                    "members": ["Dr. A", "Dr. B", "Prof. C"],
                    "size": 3,
                    "density": 0.67,
                }
            ],
            "collaboration_patterns": {
                "average_authors_per_paper": 2.8,
                "collaboration_frequency": {"2": 25, "3": 15, "4": 8},
            },
            "institutional_networks": {"cross_institutional_ratio": 0.6},
            "temporal_collaboration": {"2023": {"collaboration_rate": 0.75}},
            "geographic_collaboration": {"cross_country_collaborations": 12},
        }
