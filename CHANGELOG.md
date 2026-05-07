# Changelog

All notable changes to seo-agi are documented here.

## [1.7.1] - 2026-05-07

### Added
- **Meta-Specific Entity Isolation**: `extract_meta_entities()` mines bolded query-matched phrases from the `highlighted` field of competitor SERP results (with inline `<b>`/`<strong>`/`**` fallback parsing). These are the entities Google's snippet generator already validated as relevant -- a stronger signal than body-content extraction.
- **Bigram/Trigram AI Alignment**: `extract_target_ngrams()` tokenizes the top 3 ranking competitors' headings + titles, filters via an inlined English stopword list, and returns the top 5 bigrams and top 5 trigrams. Output seeds the AI Summary Nugget for LLM-retrieval token overlap.
- **Primary + Secondary Intent (Orcas 1)**: `detect_secondary_intent()` maps the funnel-next intent (informational → commercial → transactional → navigational), with overrides for transactional title signals (book/reserve/buy) and brand-domain dominance in the top 5.
- **45-point quality checklist**: adds Meta Entity Isolation, N-Gram Alignment, Dual-Intent, and Status Code Governance checks. Passing threshold raised to 36/45.
- **Technical Codebase Execution Rules** (SKILL.md): when the skill runs inside a project repo, it detects the framework (Next.js, Astro, Gatsby, Hugo, etc.), injects semantic HTML into source files, and emits `.htaccess` / Nginx / `next.config.js` redirect snippets for 301/410 recommendations.
- **The 410 Prune Protocol** in the rewrite workflow: every legacy URL gets an explicit 301 (preserve equity) or 410 (prune) recommendation. Silent leave-as-is is no longer acceptable.

### Changed
- `dataforseo.py`: `_extract_serp` now passes through the `highlighted` field on every organic result (was being dropped). Required for Meta Entity Isolation.
- `research.py`: research output now surfaces `primary_intent`, `secondary_intent`, `meta_entities`, and `target_ngrams` at top level (not buried in `analysis`) for direct brief consumption.
- README.md "What It Actually Does" block expanded from 13 to 14 steps reflecting dual-intent mapping (step 5), n-gram seeding (step 8), and 301/410 governance (step 12).
- HARD RULES rewritten in SKILL.md: replaced the negative "never use codename X" rule with positive naming guidance ("framework is seo-agi / seobuild-onpage; no prior internal codenames in any output").

### Tests
- Added `tests/test_research_v171.py` with 13 new tests covering meta-entity extraction (highlighted field + inline-tag fallback + dedup), n-gram extraction (stopword filtering, top-N limiting, empty-input safety), tokenizer behavior, and secondary-intent funnel + override logic.

## [1.7.0] - 2026-04-30

### Added
- **Tributary Trust Protocol** (Section 11A): off-page architecture for AEO entity validation. Defines Tier 1 owned assets (Google Sites, Medium, Subreddits, Google Sheets, LinkedIn) as tributaries that feed entity signal to the money page. Includes companion-content rules, network topology, derivation matrix, and sequencing requirements.
- **Core Belief #7**: AEO Entity Validation via Owned Tier 1 Assets. Knowledge Graph inclusion and AI Overview impression share are now primary success signals, gated by off-page corroboration.
- **`scripts/tributary_gen.py`**: CLI tool that reads a money page, extracts its 500-token chunks + entities + `{{VERIFY}}` tags, and outputs derived companion briefs to `~/Documents/SEO-AGI/tributaries/<slug>/` with a manifest mapping each draft to its host platform.
- **Execution Protocol step 11**: tributary deployment is now mandatory for commercial-intent and local pages. All quality gates (Reddit Test, Information Gain, Prove-It, `{{VERIFY}}` resolution, Section 9 banned patterns, Entity Consensus) apply equally to off-page content -- thin tributaries net-harm the money page's entity signal.

### Changed
- CLAUDE.md directory structure now lists `scripts/tributary_gen.py`
- CLAUDE.md framework features updated with Tributary Trust capability

## [1.6.1] - 2026-04-28

### Fixed
- **Heading extraction returned empty for every competitor page.** DataForSEO's `on_page/content_parsing/live` endpoint returns headings inside `main_topic[]` and `secondary_topic[]` arrays (each with `h_title` and `level`), not as flat `h1`/`h2`/`h3` arrays. The old `_extract_headings` looked for keys that don't exist, so `Avg H2s: 0, Avg H3s: 0` for every research run regardless of competitor depth. Now correctly walks the topic tree.
- **Word count returned 0 for every competitor.** `plain_text_word_count` is not a field DataForSEO returns. Now computes from `page_as_markdown` (preferred) with a fallback walking `primary_content[].text`.
- **Title extraction returned empty.** `header.title` doesn't exist; replaced with markdown H1 detection plus a `main_topic[0].h_title` fallback.
- Added regression tests covering the real API response shape so this can't silently break again.

