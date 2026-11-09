# 主題 5 書目（Phase 2）：結果不可能被記得時，LLM 能從年報讀出多少舞弊訊號？——時間外 benchmark

> 角色：ARS deep-research `bibliography_agent`（只做 Phase 2：檢索、篩選、註解）。本檔**不含**綜整、結論或撰寫；跨文獻的比較與推論留給 Phase 3。
> 研究問題（`results/research_topics.md` 主題 5）：在模型訓練截止後才出事的公司上，LLM 讀年報的舞弊判斷，能否勝過傳統會計模型與「只看公司類型」的基準？
> 規範：`results/lit_review/protocol.md`（整合性回顧、收錄標準、查核規則）。
> AI 使用聲明：檢索、查核與註解由 AI（Claude）完成；引用前請研究者核對原文。

## Annotated Bibliography

### Search Strategy

PRE-SCREENED FROM USER CORPUS:
- Adapter: <unspecified>
  Adapter origin not declared; user-written adapter should populate obtained_via per v3.6.4 schema recommendation.（來源為 `phase2_bibliography/dreamy_round10_lit_review.md` 的參考文獻與 §3 表格，非結構化 `literature_corpus[]`；依呼叫者指示視為預篩語料，以相同標準重新篩選。）
- Snapshot date: <unspecified>
  Snapshot date not declared; reproducibility is reduced. Adapter should populate obtained_at per v3.6.4 schema recommendation.（該回顧標示版本 v3，2026-11-03。）
- Total entries scanned: 36（參考文獻 33 條；Walker 2021、Walker 2022、Gow 2022、Klein 2023 拆為 4 條計算）
- Pre-screening result:
  - Included: 10 entries（每一篇都由本代理以 Crossref 或 arXiv 重新查核）
    citation_keys:
      - bao2020detecting
      - barton2024importance
      - bertomeu2021using
      - brown2020what
      - efe2026earnings
      - sugiura2026edinet
      - waffodzuyo2026benchmarking
      - wang2026umar
      - yue2026frauddebate
      - zavitsanos2021financial
  - Excluded by inclusion / exclusion criteria: 26 entries
    citation_keys:
      - bhattacharya2024accounting：符合主題，但只有相對增益、沒有 AUC；文字型子主題已有 3 篇 Tier 1，受每主題 20 篇上限，優先序較低
      - dai2026fsfdllm：摘要未寫國別與指標；dreamy 已判定片段數字不可用
      - engelberg2025entity：屬主題 3（匿名化）
      - ergun2025financial：符合主題，但只讀得到摘要、只說「平均優於」，且樣本期與 FinLlama／FinGPT 訓練期重疊（dreamy 註記）；受上限排除
      - gao_lookahead：屬主題 1（記憶偵測）
      - glasserman2024：屬主題 1／3
      - he2025chronobert：屬主題 1
      - kelly2026scaling：屬主題 1；NBER 無法連線
      - kim2024financial：arXiv 2407.17866v3 作者已「暫時撤回」（本代理以 arXiv API 確認 comment：「A co-author identified inconsistencies in the data and analyses ... we have temporarily withdrawn the working paper」）；數字不可引用，依灰色地帶＝剔除
      - kirkos2024：SSRN 預印本，數字未查證、無 AUC
      - levy2026caution：屬主題 1
      - lopezlira2025memorization：屬主題 1（其「截止後小樣本」論點與本主題相關，但受上限排除；主題 1 書目應收錄）
      - ludwig2026：屬主題 1
      - nie2025：中國樣本；只有摘要；受上限排除
      - sarkar2024：屬主題 1
      - walker2021、walker2022、gow2022、klein2023：與 Bao et al. (2020) 爭議直接相關，但本輪未能以 Crossref／arXiv 或含完整題名作者年份的 WebSearch 結果逐篇確認（Econ Journal Watch 部分無 DOI）；依規則剔除。Bao 勘誤本身已由 Crossref `updated-by` 確認，見 bao2020detecting 條目
      - wu2026anonymization：屬主題 3
      - yu2026parademb：沒有找到數字；受上限排除
      - auditfraudbench2026、auditbench2025、finverbench、vera8b：題庫型，沒有正常公司或連續分數，不回應「時間外排序 AUC」問題
      - ohartman_restatement_risk（GitHub）：與本主題高度相關（8-K 4.02 時間外、F-score 基準），但為 README 灰色文獻，本輪未查核；受 Tier 3 與總數上限排除，建議 Phase 2 查核階段再評估
- Note: presence in corpus does not imply inclusion; same criteria applied to corpus and external sources.

**Databases**：WebSearch（mode: standard，共 13 次查詢）、arXiv API（`export.arxiv.org/api/query`，8 次關鍵字查詢＋ID 查核）、Crossref API（`api.crossref.org/works`，19 次關鍵字查詢＋20 次 DOI 查核）。OpenAlex、Semantic Scholar 無 API 金鑰，不使用；Step 4.5 S2 去重依降級規則略過，改以題名人工去重。

