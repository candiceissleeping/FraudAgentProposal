# 主題 4 書目：LLM 自述知識的可靠度——模型說「我知道」時，真的知道嗎？

> 角色：ARS deep-research `bibliography_agent`（只做 Phase 2：檢索、篩選、註解書目）。本檔不做綜整、不寫正文；綜整留給 Phase 3。
> 規範：`results/lit_review/protocol.md`（整合性回顧，每主題 10–20 篇）。
> 研究問題（`results/research_topics.md` 主題 4）：LLM 對「這家公司後來出事」的自述有多準？錯在哪裡：捏造、時間錯置，還是細節記錯？不同模型差多少？自述探針能否當記憶污染的偵測工具？
> 閱讀範圍：**全部 20 篇只讀到摘要或出版資訊（`abstract_only`）**；部分條目另有 WebSearch 摘述。因此「方法弱點」一律寫 `not assessed (read scope: abstract_only)`。
> AI 使用聲明：檢索、查核與整理由 AI 工具（Claude）協助完成；引用前請研究者核對原文。

## Annotated Bibliography

### Search Strategy

PRE-SCREENED FROM USER CORPUS:
- Adapter: <unspecified>（來源為 dreamy-volta 第十輪文獻回顧的參考文獻清單，`phase2_bibliography/dreamy_round10_lit_review.md`，不是 Material Passport；依任務指示視為已預篩語料）
  Adapter origin not declared; user-written adapter should populate obtained_via per v3.6.4 schema recommendation.
- Snapshot date: 2026-11-03（該回顧 v3 的日期；條目本身未標 obtained_at）
- Total entries scanned: 29（參考文獻清單的 29 行；Walker/Gow/Klein 與 4 個題庫型研究各合併為一行）
- Pre-screening result:
  - Included: 1 entry
    citation_keys:
      - gao2025detecting（Gao, Jiang & Yan，LAP：以「只給日期的回想查詢」估計模型是否記得結果）
  - Excluded by inclusion / exclusion criteria: 28 entries
    主要原因：屬於主題 1、3、5（舞弊 benchmark、會計經典模型、匿名化與再識別、時點一致模型），不直接回應「自述知識是否可靠」。其中與本主題最接近、但歸入他題的：
      - lopezlira2025memorization：重點是遮蔽後的再識別與截止後樣本效度，歸主題 1／3
      - sugiura2026edinet：公司名探針只是 benchmark 的附帶檢驗，歸主題 1／5
      - sarkar2024lookahead、levy2026caution、glasserman2024：前視偏誤對預測的影響，歸主題 1
      - kim2024（已撤回）：不可引用
- Note: presence in corpus does not imply inclusion; same criteria applied to corpus and external sources.

**Search-fills-gap 判定**：case A。dreamy 語料只覆蓋子題「以回想探針偵測記憶」中的 1 篇；校準與自我知識、事實性幻覺、知識探測與長尾、時間知識、對照權威紀錄的查核、污染偵測的效度等子題都未覆蓋，因此對這些子題做外部檢索。

**Databases**：
- arXiv API（`export.arxiv.org/api/query`）：關鍵字檢索＋ID 查核
- Crossref API（`api.crossref.org/works`）：書目檢索＋DOI 查核
- WebSearch（mode: standard，未用 extended）：找出版處、確認會議收錄
- 未使用：OpenAlex、Semantic Scholar（無 API 金鑰）。因此 ARS Step 4.5 的 S2 去重與 `semantic_scholar_unmatched` 訊號依降級規則略過，去重改以題名比對。

**Keywords**（主詞＋同義詞）：
- 校準與自我知識：know what they know、self-knowledge、unanswerable、verbalized confidence、calibration、abstention、overconfidence
- 事實性與幻覺：hallucination、factuality、short-form factuality、confabulation、entity popularity
- 知識探測：knowledge probing、language models as knowledge bases、long-tail knowledge、popularity
- 時間：temporal、time-sensitive、knowledge cutoff、effective cutoff
- 記憶與污染：data contamination、guided instruction、membership inference、distribution shift、lookahead bias
- 領域：financial、companies、hallucination

**實際檢索式（arXiv，`search_query=`，sortBy=relevance）**：

| # | 檢索式 | 總筆數 | 取回 |
|---|---|---|---|
| 1 | `abs:"know what they know" AND abs:"language models"` | 10 | 10 |
| 2 | `ti:calibration AND ti:"large language models" AND abs:verbalized` | 10 | 10 |
| 3 | `abs:"knowledge cutoff" AND abs:"language models"` | 61 | 15 |
| 4 | `abs:"long-tail knowledge" AND abs:"language models"` | 38 | 12 |
| 5 | `abs:temporal AND abs:"time-sensitive" AND abs:"language models" AND abs:facts` | 14 | 12 |
| 6 | `abs:"data contamination" AND abs:"guided instruction"` | 1 | 1 |
| 7 | `abs:"membership inference" AND abs:"large language models" AND abs:"distribution shift"` | 11 | 10 |
| 8 | `ti:abstention AND abs:"language models" AND ti:survey` | 1 | 1 |
| 9 | `abs:hallucination AND abs:entities AND abs:popularity AND abs:"language models"` | 13 | 12 |
| 10 | `ti:"knowledge bases" AND ti:"language models" AND abs:probing` | 7 | 7 |
| 11 | `abs:"self-knowledge" AND abs:"large language models" AND abs:unanswerable` | 1 | 1 |
| 12 | `abs:hallucination AND abs:financial AND abs:"large language models" AND abs:factual` | 17 | 12 |
| 13 | `abs:"verbalized confidence" AND abs:"factual" AND abs:entities` | 0 | 0 |
| 14 | `ti:"Deficiency of Large Language Models in Finance"` | 1 | 1 |
| 15 | `abs:"knowledge cutoff" AND abs:companies` | 2 | 2 |
| | 合計 | 187 | 106 |

