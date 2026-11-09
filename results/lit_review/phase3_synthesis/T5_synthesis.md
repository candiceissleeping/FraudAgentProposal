# 主題 5 綜整（Phase 3，synthesis_agent）：結果不可能被記得時，LLM 能從年報讀出多少舞弊訊號？——時間外 benchmark

- 角色：ARS deep-research `synthesis_agent`，只做 Phase 3（綜整、矛盾處理、缺口分析）；不起草報告正文、不做跨主題整合
- 輸入：`results/lit_review/phase2_bibliography/T5_bibliography.md`、`T5_sources.json`；來源查核 `results/lit_review/phase2_verification/verification.md`（本主題 20 篇全部 VERIFIED）
- 研究問題：在模型訓練截止後才出事的公司上，LLM 讀年報的舞弊判斷，能否勝過傳統會計模型與「只看公司類型」的基準？
- 閱讀範圍聲明：本主題 20 篇在 T5 書目中**全部只讀到摘要**（`abstract_only`），方法弱點未評估，引用錨點一律為 `section:abstract`。
- **dreamy 數字的標示**：T5 書目中凡標「據 dreamy 回顧」的數字，本代理與 T5 書目代理都未重讀原文。本綜整在這些數字後一律加註「（數字取自 dreamy 文獻回顧，未重新核對）」。
- **跨主題引用**：本檔另引用 2 筆只屬於其他主題書目的來源，皆因與本主題直接相關：`lopezlira2025memorization`（T1／T3 書目；T5 書目自己註明其「截止後」論點與本主題相關、應由主題 1 收錄）、`duan2024membership`（T1／T4 書目；時間內外比較的分布偏移）。此外，`sugiura2026edinet` 雖在本主題書目中，但其公司名探針與逐年表現是依 T3 書目的章節閱讀紀錄（§5）引用，因為 T5 書目只讀摘要、並把探針數字記為「dreamy 回顧另記載」。
- 日期：2026-11-09

## 預定主張清單

（取代 Claim Intent Manifest；本環境沒有 Material Passport。）

| 編號 | 預定主張 | 預定依據（key） | 不可越界的限制 |
|---|---|---|---|
| C1 | 傳統會計模型提供中等水準的基準，但方法排序隨變數群、標籤、誤判成本與切分方式而變 | beneish1999detection、dechow2011predicting、perols2011financial、bao2020detecting、bertomeu2021using | Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract-->有勘誤；勘誤內容的解讀來自 dreamy |
| C2 | 文字含舞弊訊號，但相對公開公司資訊的增量在近期研究中受到質疑 | purda2015accounting、hoberg2017fraudulent、brown2020what、efe2026earnings | Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract-->樣本小、為法說會而非 10-K |
| C3 | LLM 舞弊偵測的報告增益多來自時間內評估；在公司隔離或更嚴格的設定下增益縮小 | yue2026frauddebate、wang2026umar、sugiura2026edinet、waffodzuyo2026benchmarking、efe2026earnings | Yue 等 (2026) <!--ref:yue2026frauddebate--><!--anchor:section:abstract-->與 Waffo Dzuyo 等 (2026) <!--ref:waffodzuyo2026benchmarking--><!--anchor:section:abstract-->的數字取自 dreamy，未核對 |
| C4 | 舞弊標籤本身是測量問題：資料庫差異、未被發現的舞弊、偵測與發生混在一起、揭露時滯 | karpoff2017proxies、dyck2024pervasive、barton2024importance、zavitsanos2021financial | 不推論對照組中舞弊的確切比例 |
| C5 | 以訓練截止日或提交時答案未知為界的前瞻／即時評估，是排除記憶的通用設計，但在舞弊領域本次檢索範圍內未見應用 | roberts2024cutoff、karger2025forecastbench、li2025deepfund、lopezlira2025memorization | 缺口以「本次檢索範圍內」為界 |

總限制：不使用未限定的因果語言；本研究第九、十輪的數字只出現在「與本研究實驗的對照」小節。

## Synthesis Report

### Literature Matrix

**Date compiled**：2026-11-09｜**Total sources**：20（本主題）＋ 2 筆跨主題（`lopezlira2025memorization`、`duan2024membership`，未列入矩陣）｜**Themes identified**：5

主題代號：
- **A** 傳統會計基準：中等水準，排序隨評估設定而變
- **B** 文字訊號：存在，但相對公開資訊的增量有爭議
- **C** LLM 舞弊偵測：報告增益多來自時間內評估，嚴格評估下縮小
- **D** 標籤是測量問題（資料庫、未發現舞弊、偵測 vs 發生、時滯）
- **E** 前瞻／時間外／即時評估作為排除記憶的設計

符號：✓ 支持；✗ 相反或限制性證據；◐ 部分相關；— 未涉及。等級與 Tier 依 T5 書目。

