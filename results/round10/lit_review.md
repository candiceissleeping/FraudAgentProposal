# 文獻探討：LLM 財報舞弊偵測的評估基準與記憶問題

> 日期：2026-11-03。形式：敘事回顧（deep-research `lit-review` 模式），不是系統性回顧，不宣稱涵蓋全部文獻。
> 檢索方式：網路搜尋（2026-11-03）。本環境無法連到 arxiv.org，所以除了 **FraudDebate-Agent 與 AuditFraudBench 兩篇讀過全文**外，其餘只讀到摘要、出版資訊或二手摘要；表中「讀取程度」欄位逐篇標明。數字只引用來源明確寫出的部分。
> AI 使用聲明：本文的檢索、整理與撰寫由 AI 工具（Claude）協助完成，研究者需逐篇核對原文後再引用。

## 1. 要回答的問題
1. 如果要拿一篇研究當 **benchmark**（同一份資料、同一種切分、可比較的 AUC），目前哪些最合適？
2. 現有 LLM 舞弊偵測研究，有沒有處理「模型記得公司與結果」的問題？

## 2. 三類研究，適合程度不同
| 類型 | 做法 | 能當 AUC benchmark 嗎 |
|---|---|---|
| **A. 母體排序型** | 舞弊與正常公司混在一起，模型輸出分數，算 AUC | **可以** |
| **B. 題庫型基準** | 題目多半是已知的舞弊案例，問 LLM 是否、哪一類 | 不行（沒有正常公司、沒有連續分數） |
| **C. 記憶／前視偏誤** | 檢驗 LLM 在金融任務上是否靠記憶 | 不是 benchmark，是本研究的方法論依據 |

## 3. A 類：母體排序型（可當 benchmark）

| 研究 | 資料與樣本 | 模型 | 輸入有無身分 | 切分 vs 模型訓練截止 | 主要結果 | 處理記憶？ | 讀取程度 |
|---|---|---|---|---|---|---|---|
| **Bao, Ke, Li, Yu & Zhang (2020)**, *JAR* 58(1):199–235 | Compustat 28 項原始數字，AAER 標籤，FY1991–2008 | RUSBoost（非 LLM） | 只有數字 | 測試 FY2003–2008（時間外） | AUC **0.725**（RUSBoost）、logit 0.672 | 不適用 | 作者部落格摘要；Walker (2021, *Econ Journal Watch*) 批評連續舞弊跨訓練與測試期，期刊後來刊出勘誤 |
| **Bertomeu, Cheynel, Floyd & Pan (2021)**, *RAST* 26(2):468–519 | 會計＋審計＋市場變數，AAER 等標籤 | 梯度提升樹（非 LLM） | 只有數字 | — | 會計變數本身不強，和審計、市場變數交互作用後變重要；AUC 搜尋結果未顯示 | 不適用 | 只讀到摘要 |
| **Bhattacharya & Mićković (2024)**, *IJAIS* 53:100682 | 10-K MD&A，據後續引用為 1994–2013 | 微調 BERT | MD&A 原文（未提遮蔽） | 未確認 | 同樣檢查家數下，抓到的舞弊是文字基準的 5 倍、數字基準的 3 倍 | 未提及 | 只讀到摘要 |
| **Yue, Yang & Liu (2026) FraudDebate-Agent**, *Mathematics* 14(15):2695 | Bao 資料＋EDGAR-CORPUS MD&A；測試 FY2003–2008，16,180 公司年度、118 件舞弊 | XGBoost、FinBERT、同業距離＋LLM 辯論（Llama-3-70B、gpt-4-turbo-2024-04-09） | 提示詞有 **`[CIK-FY]`**；MD&A **未遮蔽** | 時間外切分只防訓練標籤洩漏；AAER 早於 LLM 截止（2023-12） | 完整方法 **0.806**；三個非 LLM agent 平均 0.770；GPT-4 zero-shot 0.681；XGBoost 0.738 | **未討論** | **全文** |
| **Wang 等 (2026) UMAR**，arXiv 2606.15640 | 10-K，2019–2023，3,200 公司年度；標籤為**重編** | MD&A 文字 agent、比率 agent、CAM agent；Dempster–Shafer 融合 | 未確認 | **樣本年代早於現行 LLM 截止** | AUROC **0.782**、PR-AUC 0.341 | 摘要未提及 | 只讀到摘要 |
| **Benchmarking Generalization in FSFD**，arXiv 2607.19259（2026-07） | 公司層級資料：財報＋摘要化的 MD&A（10-Q）＋舞弊標籤 | LLM 提示框架；約 249 件 AAER 經專家逐件檢視 | 未確認 | 提出新任務 CI-FSFD：測試「沒看過的公司」，批評隨機切分過度樂觀 | 摘要稱其方法在 CI-FSFD 最佳 | 摘要未提及記憶 | 只讀到摘要 |
| **Amin & Aßenmacher (2025)**，FinNLP 2025（ACL Anthology 2025.finnlp-2.10） | 10-K MD&A 的新開放資料集（Zenodo） | 數種 ML／DL 分類器作基準 | MD&A 原文 | 未確認 | 未讀到數字 | 未確認 | 只讀到摘要 |
| **EDINET-Bench**（Sugiura 等，ICLR 2026；arXiv 2506.08762） | 日本 EDINET 十年年報；包含舞弊偵測任務 | 前沿 LLM zero-shot | 未確認 | 未確認 | 舞弊偵測與盈餘預測的二元分類**只比 logistic regression 好一點** | 搜尋結果未提及 | 只讀到摘要 |

