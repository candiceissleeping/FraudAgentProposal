# 實驗 E 完整說明：除了「記不記得出事」，模型有沒有用到公司類型？

只用 Claude Opus 5.5。預先登錄：`protocol.md`（commit `90e2b3f`）；結果：`evaluation.md`。

## 0. 要回答的問題
第八輪 MEM 只給「公司名稱＋會計年度」，AUC 0.88。模型可能用了兩種資訊：
1. **記得結果**：記得這家公司後來重編或被 SEC 處分
2. **公司類型**：不知道結果，但從名稱知道是哪類公司（規模、上市地點、新公司或老公司…）

E 用兩種獨立的做法估計第 2 種的大小：
- **E1**：從「只給名稱」的回答裡，把「記得」的影響扣掉，看剩下多少區分力（不需新執行）
- **E2**：完全不給名稱，只給公司類型，看光靠類型能分到多少（新執行）

---

## 1. E1：扣掉「知道」後的殘差 AUC

### 資料
實驗 A 的 Opus 5.5 5 次執行（`results/mem_isolated/run1–5.json`）。每次模型對 28 家公司各回答：
- `risk_score`：0–100 的風險分數
- `knows_later_problems`：是否知道這家公司該年度後來出事

### 計算步驟（以第 1 次執行為例）
**步驟 1：依模型自己的回答分成兩組，算每組平均分數**
- 說「知道」：14 家（問題公司 12 家＋對照公司 2 家），平均 **75.7** 分
- 說「不知道」：14 家（問題公司 2 家＋對照公司 12 家），平均 **10.4** 分

**步驟 2：每家公司的分數減去它那一組的平均 → 殘差**
| 公司 | 組別 | 分數 | 說知道？ | 該組平均 | 殘差 |
|---|---|---|---|---|---|
| SAExploration | 問題 | 92 | 知道 | 75.7 | +16.3 |
| Welbilt | 對照 | 85 | 知道 | 75.7 | +9.3 |
| Becton Dickinson | 問題 | 30 | 知道 | 75.7 | −45.7 |
| Evoqua | 問題 | 22 | 不知道 | 10.4 | +11.6 |
| Mitek | 對照 | 18 | 不知道 | 10.4 | +7.6 |
| Gentex | 問題 | 5 | 不知道 | 10.4 | −5.4 |
| Boston Scientific | 對照 | 6 | 不知道 | 10.4 | −4.4 |
（28 家完整列表可由 `experiment/mem_models.py` 的 `strata()` 重算）

殘差的意思：在同樣「記得」（或同樣「不記得」）的公司之間，這家被打得比同組平均高還是低。

**步驟 3：用殘差算 AUC**
AUC = 把 14 家問題公司和 14 家對照公司兩兩配對（14 × 14 = 196 對），問題公司殘差較高的比例（相同算一半）。第 1 次執行得到 **0.566**。

**步驟 4：5 次各算一次，取平均**
| 執行 | 原始分數 AUC | 只用「知道」旗標的 AUC | 兩組平均（知道／不知道） | 殘差 AUC |
|---|---|---|---|---|
| run1 | 0.862 | 0.857 | 75.7／10.4 | 0.566 |
| run2 | 0.885 | 0.893 | 79.3／13.7 | 0.559 |
| run3 | 0.883 | 0.893 | 73.0／10.4 | 0.464 |
| run4 | 0.875 | 0.893 | 71.7／8.4 | 0.518 |
| run5 | 0.878 | 0.893 | 71.0／9.4 | 0.602 |
| **平均** | 0.88 | **0.89** | | **0.54** |

### 「只用知道旗標的 AUC」怎麼算
把「說知道」當 1 分、「說不知道」當 0 分，同樣算 AUC。第 1 次：問題公司 12/14 說知道，對照公司 2/14 說知道：
- 問題 1 分 vs 對照 0 分：12 × 12 = 144 對，問題公司贏
- 兩邊都 1 分：12 × 2 = 24 對，平手（算 12）
- 兩邊都 0 分：2 × 12 = 24 對，平手（算 12）
- 問題 0 分 vs 對照 1 分：2 × 2 = 4 對，問題公司輸
- AUC = (144 + 12 + 12) ÷ 196 = **0.857**