**Keywords（實際查詢字串）**：
- Crossref（`query.bibliographic`）：
  1. `Predicting material accounting misstatements Dechow Ge Larson Sloan`
  2. `The detection of earnings manipulation Beneish 1999`
  3. `Financial statement fraud detection analysis of statistical and machine learning algorithms Perols`
  4. `Finding needles in a haystack using data analytics to improve fraud prediction Perols`
  5. `Detecting management fraud in public companies Cecchini Aytug Koehler Pathak`
  6. `Accounting variables, deception, and a bag of words Purda Skillicorn`
  7. `Do fraudulent firms produce abnormal disclosure Hoberg Lewis`
  8. `Proxies and databases in financial misconduct research Karpoff Koester Lee Martin`
  9. `The importance of distinguishing errors from irregularities in restatement research Hennes Leone Miller`
  10. `How pervasive is corporate fraud Dyck Morse Zingales`（另以 `... Review of Accounting Studies 2024` 再查一次）
  11. `Detecting deceptive discussions in conference calls Larcker Zakolyukina`
  12. `Detecting accounting fraud in publicly traded U.S. firms using a machine learning approach Bao Ke Li Yu Zhang`
  13. `What are you saying? Using topic to detect financial misreporting Brown Crowley Elliott`
  14. `Using machine learning to detect misstatements Bertomeu Cheynel Floyd Pan`
  15. `Deep learning for detecting financial statement fraud Craja Kim Lessmann`
  16. `Financial misconduct detection probability commission Barton Burnett Gunny Miller`
  17. `large language model accounting fraud detection`；`ChatGPT financial statement fraud detection`；`generative AI financial misreporting detection annual reports`；`large language model restatement prediction`
  18. `Financial misstatement detection: a realistic evaluation Zavitsanos`；`ForecastBench dynamic benchmark AI forecasting capabilities Karger`；`Data contamination through the lens of time Roberts`
- arXiv（`search_query`）：
  1. `abs:"large language model" AND abs:fraud AND (abs:"financial statement" OR abs:accounting OR abs:10-K)`
  2. `abs:"language model" AND (abs:restatement OR abs:misstatement OR abs:"accounting fraud" OR abs:"financial misreporting")`
  3. `abs:"financial statement fraud" AND (abs:LLM OR abs:GPT OR abs:transformer OR abs:BERT)`
  4. `ti:LiveBench AND ti:"contamination"`；`ti:LiveCodeBench`；`ti:cutoff AND ti:longitudinal AND ti:contamination`；`ti:ForecastBench`
  5. `abs:"look-ahead bias" AND abs:"knowledge cutoff" AND (abs:financial OR abs:finance)`
  6. ID 查核：2407.17866、2305.17457、2504.14765、2310.10628、2606.15640、2506.08762、2607.19259、2611.01123、2605.14467、2505.11065、2510.07920、2409.19839
- WebSearch（standard）：
  - 檢索用：`large language model financial statement fraud detection 10-K misstatement 2025`；`LLM restatement prediction 8-K Item 4.02 non-reliance machine learning`；`financial misreporting detection lag years between misstatement and disclosure AAER machine learning label delay`；`GPT large language model detect financial misreporting annual report accounting research 2024 2025 journal`；`post knowledge cutoff evaluation LLM financial prediction benchmark rolling time-split contamination-free finance 2025`
  - 查核／取摘要用：`Kim Muhn Nikolaev "Financial Statement Analysis with Large Language Models"`；`"To the Cutoff... and Beyond? A Longitudinal Perspective on LLM Data Contamination" Roberts`；`"Positive-Unlabeled Learning for Financial Misstatement Detection under Realistic Constraints"`；`ForecastBench Karger ICLR 2025 dynamic benchmark AI forecasting`；Hoberg & Lewis、Dechow et al.、Beneish、Bertomeu et al. 的題名＋abstract 查詢

**Boolean**：（fraud OR misstatement OR misreporting OR restatement OR AAER OR "Item 4.02"）AND（prediction OR detection OR "machine learning" OR "language model" OR LLM OR text）；時間外子題另用（"knowledge cutoff" OR "post-cutoff" OR contamination OR "look-ahead"）AND（benchmark OR "dynamic" OR "live" OR "longitudinal"）。

**Date Range**：以 2020–2026 為主；經典會計舞弊與標籤文獻（1999–2017）依 protocol 不限年份。

**Last Searched**：2026-11-09

**Language**：英文（未檢索中文、日文資料庫）。

**Inclusion Criteria**（protocol 原文）：直接回應主題 5；2020 年以後為主，經典會計舞弊奠基文獻不限年份；期刊或會議（Tier 1）、預印本（Tier 2，標示）、官方或技術文件（Tier 3，至多 2 篇）；有 DOI、arXiv ID 或穩定網址且題名、作者、年份可核對。

**Exclusion Criteria**：只是順帶提到；部落格、新聞、行銷文章、學生論文、課程專案；掠奪性期刊；查不到存在證據；作者撤回；屬其他主題（1–4）的核心文獻（避免重複，交由該主題書目）。

**Coverage Distribution Advisory**：

DISTRIBUTIONAL_SKEW_ADVISORY:
- Dimension: time distribution
- Concentration: 2020s = 14/20 (70%)
- Advisory: This is a coverage-distribution signal, not a defect. Consider whether the RQ warrants broader periods, sites, methods, or venue families.
- Search response: no expansion; user requested this scope（protocol 規定「2020 年以後為主」；1999–2017 的 6 篇為經典基準與標籤文獻）