**部分查證、未收入表格**：
- 「Improving Financial Statement Fraud Detection: A Large Language Model Processing Approach」（ACM，doi 10.1145/3796514）：一次搜尋顯示 99,155 份 MD&A、10,814 家公司、1995–2019、AAER 標籤，另一次搜尋查不到同名條目，需人工確認。
- FSFDLLM（ResearchGate）：只有標題與一句描述。

## 4. B 類：題庫型基準（不適合當 AUC benchmark）
| 研究 | 內容 | 為什麼不適合 | 讀取程度 |
|---|---|---|---|
| **AuditFraudBench**（Liu 等，arXiv 2606.08345，2026-06） | 84 件 AAER；三個任務：獲利來源歸因（34 題）、誤導敘述（294 題）、舞弊類型（295 題）；8 個 LLM 單次提示、溫度 0 | 標籤全部為舞弊或誤導，沒有正常公司；輸出是是／否與類別，沒有分數。提示詞含公司名稱（附錄 C），全文未討論記憶 | **全文** |
| **AuditBench／Automating Financial Statement Audits**（Wang, Liu, Zhao, Li & Zhang，2025；AAAI 2025 workshop；Springer CCIS 2533:59–81） | 真實財務表格＋合成交易，植入錯誤 | 錯誤是人為植入，不是真實舞弊 | 只讀到摘要 |
| **FinVerBench**（arXiv 2605.29586，2026） | 原生 XBRL 的財報驗證；討論基準效度與校準 | 驗證任務，非舞弊排序 | 只讀到摘要 |
| **VERA-8B**（Liu & Chen，arXiv 2608.28402，2026-08） | SFT＋GRPO 訓練的審計風險推理模型；證據不足時棄權 | 作者明說執法結果不能直接當申報層級的標籤 | 只讀到摘要 |

## 5. C 類：記憶與前視偏誤（本研究的方法論依據）
| 研究 | 發現 | 與本研究的關係 | 讀取程度 |
|---|---|---|---|
| **Glasserman & Lin (2023/2024)**，*Journal of Financial Data Science*；arXiv 2309.17322 | GPT 新聞情緒預測報酬有前視偏誤，也有「分心效應」（知道公司是誰反而干擾）；提出匿名化程序；時間內匿名版表現反而較好 | 最早系統檢驗金融 LLM 前視偏誤；匿名化的先例 | 只讀到摘要 |
| **Lopez-Lira, Tang & Zhu (2025)**，"The Memorization Problem"，SSRN 5217505；arXiv 2504.14765 | LLM 能精確背出訓練截止前的經濟數值，截止後就背不出；**遮蔽保護力弱：模型能從很少的線索重建出原本的實體，連複雜的財務文件也是** | **直接支持本輪試跑**（B 組遮蔽後 16/20 被認出）與「時間外樣本才是根本解法」 | 只讀到摘要 |
| **Kim, Muhn & Nikolaev (2024)**，"Financial Statement Analysis with LLMs"（Chicago Booth 工作論文；arXiv 版已撤回） | GPT-4 讀**匿名化**財報（去名稱、年份改相對年）預測盈餘方向，與專用 ANN 相當；並檢驗 GPT-4 從匿名財報猜出公司或年度的能力「可忽略」；2022–2023 屬模型訓練截止後 | **方法學最接近本研究**：匿名化＋辨識檢驗＋時間外，但用於盈餘預測、只給數字 | 只讀到二手摘要 |
| **He, Lv, Manela & Wu (2025)** ChronoBERT／ChronoGPT，arXiv 2502.21206 | 只用各時點以前的文本訓練；新聞預測報酬的 Sharpe 與一般模型相當，推論前視偏誤不大 | 另一條解法：時點一致的模型 | 只讀到摘要 |
| **Kelly, Malamud, Schwab & Xu (2026)**，"Scaling Point-in-Time Language Models"，NBER w35247；arXiv 2607.11889 | 最大 40 億參數、1 兆 token，2013–2024 逐年 checkpoint | 時點一致模型的規模化；可作未來替代 | 只讀到摘要 |
| MemGuard-Alpha（arXiv 2603.26797） | 偵測並過濾記憶造成的前視偏誤 | 相關工具 | 只讀到摘要 |

