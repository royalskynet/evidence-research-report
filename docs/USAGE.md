# Usage

## Invocation

Mention the skill explicitly when you want deterministic routing:

```text
Use evidence-research-report in quick mode to verify whether Vendor A documents feature X.
```

The Codex edition may also be invoked implicitly when the request clearly asks for source-verified diligence, comparison, regulatory research, or decision support.

## Choose a mode

- **No research:** formatting, translation, or restructuring of already verified material. No search and no new claims.
- **Quick:** one or two decision questions, a narrow fact check, or a short answer.
- **Standard:** formal diligence or comparison across two to five subjects.
- **Deep:** only when the user explicitly requests exhaustive work or approves a material cross-jurisdiction escalation.

High stakes do not automatically mean deep mode. A narrow legal question can use quick or standard mode if the current primary legal text directly answers it.

## Give a good request

Include the decision question, subjects, time cutoff, output language, and length when they matter:

```text
As of 2026-06-30, compare Vendor A and Vendor B on documented screening coverage and public limitations. Use standard mode, Simplified Chinese, no more than 1,200 words.
```

The skill asks at most one clarifying question, and only when the missing detail would materially change the result.

## Expected output

- Direct conclusion first
- Scope and data cutoff
- Verified facts with numbered citations
- Explicitly labeled inference, when needed
- Material evidence gaps
- A reference table containing full URLs

The structure remains proportional to the question. Empty boilerplate sections are omitted.

## Formatting-only boundary

If you say the content is already verified and request formatting only, the skill must not browse, add evidence, or alter claims. This prevents a small editing request from silently becoming a research task.

## Validate a saved report

```bash
python3 scripts/validate_report.py report.md
```

Resolve every `FAIL` before delivery. Review warnings and remove unused references when appropriate.
