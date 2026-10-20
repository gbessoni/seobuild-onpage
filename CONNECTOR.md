# SEOBuild Connector -- Build Specification

Status: **specification, not yet built.** This document describes the hosted
MCP connector that turns the open-source skill into a metered product.

The reference implementation studied for this spec is Lantern People
(`people.lantern.md`), whose public discovery endpoints were inspected directly
on 2026-10-16. Where this spec says "Lantern does X", that is an observation
from their live endpoints, not a guess.

---

## 1. Why a connector and not a skill

The open-source skill cannot be monetized, and that is a structural fact rather
than a pricing problem:

| Format | Can it hold a subscription? |
|---|---|
| Skill (git clone) | No. The customer has SKILL.md permanently and can pass it to anyone. |
| Plugin (`claude plugin install`) | No. Better install UX, identical files, identical copy problem. |
| **Hosted MCP connector** | **Yes.** Runs on our infrastructure. We issue tokens, meter calls, revoke access. |

A connector also removes the bring-your-own-key barrier. Today a buyer must
obtain DataForSEO credentials, a Massive token, and a Python environment before
anything runs. That is acceptable for a free tool and fatal above roughly
$100/month. The connector holds those keys server side and bundles the cost.

Both tiers run the same rules engine. This is one product with two delivery
paths, not two products.

---

## 2. The discovery flow

The entire "type a URL and it connects" experience is four endpoints on one
domain. A user says `seo.seobuild.md`, the agent does the rest.

```
agent POSTs /mcp
      │
      ▼
401 + WWW-Authenticate: Bearer resource_metadata="https://.../.well-known/oauth-protected-resource"
      │
      ▼
agent GETs /.well-known/oauth-protected-resource
      → learns the MCP endpoint and which server authorizes it
      │
      ▼
agent GETs /.well-known/oauth-authorization-server
      → learns authorize, token, and registration endpoints
      │
      ▼
agent POSTs /oauth/register     (Dynamic Client Registration)
      → self-registers, no pre-arranged credentials
      │
      ▼
OAuth authorization code + PKCE  (or device code for headless CLIs)
      │
      ▼
agent POSTs /mcp with Bearer token  →  connected
```

**Dynamic Client Registration is the critical piece.** Without a
`registration_endpoint`, every agent vendor would need credentials issued by
hand. With it, Grok, Claude Code, Codex, and anything else built on the MCP
spec self-register with no involvement from us. This single field is the
difference between "works everywhere" and "works for one client".

---

## 3. Required endpoints

### `GET /.well-known/oauth-protected-resource`

```json
{
  "resource": "https://seo.seobuild.md/mcp",
  "authorization_servers": ["https://seo.seobuild.md"],
  "scopes_supported": ["audit", "generate", "monitor"],
  "bearer_methods_supported": ["header"],
  "resource_name": "SEOBuild"
}
```

### `GET /.well-known/oauth-authorization-server`

```json
{
  "issuer": "https://seo.seobuild.md",
  "authorization_endpoint": "https://seo.seobuild.md/oauth/authorize",
  "token_endpoint": "https://seo.seobuild.md/oauth/token",
  "registration_endpoint": "https://seo.seobuild.md/oauth/register",
  "revocation_endpoint": "https://seo.seobuild.md/oauth/revoke",
  "device_authorization_endpoint": "https://seo.seobuild.md/oauth/device",
  "response_types_supported": ["code"],
  "grant_types_supported": [
    "authorization_code",
    "refresh_token",
    "urn:ietf:params:oauth:grant-type:device_code"
  ],
  "code_challenge_methods_supported": ["S256"],
  "token_endpoint_auth_methods_supported": ["none"],
  "scopes_supported": ["audit", "generate", "monitor"]
}
```

Notes on these choices, each mirroring Lantern:

- `token_endpoint_auth_methods_supported: ["none"]` plus PKCE S256 is the
  correct public-client configuration. Agents cannot hold a client secret.
- The **device code grant** is what lets a headless CLI authenticate. Without
  it, terminal-based agents cannot complete a browser redirect.
- `revocation_endpoint` is what makes cancellation actually cut off access.

### `POST /mcp`

Streamable HTTP MCP transport. Unauthenticated requests must return `401` with
the `WWW-Authenticate` header above. That header is the breadcrumb that starts
the entire discovery chain, so it is not optional.

### `GET /`

The marketing landing page. Same domain, so the URL a user types is also the
URL they can visit and read.

---

## 4. Tools exposed

Each tool maps to an existing capability in the skill. Scope gating is enforced
server side, never in the tool description.

| Tool | Scope | What it does |
|---|---|---|
| `audit_ai_visibility` | `audit` | Share-of-answer for a domain against named competitors. The lead magnet. |
| `research_keyword` | `audit` | SERP, PAA, related keywords, competitor content parsing, meta entities, n-grams. |
| `generate_page` | `generate` | Full page per SKILL.md rules, plus the 74-point scorecard. |
| `rewrite_page` | `generate` | Gap analysis against the current top 3, with 301/410 recommendations. |
| `find_ghost_paths` | `generate` | Impression-earning URLs that return 404. Requires the user's GSC connection. |
| `track_citations` | `monitor` | Weekly share-of-answer delta against named competitors. |
| `generate_tributaries` | `generate` | Tier 1/Tier 2 off-page companion briefs. |