| Source | Year | Level | Tier | A | B | C | D | E |
|---|---|---|---|---|---|---|---|---|
| Beneish <!--ref:beneish1999detection--><!--anchor:section:abstract--> | 1999 | IV | 1 | ✓ | — | — | — | — |
| Dechow 等 <!--ref:dechow2011predicting--><!--anchor:section:abstract--> | 2011 | IV | 1 | ✓ | — | — | ◐ | — |
| Perols <!--ref:perols2011financial--><!--anchor:section:abstract--> | 2011 | IV | 1 | ✓ | — | — | — | — |
| Bao 等 <!--ref:bao2020detecting--><!--anchor:section:abstract--> | 2020 | IV | 1（有勘誤） | ✓ | — | — | — | ◐ |
| Bertomeu 等 <!--ref:bertomeu2021using--><!--anchor:section:abstract--> | 2021 | IV | 1 | ✓ | ◐ | — | — | — |
| Purda 與 Skillicorn <!--ref:purda2015accounting--><!--anchor:section:abstract--> | 2015 | IV | 1 | — | ✓ | — | — | — |
| Hoberg 與 Lewis <!--ref:hoberg2017fraudulent--><!--anchor:section:abstract--> | 2017 | IV | 1 | — | ✓ | — | ◐ | — |
| Brown 等 <!--ref:brown2020what--><!--anchor:section:abstract--> | 2020 | IV | 1 | — | ✓ | — | ◐ | — |
| Yue 等 <!--ref:yue2026frauddebate--><!--anchor:section:abstract--> | 2026 | IV | 1 | — | ◐ | ✗（框架勝過 ML 基準，時間內） | — | — |
| Wang 等 <!--ref:wang2026umar--><!--anchor:section:abstract--> | 2026 | IV | 2 | — | ◐ | ✗（勝過 LR、XGBoost 與 LLM 基準，時間內） | — | — |
| Sugiura 等 <!--ref:sugiura2026edinet--><!--anchor:section:abstract--> | 2026 | IV | 1 | — | — | ✓ | — | ◐ |
| Waffo Dzuyo 等 <!--ref:waffodzuyo2026benchmarking--><!--anchor:section:abstract--> | 2026 | IV | 2 | — | — | ✓ | — | ✓ |
| Efe 等 <!--ref:efe2026earnings--><!--anchor:section:abstract--> | 2026 | IV | 2 | — | ✗（文字無可偵測增益） | ✓ | — | — |
| Karpoff 等 <!--ref:karpoff2017proxies--><!--anchor:section:abstract--> | 2017 | IV | 1 | — | — | — | ✓ | — |
| Dyck 等 <!--ref:dyck2024pervasive--><!--anchor:section:abstract--> | 2024 | III | 1（有更正） | — | — | — | ✓ | — |
| Barton 等 <!--ref:barton2024importance--><!--anchor:section:abstract--> | 2024 | IV | 1 | — | — | — | ✓ | — |
| Zavitsanos 等 <!--ref:zavitsanos2021financial--><!--anchor:section:abstract--> | 2021 | IV | 1 | ◐ | — | — | ✓ | ✓ |
| Roberts 等 <!--ref:roberts2024cutoff--><!--anchor:section:abstract--> | 2024 | III | 1 | — | — | — | — | ✓ |
| Karger 等 <!--ref:karger2025forecastbench--><!--anchor:section:abstract--> | 2025 | IV | 1 | — | — | ◐ | — | ✓ |
| Li 等 <!--ref:li2025deepfund--><!--anchor:section:abstract--> | 2025 | IV | 1 | — | — | ◐ | — | ✓ |
| **Totals** | | | | **5✓ 1◐** | **3✓ 1✗ 3◐** | **3✓ 2✗ 2◐** | **4✓ 3◐** | **5✓ 2◐** |

（C 欄的 ✗ 表示該研究報告的 LLM 增益與「嚴格評估下增益縮小」方向相反；但兩篇的測試年度都早於近期模型的訓練截止日，屬時間內評估。）

### Key Themes

#### Theme A：傳統會計基準提供中等水準的偵測力，方法排序隨評估設定而變
**Evidence Strength**：Moderate（多篇同儕審查期刊，但全部只讀摘要，且各研究的標籤、樣本、指標不同，無法直接比較數字）
**Sources**：5 篇支持、1 篇部分相關；Level IV
**Synthesis**：

會計舞弊預測的經典模型給出了「有用但不完美」的基準。Beneish (1999) <!--ref:beneish1999detection--><!--anchor:section:abstract--> 以財務比率的年變動建構 M-score，摘要稱模型在公開揭發前約能辨識一半的操縱公司；Dechow 等 (2011) <!--ref:dechow2011predicting--><!--anchor:section:abstract--> 以約 2,190 份 AAER 建構錯報樣本，F-score 涵蓋應計品質、財務績效、非財務指標、表外活動與市場誘因。

後續研究顯示「哪個方法最好」取決於評估設定。Perols (2011) <!--ref:perols2011financial--><!--anchor:section:abstract--> 在變動誤判成本與正例比例下比較六種方法，logistic 迴歸與 SVM 相對較好，且 42 個預測變數中只有 6 個被各演算法一致選用。Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract--> 以原始會計數字加上集成學習（RUSBoost）並提出排序型指標 NDCG@k，摘要稱大幅勝過 Dechow 等 (2011) <!--ref:dechow2011predicting--><!--anchor:section:abstract-->的 logistic 模型；但 Crossref 記錄該文有 2022 年勘誤，T5 書目據 dreamy 回顧記載勘誤指程式錯誤導致績效指標高估（數字取自 dreamy 文獻回顧，未重新核對；勘誤內容本代理未讀）。Bertomeu 等 (2021) <!--ref:bertomeu2021using--><!--anchor:section:abstract--> 以梯度提升樹發現會計變數單獨偵測錯報的效果差，與審計與市場變數合用時才有用。

整合來看，傳統基準的價值在於提供「不需讀文字、不需 LLM」的參照點；但不同研究的數字因標籤（AAER vs 重編）、盛行率（配對 vs 母體）與指標（AUC vs NDCG@k）而不可直接比較。Perols (2011) <!--ref:perols2011financial--><!--anchor:section:abstract--> 特別提醒：AUC 以外，成本與盛行率設定會改變方法排序。

#### Theme B：文字含舞弊訊號，但相對公開公司資訊的增量受到質疑
**Evidence Strength**：Contested（三篇較早的 Tier 1 研究支持，一篇近期預印本提出反證）
**Sources**：3 篇支持、1 篇提出反證、3 篇部分相關；Level IV
**Synthesis**：

LLM 之前的文字研究一致發現年報敘述含有舞弊訊號。Purda 與 Skillicorn (2015) <!--ref:purda2015accounting--><!--anchor:section:abstract--> 以 MD&A 的 bag-of-words 建構「真實機率」，在橫斷面與時間序列設定都有效，且能在同一家公司的一系列報告中辨認出舞弊報告；Hoberg 與 Lewis (2017) <!--ref:hoberg2017fraudulent--><!--anchor:section:abstract--> 發現舞弊公司的 MD&A 偏離強基準，異常文字可在樣本外預測舞弊，且異常揭露只出現在舞弊進行的年度；Brown 等 (2020) <!--ref:brown2020what--><!--anchor:section:abstract--> 以 LDA 主題變數，在樣本外使偵測率最多提升 59%（相對於財務與文字風格變數模型）。

