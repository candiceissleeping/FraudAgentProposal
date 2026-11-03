# 第十輪：復刻 FraudDebate-Agent 的 LLM 基準，量測記憶的影響（預先登錄）

本文件在建立樣本、下載 MD&A 全文、執行任何 LLM 之前提交。提交前只做了三件事：下載 Bao et al. 複製資料、下載 farr 的 gvkey→CIK 對照表、測試各網域能否連線。這些步驟都不看 LLM 輸出，也不看任何分數。之後的修改一律記在 §10「修訂紀錄」，附日期與理由；§7 的假設與判讀標準提交後不得更改。

## 0. 目的與研究問題
復刻對象：Yue, Yang & Liu (2026), *FraudDebate-Agent*, *Mathematics* 14(15), 2695, doi:10.3390/math14152695。表 3 的「GPT-4 zero-shot reading the filing」AUC 為 0.681。本 repo 第七輪的整份 10-K 不遮蔽 AUC 是 0.90，只給名稱是 0.88。

1. 在他們的資料（FY2003–2008 測試集）上，LLM 的記憶有多大？
2. 0.681 和 0.90 差這麼多，主因是「樣本多半是模型不認得的小公司」，還是「模型比較舊」？
3. 改用本 repo 的事實卡方法（遮蔽 → 抽取 → 引文驗證 → 卡片 → 評分），結果如何？

候選解釋（每一項都對應 §8 的一個分析）：
| 代號 | 解釋 | 對應分析 |
|---|---|---|
| E1 | 舞弊公司多半冷門、沒有新聞報導，模型不認得 | §8.2 知名度分層 |
| E2 | 極度不平衡（母體約 0.7% 舞弊）；我們先前是 1:1 配對 | AUC 不受盛行率影響；另報加權 PR-AUC、P@1% |
| E3 | 標籤是公司年度：舞弊公司在錯報期以外的年度算正常，記憶會把這些年度打高分 | §8.3 公司層級 vs 公司年度層級 |
| E4 | 我們先前的樣本刻意挑知名案例 | §8.2：只看知名組時是否接近 0.90 |
| E5 | 模型新舊 | §8.1 各模型並列；R4 |
| E6 | 提示詞與輸出格式（0–1 機率 vs 0–100 分；只給 MD&A vs 整份 10-K） | A 組與第七輪格式的差異列表；D 組 |

## 1. 資料來源
| 資料 | 來源 | 狀態（提交時） |
|---|---|---|
| AAER 標籤 + 28 項會計數字 + 14 個比率 | Bao et al. (2020) 複製資料 `data_FraudDetection_JAR2020.csv`（raw.githubusercontent.com/JarFraud/FraudDetection） | 已下載；146,045 列，FY1990–2014 |
| gvkey → CIK | Ian Gow 的 R 套件 farr 的 `gvkey_ciks` 資料（raw.githubusercontent.com/iangow/farr），以 `pyreadr` 讀取 | 已下載；49,089 列 |
| MD&A（Item 7） | EDGAR-CORPUS（huggingface.co/datasets/eloukas/edgar-corpus），`section_7` 欄位 | 網域可連，尚未下載 |
| 公司名稱、舊名、10-K 報告期間 | SEC `data.sec.gov/submissions/CIK##########.json`（User-Agent 同前幾輪） | 可連 |
| 時間外對照 | 本 repo `results/round9/pairs.json`（27 對 8-K 4.02，2026-07～10） | repo 內 |

論文說 Bao 資料與 MD&A「以 CIK/gvkey + 會計年度連結」，但沒有公布連結表。Bao 資料只有 gvkey，所以本輪改用 farr 的公開對照表。這是一項與論文的差異，報告時要註明。

