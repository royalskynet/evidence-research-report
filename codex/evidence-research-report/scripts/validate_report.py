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


def validate(text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for marker in UNRESOLVED_MARKERS:
        if marker in text:
            errors.append(f"unresolved marker remains: {marker}")

    lines = text.splitlines()
    reference_index = next(
        (index for index, line in enumerate(lines) if REFERENCE_HEADING.match(line.strip())),
        None,
    )
    if reference_index is None:
        errors.append("missing reference section heading")
        return errors, warnings

    body = "\n".join(lines[:reference_index])
    reference_lines = lines[reference_index + 1 :]
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

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Markdown citation numbering, reference URLs, and unresolved markers."
    )
    parser.add_argument("report", type=Path, help="Markdown report to validate")
    args = parser.parse_args()

    try:
        text = args.report.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"FAIL: cannot read {args.report}: {exc}")
        return 2

    errors, warnings = validate(text)
    for warning in warnings:
        print(f"WARN: {warning}")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    body, _, _ = text.partition("参考资料")
    citation_count = len({int(value) for value in CITATION.findall(body)})
    print(f"PASS: {citation_count} cited source(s); deterministic checks complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
