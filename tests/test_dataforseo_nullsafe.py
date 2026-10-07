"""Null-safety regression tests for the DataForSEO client.

DataForSEO returns `null` rather than an empty value for many fields on
zero-result and long-tail queries. A present-but-null field crashed the
client in several places. PR #1 fixed three of them; this file covers all
of them so the class of bug cannot reappear.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.dataforseo import DataForSEOClient

C = DataForSEOClient("test", "test")


def _serp(items):
    return {"tasks": [{"result": [{"items": items, "se_results_count": 0}]}]}


def _kw(items):
    return {"tasks": [{"result": [{"items": items}]}]}


# --- fixed by PR #1 -----------------------------------------------------------

def test_serp_items_null():
    """items key present but null -> must not raise TypeError."""
    out = C._extract_serp(_serp(None))
    assert out["organic"] == []
    assert out["paa"] == []


def test_keyword_volume_null_does_not_break_sort():
    """_extract_keywords sorts on volume. A null volume crashed the sort,
    so one long-tail keyword with no volume killed the whole pull."""
    out = C._extract_keywords(_kw([
        {"keyword_data": {"keyword": "a",
                          "keyword_info": {"search_volume": None, "cpc": None, "competition": None},
                          "keyword_properties": {"keyword_difficulty": 5}}},
        {"keyword_data": {"keyword": "b",
                          "keyword_info": {"search_volume": 100, "cpc": 1.0, "competition": 0.5},
                          "keyword_properties": {"keyword_difficulty": 9}}},
    ]))
    assert len(out) == 2
    assert out[0]["keyword"] == "b"          # sorted desc by volume
    assert out[1]["volume"] == 0             # null coerced, not None
    assert out[1]["cpc"] == 0
    assert out[1]["competition"] == 0


def test_keyword_properties_null():
    out = C._extract_keywords(_kw([
        {"keyword_data": {"keyword": "a",
                          "keyword_info": {"search_volume": 10, "cpc": 1, "competition": 0.1},
                          "keyword_properties": None}},
    ]))
    assert out[0]["difficulty"] == 0


# --- gaps PR #1 left behind ---------------------------------------------------

def test_nested_paa_items_null():
    """A people_also_ask block whose own items array is null."""
    out = C._extract_serp(_serp([{"type": "people_also_ask", "items": None}]))
    assert out["paa"] == []


def test_keyword_info_object_null():
    """PR #1 guarded the values inside keyword_info but not the object."""
    out = C._extract_keywords(_kw([
        {"keyword_data": {"keyword": "a", "keyword_info": None,
                          "keyword_properties": {"keyword_difficulty": 3}}},
    ]))
    assert out[0]["volume"] == 0
    assert out[0]["difficulty"] == 3


def test_content_parse_items_null():
    assert C._extract_content({"tasks": [{"result": [{"items": None}]}]}) is None


# --- adjacent null tolerance --------------------------------------------------

def test_organic_fields_null():
    out = C._extract_serp(_serp([
        {"type": "organic", "rank_absolute": 1, "url": None, "domain": None,
         "title": None, "description": None, "highlighted": None},
    ]))
    assert out["organic"][0]["highlighted"] == []


def test_everything_null_at_once():
    """Worst case: a fully null response must degrade, not explode."""
    assert C._extract_serp({"tasks": [{"result": None}]})["organic"] == []
    assert C._extract_keywords({"tasks": [{"result": None}]}) == []
    assert C._extract_content({"tasks": [{"result": None}]}) is None


if __name__ == "__main__":
    test_serp_items_null()
    test_keyword_volume_null_does_not_break_sort()
    test_keyword_properties_null()
    test_nested_paa_items_null()
    test_keyword_info_object_null()
    test_content_parse_items_null()
    test_organic_fields_null()
    test_everything_null_at_once()
    print("All tests passed.")
