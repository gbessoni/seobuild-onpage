# seo-agi Technical Specification

Current as of **v2.5.0**. This document describes the data layer and execution
architecture. For the content rules themselves, see `SKILL.md`.

## Overview

seo-agi (shipped as `seobuild-onpage`) is a Claude Code skill that writes and
rewrites pages optimized for AI answer engines as well as classic organic
search. It bridges the gap between "SEO audit tools" and "content generation"
by making live competitive data the input to the writing, not a separate
workflow.

The companion verification agent, **seobuild-verify**, lives in its own
repository (`gbessoni/seobuild-verify`) and resolves the `{{VERIFY}}` family of
tags this engine emits. It is not part of this codebase.

## Architecture

```
User prompt ("write a page for airport parking JFK")
  │
  ▼
SKILL.md (orchestrator, read by the agent at runtime)
  │
  ├── scripts/research.py          SERP + keyword + competitor content
  │     ├── lib/env.py             config + credential loader
  │     ├── lib/dataforseo.py      DataForSEO REST client
  │     ├── lib/massive.py         Massive Web Render client (v1.9.0)
  │     └── lib/serp_analyze.py    intent detection + gap analysis
  │
  ├── scripts/gsc_pull.py          Search Console performance + ghost paths
  │     └── lib/gsc_client.py      GSC API client
  │
  ├── scripts/tributary_gen.py     Tier 1/Tier 2 off-page companion briefs
  │
  ├── scripts/setup.py             first-run config
  │
  └── references/
        ├── page-templates.md      structural templates by page type
        ├── schema-patterns.md     JSON-LD + inline RDFa patterns
        └── quality-checklist.md   70-point scoring rubric
```

## Content Parsing: Massive primary, DataForSEO fallback

As of v1.9.0, competitor page content is parsed by **Massive Web Render** when
`MASSIVE_API_TOKEN` is set, because it returns rendered markdown including
JavaScript-loaded content that DataForSEO's parser misses.

Fallback is **per URL, not per run**: if Massive errors or returns empty for a
single competitor, that one URL falls back to DataForSEO and the run continues.
A partial Massive outage cannot break a research run. The parser used for each
URL is recorded in `research.content_parsers`.

SERP results and keyword data continue to come from DataForSEO. Massive's
`/search` endpoint returns only "also-searched" suggestions, not organic
results, so it is not used for SERP.

## Data Flow

### Write flow

```
1. FORENSIC SERP AUDIT
   QDD check, Site vs. Page audit, competitor EMQ ratio (context only
   since v2.3.0), CVR estimate.

2. GHOST PATH CHECK (optional, GSC-connected sites)
   gsc_pull.py --ghost-paths finds URLs earning impressions that 404.

3. RESEARCH
   DataForSEO SERP          top N organic, PAA, highlighted snippet phrases
   DataForSEO Labs          related keywords, volume, difficulty
   Massive or DataForSEO    competitor page content per URL
   Output: research JSON saved to ~/.local/share/seo-agi/research/

4. ANALYZE
   Word count stats, heading patterns, topic frequency, intent detection,
   meta entities, target n-grams, missing spokes, DOM nesting audit.

5. BRIEF
   Agent assembles the brief from research output plus SKILL.md rules.
   Blocks on missing brand differentiators (v1.9.1).

6. WRITE
   500-token QFO chunks, entity-fact pairing, named source attribution,
   5+ outbound citations, strict phrase placement, schema markup.
   Output: ~/Documents/SEO-AGI/pages/

7. SCORE
   70-point checklist printed as a scorecard. Below 60/70 requires revision.
```

### Rewrite flow

Same as above, plus:

- Ingest the existing URL or file, extract title/meta/headings/word count
- Gap analysis against the current top 3
- **410 Prune Protocol** (v1.7.1): every legacy URL gets an explicit `301`
  (topic survives, consolidate equity) or `410` (thin, cannibalizing, or
  out-of-circle) recommendation. Silent leave-as-is is not an acceptable output.
- Output rewritten page plus a change summary to `~/Documents/SEO-AGI/rewrites/`

## DataForSEO endpoints used

| Endpoint | Purpose | Used in |
|---|---|---|
| `/v3/serp/google/organic/live/advanced` | Organic results, PAA, `highlighted` snippet phrases | `dataforseo.py` |
| `/v3/dataforseo_labs/google/related_keywords/live` | Related keywords, volume, difficulty | `dataforseo.py` |
| `/v3/dataforseo_labs/google/keyword_suggestions/live` | Keyword ideation | `dataforseo.py` |
| `/v3/on_page/content_parsing/live` | Competitor content (fallback parser) | `dataforseo.py` |

**Response shape notes.** `content_parsing/live` does not return flat
`h1`/`h2`/`h3` arrays. Headings live in `page_content.main_topic[]` and
`page_content.secondary_topic[]` as objects carrying `h_title` and `level`.
There is no `plain_text_word_count` field; word count is computed from
`page_as_markdown` with a fallback that walks `primary_content[].text`.
Bolded query-matched snippet phrases arrive in a per-result `highlighted`
array, not as inline `<b>` tags.

## Massive Web Render

| Endpoint | Purpose | Used in |
|---|---|---|
| `/browser?url=...&format=markdown&country=..` | Rendered page markdown | `massive.py` |

