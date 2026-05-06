import json

import pytest

from src.search import SearchEngine


def make_engine(tmp_path):
    engine = SearchEngine(index_path=tmp_path / "index.json", delay_seconds=0)
    engine.index = {
        "good": {
            "https://example.test/1/": {"frequency": 2, "positions": [0, 5]},
            "https://example.test/2/": {"frequency": 1, "positions": [3]},
        },
        "friends": {
            "https://example.test/1/": {"frequency": 1, "positions": [1]},
        },
    }
    engine.page_count = 2
    return engine


def test_print_word_returns_postings_case_insensitively(tmp_path):
    engine = make_engine(tmp_path)
    postings = engine.print_word("GOOD")
    assert set(postings) == {"https://example.test/1/", "https://example.test/2/"}


def test_print_rejects_multiple_words(tmp_path):
    engine = make_engine(tmp_path)
    with pytest.raises(ValueError):
        engine.print_word("good friends")


def test_find_single_word_ranked_by_frequency(tmp_path):
    engine = make_engine(tmp_path)
    results = engine.find("good")
    assert [result["url"] for result in results] == [
        "https://example.test/1/",
        "https://example.test/2/",
    ]


def test_find_multi_word_query_uses_and_semantics(tmp_path):
    engine = make_engine(tmp_path)
    results = engine.find("good friends")
    assert len(results) == 1
    assert results[0]["url"] == "https://example.test/1/"
    assert results[0]["score"] == 3


def test_find_handles_empty_and_nonexistent_queries(tmp_path):
    engine = make_engine(tmp_path)
    assert engine.find("") == []
    assert engine.find("wordnotintheindex") == []


def test_save_and_load_round_trip(tmp_path):
    engine = make_engine(tmp_path)
    engine.save()

    loaded = SearchEngine(index_path=tmp_path / "index.json")
    loaded.load()

    assert loaded.index == engine.index
    assert loaded.page_count == 2