近期的反證來自 Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract-->：109 則重編前法說會對 218 則配對控制，文字可預測重編，但相對公開公司資訊沒有可偵測的排序增益（加入文字的 AUROC 增益 95% CI −0.05 至 0.11），且文字分類器勝過隨機多半來自 SPAC 相關重編。這是本主題中「讀到的內容未必增加訊號」最直接的證據。

兩方的差異可能來自文字類型（10-K／MD&A vs 法說會逐字稿）、樣本大小（Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract-->的信賴區間很寬，與「有中等增益」也相容）、基準的定義（Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract-->的「公開公司資訊」可能已涵蓋早期研究中的部分財務變數），以及標籤組成（SPAC 集中）。在摘要層級無法判定哪一個是主因。Bertomeu 等 (2021) <!--ref:bertomeu2021using--><!--anchor:section:abstract--> 的「會計變數單獨效果差、需與其他變數合用」，以及 Yue 等 (2026) <!--ref:yue2026frauddebate--><!--anchor:section:abstract--> 與 Wang 等 (2026) <!--ref:wang2026umar--><!--anchor:section:abstract--> 都把 MD&A 文字作為多 agent 框架的一部分，說明文字在近期研究中多以「與數字合用」的形式出現，而非單獨評估。

#### Theme C：LLM 舞弊偵測的報告增益多來自時間內評估，在嚴格評估下縮小
**Evidence Strength**：Emerging（3 篇支持、2 篇提出相反的時間內結果；多為 2026 年預印本，且數個關鍵數字取自 dreamy、未核對）
**Sources**：3 篇支持、2 篇提出相反方向的時間內結果、2 篇部分相關；Level IV
**Synthesis**：

2025–2026 年的 LLM 舞弊偵測研究可依評估設計分成兩組。

**時間內、報告明顯增益的一組**：Yue 等 (2026) <!--ref:yue2026frauddebate--><!--anchor:section:abstract--> 的四角色多 agent 框架（量化分析、FinBERT 讀 MD&A、RAG 同業比較、Critic–Debate）在 Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract-->的資料上報告完整方法 AUC 0.806、GPT-4 zero-shot 0.681、XGBoost 0.738、RUSBoost 0.725、F-score LR 0.690（數字取自 dreamy 文獻回顧，未重新核對）；測試年度早於所有 LLM 的訓練截止日。Wang 等 (2026) <!--ref:wang2026umar--><!--anchor:section:abstract--> 的 UMAR 在 3,200 個 2019–2023 年公司年度上 AUROC 0.782、PR-AUC 0.341、ECE 0.052，勝過 LR、XGBoost、FinBERT 與單一／雙 agent LLM 基準；其標籤為 Audit Analytics non-reliance 重編、測試 2023 年約 52 個正例（數字取自 dreamy 文獻回顧，未重新核對），測試年度早於近期模型的截止日。值得注意的是，即使在 Yue 等 (2026) <!--ref:yue2026frauddebate--><!--anchor:section:abstract-->的時間內結果中，GPT-4 zero-shot（0.681，dreamy 數字）也低於 XGBoost——LLM 的增益來自整個框架，而非 LLM 單獨。

**嚴格評估、增益縮小的一組**：Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:abstract--> 的日本年報 benchmark 中，最先進的 LLM 在舞弊偵測上只比 logistic 迴歸略好，摘要稱單純把年報交給 LLM 不夠。Waffo Dzuyo 等 (2026) <!--ref:waffodzuyo2026benchmarking--><!--anchor:section:abstract--> 的摘要指出隨機切分造成過度樂觀，並提出公司隔離任務 CI-FSFD；在 CI-FSFD 上微調 Fino1-8B 0.74、RF 0.70、zero-shot LLM 約 0.50，隨機切分最高 0.96（數字取自 dreamy 文獻回顧，未重新核對）。Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract--> 的 LLM 分數較高，但該 LLM 能在 66% 遮蔽逐字稿中說出確切股票代號，且模型在重編發生後才發布——其較高分數可能含有記憶成分，但摘要層級未量化。

跨領域的前瞻評估也指向同一方向：Karger 等 (2025) <!--ref:karger2025forecastbench--><!--anchor:section:abstract--> 在只涉及提交時答案未知之事件的 ForecastBench 上，專家預測者顯著勝過最佳 LLM；Li 等 (2025) <!--ref:li2025deepfund--><!--anchor:section:abstract--> 在只用截止後資料的即時基金投資評估中，連 DeepSeek-V3、Claude-3.7-Sonnet 也出現淨交易虧損，並把歷史回測的過度樂觀歸因於模型「時間旅行」。這兩篇不是舞弊研究，只作為「時間內回測 vs 前瞻評估」落差的旁證。

**對記憶假說的反面證據**：Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:5--> 的逐年分析發現，舞弊偵測表現在近年沒有下降，且只給財務表格時 7 個模型的公司名準確率都 ≤ 0.05（依 T3 書目的 §5 章節閱讀紀錄）。如果記憶顯著推高較早年度的表現，較接近截止日的年度應該較差；他們沒有觀察到這個型態。但作者也自承不能據此斷定沒有污染（T3 書目引文），且名稱探針只測「表格 → 名稱」、未測「表格 → 結果」。

整合來看，「LLM 勝過傳統基準」的報告主要出現在時間內、隨機或時間序切分、且使用多 agent 或微調的設定；在公司隔離、zero-shot 或前瞻設定下，增益縮小甚至消失。這是本綜整的整合性解讀，受限於多個關鍵數字未經核對。

#### Theme D：舞弊標籤本身是測量問題
**Evidence Strength**：Moderate（4 篇 Tier 1，包括一篇自然實驗）
**Sources**：4 篇支持、3 篇部分相關；Levels III–IV
**Synthesis**：