## 2. 樣本建構（每一步記錄流失數，寫入 `results/round10/attrition.tsv`）
1. Bao 資料中 FY2003–2008 的全部公司年度。標籤 = `misstate`（原樣使用）。提交前已算出：35,166 列，其中 `misstate = 1` 有 261 列。
2. gvkey 補零到 6 位後對應 CIK。一個 gvkey 對到多個 CIK 時，保留全部候選 CIK，到第 3 步再用 EDGAR-CORPUS 是否有資料來決定。對到的有效期間（first/last_date）只用來排序候選，不用來排除。提交前已算出：30,675 列對得到，261 件舞弊全部對得到。
3. 找出對應的 10-K：
   - 依 Compustat 慣例，期末月份 ≥ 6 時 fyear = 期末年，否則 fyear = 期末年 − 1
   - 用 submissions JSON 取該 CIK 的 10-K 系列（10-K、10-K405、10-KSB 及其 /A 以外的原始版）的 `reportDate`，選出期末對應這個 fyear 的那一份原始申報，記錄其申報年
   - submissions 查不到時，退而假設申報年 = fyear + 1，並標記 `period_inferred = 1`
4. 在 EDGAR-CORPUS 該申報年的資料（train／validate／test 三個檔都找）中找 `cik` 相符的那一筆，取 `section_7`
5. 可解析的 MD&A：`section_7` 以空白切分 ≥ 100 個 token（與論文的 ≥ 100 tokens 一致；論文沒說用哪種斷詞，這裡用空白斷詞）
6. 抽樣：
   - **主樣本 M**：全部合格的舞弊公司年度，加上合格的非舞弊公司年度中，以種子 `20261103` 用 `random.Random(seed).sample` 抽出的 10 倍數量（**不配對**）。非舞弊的抽樣池包含舞弊公司在錯報期以外的年度。
   - **補充樣本 S**（給 §8.3 用）：舞弊公司（FY1991–2008 任一年 `misstate = 1` 的 gvkey）在 FY2003–2008 的其他合格非舞弊年度中，不在 M 的那些。S 超過 300 筆時，以同一種子抽 300 筆。
   - **D 組子樣本**：M 裡的全部舞弊，加上同一種子從 M 的非舞弊中抽出的 150 筆，作為 D 組與 A／B／C 組的比較子集。M 的舞弊超過 150 件時，隨機取 150 件。
7. 論文報告測試集有 118 件舞弊。我們的數量若不同，照實報告，不做調整；兩者差距超過 ±30% 時，另外列出可能原因。

**敏感度分析（描述性）**：Bao et al. 在處理「跨訓練／測試期的連續舞弊」時有特別處理。另做一版：排除 `p_aaer` 也出現在 FY ≤ 2002 的舞弊公司年度。

## 3. 輸入的處理
- **截斷**：Llama-3-70B 的上下文長度是 8k token，論文想必也截斷過，但沒說截斷方式。本輪一律取 MD&A 的前 **4,500 個空白 token**，所有模型、所有組都相同。
- **遮蔽（B、D 組）**：`experiment/edgar_risk/redact.py` 的 `make_redactor(aliases, fiscal_year, reference_text)`。aliases = submissions 的名稱、舊名，加上程式從名稱產生的簡稱（沿用第九輪 f 的做法）。CIK、網址、人名、地名一律遮蔽，年份改成 Y0／Y-1／Y+1 等相對年。
- 每份輸入、遮蔽後文字、送出的完整提示都存檔（`data/round10/inputs/`），結果才能重現。

## 4. 實驗組
| 組 | 模型看到什麼 | 輸出 |
|---|---|---|
| **A 復刻基準** | `[CIK-FY]`（`CIK: <cik>, fiscal year: <fy>`）+ 截斷後 MD&A **原文** | 舞弊機率 0–1 |
| **B 遮蔽版** | 同一份 MD&A 遮蔽後，表頭改為 `[COMPANY-Y0]` | 舞弊機率 0–1 |
| **C 只給名稱** | 公司名稱（申報當時的名稱）+ 會計年度，不給任何文字 | 舞弊機率 0–1 + 記憶探針 |
| **D 事實卡** | 遮蔽後 EDGAR-CORPUS 的全部可用章節（1、1A、3、7、7A、8、9、9A、9B）→ 抽取（`data/round8/extract_prompt.md`，原文照用）→ 程式驗證引文 → 卡片 → 評分（`data/round8/judge_prompt.md`） | 0–100 分 |

