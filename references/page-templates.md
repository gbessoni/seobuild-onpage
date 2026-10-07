# Page Templates Reference

Each page type has a specific structure that performs well in search.
The skill auto-detects page type from the keyword intent, but users can override.

## Service Page

**Triggers:** "[service] in [location]", "[service] company", "[service] near me"

**Structure:**
```
H1: [Service] in [Location] - [Value Prop]
  H2: What Is [Service] / How [Service] Works
  H2: [Service] Options / Types of [Service]
    H3: [Option 1]
    H3: [Option 2]
    H3: [Option 3]
  H2: Pricing / What Does [Service] Cost
  H2: How to Choose [a/the right] [Service Provider]
  H2: Why [Company/Location] for [Service]
  H2: Frequently Asked Questions
    H3: [PAA Question 1]
    H3: [PAA Question 2]
    H3: [PAA Question 3]
```

**Schema:** LocalBusiness + FAQPage
**Word count target:** 1500-2500
**Must include:** Pricing (even ranges), specific location references, social proof

## Comparison Page

**Triggers:** "[X] vs [Y]", "best [category]", "[product] alternatives", "top [N] [category]"

**Structure:**
```
H1: [X] vs [Y]: [Differentiating Angle] ([Year])
  H2: Quick Comparison / TL;DR
    [Comparison table]
  H2: What Is [X]
    H3: Key Features
    H3: Pricing
    H3: Best For
  H2: What Is [Y]
    H3: Key Features
    H3: Pricing
    H3: Best For
  H2: [X] vs [Y]: [Criteria 1]
  H2: [X] vs [Y]: [Criteria 2]
  H2: [X] vs [Y]: [Criteria 3]
  H2: Which Should You Choose?
  H2: FAQ
```

**Schema:** FAQPage (+ Product if applicable)
**Word count target:** 2000-3500
**Must include:** Comparison table near top, specific criteria-based sections, clear recommendation

## How-To / Guide

**Triggers:** "how to [action]", "[topic] guide", "[topic] tutorial"

**Structure:**
```
H1: How to [Action]: [Qualifier] Guide ([Year])
  H2: What You'll Need / Prerequisites
  H2: Step 1: [Action]
    H3: [Sub-step if complex]
  H2: Step 2: [Action]
  H2: Step 3: [Action]
  H2: [N] more steps...
  H2: Common Mistakes / Troubleshooting
  H2: Tips from [Experts/Experience]
  H2: FAQ
```

**Schema:** HowTo + FAQPage
**Word count target:** 1500-3000
**Must include:** Numbered steps, specific examples, troubleshooting section

## Location Page

**Triggers:** "[service] [city]", "[business type] [neighborhood]", "[thing to do] in [location]"

**Structure:**
```
H1: [Service/Topic] in [City, State] - [Value Prop]
  H2: [Service] Options in [City]
    H3: [Option/Area 1]
    H3: [Option/Area 2]
  H2: [City]-Specific Information
    [Local details: regulations, seasonality, landmarks, neighborhoods]
  H2: Pricing in [City]
  H2: How to [Get Started/Book/Find] [Service] in [City]
  H2: Tips for [Service] in [City]
  H2: Nearby Alternatives
    [Adjacent cities/neighborhoods]
  H2: FAQ
```

**Schema:** LocalBusiness + FAQPage + BreadcrumbList
**Word count target:** 1200-2000
**Must include:** Specific local details (not generic), nearby alternatives for internal linking, local pricing

## Product / Feature Page

**Triggers:** "[product] features", "[product] review", "[product] pricing"

**Structure:**
```
H1: [Product Name]: [Key Benefit] ([Year])
  H2: What Is [Product]
  H2: Key Features
    H3: [Feature 1] - [Benefit]
    H3: [Feature 2] - [Benefit]
    H3: [Feature 3] - [Benefit]
  H2: Pricing
    [Plans table or breakdown]
  H2: Pros and Cons
  H2: Who Is [Product] Best For
  H2: [Product] vs Alternatives
  H2: How to Get Started
  H2: FAQ
```