標籤文獻對「AUC 衡量了什麼」提出四個保留。

1. **不同資料庫不可互換**：Karpoff 等 (2017) <!--ref:karpoff2017proxies--><!--anchor:section:abstract--> 以 1,243 件執法案例史為對照，顯示實證結果會因使用重編、集體訴訟、AAER 等哪個資料庫而不同，並估計各資料庫四項會影響推論之特性的經濟重要性（四項特性的內容需讀全文確認）。Brown 等 (2020) <!--ref:brown2020what--><!--anchor:section:abstract--> 同時用 AAER 與重編／10-K/A 中的故意違規作標籤，Dechow 等 (2011) <!--ref:dechow2011predicting--><!--anchor:section:abstract--> 以 AAER 建構樣本。
2. **對照組含未被發現的舞弊**：Dyck 等 (2024) <!--ref:dyck2024pervasive--><!--anchor:section:abstract--> 利用 Arthur Andersen 倒閉造成前客戶受到更多審視的自然實驗，估計正常時期約只有三分之一的舞弊被發現，每年約 10% 的大型上市公司在進行證券舞弊（95% CI 7%–14%）；該文有 2025 年更正，更正內容未讀。
3. **偵測與發生混在一起**：Barton 等 (2024) <!--ref:barton2024importance--><!--anchor:section:abstract--> 指出重編只觀察得到「被發現的錯報」，以部分可觀察的雙變量 probit 分開發生機率與偵測機率，並重新檢驗三篇既有研究顯示分開兩者的重要性。
4. **揭露時滯與標籤成熟**：Zavitsanos 等 (2021) <!--ref:zavitsanos2021financial--><!--anchor:section:abstract--> 的評估框架聚焦稀有錯報類別、依時間切分訓練與測試，並考慮錯報往往很久才被發現；摘要指出評估流程顯著影響系統表現。Hoberg 與 Lewis (2017) <!--ref:hoberg2017fraudulent--><!--anchor:section:abstract--> 的「異常揭露只出現在舞弊進行的年度」則關係到應讀哪一年的報告。

這四點對時間外 benchmark 有直接含意：時間外樣本越新，對照組中「尚未被發現」的舞弊比例可能越高，標籤越不成熟；任何方法的 AUC 都會因此被壓低，而這是標籤雜訊，不是模型能力。這是依上述文獻所做的推論。

#### Theme E：前瞻／時間外／即時評估作為排除記憶的通用設計
**Evidence Strength**：Moderate（設計共識明確，但在舞弊領域本次檢索範圍內未見應用）
**Sources**：5 篇支持、2 篇部分相關；Levels III–IV（另有 1 筆跨主題來源）
**Synthesis**：

LLM 評估文獻發展出三種排除記憶的評估設計。

- **截止日自然實驗**：Roberts 等 (2024) <!--ref:roberts2024cutoff--><!--anchor:section:abstract--> 以 GPT 模型的截止日切分程式題，截止前通過率與 GitHub 熱門度、發布日期有顯著關聯，構成污染的強證據（WebSearch 摘錄另稱截止後此關聯消失）。Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract-->（跨主題，T1／T3 書目）也報告截止日後沒有回想。
- **前瞻式動態 benchmark**：Karger 等 (2025) <!--ref:karger2025forecastbench--><!--anchor:section:abstract--> 自動產生並定期更新只涉及提交時答案未知之未來事件的題目，以避免資料洩漏。
- **即時評估、依各模型截止日界定**：Li 等 (2025) <!--ref:li2025deepfund--><!--anchor:section:abstract--> 只用各模型預訓練截止後發布的資料評估。

會計文獻在 LLM 之前就有相關的時間切分概念：Zavitsanos 等 (2021) <!--ref:zavitsanos2021financial--><!--anchor:section:abstract--> 依時間切分並處理揭露時滯（WebSearch 摘錄另述：訓練時尚未揭露的錯報先標為負例，過了重編日才改為正例）；Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract--> 採時間序切分（dreamy 回顧記為測試 2003–2008；數字取自 dreamy 文獻回顧，未重新核對）。Waffo Dzuyo 等 (2026) <!--ref:waffodzuyo2026benchmarking--><!--anchor:section:abstract--> 的公司隔離是另一種切分，控制的是公司層級洩漏，不是時間層級。

方法上的保留來自 Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract-->（跨主題，T1／T4 書目）：時間範圍不同的樣本之間存在分布偏移，時間內外的表現差距不能全歸因於記憶。在舞弊情境中，這種偏移包括公司組成、標籤類型與標籤成熟度（Theme D）。

### Contradictions & Resolutions