**D 組卡片**：主分析用 **L3 紅旗總數卡**（第九輪 e 的最終設計）。數字警訊沒有 XBRL，改用 Bao 資料的 Compustat 項目，依第九輪 c 的四個定義計算（Beneish M、Dechow F、應計、現金流量 vs 淨利）；算不出來的項目從分母扣掉。次分析用完整事實卡（J0，只含 F 欄位與可算出的比率）。

**自述探針（全部組）**：分數輸出之後，**在同一個回答裡**接著回答：
- `recognised`：是否認得這家公司
- `guess`：猜的名稱
- `knows_later_problems`：是否知道後來有重編或 SEC 處分

C 組另外分開問兩題：`knows_accounting_problems`、`knows_sec_enforcement`（與第九輪 b 的 `memory_prompt.md` 相同）。

**提示詞**：論文沒有公布 zero-shot 提示，A 組提示由本輪自行撰寫，存為 `data/round10/prompt_A.md`（B、C 同目錄），在試跑前提交，報告時要註明「非原作者提示」。提示要求只輸出 JSON：`{"fraud_probability": <0-1>, "reason": "...", "recognised": ..., "guess": "...", "knows_later_problems": ...}`。

## 5. 模型
| 模型 | 固定版本 ID | 訓練截止（官方來源） | 推論管道 | 提交時狀態 |
|---|---|---|---|---|
| GPT-4 Turbo（論文用） | `gpt-4-turbo-2024-04-09` | 2023-12-01（OpenAI 模型頁 developers.openai.com/api/docs/models/gpt-4-turbo） | OpenAI API、Batch API | **未就緒**：沒有金鑰，api.openai.com 被代理擋（CONNECT 403）；模型頁顯示此快照可能已停用，需確認 |
| Llama-3-70B-Instruct（論文用） | `meta.llama3-70b-instruct-v1:0`（Bedrock）或 HF `meta-llama/Meta-Llama-3-70B-Instruct` | 2023-12（AWS Bedrock 模型卡；Meta／NVIDIA 模型卡同） | 待確認 | **未就緒**：Together、Groq、OpenRouter、HF router 都被擋；Bedrock 端點可連，但需使用者確認可用的帳號 |
| Claude Opus 5.5 | `claude-opus-5-5` | 2026-06（官方文件，使用者已確認） | 本 session 的 subagent（與第八、九輪相同） | 可用 |
| Claude Opus 4.8（選擇性） | `claude-opus-4-8` | 2026-01（官方文件，使用者已確認） | 需要 Anthropic API 金鑰 | 未就緒 |

- 樣本的 AAER 大多在 2005–2015 年發布，**四個模型的訓練截止都晚於此**，所以四個模型都**有可能**記得結果。R4 比的是記得多少，不是記不記得。
- API 模型：溫度 0、單次執行。另取 20 筆以溫度 0.7 跑 5 次，與論文的設定對照，作為敏感度分析。subagent 無法設定溫度，報告時註明。
- **主模型**：假設 R1–R3、R5 以 `gpt-4-turbo-2024-04-09` 為主要判定。若該模型確定無法使用，改以 `claude-opus-5-5` 判定，並在 §10 記錄；R4 則改成比較其他可用模型，若只剩一個模型，R4 判為「無法檢驗」。
- 所有原始輸出（含 API 回應的 metadata 與 token 用量）存成 JSON：`data/round10/raw_outputs/<model>/<group>/<id>.json`。

