# Changelog / 更新记录

## 1.1.0 — 2026-08-13

- Validator: add `--check-list` claim→source checklist, `--check-urls` URL-liveness probe (offline-safe), and `--ledger` deep-mode YAML ledger cross-check.
- References: add S0 authority-source quick table (OpenSanctions / OpenCorporates / jurisdiction portals) and an archive-URL rule for consequential sources.
- Deep mode: replace free-form ledgers with a structured YAML source/claim sidecar, cross-checked by the validator.
- Planning: perspective-guided question decomposition in standard and deep modes.
- Two new evals: `sanctions-authority-direct`, `archive-url-on-consequential`.

---

- 驗證器：新增 `--check-list` 主張→來源核對清單、`--check-urls` 連結存活探測（離線自動跳過）、`--ledger` 深度模式 YAML 台帳交叉檢查。
- 參考文件：新增 S0 權威源直達表（OpenSanctions／OpenCorporates／各司法區入口）；重要主張來源附存檔 URL 規則。
- 深度模式：來源／主張台帳改為結構化 YAML sidecar，由驗證器交叉檢查。
- 規劃：標準／深度模式改為視角引導的必答問題分解。
- 新增 2 條 eval：`sanctions-authority-direct`（權威源直達）、`archive-url-on-consequential`（重要主張存檔 URL）。

## 1.0.0 — 2026-07-22

- Published separate Claude Code and OpenAI Codex editions.
- Added quick, standard, deep, and no-research routing with explicit stop conditions.
- Added claim-level evidence rules and a deterministic local report validator.
- Added bilingual installation, usage, methodology, and security documentation.
- Removed organization-specific names, internal roles, local paths, and named evaluation subjects from the public release.

---

- 发布独立的 Claude Code 版与 OpenAI Codex 版。
- 加入快速、标准、深度与不调研路由，以及明确停止条件。
- 加入主张级证据规则与本地确定性报告验证器。
- 补充中英文安装、使用、方法与安全说明。
- 从公开版移除组织名称、内部角色、本机路径与具名评测对象。