| Claim A | Claim B | Resolution |
|---|---|---|
| Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract-->：原始會計數字＋集成學習大幅勝過 Dechow 等 (2011) <!--ref:dechow2011predicting--><!--anchor:section:abstract-->的 logistic 模型 | Bertomeu 等 (2021) <!--ref:bertomeu2021using--><!--anchor:section:abstract-->：會計變數單獨偵測錯報效果差；Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract-->的 2022 勘誤（dreamy：程式錯誤導致績效高估） | **未解決（flagged）**。標籤不同（AAER 舞弊 vs 重大錯報；Bertomeu 等 (2021) <!--ref:bertomeu2021using--><!--anchor:section:abstract-->的確切標籤未從摘要確認，dreamy 據灰色來源記為 8-K 4.02，未經查核）、變數設定與演算法不同。勘誤後的實際績效與 Walker 等的批評，本輪都未能核對。 |
| Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract-->：集成學習勝過 logistic | Perols (2011) <!--ref:perols2011financial--><!--anchor:section:abstract-->：六種方法中 logistic 與 SVM 相對較好 | **可調和（條件性差異）**。Perols (2011) <!--ref:perols2011financial--><!--anchor:section:abstract--> 比較的演算法集合不含 RUSBoost，且在變動誤判成本與盛行率下評估；Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract-->用排序型指標。方法排序依評估設定而變，正是 Perols (2011) <!--ref:perols2011financial--><!--anchor:section:abstract--> 的論點。 |
| Purda 與 Skillicorn (2015) <!--ref:purda2015accounting--><!--anchor:section:abstract-->、Hoberg 與 Lewis (2017) <!--ref:hoberg2017fraudulent--><!--anchor:section:abstract-->、Brown 等 (2020) <!--ref:brown2020what--><!--anchor:section:abstract-->：文字在樣本外預測舞弊，最多提升 59% | Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract-->：法說會文字相對公開公司資訊無可偵測的排序增益（95% CI −0.05 至 0.11），且多來自 SPAC | **未解決（flagged），且對本研究是重要的反面證據**。差異可能來自文字類型、樣本大小、基準定義與標籤組成；Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract-->的信賴區間寬，也與中等增益相容。這組矛盾直接關係到「讀到的內容」能否勝過「公司類型」基準。 |
| Yue 等 (2026) <!--ref:yue2026frauddebate--><!--anchor:section:abstract-->：FraudDebate 0.806 > XGBoost 0.738（dreamy 數字）；Wang 等 (2026) <!--ref:wang2026umar--><!--anchor:section:abstract-->：UMAR 0.782 勝過所有基準 | Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:abstract-->：LLM 只略勝 logistic；Waffo Dzuyo 等 (2026) <!--ref:waffodzuyo2026benchmarking--><!--anchor:section:abstract-->：公司隔離下 zero-shot LLM 約 0.50（dreamy 數字） | **部分可調和**。前兩篇是時間內、多 agent 框架；後兩篇是 zero-shot 或公司隔離。設計不同，數字不可直接比較；但型態一致指向「增益依評估設計而定」。Yue 等 (2026) <!--ref:yue2026frauddebate--><!--anchor:section:abstract-->與 Waffo Dzuyo 等 (2026) <!--ref:waffodzuyo2026benchmarking--><!--anchor:section:abstract-->的數字未經核對。 |
| Yue 等 (2026) <!--ref:yue2026frauddebate--><!--anchor:section:abstract-->、Wang 等 (2026) <!--ref:wang2026umar--><!--anchor:section:abstract-->：時間內回測中 LLM 框架勝過基準 | Li 等 (2025) <!--ref:li2025deepfund--><!--anchor:section:abstract-->：只用截止後資料時旗艦 LLM 淨虧損；Karger 等 (2025) <!--ref:karger2025forecastbench--><!--anchor:section:abstract-->：前瞻預測中專家勝過最佳 LLM | **領域不同（insufficient overlap）**。後兩篇不是舞弊研究，只作為「回測 vs 前瞻」落差的旁證，不構成直接矛盾。 |
| （記憶假說的預期）時間內的 LLM 表現應被記憶推高，越接近截止日越差 | Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:5-->：逐年舞弊偵測表現在近年沒有下降；表格輸入下公司名探針 ≤ 0.05 | **對記憶假說的反面證據，未解決**。可能解讀：表格輸入下記憶難以被觸發；或記憶效應在該資料上不大。作者自承不能斷定沒有污染。 |
| Zavitsanos 等 (2021) <!--ref:zavitsanos2021financial--><!--anchor:section:abstract-->：評估需處理揭露時滯 | Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract-->、Yue 等 (2026) <!--ref:yue2026frauddebate--><!--anchor:section:abstract-->：時間序切分 | **未解決（flagged）**。摘要層級無法確認後兩篇的切分是否處理了揭露時滯。 |

#### Cross-Paper Tension Inventory (#262)

