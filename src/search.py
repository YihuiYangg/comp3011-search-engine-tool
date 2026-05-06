"""Index storage, retrieval, and query processing for the search tool."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .crawler import PoliteCrawler
from .indexer import Document, build_index, tokenize

Index = dict[str, dict[str, dict[str, int | list[int]]]]


class SearchEngine:
    """Coordinates crawling, indexing, saving/loading, and searching."""

    def __init__(
        self,
        *,
        base_url: str = "https://quotes.toscrape.com/",
        index_path: str | Path = "data/index.json",
        delay_seconds: float = 6.0,
        max_pages: int = 120,
    ) -> None:
        self.base_url = base_url
        self.index_path = Path(index_path)
        self.delay_seconds = delay_seconds
        self.max_pages = max_pages
        self.index: Index = {}
        self.page_count = 0

    def build(self) -> None:
        """Crawl the target website and build a fresh inverted index."""

        crawler = PoliteCrawler(
            self.base_url,
            delay_seconds=self.delay_seconds,
            max_pages=self.max_pages,
        )
        crawled_pages = crawler.crawl()
        documents = [Document(url=page.url, html=page.html) for page in crawled_pages]
        self.index = build_index(documents)  # type: ignore[assignment]
        self.page_count = len(crawled_pages)

    def save(self) -> None:
        """Persist the index to a JSON file."""

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "base_url": self.base_url,
            "page_count": self.page_count,
            "index": self.index,
        }
        self.index_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def load(self) -> None:
        """Load a previously saved JSON index."""

        if not self.index_path.exists():
            raise FileNotFoundError(
                f"Index file not found at {self.index_path}. Run 'build' first."
            )
        payload = json.loads(self.index_path.read_text(encoding="utf-8"))
        self.base_url = payload.get("base_url", self.base_url)
        self.page_count = int(payload.get("page_count", 0))
        self.index = payload["index"]

    def print_word(self, word: str) -> dict[str, dict[str, int | list[int]]]:
        """Return the posting list for one word."""

        tokens = tokenize(word)
        if len(tokens) != 1:
            raise ValueError("print expects exactly one word")
        return self.index.get(tokens[0], {})

    def find(self, query: str) -> list[dict[str, Any]]:
        """Find pages containing all query terms, ranked by total term frequency."""

        terms = tokenize(query)
        if not terms:
            return []

        posting_lists = [self.index.get(term, {}) for term in terms]
        if any(not postings for postings in posting_lists):
            return []

        common_urls = set(posting_lists[0].keys())
        for postings in posting_lists[1:]:
            common_urls &= set(postings.keys())

        results: list[dict[str, Any]] = []
        for url in common_urls:
            term_stats = {
                term: self.index[term][url]
                for term in sorted(set(terms))
                if url in self.index.get(term, {})
            }
            score = sum(int(stats["frequency"]) for stats in term_stats.values())
            results.append(
                {
                    "url": url,
                    "score": score,
                    "terms": term_stats,
                }
            )

        return sorted(results, key=lambda item: (-item["score"], item["url"]))