DISTRIBUTIONAL_SKEW_ADVISORY:
- Dimension: geographic distribution
- Concentration: 美國（SEC／AAER／10-K／8-K 樣本）= 11/12 (92%)（known_N 只計摘要、metadata 或 dreamy 回顧明示樣本地區者；Beneish、Perols、Purda & Skillicorn、Barton et al.、Dyck et al.、Roberts et al.、Karger et al.、Li et al.（DeepFund）未明示，不計；Efe、Zavitsanos、Bertomeu 的地區依 dreamy 回顧記載）
- Advisory: This is a coverage-distribution signal, not a defect. Consider whether the RQ warrants broader periods, sites, methods, or venue families.
- Search response: 主題 5 的標籤（8-K 4.02、AAER）本身就是美國制度，集中屬預期；唯一非美國樣本為 EDINET-Bench（日本）。可補的檢索字串：`financial statement fraud detection China CSMAR large language model`、`J-STAGE 不正会計 予測`（本輪未執行）

方法分布（量化檔案研究 6、計算／ML 模型 8、資料集／benchmark／評估框架 6；最大 40%）與期刊分布（最大為 JAR、RAST 各 2/20；純預印本 3/20）未觸發提醒。

### PRISMA Flow

```
Records identified (total): 240
|-- Crossref 關鍵字查詢: 106（19 次查詢 × 3–10 筆）
|-- arXiv 關鍵字查詢: 48（顯示筆數；查詢 2 的 51 筆總數中取前 30）
|-- WebSearch 檢索用查詢: 50（5 次 × 10 個連結；另 8 次查核用查詢不計入）
+-- dreamy 預篩語料: 36

Duplicates removed: 約 30（SSRN 工作論文版與期刊版、arXiv 與 WebSearch、dreamy 與外部檢索的重複；人工題名比對，未經 S2 去重，故為約數）
Records screened (title/abstract): 約 210
Records excluded: 約 152（大多為無關領域：化學、信用卡／區塊鏈詐欺、釣魚網址、教學等；以及書籍章節、學生論文、課程專案、廠商頁面）
Eligibility assessed (abstract／metadata 層級；本輪未讀全文): 58（dreamy 語料 36＋外部候選 22）
Excluded at eligibility (with reasons): 38
  - dreamy 語料 26 條：理由逐條見上方 PRE-SCREENED 區塊（屬主題 1／3：10；題庫型：4；Walker 等未能查核：4；作者撤回：1；指標不明或受上限：6；GitHub 灰色文獻：1）
  - 外部候選 12 條：
    - 受每主題 20 篇上限、優先序較低：8（Perols et al. 2017 TAR、Cecchini et al. 2010 Management Science、Cecchini et al. 2010 DSS、Craja et al. 2020 DSS、Hennes et al. 2008 TAR、Larcker & Zakolyukina 2012 JAR、LiveBench arXiv 2406.19314、LiveCodeBench arXiv 2403.07974）
    - 只有 DOI 與題名、讀不到摘要：1（Zavitsanos et al. 2025, ICAIF '25, DOI 10.1145/3768292.3770366；dl.acm.org 無法連線）
    - 題庫型／非排序任務：1（FinED-Bench, arXiv 2608.12342，僅見 WebSearch 連結，未查核）
    - 交易 agent 洩漏、與已收錄 DeepFund 重疊且未經審查：1（Profit Mirage, arXiv 2510.07920）
    - 一般 PU 學習方法、舞弊僅為應用例：1（Zavitsanos & Paliouras 2026, arXiv 2605.14467，journal_ref: Data Min Knowl Disc 40, 101）
Studies included in review: 20（dreamy 語料 10＋外部 10）
```

說明：Crossref 與 arXiv 的模糊檢索會回傳大量「總筆數」（例如 Crossref 動輒百萬筆），上表只計實際取回並檢視的筆數。

### Sources (N = 20)

> 欄位說明：**閱讀範圍**一律依實況填寫。本代理本輪**沒有讀任何全文**，20 篇皆為 `abstract_only`（摘要來自 Crossref、arXiv API 或 WebSearch 摘要片段）。凡標「據 dreamy 回顧」的數字，是 dreamy 回顧（其自述讀取範圍見該檔）所記，本代理未重讀原文。證據等級依 `deep-research/references/source_quality_hierarchy.md`（I–VII）。Tier：1＝期刊或會議論文，2＝預印本，3＝官方或技術文件。

#### 子主題 A：經典會計舞弊／錯報預測模型（傳統基準）

1. **Beneish, M. D. (1999). The detection of earnings manipulation. *Financial Analysts Journal, 55*(5), 24–36. https://doi.org/10.2469/faj.v55.n5.2296**
   - 識別碼：DOI 10.2469/faj.v55.n5.2296（Crossref 題名、作者、卷期相符）｜閱讀範圍：abstract_only（EconPapers 摘要，經 WebSearch）｜from_dreamy_corpus: false
   - Relevance：M-score 的原始文獻；本研究第九輪的傳統基準之一。
   - Key Findings：描繪盈餘操縱公司的特徵並提出偵測模型；變數用來捕捉操縱造成的報表扭曲或促使操縱的前提條件；摘要稱模型在公開揭發前約能辨識一半的操縱公司。
   - Methodology：以財務比率的年變動建構機率模型（細節未讀）。
   - Quality：Level IV（檔案型個案－對照）；Tier 1。
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：第九輪時間外 4.02 樣本的 M-score AUC 0.66 即以此模型計算；係數與門檻的二手來源互有出入（WebSearch 結果），實作時應以原文為準。

