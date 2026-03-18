# SEO-AGI

### One command. Competitive data in. Ranking pages out.

Most SEO tools tell you what's wrong with your site. This one writes the pages.

`/seoagi "airport parking JFK"` pulls the current SERP, analyzes what's ranking, finds the gaps in their content, and writes you a complete page -- with the heading structure, depth, FAQ section, and schema markup that actually competes. Not thin content. Not keyword-stuffed filler. Pages backed by live data from the tools the pros use.

**I built this because I got tired of the gap between "SEO audit" and "published page."** I've been doing SEO for 20+ years in ground transportation (1M+ bookings, 2M+ rides across my companies). The workflow was always the same: pull SERP data, analyze competitors, find gaps, write brief, write page, add schema, publish. Over and over. So I turned that entire workflow into a single skill that any AI agent can execute.

The result? I used this to research a competitor's best-performing pages, built equivalent content with `/seoagi`, bought the exact-match domains, and every single page is ranking on page 1. That's not theory. That's the workflow.

---

## What It Actually Does

```
You: /seoagi "best project management tools 2026"

SEO-AGI:
  1. Pulls SERP top 10 via DataForSEO
  2. Parses competitor content (word count, headings, topics covered)
  3. Extracts People Also Ask questions
  4. Pulls related keywords with search volumes
  5. Detects search intent (informational vs commercial vs transactional)
  6. Generates a data-driven content brief
  7. Writes the complete page (Markdown + YAML frontmatter)
  8. Adds FAQ section from real PAA data
  9. Generates JSON-LD schema markup
  10. Validates against a quality checklist
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
- Content structured for AI citation (Perplexity, ChatGPT, Google AI Overviews)
- Entity-rich writing that LLMs can extract and reference
- Depth-over-length philosophy (comprehensive coverage that becomes the authoritative source)
- FAQ patterns that match how AI systems parse and surface answers
- Data-backed claims that AI systems prefer to cite over vague assertions

**The quality checklist every page runs through:**
- Title tag <60 chars with target keyword? Check.
- Meta description <155 chars with CTA? Check.
- Single H1 mirroring the title? Check.
- Logical H2 > H3 hierarchy? Check.
- At least 3 PAA questions answered? Check.
- Specific data/statistics (not vague claims)? Check.
- JSON-LD schema appropriate to page type? Check.
- Word count within competitive range? Check.
- No keyword stuffing? Check.

Pages scoring below 80% get flagged with specific items to fix. Below 60% = rewrite.

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

## Install

### Claude Code

```bash
claude install-skill gbessoni/seo-agi
```

### OpenClaw

Add to your `.claude/settings.json`:

```json
{
  "skills": ["gbessoni/seo-agi"]
}
```

Or clone directly:

```bash
git clone https://github.com/gbessoni/seo-agi.git ~/.claude/skills/seo-agi
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/gbessoni/seo-agi.git
cd seo-agi

# 2. Configure
mkdir -p ~/.config/seo-agi
cp .env.example ~/.config/seo-agi/.env
# Edit with your API keys

# 3. Use with Claude Code
# Just say: "write an SEO page for [keyword]"
```

**Minimum keys needed:** DataForSEO (~$0.002/query). Everything else is optional but makes it stronger.

---

## Use Cases

**Exact-match domain play**: Research competitor's top pages with OpenClaw, generate equivalent content with `/seoagi`, buy the domains, publish. Page 1.

**Location page generation**: `/seoagi "plumber in [city]"` x 50 cities. Each page gets city-specific research, local PAA questions, LocalBusiness schema. Not cookie-cutter templates.

**Content refresh**: Point it at your underperforming URLs. It pulls your actual GSC data, compares against current top 3, and tells you exactly what to add, expand, or restructure. Then does it.

**Competitive intelligence**: `/seoagi research "competitor keyword"` gives you the full landscape without writing anything. Word count ranges, heading structures, topic gaps, related keywords with volumes.

**Brief handoff**: `/seoagi brief "keyword"` generates a structured content brief you can hand to a human writer. Research-backed, not vibes-based.

---

## The Workflow That Got Me Here

I've been running this workflow manually for 20 years across ParkingAccess.com (1M+ bookings) and Shuttlefare.com (2M+ rides). The pattern never changed:

1. Find what's ranking
2. Figure out what they cover that you don't
3. Write something deeper
4. Add the technical SEO (schema, meta, structure)
5. Publish and move on

seo-agi is that pattern, automated. The 20 years of pattern recognition compressed into a SKILL.md file, backed by live data APIs, running inside a super agent that can decompose and parallelize the work.

It's not AI replacing SEO expertise. It's SEO expertise finally having the right delivery mechanism.

---

## Testing

```bash
# Unit tests (no API keys needed)
python3 tests/test_env.py
python3 tests/test_serp_analyze.py
python3 tests/test_dataforseo.py

# Mock mode (uses fixture data, runs full pipeline)
python3 scripts/research.py "airport parking JFK" --mock --output=compact
```

---

## Contributing

Open source, MIT license. PRs welcome.

The skill is modular. Want to add a new page template? Edit `references/page-templates.md`. New schema pattern? `references/schema-patterns.md`. Better quality checks? `references/quality-checklist.md`. New data source? Add a client in `scripts/lib/` and wire it into `research.py`.

---

## Credits

Built by [Greg Bessoni](https://github.com/gbessoni) ([@gregbessoni](https://x.com/gregbessoni)).

## License

MIT