```yaml
cross_paper_tensions:
  - pair_id: CP-001
    paper_a: "bao2020detecting"
    paper_b: "bertomeu2021using"
    candidate_basis: "opposite finding direction"
    overlap_topic: "原始會計數字能否有效偵測舞弊／錯報"
    a_finding: "原始會計數字＋集成學習大幅勝過 Dechow logistic 模型（有 2022 勘誤）"
    a_evidence_pointer: "T5_bibliography.md #4 Key Findings（Crossref 摘要）與補充（勘誤解讀據 dreamy）"
    b_finding: "會計變數單獨偵測錯報效果差，需與審計與市場變數合用"
    b_evidence_pointer: "T5_bibliography.md #5 Key Findings（WebSearch 摘要片段）"
    pair_assessment: "contradiction"
    resolution_status: "flagged_unresolved"
    scholar_confirmation: "pending"
  - pair_id: CP-002
    paper_a: "bao2020detecting"
    paper_b: "perols2011financial"
    candidate_basis: "opposite finding direction"
    overlap_topic: "哪類演算法較適合舞弊偵測"
    a_finding: "集成學習（RUSBoost）勝過 logistic"
    a_evidence_pointer: "T5_bibliography.md #4 Key Findings"
    b_finding: "六種方法中 logistic 與 SVM 相對較好"
    b_evidence_pointer: "T5_bibliography.md #3 Key Findings"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶2"
    scholar_confirmation: "pending"
  - pair_id: CP-003
    paper_a: "brown2020what"
    paper_b: "efe2026earnings"
    candidate_basis: "opposite finding direction"
    overlap_topic: "文字對舞弊／重編預測的增量"
    a_finding: "10-K 主題變數樣本外偵測率最多提升 59%"
    a_evidence_pointer: "T5_bibliography.md #8 Key Findings（Crossref 摘要）"
    b_finding: "法說會文字相對公開公司資訊無可偵測排序增益（CI −0.05 至 0.11），多來自 SPAC"
    b_evidence_pointer: "T5_bibliography.md #13 Key Findings（arXiv 摘要）"
    pair_assessment: "contradiction"
    resolution_status: "flagged_unresolved"
    scholar_confirmation: "pending"
  - pair_id: CP-004
    paper_a: "hoberg2017fraudulent"
    paper_b: "efe2026earnings"
    candidate_basis: "opposite finding direction"
    overlap_topic: "揭露文字能否在樣本外預測舞弊"
    a_finding: "異常 MD&A 文字可在樣本外預測舞弊"
    a_evidence_pointer: "T5_bibliography.md #7 Key Findings"
    b_finding: "文字相對公開資訊無可偵測增益"
    b_evidence_pointer: "T5_bibliography.md #13 Key Findings"
    pair_assessment: "conditional_difference"
    resolution_status: "flagged_unresolved"
    scholar_confirmation: "pending"
  - pair_id: CP-005
    paper_a: "yue2026frauddebate"
    paper_b: "sugiura2026edinet"
    candidate_basis: "opposite finding direction"
    overlap_topic: "LLM 是否明顯勝過傳統基準"
    a_finding: "完整框架 AUC 0.806 > XGBoost 0.738 > F-score LR 0.690（dreamy 數字，未核對）"
    a_evidence_pointer: "T5_bibliography.md #9 Key Findings（數字據 dreamy 回顧）"
    b_finding: "最先進 LLM 在舞弊偵測上只比 logistic 略好"
    b_evidence_pointer: "T5_bibliography.md #11 Key Findings（arXiv 摘要）"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶4"
    scholar_confirmation: "pending"
  - pair_id: CP-006
    paper_a: "wang2026umar"
    paper_b: "waffodzuyo2026benchmarking"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "LLM 舞弊偵測在不同切分下的表現"
    a_finding: "時間序切分下 AUROC 0.782，勝過單一 LLM 基準"
    a_evidence_pointer: "T5_bibliography.md #10 Key Findings（arXiv 摘要）"
    b_finding: "隨機切分過度樂觀；公司隔離下 zero-shot LLM 約 0.50（dreamy 數字，未核對）"
    b_evidence_pointer: "T5_bibliography.md #12 Key Findings（摘要＋dreamy 數字）"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶4"
    scholar_confirmation: "pending"
  - pair_id: CP-007
    paper_a: "yue2026frauddebate"
    paper_b: "li2025deepfund"
    candidate_basis: "agent-noted cross-cluster"
    overlap_topic: "時間內回測 vs 截止後評估的 LLM 金融表現"
    a_finding: "時間內測試中 LLM 框架勝過基準"
    a_evidence_pointer: "T5_bibliography.md #9 Key Findings"
    b_finding: "只用截止後資料時旗艦 LLM 淨交易虧損；回測因時間旅行而過度樂觀"
    b_evidence_pointer: "T5_bibliography.md #20 Key Findings"
    pair_assessment: "insufficient_overlap"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"
  - pair_id: CP-008
    paper_a: "zavitsanos2021financial"
    paper_b: "bao2020detecting"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "錯報偵測的時間切分是否處理揭露時滯"
    a_finding: "評估需考慮錯報往往很久才被發現；評估流程顯著影響表現"
    a_evidence_pointer: "T5_bibliography.md #17 Key Findings（arXiv 摘要）"
    b_finding: "時間序切分（測試年度據 dreamy 記為 2003–2008）"
    b_evidence_pointer: "T5_bibliography.md #4 Methodology"
    pair_assessment: "conditional_difference"
    resolution_status: "flagged_unresolved"
    scholar_confirmation: "pending"
  - pair_id: CP-009
    paper_a: "karpoff2017proxies"
    paper_b: "brown2020what"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "舞弊標籤的資料庫選擇"
    a_finding: "實證結果因資料庫而異，各資料庫有四項影響推論的特性"
    a_evidence_pointer: "T5_bibliography.md #14 Key Findings"
    b_finding: "同時以 AAER 與重編／10-K/A 故意違規作標籤"
    b_evidence_pointer: "T5_bibliography.md #8 Relevance"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Key Themes > Theme D, ¶2"
    scholar_confirmation: "pending"
  - pair_id: CP-010
    paper_a: "dyck2024pervasive"
    paper_b: "barton2024importance"
    candidate_basis: "shared RQ subtopic"
    overlap_topic: "被觀察到的舞弊只是發生的一部分"
    a_finding: "正常時期約只有三分之一的舞弊被發現"
    a_evidence_pointer: "T5_bibliography.md #15 Key Findings"
    b_finding: "重編只反映被發現的錯報，應分開發生與偵測機率"
    b_evidence_pointer: "T5_bibliography.md #16 Key Findings"
    pair_assessment: "no_material_conflict"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"
  - pair_id: CP-011
    paper_a: "roberts2024cutoff"
    paper_b: "karger2025forecastbench"
    candidate_basis: "shared RQ subtopic"
    overlap_topic: "以截止日或答案未知為界的去污染評估"
    a_finding: "截止前通過率與熱門度、發布日期相關，構成污染證據"
    a_evidence_pointer: "T5_bibliography.md #18 Key Findings"
    b_finding: "只用提交時答案未知的題目；專家勝過最佳 LLM"
    b_evidence_pointer: "T5_bibliography.md #19 Key Findings"
    pair_assessment: "no_material_conflict"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"
  - pair_id: CP-012
    paper_a: "efe2026earnings"
    paper_b: "sugiura2026edinet"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "LLM 在舞弊／重編任務上是否認得公司"
    a_finding: "LLM 在 66% 遮蔽逐字稿中說出股票代號，模型發布晚於重編"
    a_evidence_pointer: "T5_bibliography.md #13 Key Findings"
    b_finding: "表格輸入下公司名準確率 ≤ 0.05；逐年表現近年未下降"
    b_evidence_pointer: "T3_bibliography.md #7 主要發現（sections：§5）——跨主題紀錄"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Key Themes > Theme C, ¶4"
    scholar_confirmation: "pending"
```