2. **Dechow, P. M., Ge, W., Larson, C. R., & Sloan, R. G. (2011). Predicting material accounting misstatements. *Contemporary Accounting Research, 28*(1), 17–82. https://doi.org/10.1111/j.1911-3846.2010.01041.x**
   - 識別碼：DOI（Crossref 相符）｜閱讀範圍：abstract_only（摘要片段經 WebSearch）｜from_dreamy_corpus: false
   - Relevance：F-score 的原始文獻；AAER 樣本建構的標準參考。
   - Key Findings：以 1982–2005 年約 2,190 份 AAER 建構錯報公司樣本；模型輸出為縮放後的 logistic 機率（F-score），大於 1 表示錯報可能性較高；涵蓋應計品質、財務績效、非財務指標、表外活動與市場誘因。
   - Methodology：logistic 迴歸，財務比率與市場變數。
   - Quality：Level IV；Tier 1。
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：第九輪 F-score AUC 0.63 的來源模型；dreamy 回顧記載 FraudDebate 表 3 的「F-score LR 0.690」，兩者樣本與標籤不同。

3. **Perols, J. (2011). Financial statement fraud detection: An analysis of statistical and machine learning algorithms. *Auditing: A Journal of Practice & Theory, 30*(2), 19–50. https://doi.org/10.2308/ajpt-50009**
   - 識別碼：DOI（Crossref 相符）｜閱讀範圍：abstract_only（Crossref 摘要）｜from_dreamy_corpus: false
   - Relevance：在不同誤判成本與舞弊比例假設下比較 ML 方法，是「稀有正例下如何評估」的早期文獻。
   - Key Findings：六種方法中 logistic 迴歸與 SVM 表現相對較好，優於類神經網路、bagging、C4.5 與 stacking；42 個預測變數中只有 6 個被各演算法一致選用（審計師更換、裁量性應計、四大審計、應收帳款、達成或超越分析師預測、異常員工生產力）。
   - Methodology：舞弊公司與非舞弊公司樣本，變動誤判成本與正例比例的模擬評估。
   - Quality：Level IV；Tier 1。
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：提醒 AUC 以外，成本與盛行率設定會改變方法排序；第九輪 4.02 樣本為配對設計，盛行率與母體不同。

4. **Bao, Y., Ke, B., Li, B., Yu, Y. J., & Zhang, J. (2020). Detecting accounting fraud in publicly traded U.S. firms using a machine learning approach. *Journal of Accounting Research, 58*(1), 199–235. https://doi.org/10.1111/1475-679X.12292**（Erratum: *Journal of Accounting Research, 60*(4), 1635–1646, 2022, https://doi.org/10.1111/1475-679X.12454）
   - 識別碼：DOI（Crossref 相符；Crossref `updated-by` 欄位顯示 2022-08-04 的 erratum，DOI 10.1111/1475-679x.12454，題名「Erratum」，卷期頁 60(4):1635–1646）｜閱讀範圍：abstract_only（Crossref 摘要）｜from_dreamy_corpus: true
   - Relevance：第十輪復刻 FraudDebate-Agent 所用的標準資料（AAER、28 項原始會計數字）。
   - Key Findings：以理論挑選的原始會計數字（而非比率）加上集成學習（RUSBoost）建模；提出排序型評估指標（NDCG@k）；摘要稱大幅勝過 Dechow et al. 的 logistic 模型與 Cecchini et al. 的財務核 SVM。
   - Methodology：AAER 標籤，集成學習，時間序切分（dreamy 回顧記為測試 2003–2008）。
   - Quality：Level IV；Tier 1；**有勘誤**。
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 補充（據 dreamy 回顧，本代理未重讀）：勘誤指程式錯誤導致績效指標高估；dreamy 另記載 Walker（Econ Journal Watch）的批評與後續討論，本代理本輪未能逐篇查核，故不列為獨立來源。
   - 與本研究的關聯：第十輪的資料與基準數字來源；所有樣本年度都早於任何 LLM 的訓練截止，資料內部沒有時間外對照。

5. **Bertomeu, J., Cheynel, E., Floyd, E., & Pan, W. (2021). Using machine learning to detect misstatements. *Review of Accounting Studies, 26*(2), 468–519. https://doi.org/10.1007/s11142-020-09563-8**
   - 識別碼：DOI（Crossref 相符；線上首刊 2020-10-02）｜閱讀範圍：abstract_only（摘要片段經 WebSearch）｜from_dreamy_corpus: true
   - Relevance：以梯度提升樹預測重大錯報，並比較會計、審計、市場與治理變數群的貢獻。
   - Key Findings：會計變數單獨偵測錯報的效果差，與審計與市場變數合用時才有用；另比較演算法並做一年與兩年後的預測。
   - Methodology：gradient boosted regression trees；標籤的確切來源本代理未從摘要確認（dreamy 回顧據灰色來源記為 8-K 4.02，未經查核）。
   - Quality：Level IV；Tier 1。
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：「只看會計數字不夠」與第九輪事實卡（含非財務資訊）的設計可對照；若標籤確為 4.02，則是本研究 4.02 樣本最接近的非 LLM 基準。

