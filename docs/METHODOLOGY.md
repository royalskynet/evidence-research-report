# Methodology

## Design goals

The skill optimizes for four properties in order:

1. Every material claim is traceable to a source that was actually opened and read.
2. The evidence is appropriate for the claim being made.
3. Research effort is proportional to the decision.
4. The final report is concise enough to use.

## Source classes

| Class | Typical sources | Appropriate use |
|---|---|---|
| S0 | Current law, regulators, courts, public registries, formal filings, primary datasets | Legal requirements, registration, judgments, filed facts |
| S1 | Company sites, product/API docs, announcements, status and security pages | What the organization publishes or claims |
| S2 | Counterparty announcements, editorially accountable media, procurement records | Independently reported events or a counterparty's position |
| S3 | Research with disclosed methods, academic or industry analysis | Conclusions within the stated sample, date, and method |
| S4 | Forums, social posts, aggregators, search snippets | Leads for further investigation only |

“Official first” is claim-dependent. A product manual is primary evidence for a documented feature, while a regulator or statute is primary evidence for a legal requirement. First-party marketing alone cannot establish effectiveness or market leadership.

## Claim rules

- Open and read the source before citing it.
- Verify subject, scope, date, and qualifiers—not just matching keywords.
- Mark analysis as `[Inference]` or the requested language equivalent and cite the underlying facts nearby.
- Prefer two independent sources for consequential or disputed claims, unless one authoritative S0 document directly resolves the point.
- State “not found in the public sources reviewed” instead of claiming that something does not exist.
- Preserve the procedural state of allegations, investigations, judgments, settlements, and sanctions.

## Cost controls

Research begins with at most three to five decision questions. Search batches combine independent queries where the platform permits. After each batch, the agent identifies a specific missing fact that could change the conclusion. If none exists, research stops.

Automatic stop conditions are:

- every decision question has adequate support;
- two consecutive searches add no material evidence; or
- the selected mode's declared ceiling is reached.

Reaching the ceiling produces an evidence-gap statement; it does not silently upgrade the task.

## Release gate

Before delivery, the agent checks every material claim against its cited source, resolves source conflicts explicitly, removes unsupported content, and runs the deterministic validator. The validator is deliberately narrow and local: it does not fetch URLs or judge semantic entailment.
