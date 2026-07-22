import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
