---
name: mannie-evidence-research
description: "Evidence Research (ERRG) + Debate Audit (ERRD) + Judgment (ERRJ) + OSINT — 最小足夠研究，證據為先，OmniRoute FREE LLM combo 驅動。單一技能完整流程。"
version: 2.0.0
author: Mannie (fork of evidence-research-report)
license: MIT
metadata:
  hermes:
    tags: [Research, OSINT, Due-Diligence, Evidence, Debate, Audit]
    model: omniroute
    base_url: http://127.0.0.1:20128/v1
    api_key: dummy
    commands:
      errg: "Evidence Research Report — <topic> 來源驗證研究報告"
      errd: "Debate Audit — <topic> 產生 audit packet（含前情提要）"
      errj: "Judgment — 收到外部 <reply> 後逐項裁決"
---

# Mannie Evidence Research (整合版)

以最小足夠研究回答決策問題。證據品質優先於來源數量；無法核實就排除。

## 整體流程

```
errg <topic> → 研究報告 (Markdown)
     ↓
errd <topic> → audit packet (前情提要 + 爭點 + Flag + 來源)
     ↓
使用者自行 → 外部模型審查 (拿 audit packet + 報告去別處)
     ↓
errj <reply> → 接收外部回覆，逐項裁決
```

## 深度路由

| 模式 | 預算 |
|------|------|
| 快速 | ≤2 搜索批次，2-4 強來源 |
| 標準 | 2-3 搜索批次，6-12 有效來源 |
| 深度 | 跨轄區詳盡；先確認範圍 |

高風險不自動升級。除非用戶明示。

## 核心證據規則

1. 搜索發現候選 → 引用前必須 fetch/read 實際頁面
2. AI 摘要/標題/無法讀取頁面不進正文
3. 公司官網只證明自述；成效/爭議需獨立來源
4. 法律/監管/法院/登記優先原文
5. 重要主張後 `[N]`；同一 URL 固定編號
6. 無法核實 → 寫「已查未確認」
7. 推論標 `[推論]`，附事實引用
8. 不設來源配額，不用星級評分

## 來源分級（報告適用）

| 等級 | 適用 | 可證明 | 不足處 |
|------|------|--------|--------|
| S0 | 法律/監管/法院/登記/原始資料 | 法規內容、裁判、申報 | 延伸結論 |
| S1 | 公司官網/API文檔/公告 | 自述、規格、公告 | 績效、獨立驗證 |
| S2 | 合作方公告/獨立媒體/採購文件 | 合作方立場、採用 | 未披露條款 |
| S3 | 研究方法說明/學術分析 | 方法範圍內 | 跨範圍結論 |
| S4 | 社群/論壇/聚合 | 後續線索 | 核心結論 |

## ERRG — 執行流程

1. 提取決策問題、範圍、截止時間、語言、篇幅
2. 列 ≤5 必答問題
3. 中英文查詢，合併搜索
4. 先抓最可能回答的頁面
5. 每輪後檢查「缺哪個會改結論」，具名缺口繼續，否則停止
6. 繁體中文 Markdown；停止條件：必答都有來源／連兩次無新證據／達上限

## 輸出格式

```markdown
# [主題] — 證據研究報告
## 研究範圍
## 核心發現
## 詳細分析
## 資料缺口
## 證據邊界
## 參考資料
[N] [來源], [日期], 查閱 [日期], [URL]
```

## ERRD — Debate Audit

既存報告魔鬼代言人挑戰。

### 規則
1. 異議皆需可查證來源
2. AI摘要/無法讀取頁面/匿名 → 不進
3. 無反方證據 → `INSUFFICIENT_ADVERSARIAL_EVIDENCE`
4. 外部新來源/URL → 標 `OUT_OF_RECORD_REJECTED`
5. 原報告只讀不覆蓋

### Packet 格式

```markdown
## 前情提要 (Context)
[一段話摘要決策背景和核心結論]

## 核心結論
[原報告的核心結論]

## 爭點 #1
- **主張**: [原文]
- **來源等級**: [S0-S4]
- **Flag**: [inference|extrapolation|no-source|single-source|stale]
- **反方證據**: [若有，附來源]
- **影響層級**: [HIGH/MEDIUM/LOW]

## 證據邊界記錄
[資料截止日、已查未確認項目]
```

### 硬性上限

- 最多 5 爭點
- Packet 目標 ≤ 6000 中文字
- 無高影響異議 → 立即停止

## ERRJ — 裁決

收到外部回覆後：

- `PRO_WINS`：正方成立
- `CON_WINS`：反方成立 → 修正建議
- `SPLIT`：各有理 → 修正建議
- `UNRESOLVED`：證據不足 → 缺口

雙方相同證據閘門。

## OSINT 預設

| 需求 | 預設方向 |
|------|----------|
| 競品分析 | S1 官網 + S2 獨立媒體 + 產品對照 |
| 服務商盡調 | S0 公司登記/訴訟 + S1 官網 + S2 合作方 |
| 被盜事件 | S2 獨立媒體 + S0 官方通報 + S4 社群時序 |
| 監管誠信 | S0 SEC EDGAR / OFAC SDN 優先 |

制裁措辭：只能寫「在已查清單與時間點未命中」。

## 工具層

- **LLM**：OmniRoute FREE (127.0.0.1:20128/v1)
- **搜索**：OmniRoute web_search
- **頁面讀取**：markdown convert/fetch
- **交叉驗證**：user 自行拿 packet + 報告外部核實

## 驗收

- 交付前逐項語義核實（非抽查）
- 驗收失敗 → 修正後重交
- Validator missing → `skipped`，不說 `pass`
