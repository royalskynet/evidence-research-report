# 檢索韌性（反封鎖／反爬）

任一搜尋引擎回驗證碼或空殼、或抓回疑似殼層頁面時，讀本檔並改用 `scripts/search_web.py`／`scripts/fetch_page.py` 的退路鏈，**不得就地放棄改寫「無法查證」**。

## 觸發時機

- 搜尋引擎直接 curl 回驗證碼（recaptcha、`Just a moment...`、`unusual traffic`）、空殼、或 HTTP 403／429／503。
- 抓回的頁面 body 含 `cf-challenge`、`verify you are human` 等反爬特徵。
- 抓回的頁面是 JS 渲染 SPA 殼層（字數過少且 `<script src` 密度高）。
- 瀏覽器報 `ERR_HTTP2_PROTOCOL_ERROR`（如 Bybit）。

## 搜尋退路（search_web.py）

優先序（`--engine auto` 依序輪替，首個成功即停；每引擎連 2 次封鎖即跳下一個，不做長 sleep 硬等）：

1. 金鑰引擎：Firecrawl `/v1/search`（有 key 才用）；其他金鑰引擎（Tavily／Brave／Serper／Exa）偵測到才用。
2. 免金鑰：DuckDuckGo html → DuckDuckGo lite → Mojeek。
3. harness 原生 WebSearch（如有）。

輸出每行 `TITLE\tURL`（organic，去引擎跳轉包裝）。`exit 0`=有結果、`2`=全引擎被封／失敗、`3`=無結果。

## 抓取退路（fetch_page.py）

優先序：

1. `curl`（擬真 headers，HTTP/2 錯誤自動加 `--http1.1` 重試一次）。
2. 封鎖／殼層偵測 → Firecrawl `/v1/scrape`（有 key；自帶 JS 渲染）。
3. r.jina.ai（免金鑰）。
4. web.archive.org 最近快照。
5. archive.today。
6. 本地 Camoufox 渲染（見 `setup_render.sh`）。

stderr 標明最終管道與快照日期。`exit 0`=成功、`2`=全鏈失敗、`4`=取回但疑似殼層。

### 引用規範

- Firecrawl／jina／Wayback／archive.today 取回內容＝「讀取實際頁面」，可支撐正文；但**參考資料須標註取得管道與快照日期**（鏡像有時效風險）。
- 本地渲染＝等同直讀原站，無此限制。
- **時效敏感主張**（費率、政策、牌照）優先本地渲染直讀原站，避免依賴鏡像。

## SPA 判別

下列域名已知為 SPA，直接走渲染層，不浪費 curl 重試（可依現況增補）：

- `www.okx.com/help`
- `www.bybit.com/en/help-center`
- `www.gate.io`
- `www.lbank.com`

一般判別：body 字數 < 500 且 `<script src` 密度高、正文節點空、含「loading…」或導航殼。

## 禮貌性與 cooldown（硬規則）

- 同域名連續請求間隔 ≥ 3s。
- 被 429／403 的域名進 cooldown ≥ 10 min，期間只走 mirror／渲染路徑。
- 單引擎連 2 次封鎖即跳下一個，不做長 sleep 硬等。
- 不做大規模並發爬取。

## 金鑰紀律

- 金鑰只存 `~/.hermes/.env` 與 private repo `hermes-env-sync`；public repo 永不含金鑰。
- 腳本啟動時 parse `~/.hermes/.env`（只讀 `KEY=VALUE`，不 source）；缺 key 的引擎靜默跳過自動降級，不報錯中斷。
- 金鑰服務只收目標 URL／搜尋 query，不收報告內容；仍禁止把報告內容、主張清單、API key 外送任何第三方。