`MassiveClient.content_parse()` returns the same shape as
`DataForSEOClient._extract_content()` (`title`, `word_count`, `headings`,
`plain_text_size`, `links`) so it is a drop-in substitute.

## Google Search Console

| Method | Purpose | Used in |
|---|---|---|
| `searchanalytics.query()` | Query and page performance | `gsc_pull.py` |

**Crawl Stats is not available in the API.** The Search Console API covers
Search Analytics, Sites, Sitemaps, and URL Inspection only. The
`Crawl Stats > By purpose > Discovery` report is UI-only. Ghost path detection
therefore has two paths:

- `--ghost-paths` queries Search Analytics for impression-earning pages and
  checks which return 404. This is the API-accessible proxy.
- `--crawl-stats-csv=<path>` ingests a manual UI export and isolates
  Discovery-purpose 404s.

Both run results through a junk-path filter that blocks exploit probes,
scraper-invented URLs, and malformed paths so they never become generated pages.

## Configuration

```
~/.config/seo-agi/
├── .env              API credentials
└── config.json       default location, language, site, serp depth
```

The config directory name is `seo-agi`, hardcoded as `CONFIG_DIR` in
`lib/env.py`. It is deliberately not renamed to match the repository name.

### Recognized credentials

| Variable | Required | Purpose |
|---|---|---|
| `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD` | Yes | SERP, keywords, fallback content parsing |
| `MASSIVE_API_TOKEN` | No | Primary content parser when present |
| `GSC_SERVICE_ACCOUNT_PATH` | No | Search Console performance and ghost paths |
| `AHREFS_API_KEY` / `SEMRUSH_API_KEY` | No | Supplementary keyword data |

## Research output schema

Signals are surfaced at the top level for direct brief consumption rather than
buried inside `analysis`.

```json
{
  "keyword": "airport parking JFK",
  "timestamp": "2026-10-07T14:30:00+00:00",
  "location": 2840,
  "language": "en",
  "source": "dataforseo",
  "content_parsers": {"massive": 4, "dataforseo-fallback": 1},

  "primary_intent": "commercial",
  "secondary_intent": "transactional",
  "meta_entities": ["jfk long-term self parking at kennedy airport from $12.95"],
  "target_ngrams": {
    "bigrams":  [{"phrase": "jfk airport", "count": 7}],
    "trigrams": [{"phrase": "jfk airport parking", "count": 4}]
  },
  "differentiators": ["women-owned", "24/7 service"],
  "missing_spokes": [{"anchor": "EV charging stations", "competitor_count": 2}],
  "structural_directives": {
    "snippet_answer_container": "block-level wrapper, never a bare <p>",
    "anti_paragraph_rule": true,
    "max_dom_nesting_depth": 3,
    "outbound_citations_min": 5,
    "strict_phrase_placement": "Title and H1 only",
    "entity_fact_pairing": "bind every entity to a hard fact",
    "intent_divergence": "strip CTAs if informational, feature if local",
    "anti_boilerplate_linking": "contextual per chunk",
    "anti_nlp_stuffing": "no force-repeated entity lists"
  },
  "dom_nesting": {"target_max_depth": 3, "assessed_count": 0, "flagged": [],
                  "status": "not_assessed (no raw HTML from current parsers)"},
  "affiliate": {"mode": "none"},

  "serp": {"organic": [], "paa": [], "featured_snippet": null},
  "related_keywords": [],
  "analysis": {
    "intent": "commercial",
    "word_count_stats": {},
    "paa_questions": [],
    "topic_frequency": [],
    "heading_patterns": {}
  }
}
```

## Page frontmatter

```yaml
---
title: "Airport Parking at JFK: Rates, Lots & Shuttle Guide"
meta_description: "Compare JFK parking from $8/day. Official lots, off-site savings, shuttle times."
target_keyword: "airport parking JFK"
secondary_keywords: ["JFK long term parking", "cheap parking near JFK"]
search_intent: "commercial"
secondary_intent: "transactional"
page_type: "service-location"
schema_type: "FAQPage, LocalBusiness, BreadcrumbList"
word_count: 2200
reddit_test: "r/travel -- passes: break-even math, terminal tips, real pricing"
information_gain: "EV charging availability, cell phone lot capacity"
created: "2026-10-07"
research_file: "~/.local/share/seo-agi/research/airport-parking-jfk-20261007.json"
---
```

## Testing

Tests are plain executable scripts, not a pytest suite. Each file runs
standalone and prints `All tests passed.` on success.

```bash
python3 tests/test_env.py
python3 tests/test_dataforseo.py
python3 tests/test_serp_analyze.py
python3 tests/test_massive.py
python3 tests/test_research_v171.py
python3 tests/test_research_v191.py
python3 tests/test_research_v200.py
python3 tests/test_research_v220.py
python3 tests/test_gsc_ghost_paths.py
```

`python3 -m unittest discover tests/` collects zero tests, because these files
do not subclass `unittest.TestCase`. Run them directly.

Mock mode needs no credentials:

```bash
python3 scripts/research.py "test keyword" --mock --output=compact
```

Fixtures in `fixtures/` provide sample API responses for offline development.
