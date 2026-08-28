# Dev Log — Two-Round Verification Pattern

**Date**: 2026-08-28
**Scope**: `claude/competitive-research-report/`

## Problem

The existing `evidence-research-report` skill already ships a strong single-pass fetch-resilience chain (`references/retrieval-resilience.md`): when a source is blocked or renders as an empty SPA shell, it walks curl → keyed scrape API → mirror → archive → local anti-bot render, and only gives up once every tier in that chain has failed. That answers "how do I get *this one page*" reliably.

It does not answer a different question that came up in a separate, more compliance-flavored research workflow: what do you do with the *list of claims that still have no source* once a first full research pass is done? Retrying every one of them indefinitely is not affordable, and quietly dropping them loses information that is itself sometimes worth stating (e.g. "this metric is not broken out publicly"). The report also needs to read as a finished piece of analysis, not as a log of what was tried and failed.

## Approach

`claude/competitive-research-report/SKILL.md` adds a second, smaller loop on top of a normal research pass:

1. **Round 1** runs the normal search → fetch → cite flow and produces a draft plus an internal (non-published) gap list: every claim that ended up with a `[unverified]` / `[⚠️ page unreachable]` / `[data gap]` marker, tagged by why it failed — page exists but wouldn't load ("blocked/rendered"), or no source was ever found ("not found").
2. **Round 2** gives each gap item exactly one follow-up attempt, routed by that tag:
   - blocked/rendered items go through the same local anti-bot render tier the fetch-resilience chain already has, batched rather than retried per URL;
   - not-found items go to a single subagent dispatch that tries a different angle (language, phrasing, alternate primary source) once.
   
   Whichever channel is used, the rule is strict: one attempt, no retry, no falling back to the other channel for the same item. This keeps Round 2 bounded regardless of how many gaps Round 1 produces.
3. **Integration** merges both rounds into one report. Resolved items get rewritten in place with their new citation. Still-unresolved items keep their confidence marker exactly where the claim would have lived — inside the relevant paragraph or table cell. There is deliberately no "data gaps" or "unresolved items" section: aggregating them separately is what made earlier drafts read like a status report on the research process instead of a report on the subject matter.

## Why this is a separate skill instead of a mode flag on `evidence-research-report`

The two skills serve different report shapes: `evidence-research-report` is decision-support-generic (S0-S4 evidence tiers, quick/standard/deep routing) for open-ended due-diligence questions. `competitive-research-report` is built around a fixed peer-comparison output (comparison table + per-organization sections across a fixed dimension list) for benchmarking exercises, which is where the round-1/round-2/gap-ledger discipline actually matters — those reports get read by an audience that needs a finished analytical document, not a research trace. Keeping it a separate skill avoids overloading `evidence-research-report`'s mode system with a workflow shape it wasn't designed for. The local-render tier is deliberately reused rather than reimplemented — see `claude/evidence-research-report/references/retrieval-resilience.md`.

## Note on origin

This pattern was generalized from an internal compliance-research skill built for a specific organization. Organization identity, internal KPI-alignment hooks, and a named peer list were removed before publication here, consistent with this project's existing practice of stripping organization-specific detail from public releases (see `CHANGELOG.md` 1.0.0).