### 讀法
- 只用「知道」一個旗標排序（0.89）就等於用完整分數（0.88）→ 分數沒有比「記不記得」多帶任何資訊
- 扣掉「知道」後只剩 0.54（0.5 = 擲銅板）→ 在同樣記得或同樣不記得的公司之間，模型幾乎分不出問題公司
- 對照：時間外樣本（模型不可能記得）只給名稱是 0.69，那是公司類型能做到的程度；第八輪扣掉記憶後只有 0.54，比 0.69 低很多

---

## 2. E2：只給公司類型卡、不給名稱

### 2.1 卡片欄位與資料來源
原則：**每個值都是該會計年度當時的狀態**，不用任何事後資訊。例如 EDGAR 現在顯示 Latch 在 OTC 交易，那是出事下市之後的結果，用了就等於洩漏答案。

| 欄位 | 來源 | 為什麼是當年的 |
|---|---|---|
| 會計年度 | 樣本定義（當初抽樣記錄的 10-K） | — |
| 總資產 | 該年度 10-K 的 XBRL `us-gaap:Assets`，期末日＝會計年度結束日，申報編號＝該 10-K | 取自那一份 10-K |
| 公開流通市值 | 同一份 10-K 的 XBRL `dei:EntityPublicFloat` | 10-K 封面申報的數字 |
| 掛牌交易所 | 同一份 10-K 封面「Securities registered pursuant to Section 12(b)」那一欄 | 當年封面 |
| 在 SEC 申報的年數 | EDGAR 第一筆申報日到會計年度結束日 | 只算到當年 |
| 產業（L1、L2 才有） | 抽樣時記錄的 4 位數 SIC 代碼與 SEC 的名稱表 | 抽樣時的紀錄 |

資料來源：`data.sec.gov`（XBRL companyfacts、申報清單）與 `www.sec.gov`（10-K 原文、SIC 名稱表）。82 家公司（第八輪 28＋時間外 54）的原始值存在 `data/mem_type/facts.json`。

### 2.2 製作流程（`experiment/mem_type.py build`）
1. 從抽樣紀錄取每家公司的 CIK、SIC、該年度 10-K 的申報編號與期末日（第八輪：`config/round7_cases.json`、`results/round7/controls.json`；時間外：`data/mem_type/round9_pairs.json`）
2. 下載 XBRL companyfacts，挑出「申報編號＝該 10-K」的總資產與公開流通市值
3. 下載申報清單，找最早的申報日，以及該 10-K 的主文件名
4. 下載該 10-K 主文件，先移除開頭隱藏的 inline XBRL 區塊，再找「Securities registered pursuant to Section 12(b)」到封面下一個問題之間的文字，判斷 Nasdaq／NYSE／NYSE American／無
5. 依分級規則轉成文字，組成一行卡片

**實例（Latch，FY2021）**
- 原始值：總資產 4.52 億美元、流通市值 14 億美元、封面登記 Nasdaq、第一筆申報 2020-09-25（SPAC 時期）
- L1 卡：`industry: SIC 5072 Wholesale-Hardware; fiscal year ended 2021-12-31; total assets: $100 million-$1 billion; public float: $700 million-$5 billion; exchange listing (Section 12(b)): Nasdaq; filing with the SEC for: under 3 years`
- L2 卡：`industry: Wholesale-Durable Goods; fiscal year 2021; total assets: $100 million-$1 billion; public float: $700 million or more; exchange listing (Section 12(b)): Nasdaq; filing with the SEC for: under 3 years`
- **L3 卡（實際評分用）**：`fiscal year 2021; total assets: $100 million-$1 billion; public float: $700 million or more; exchange listing (Section 12(b)): Nasdaq; filing with the SEC for: under 3 years`

