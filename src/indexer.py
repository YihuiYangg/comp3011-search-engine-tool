"""Text extraction and inverted-index construction utilities.

The inverted index format is deliberately JSON-friendly:

{
    "word": {
        "https://example/page": {
            "frequency": 2,
            "positions": [3, 19]
        }
    }
}

Positions are zero-based token positions within a page's visible text.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Iterable

from bs4 import BeautifulSoup

# Keeps words/numbers and simple contractions such as "don't".
TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?", re.IGNORECASE)


@dataclass(frozen=True)
class Document:
    """A crawled page ready to be indexed."""

    url: str
    html: str


def extract_visible_text(html: str) -> str:
    """Extract human-visible text from an HTML document.

    Script, style, noscript, and SVG elements are removed because their text is
    not useful for a simple content search engine.
    """

    soup = BeautifulSoup(html, "html.parser")
    for element in soup(["script", "style", "noscript", "svg"]):
        element.decompose()
    return soup.get_text(separator=" ", strip=True)


def tokenize(text: str) -> list[str]:
    """Return case-normalised word tokens from text."""

    return [match.group(0).lower() for match in TOKEN_RE.finditer(text)]


def index_document(url: str, html: str) -> dict[str, dict[str, dict[str, list[int] | int]]]:
    """Build an inverted index for a single document."""

    text = extract_visible_text(html)
    tokens = tokenize(text)
    index: dict[str, dict[str, dict[str, list[int] | int]]] = {}

    positions_by_word: DefaultDict[str, list[int]] = defaultdict(list)
    for position, token in enumerate(tokens):
        positions_by_word[token].append(position)

    for word, positions in positions_by_word.items():
        index[word] = {
            url: {
                "frequency": len(positions),
                "positions": positions,
            }
        }
    return index


def merge_indices(
    base: dict[str, dict[str, dict[str, list[int] | int]]],
    addition: dict[str, dict[str, dict[str, list[int] | int]]],
) -> dict[str, dict[str, dict[str, list[int] | int]]]:
    """Merge one inverted index into another and return the merged index."""

    for word, postings in addition.items():
        base.setdefault(word, {})
        for url, stats in postings.items():
            base[word][url] = stats
    return base


def build_index(documents: Iterable[Document]) -> dict[str, dict[str, dict[str, list[int] | int]]]:
    """Build a complete inverted index from a sequence of documents."""

    index: dict[str, dict[str, dict[str, list[int] | int]]] = {}
    for document in documents:
        merge_indices(index, index_document(document.url, document.html))
    return index
