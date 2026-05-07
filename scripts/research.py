#!/usr/bin/env python3
"""
seo-agi research orchestrator.
Pulls SERP data, keyword data, PAA questions, and competitor content analysis
into a single research.json file that feeds content generation.

Usage:
    python3 research.py "<keyword>" [options]

Options:
    --serp-depth=N       Number of SERP results to analyze (default: 10)
    --include-paa        Include People Also Ask extraction (default: true)
    --location=CODE      DataForSEO location code (default: 2840 = US)
    --language=CODE      Language code (default: en)
    --output=FORMAT      Output: json|compact|brief (default: compact)
    --save-dir=PATH      Save raw data (default: ~/.local/share/seo-agi/research/)
    --content-depth=N    Number of top results to parse for content (default: 5)
    --mock               Use fixture data instead of live API calls
"""

import sys
import os
import json
import re
import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# Add parent dir to path for lib imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.env import load_env, load_config, get_credentials, ensure_dirs
from lib.dataforseo import DataForSEOClient
from lib.serp_analyze import analyze_serp


# Minimal English stopword list. Kept inline -- avoiding NLTK / spaCy
# dependency. Covers function words, modal verbs, common copulas, and
# pronouns. Not exhaustive; goal is "filter the obvious noise."
_STOPWORDS = frozenset(
    """
    a about above after again against all am an and any are as at be because
    been before being below between both but by can cant cannot could couldnt
    did didnt do does doesnt doing dont down during each few for from further
    had hadnt has hasnt have havent having he hed hell hes her here heres hers
    herself him himself his how hows i id ill im ive if in into is isnt it its
    itself just lets like me more most mustnt my myself no nor not of off on
    once only or other ought our ours ourselves out over own same shant she
    shed shell shes should shouldnt so some such than that thats the their
    theirs them themselves then there theres these they theyd theyll theyre
    theyve this those through to too under until up very was wasnt we wed
    well were werent weve what whats when whens where wheres which while who
    whos whom why whys with wont would wouldnt you youd youll your youre yours
    yourself yourselves
    """.split()
)


def extract_meta_entities(serp_data: dict) -> list[str]:
    """Extract bolded query-matched entities from competitor SERP description
    snippets. These are the exact tokens Google's snippet generator chose as
    most relevant -- a stronger signal than body-content entity extraction.

    DataForSEO surfaces these in two ways:
      1. A `highlighted` list per organic result (preferred; pre-extracted)
      2. Inline <b>/<strong>/**...** tags in the description (some sources)
    We accept both. Output is deduped, lowercase, ordered by frequency.
    """
    organic = serp_data.get("organic", []) or []
    pattern = re.compile(
        r"<b>(.+?)</b>|<strong>(.+?)</strong>|\*\*(.+?)\*\*",
        re.IGNORECASE | re.DOTALL,
    )
    counter: Counter[str] = Counter()

    def _add(term: str) -> None:
        term = re.sub(r"\s+", " ", term).strip().lower()
        term = term.strip(".,;:!?\"'()[]{}<>")
        if 2 <= len(term) <= 80:
            counter[term] += 1

    for r in organic:
        # Source 1: pre-extracted highlighted phrases
        for phrase in r.get("highlighted") or []:
            if isinstance(phrase, str):
                _add(phrase)
        # Source 2: inline tags in description (fallback)
        desc = r.get("description") or ""
        for m in pattern.finditer(desc):
            term = m.group(1) or m.group(2) or m.group(3) or ""
            _add(term)
    # Most frequent first; ties keep insertion order
    return [t for t, _ in counter.most_common(15)]


def _tokenize(text: str) -> list[str]:
    """Lowercase word tokens, no punctuation, no stopwords, length >= 3."""
    text = re.sub(r"[^A-Za-z0-9\s'-]+", " ", text.lower())
    tokens = []
    for raw in text.split():
        # Drop leading/trailing apostrophes-hyphens, drop pure-numeric junk
        tok = raw.strip("'-")
        if len(tok) < 3:
            continue
        if tok in _STOPWORDS:
            continue
        if tok.isdigit():
            continue
        tokens.append(tok)
    return tokens


