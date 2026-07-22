# Security

## Runtime boundary

The skill is instruction text plus one standard-library Python validator. It:

- reads only the report path supplied by the user;
- writes no files;
- makes no network requests;
- reads no environment variables, credentials, browser data, agent memory, or shell startup files;
- executes no subprocesses and installs no packages;
- has no persistence, telemetry, auto-update, or secondary-download mechanism.

The validator prints local pass, warning, or failure messages and exits with a conventional status code.

## Review before installation

Treat every skill as executable guidance. Inspect the archive listing, `SKILL.md`, and `scripts/validate_report.py` before installation. Install from a pinned commit or release and compare published checksums when available.

## Report data

Research reports may contain sensitive business information. The skill does not transmit report contents by itself, but the host agent's browsing tools may send search queries or URLs to their configured providers. Do not include confidential report text in search queries, and follow your organization's data-handling rules.

## Reporting a vulnerability

Open a GitHub security advisory or a minimal issue that does not contain secrets. Include the affected version, file, reproducible behavior, and expected boundary.