#### 子主題 B：文字型舞弊與錯報偵測（LLM 之前）

6. **Purda, L., & Skillicorn, D. (2015). Accounting variables, deception, and a bag of words: Assessing the tools of fraud detection. *Contemporary Accounting Research, 32*(3), 1193–1223. https://doi.org/10.1111/1911-3846.12089**
   - 識別碼：DOI（Crossref 相符；線上首刊 2014-10-09）｜閱讀範圍：abstract_only（Crossref 摘要）｜from_dreamy_corpus: false
   - Relevance：以 MD&A 用字建構「真實機率」，並與 8 種量化與語言工具比較。
   - Key Findings：語言方法在橫斷面與時間序列設定都有效；能在同一家公司的一系列報告中辨認出舞弊報告，摘要指出這是會計型工具常有困難的情境；真實機率的水準與變動都和舞弊相關。
   - Methodology：資料驅動的 bag-of-words 分類，MD&A（年報與季報）。
   - Quality：Level IV；Tier 1。
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：第九輪「整份 10-K」組（AUC 0.76）的文字訊號前身；也提供「同公司跨年」的評估方式。

7. **Hoberg, G., & Lewis, C. (2017). Do fraudulent firms produce abnormal disclosure? *Journal of Corporate Finance, 43*, 58–85. https://doi.org/10.1016/j.jcorpfin.2016.12.007**
   - 識別碼：DOI（Crossref 相符）｜閱讀範圍：abstract_only（EconPapers 摘要經 WebSearch）｜from_dreamy_corpus: false
   - Relevance：以 AAER 標籤檢驗 MD&A 的「異常揭露」能否預測舞弊。
   - Key Findings：舞弊公司的 MD&A 偏離強基準；異常文字可在樣本外預測舞弊；舞弊公司較少使用與詳細揭露相關的 LDA 主題，經理人在舞弊年度較少自我指涉；異常揭露只出現在舞弊進行的年度。
   - Methodology：LDA 主題模型、相對同業的異常文字度量。
   - Quality：Level IV；Tier 1。
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：「舞弊年度才出現」的特性，關係到本研究應以哪一年的 10-K 給模型讀（違規期間 vs 揭露前一年）。

8. **Brown, N. C., Crowley, R. M., & Elliott, W. B. (2020). What are you saying? Using *topic* to detect financial misreporting. *Journal of Accounting Research, 58*(1), 237–291. https://doi.org/10.1111/1475-679X.12294**
   - 識別碼：DOI（Crossref 相符）｜閱讀範圍：abstract_only（Crossref 摘要）｜from_dreamy_corpus: true
   - Relevance：10-K 主題內容對故意錯報的增量預測力，標籤同時用 AAER 與重編／10-K/A 中的故意違規。
   - Key Findings：1994–2012 年 10-K 敘述；主題變數在樣本外使偵測率最多提升 59%（相對於財務與文字風格變數模型）；在嚴重的收入認列錯報上勝過傳統模型。
   - Methodology：貝氏主題模型（LDA）＋樣本外測試。
   - Quality：Level IV；Tier 1。
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：同時使用 AAER 與重編標籤，可對照本研究 4.02（第九輪）與 AAER（9f）兩種樣本。

#### 子主題 C：LLM 財報舞弊／重編偵測（2025–2026）

9. **Yue, X., Yang, J., & Liu, W. (2026). FraudDebate-Agent: A multi-agent LLM framework with an evidence-based debate mechanism for financial statement fraud detection. *Mathematics, 14*(15), Article 2695. https://doi.org/10.3390/math14152695**
   - 識別碼：DOI（Crossref 相符，線上 2026-07-27）｜閱讀範圍：abstract_only（Crossref 摘要；表 3 數字據 dreamy 回顧，其讀取範圍為全文）｜from_dreamy_corpus: true
   - Relevance：第十輪復刻對象；在 Bao 資料上同時報告 LLM 與傳統基準的 AUC。
   - Key Findings：四角色多 agent（量化分析、FinBERT 讀 MD&A、RAG 同業比較、Critic–Debate）。據 dreamy 回顧：完整方法 AUC 0.806、GPT-4 zero-shot 0.681、XGBoost 0.738、RUSBoost 0.725、F-score LR 0.690。
   - Methodology：Bao 資料＋EDGAR-CORPUS MD&A，時間外測試（FY2003–2008）。
   - Quality：Level IV；Tier 1（MDPI 期刊）。
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：第十輪的直接比較對象；測試年度早於所有 LLM 截止日，因此屬「時間內」對照，可與第九輪時間外結果並列。