The rules themselves stay in `SKILL.md`. The connector serves them; it does not
fork them. One source of truth.

---

## 5. Tiers

| | Free | Trial (3 days) | Paid |
|---|---|---|---|
| `audit_ai_visibility` | **Unlimited, forever** | Unlimited | Unlimited |
| `research_keyword` | 3 per day | Unlimited | Unlimited |
| `generate_page` | Not available | 3 total | Unlimited |
| `rewrite_page` | Not available | 1 total | Unlimited |
| `track_citations` | Not available | 3 days | Continuous |
| `generate_tributaries` | Not available | Not available | Unlimited |
| API keys required | None | None | None |

**The audit is never metered.** It is the lead magnet from the GTM plan: a
stranger types a domain, gets a number showing how invisible they are, and that
number is the entire sales conversation. Metering it would be optimizing the
wrong thing.

Generation is what is scarce, because generation is what costs money in
DataForSEO and Massive calls.

Monitoring is what is recurring, because "am I more or less cited than last
week" is a question that regenerates forever. Generation alone churns once the
customer has made their pages.

---

## 6. The connect message

When a client completes the handshake, return a capabilities brief. Most MCP
servers expose tools and stop, leaving the user with no idea what to say.
Lantern writes the user's first prompt for them, and that is the activation
moment.

```
You're connected to SEOBuild.

- Ask for a page in plain language: "write an SEO page for emergency plumber dallas"
- Audit any domain's AI visibility: "how visible is spothero.com in AI answers?"
- Rewrite an existing URL against the current top 3
- Pages are written to disk, never published without you

Your free trial
1. Unlimited AI-visibility audits, with named competitor share-of-answer
2. 3 full page generations, scored against the 74-point checklist
3. Live SERP, PAA, and competitor content parsing included, no API keys needed
4. Competitor citation tracking for 3 days
5. Entity-fact pairing, outbound citations, and schema markup on every page

Try it: "audit my AI visibility for airport parking jfk"
After your trial, choose a plan to keep generating.
```

Four things this does deliberately:

1. **Leads with what stays free.** The audit is unlimited forever, so it opens
   the list rather than hiding behind the metered items.
2. **Itemizes the trial.** "3 free pages" reads as nothing. The same offer in
   five numbered lines reads as substantial. Identical value, better framing.
3. **States the upgrade upfront.** No surprise wall on day four.
4. **Names the safety boundary.** "Pages are written to disk, never published
   without you" removes the fear that an agent will do something irreversible.

---

## 7. Metering

Count at the tool-call boundary, server side, before execution.

```
request → authenticate → resolve plan → check quota
    │
    ├── within quota  → execute, decrement, log
    └── over quota    → return an MCP error naming the limit and the upgrade URL
```

Over-quota responses must be actionable. `"Trial limit reached: 3 of 3 page
generations used. Continue at https://seobuild.md/pricing"` is a sales moment.
A bare `429` is a dead end.

Record per call: account, tool, scope, timestamp, upstream cost (DataForSEO and
Massive calls incurred). Upstream cost per generated page runs roughly
$0.01 to $0.02 today, so unit economics are comfortable at any realistic price,
but it needs to be measured rather than assumed.

---

## 8. Build notes

- **Transport:** Streamable HTTP, not SSE. SSE is deprecated in the current MCP
  spec.
- **Hosting:** Lantern runs on Railway. Any platform with a stable hostname and
  TLS works. The hostname matters more than the platform, because the hostname
  is the install command.
- **Domain:** pick something short and typeable. The domain *is* the product's
  install UX. `seo.seobuild.md` is in the same shape as `people.lantern.md`.
- **Sign-in:** Google OAuth only at first. Every additional field costs
  conversion, and Lantern's entire onboarding was one Google sign-in.
- **Do not fork SKILL.md.** The connector reads the same rules file this repo
  publishes. If the rules diverge, the free tier stops being a faithful preview
  of the paid one.

### Effort, honestly

This is not a weekend. OAuth 2.1 with dynamic client registration, PKCE, the
device flow, token lifecycle, revocation, and usage metering is a few weeks of
work even on top of a framework that handles part of it. The install experience
is trivial for the user precisely because the server absorbs that complexity.

---

## 9. Sequence

1. Register the domain and stand up a landing page at `/`.
2. Implement the two discovery endpoints plus the `401` breadcrumb on `/mcp`.
   Verify with `curl` that a client can walk the chain unauthenticated.
3. Implement OAuth: registration, authorize, token, revoke, device.
4. Expose `audit_ai_visibility` only, free and unmetered. Ship it.
5. Add metering, then `research_keyword` and `generate_page` behind the trial.
6. Add `track_citations`. This is the one that makes revenue recur.
7. Add billing and the upgrade path.

Step 4 is the real milestone. A connector that does nothing but hand strangers
their AI-visibility number, for free, is already the top of the funnel the GTM
plan depends on. Everything after that is monetization on an audience that
already showed up.