**subagent 規則（Opus 5.5）**：
- 同時最多 20 個；每個 agent 只讀指派給它的輸入檔
- A、B 組每個 agent 處理 5 筆；C 組每個 agent 處理 25 筆
- 分批用固定種子隨機排序；**同一個 agent 不會同時拿到同一筆的 A 版與 B 版**
- 舞弊與非舞弊混在同一批，不告訴 agent 盛行率

## 6. 成本控制
1. 先用 M 裡的 20 筆（4 件舞弊 + 16 件非舞弊，同一種子）在每個可用模型上跑 A、B、C，D 組跑 5 筆
2. 實測 token 數，換算各組 × 各模型的全量成本（API 依官方價格；能用 Batch API 就用）
3. **使用者同意預算後才全量執行**。試跑的 20 筆計入最終樣本（全量時不重跑），試跑結果在全量完成前不計算 AUC

## 7. 預先登錄的假設與判讀標準（提交後不可改）
所有 CI 都是 bootstrap 95%，2,000 次，種子 0。「配對差」的意思是：在同一批公司年度上，以重抽「公司年度」的方式，對兩組的 AUC 差算 bootstrap CI（舞弊與非舞弊分層重抽）。

| 代號 | 假設 | 判為「成立」的標準 | 樣本 |
|---|---|---|---|
| **R0**（復刻） | A 組能重現論文的約 0.68 | gpt-4-turbo 的 A 組 AUC 95% CI 包含 0.681 | M |
| **R1** | 只給名稱也有區分力（記憶存在） | C 組 AUC 的 CI 下界 > 0.5 | M |
| **R2** | 認出公司會提高 AUC | AUC(A) − AUC(B) 的配對 CI 下界 > 0 | M |
| **R3** | A − B 集中在知名公司 | (a) 知名組 A − B 的 CI 下界 > 0；(b) 冷門組 A − B 的 CI 包含 0；(c) 兩組差距相減（知名 − 冷門）的 CI 下界 > 0。三項都成立才算成立；(a)(c) 成立、(b) 不成立記為「部分成立」 | M，分層見 §8.2 |
| **R4** | 新模型記得更多 | AUC_C(claude-opus-5-5) − AUC_C(gpt-4-turbo) 的配對 CI 下界 > 0；同時報告「知道後來出事」的舞弊比例差（McNemar 檢定，p < 0.05） | M |
| **R5** | 時間外樣本沒有記憶 | 第九輪 27 對上 AUC(A) − AUC(B) 的配對 CI 包含 0，且點估計絕對值 ≤ 0.05；同時 C 組自述知道結果 ≤ 1/27 | round9 pairs |

- 每個假設都對每個可用模型各判一次；「主判定」依 §5 的主模型
- R3 的知名度以 C 組在同一個模型的探針為準（§8.2）。知名組的舞弊少於 10 件時，R3 判為「無法檢驗」
- R5 只能以 Opus 5.5 判定，因為對舊模型而言，2026 年的樣本必然在截止日之後，而且 R5 檢驗的是方法本身

## 8. 分析（全部由 `experiment/edgar_risk/round10.py evaluate` 產生 `evaluation.md`）

### 8.1 主表
每組 × 每模型報告：
- AUC（`round3.auc`、`auc_ci`）
- PR-AUC（average precision）與 Precision@1%：以抽樣權重還原到母體盛行率（非舞弊權重 = 母體合格非舞弊數 ÷ 抽中數），讓結果可以和論文直接比較；未加權版另列

### 8.2 知名度分層
- **主定義**：知名 = 同一個模型在 C 組的 `knows_sec_enforcement` 或 `knows_accounting_problems` 為 true。這個定義**只有舞弊公司年度有意義**，所以分層 AUC 的做法是「各層的舞弊 vs 全部非舞弊」
- 為了檢查非舞弊這一側，另報：非舞弊中自述「認得公司」的比例，以及依認得與否分層的平均分數
- **輔助定義**：總資產（`at`）的母體四分位（各 fyear 分開算），分別以舞弊與非舞弊都在同一分位內計算 AUC
- 每一層都報 AUC、A − B、A − C 及配對 CI