10. **Wang, Y., Wang, M., Lu, Y., Peng, Z., & Lin, S. (2026). *Multi-agent framework for audit risk assessment with explicit uncertainty and evidence conflict modeling* (arXiv:2606.15640) [Preprint]. arXiv. https://arxiv.org/abs/2606.15640**
    - 識別碼：arXiv 2606.15640（arXiv API 題名相符）｜閱讀範圍：abstract_only（arXiv 摘要）｜from_dreamy_corpus: true
    - Relevance：以重編為標籤、時間順序切分、近年（2019–2023）資料，並含單一 LLM 基準。
    - Key Findings：UMAR（MD&A 文字、財務比率、CAM 三個 agent，Dempster–Shafer 融合）在 3,200 個公司年度上 AUROC 0.782、PR-AUC 0.341、ECE 0.052，勝過 LR、XGBoost、FinBERT 與單一／雙 agent LLM 基準。
    - Methodology：美國 10-K（2019–2023）；dreamy 回顧記為 Audit Analytics non-reliance 重編、測試 2023 年約 52 個正例。
    - Quality：Level IV；Tier 2（預印本）。
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：non-reliance 重編與本研究的 8-K 4.02 標籤概念相同；其測試年 2023 早於近期模型截止日。

11. **Sugiura, I., Ishida, T., Makino, T., Tazuke, C., Nakagawa, T., Nakago, K., & Ha, D. (2026). EDINET-Bench: Evaluating LLMs on complex financial tasks using Japanese financial statements. In *The Fourteenth International Conference on Learning Representations (ICLR 2026)*. arXiv:2506.08762. https://arxiv.org/abs/2506.08762**
    - 識別碼：arXiv 2506.08762（arXiv API 題名相符；comment「Accepted to ICLR 2026」）｜閱讀範圍：abstract_only（arXiv 摘要）｜from_dreamy_corpus: true
    - Relevance：公開、可重現的 LLM 會計舞弊偵測 benchmark，讀整份年報。
    - Key Findings：以十年日本年報建構舞弊偵測、盈餘預測與產業分類任務；最先進的 LLM 在舞弊與盈餘這類二元分類上只比 logistic 迴歸略好；單純把年報交給 LLM 不夠。
    - Methodology：EDINET 年報；zero-shot LLM；dreamy 回顧另記載公司名探針 ≤ 0.05。
    - Quality：Level IV；Tier 1（ICLR）。
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：「整份年報給 LLM」的對照設計，與第九輪 9g（整份 10-K，AUC 0.76）相近；非美國樣本。

12. **Waffo Dzuyo, G. S., Guibon, G., Cerisara, C., & Belmar-Letelier, L. (2026). *Benchmarking generalization in financial statement fraud detection: Robust evaluation and novel tasks* (arXiv:2607.19259) [Preprint; accepted at FinLLM@IJCAI 2026]. arXiv. https://arxiv.org/abs/2607.19259**
    - 識別碼：arXiv 2607.19259（arXiv API 題名相符）｜閱讀範圍：abstract_only（arXiv 摘要；數字據 dreamy 回顧）｜from_dreamy_corpus: true
    - Relevance：直接處理「隨機切分高估績效」的問題，提出公司隔離任務。
    - Key Findings：摘要指出隨機切分造成過度樂觀，無法反映對新公司或未來期間的泛化；提出 Company-Isolated FSFD（CI-FSFD），並公開美國公司資料（財報、摘要後的 MD&A、舞弊標籤）。據 dreamy 回顧：CI-FSFD 上微調 Fino1-8B 0.74、RF 0.70、zero-shot LLM 約 0.50，隨機切分最高 0.96。
    - Methodology：AAER 標籤、10-Q 公司季度、LLM 整合結構化與文字資料。
    - Quality：Level IV；Tier 2（workshop／預印本）。
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：公司隔離與本研究的「時間外」是兩種不同的切分；兩者可並列報告。

13. **Efe, A., Sapra, S., & Ahmed, B. (2026). *Do earnings calls help predict financial restatements? Evaluating text beyond public firm information* (arXiv:2611.01123) [Preprint]. arXiv. https://arxiv.org/abs/2611.01123**
    - 識別碼：arXiv 2611.01123（arXiv API 題名相符）｜閱讀範圍：abstract_only（arXiv 摘要）｜from_dreamy_corpus: true
    - Relevance：重編預測、配對設計、公開資訊基準，並檢查 LLM 是否認得公司。
    - Key Findings：109 份重編前的法說會 vs 218 份配對對照；文字可預測重編但相對公開公司資訊沒有可偵測的排序增益（加入文字的 AUROC 增益 95% CI −0.05 至 0.11）；文字分類器勝過隨機主要來自 SPAC 相關重編；LLM 分數較高，但在 66% 遮蔽後逐字稿中說出確切股票代號，且模型發布晚於重編。
    - Methodology：配對個案－對照；文字分類器與 LLM；身分辨識檢查。
    - Quality：Level IV；Tier 2（預印本，8 頁）。
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：與第九輪的配對 4.02 設計、「只給名稱」基準（0.69）與殘差概念直接對應；也顯示 SPAC 類重編可能主導結果，與第九輪樣本組成相關。

#### 子主題 D：標籤——AAER、重編與偵測機率