**Crossref 書目檢索（`query.bibliographic=`，rows 3–4）**：11 次，查找以下題名的正式出版版本——hallucination survey（Huang 等）、Head-to-Tail、Know Your Limits（abstention survey）、Don't Hallucinate, Abstain、Time Awareness in LLMs（2 次，未找到）、Popular but Wrong、Data Contamination Quiz、Does Data Contamination Detection Work (Well)（第 1 次解析失敗，重試成功）、LLMLagBench（未找到）、Can Prompts Rewind Time（解析失敗）。約取回 30 筆。

**Crossref DOI 查核（`/works/{DOI}`）**：17 次，全部題名相符（見各條目）。
**arXiv ID 查核（`id_list=`）**：29 個不同 ID，全部題名相符。

**WebSearch（standard，9 次）**：
1. `LLM self-reported knowledge of events misdating temporal errors hallucination knowledge cutoff awareness`
2. `"Large Language Models Struggle to Learn Long-Tail Knowledge" Kandpal ICML 2023 PMLR`
3. `LLM memorization probe self-report validity "data contamination" detection quiz Golchin Surdeanu TACL`
4. `"Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs" ICLR 2024 openreview`
5. `"Time Travel in LLMs: Tracing Data Contamination in Large Language Models" ICLR 2024 openreview`
6. `"Do Membership Inference Attacks Work on Large Language Models?" COLM 2024 Duan`
7. `"Dated Data: Tracing Knowledge Cutoffs in Large Language Models" COLM 2024`
8. `"Beyond the Reported Cutoff: Where Large Language Models Fall Short on Financial Knowledge" Shah Chava conference`
9. `"Detecting Lookahead Bias in LLM Forecasts" Gao Jiang Yan`

**已知條目（known-item）**：子題的奠基文獻（如 Petroni 2019、Kadavath 2022、FActScore、PopQA、semantic entropy）先依領域知識列出候選，再逐一以 arXiv ID 或 Crossref DOI 查核存在與題名；沒有查到的一律不列。

**Boolean**：子題內同義詞以 OR、子題概念與「language models」以 AND 組合（arXiv 的 `abs:`／`ti:` 欄位）；未使用 NOT。
**Date Range**：2020 年以後為主；奠基文獻不限年份（本書目只有 Petroni 2019 一篇早於 2020，標為 seminal）。
**Last Searched**：2026-11-09
**Language**：英文（未找到可用的中文文獻）。

**Inclusion Criteria**（依 protocol）：
- 直接回應主題 4 的研究問題：模型的自述或自評信心是否可靠、事實錯誤的類型與成因、知識覆蓋與實體知名度／時間的關係、以自述或回想探針偵測記憶與污染及其效度、以權威資料查核模型陳述
- Tier 1 期刊或會議論文；Tier 2 預印本（標示）；Tier 3 官方或技術文件每主題至多 2 篇（本書目 0 篇）
- 有 DOI、arXiv ID 或穩定網址，題名、作者、年份可核對

**Exclusion Criteria**：
- 只順帶提到自述或校準（例如以校準為工具的 RAG、多模態、推理任務）
- 需要模型內部 logits 或權重、且無黑箱版本的方法（本研究只用閉源 API 的文字輸出），除非用來說明效度問題
- 部落格、新聞、行銷文章；查不到存在證據者（灰色地帶＝剔除）
- 與他主題重複且他主題更適合者（歸給他主題）
- 超過 20 篇上限時，與已收錄條目功能重疊者

**Coverage Distribution Advisory**：

DISTRIBUTIONAL_SKEW_ADVISORY:
- Dimension: methodological distribution
- Concentration: computational/benchmark empirical study = 17/20 (85%)（其餘：narrative／systematic review 2、theoretical 1）
- Advisory: This is a coverage-distribution signal, not a defect. Consider whether the RQ warrants broader periods, sites, methods, or venue families.
- Search response: 本主題本質上是 NLP 的實證問題，計算實驗佔多數合理；若 Phase 3 需要「人類專家查核 LLM 陳述」或質性錯誤分析的對照，可補檢 `abs:"error analysis" AND abs:hallucination AND abs:annotation`，或會計／法律領域的人工查核研究。

其他維度：
- 時間分布：2019 1／2022 2／2023 4／2024 7／2025 5／2026 1（以正式出版年計），單一年份最多 7/20（35%），未觸發。
- venue 分布：ACL 系列（ACL、EMNLP、NAACL、Findings、TACL）8/20（40%）；ICLR／ICML／COLM 6/20；期刊（Nature、ACM TOIS）2/20；只有預印本 4/20（20%）。未觸發。同儕審查比例 16/20（80%）。
- 地理分布：多數條目沒有可判定的研究地區或樣本國別（資料多為英文維基百科或網路語料），已知值太少，不評估。另註：**財務或公司領域只有 2/20**（Shah 等 2025、Gao 等 2025），這是主題內容的覆蓋限制，不是分布門檻訊號。

### PRISMA Flow