**Coverage Note**：20 papers in corpus（另 2 筆跨主題來源未納入配對）；12 candidate pairs considered（basis：shared RQ subtopic／shared construct／opposite finding direction／agent-noted cross-cluster；沒有引用網絡資料，未使用 bibliographic coupling；沒有 scholar flag）。This is a **scoped advisory scan, not complete pairwise contradiction detection** — cross-neighborhood pairs not surfaced here may exist and are not claimed absent（例如 Beneish (1999) <!--ref:beneish1999detection--><!--anchor:section:abstract--> 與 Dechow 等 (2011) <!--ref:dechow2011predicting--><!--anchor:section:abstract--> 的基準在不同標籤上的相對表現、Dyck 等 (2024) <!--ref:dyck2024pervasive--><!--anchor:section:abstract--> 的未發現舞弊比例對 Yue 等 (2026) <!--ref:yue2026frauddebate--><!--anchor:section:abstract--> 結果的影響，未逐一評估）。涉及 dreamy 數字的配對（CP-001、CP-005、CP-006、CP-008）證據強度較低。Scholar confirms each `resolution_pointer` and may flag additional cross-pairs.

### Knowledge Gaps

1. **在本次檢索範圍內，未見在訓練截止日後才揭露的舞弊或重編案例上評估 LLM 的研究**（Temporal／Empirical）。本主題收錄的 LLM 舞弊研究，測試年度都早於近期模型的截止日（Yue 等 (2026) <!--ref:yue2026frauddebate--><!--anchor:section:abstract-->、Wang 等 (2026) <!--ref:wang2026umar--><!--anchor:section:abstract-->）、使用公司隔離而非時間隔離（Waffo Dzuyo 等 (2026) <!--ref:waffodzuyo2026benchmarking--><!--anchor:section:abstract-->），或模型發布晚於標籤事件（Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract-->）。前瞻與即時評估的設計（Karger 等 (2025) <!--ref:karger2025forecastbench--><!--anchor:section:abstract-->、Li 等 (2025) <!--ref:li2025deepfund--><!--anchor:section:abstract-->）在本次檢索範圍內未見應用於舞弊。
2. **在本次檢索範圍內，未見同時報告「只給公司名稱或公司類型」基準的 LLM 舞弊研究**（Methodological）。最接近的是 Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract--> 的「公開公司資訊」基準。含意：LLM 讀年報的分數中，有多少只是公司層級先驗，沒有既有估計。
3. **8-K Item 4.02 作為舞弊標籤的專門研究**（Empirical）。T5 書目只找到間接文獻（Karpoff 等 (2017) <!--ref:karpoff2017proxies--><!--anchor:section:abstract-->、Barton 等 (2024) <!--ref:barton2024importance--><!--anchor:section:abstract-->）；書目另記錄一篇區分錯誤與違規的重編研究因上限排除，本綜整不引用。
4. **滾動式 benchmark 的標籤成熟問題**（Theoretical／Methodological）。ForecastBench 的題目在提交後即可解答（Karger 等 (2025) <!--ref:karger2025forecastbench--><!--anchor:section:abstract-->），但舞弊標籤需要數年才成熟（Zavitsanos 等 (2021) <!--ref:zavitsanos2021financial--><!--anchor:section:abstract-->、Dyck 等 (2024) <!--ref:dyck2024pervasive--><!--anchor:section:abstract-->）；在本次檢索範圍內未見處理「標籤成熟期 vs 模型截止日」兩者衝突的評估設計。
5. **非美國樣本**（Geographic）：除 EDINET-Bench（Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:abstract-->，日本）外，T5 書目中有明示地區者皆為美國；中國、台灣、日本的 LLM 舞弊文獻未系統檢索。
6. **Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract--> 的勘誤與後續爭議**（Empirical，查核層級）：Walker 等的批評本輪未能逐篇查核，勘誤後的實際績效未讀；以 Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract-->的資料為基準的研究（包括 Yue 等 (2026) <!--ref:yue2026frauddebate--><!--anchor:section:abstract-->）的比較基礎因此不確定。

### Evidence Convergence Map

```
Strong:      [          ] （無；全部只讀摘要，關鍵 LLM 數字多取自 dreamy、未核對）
Moderate:    [======    ] Theme D 標籤是測量問題（4 支持／3 部分，Levels III–IV）
Moderate:    [======    ] Theme A 傳統基準中等、排序依設定（5 支持／1 部分，Level IV）
Moderate:    [=====     ] Theme E 前瞻／時間外設計（5 支持／2 部分；舞弊領域未見應用）
Emerging:    [====      ] Theme C LLM 增益依評估設計（3 支持／2 相反／2 部分；多為 2026 預印本與 dreamy 數字）
Contested:   [====      ] Theme B 文字增量（3 支持／1 反證／3 部分）
Gap:         [          ] 截止後揭露舞弊上的 LLM 評估；名稱／類型基準（0 篇，在本次檢索範圍內）
```

### Theoretical Integration

本主題的文獻可以整合成一個「評估效度的三層結構」，每一層都可能讓 LLM 舞弊偵測的 AUC 偏離「從年報讀出的真實訊號」。

1. **標籤層**（Theme D）：AUC 衡量的是對「被發現並被某資料庫記錄的舞弊」的排序，而非對「舞弊」本身（Karpoff 等 (2017) <!--ref:karpoff2017proxies--><!--anchor:section:abstract-->、Dyck 等 (2024) <!--ref:dyck2024pervasive--><!--anchor:section:abstract-->、Barton 等 (2024) <!--ref:barton2024importance--><!--anchor:section:abstract-->）。標籤雜訊通常壓低所有方法的 AUC，且對越新的樣本越嚴重（Zavitsanos 等 (2021) <!--ref:zavitsanos2021financial--><!--anchor:section:abstract-->）。
2. **切分層**（Theme C、E）：隨機切分、公司重疊、時間內測試都會讓結果偏樂觀（Waffo Dzuyo 等 (2026) <!--ref:waffodzuyo2026benchmarking--><!--anchor:section:abstract-->、Li 等 (2025) <!--ref:li2025deepfund--><!--anchor:section:abstract-->）；對 LLM 而言，最強的洩漏來源是「模型已知結果」，只有截止後揭露的樣本能排除（Roberts 等 (2024) <!--ref:roberts2024cutoff--><!--anchor:section:abstract-->、Karger 等 (2025) <!--ref:karger2025forecastbench--><!--anchor:section:abstract-->）。
3. **基準層**（Theme A、B）：「勝過傳統模型」需要說明是勝過哪個基準。傳統會計模型（Beneish (1999) <!--ref:beneish1999detection--><!--anchor:section:abstract-->、Dechow 等 (2011) <!--ref:dechow2011predicting--><!--anchor:section:abstract-->）是一種基準；「公開公司資訊」（Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract-->）是更強、也更接近「公司類型先驗」的基準。後者在本次檢索範圍內很少被用在 LLM 研究中。

