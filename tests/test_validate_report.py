import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import yaml  # noqa: F401 - only used by --ledger; validator skips when missing

    HAS_YAML = True
except ImportError:  # pragma: no cover - environment-specific
    HAS_YAML = False


ROOT = Path(__file__).resolve().parents[1]
VALIDATORS = (
    ROOT / "claude" / "evidence-research-report" / "scripts" / "validate_report.py",
    ROOT / "codex" / "evidence-research-report" / "scripts" / "validate_report.py",
)


VALID_REPORT = """# 示例报告

## 核心结论

供应商官网说明其产品支持地址筛查 [1]。

## 参考资料

| 序号 | 来源 | 链接 |
|---|---|---|
| 1 | 供应商产品文档 | https://example.com/product |
"""


LEDGER_REPORT = """# 深度示例

监管要求跨境转账必须完成受益人审查 [1]。该结论不构成合规建议 [推论]。

## 参考资料

| 序号 | 来源 | 链接 |
|---|---|---|
| 1 | 央行指引原文 | https://example.com/reg |
"""

VALID_LEDGER = """sources:
  - id: S1
    url: https://example.com/reg
    grade: S0
claims:
  - id: C1
    claim: 跨境转账必须完成受益人审查
    source_id: S1
    ref: 1
    status: supported
"""

BROKEN_LEDGER = """sources:
  - id: S1
    url: https://example.com/reg
claims:
  - id: C1
    claim: 跨境转账必须完成受益人审查
    source_id: S9
    ref: 1
    status: supported
"""


class ValidatorCliTests(unittest.TestCase):
    def run_validator(self, validator: Path, content: str):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.md"
            report.write_text(content, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(validator), str(report)],
                text=True,
                capture_output=True,
                check=False,
            )

    def test_valid_report_passes(self):
        for validator in VALIDATORS:
            with self.subTest(validator=validator):
                result = self.run_validator(validator, VALID_REPORT)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("PASS", result.stdout)

    def test_missing_reference_number_fails(self):
        for validator in VALIDATORS:
            with self.subTest(validator=validator):
                result = self.run_validator(validator, VALID_REPORT.replace("[1]", "[2]"))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("missing reference", result.stdout.lower())

    def test_reference_without_url_fails(self):
        for validator in VALIDATORS:
            with self.subTest(validator=validator):
                result = self.run_validator(
                    validator,
                    VALID_REPORT.replace("https://example.com/product", "无公开链接"),
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("http", result.stdout.lower())

    def test_unresolved_marker_fails(self):
        for validator in VALIDATORS:
            with self.subTest(validator=validator):
                result = self.run_validator(
                    validator,
                    VALID_REPORT.replace("供应商官网说明", "[待核实] 供应商官网说明"),
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("unresolved marker", result.stdout.lower())

    def run_validator_args(self, validator: Path, content: str, *args: str):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            report = tmpdir / "report.md"
            report.write_text(content, encoding="utf-8")
            extra = [str(a) for a in args]
            return subprocess.run(
                [sys.executable, str(validator), str(report), *extra],
                text=True,
                capture_output=True,
                check=False,
            )

    def test_check_list_emits_claim_rows(self):
        for validator in VALIDATORS:
            with self.subTest(validator=validator):
                result = self.run_validator_args(validator, VALID_REPORT, "--check-list")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("claim -> source checklist", result.stdout)
                self.assertIn("地址筛查", result.stdout)
                self.assertIn("https://example.com/product", result.stdout)

    def test_ledger_valid_passes(self):
        if not HAS_YAML:
            self.skipTest("pyyaml not installed; ledger cross-check skipped")
        for validator in VALIDATORS:
            with self.subTest(validator=validator):
                with tempfile.TemporaryDirectory() as tmp:
                    ledger = Path(tmp) / "ledger.yaml"
                    ledger.write_text(VALID_LEDGER, encoding="utf-8")
                    result = self.run_validator_args(
                        validator, LEDGER_REPORT, "--ledger", str(ledger)
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn("ledger cross-check OK", result.stdout)

    def test_ledger_unknown_source_fails(self):
        if not HAS_YAML:
            self.skipTest("pyyaml not installed; ledger cross-check skipped")
        for validator in VALIDATORS:
            with self.subTest(validator=validator):
                with tempfile.TemporaryDirectory() as tmp:
                    ledger = Path(tmp) / "ledger.yaml"
                    ledger.write_text(BROKEN_LEDGER, encoding="utf-8")
                    result = self.run_validator_args(
                        validator, LEDGER_REPORT, "--ledger", str(ledger)
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("unknown source", result.stdout)

    def test_check_urls_flags_dead_link(self):
        """--check-urls must FAIL a dead URL. Skips silently when offline (no network)."""
        for validator in VALIDATORS:
            with self.subTest(validator=validator):
                with tempfile.TemporaryDirectory() as tmp:
                    report = Path(tmp) / "report.md"
                    report.write_text(
                        VALID_REPORT.replace(
                            "https://example.com/product",
                            "https://example.com/definitely-missing-path-9f3k2",
                        ),
                        encoding="utf-8",
                    )
                    result = subprocess.run(
                        [sys.executable, str(validator), str(report), "--check-urls"],
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    if "skipped (no network" in result.stdout:
                        self.skipTest("offline")
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn("dead reference URL", result.stdout)


if __name__ == "__main__":
    unittest.main()
