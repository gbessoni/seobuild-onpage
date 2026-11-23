# SEOBuild On-Page

An open-source skill for Claude Code, Codex, and Grok Bot. It pulls current search results for a keyword, finds gaps in the pages that already rank, and writes or rewrites a page draft against a fixed quality checklist.

The skill is free. You can bring your own DataForSEO key, or skip keys and let the skill fall back to web search. Updates install with one command:

```bash
claude plugin marketplace add gbessoni/seobuild-onpage && claude plugin install seobuild-onpage@seobuild
```

Not on Claude Code? See [Install + Setup](#install--setup) for Codex, OpenClaw, and a manual clone.

There is also a hosted connector for teams that want the same research without managing keys. The free AI-visibility audit is on the site.

- Site and free audit: https://seobuild-audit.onrender.com
- Hosted MCP endpoint: https://seobuild-audit.onrender.com/mcp
- Open-source repo: https://github.com/gbessoni/seobuild-onpage

A 7-day hosted trial and a $500/month plan are coming soon, until Stripe checkout is connected. Until then, the live paths are the free audit and the open-source install.

Current version is v2.6.0. The skill now requires every H2 on a local service page to stay inside a primary category, service, and city; local FAQs to cover DIY vs professional, pricing and timelines, and guarantees and credentials; and license or insurance facts to appear as crawlable text. The quality checklist is 74 points, and a draft is flagged if it scores below 63/74. A printed scorecard is part of every output.

## What It Actually Does

```
You: /seoagi "best project management tools 2026"

SEO-AGI:
  1.  Pulls SERP top 10 via DataForSEO
  2.  Parses competitor content (word count, headings, topics covered)
  3.  Extracts People Also Ask questions
  4.  Pulls related keywords with search volumes
  5.  Maps Primary intent (top of page) and Secondary intent (action funnel
      below the fold) per the Orcas 1 dual-intent model
  6.  Generates a data-driven content brief
  7.  Writes the complete page (Markdown + YAML frontmatter)
  8.  Extracts top bigrams/trigrams from top 3 competitors and seeds 2+ of
      them into the 200-char AI Summary Nugget for LLM-retrieval alignment
  9.  Adds FAQ section from real PAA data
  10. Generates JSON-LD schema markup + inline RDFa entities
  11. Validates every claim against 2+ sources (Entity Consensus)
  12. For rewrites: evaluates each legacy URL and recommends 301 (when topic
      survives and equity should consolidate) or 410 (when the URL is thin,
      cannibalizing, or out-of-circle and should be pruned)
  13. Validates against 74-point quality checklist
  14. Prints scorecard so you see exactly what passed
```

For rewrites, point it at any URL. It compares your page against the current top 3 ranking competitors, identifies exactly what you're missing, and rewrites with a change summary explaining every edit.

---

## The SEO Knowledge Inside

This isn't a wrapper around "write me an SEO article." The skill encodes strategies from the best in the game:

**Traditional SEO**
- Intent-first content architecture (match what searchers actually want, not what you think the keyword means)
- Competitive word count targeting (page length based on what's ranking, not arbitrary "write 2000 words")
- Heading hierarchy derived from SERP analysis (not templates, not guesswork)
- People Also Ask coverage as FAQ sections (answer the questions Google already knows people are asking)
- Schema markup patterns by page type (FAQPage, LocalBusiness, HowTo, Product, BreadcrumbList)
- Internal linking suggestions based on actual site data from GSC

**GEO / LLM SEO (Generative Engine Optimization)**
- 200-char AI Summary Nugget at top of every page, designed for Perplexity/Gemini/ChatGPT to cite as a consensus source
- 500-token chunk architecture matching Google AI's retrieval window
- Content structured for AI citation (Perplexity, ChatGPT, Google AI Overviews)
- Entity-rich writing that LLMs can extract and reference
- Depth-over-length philosophy (comprehensive coverage that becomes the authoritative source)
- FAQ patterns that match how AI systems parse and surface answers
- Data-backed claims that AI systems prefer to cite over vague assertions
- RAG targeting: zero-volume long-tail queries that "train" AI to cite your domain
- Off-page sequencing: establish third-party brand footprint before on-page SEO
- Reddit subdomain indexing: seed entity consensus across indexed Reddit layers
- Topical circle enforcement: stay inside your core service topic to avoid diluting AI authority signals
- Recursive fact-checking: every claim validated against 2+ high-ranking sources for Entity Consensus
- Spam resilience: technical relevance density prioritized over "human tone" in quality scoring

**Structural & DOM Signals**
- Semantic HTML containers: `<article>`, `<section>`, `<aside>`, `<main>` in generated HTML for Main Content zone identification
- Proof-term proximity: supporting evidence must live in the same 500-token chunk as its H2 (BERT evaluates within passage window, not page-wide)
- Query Fan-Out facet coverage: each chunk answers a distinct AI sub-query for multiplicative retrieval
- Forensic EMQ check: conditionally require exact-match keyword in H1 based on competitor optimization ratio
- QDD vulnerability detection: UGC in top 10 = HIGH_CONFIDENCE_TAKEOVER opportunity flag
- Site-level entity dominance: niche site architecture beats generalist single-page competitors

**Local / GBP Optimization**
- Ask Maps & conversational GBP optimization (structured data that answers "who has X available?")
- Holiday/exception hours, discrete service items, pre-populated Q&A
- GBP fields treated as AEO markup, not optional admin work
- Map traffic shifting: internal links from high-traffic informational pages to map embeds to boost local engagement signals

**Content Quality Signals (2026 protocols)**
- Mandatory Original Research / Data Experiment block in every page (Google's top E-E-A-T signal: Experience)
- Verification tagging system: every claim tagged with `{{VERIFY}}`, `{{RESEARCH NEEDED}}`, or `{{SOURCE NEEDED}}`
- "Not For You" block: honest section telling readers when this option is a bad fit (trust signal competitors skip)
- Information Gain Test: every page must contain content not found in the top 10 Google results

**The 74-point quality checklist every page runs through (selected highlights):**
- Information gain over top 10 Google results? Check.
- Reddit Test: would a practitioner upvote this? Check.
- Core answer in first 150 words? Check.
- Fast-scan summary within first 200 words? Check.
- 2+ hard operational Prove-It facts? Check.
- Real HTML tables (not bullet lists)? Check.
- Every section doing a unique job (no repetition)? Check.
- All specific numbers tagged with `{{VERIFY}}`? Check.
- All citations specific and traceable? Check.
- "Not For You" block present? Check.
- 500-token chunk architecture? Check.
- No banned phrases or patterns? Check.
- Word count within competitive range? Check.
- JSON-LD schema block matching page type? Check.
- FAQ section with 3+ PAA questions? Check.
- Hub/spoke internal links? Check.
- Title tag <60 chars with target keyword? Check.
- Meta description <155 chars with value prop? Check.
- Content inside site's core topical circle? Check.
- `reddit_test` and `information_gain` in frontmatter? Check.
- Single H1 tag only? Check.
- No exact-match keyword in meta description? Check.
- No keyword stuffing in H2/H3/H4 tags? Check.
- Image alt text descriptive, not keyword-stuffed? Check.
- AI Summary Nugget (200-char) at top of page? Check.
- Original Research / Data Experiment block present? Check.
- Map-to-informational internal link (local pages)? Check.
- Every claim validated against 2+ sources? Check.

- QDD check run -- UGC in top 10 flagged or cleared? Check.
- Site vs. Page audit -- competitor type identified? Check.
- Forensic EMQ ratio checked -- applied correctly? Check.
- Each 500-token chunk targets a distinct QFO facet? Check.
- ICP defined in brief and content tailored to their pain points? Check.
- Deep entity history / identity tags included where applicable? Check.
- No keyword cannibalization with existing site URLs? Check.
- Meta Entity Isolation -- entities pulled from competitor SERP snippets, not body? Check.
- N-Gram AI Alignment -- 2+ bigrams/trigrams in AI Summary Nugget? Check.
- Dual-Intent -- Primary intent in first 500 tokens + Secondary action funnel? Check.
- Status Code Governance -- explicit 301 or 410 for every legacy URL? Check.
- Trust Pilot entity profiling with exact service target bigrams? Check.
- Off-page assets mapped with cross-cutting Organization/Person schema to GBP? Check.
- Critical data points visible in raw HTML DOM (not buried solely in JSON-LD)? Check.
- Decision Fit -- heading structure maps to buyer stage (Research/Compare/Buy), not copied competitor H2s? Check.
- Brand Identity -- client differentiators woven verbatim into chunks + AI Summary Nugget? Check.
- Topical Silo -- `Recommended Spoke Pages` section appended from `missing_spokes`? Check.
- Anti-Paragraph Snippet -- primary H2 answers in block containers, not bare `<p>`? Check.
- DOM Flattening -- layout flat (max ~3 nesting levels), no wrapper-node bloat? Check.
- Goldilocks Entity Synergy -- subheadings repeat core entity pairings, not generic text? Check.
- Two-Gate Extraction -- satisfies Gate 1 retrieval AND Gate 2 citation extraction? Check.
- Anti-NLP Stuffing -- body free of force-repeated NLP-tool entity lists (de-indexation risk)? Check.
- Local Isolation -- local page targets one service+place, no multi-service stacking? Check.
- GBP Inner-Link Directive -- local page tells user to point GBP at this URL, not homepage? Check.
- Outbound Citations -- 5+ descriptive links to external authoritative sources? Check.
- Strict Phrase Placement -- exact match in Title and H1 only, never H2/H3/H4? Check.
- Entity-Fact Pairing -- entities bound to hard verifiable facts, not just named? Check.
- Intent Divergence -- CTAs stripped if informational, awards featured if local? Check.
- Anti-Boilerplate -- internal links contextual, no repeated site-wide blocks? Check.
- Off-Page Embed -- Tier 1 draft carries a Maps embed where the platform allows? Check.
- Unlinked Citation -- plain-text brand and URL mentions alongside the link? Check.
- SSR/SSG -- internal links present in the raw HTML DOM, not JS-injected? Check.
- Named Source Attribution -- every major claim names its source in visible copy? Check.
- No fabricated testing claims ("We tested 12 of these")? Check.
- Not a skyscraper -- word count from competitive median, not out-lengthing? Check.
- Quantifiable differentiators on local pages (hard numbers, not adjectives)? Check.
- Semantic variance -- every H2 defensible against the Primary GBP Category + service + city? Check.
- Spider Cluster FAQ -- DIY vs Pro, pricing and timelines, guarantees and credentials? Check.
- Credentials -- license numbers and insurance status as crawlable text? Check.
- Tributary drafts generated in the same pass for local pages? Check.

Pages scoring below 63/74 get flagged with specific items to fix. The scorecard is printed at the end of every output so you see exactly what passed.

---

## Data Integrations (BYOK)

Bring your own API keys. Use one, use all. The skill adapts:

| Integration | What It Provides | Required? |
|---|---|---|
| **DataForSEO** | Live SERP results, keyword volumes, People Also Ask, competitor content parsing | Yes (core) |
| **Google Search Console** | Your actual query data, CTR, positions, cannibalization detection | Optional |
| **Ahrefs** (via MCP) | Backlink profiles, domain authority, referring domains | Optional |
| **SEMRush** (via MCP) | Traffic estimates, keyword gaps, competitive positioning | Optional |

No keys at all? The skill falls back to web search. You lose precision but the workflow still runs.

---

## Install + Setup

### Step 1: Install the skill

**Claude Code (recommended -- installs as a plugin, updates with one command):**
```bash
claude plugin marketplace add gbessoni/seobuild-onpage
```
```bash
claude plugin install seobuild-onpage@seobuild
```

Update later with `claude plugin update seobuild-onpage`. Restart required to apply.

**Claude Code (manual clone, if you prefer to edit the files directly):**
```bash
git clone https://github.com/gbessoni/seobuild-onpage.git ~/.claude/skills/seobuild-onpage
```

**Codex:**
```bash
git clone https://github.com/gbessoni/seobuild-onpage.git ~/.codex/skills/seobuild-onpage
```

**OpenClaw:**
```bash
git clone https://github.com/gbessoni/seobuild-onpage.git ~/.agents/skills/seobuild-onpage
```

**Any other agent:** clone the repo anywhere and point your agent at `SKILL.md`. The skill locates its own scripts at runtime, so the directory name does not need to match.

After installing, **restart your agent**. Skills load at session start, so a running session will not see a newly installed one.

### Updating a cloned install

```bash
cd ~/.claude/skills/seobuild-onpage && git pull
```

If you have local edits (a modified `.env.example`, for example), stash first so the pull does not abort:

```bash
cd ~/.claude/skills/seobuild-onpage && git stash && git pull && git stash pop
```

> Already installed and seeing "destination path already exists"? You cloned it before. Use the update commands above, not the install ones.

### Step 2: Install Python dependency

```bash
pip install requests
```

### Step 3: Configure API keys (optional but recommended)

```bash
mkdir -p ~/.config/seo-agi
cp ~/.claude/skills/seobuild-onpage/.env.example ~/.config/seo-agi/.env
```

Then edit `~/.config/seo-agi/.env` with your keys:

```env
# DataForSEO -- sign up at https://dataforseo.com (~$0.002/query)
DATAFORSEO_LOGIN=your_email@example.com
DATAFORSEO_PASSWORD=your_password

# Google Search Console (optional)
GSC_SERVICE_ACCOUNT_PATH=/path/to/service-account.json
```

**No API keys?** The skill still works. It falls back to Ahrefs/SEMRush MCP tools (if connected) or web search. You lose SERP content parsing but the framework still writes quality pages.

### Step 4: Verify it works

```bash
# Test the research pipeline (uses mock data, no API keys needed)
python3 ~/.claude/skills/seobuild-onpage/scripts/research.py "best project management tools 2026" --mock --output=compact
```

You should see SERP results, PAA questions, related keywords, and heading structure data. If you see that, you're good.

### Step 5: Use it

Open Claude Code (or OpenClaw, or Codex) and type:

```
Write an SEO page for "best project management tools 2026"
```

The skill auto-triggers on SEO content requests. It will:
1. Run the research script to pull competitive data
2. Show you a content brief and confirm before writing
3. Write the full page following the SEO-AGI framework
4. Validate against the quality checklist
5. Save to `~/Documents/SEO-AGI/pages/`

---

## Verify Your Setup (Troubleshooting)

**Check if the skill is installed:**
```bash
ls ~/.claude/skills/seobuild-onpage/SKILL.md && echo "Installed" || echo "Not found"
```

**Check if API keys are configured:**
```bash
cat ~/.config/seo-agi/.env 2>/dev/null || echo "No .env file -- skill will use fallback mode"
```

**Test with live DataForSEO (if you have keys):**
```bash
python3 ~/.claude/skills/seobuild-onpage/scripts/research.py "best crm software" --output=compact
```

**Run unit tests:**
```bash
cd ~/.claude/skills/seobuild-onpage
python3 tests/test_env.py && python3 tests/test_serp_analyze.py && python3 tests/test_dataforseo.py
```

---

## Use Cases

**New page for a target keyword**: Research the current top results, then generate a draft with `/seoagi`. Review the scorecard and the `{{VERIFY}}` tags before you publish.

**Location page generation**: `/seoagi "plumber in [city]"` x 50 cities. Each page gets city-specific research, local PAA questions, LocalBusiness schema. Not cookie-cutter templates.

**Content refresh**: Point it at your underperforming URLs. It pulls your actual GSC data, compares against current top 3, and tells you exactly what to add, expand, or restructure. Then does it.

**Competitive intelligence**: `/seoagi research "competitor keyword"` gives you the full landscape without writing anything. Word count ranges, heading structures, topic gaps, related keywords with volumes.

**Brief handoff**: `/seoagi brief "keyword"` generates a structured content brief you can hand to a human writer. Research-backed, not vibes-based.

---

## How the hosted connector fits

The open-source skill is the rules and the local workflow. The hosted MCP connector at `/mcp` runs the live keyword and AI-visibility research so a team does not have to store DataForSEO keys on every machine.

Typical path:

1. Run a free AI-visibility audit on the site (no card).
2. Connect the hosted connector in Claude Code, Codex, or Grok Bot.
3. Use it to research a keyword, draft or rewrite a page, and read the scorecard.
4. A 7-day trial of the hosted connector, then a $500/month plan, are coming soon, until Stripe checkout is connected.

On the hosted connector, Search Console connection is coming soon.

---

## Testing

See "Verify Your Setup" above for full test commands. Quick version:

```bash
cd ~/.claude/skills/seobuild-onpage

# Unit tests (no API keys needed)
python3 tests/test_env.py && python3 tests/test_serp_analyze.py && python3 tests/test_dataforseo.py

# Mock mode (full pipeline with fixture data)
python3 scripts/research.py "best project management tools 2026" --mock --output=compact

# No-creds mode (returns skeleton for agent to fill via MCP/WebSearch)
python3 scripts/research.py "test keyword" --output=compact
```

---

## Contributing

Open source, MIT license. PRs welcome.

The skill is modular. Want to add a new page template? Edit `references/page-templates.md`. New schema pattern? `references/schema-patterns.md`. Better quality checks? `references/quality-checklist.md`. New data source? Add a client in `scripts/lib/` and wire it into `research.py`.

---

## Credits

Built by [Greg Bessoni](https://github.com/gbessoni) ([@gregbessoni](https://x.com/gregbessoni)).

## License

MIT. See [LICENSE](LICENSE).