```
Records identified (total): 約 255（含重複）
|-- arXiv 關鍵字檢索：106（15 個檢索式，總筆數 187）
|-- Crossref 書目檢索：約 30（11 次）
|-- WebSearch：9 次，約 90 個連結（多為同一論文的不同頁面）
+-- Other sources：dreamy 語料 29 行
（另：known-item 查核 arXiv 29 個 ID、Crossref 17 個 DOI，用於確認存在與書目，不另計為新紀錄）

Duplicates removed: 約 105（同一論文的 arXiv／會議／網頁版本，以題名比對；無 S2 去重）
Records screened (title/metadata): 約 150
Records excluded at title/metadata: 約 128
Abstract-level assessed: 22（20 篇以 arXiv 或 Crossref 讀取摘要；2 篇只有 WebSearch 摘述）
Excluded at abstract level (with reasons): 2
  - Golchin & Surdeanu (2025) Data Contamination Quiz, TACL（DOI 10.1162/tacl.a.20 已查核）：與同作者 Time Travel (2024) 功能重疊；20 篇上限內優先收錄較早、以「生成補全」為核心的版本。可作備選。
  - Pęzik 等 (2025) LLMLagBench, arXiv 2511.12116（ID 已查核）：預印本，只讀到 WebSearch 二手摘述（模型自述截止日與實際知識邊界不符）；未讀摘要原文，依灰色地帶規則不收。可作備選。
Full-text articles assessed: 0（本輪未讀全文）
Studies included in review: 20
```

**標題／中繼資料階段排除的近似條目（擇要，供 Phase 3 參考）**：
- Tian 等 (2023) Just Ask for Calibration, EMNLP（DOI 10.18653/v1/2023.emnlp-main.330 已查核）：與 Xiong 等重疊
- Wen 等 (2025) Know Your Limits: abstention survey, TACL（DOI 10.1162/tacl_a_00754 已查核）：與 Yin 等、Kadavath 等重疊，因 20 篇上限排除；Phase 3 若需要 abstention 的分類框架可補入
- Feng 等 (2024) Don't Hallucinate, Abstain, ACL（DOI 10.18653/v1/2024.acl-long.786 已查核）：多模型協作的 abstention 方法，偏方法改進
- Manakul 等 (2023) SelfCheckGPT, EMNLP（DOI 已查核）：與 Farquhar 等（一致性型偵測）重疊
- Lin, Hilton & Evans (2022) TruthfulQA, ACL（DOI 已查核）：測的是常見誤解，不是實體事件知識
- Lin, Hilton & Evans (2022) Teaching Models to Express Their Uncertainty in Words（arXiv 2205.14334 已查核）：出版處未查核
- Herel 等 (2024) Time Awareness in LLMs（arXiv 2409.13338 已查核）：預印本，出版處未查到；只讀到題名
- Gao, X. 等 (2025) Can Prompts Rewind Time（arXiv 2510.02340）：屬「以提示模擬截止日」，歸主題 1／2
- Kang & Liu (2023) Deficiency of LLMs in Finance（arXiv 2311.15548）：與 Shah 等 (2025) 重疊且較舊
- Duan 等的延伸：Das, Zhang & Tramèr (2024) Blind Baselines（arXiv 2406.16201 已查核）、Maini 等 (2024) LLM Dataset Inference（arXiv 2406.06443）：與 Duan 等、Fu 等功能重疊
- Shi 等 (2024) Min-K% Prob（arXiv 2310.16789 已查核）：需要 token 機率，閉源 API 不適用
- Pal 等 (2025) Knowing What You Know Is Not Enough（arXiv 2511.13240）：信心與行動的一致性，偏 agent 決策

### Sources (N = 20)

**證據等級對照說明**：ARS 的 I–VII 等級是為臨床與社會科學設計。本書目依 `references/source_quality_hierarchy.md` 的定義做如下對應，Phase 3 引用時請保留此說明：
- **III**（有對照的非隨機研究）：有操控條件或對照組的計算實驗（例如控制訓練資料、比較有無檢索、截止前後對照）
- **V**（描述性研究的回顧）：回顧或綜述（Fu 等為有明確檢索的回顧；Huang 等為敘事綜述，嚴格說低於 V）
- **VI**（單一描述性研究）：以 benchmark 描述多個模型表現、沒有操控變因者
- **VII**（專家意見／理論論證）：理論或立場論文

**Tier**：1＝同儕審查期刊或會議；2＝預印本；3＝官方或技術文件。

---

#### 子題 A：校準與自我知識——模型對「自己知不知道」的判斷

1. **Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., Hatfield-Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston, S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman, S., Fort, S., . . . Kaplan, J. (2022). *Language models (mostly) know what they know* (arXiv:2207.05221). arXiv. https://doi.org/10.48550/arXiv.2207.05221**
   - 識別碼：arXiv 2207.05221（ID 查核題名相符；36 位作者）
   - Relevance：本主題的核心前例：模型能否預測自己答不答得出來（P(IK)，「I know」的機率）、能否評估自己答案為真的機率（P(True)）。直接對應「模型說『我知道』時是否真的知道」。
   - Key Findings：（摘要）大型模型在適當格式下，對選擇題與是非題校準良好；P(True) 的表現、校準與規模化趨勢都不錯，讓模型先看多個自己的樣本再評估會更好；P(IK) 可以訓練且部分跨任務泛化，但在新任務上的校準較差。
   - Methodology：在同一模型家族、不同規模上做自評實驗；P(IK) 以監督式訓練取得。
   - Quality：Level III（有規模與條件對照的計算實驗）；Tier 2（預印本，未見正式出版）
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：實驗 D 的「說知道」相當於口頭版的 P(IK)；摘要指出 P(IK) 在新任務上校準變差，可用來解讀 Sonnet 在時間外樣本 33 則中 32 則「說知道」卻無紀錄支持的現象（跨分布時自評失準）。注意本文的 P(IK) 是機率輸出，與本研究的自然語言自述不同。