**未查證、不收入**：Sarkar & Vafa「Lookahead bias in pretrained language models」——兩次搜尋都找不到原文，依規則不引用。

## 6. 綜合判讀

### 6.1 哪些適合當 benchmark
1. **Bao et al. (2020) 的資料與切分是事實上的標準**：公開、時間外（FY2003–2008）、有基準 AUC（RUSBoost 0.725）。FraudDebate-Agent 也直接沿用。要注意 Walker (2021) 指出的連續舞弊問題與期刊勘誤。
2. **FraudDebate-Agent 是同一份資料上唯一有 LLM 結果的研究**（0.681 至 0.806），但模型已停用、zero-shot 提示詞未公布，只能並列比較。
3. **文字基準**：Bhattacharya & Mićković (2024)（BERT＋MD&A）是期刊等級的代表。FraudDebate-Agent 的 FinBERT（0.703）可作同資料上的參照。
4. **新的時間外或跨公司評估**：Benchmarking Generalization（CI-FSFD）主張評估「沒看過的公司」，方向與本研究一致，但它防的是訓練洩漏，不是 LLM 記憶。
5. **不適合**：AuditFraudBench、AuditBench、FinVerBench、VERA-8B。它們測的是理解、驗證或推理，不是在母體中排序舞弊。

### 6.2 一致的發現
- **LLM 單獨使用並不強**：GPT-4 zero-shot 0.681，低於 XGBoost 0.738（FraudDebate-Agent）；EDINET-Bench 只比 logistic regression 好一點；AuditFraudBench 中，模型大小與推理版都不保證更好。
- **LLM 的增量集中在整合階段**：FraudDebate-Agent 的辯論只帶來約 +0.027 至 +0.036。

### 6.3 研究空缺（本研究的定位）
- **以 AAER 為標籤的 LLM 舞弊研究，沒有一篇檢驗記憶**：FraudDebate-Agent 與 AuditFraudBench 全文都沒有討論，而且輸入都含公司身分；其餘研究在摘要層級也未提及。
- **記憶文獻已經警告「遮蔽不夠」**（Lopez-Lira 等），**匿名化加辨識檢驗**的做法也已在盈餘預測中示範（Kim 等），但還沒有人用到舞弊偵測。
- **本研究的貢獻**：
  1. 在同一份標準資料（Bao＋EDGAR-CORPUS）上，把 LLM 分數分解成「記憶」與「推理」（第十輪 A、B、C、D 組）
  2. 提出「引文驗證事實卡＋粗化＋辨識探針＋時間外」的記憶安全評估流程（第八至九輪）

## 7. 限制
- 除兩篇外只讀到摘要，表中「未確認」的欄位需看原文。
- 以英文網路搜尋為主，可能漏掉會計期刊尚未上網的版本，以及中文文獻。
- 2026 年的 arXiv 論文多數尚未經同儕審查。

## 參考來源（網址）
- Bao et al. (2020) 摘要：https://clsbluesky.law.columbia.edu/2020/06/05/introducing-machine-learning-to-corporate-fraud-detection/
- Walker (2021) 批評：https://econjwatch.org/File+download/1185/WalkerMar2021.pdf
- Bertomeu et al. (2021)：https://ideas.repec.org/a/spr/reaccs/v26y2021i2d10.1007_s11142-020-09563-8.html
- Bhattacharya & Mićković (2024)：https://dare.uva.nl/id/fa67c5ec-5058-40d2-924e-1470ead21eaa
- FraudDebate-Agent：https://doi.org/10.3390/math14152695
- UMAR：https://arxiv.org/pdf/2606.15640
- Benchmarking Generalization in FSFD：https://arxiv.org/abs/2607.19259
- Amin & Aßenmacher (2025)：https://aclanthology.org/2025.finnlp-2.10
- EDINET-Bench：https://mlanthology.org/iclr/2026/sugiura2026iclr-edinetbench/
- ACM 10.1145/3796514：https://dl.acm.org/doi/10.1145/3796514
- AuditFraudBench：https://arxiv.org/pdf/2606.08345
- AuditBench：https://openreview.net/pdf?id=4MaWVsVb2g
- FinVerBench：https://arxiv.org/pdf/2605.29586
- VERA-8B：https://arxiv.org/pdf/2608.28402
- Glasserman & Lin：https://arxiv.org/pdf/2309.17322
- Lopez-Lira, Tang & Zhu：https://papers.ssrn.com/abstract=5217505
- Kim, Muhn & Nikolaev：https://www.chicagobooth.edu/research/fama-miller/finance-research/funding/a-demand-system-approach-for-fixed-income/financial-statement-analysis-with-large-language-models
- ChronoBERT／ChronoGPT：https://arxiv.org/pdf/2502.21206
- Scaling Point-in-Time LMs：https://www.nber.org/papers/w35247
- MemGuard-Alpha：https://arxiv.org/pdf/2603.26797
- Zavitsanos et al.（AAER 標籤的現實評估）：https://arxiv.org/pdf/2305.17457