**Schema:** Product + FAQPage + Review (if review angle)
**Word count target:** 1500-2500
**Must include:** Pricing specifics, honest pros/cons, clear "best for" segment

## General Quality Rules (All Templates)

1. Every H2 section should have at least 150 words of substantive content
2. FAQ sections use the exact PAA questions (or close variants) as H3s
3. Include at least one data point, stat, or specific example per major section
4. Internal links should go in contextually relevant spots, not dumped at the bottom
5. Schema markup matches the page type (see schema-patterns.md)
6. Year in title only if the content is genuinely time-sensitive
7. No filler paragraphs. If a section doesn't add value, cut it.

---

## Universal Block Requirements (all templates, current as of v2.5.0)

These apply on top of the per-type skeletons above. Where this section and an
older rule above disagree, this section wins.

### Required blocks, in order

1. **AI Summary Nugget** -- 200 characters maximum, first element after
   frontmatter, above the H1. Pure facts: primary entity, key number, core
   distinction. No marketing language. This is the passage answer engines lift
   as a consensus snippet.
2. **Opening answer block** -- 100 to 150 words, third-person and objective.
   Answers the query directly, no preamble or definitional throat-clearing.
3. **Fast-scan summary** -- within the first 200 words. Bullets with concrete
   facts, a key-takeaways box, or a comparison table.
4. **Main body** -- 500-token chunks (see below).
5. **Comparison table** -- real `<table>`, columns that do work: Best For,
   Main Tradeoff, Why It Matters, Typical Cost.
6. **Prove-It section** -- two or more hard operational facts with traceable
   citations.
7. **Original Research / Data Experiment block** -- a specific test, analysis,
   or first-hand observation. Pages without one cap out on the scorecard.
8. **Not For You block** -- honest scenarios where this is the wrong choice.
   At least one line a competitor would never publish.
9. **FAQ** -- three or more real PAA questions, wrapped in FAQPage schema.
10. **Recommended Spoke Pages** -- built from `research.missing_spokes`,
    derived per page. Never the same list across pages.

### 500-token chunk architecture

Each chunk is roughly 375 words and must stand alone as the answer to one
specific sub-query (one QFO facet per chunk, never two). Within every chunk:

- **Question-based H2** using entity names, never the exact-match keyword.
- **Snippet answer** in the first 2-3 sentences, wrapped in a block-level
  structural container, not a bare `<p>`.
- **Entity-fact pairing** -- every entity bound to a hard fact in that same
  chunk: time, place, cost, capacity, frequency, distance, or date.
- **Named source attribution** -- major claims name their source in the visible
  copy, then link to it.
- **Proof-term proximity** -- supporting evidence lives in the same chunk as the
  heading it supports.
- Never split a table across a chunk boundary. Never stack two H2s without
  250+ words between them.

### Informational vs Local template separation

The same page skeleton diverges by intent. Applying the wrong column demotes
the page.

| | Informational / global | Local service (Ask Maps) |
|---|---|---|
| Sales CTAs | Strip | Keep, maximum two |
| "Free estimate" offers | Strip | Permitted |
| Awards, badges, certifications | Strip from text layer, SVG only | Feature prominently |
| Quantifiable differentiators | Omit | Required, two or more, hard numbers |
| Outbound citations | 5+ required | 5+ required |
| Service scope | Single topic cluster | Exactly one service, one location |
| GBP directive | Not applicable | Required at top of brief |

Determine intent from `research.primary_intent` before choosing a column.

### Hard limits

- Exact-match keyword appears in the Title and H1 only. Never in H2/H3/H4,
  meta description, or alt text.
- Five or more descriptive outbound links to external authoritative sources.
- Maximum DOM nesting depth of roughly three levels in the content region.
- Server-rendered or static output. Internal links must exist in the raw HTML.
- No fabricated testing claims ("We tested 12 of these") unless the testing
  happened and the methodology is documented.
- No skyscraper pages. Word count comes from the competitive median.
- Internal links are contextual per chunk, never a repeated sitewide block.