## [1.6.0] - 2026-04-15

### Added
- **Ideal Customer Persona (ICP)**: Page brief template now requires a defined ICP with demographics, psychographics, and specific pain points. Content maps to the actual reader, not a generic audience.
- **Deep Entity History & Identity Tags**: Founding dates, generational ownership, and identity attributes (women-owned, veteran-owned) are now explicit entity signals in Section 4 SEAT Signals.
- **The Self-Placement Rule**: Listicle guidance now explicitly allows ranking the client #1, provided the entry is objective with a specific use-case and honest tradeoffs.
- **Keyword Cannibalization Governance**: Section 9 "Never Do" list now prohibits creating pages that compete with existing URLs for the same intent. Sales-focused duplicates get tagged with `noindex` recommendation.

### Changed
- Quality checklist expanded from 38 to 41 items (ICP alignment, entity history, cannibalization)
- Minimum passing score raised to 33/41
- Both brief templates (Page Brief Template + Execution Protocol) updated with ICP field

## [1.3.0] - 2026-03-25

### Added
- **AI Summary Nugget**: Mandatory 200-character fact-dense block at top of every page, designed for LLM scrapers (Perplexity, Gemini, ChatGPT) to cite as a consensus source
- **Original Research Block**: Every page must include a data experiment or first-hand observation section to satisfy Google's Experience (E-E-A-T) signal
- **Map Traffic Shifting**: Local SEO instruction to link from high-traffic informational pages to map embeds, shifting user interaction signals toward local intent
- **Spam Resilience Logic**: Quality checklist now prioritizes technical relevance density over "human tone" -- factually perfect content is not downgraded for sounding clinical
- **Recursive Fact-Checking**: New execution step validates every claim against 2+ high-ranking sources for Entity Consensus before delivery

### Changed
- Quality checklist expanded from 24 to 28 items
- Minimum passing score raised to 22/28
- Execution protocol now has 11 steps (was 10)

## [1.2.0] - 2026-03-25

### Added
- Anti-spam ranking signals: single H1 rule, no EMQ in meta descriptions, no keyword-stuffed alt text, no duplicate content, internal linking requirements
- EMQ allowed in title and URL, banned in H2/H3/H4 subheadings
- Interactive elements section (cost calculators, widgets) to defend against AI Overview traffic loss
- Broken backlink monitoring guidance
- "Boat anchor" page culling (410 status for unindexable cruft)

### Changed
- Quality checklist expanded from 20 to 24 items (added H1, meta desc, heading, alt text checks)

## [1.1.0] - 2026-03-24

### Added
- Hard rule: framework is named seo-agi only; prior internal codenames must not appear in output
- Mandatory printed scorecard at end of every page output (no exceptions)
- FAQ/PAA section required (3+ questions, FAQPage schema)
- JSON-LD schema block required per page type
- Hub/spoke internal links required in every output
- RAG Targeting section (write for AI retrieval, not keyword volume)
- Topical Circle Audit (stay inside core service topic, noindex strays)
- Off-Page Sequencing (establish external brand footprint before on-page)
- Reddit Subdomain Indexing (subdomains over standard posts for AI retrieval)
- Ask Maps / Conversational GBP Optimization

### Changed
- Quality checklist expanded from base to 20 items
- Scorecard enforcement language strengthened ("INCOMPLETE without this table")

## [1.0.0] - 2026-03-23

### Added
- Initial release: GEO framework skill for Claude Code, OpenClaw, and Codex
- 500-token chunk architecture for Google AI retrieval
- SEAT signals (Semantic + E-E-A-T + Entity/Knowledge Graph)
- Google AI Search 7 ranking signals (Gecko, Jetstream, BM25, PCTR, Freshness, Boost/Bury)
- Reddit Test, Prove-It Details, Not For You, Information Gain quality gates
- Verification tagging system (VERIFY, RESEARCH NEEDED, SOURCE NEEDED)
- DataForSEO integration with graceful no-creds fallback
- MCP tool integration (Ahrefs, SEMRush)
- Google Search Console pull scripts
- Skill root discovery loop (works across Claude Code, OpenClaw, Codex, Gemini)
- Reference files: page templates, schema patterns, quality checklist
- Mock mode for testing without API keys