2. **Yin, Z., Sun, Q., Guo, Q., Wu, J., Qiu, X., & Huang, X. (2023). Do large language models know what they don't know? In *Findings of the Association for Computational Linguistics: ACL 2023* (pp. 8653–8665). Association for Computational Linguistics. https://doi.org/10.18653/v1/2023.findings-acl.551**
   - 識別碼：DOI 10.18653/v1/2023.findings-acl.551（Crossref 相符）；arXiv 2305.18153
   - Relevance：以「能否辨認無法回答的問題」衡量自我知識，對應「沒有紀錄的公司，模型是否會說不知道」。
   - Key Findings：（摘要）提出 SelfAware 資料集（五類無法回答的問題與可回答的對照）與自動偵測回答中不確定性的方法；20 個 LLM 有一定的自我知識，in-context learning 與 instruction tuning 能提升，但與人類辨認知識邊界的能力仍有明顯差距。
   - Methodology：建構對照資料集，跨 20 個模型的 benchmark 比較。
   - Quality：Level VI（描述性 benchmark；含方法比較）；Tier 1
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：本研究的時間外公司可視為「對模型而言不可知」的問題（結果發生在截止後）；Yin 等的「可回答 vs 無法回答」配對設計，對應本研究「問題公司 vs 時間外公司」的對照。

3. **Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2024). Can LLMs express their uncertainty? An empirical evaluation of confidence elicitation in LLMs. In *The Twelfth International Conference on Learning Representations (ICLR 2024)*. https://iclr.cc/virtual/2024/poster/18135**
   - 識別碼：arXiv 2306.13063（ID 查核相符；arXiv 註記「accepted by ICLR 2024」；WebSearch 見 ICLR 2024 海報頁）
   - Relevance：黑箱（只看文字輸出）情境下口頭信心的可靠度，與本研究只能用閉源 API 文字輸出的條件相同。
   - Key Findings：（摘要）LLM 口頭表達信心時傾向過度自信；模型能力越強，校準與失誤預測越好；人類啟發式提示、多次回答的一致性與較好的彙整方法可減輕過度自信；白箱方法較好但差距小（AUROC 0.522 vs 0.605）；需要專業知識的任務上所有方法都表現不佳。
   - Methodology：提示策略 × 抽樣 × 彙整的框架，5 類資料集、5 個模型（含 GPT-4、LLaMA 2 Chat）。
   - Quality：Level III（多種方法在相同資料上的對照比較）；Tier 1
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：「越強的模型校準越好」與實驗 D 的 Opus 97% > Sonnet 86% > Haiku 83% 方向一致，但 Sonnet 的過度自述不符單調趨勢，值得在 Phase 3 討論；「專業知識任務表現差」對應 SEC 執法這類專業事件。

4. **Wei, J., Karina, N., Chung, H. W., Jiao, Y. J., Papay, S., Glaese, A., Schulman, J., & Fedus, W. (2024). *Measuring short-form factuality in large language models* (arXiv:2411.04368). arXiv. https://doi.org/10.48550/arXiv.2411.04368**
   - 識別碼：arXiv 2411.04368（ID 查核相符）
   - Relevance：SimpleQA 把答案分為「正確／錯誤／未作答」，明確把「是否知道自己知道」當成評估目標；評分方式可直接借用於本研究的自述查核。
   - Key Findings：（摘要）題目以 GPT-4 對抗式蒐集、每題只有單一無爭議答案；理想模型應盡量答對，並對沒有把握的題目不作答；作者定位為檢驗模型是否「know what they know」的簡單評估。
   - Methodology：benchmark 建構（短答事實題）。
   - Quality：Level VI（benchmark／資料集論文）；Tier 2（預印本；作者為 OpenAI，arXiv 註記附部落格）
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：本研究 254 則自述可依「相符／不符／說不知道」三分，對應 SimpleQA 的三類評分；「單一無爭議答案」的要求提醒：SEC 紀錄中「重編 vs 處分」的界線（如 Evoqua）需要事先定義判定規則。

5. **Ni, S., Bi, K., Guo, J., & Cheng, X. (2026). Popular but wrong: Understanding and mitigating LLM overconfidence through knowledge popularity. In *Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing* (pp. 28085–28101). Association for Computational Linguistics. https://doi.org/10.18653/2026.emnlp-main.1231**
   - 識別碼：DOI 10.18653/2026.emnlp-main.1231（Crossref `/works` 查核題名、作者、頁碼相符；此 DOI 字串沒有一般 ACL DOI 的 `v1/`，照 Crossref 回傳原樣記錄）；arXiv 2505.17537（註記 EMNLP 2026 Main）
   - Relevance：直接處理「錯誤卻高信心」的成因：知名度。對應 Sonnet 對無紀錄公司也常說「知道」。
   - Key Findings：（摘要）以 Wikidata 三元組建構實體事實問答；幻覺答案不是隨機的，傾向比正確答案更知名、或更常與問題實體共同出現；信心與生成答案的知名度強相關，錯誤答案中越知名者信心越高；加入知名度訊號後，錯誤答案的平均信心由 0.765 降到 0.254、整體 ECE 由 0.356 降到 0.050。
   - Methodology：六個模型、三個資料集的實證分析＋校正方法。
   - Quality：Level III（含有無知名度訊號的對照）；Tier 1
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：提供「細節記錯」的一種機制假說：GTT 把「營業成本」記成「營收」、Evoqua 把「SEC 處分」說成「重編」，可能是較常見的舞弊敘事（營收、重編）取代了實際細節；也提示把公司知名度當成自述錯誤的分層變數。

#### 子題 B：事實性幻覺——錯誤的類型與成因

