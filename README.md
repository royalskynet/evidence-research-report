# Evidence Research Report

[简体中文](README.zh-CN.md)

A compact, evidence-first research skill for Claude Code and OpenAI Codex. It produces decision-ready reports without turning a small question into an open-ended, hour-long research project.

## What it does

- Routes each request to no-research, quick, standard, or deep mode.
- Treats search results as discovery only; a source must be opened and read before it can support a claim.
- Separates first-party statements, authoritative records, independent reporting, and inference.
- Stops when the decision questions are supported, two searches add no material evidence, or the declared budget is reached.
- Rejects unsupported superlatives and states material evidence gaps explicitly.
- Runs a deterministic validator for citation numbering, reference URLs, and unresolved markers.
- Does not require API keys, third-party models, runtime package installation, or shell startup files.

## Repository layout

```text
claude/evidence-research-report/   Claude Code edition
codex/evidence-research-report/    OpenAI Codex edition
hermes/mannie-evidence-research/   Hermes Agent edition (ERRG + ERRD + ERRJ + OSINT)
dist/                              Installable .skill archives
docs/                              English and Chinese documentation
tests/                             Deterministic validator tests
```

The editions share the same evidence policy, report patterns, deep-mode controls, evaluations, and validator. `SKILL.md` files differ where platforms require different tool wording or metadata.

> **Hermes edition**: Integrates ERRG (research), ERRD (debate audit), ERRJ (judgment), and OSINT presets into a single skill. Uses OmniRoute FREE LLM combo. Brief dependencies are `omniroute --port 20128`. n
## Quick start

Download the matching archive from `dist/`, inspect it, and extract it into your user skill directory:

```bash
# Claude Code
unzip dist/evidence-research-report-claude.skill -d ~/.claude/skills

# OpenAI Codex
unzip dist/evidence-research-report-codex.skill -d ~/.codex/skills
```

Restart the host application after installation. See [Installation](docs/INSTALLATION.md) for source installs, verification, updates, and uninstall instructions.

## Example prompts

```text
Confirm whether Vendor A documents a transaction-monitoring API. Keep the answer under 300 words.

Compare three vendors' documented sanctions-screening capabilities for a procurement decision.

Deeply compare the current regulatory requirements in three jurisdictions and provide a complete evidence chain.

This report is already verified. Reformat it only; do not research or change any claims.
```

The default report language is Simplified Chinese; product names and technical terms remain in their original language. A user instruction can override the output language and format.

## Evidence and cost controls

| Mode | Typical use | Default limit |
|---|---|---|
| No research | Formatting, translation, or organization of verified material | No search; no new claims |
| Quick | One narrow question or a short report | Up to 2 search batches; usually 2–4 strong pages |
| Standard | Vendor diligence, 2–5 subject comparison, formal report | Start with 2–3 search batches; usually 6–12 useful sources |
| Deep | Explicitly requested exhaustive work or an approved cross-jurisdiction escalation | Up to 4–6 search batches; usually 12–25 useful sources |

These are ceilings and operating ranges, not source quotas. Source quality and claim coverage decide when research is complete.

## Validation

From either installed skill directory:

```bash
python3 scripts/validate_report.py /path/to/report.md
```

The validator checks mechanical properties only. A `PASS` does not prove that a source semantically supports a claim; the agent must still verify every material claim against the cited source.

Run the repository tests with:

```bash
python3 -m unittest discover -s tests -v
```

## Documentation

- [Installation](docs/INSTALLATION.md) / [安装说明](docs/INSTALLATION.zh-CN.md)
- [Usage](docs/USAGE.md) / [使用说明](docs/USAGE.zh-CN.md)
- [Methodology](docs/METHODOLOGY.md) / [方法说明](docs/METHODOLOGY.zh-CN.md)
- [Security](SECURITY.md) / [安全说明](SECURITY.zh-CN.md)

## Privacy and provenance

This repository is a generic public release. It contains no organization-specific names, internal department labels, local filesystem paths, credentials, report contents, or private source lists. Example prompts use fictional placeholders.

## License

[MIT](LICENSE)
