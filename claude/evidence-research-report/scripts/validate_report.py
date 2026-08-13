#!/usr/bin/env python3
"""Validate deterministic citation and release gates for a Markdown report."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REFERENCE_HEADING = re.compile(
    r"^(?:#{1,6}\s*)?(?:[一二三四五六七八九十]+[、.]\s*)?"
    r"(?:参考资料|參考資料|References)\s*$",
    re.IGNORECASE,
)
CITATION = re.compile(r"\[(\d+)\]")
TABLE_REFERENCE = re.compile(r"^\|\s*(\d+)\s*\|")
LIST_REFERENCE = re.compile(r"^\s*\[(\d+)\]\s+")
URL = re.compile(r"https?://[^\s|)>]+", re.IGNORECASE)
UNRESOLVED_MARKERS = (
    "[待核实]",
    "[待核實]",
    "[待补来源]",
    "[待補來源]",
    "[⚠️ 待补来源]",
    "[⚠️ 待補來源]",
)


def _split_report(text: str) -> tuple[str, str, int | None]:
    """Return (body, reference_lines, reference_index)."""
    lines = text.splitlines()
    index = next(
        (i for i, line in enumerate(lines) if REFERENCE_HEADING.match(line.strip())),
        None,
    )
    if index is None:
        return "\n".join(lines), "", None
    body = "\n".join(lines[:index])
    return body, "\n".join(lines[index + 1 :]), index


def analyze(
    text: str,
) -> tuple[list[str], list[str], set[int], dict[int, str], str]:
    """Deterministic structural checks.

    Returns (errors, warnings, cited_numbers, references, body).
    references maps number -> full reference line.
    """
    errors: list[str] = []
    warnings: list[str] = []

    for marker in UNRESOLVED_MARKERS:
        if marker in text:
            errors.append(f"unresolved marker remains: {marker}")

    body, reference_text, reference_index = _split_report(text)
    if reference_index is None:
        errors.append("missing reference section heading")
        return errors, warnings, set(), {}, body

    reference_lines = reference_text.splitlines()
    citations = {int(value) for value in CITATION.findall(body)}
    if not citations:
        errors.append("no numeric citations found in report body")

    references: dict[int, str] = {}
    for line in reference_lines:
        match = TABLE_REFERENCE.match(line) or LIST_REFERENCE.match(line)
        if not match:
            continue
        number = int(match.group(1))
        if number in references:
            errors.append(f"duplicate reference number: {number}")
            continue
        references[number] = line
        if not URL.search(line):
            errors.append(f"reference {number} must contain an http(s) URL")

    for number in sorted(citations - references.keys()):
        errors.append(f"missing reference for citation [{number}]")

    if citations:
        expected = set(range(1, max(citations) + 1))
        for number in sorted(expected - citations):
            errors.append(f"citation numbering gap at [{number}]")

    for number in sorted(references.keys() - citations):
        warnings.append(f"reference [{number}] is not cited in the report body")

    return errors, warnings, citations, references, body


def validate(text: str) -> tuple[list[str], list[str]]:
    """Public validation entry point; returns (errors, warnings)."""
    errors, warnings, _, _, _ = analyze(text)
    return errors, warnings


def build_checklist(
    body: str, references: dict[int, str]
) -> list[tuple[int, str, str]]:
    """Machine-extracted claim -> source checklist for human semantic review.

    Each body line that carries at least one [N] citation becomes one row:
    (line_number, claim_text, "；"-joined "[N] <url>" sources).
    """
    rows: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(body.splitlines(), 1):
        numbers = sorted({int(v) for v in CITATION.findall(line)})
        if not numbers:
            continue
        claim_text = line.strip()
        if not claim_text:
            continue
        sources = []
        for n in numbers:
            src = references.get(n)
            urls = URL.findall(src) if src else []
            if urls:
                sources.append(f"[{n}] {urls[0]}")
            else:
                sources.append(f"[{n}] (missing reference)")
        rows.append((lineno, claim_text, "；".join(sources)))
    return rows


def _collect_urls(references: dict[int, str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for line in references.values():
        for url in URL.findall(line):
            url = url.rstrip(",.;，。；、")
            if url not in seen:
                seen.add(url)
                out.append(url)
    return out


def check_url(url: str, timeout: float = 8.0) -> tuple[bool | None, object]:
    """HEAD a URL. Returns (ok, detail).

    ok: True=2xx/3xx reachable, False=dead (4xx/5xx or explicit failure),
        None=connection-level failure (DNS/refused/timeout) — offline probe.
    """
    import urllib.error
    import urllib.request

    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "validate_report.py/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, resp.status
    except urllib.error.HTTPError as exc:
        return False, exc.code
    except Exception as exc:  # noqa: BLE001 - connection-level: offline probe
        return None, type(exc).__name__ + ": " + str(exc)


def check_urls(urls: list[str], timeout: float = 8.0) -> tuple[bool, list[tuple[str, bool | None, object]]]:
    """HEAD-check every URL. Returns (offline, [(url, ok, detail)]).

    offline=True when every request failed at connection level (likely no network).
    """
    statuses: list[tuple[str, bool | None, object]] = []
    connection_fail = 0
    for url in urls:
        ok, detail = check_url(url, timeout=timeout)
        statuses.append((url, ok, detail))
        if ok is None:
            connection_fail += 1
    offline = len(urls) > 0 and connection_fail == len(urls)
    return offline, statuses


def check_ledger(
    body: str, references: dict[int, str], ledger_path: Path
) -> tuple[list[str], bool]:
    """Deep-mode ledger cross-check.

    Loads a YAML sidecar (sources + claims). Verifies:
    - every claim entry that names a source_id resolves to a declared source;
    - citations actually present in the body are accounted for by a claim record.
    Returns (messages, fatal). Fatal=False means only advisory notes.
    """
    errors: list[str] = []
    try:
        import yaml

        data = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    except ImportError:
        return ["WARN: pyyaml not installed; ledger cross-check skipped"], False
    except Exception as exc:  # noqa: BLE001 - malformed sidecar
        return [f"invalid ledger YAML: {exc}"], True

    if not isinstance(data, dict):
        return ["invalid ledger: expected a mapping with 'sources' and 'claims'"], True

    sources = data.get("sources") or []
    claims = data.get("claims") or []
    if not isinstance(sources, list) or not isinstance(claims, list):
        return ["invalid ledger: 'sources' and 'claims' must be lists"], True

    source_ids = {
        s.get("id") for s in sources if isinstance(s, dict) and s.get("id")
    }
    body_cites = {int(v) for v in CITATION.findall(body)}

    ledger_refnums: set[int] = set()
    for c in claims:
        if not isinstance(c, dict):
            continue
        sid = c.get("source_id") or c.get("source")
        if sid and sid not in source_ids:
            errors.append(
                f"ledger claim '{c.get('id', '?')}' references unknown source '{sid}'"
            )
        ref = c.get("ref")
        if isinstance(ref, int):
            ledger_refnums.add(ref)
            if ref not in references:
                errors.append(
                    f"ledger claim '{c.get('id', '?')}' ref [{ref}] has no report reference"
                )

    # Every in-body citation should have a claim record in deep mode.
    uncovered = sorted(body_cites - ledger_refnums)
    if uncovered:
        errors.append(
            "ledger has no claim record for in-body citation(s) "
            + ", ".join(f"[{n}]" for n in uncovered)
        )

    if not errors:
        errors.append(f"ledger cross-check OK ({len(claims)} claims, {len(sources)} sources)")
    return errors, False


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check Markdown citation numbering, reference URLs, and unresolved markers; "
            "optionally emit a claim->source checklist, probe URL liveness, and "
            "cross-check a deep-mode YAML ledger."
        )
    )
    parser.add_argument("report", type=Path, help="Markdown report to validate")
    parser.add_argument(
        "--check-list",
        action="store_true",
        help="print machine-extracted claim -> source checklist for human semantic review",
    )
    parser.add_argument(
        "--check-urls",
        action="store_true",
        help="HEAD-probe reference URLs for liveness (skipped if offline)",
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        metavar="LEDGER.yaml",
        help="deep-mode YAML ledger sidecar path to cross-check",
    )
    args = parser.parse_args()

    try:
        text = args.report.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"FAIL: cannot read {args.report}: {exc}")
        return 2

    errors, warnings, citations, references, body = analyze(text)

    for warning in warnings:
        print(f"WARN: {warning}")

    if args.check_list:
        rows = build_checklist(body, references)
        print("\n== claim -> source checklist (human semantic review) ==")
        if rows:
            for lineno, claim_text, sources in rows:
                print(f"  L{lineno} | {claim_text}  ->  {sources}")
        else:
            print("  (no claim-carrying lines extracted)")
        print("  -- review each row: does the cited source semantically support the claim?")

    if args.check_urls:
        urls = _collect_urls(references)
        offline, statuses = check_urls(urls)
        if offline:
            print("\nURL liveness check skipped (no network / connection-level failures on all URLs)")
        else:
            dead = 0
            print("\n== reference URL liveness ==")
            for url, ok, detail in statuses:
                if ok is True:
                    print(f"  OK   {url}  ({detail})")
                elif ok is False:
                    dead += 1
                    print(f"  DEAD {url}  (HTTP {detail})")
                    errors.append(f"dead reference URL: {url} (HTTP {detail})")
                else:
                    print(f"  ?    {url}  ({detail})")
            if dead:
                print(f"  -> {dead} dead reference URL(s)")

    if args.ledger:
        lerrors, _ = check_ledger(body, references, args.ledger)
        ledger_errs = [
            m for m in lerrors
            if "cross-check OK" not in m and "skipped" not in m
        ]
        print("\n== deep-mode ledger cross-check ==")
        for msg in lerrors:
            prefix = "FAIL: " if msg in ledger_errs else "  "
            print(prefix + msg)
        errors.extend(ledger_errs)

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    body_only, _, _ = text.partition("参考资料")
    citation_count = len({int(value) for value in CITATION.findall(body_only)})
    print(f"PASS: {citation_count} cited source(s); deterministic checks complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