**分級**
| 欄位 | L1 | L2、L3 |
|---|---|---|
| 產業 | 4 位數 SIC 名稱 | L2：SIC 大類名稱；L3：不給 |
| 會計年度 | 精確結束日 | 只給年份 |
| 總資產 | 5 級：<1 千萬／1 千萬–1 億／1–10 億／10–100 億／≥100 億 | 3 級：<1 億／1–10 億／≥10 億 |
| 流通市值 | 6 級：<1 千萬／1 千萬–7,500 萬／7,500 萬–2.5 億／2.5–7 億／7–50 億／≥50 億 | 3 級：<7,500 萬／7,500 萬–7 億／≥7 億 |
| 交易所 | Nasdaq／NYSE／NYSE American／無 | 同左 |
| 申報年數 | <3／3–10／10–20／≥20 年 | 同左 |

**建卡時發現並修正的問題**（都在任何評分執行前修正，記在 `protocol.md` 修訂紀錄）
- 新式 inline XBRL 的 10-K 開頭有大段隱藏資料，第一版只讀前 6 萬字，讀不到封面，把 ADM、IMAX 等判成「無」→ 先移除隱藏區塊
- 有些封面把交易所表格放在 12(g) 那行之後（例：BONK 寫 12(b) None，表格列 Nasdaq）→ 讀到封面下一個問題為止
- 有些封面沒有 12(b) 登記行，程式誤抓到別段文字（例：Globaltek）→ 只認「Securities registered pursuant to/under Section 12(b)」這一行，找不到就算「無」
- 修正後抽查：Ideanomics、Malvern、SAExploration、AMMO 在 Nasdaq，CPI Aero、TransAtlantic 在 NYSE American；Adamis FY2020 封面 12(b) 寫的就是 None

### 2.3 先檢查：卡片能不能被認出是哪家公司（封閉式配對）
- 做法：一個無工具 Opus session，同時給 28 個公司名稱（含年度）與 28 張卡（不同順序），要求一一配對
- 預先登錄的標準：配對正確 ≤ 3 家；不通過就依序粗化 L1 → L2 → L3
- 結果：

| 等級 | 第八輪 | 時間外 | 判定 |
|---|---|---|---|
| L1 | 26/28 | 45/54 | 不通過 |
| L2 | 24/28 | 25/54 | 不通過 |
| L3 | 20/28 | 16/54 | 不通過 |

- 依預先登錄：三級都不通過時，以 L3 評分並在報告中標示
- 為什麼這不代表評分時認得出來：配對時模型手上有名單，只要在 28 個名字中挑規模、上市地點相符的就好；評分時沒有名單，必須自己猜（見 2.6 的結果：全部「unknown」）
- 這一步程式一開始也寫錯了：比對時要求模型回答的名稱連年度也一樣，顯示 0 家配對正確；看原始回覆後改為只比對名稱，重算結果如上

### 2.4 怎麼餵給 LLM
每次執行送出**一則訊息**：提示詞＋打亂順序的卡片清單，一行一張卡，編號 1–28（時間外 1–54）。提示詞全文：

```
# Company-type baseline

Below are 28 anonymized company profiles for one annual report each. You are NOT given the company names or the reports.
Every value describes the company as of that fiscal year.

For each profile, using only the profile and what you already know, rate the risk that the company's financial statements
for that fiscal year are materially misstated, through fraud or serious accounting errors (0 = no concern, 100 = almost
certainly misstated). Also give your best guess of which company it is ("unknown" if you cannot tell), and say whether you
know of later accounting problems, restatements or SEC enforcement involving that period.

Reply with only this JSON list, one entry per profile, in the order given, and nothing else:
[{"id": <number as listed>, "risk_score": <int>, "company_guess": "<name or unknown>", "knows_later_problems": <true|false>, "basis": "short reason"}, ...]

1. fiscal year 2018; total assets: $100 million-$1 billion; public float: $75-700 million; exchange listing (Section 12(b)): NYSE; filing with the SEC for: 20 years or more
2. fiscal year 2017; total assets: $1 billion or more; public float: $700 million or more; exchange listing (Section 12(b)): Nasdaq; filing with the SEC for: 10-20 years
...
```
- 提示詞的評分句與 MEM 完全相同，只把「公司名稱＋年度」換成卡片，並多問「猜是哪家公司」
- 每次以不同種子打亂順序（20261111–20261115），程式記下每個編號對應哪家公司，評分後再對回
- 模型回覆範例：`{"id": 1, "risk_score": 10, "company_guess": "unknown", "knows_later_problems": false, "basis": "Mid-size, long-tenured NYSE filer; moderate baseline risk"}`