def extract_target_ngrams(content_data: list, top_n_competitors: int = 3, top_k: int = 5) -> dict:
    """Scan the body text of the top N ranking competitors and return the
    top K most frequent bigrams (2-word) and trigrams (3-word) phrases.

    Body text comes from each competitor's parsed `headings` (joined) plus,
    where available, the underlying topic primary_content -- which is what
    DataForSEOClient._extract_content already aggregates into word_count.
    Since we don't have raw body text in the parsed output, we use heading
    text as the canonical body proxy: headings carry the topic-load and are
    consistent across competitors. Future versions can extend this by
    plumbing primary_content through.
    """
    body_texts: list[str] = []
    for content in (content_data or [])[:top_n_competitors]:
        if not content:
            continue
        # Heading text (most signal-dense per token)
        headings = content.get("headings") or []
        body_texts.append(" ".join(h.split(": ", 1)[-1] for h in headings))
        # Page title is also high-signal
        title = content.get("title") or ""
        if title:
            body_texts.append(title)

    if not body_texts:
        return {"bigrams": [], "trigrams": []}

    tokens = _tokenize(" ".join(body_texts))
    if len(tokens) < 2:
        return {"bigrams": [], "trigrams": []}

    bigram_counts = Counter(
        " ".join(tokens[i : i + 2]) for i in range(len(tokens) - 1)
    )
    trigram_counts = Counter(
        " ".join(tokens[i : i + 3]) for i in range(len(tokens) - 2)
    )

    return {
        "bigrams": [
            {"phrase": p, "count": c} for p, c in bigram_counts.most_common(top_k)
        ],
        "trigrams": [
            {"phrase": p, "count": c} for p, c in trigram_counts.most_common(top_k)
        ],
    }


def detect_secondary_intent(keyword: str, primary_intent: str, serp_data: dict) -> str:
    """Map secondary intent per the Orcas 1 dual-intent model. The primary
    intent answers 'what did the user type'. The secondary intent answers
    'what do they want to do next'. A page targeting 'best CRM 2026'
    (primary: commercial) usually has a transactional secondary (start
    free trial, book demo). A 'how to park at JFK' page (primary:
    informational) usually has a transactional secondary (reserve a spot).

    Heuristic: invert primary along the funnel.
        informational -> commercial    (compare options after learning)
        commercial    -> transactional (act after comparing)
        transactional -> navigational  (find the seller / brand)
        navigational  -> transactional (act once on the brand)
    Override based on SERP-feature signals when stronger evidence exists.
    """
    funnel_map = {
        "informational": "commercial",
        "commercial": "transactional",
        "transactional": "navigational",
        "navigational": "transactional",
    }
    secondary = funnel_map.get(primary_intent, "transactional")

    organic = serp_data.get("organic", []) or []
    titles_text = " ".join(
        (r.get("title") or "").lower() for r in organic[:5]
    )

    # Strong transactional override
    if any(s in titles_text for s in ["book", "reserve", "buy", "order", "shop", "checkout"]):
        secondary = "transactional"
    # Strong navigational override (lots of brand-domain hits in top 5)
    domains = [r.get("domain", "") for r in organic[:5]]
    if domains and len(set(domains)) <= 2:
        secondary = "navigational"

    return secondary


def parse_args():
    parser = argparse.ArgumentParser(description="SEO-AGI Research")
    parser.add_argument("keyword", help="Target keyword or topic")
    parser.add_argument(
        "--serp-depth", type=int, default=10, help="SERP depth"
    )
    parser.add_argument(
        "--content-depth",
        type=int,
        default=5,
        help="Number of competitors to parse content from",
    )
    parser.add_argument(
        "--location", type=int, default=None, help="Location code"
    )
    parser.add_argument(
        "--language", default=None, help="Language code"
    )
    parser.add_argument(
        "--output",
        choices=["json", "compact", "brief"],
        default="compact",
        help="Output format",
    )
    parser.add_argument(
        "--save-dir", default=None, help="Directory to save research data"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use fixture data (no API calls)",
    )
    return parser.parse_args()


def load_mock_data(keyword: str) -> dict:
    """Load fixture data for testing without API calls."""
    fixtures_dir = (
        Path(__file__).parent.parent / "fixtures"
    )

    serp_fixture = fixtures_dir / "serp_sample.json"
    keywords_fixture = fixtures_dir / "keywords_sample.json"

    serp_data = {"organic": [], "paa": [], "featured_snippet": None}
    related_kw = []

    if serp_fixture.exists():
        with open(serp_fixture) as f:
            serp_data = json.load(f)

    if keywords_fixture.exists():
        with open(keywords_fixture) as f:
            related_kw = json.load(f)

    return {
        "keyword": keyword,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "mock",
        "primary_intent": "commercial",
        "secondary_intent": "transactional",
        "meta_entities": [],
        "target_ngrams": {"bigrams": [], "trigrams": []},
        "serp": serp_data,
        "related_keywords": related_kw,
        "analysis": {
            "intent": "commercial",
            "word_count_stats": {
                "min": 800,
                "max": 3200,
                "median": 1800,
                "recommended_min": 1440,
                "recommended_max": 2340,
            },
            "paa_questions": serp_data.get("paa", []),
            "topic_frequency": [],
            "heading_patterns": {
                "avg_h2_count": 6,
                "avg_h3_count": 8,
                "median_h2_count": 5,
                "median_h3_count": 7,
            },
        },
    }