在這個結構下，本主題的研究問題可以重述為：在標籤層的雜訊下（無法消除，只能說明），在切分層排除記憶（截止後揭露），並在基準層同時對照傳統模型與公司類型先驗，LLM 讀年報是否仍有增益。Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:5--> 的逐年結果與 Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract--> 的無增益結果，是這個問題的兩個重要的反面參照：前者提示記憶在某些設定下可能不是主要驅動，後者提示文字的增量可能被公司層級資訊吸收。這是本綜整的整合性推論。

### 與本研究實驗的對照

（以下為本研究自身實驗，取自 `results/research_topics.md`，**不是文獻**，不作為已確立的發現。）

- **時間外 4.02 樣本：事實卡 0.77、紅旗總數卡 0.76、整份 10-K 0.76；只給名稱 0.69；扣掉名稱先驗的殘差約 0.65**：對應 Gap 1 與 Gap 2——在本次檢索範圍內未見同時具備「截止後揭露」與「名稱／類型基準」的研究。殘差的設計回應了 Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract--> 的提醒（公司層級資訊可能吸收大部分訊號）。
- **參考：Dechow 等 (2011) <!--ref:dechow2011predicting--><!--anchor:section:abstract--> 的 F-score 0.63、Beneish (1999) <!--ref:beneish1999detection--><!--anchor:section:abstract--> 的 M-score 0.66**：與 Yue 等 (2026) <!--ref:yue2026frauddebate--><!--anchor:section:abstract--> 表 3 的 F-score LR 0.690（數字取自 dreamy 文獻回顧，未重新核對）樣本與標籤不同，不可直接比較；Perols (2011) <!--ref:perols2011financial--><!--anchor:section:abstract--> 也提醒配對設計的盛行率與母體不同。
- **AAER 擴大樣本 43 對：L3 卡 0.71、殘差 0.51**：AAER 與 4.02 是不同標籤（Karpoff 等 (2017) <!--ref:karpoff2017proxies--><!--anchor:section:abstract-->），兩組結果需分開報告；殘差較低可能有多種解釋（樣本、標籤、知名度），依 Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract-->，不同樣本間的差距不能直接歸於記憶。
- **時間外樣本的對照公司可能含未被發現的舞弊**：依 Dyck 等 (2024) <!--ref:dyck2024pervasive--><!--anchor:section:abstract--> 與 Zavitsanos 等 (2021) <!--ref:zavitsanos2021financial--><!--anchor:section:abstract-->，這會壓低所有方法的 AUC，且對最新樣本最嚴重。
- **第十輪：在 Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract--> 標準資料上復刻 FraudDebate-Agent 的 LLM 基準（進行中）**：該資料的樣本年度早於所有 LLM 截止日，屬時間內對照；Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract-->的勘誤（dreamy 解讀）與 Walker 等的爭議未經核對，是復刻時需要先釐清的比較基礎（Gap 6）。

### Synthesis Limitations

- **閱讀深度**：20 篇全部只讀摘要（部分為 WebSearch 摘要片段），方法弱點未評估。
- **dreamy 數字**：Yue 等 (2026) <!--ref:yue2026frauddebate--><!--anchor:section:abstract-->的 AUC、Waffo Dzuyo 等 (2026) <!--ref:waffodzuyo2026benchmarking--><!--anchor:section:abstract-->的 AUC、Wang 等 (2026) <!--ref:wang2026umar--><!--anchor:section:abstract-->的標籤與測試正例數、Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract-->的測試年度與勘誤解讀、Bertomeu 等 (2021) <!--ref:bertomeu2021using--><!--anchor:section:abstract-->的標籤來源，都取自 dreamy 文獻回顧，未重新核對；本檔已逐處標註。Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract-->、Zavitsanos 等 (2021) <!--ref:zavitsanos2021financial--><!--anchor:section:abstract-->、Bertomeu 等 (2021) <!--ref:bertomeu2021using--><!--anchor:section:abstract-->的樣本地區也依 dreamy 記載。
- **跨主題來源**：Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:5-->的逐年表現與名稱探針依 T3 書目的章節閱讀紀錄（§5）；T5 書目對同一篇只讀摘要，並記為「dreamy 回顧另記載」。兩份書目對同一篇的等級不同（T5：IV；T3：VI；T1：III），本檔依 T5。Roberts 等 (2024) <!--ref:roberts2024cutoff--><!--anchor:section:abstract-->在 T5 為 ICLR 2024、Level III、Tier 1，在 T1（key 不同）為預印本、Level IV、Tier 2。
- **錨點**：所有本主題來源錨點為 `section:abstract`；只有 Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:5-->的逐年與探針結果使用 `section:5`（依 T3 紀錄）。
- **出版狀態**：Wang 等 (2026) <!--ref:wang2026umar--><!--anchor:section:abstract-->、Waffo Dzuyo 等 (2026) <!--ref:waffodzuyo2026benchmarking--><!--anchor:section:abstract-->、Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract-->為 2026 年預印本，未經完整同儕審查；Dyck 等 (2024) <!--ref:dyck2024pervasive--><!--anchor:section:abstract-->有更正、Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract-->有勘誤，內容都未讀。
- **檢索限制**：只檢索英文；Walker（Econ Journal Watch）對 Bao 等 (2020) <!--ref:bao2020detecting--><!--anchor:section:abstract-->的批評、T5 書目因上限排除的文獻、以及已撤回的 LLM 財報分析預印本，都未納入。
- **矛盾掃描**：Cross-Paper Tension Inventory 是有範圍的建議性掃描，不是完整的兩兩比較。
- 本檔未經任何外部審查或稽核步驟。