14. **Karpoff, J. M., Koester, A., Lee, D. S., & Martin, G. S. (2017). Proxies and databases in financial misconduct research. *The Accounting Review, 92*(6), 129–163. https://doi.org/10.2308/accr-51766**
    - 識別碼：DOI（Crossref 相符）｜閱讀範圍：abstract_only（Crossref 摘要）｜from_dreamy_corpus: false
    - Relevance：比較重編、證券集體訴訟與 AAER 等四個常用資料庫作為舞弊代理變數的差異。
    - Key Findings：實證結果會因使用哪個資料庫而不同；以 1,243 件監理機關對財務不實陳述採取執法行動的案例史為對照，辨識並估計各資料庫四項會影響推論的特性的經濟重要性，並給研究者建議。
    - Methodology：資料庫與手工案例史的比對。
    - Quality：Level IV；Tier 1。
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：第九輪用 8-K 4.02、9f 用 AAER；兩種標籤不可互換，報告時須分開。四項特性的具體內容需讀全文確認。

15. **Dyck, A., Morse, A., & Zingales, L. (2024). How pervasive is corporate fraud? *Review of Accounting Studies, 29*(1), 736–769. https://doi.org/10.1007/s11142-022-09738-5**（Correction: *Review of Accounting Studies, 30*(4), 3996–3998, 2025, https://doi.org/10.1007/s11142-025-09919-y）
    - 識別碼：DOI（Crossref 相符；`updated-by` 顯示 2025-09-01 更正）｜閱讀範圍：abstract_only（Crossref 摘要）｜from_dreamy_corpus: false
    - Relevance：估計未被發現的舞弊比例，關係到「對照公司」標籤的乾淨程度。
    - Key Findings：利用 Arthur Andersen 倒閉造成前客戶受到更多審視的自然實驗；正常時期約只有三分之一的舞弊被發現；每年約 10% 的大型上市公司在進行證券舞弊（95% CI 7%–14%）；舞弊每年毀損約 1.6% 的股東價值。
    - Methodology：自然實驗、下界估計。
    - Quality：Level III（自然實驗）；Tier 1；**有更正**（更正內容本代理未讀）。
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：第九輪的對照公司可能含未被發現的舞弊，會壓低所有方法的 AUC；這是標籤雜訊，不是模型能力。

16. **Barton, F. J., Burnett, B. M., Gunny, K., & Miller, B. P. (2024). The importance of separating the probability of committing and detecting misstatements in the restatement setting. *Management Science, 70*(1), 32–53. https://doi.org/10.1287/mnsc.2022.4627**
    - 識別碼：DOI（Crossref 相符）｜閱讀範圍：abstract_only（Crossref 摘要）｜from_dreamy_corpus: true
    - Relevance：重編只觀察得到「被發現的錯報」（部分可觀察性），預測重編等於同時預測發生與被發現。
    - Key Findings：以部分可觀察的雙變量 probit 分開發生機率與偵測機率；重新檢驗三篇既有重編研究，顯示分開兩者的重要性；建議以重編衡量會計品質的研究採用此模型。
    - Methodology：bivariate probit with partial observability。
    - Quality：Level IV；Tier 1。
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：LLM 讀 10-K 的分數可能同時反映「做了錯報」與「容易被發現」的特徵；時間外 4.02 樣本的 AUC 解讀需考慮這點。

#### 子主題 E：時間外驗證、偵測時滯與滾動 benchmark