def run_research(args) -> dict:
    """Execute the full research pipeline."""
    creds = get_credentials()
    config = load_config()

    location = args.location or config["default_location"]
    language = args.language or config["default_language"]

    if args.mock:
        return load_mock_data(args.keyword)

    if not creds["has_dataforseo"]:
        print(
            "NO_DATAFORSEO_CREDS: DataForSEO credentials not found.",
            file=sys.stderr,
        )
        print(
            "Falling back to mock data. For live research, add credentials to "
            "~/.config/seo-agi/.env",
            file=sys.stderr,
        )
        print(
            "Or use Ahrefs/SEMRush MCP tools in Claude Code as alternative data sources.",
            file=sys.stderr,
        )
        # Return a skeleton that the agent can fill in via MCP tools or WebSearch
        return {
            "keyword": args.keyword,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "no-creds-fallback",
            "location": location,
            "language": language,
            "primary_intent": "unknown",
            "secondary_intent": "unknown",
            "meta_entities": [],
            "target_ngrams": {"bigrams": [], "trigrams": []},
            "serp": {"organic": [], "paa": [], "featured_snippet": None},
            "related_keywords": [],
            "analysis": {
                "keyword": args.keyword,
                "intent": "unknown",
                "word_count_stats": {},
                "paa_questions": [],
                "topic_frequency": [],
                "heading_patterns": {},
                "competitors_analyzed": 0,
                "total_organic_results": 0,
                "featured_snippet": None,
            },
            "_fallback_note": (
                "No DataForSEO credentials. Use Ahrefs MCP, SEMRush MCP, "
                "or WebSearch to gather competitive data manually."
            ),
        }

    client = DataForSEOClient(
        creds["dataforseo_login"], creds["dataforseo_password"]
    )

    # Step 1: SERP results
    print(f"Fetching SERP for: {args.keyword}", file=sys.stderr)
    serp_data = client.serp_live(
        args.keyword, location, language, args.serp_depth
    )

    # Step 2: Related keywords
    print("Fetching related keywords...", file=sys.stderr)
    related_kw = client.related_keywords(args.keyword, location, language)

    # Step 3: Parse competitor content (top N)
    content_data = []
    organic = serp_data.get("organic", [])
    parse_count = min(args.content_depth, len(organic))

    for i in range(parse_count):
        url = organic[i].get("url", "")
        if url:
            print(
                f"Parsing content ({i+1}/{parse_count}): {url[:80]}...",
                file=sys.stderr,
            )
            content = client.content_parse(url)
            content_data.append(content)

            # Merge content data back into organic result
            if content:
                organic[i]["word_count"] = content.get("word_count", 0)
                organic[i]["headings"] = content.get("headings", [])
        else:
            content_data.append(None)

    # Step 4: Analyze
    print("Analyzing competitive landscape...", file=sys.stderr)
    analysis = analyze_serp(serp_data, content_data, args.keyword)

    # Step 5: v1.7.1 -- LLM Retrieval signals
    primary_intent = analysis.get("intent", "unknown")
    secondary_intent = detect_secondary_intent(args.keyword, primary_intent, serp_data)
    meta_entities = extract_meta_entities(serp_data)
    target_ngrams = extract_target_ngrams(content_data, top_n_competitors=3, top_k=5)

    # Assemble research output. Surface the new signals at top level for
    # easy brief consumption -- do not bury them inside `analysis`.
    research = {
        "keyword": args.keyword,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "location": location,
        "language": language,
        "source": "dataforseo",
        "primary_intent": primary_intent,
        "secondary_intent": secondary_intent,
        "meta_entities": meta_entities,
        "target_ngrams": target_ngrams,
        "serp": serp_data,
        "related_keywords": related_kw[:20],
        "analysis": analysis,
    }

    return research


def save_research(research: dict, save_dir: str = None):
    """Save research data to disk."""
    ensure_dirs()
    config = load_config()

    if save_dir:
        out_dir = Path(save_dir).expanduser()
    else:
        out_dir = Path.home() / ".local" / "share" / "seo-agi" / "research"

    out_dir.mkdir(parents=True, exist_ok=True)

    # Filename from keyword + date
    slug = (
        research["keyword"]
        .lower()
        .replace(" ", "-")
        .replace("/", "-")[:50]
    )
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{slug}-{date_str}.json"

    filepath = out_dir / filename
    with open(filepath, "w") as f:
        json.dump(research, f, indent=2)

    print(f"Research saved: {filepath}", file=sys.stderr)
    return str(filepath)