6. **Huang, L., Yu, W., Ma, W., Zhong, W., Feng, Z., Wang, H., Chen, Q., Peng, W., Feng, X., Qin, B., & Liu, T. (2025). A survey on hallucination in large language models: Principles, taxonomy, challenges, and open questions. *ACM Transactions on Information Systems, 43*(2), 1–55. https://doi.org/10.1145/3703155**
   - 識別碼：DOI 10.1145/3703155（Crossref 相符）；arXiv 2311.05232
   - Relevance：提供幻覺的分類架構，可作為本研究錯誤類型（捏造、時間錯置、細節記錯）的對照框架。
   - Key Findings：（摘要）提出 LLM 時代的幻覺分類，整理成因、偵測方法與 benchmark、緩解方法，以及檢索增強的限制；指出「知識邊界」的理解是未來方向。
   - Methodology：敘事綜述。
   - Quality：Level V（綜述；非系統性回顧，嚴格說低於 V）；Tier 1
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：Phase 3 可用其分類為本研究的錯誤編碼表命名，確認「時間錯置」（Welbilt 2016 重編套到 2018）是否已有對應類別，或屬於本研究可補充的細類。

7. **Kalai, A. T., Nachum, O., Vempala, S. S., & Zhang, E. (2025). *Why language models hallucinate* (arXiv:2509.04664). arXiv. https://doi.org/10.48550/arXiv.2509.04664**
   - 識別碼：arXiv 2509.04664（ID 查核相符）
   - Relevance：從訓練與評分機制解釋「不確定時仍猜測」，對應模型對沒有紀錄的公司仍給出「知道」的自述。
   - Key Findings：（摘要）幻覺可視為二元分類的錯誤：若錯誤陳述與事實無法區分，預訓練的統計壓力就會產生幻覺；幻覺持續存在，是因為多數評估的評分方式獎勵猜測、懲罰表達不確定；主張修改主流 benchmark 的評分，而不是再增加幻覺評估。
   - Methodology：理論分析與立場論證。
   - Quality：Level VII（理論論證）；Tier 2（預印本）
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：本研究的自述探針若只問「知不知道」而不給「不知道」的獎勵或選項，可能誘發猜測；提示 Phase 3 檢視探針題目是否提供明確的不知道選項。

8. **Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting hallucinations in large language models using semantic entropy. *Nature, 630*(8017), 625–630. https://doi.org/10.1038/s41586-024-07421-0**
   - 識別碼：DOI 10.1038/s41586-024-07421-0（Crossref 相符，含摘要）
   - Relevance：「捏造」（confabulation：任意且錯誤的生成）的黑箱偵測方法，可用於區分本研究的捏造與穩定的錯誤記憶。
   - Key Findings：（摘要）提出以熵為基礎、在語意層級估計不確定性的方法，用來偵測幻覺中的一個子類：confabulation（任意、錯誤的生成）；方法考慮同一意思可有不同說法，適用於新問題。
   - Methodology：統計方法（多次抽樣、依語意等價分群後計算熵）。
   - Quality：Level III（方法在多資料集上與基準比較）；Tier 1
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：若同一公司重問多次，自述內容不穩定，屬捏造；三個模型都穩定地把 Welbilt 的 2016 重編說成 2018，則是一致的錯誤記憶，semantic entropy 偵測不到。這個區分可直接用在錯誤分類上。

#### 子題 C：知識探測、長尾與實體知名度

9. **Petroni, F., Rocktäschel, T., Riedel, S., Lewis, P., Bakhtin, A., Wu, Y., & Miller, A. (2019). Language models as knowledge bases? In *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP)* (pp. 2463–2473). Association for Computational Linguistics. https://doi.org/10.18653/v1/D19-1250**
   - 識別碼：DOI 10.18653/v1/D19-1250（Crossref 相符；作者順序依 Crossref）；arXiv 1909.01066
   - Relevance：**Seminal**。LAMA 知識探測的起點：以填空問句探測模型記得的關係知識，是本研究「回想探針」的方法源頭。
   - Key Findings：（摘要）未微調的 BERT 所含關係知識，可與有部分 oracle 知識的傳統 NLP 方法競爭；在開放領域問答上也表現不錯；某些類型的事實知識比其他類型容易學到。
   - Methodology：以 cloze 問句探測多個預訓練模型。
   - Quality：Level VI（描述性探測）；Tier 1；seminal（2019，早於 2020，依 protocol 允許）
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：本研究的探針是自然語言問答而非填空，但「知識類型影響可回想程度」對應：公司名稱與事件類型（重編、SEC 處分）可能比事件年份更容易被記住。

10. **Kandpal, N., Deng, H., Roberts, A., Wallace, E., & Raffel, C. (2023). Large language models struggle to learn long-tail knowledge. In *Proceedings of the 40th International Conference on Machine Learning* (Proceedings of Machine Learning Research, Vol. 202, pp. 15696–15707). PMLR. https://proceedings.mlr.press/v202/kandpal23a.html**
   - 識別碼：arXiv 2211.08411（ID 查核相符，註記 ICML 2023 camera ready）；PMLR 頁面經 WebSearch 確認
   - Relevance：事實知識與預訓練語料中相關文件數的關係，解釋小型、少被報導的公司為何較少被記得或記錯。
   - Key Findings：（摘要）模型答對事實題的能力，與預訓練時看過的相關文件數有強相關與因果關係；大模型較能學到長尾知識，但要在支持文件很少的問題上達到競爭水準，需把規模放大好幾個數量級；檢索增強可降低對預訓練資訊的依賴。
   - Methodology：以實體連結計算預訓練語料中的相關文件數；跨語料與模型規模的相關及因果（介入）分析。
   - Quality：Level III（含因果介入的計算實驗）；Tier 1
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：預測自述準確度應隨公司媒體曝光（可代理為相關文件數）上升；也與實驗 C「記得越少的模型 AUC 越低」及模型規模差異（Opus > Sonnet > Haiku）相呼應。