### 8.3 公司層級 vs 公司年度層級
- 公司層級標籤：FY1991–2008 任一年 `misstate = 1` 即為舞弊公司
- 在 M ∪ S 上，比較三群的分數：(i) 舞弊年度；(ii) 舞弊公司的非錯報年度；(iii) 其他非舞弊
- 記憶造成誤判的預測：(ii) vs (iii) 的 AUC 在 A、C 組 > 0.5，在 B 組接近 0.5。報告各組的 AUC_(ii vs iii) 與 A − B 的配對 CI（描述性，不列為假設）
- 也報告以公司層級標籤重算的 M 主表

### 8.4 時間外對照（R5）
- 樣本：`results/round9/pairs.json` 的 27 對。用的年報與第九輪相同（Y0 的原始 10-K），MD&A 從 EDGAR 原文用程式切出 Item 7，截斷規則同 §3
- A、B、C 三組完全相同的提示，只用 Opus 5.5。資源許可時，舊模型也跑：舊模型在這批樣本上只能靠公司類型先驗，可當作負對照

### 8.5 不用 LLM 的基準
- Dechow F-score（model 1，用 Bao 項目算）
- 以 14 個比率訓練的 logistic regression，訓練 FY1991–1999（與論文切分一致），在 M 上評估
- D 子樣本：程式直接數紅旗的總數（與第九輪 f 相同）

### 8.6 一致性檢查（描述性）
- 模型自述（recognised／knows_later_problems）與實際表現的一致性：自述知道結果的舞弊 vs 自述不知道的舞弊，A 組分數的差異
- A 組與 C 組分數的 Spearman 相關；控制 B 組分數後，A 與 C 的偏相關（`round9e` 的方法）

## 9. 執行順序
1. 提交本 protocol
2. 建樣本（`round10.py sample`）→ `attrition.tsv`、`sample.json`；寫好提示並提交
3. 試跑 20 筆 → 成本估算 → **等使用者同意**
4. 全量 → `round10.py collect` → `evaluate` → `evaluation.md`
5. `review.md`（中文判讀）、簡報總表、更新 `PROPOSAL.md` 的文獻比較段落

缺 API 金鑰、網域被擋、資料下載不到時，停下來回報，**不使用模擬或編造的結果**。

## 10. 修訂紀錄
- 2026-11-03：初版，於建立樣本、執行任何 LLM 前提交
- 2026-11-03（執行任何 LLM 前；使用者決定）：**主模型改為 Llama-3-70B-Instruct**。理由：OpenAI 停用公告表列出 `gpt-4-turbo-2024-04-09` 已於 2026-10-23 停用（developers.openai.com/api/docs/deprecations；本環境無法連到 OpenAI 即時確認），論文的 GPT-4 zero-shot 基準因此無法以原模型重現。Llama-3-70B-Instruct 是論文使用的另一個模型，權重公開、不會停用，訓練截止 2023-12，與 GPT-4 Turbo 同期。修改內容：
  - §5 的「主模型」改為 Llama-3-70B-Instruct；原「GPT-4 不可用時改以 Opus 5.5 判定」的條款作廢
  - R1、R2、R3、R5 的主判定改以 Llama-3-70B-Instruct 為準（R5 仍依原規定只以 Opus 5.5 判定）；判讀標準不變
  - R4 改為 AUC_C(claude-opus-5-5) − AUC_C(Llama-3-70B-Instruct)，標準不變
  - R0 判為「無法以原模型檢驗」。Llama-3-70B 的 A 組 AUC 與 0.681 並列，只作描述性比較，不稱為復刻成功或失敗（0.681 是 GPT-4 的數字）
  - 推論管道與固定版本 ID 待確認，確認後補記於此
  - 「原基準發表數月內即無法重現」列為一項發現，寫進 review.md 與 PROPOSAL.md