def format_compact(research: dict) -> str:
    """Format research as compact human-readable output."""
    lines = []
    kw = research["keyword"]
    analysis = research.get("analysis", {})
    serp = research.get("serp", {})
    organic = serp.get("organic", [])

    lines.append(f"# Research: {kw}")
    lines.append(
        f"Intent: primary={research.get('primary_intent', 'unknown')}, "
        f"secondary={research.get('secondary_intent', 'unknown')}"
    )

    # Word count
    wc = analysis.get("word_count_stats", {})
    if wc:
        lines.append(
            f"Competitor word count: {wc.get('min', '?')}-{wc.get('max', '?')} "
            f"(median: {wc.get('median', '?')})"
        )
        lines.append(
            f"Recommended range: {wc.get('recommended_min', '?')}-"
            f"{wc.get('recommended_max', '?')} words"
        )

    # Top results
    lines.append(f"\n## Top {len(organic)} Results")
    for r in organic[:10]:
        wc_str = (
            f" ({r.get('word_count', '?')} words)"
            if r.get("word_count")
            else ""
        )
        lines.append(f"  {r['position']}. {r['title']}{wc_str}")
        lines.append(f"     {r['url']}")

    # PAA
    paa = analysis.get("paa_questions", serp.get("paa", []))
    if paa:
        lines.append(f"\n## People Also Ask ({len(paa)})")
        for q in paa:
            lines.append(f"  - {q}")

    # Related keywords
    related = research.get("related_keywords", [])
    if related:
        lines.append(f"\n## Related Keywords (top 10)")
        for kw_data in related[:10]:
            lines.append(
                f"  - {kw_data['keyword']} "
                f"(vol: {kw_data['volume']}, "
                f"diff: {kw_data.get('difficulty', '?')})"
            )

    # Topics
    topics = analysis.get("topic_frequency", [])
    if topics:
        lines.append(f"\n## Common Topics Across Competitors")
        for t in topics[:15]:
            lines.append(
                f"  - {t['topic']} (in {t['competitor_count']} pages)"
            )

    # Heading patterns
    hp = analysis.get("heading_patterns", {})
    if hp:
        lines.append(f"\n## Heading Structure")
        lines.append(
            f"  Avg H2s: {hp.get('avg_h2_count', '?')}, "
            f"Avg H3s: {hp.get('avg_h3_count', '?')}"
        )

    # Meta entities (bolded SERP-snippet terms -- v1.7.1)
    meta_ents = research.get("meta_entities", [])
    if meta_ents:
        lines.append(f"\n## Meta Entities (bolded in competitor SERP snippets)")
        for ent in meta_ents[:10]:
            lines.append(f"  - {ent}")

    # Target n-grams (top 3 competitor body text -- v1.7.1)
    ngrams = research.get("target_ngrams", {}) or {}
    bigrams = ngrams.get("bigrams", [])
    trigrams = ngrams.get("trigrams", [])
    if bigrams or trigrams:
        lines.append(
            f"\n## Target N-grams (seed 2+ into AI Summary Nugget)"
        )
        if bigrams:
            lines.append("  Bigrams:")
            for b in bigrams:
                lines.append(f"    - {b['phrase']} ({b['count']}x)")
        if trigrams:
            lines.append("  Trigrams:")
            for t in trigrams:
                lines.append(f"    - {t['phrase']} ({t['count']}x)")

    return "\n".join(lines)


def main():
    args = parse_args()
    research = run_research(args)

    # Save
    filepath = save_research(research, args.save_dir)

    # Output
    if args.output == "json":
        print(json.dumps(research, indent=2))
    elif args.output == "brief":
        # Minimal output for piping into content generation
        analysis = research.get("analysis", {})
        brief_data = {
            "keyword": research["keyword"],
            "primary_intent": research.get("primary_intent"),
            "secondary_intent": research.get("secondary_intent"),
            "meta_entities": research.get("meta_entities", []),
            "target_ngrams": research.get("target_ngrams", {}),
            "word_count_stats": analysis.get("word_count_stats"),
            "paa_questions": analysis.get(
                "paa_questions",
                research.get("serp", {}).get("paa", []),
            ),
            "topic_frequency": analysis.get("topic_frequency", [])[:10],
            "heading_patterns": analysis.get("heading_patterns"),
            "research_file": filepath,
        }
        print(json.dumps(brief_data, indent=2))
    else:
        print(format_compact(research))


if __name__ == "__main__":
    main()
