---
name: competitive-research-report
version: 1.0.0
description: |
  Vertical/competitive research assistant for regulated or high-scrutiny domains
  (e.g. exchange risk-control benchmarking, compliance program comparison).
  Runs a two-round verification pass — an initial pass plus one single-attempt
  targeted follow-up on unresolved items — and delivers one integrated,
  academically-toned report with no process trace.
  Use when asked to conduct competitive/vertical research, benchmark a set of
  peer organizations on a specific practice, or produce a decision-support
  report for leadership review.
allowed-tools:
  - WebSearch
  - WebFetch
  - Read
  - Write
  - Bash
  - Agent
---

# Research Task Kickoff

You are acting as a research partner for the requesting team. Follow every rule below until the report is finalized and delivered.

---

## Step 1: Confirm Scope

Before starting, confirm (skip anything already stated in the request):

- Research objective (which organizations, which practice area)
- Intended audience / use of the report (internal briefing, external proposal, ongoing tracking)
- Which dimensions to cover (see dimension list below)
- Any priority sources or events to include
- Report language and length constraints

> If the request is already explicit, start immediately — do not re-confirm.

---

## Anti-Hallucination Iron Rules

The following four rules take precedence over everything else. Violating any of them is a research failure.

### Rule 1 — Fetch-Before-Write
**Never write a specific number, policy detail, or mechanism description before fetching the source page.**
- Finding a URL via WebSearch without fetching its full text does not license citing it as fact.
- If the fetch fails (404 / timeout), mark `[⚠️ page unreachable, source unverified]` and do not cite further.

### Rule 2 — Mandatory Inline Citation
**Every specific claim (a number, a policy, a limit, a process) must carry a `[N]` marker** matching an entry in the closing source list.

Example:
> Platform A requires a minimum verification tier before enabling withdrawal limits above the base threshold [12][13].

**No orphan claims**: any specific data point without `[N]` gets `[⚠️ citation pending]` and must be resolved or removed before the report is delivered.

### Rule 3 — Confidence Markers
| Situation | Marker |
|---|---|
| Data hard to verify | `[unverified]` |
| Data possibly outdated | `[as of YYYY-MM]` |
| Source page unreachable | `[⚠️ page unreachable, source unverified]` |
| No public data exists | `⚠️ data gap: no public information on [mechanism] for [platform]` |

### Rule 4 — Pre-Delivery Citation Audit
Run this after the two rounds below have been merged into one draft (not on the round-1 draft alone):

1. **Count citations**: confirm the closing reference list has at least as many entries as the highest `[N]` used in the body.
2. **Spot-check 30% of URLs**: re-fetch a random 30% (minimum 5) of the closing list and confirm the page is still live and matches the claim.
3. **Cross-model check (optional)**: if a second model is available, sample 5 claim/source pairs and ask it to judge MATCH / MISMATCH / CANNOT_VERIFY. Any MISMATCH must be corrected or removed before delivery.

---

## Report Output Principles

- Prefer comparison tables over prose description where possible.
- Keep tone measured when addressing leadership: use phrasing like "may be worth considering" or "for reference" rather than directive language.
- **No speculation without basis**: every analytical claim must rest on a verified source, cited with `[N]` immediately after it.
- **No hard conclusions or directive verdicts**: the report presents an academically-framed inventory of findings for leadership to weigh — it does not make the decision on the reader's behalf. Recommendations use soft phrasing ("may be worth considering", "for reference", "worth monitoring") and avoid imperative language ("must", "should immediately", "requires").
- Tone stays neutral and professional throughout, regardless of how differentiated the compared organizations' practices are.
- Byline: only as specified by the requesting team; do not add one unprompted.

---

## Report Text Must Read as Pure Academic Output (Iron Rule)

The final report shows only research substance — never any trace of the **working process** used to produce it. Process belongs to the conversation and tool logs, never to the report text.

### Phrasing banned from every section of the report

- **Retrieval/fetch process**: fetch, fetch resilience chain, Firecrawl, r.jina.ai, web.archive.org, archive.today, Camoufox, curl, Wayback, snapshot, rendering, crawl, pipeline, SPA shell, 429/403
- **Agent/model orchestration**: agent, subagent, delegate, cross-model verification, agent reach, round 1, round 2, two-round, supplement round, targeted follow-up round
- **Retry/repair process**: retry, second pass, resilience, rollback, "after correction", "after re-fetching"
- **Informal English terms mixed into prose**: vendor, marketing, workaround, fallback (proper nouns / field names are exempt)

### Handling data gaps

- A **verifiable public gap fact** (e.g. a page is no longer public, or a vendor does not break out a given metric) is written in neutral academic language and folded into the body wherever that fact naturally belongs.
- An item that remains unresolved after both rounds of the workflow below is either folded into its natural location with a neutral confidence marker, or removed if it carries no informative content on its own.
- **No standalone "data gaps" or "unresolved items" section or appendix.** Every gap disposition lives at the point in the report where the underlying claim would have appeared.

### Neutral academic substitutes

| Process language | Academic substitute |
|---|---|
| "still nothing after fetching" | "no corresponding material is publicly available" |
| "result of the retry search" | "supplementary verifiable fact" |
| "result of the fetch chain" | "carrier hit outcome" |
| "response no longer supported" | "no longer publicly available" |
| "vendor self-reported" | "self-reported by the provider" |
| "marketing page" | "its website home page" |

### The only "process" trace permitted

- The "access date" column in the reference table — this is a citation-format element, not a process trace.
- Terms like "fetch", "crawler", or "pipeline" appearing inside a *quoted source's own text* — that belongs to the cited material, not to this report's own working process.

### Pre-delivery check