11. **Mallen, A., Asai, A., Zhong, V., Das, R., Khashabi, D., & Hajishirzi, H. (2023). When not to trust language models: Investigating effectiveness of parametric and non-parametric memories. In *Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)* (pp. 9802–9822). Association for Computational Linguistics. https://doi.org/10.18653/v1/2023.acl-long.546**
    - 識別碼：DOI 10.18653/v1/2023.acl-long.546（Crossref 相符）；arXiv 2212.10511
    - Relevance：PopQA：以實體知名度分層的知識探測，說明「何時不該信任模型自身的記憶」。
    - Key Findings：（摘要）10 個模型在 14k 題 PopQA 上，對較不知名的事實知識表現差，且放大規模無法明顯改善長尾記憶；檢索增強的模型大幅勝過大好幾個數量級的模型，但對高知名度實體，未經檢索的模型仍有競爭力。
    - Methodology：大規模知識探測＋4 種增強方法比較。
    - Quality：Level III（有無檢索的對照）；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：支持以知名度分層分析自述準確度；dreamy 第八輪觀察到 AAER 公司比時間外小公司容易被認出，與 PopQA 的知名度效應方向一致。

12. **Sun, K., Xu, Y., Zha, H., Liu, Y., & Dong, X. L. (2024). Head-to-tail: How knowledgeable are large language models (LLMs)? A.K.A. will LLMs replace knowledge graphs? In *Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)* (pp. 311–325). Association for Computational Linguistics. https://doi.org/10.18653/v1/2024.naacl-long.18**
    - 識別碼：DOI 10.18653/v1/2024.naacl-long.18（Crossref 相符）；arXiv 2308.10168
    - Relevance：以 head／torso／tail 分層，並設計「接近模型有信心內化之知識」的評估指標，與本研究「說知道且說得出內容」的判定相近。
    - Key Findings：（摘要）18K 題問答，依知名度分為 head、torso、tail；16 個公開 LLM 對事實知識的掌握仍不完美，torso 到 tail 實體尤其差。
    - Methodology：benchmark 建構＋自動評估方法＋跨模型比較。
    - Quality：Level VI（描述性 benchmark）；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：本研究的樣本多為中小型公司（AAER、4.02），大多落在 torso／tail；可據此預期自述的錯誤率高於大型知名公司，並據以設計分層報告。

#### 子題 D：時間知識與知識截止

13. **Dhingra, B., Cole, J. R., Eisenschlos, J. M., Gillick, D., Eisenstein, J., & Cohen, W. W. (2022). Time-aware language models as temporal knowledge bases. *Transactions of the Association for Computational Linguistics, 10*, 257–273. https://doi.org/10.1162/tacl_a_00459**
    - 識別碼：DOI 10.1162/tacl_a_00459（Crossref 相符）；arXiv 2106.15110
    - Relevance：會隨時間改變的事實如何被模型記住，直接對應「時間錯置」錯誤。
    - Key Findings：（摘要）提出探測隨時間變化之事實知識的診斷資料集；只用特定時段資料訓練、或混合大範圍時段資料訓練的模型，各有問題；把文字與時間戳一起建模，能改善訓練期間事實的記憶，以及對未來時段未見事實的校準。
    - Methodology：診斷資料集＋訓練方法對照實驗。
    - Quality：Level III（有無時間戳的對照訓練）；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：Welbilt 的錯誤（把 2016 年的真實重編套到被問的 2018 年）符合「訓練文字沒有可靠時間標記時，事件與年份綁定鬆散」的機制；也提示探針應同時問「哪一年」，以區分「記得事件」與「記得事件年份」。

14. **Cheng, J., Marone, M., Weller, O., Lawrie, D., Khashabi, D., & Van Durme, B. (2024). Dated data: Tracing knowledge cutoffs in large language models. In *Proceedings of the First Conference on Language Modeling (COLM 2024)*. https://arxiv.org/abs/2403.12958**
    - 識別碼：arXiv 2403.12958（ID 查核相符）；COLM 2024 收錄（WebSearch 見 JHU 新聞「COLM outstanding paper award」與 alphaxiv「Published as a conference paper at COLM 2024」）
    - Relevance：模型的「實際」知識截止日因資源與主題而異，影響「時間外樣本」的界定，以及模型對截止前後事件的自述。
    - Key Findings：（摘要）提出「有效截止日」概念，與開發者公布的截止日不同，且因子資源與主題而異；以跨資料版本的探測估計，發現有效截止日常與公布值不同；原因是 CommonCrawl 新快照含大量舊資料，以及去重時語意重複與詞面近重複的問題。
    - Methodology：以不同版本資源上的困惑度（perplexity）隨時間的最低點估計有效截止日；搭配開放預訓練資料的直接分析。
    - Quality：Level VI（描述性測量，含成因分析）；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：本研究以公布的截止日界定時間外樣本；若財經新聞或 SEC 文件的有效截止日較早或較晚，時間外樣本的「不可能被記得」假設需要以探針實證確認（本研究的辨識與回想探針正有此功能）。方法需 token 機率，閉源 API 無法直接複製。

#### 子題 E：以權威資料查核模型的事實陳述

