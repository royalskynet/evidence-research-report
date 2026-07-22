# Installation

## Requirements

- Claude Code or OpenAI Codex with local skill support
- Python 3.10 or later for the optional report validator
- No Python packages, API keys, or external model accounts are required

## Install from an archive

Inspect the archive before extracting it:

```bash
unzip -l dist/evidence-research-report-claude.skill
unzip -l dist/evidence-research-report-codex.skill
```

Install one or both editions:

```bash
unzip dist/evidence-research-report-claude.skill -d ~/.claude/skills
unzip dist/evidence-research-report-codex.skill -d ~/.codex/skills
```

Each archive contains one top-level directory named `evidence-research-report`. Restart the host application so it discovers the new skill.

## Install from source

```bash
cp -R claude/evidence-research-report ~/.claude/skills/
cp -R codex/evidence-research-report ~/.codex/skills/
```

Review the target first if a directory with that name already exists. Replacing an existing installation overwrites local modifications.

## Verify

Confirm the manifest and run the validator tests:

```bash
test -f ~/.claude/skills/evidence-research-report/SKILL.md
test -f ~/.codex/skills/evidence-research-report/SKILL.md
python3 -m unittest discover -s tests -v
```

For Codex, `agents/openai.yaml` supplies display metadata and permits implicit invocation. Claude Code does not need that file.

## Update

Download or clone the new version, inspect the diff, then replace only the matching skill directory. This project has no auto-update mechanism and never downloads executable code at runtime.

## Uninstall

Remove only the directory you installed:

```bash
rm -r ~/.claude/skills/evidence-research-report
rm -r ~/.codex/skills/evidence-research-report
```