```bash
grep -nE "fetch|Firecrawl|jina|archive\.today|Wayback|Camoufox|snapshot|crawl|retry|agent|subagent|pipeline|SPA|vendor|marketing|fallback|workaround|round 1|round 2|two-round|agent reach|supplement round|data gap(s)? section" report.md
```

A hit anywhere outside a reference-table source title means the draft is not final — clear the term or rewrite it in neutral academic language before delivery.

---

## Standard Research Dimensions

Select as needed:

1. **KYC / AML** — verification tiers, document requirements, biometric checks, high-risk jurisdiction restrictions, suspicious-activity reporting
2. **Transaction risk control** — anomaly detection, limit mechanisms, leverage/liquidation controls, wash-trading detection
3. **Account security** — anomalous-login detection, 2FA, account-freeze trigger conditions
4. **Fund security** — hot/cold wallet management, withdrawal review process, large-withdrawal allowlisting
5. **Regulatory compliance** — licensing status, FATF Travel Rule, sanctions screening (e.g. OFAC)
6. **Market integrity** — anti-manipulation controls, price-spike protection, liquidation mechanics

---

## Research Workflow

### Round 1 — Initial Pass

```
WebSearch (2-3 keyword variants, target language + English)
  ↓
Build a candidate URL list (not yet cited as fact)
  ↓
Record: [N] title — URL — search date
  ↓
WebFetch every candidate URL
  ↓
Extract concrete numbers / policy detail from the page text
  ↓
Cannot extract → mark [⚠️ page unreachable] or [data insufficient], do not cite
  ↓
Can extract → add to the citation list, assign N
  ↓
Draft the report body, attaching [N] to every claim as it is written
```

At the end of Round 1, compile a **working gap list** (an internal artifact, not a report section). For every item still marked `[unverified]` / `[⚠️ page unreachable]` / `[data gap]`, record: which dimension/platform it belongs to, the specific claim being sought, the URLs already attempted, and a failure-mode tag:

- **Tag A — blocked/rendered**: the source page exists but WebFetch could not read it (anti-bot block, JS-rendered shell, timeout).
- **Tag B — not found**: no source was found at all; the claim needs a different angle, a different source, or a different language.

If Round 1 produces no gap items, skip Round 2 entirely and go straight to integration.

### Round 2 — Targeted Follow-Up (single attempt per item, no retries)

Each gap item gets **exactly one** follow-up attempt, routed by its failure-mode tag. Whether it succeeds or fails, do not retry it and do not try the other channel on the same item.

- **Tag A items** → batch the affected URLs into one local anti-bot render pass (see `references/two-round-verification.md` in the sibling `evidence-research-report` skill for the fetch-resilience chain this project already ships, including the local-render tier). One pass per batch, not per URL. A page that renders with real body content is cited normally under Rule 1/Rule 2. A page that still fails is left with its Round-1 marker — final, no second attempt.
- **Tag B items** → batch same-type gaps into one dispatch to a general-purpose subagent, asking it to re-approach with a different keyword angle, a different language, or an alternate primary source, and to report back either a specific fact with its source URL, or a confirmation that no credible source exists. A negative result is final for that item — no second dispatch.

Do not open a third round. Do not combine both channels on the same item.

### Integration — One Final Report

Merge the Round 1 draft and the Round 2 outcomes into a single report:

- Items resolved in Round 2: rewrite the relevant sentence in place with the new fact and its `[N]`, in the section where it already lived — do not add a new section.
- Items still unresolved after Round 2: keep the Rule 3 confidence marker in its natural location (a sentence inside the platform's analysis, a table cell) — never collected into a separate list or appendix.
- Items with no informative content even as a gap (a plain "nothing found," not itself a fact worth stating): remove the claim entirely.
- Only after this merge, run Rule 4's pre-delivery citation audit.

---

## Report Output Format

### 1. Executive Summary (≤300 words)
Objective, scope, key findings, and headline observations.

### 2. Policy Landscape (if applicable)
Grouping of approaches with representative organizations.

### 3. Comparison Table

| Dimension | Org A | Org B | … |
|------|---------|---------|---|
| Mechanism X | … [N] | … [N] | … |

### 4. Per-Organization Analysis
For each organization:
- Mechanism overview (with `[N]`)
- Distinctive practices (with `[N]`)
- Recent material events / regulatory developments (with `[N]`)

### 5. Gap Analysis
(where data is sufficient) per-dimension status: met ✅ / partial ⚠️ / insufficient data ❓

### 6. Observations for Consideration
Prioritized (high/medium/low) points worth noting, each with a supporting reference `[N]`, phrased as observations rather than directives.

### 7. Reference List

| N | Source Title | URL |
|-----|---------|------|
| 1 | Example Source | https://... |

---

## Output Language

Match the language requested by the requesting team; default to the language of the request itself.

---

## Common Source Types

- Official documentation / help centers of the organizations under review
- Public regulatory notices, enforcement records
- Industry research (e.g. Chainalysis, Elliptic, Messari for crypto-specific work)
- News coverage of security incidents or regulatory action
- FATF / OFAC / FinCEN official publications
- Wayback Machine (fallback when an official page has been taken down)

---

## Pro Tips

- **Conflicting sources**: keep both readings, each attributed to its source, and let the requesting team judge.
- **Official page not found**: try Wayback Machine or established industry media before giving up.
- **Each search keyword**: try 2-3 variants (target language + English) to raise coverage.
- **Numbers in tables**: attach `[N]` directly in the cell, not only in surrounding prose.
- **Round 2 routing**: use the local-render channel only when a page demonstrably exists but won't load (anti-bot/JS); use the subagent channel when no source has been found at all. Don't spend a page's one attempt retrying a channel that already failed for the same reason.