17. **Zavitsanos, E., Mavroeidis, D., Bougiatiotis, K., Spyropoulou, E., Loukas, L., & Paliouras, G. (2021). Financial misstatement detection: A realistic evaluation. In *Proceedings of the Second ACM International Conference on AI in Finance (ICAIF '21)* (pp. 1–9). ACM. https://doi.org/10.1145/3490354.3494453**（arXiv:2305.17457）
    - 識別碼：DOI 10.1145/3490354.3494453（Crossref：作者與會議相符，Crossref 題名只收錄主標題「Financial misstatement detection」）；arXiv 2305.17457（完整題名相符，journal_ref 為 ICAIF 2021）｜閱讀範圍：abstract_only（arXiv 摘要）｜from_dreamy_corpus: true
    - Relevance：錯報偵測的「真實評估」框架，明確處理時間切分與偵測時滯。
    - Key Findings：提出新的評估框架，(a) 聚焦稀有的錯報類別，(b) 依時間切分訓練與測試，(c) 考慮錯報往往很久才被發現；顯示評估流程顯著影響系統表現。WebSearch 摘錄另述：訓練時尚未揭露的錯報先標為負例，過了重編日才改為正例。
    - Methodology：文獻回顧＋多模型、多特徵在新框架下的比較。
    - Quality：Level IV；Tier 1（ACM 會議）。
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：直接對應第九輪「依揭露日界定時間外」與「對照公司標籤尚未成熟」的設計問題。

18. **Roberts, M., Thakur, H., Herlihy, C., White, C., & Dooley, S. (2024). To the cutoff... and beyond? A longitudinal perspective on LLM data contamination. In *The Twelfth International Conference on Learning Representations (ICLR 2024)*. arXiv:2310.10628（預印本題名：Data contamination through the lens of time）. https://arxiv.org/abs/2310.10628**
    - 識別碼：arXiv 2310.10628（arXiv API 題名「Data Contamination Through the Lens of Time」相符；ICLR 2024 題名經 WebSearch 確認，iclr.cc poster 17911）｜閱讀範圍：abstract_only（arXiv 摘要）｜from_dreamy_corpus: false
    - Relevance：以訓練截止日為自然實驗，比較截止前後題目的表現，是「時間外樣本」設計在 LLM 評估中的方法先例。
    - Key Findings：以 GPT 模型的截止日切分 Codeforces 與 Project Euler 題目；截止前通過率與 GitHub 熱門度、發布日期有顯著關聯，提供污染的強證據；WebSearch 摘錄稱截止後此關聯消失；公開資料與評估框架。
    - Methodology：縱向（longitudinal）自然實驗。
    - Quality：Level III（自然實驗）；Tier 1（ICLR）。
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：第九輪「截止前 AAER vs 截止後 4.02」的比較在結構上與此相同；也提示以「知名度」作為污染的共變量。

19. **Karger, E., Bastani, H., Chen, Y.-H., Jacobs, Z., Halawi, D., Zhang, F., & Tetlock, P. E. (2025). ForecastBench: A dynamic benchmark of AI forecasting capabilities. In *The Thirteenth International Conference on Learning Representations (ICLR 2025)*. arXiv:2409.19839. https://arxiv.org/abs/2409.19839**
    - 識別碼：arXiv 2409.19839（arXiv API 題名相符；ICLR 2025 proceedings 經 WebSearch 確認）｜閱讀範圍：abstract_only（arXiv 摘要）｜from_dreamy_corpus: false
    - Relevance：「題目在提交時答案未知」的動態 benchmark，是滾動式時間外評估的通用範本。
    - Key Findings：自動產生並定期更新 1,000 題預測題，題目只涉及提交時答案未知的未來事件以避免資料洩漏；在 200 題子集上，專家預測者顯著勝過最佳 LLM（p < 0.001）；公開排行榜。
    - Methodology：前瞻式（prospective）評估，與人類專家及一般大眾比較。
    - Quality：Level IV；Tier 1（ICLR）。
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：本研究擬議的「隨模型更新的 8-K 4.02／AAER 滾動 benchmark」可借用其題目更新與排行榜機制；差別在舞弊標籤需要等待成熟期。

20. **Li, C., Shi, Y., Wang, C., Duan, Q., Ruan, R., Huang, W., Long, H., Huang, L., Tang, N., & Luo, Y. (2025). Time travel is cheating: Going live with DeepFund for real-time fund investment benchmarking. In *Advances in Neural Information Processing Systems (NeurIPS 2025), Datasets and Benchmarks Track*. arXiv:2505.11065. https://arxiv.org/abs/2505.11065**
    - 識別碼：arXiv 2505.11065（arXiv API 題名相符；comment「NeurIPS 2025 Datasets and Benchmarks Track」）｜閱讀範圍：abstract_only（arXiv 摘要）｜from_dreamy_corpus: false
    - Relevance：金融領域的即時（live）benchmark，只用各模型預訓練截止後發布的資料。
    - Key Findings：歷史回測讓 LLM「時間旅行」、利用訓練語料中的未來資訊，導致資訊洩漏與過度樂觀；DeepFund 連接即時市場資料，只用截止後資料評估九個旗艦 LLM；即使 DeepSeek-V3、Claude-3.7-Sonnet 也出現淨交易虧損。
    - Methodology：多 agent 架構，即時評估。
    - Quality：Level IV；Tier 1（NeurIPS D&B）。
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：「各模型截止日不同、需以各自截止日界定時間外」的原則，可直接用於本研究跨模型（Opus、Sonnet、Haiku）的時間外樣本界定。

### Search Limitations
- **讀取深度**：本輪 20 篇全部只讀到摘要（Crossref、arXiv API 或 WebSearch 摘要片段）；方法弱點依 ARS 規則一律寫 `not assessed`。標「據 dreamy 回顧」的數字未經本代理重讀原文。
- **無法連線的主機**：dl.acm.org 無法解析（Zavitsanos et al. 2025 ICAIF '25 的 PU 學習論文因此讀不到摘要而排除）；protocol 記載 MDPI、SSRN、NBER 先前無法連線，本輪未再嘗試。
- **無引用網絡**：OpenAlex、Semantic Scholar 無 API 金鑰，沒有做前向／後向引用追蹤，也沒有 S2 去重；Google Scholar 未檢索。經典文獻（Beneish、Dechow、Perols 等）的後續引用文獻可能有遺漏。
- **語言與地區**：只檢索英文；中國（CSMAR）、日本（J-STAGE）與台灣的 LLM 舞弊偵測文獻未系統檢索。
- **WebSearch 的限制**：結果為摘要化的片段，數字與細節可能不精確；作為存在證據時，本代理只採用同時出現完整題名、作者與年份的結果，且多數已另以 Crossref 或 arXiv 交叉確認。
- **未涵蓋**：Walker（Econ Journal Watch）對 Bao et al. 的批評與後續討論，本輪未能逐篇查核；8-K 4.02 作為標籤的專門研究（例如 4.02 揭露與重編嚴重度、揭露時滯的量化研究）只找到間接文獻（Hennes et al. 2008 因上限排除；Karpoff et al. 2017、Barton et al. 2024 收錄），可能仍有直接研究未被檢出。
- **2026 年預印本**：UMAR、Waffo Dzuyo、Efe 等多數未經完整同儕審查。
- **Kim, Muhn & Nikolaev (2024)**：LLM 財報分析的代表作，但作者已暫時撤回，依灰色地帶規則排除；若作者日後恢復或正式出版，應重新評估。