15. **Min, S., Krishna, K., Lyu, X., Lewis, M., Yih, W., Koh, P. W., Iyyer, M., Zettlemoyer, L., & Hajishirzi, H. (2023). FActScore: Fine-grained atomic evaluation of factual precision in long form text generation. In *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing* (pp. 12076–12100). Association for Computational Linguistics. https://doi.org/10.18653/v1/2023.emnlp-main.741**
    - 識別碼：DOI 10.18653/v1/2023.emnlp-main.741（Crossref 相符）；arXiv 2305.14251
    - Relevance：把生成拆成原子事實、逐一對照可靠知識來源，是本研究「自述對照 SEC 紀錄」的方法範本。
    - Key Findings：（摘要）以人物傳記為題，ChatGPT 的原子事實支持率只有 58%；自動估計器（檢索＋強模型）誤差低於 2%；以此評估 13 個模型 6,500 份生成，GPT-4 與 ChatGPT 比公開模型更符合事實。
    - Methodology：人工標註＋自動評估器，以維基百科為知識來源。
    - Quality：Level VI（評估方法與描述性比較）；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：本研究可把每則自述拆成「有無事件」「事件類型」「年份」「科目」等原子事實，分別對照 SEC 紀錄，使「相符 97%／86%／83%」與「說得出問題類型 86%／69%／40%」成為原子層級的指標；知識來源由維基百科換成 AAER／8-K 4.02，屬權威紀錄。

16. **Shah, A., Ye, L., Jaskowski, S., Xu, W., & Chava, S. (2025). Beyond the reported cutoff: Where large language models fall short on financial knowledge. In *Proceedings of the Second Conference on Language Modeling (COLM 2025)*. https://arxiv.org/abs/2504.00042**
    - 識別碼：arXiv 2504.00042（ID 查核相符；arXiv 註記「Paper accepted at CoLM 2025」，WebSearch 摘述一致）
    - Relevance：與本研究最接近的領域文獻：以美國上市公司的財務資料當 ground truth，查核 LLM 的公司知識，並分析公司特徵。
    - Key Findings：（摘要）超過 19.7 萬題、對照實際財務資料；LLM 對較早期的財務表現所知較少，對大型公司與較近年份較清楚；但同時對大型公司、尤其近年資料，**更容易產生幻覺**；公司規模、散戶投資、機構關注與財報可讀性都和準確度有關。
    - Methodology：大規模問答＋以公司特徵為解釋變數的迴歸式分析。
    - Quality：Level IV（觀察性、以公司特徵解釋差異，類似橫斷面研究）；Tier 1（COLM 2025，依 arXiv 註記）
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：「大型公司較常被認得、也較常幻覺」對應本研究的兩個現象：AAER 知名公司容易被認出，以及 Sonnet 對無紀錄公司過度說「知道」；可作為以公司規模與關注度分層的直接文獻依據。題目是財務數值，不是執法事件，外推時須說明。

#### 子題 F：以自述或回想探針偵測記憶與污染，以及這類探針的效度

17. **Golchin, S., & Surdeanu, M. (2024). Time travel in LLMs: Tracing data contamination in large language models. In *The Twelfth International Conference on Learning Representations (ICLR 2024)*. https://iclr.cc/virtual/2024/poster/19550**
    - 識別碼：arXiv 2308.08493（ID 查核相符；arXiv 註記「Published at ICLR 2024 as a Spotlight paper」）；ICLR 2024 海報頁經 WebSearch 確認
    - Relevance：只靠提示與輸出（黑箱）偵測污染的代表方法：給資料集名稱與開頭，請模型補完。和本研究「問模型是否記得」的探針同屬行為探測。
    - Key Findings：（摘要）以「guided instruction」（資料集名、分割、例句開頭）請模型補完，輸出與原文完全或近乎相同即判為污染；再以與一般指令比較的統計檢定，或 GPT-4 few-shot 分類器，判斷整個分割是否被污染；最佳方法與人類專家判定相比準確率 92%–100%；GPT-4 被 AG News、WNLI、XSum 污染。
    - Methodology：方法提出＋與人工判定比對。
    - Quality：Level III（guided vs general instruction 的對照）；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：其「加入身分線索 vs 不加」的對照邏輯，對應本研究的「給名稱 vs 不給名稱」；但它偵測的是逐字記憶，本研究偵測的是事件知識（記得結果），兩者的效度證據不能直接互換。

18. **Gao, Z., Jiang, W., & Yan, Y. (2025). *Detecting lookahead bias in LLM forecasts* (arXiv:2512.23847). arXiv. https://doi.org/10.48550/arXiv.2512.23847**
    - 識別碼：arXiv 2512.23847（ID 查核相符；v1 題名為 *A Test of Lookahead Bias in LLM Forecasts*，現行 v2 改為上述題名）
    - Relevance：財經領域以「回想查詢」量化模型是否記得結果，並檢驗它能否解釋預測表現；與本研究的「自述探針能否當記憶污染偵測工具」最直接相關。
    - Key Findings：（摘要）以「只給公司與日期」的回想查詢估計模型已內化結果的機率（Lookahead Propensity, LAP）；LAP 在樣本期內為正、訓練截止後幾乎歸零；LAP 與 LLM 預測在準確度迴歸中的正交互作用，表示前視偏誤污染；在新聞標題預測報酬、法說會預測資本支出兩個應用中，高 LAP 樣本的預測力被放大，截止後樣本則交互作用不顯著。
    - Methodology：統計檢定程序＋兩個財經應用；以截止前後樣本作對照。
    - Quality：Level III（截止前後對照）；Tier 2（預印本）
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：本研究的實驗 E1（扣掉「說知道」後 AUC 由 0.88 降到 0.54）在邏輯上與 LAP×預測的交互作用檢定相同；本研究多了一步：以 SEC 紀錄查核自述本身是否正確（實驗 D），LAP 則沒有對照外部紀錄。
    - `from_dreamy_corpus: true`（dreamy 回顧列為全文閱讀；本書目只讀摘要，閱讀範圍依本輪實際記錄為 abstract_only）

