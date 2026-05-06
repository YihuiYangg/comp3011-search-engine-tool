"""Polite same-site crawler for https://quotes.toscrape.com/."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class CrawledPage:
    """HTML fetched from one URL."""

    url: str
    html: str


class CrawlerError(RuntimeError):
    """Raised when the crawler cannot complete a requested action."""


class PoliteCrawler:
    """Breadth-first crawler restricted to the starting website.

    The default delay is 6 seconds to satisfy the coursework politeness window.
    Tests can inject delay_seconds=0 to avoid slow test execution.
    """

    def __init__(
        self,
        base_url: str,
        *,
        delay_seconds: float = 6.0,
        timeout_seconds: float = 15.0,
        max_pages: int = 120,
        session: requests.Session | None = None,
    ) -> None:
        if delay_seconds < 0:
            raise ValueError("delay_seconds cannot be negative")
        if max_pages <= 0:
            raise ValueError("max_pages must be positive")

        self.base_url = self._normalise_url(base_url)
        self.allowed_netloc = urlparse(self.base_url).netloc
        self.delay_seconds = delay_seconds
        self.timeout_seconds = timeout_seconds
        self.max_pages = max_pages
        self.session = session or requests.Session()
        self._last_request_at: float | None = None

    @staticmethod
    def _normalise_url(url: str) -> str:
        """Remove fragments and normalise trailing slashes for deterministic URLs."""

        no_fragment, _fragment = urldefrag(url)
        parsed = urlparse(no_fragment)
        path = parsed.path or "/"
        if not path.endswith("/") and "." not in path.rsplit("/", 1)[-1]:
            path += "/"
        return parsed._replace(path=path, query="").geturl()

    def _is_allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and parsed.netloc == self.allowed_netloc

    def _wait_if_needed(self) -> None:
        if self._last_request_at is None:
            return
        elapsed = time.monotonic() - self._last_request_at
        wait_time = self.delay_seconds - elapsed
        if wait_time > 0:
            time.sleep(wait_time)

    def _request(self, url: str) -> str:
        """Fetch a URL politely and return HTML text."""

        self._wait_if_needed()
        response = self.session.get(
            url,
            timeout=self.timeout_seconds,
            headers={"User-Agent": "COMP3011-coursework-search-tool/1.0"},
        )
        self._last_request_at = time.monotonic()
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if "html" not in content_type.lower():
            raise CrawlerError(f"URL did not return HTML: {url}")
        return response.text

    def extract_links(self, html: str, current_url: str) -> list[str]:
        """Extract normalised same-site links from a page."""

        soup = BeautifulSoup(html, "html.parser")
        links: list[str] = []
        seen: set[str] = set()
        for anchor in soup.find_all("a", href=True):
            absolute = self._normalise_url(urljoin(current_url, anchor["href"]))
            parsed = urlparse(absolute)

            # The login/logout links are not quote-content pages. Skipping them
            # avoids unnecessary 404 warnings while keeping the crawler focused
            # on pages that should be indexed for the coursework search tool.
            if parsed.path.rstrip("/") in {"/login", "/logout"}:
                continue

            if self._is_allowed(absolute) and absolute not in seen:
                seen.add(absolute)
                links.append(absolute)
        return links

    def crawl(self) -> list[CrawledPage]:
        """Crawl pages starting from base_url using breadth-first traversal."""

        queue: deque[str] = deque([self.base_url])
        queued: set[str] = {self.base_url}
        visited: set[str] = set()
        pages: list[CrawledPage] = []

        while queue and len(pages) < self.max_pages:
            url = queue.popleft()
            queued.discard(url)
            if url in visited:
                continue

            try:
                html = self._request(url)
            except requests.RequestException as exc:
                print(f"Warning: failed to fetch {url}: {exc}")
                visited.add(url)
                continue
            except CrawlerError as exc:
                print(f"Warning: skipped {url}: {exc}")
                visited.add(url)
                continue

            visited.add(url)
            pages.append(CrawledPage(url=url, html=html))

            for link in self.extract_links(html, url):
                if link not in visited and link not in queued:
                    queue.append(link)
                    queued.add(link)

        return pages
