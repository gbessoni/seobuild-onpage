"""Tests for v1.7.1 research-pipeline additions:
extract_meta_entities, extract_target_ngrams, detect_secondary_intent.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from research import (
    extract_meta_entities,
    extract_target_ngrams,
    detect_secondary_intent,
    _tokenize,
    _STOPWORDS,
)


# --- extract_meta_entities ----------------------------------------------------

def test_meta_entities_from_highlighted_field():
    """DataForSEO returns bolded snippet phrases in `highlighted` arrays.
    These are the primary source for the Meta Entity Isolation check."""
    serp = {
        "organic": [
            {
                "title": "JFK Parking",
                "description": "plain description text",
                "highlighted": ["JFK long-term parking", "from $12.95/day"],
            },
            {
                "title": "SpotHero",
                "description": "another result",
                "highlighted": ["JFK long-term parking", "covered garages"],
            },
        ]
    }
    out = extract_meta_entities(serp)
    # "jfk long-term parking" appears in 2 results -> top of list
    assert out[0] == "jfk long-term parking"
    assert "covered garages" in out
    assert "from $12.95/day" in out


def test_meta_entities_from_inline_tags_fallback():
    """Some sources embed <b>/<strong>/** in description text. Must be
    parsed as a fallback so we don't lose the signal."""
    serp = {
        "organic": [
            {
                "description": "Try <b>JFK parking</b> from $20/day with <strong>free shuttle</strong>.",
                "highlighted": [],
            },
            {
                "description": "Markdown variant: **JFK parking** is competitive.",
                "highlighted": [],
            },
        ]
    }
    out = extract_meta_entities(serp)
    assert "jfk parking" in out  # appears 2x across both formats
    assert "free shuttle" in out


def test_meta_entities_empty_when_no_signal():
    serp = {"organic": [{"description": "no markup here", "highlighted": []}]}
    assert extract_meta_entities(serp) == []


def test_meta_entities_handles_missing_organic():
    assert extract_meta_entities({}) == []
    assert extract_meta_entities({"organic": None}) == []


def test_meta_entities_dedupes_and_orders_by_frequency():
    serp = {
        "organic": [
            {"highlighted": ["alpha", "beta"], "description": ""},
            {"highlighted": ["alpha", "ALPHA"], "description": ""},  # case fold
            {"highlighted": ["alpha", "gamma"], "description": ""},
        ]
    }
    out = extract_meta_entities(serp)
    assert out[0] == "alpha"  # 4 occurrences, lowercased
    assert "beta" in out
    assert "gamma" in out


# --- extract_target_ngrams ----------------------------------------------------

def test_ngrams_extracts_bigrams_and_trigrams():
    """Top 3 competitors' headings -> top 5 bigrams + trigrams.
    Stopwords ('and', 'for') must be filtered. Numeric junk filtered."""
    content_data = [
        {
            "title": "JFK Airport Parking Guide",
            "headings": [
                "H2: JFK Airport Parking Rates",
                "H2: JFK Airport Parking Lots",
                "H3: Long Term JFK Airport Parking",
            ],
        },
        {
            "title": "Airport Parking JFK Comparison",
            "headings": [
                "H2: Airport Parking Costs",
                "H2: Airport Parking Reviews",
            ],
        },
        {
            "title": "JFK Long Term Parking",
            "headings": ["H2: JFK Long Term", "H2: Long Term Parking 2026"],
        },
    ]
    out = extract_target_ngrams(content_data, top_n_competitors=3, top_k=5)
    bigrams = [b["phrase"] for b in out["bigrams"]]
    trigrams = [t["phrase"] for t in out["trigrams"]]

    # Top bigram should be airport parking or jfk airport (both very frequent)
    assert any("airport parking" in b or "jfk airport" in b for b in bigrams[:3])
    # Trigrams should include jfk airport parking variants
    assert any("airport parking" in t for t in trigrams)
    # No bigrams should contain pure stopwords
    for b in bigrams:
        for tok in b.split():
            assert tok not in _STOPWORDS, f"stopword in bigram: {b}"


def test_ngrams_handles_only_top_n():
    """Should respect top_n_competitors -- if we pass 5 competitors but ask
    for top 3, only the first 3 are scanned."""
    content_data = [
        {"title": "alpha alpha alpha", "headings": []},
        {"title": "alpha alpha alpha", "headings": []},
        {"title": "alpha alpha alpha", "headings": []},
        {"title": "ZZZ never appears", "headings": ["H2: ZZZ never appears"]},
        {"title": "ZZZ never appears", "headings": ["H2: ZZZ never appears"]},
    ]
    out = extract_target_ngrams(content_data, top_n_competitors=3, top_k=5)
    bigrams = [b["phrase"] for b in out["bigrams"]]
    # 'zzz' content from competitors 4-5 should not appear
    for b in bigrams:
        assert "zzz" not in b.lower()


def test_ngrams_empty_input():
    assert extract_target_ngrams([], 3, 5) == {"bigrams": [], "trigrams": []}
    assert extract_target_ngrams(None, 3, 5) == {"bigrams": [], "trigrams": []}
    assert extract_target_ngrams([None, None], 3, 5) == {"bigrams": [], "trigrams": []}


def test_tokenize_filters_stopwords_and_short():
    tokens = _tokenize("The JFK airport is in New York and is very busy.")
    assert "the" not in tokens
    assert "is" not in tokens
    assert "and" not in tokens
    assert "in" not in tokens
    assert "jfk" in tokens
    assert "airport" in tokens
    assert "york" in tokens
    assert "busy" in tokens


def test_tokenize_drops_pure_digits():
    tokens = _tokenize("Park here for $20 in 2026 today")
    assert "20" not in tokens
    assert "2026" not in tokens
    assert "park" in tokens
    assert "today" in tokens


# --- detect_secondary_intent --------------------------------------------------

def test_secondary_intent_funnel_default():
    """Without strong SERP signals, secondary intent follows the funnel:
    informational -> commercial, commercial -> transactional, etc."""
    empty_serp = {"organic": []}
    assert detect_secondary_intent("kw", "informational", empty_serp) == "commercial"
    assert detect_secondary_intent("kw", "commercial", empty_serp) == "transactional"
    assert detect_secondary_intent("kw", "transactional", empty_serp) == "navigational"
    assert detect_secondary_intent("kw", "navigational", empty_serp) == "transactional"


def test_secondary_intent_transactional_override():
    """Strong transactional words in top-5 titles should pull secondary
    to transactional regardless of funnel default."""
    serp = {
        "organic": [
            {"title": "Book JFK parking now", "domain": "a.com"},
            {"title": "Reserve your spot", "domain": "b.com"},
            {"title": "JFK parking guide", "domain": "c.com"},
            {"title": "Parking info", "domain": "d.com"},
            {"title": "Long term parking", "domain": "e.com"},
        ]
    }
    # primary informational normally maps to commercial, but 'book/reserve'
    # in titles forces transactional
    assert detect_secondary_intent("kw", "informational", serp) == "transactional"


def test_secondary_intent_navigational_override():
    """If <=2 distinct domains hold the top 5, the intent is brand-driven."""
    serp = {
        "organic": [
            {"title": "JFK parking", "domain": "spothero.com"},
            {"title": "Book now", "domain": "spothero.com"},
            {"title": "Reviews", "domain": "spothero.com"},
            {"title": "Locations", "domain": "spothero.com"},
            {"title": "Rates", "domain": "spothero.com"},
        ]
    }
    # With "Book"/"Reserve" not present here, navigational override kicks in
    assert detect_secondary_intent("kw", "informational", serp) == "navigational"


if __name__ == "__main__":
    test_meta_entities_from_highlighted_field()
    test_meta_entities_from_inline_tags_fallback()
    test_meta_entities_empty_when_no_signal()
    test_meta_entities_handles_missing_organic()
    test_meta_entities_dedupes_and_orders_by_frequency()
    test_ngrams_extracts_bigrams_and_trigrams()
    test_ngrams_handles_only_top_n()
    test_ngrams_empty_input()
    test_tokenize_filters_stopwords_and_short()
    test_tokenize_drops_pure_digits()
    test_secondary_intent_funnel_default()
    test_secondary_intent_transactional_override()
    test_secondary_intent_navigational_override()
    print("All tests passed.")