19. **Duan, M., Suri, A., Mireshghallah, N., Min, S., Shi, W., Zettlemoyer, L., Tsvetkov, Y., Choi, Y., Evans, D., & Hajishirzi, H. (2024). Do membership inference attacks work on large language models? In *Proceedings of the First Conference on Language Modeling (COLM 2024)*. https://arxiv.org/abs/2402.07841**
    - 識別碼：arXiv 2402.07841（ID 查核相符；arXiv 註記「Accepted at Conference on Language Modeling (COLM), 2024」）
    - Relevance：記憶偵測方法的效度警訊：表面上成功的偵測，可能只是成員與非成員的時間範圍不同所造成的分布差異。
    - Key Findings：（摘要）在 Pile 上訓練、160M 到 12B 參數的模型上，多數設定的 membership inference 幾乎只比隨機猜測好；原因是資料量大、訓練迭代少，以及成員與非成員的界線本來就模糊；先前看似成功的設定，可歸因於分布偏移，例如成員與非成員來自相同領域但**時間範圍不同**。
    - Methodology：大規模評估＋公開 benchmark（MIMIR）。
    - Quality：Level III（多設定的對照評估）；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：本研究以「時間內 vs 時間外」公司比較自述，兩組的差異不只在於是否被記得，還有年份、公司特徵與標籤成熟度的分布差異；Duan 等正好說明這種對照可能把分布差異誤認為記憶。

20. **Fu, Y., Uzuner, O., Yetisgen, M., & Xia, F. (2025). Does data contamination detection work (well) for LLMs? A survey and evaluation on detection assumptions. In *Findings of the Association for Computational Linguistics: NAACL 2025* (pp. 5235–5256). Association for Computational Linguistics. https://doi.org/10.18653/v1/2025.findings-naacl.291**
    - 識別碼：DOI 10.18653/v1/2025.findings-naacl.291（Crossref 相符）；arXiv 2410.18966
    - Relevance：系統整理污染偵測方法背後的假設並檢驗其是否成立，是評估「自述探針」效度的框架。
    - Key Findings：（摘要）回顧 50 篇污染偵測研究，歸納八類假設並檢視是否經過嚴謹驗證；以三類假設做個案研究（實例層級、即 MIA）：在預訓練用過的資料集上，表現可能接近隨機，顯示模型可能學到資料分布而非記住個別實例；資料在「見過／未見過」之間有分布偏移時，MIA 很容易失效。
    - Methodology：系統性文獻回顧（50 篇）＋案例實證。
    - Quality：Level V（回顧＋描述性驗證）；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：Phase 3 可用其八類假設逐一檢核本研究探針的假設（例如「說知道 ⇒ 訓練時見過該事件」）；「學到分布而非個別實例」對應主題 1 的「公司類型先驗」成分。

### Search Limitations
- **閱讀深度**：20 篇全部只讀到摘要（arXiv 或 Crossref）或 WebSearch 摘述，沒有讀全文；方法弱點一律未評估。關鍵數字（如 Ni 等的 ECE、Shah 等的公司特徵效果）只能引用摘要所寫，細節需讀全文確認。
- **資料庫**：沒有 Semantic Scholar 與 OpenAlex（無 API 金鑰），無法做引用網絡追蹤（forward／backward citation）與 S2 去重；去重只靠題名比對，PRISMA 的重複數與標題篩選數為近似值。
- **arXiv 檢索的限制**：關鍵字只用 `abs:`／`ti:` 欄位與 relevance 排序，總筆數大的檢索式（如 #3 有 61 筆）只取前 12–15 筆；可能漏掉用詞不同的研究（例如 epistemic honesty、knowledge boundary、temporal misalignment）。
- **known-item 偏誤**：奠基文獻部分先依領域知識列為候選再查核，可能偏向高被引的英文 NLP 文獻。
- **子題覆蓋不均**：
  - 「時間錯置」（把真實事件套到錯誤年份）作為錯誤類型的直接研究較少；本書目只收 Dhingra 等與 Cheng 等兩篇。Herel 等 (2024) 與 LLMLagBench (2025) 因只讀到題名或二手摘述而未收，可在下一輪讀取摘要後補入。
  - 財務或公司領域只有 2 篇（Shah 等、Gao 等）；以 SEC 執法紀錄查核 LLM 事件記憶的研究，**在本次檢索範圍內**未找到。這是以本次檢索為界的觀察，不是無此研究的證明。
  - 模型自述與人類專家查核的比較、以及不同模型家族（Claude 系列）之間自述差異的研究，未找到直接文獻。
- **出版狀態**：Cheng 等、Duan 等、Shah 等的 COLM 收錄依 arXiv 註記與 WebSearch 確認，COLM 無 DOI；Ni 等的 DOI 字串格式與一般 ACL DOI 不同（無 `v1/`），已以 Crossref `/works` 查核相符，Phase 2 來源查核時可再確認。
- **預印本**：4 篇為預印本（Kadavath 等、Wei 等、Kalai 等、Gao 等），其中 Gao 等與 Kalai 等為 2025 年 arXiv，依 ARS v3.7.3 的 `preprint_post_llm_inflection` 規則屬應留意的類別。
- **語言**：只檢索英文。

### 交還給呼叫者
本檔只完成 Phase 2 書目。綜整（例如把 20 篇整理成錯誤類型框架、或評估自述探針的效度）屬 Phase 3，請由 synthesis 階段處理。