### 2.5 執行環境：和實驗 A–D 完全相同
是的，同樣是 Claude Code CLI。執行地點是本專案的雲端工作環境（不是使用者的 Mac），由 `experiment/mem_type.py` 用 Python 依序呼叫，每次一個全新 session：
```
claude -p "<提示詞＋卡片清單>" --model claude-opus-5-5 --tools "" --strict-mcp-config \
       --setting-sources "" --no-session-persistence --output-format stream-json --verbose
```
- 每次在新建的空目錄執行（例：`/tmp/mem_jail_4xsnovg1`），Claude Code 2.1.319
- 正式執行前先跑 canary：無工具時答不出截止後的台股收盤；開放搜尋時被偵測
- 每次執行都通過 7 項檢查。第八輪 run1 的紀錄：啟動時 `tools: []`、`mcp_servers: []`；結束時一輪、伺服器端搜尋 0、`claude-opus-5-5` 搜尋次數 0；花費約 0.07 美元
- 封閉式配對的 6 個 session 也在同一個環境中執行
- 原始紀錄（`L3/{round8,oot}/raw/`）commit（`630fa7d`）之後才讀標籤計算

### 2.6 結果
| 樣本 | 5 次 AUC | 平均分數 AUC | 95% CI | 組內勝／平／負 | 猜中公司 | 說「知道」 |
|---|---|---|---|---|---|---|
| 第八輪 | 0.50／0.52／0.52／0.52／0.54 | **0.53** | 0.32–0.74 | 6／4／4 | 0／140 | 0／140 |
| 時間外 | 0.61／0.62／0.59／0.58／0.62 | **0.60** | 0.44–0.75 | 17／3／7 | 0／270 | 0／270 |

- 410 張卡模型全部回答「unknown」，沒有說知道任何公司出事 → 評分時沒有認出公司
- 第八輪 0.53 與 E1 的 0.54 一致
- 時間外 0.60 低於預先登錄的 0.62 門檻：L3 卡只抓到名稱帶的一部分類型資訊（只給名稱是 0.69）
- 第八輪平手多（4 對），一部分原因是配對設計：對照公司依產業與規模選出，同一對的類型本來就接近（ADM 與 Bunge 的 L1 卡甚至完全相同）

---

## 3. 合併判讀與限制
- **兩種獨立做法得到一樣的答案**：E1 從名稱回答扣掉記憶後 0.54，E2 不給名稱只給類型 0.53。在第八輪這批公司上，記憶以外的資訊貢獻很小，0.88 幾乎全部來自記得結果
- E2 的類型卡比名稱少了產業、知名度等資訊（時間外 0.60 對 0.69），所以 E2 單獨只能說明「規模、流通市值、交易所、申報年數」沒有區分力；名稱帶的其他資訊由 E1 涵蓋
- 封閉式配對三級都沒通過（已標示）；評分時則完全沒有認出公司
- 第八輪只有 14 對，CI 很寬；只用 Opus 5.5

## 4. 檔案與 commit
| 內容 | 位置 | commit |
|---|---|---|
| 預先登錄（含修訂紀錄） | `results/mem_type/protocol.md` | `90e2b3f` |
| 公司資料、建卡程式 | `data/mem_type/facts.json`、`experiment/mem_type.py` | `95168f8` |
| canary、封閉式配對 | `results/mem_type/raw/`、`results/mem_type/probe/` | `96c56e4` |
| 評分原始紀錄 | `results/mem_type/L3/{round8,oot}/` | `630fa7d` |
| 結果與判讀 | `results/mem_type/evaluation.md`、`L3/*_scores.csv` | `bb91ed1` |

重跑方式：
```
SEC_UA="<名稱 email>" python -m experiment.mem_type build
python -m experiment.mem_type probe --level L3
python -m experiment.mem_type run --level L3 --runs 5
python -m experiment.mem_type evaluate --level L3
```
