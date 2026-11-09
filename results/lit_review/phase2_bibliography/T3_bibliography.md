# 主題 3 文獻書目：匿名化與再識別的取捨（Phase 2，bibliography_agent）

> 主題：財務資訊要粗到什麼程度，LLM 才認不出公司、又不失判斷力？「有名單的封閉式辨識」與「沒有名單的開放式辨識」該用哪個當標準？（`results/research_topics.md` 主題 3）
> 角色與範圍：ARS deep-research `bibliography_agent`，只做 Phase 2（檢索、篩選、註解書目）。本檔**不做綜整、不下結論、不起草**；綜整留給 Phase 3。
> 檢索規範：`results/lit_review/protocol.md`（整合性回顧；收錄標準與查核規則照該檔）。
> 機器可讀清單：`T3_sources.json`（同目錄）。

## Annotated Bibliography

### Search Strategy

PRE-SCREENED FROM USER CORPUS:
- Adapter: <unspecified>
  Adapter origin not declared; user-written adapter should populate obtained_via per v3.6.4 schema recommendation.
  （語料為 markdown 文獻回顧 `dreamy_round10_lit_review.md` v3，不是 Material Passport 的 `literature_corpus[]`；依本任務指示視為已預篩語料，以相同標準重篩。）
- Snapshot date: <unspecified>
  Snapshot date not declared; reproducibility is reduced. Adapter should populate obtained_at per v3.6.4 schema recommendation.（文件本身標示版本日期 2026-11-03。）
- Total entries scanned: 35（參考文獻清單逐條計數；Walker、Gow、Klein 分開計；題庫型 4 篇分開計）
- Pre-screening result:
  - Included: 6 entries
    citation_keys:
      - efe2026earnings
      - engelberg2025neutering
      - glasserman2024lookahead
      - lopezlira2025memorization
      - sugiura2026edinet
      - wu2025anonymization
  - Excluded by inclusion / exclusion criteria: 29 entries
    citation_keys:
      - bao2020（及 2022 勘誤）、barton2024、bertomeu2021、bhattacharya2024、brown2020、dai2026、ergun2025、kirkos2024、nie2025、yu2026、yue2026、wang2026umar、waffodzuyo2026、zavitsanos2021、walker2021_2022、gow2022、klein2023、ohartman_github、auditfraudbench2026、auditbench2025、finverbench、vera8b：舞弊預測模型或題庫，未處理匿名化或再識別（屬主題 5）
      - gao_lap、sarkar2024、levy2026、ludwig2026、he2025chronobert、kelly2026：前視偏誤與時點一致模型，未涉及匿名化或身分辨識（屬主題 1）
      - kim2024：arXiv v3 已撤回（2025-02-20），數字不可引用；方法僅作背景，不收錄
- Note: presence in corpus does not imply inclusion; same criteria applied to corpus and external sources.

uncovered_topics（語料未涵蓋、改以外部檢索補足）：LLM 對一般文字的推論式再識別；開放世界 vs 封閉世界的辨識評估；文字匿名化的效用—風險指標與 benchmark；統計揭露控制（SDC）與 k-匿名等經典概念。→ Step 2 case A：外部檢索限縮於上述主題。

**Coverage Distribution Advisory**:

DISTRIBUTIONAL_SKEW_ADVISORY:
- Dimension: time distribution
- Concentration: 2020 年代 = 16/20 (80%)
- Advisory: This is a coverage-distribution signal, not a defect. Consider whether the RQ warrants broader periods, sites, methods, or venue families.
- Search response: no expansion; protocol 規定以 2020 年後為主。2020 年前的 4 篇（Sweeney 2002、Narayanan & Shmatikov 2008、Shlomo 2010、Rocher et al. 2019）已標為 seminal。另：2025–2026 年 = 12/20 (60%)，未達門檻。

DISTRIBUTIONAL_SKEW_ADVISORY:
- Dimension: geographic distribution（以研究資料的地區為準；只計有明確標示者）
- Concentration: 美國資料 = 7/9 (78%)（美國：Engelberg、Lopez-Lira、Wu、Glasserman & Lin、Greve & Sablica、Efe、Krčo；非美國：Sugiura（日本 EDINET）、Pilán（歐洲人權法院判決）。其餘 11 篇為線上平台、合成資料或多國人口，未計入）
- Advisory: This is a coverage-distribution signal, not a defect. Consider whether the RQ warrants broader periods, sites, methods, or venue families.
- Search response: 本研究樣本是美國 AAER／8-K 4.02，美國集中與 RQ 相符；但台灣、中國、歐洲財務文字的再識別研究未檢索（見 Search Limitations）。建議 Phase 3 若需要，補檢索字串：`"anonymized" AND ("annual report" OR "financial statements") AND (LLM) AND (China OR Taiwan OR Europe)`。

DISTRIBUTIONAL_SKEW_ADVISORY:
- Dimension: methodological distribution
- Concentration: 計算／實證量化研究 = 17/20 (85%)（其餘：資料集 1 篇（Pilán 2022 TAB）、理論模型 1 篇（Sweeney 2002）、方法回顧 1 篇（Shlomo 2010））
- Advisory: This is a coverage-distribution signal, not a defect. Consider whether the RQ warrants broader periods, sites, methods, or venue families.
- Search response: no expansion；RQ 本身是量化的取捨曲線問題。法規與倫理面（如 GDPR Recital 26 的「合理可能」標準）只在 Thees et al. 中順帶出現，若 Phase 3 需要政策面，可補檢索 `"anonymisation" AND "GDPR" AND "reasonably likely" AND "LLM"`。

（venue tier：預印本 8/20 (40%)；同一會議系列最多為 ICLR 3/20 (15%)。未觸發。）

**Databases**: arXiv API（export.arxiv.org）、Crossref API（api.crossref.org，`query.bibliographic` 檢索與 `/works/{DOI}` 查核）、WebSearch（standard 模式）、dreamy 第十輪文獻回顧（預篩語料）。OpenAlex 與 Semantic Scholar 依 protocol 不使用（無 API 金鑰）；ARS Step 4.5 的 S2 去重依降級規則略過，改以題名與識別碼人工去重。

**Keywords**（主要詞＋同義詞）:
- 匿名化：anonymization／anonymisation、de-identification、entity masking、entity neutering、text sanitization、named entity swapping、coarsening／generalization、topcoding
- 再識別：re-identification、de-anonymization、deanonymization、linkage attack、identity disclosure、firm identification、authorship attribution
- 對象：financial text、earnings call、10-K／annual report、financial statements、tabular／microdata
- 評估：privacy-utility trade-off、disclosure risk、information loss、closed-world／open-world、open-set、k-anonymity、quasi-identifiers、statistical disclosure control
- 模型：large language models、LLM agents、look-ahead bias、memorization

**Boolean**（實際執行的查詢；arXiv 以 `abs:`／`ti:` 欄位）:
- arXiv（23 組）：
  1. `abs:"re-identification" AND abs:"large language models" AND abs:anonymized`
  2. `abs:"entity masking" AND abs:financial`
  3. `abs:anonymization AND abs:"look-ahead bias"`
  4. `abs:"beyond memorization" AND abs:privacy`
  5. `abs:anonymization AND abs:LLM AND abs:"financial"`
  6. `abs:"de-anonymization" AND abs:"language models"`
  7. `abs:"text anonymization" AND abs:"utility"`
  8. `abs:"financial statements" AND abs:anonymized AND abs:identify`
  9. `abs:"look-ahead bias" AND abs:"company" AND abs:identif*`
  10. `abs:memorization AND abs:"earnings" AND abs:anonym*`
  11. `abs:"re-identification" AND abs:"tabular" AND abs:"language model"`
  12. `ti:"Memorization Problem"`
  13. `abs:"open-world" AND abs:"authorship attribution" AND abs:"closed-world"`
  14. `abs:"statistical disclosure control" AND abs:"large language model"`
  15. `abs:"linkage attack" AND abs:"large language models"`
  16. `abs:"quasi-identifiers" AND abs:"LLM" AND abs:"re-identification"`
  17. `abs:"generalization" AND abs:"quasi-identifiers" AND abs:"utility" AND abs:"disclosure risk"`
  18. `abs:"re-identification" AND abs:"large language models" AND abs:"tabular"`
  19. `abs:"de-anonymize" AND abs:"LLM"`
  20. `abs:"open-set" AND abs:"re-identification" AND abs:"text"`
  21. `abs:"Large-scale online deanonymization"`
  22. `abs:anonymization AND abs:"earnings call"`
  23. `abs:"masked" AND abs:"company" AND abs:"identify" AND abs:"LLM" AND abs:"financial"`
  - 另以 `id_list` 查核 27 個 arXiv ID 的題名、作者、journal_ref 與摘要。
- Crossref `query.bibliographic`（15 組，每組取前 3–8 筆）："k-anonymity: a model for protecting privacy Sweeney"；"Robust de-anonymization of large sparse datasets"；"Estimating the success of re-identifications in incomplete datasets using generative models Rocher"；"disclosure risk anonymized documents machine learning re-identification attack Manzanares-Salor"；"Entity Neutering Engelberg Manela Mullins Vulicevic"；"Assessing Look-Ahead Bias in Stock Return Predictions Generated by GPT Sentiment Analysis"；"R-U confidentiality map disclosure risk data utility Duncan"；"Look-Ahead Bias in Financial Forecasts Generated by Large Language Models"；"The Text Anonymization Benchmark (TAB) …"；"Adaptive Text Anonymization … Loiseau"；"Large Language Models are Advanced Anonymizers Staab"；"Beyond Memorization: Violating Privacy Via Inference with Large Language Models"；"Large-scale online deanonymization with LLMs Lermen"；"EDINET-Bench …"；"disclosure risk utility trade-off coarsening generalization statistical disclosure control microdata"。另以 `/works/{DOI}` 查核 13 個 DOI。
- WebSearch（13 次，standard）："LLM identify company from anonymized financial statements re-identification look-ahead bias"；"anonymized 10-K firm identification large language model memorization accounting research"；"LLM recognize firm from financial ratios numbers only anonymized fundamentals "look-ahead" paper 2025"；"Summoning the Oracle to Slay It …"；""Large-scale online deanonymization with LLMs" arXiv"；"closed-world vs open-world evaluation de-anonymization attack candidate set "none of the above" LLM"；Staab 2024 ICLR 查核；Staab 2025 ICLR 查核；Lermen USENIX 查核（2 次）；"Entity Neutering" 摘要；Duncan & Stokes R-U map；Narayanan & Shmatikov 摘要。

**Date Range**: 2020–2026 為主；k-匿名、連結攻擊、統計揭露控制的奠基文獻不限年份（標示 seminal）。

**Last Searched**: 2026-11-09

**Inclusion Criteria**（照 protocol）: 直接回應主題 3（匿名化／粗化與再識別的取捨、再識別的評估方式、效用損失）；期刊與會議論文（Tier 1）、預印本（Tier 2，標示）；DOI、arXiv ID 或穩定網址可查核，題名、作者、年份相符；英文為主；2020 年後為主，經典不限。

**Exclusion Criteria**: 只順帶提到匿名化；部落格、新聞、行銷文章、二手摘要網站；掠奪性期刊；查不到存在證據者（灰色地帶＝剔除）；已撤回者；取不到摘要、無法註解者；超出每主題 20 篇上限時，與 RQ 距離較遠者。

### PRISMA Flow

（數字為依查詢紀錄的人工計數；WebSearch 的「紀錄」指結果中不重複的學術文獻，而非連結數。）

```
Records identified (total): 179
|-- arXiv API: 76（23 組查詢實際取回的條目）
|-- Crossref API: 52（15 組查詢取回的條目）
|-- WebSearch: 16（13 次查詢、約 130 個連結中可辨識的不重複學術文獻）
+-- dreamy 預篩語料: 35

Duplicates removed: 30（arXiv 查詢間重複 13；Crossref 與 arXiv／語料重複 5；WebSearch 與其他來源重複 9；語料與 arXiv 重複 3）
Records screened (title/abstract): 149
Records excluded: 119（主題不符，如交易 agent、資安 SIEM、影像再識別、魚類再識別、加密貨幣詐騙；或屬主題 1、5）
Full-text / eligibility assessed: 30（讀摘要，4 篇另讀指定章節）
Eligibility excluded (with reasons): 10
  - Kim, Muhn & Nikolaev (2024, arXiv 2407.17866)：已撤回
  - Duncan & Stokes (2004, CHANCE, DOI 10.1080/09332480.2004.10554908)：Crossref 確認存在，但取不到摘要（出版商主機無法連線），無法註解；R-U 取捨概念由 Shlomo (2010) 代表
  - Jiang, Liu, Cho & Oermann (2026, arXiv 2602.08997)：相關（準識別子相關性、HIPAA Safe Harbor），但為立場論文；為維持同儕審查比例與 20 篇上限而排除
  - Morris et al. (2024, DIRI, arXiv 2410.17035)：臨床病歷，與 Wen & Li、Lermen 重疊
  - Yang, Zhu & Gurevych (2024/ACL 2025, arXiv 2407.11770)：效用—隱私框架，與 Staab 2025、Loiseau 2026 重疊
  - Pilán et al. (2024, arXiv 2412.12928)：以泛化（generalization）取代遮蔽，相關；但未查到出版處，且與 TAB 同團隊重疊
  - Patsakis & Lykousas (2023, arXiv 2303.12429)：早期示範，已被 Staab 2024 等取代
  - Deußer et al. (2025, DSAA survey)：綜述，內容與已收錄的原始研究重疊
  - Li, Wang & Ma (2026, EMNLP, FinCAD)：以解碼方式抑制記憶，不是匿名化（偏主題 1）
  - Benhenda (2026, Look-Ahead-Bench, arXiv 2601.13770)：前視偏誤 benchmark，未涉及身分辨識（偏主題 1）
Studies included in review: 20（語料 6、外部 14）
```

### Sources (N = 20)

方法弱點的標記方式：依 `review_criteria_framework.md` §2.1（實證研究）六項：研究假設清楚度、變數操作定義、內部效度、外部效度、統計報告完整度、結論保守度。`checked: found` = 讀過的章節中發現該項有弱點；`checked: none found` = 讀過、未發現；`not checked` = 未檢查。讀取範圍為 `abstract_only` 者一律寫 `not assessed`。標為 `sections` 的 4 篇，是透過 WebFetch 讀取 arXiv HTML 版的指定章節（含原文短句），列於各條。

---

#### 子主題 A：金融文字與財務報表的匿名化及公司再識別

1. **Engelberg, J., Manela, A., Mullins, W., & Vulicevic, L. (2025). *Entity neutering* [Working paper]. SSRN. https://doi.org/10.2139/ssrn.5182756**
   - 識別碼：DOI 10.2139/ssrn.5182756（Crossref 確認，posted-content）；讀取：abstract_only（摘要經 WebSearch 取得的研討會公告與作者網頁版本）；來自 dreamy 語料
   - 相關性：目前最直接的「強遮蔽」方法：反覆遮蔽並改寫，直到另一個 LLM 認不出公司，正是主題 3「要粗到什麼程度」的一個操作化答案。
   - 主要發現：兩個摘要版本數字不同：一版為超過 50 萬篇新聞、遮蔽後辨識率降到隨機水準；另一版為 100 萬篇、約 90% 的文章認不出公司或時期，這些文章的原文與遮蔽後情緒判斷 90% 一致、報酬預測力相近，差距可當前視偏誤的上限。已延伸到 MD&A 與法說會。
   - 方法：LLM agent 迭代「遮蔽實體＋改寫」，以獨立 LLM 的辨識結果當停止條件（以辨識失敗為準的對抗式匿名化）。
   - 證據等級：III（同一文本原文 vs 遮蔽版的對照）；Tier 2（工作論文）
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：本研究的匿名化階梯（dreamy 9c、9d、9f；peaceful E2）是「固定粗化等級、事後測辨識」；Engelberg 的做法是「以辨識失敗為停止條件」。兩個摘要版本的數字差異，Phase 3 引用前需核對 SSRN 最新版。

2. **Lopez-Lira, A., Tang, Y., & Zhu, M. (2025). *The memorization problem: Can we trust LLMs' economic forecasts?* (arXiv:2504.14765). arXiv. https://arxiv.org/abs/2504.14765**
   - 識別碼：arXiv 2504.14765（arXiv API 確認，v2）；讀取：abstract_only；來自 dreamy 語料
   - 相關性：證明「遮蔽」擋不住再識別，是主題 3 的反面基準。
   - 主要發現：LLM 記得訓練期內的經濟與金融數值；要求「遵守歷史界線」的指示無法阻止回想；遮蔽失敗，因為 LLM 能從很少的上下文重建實體與日期；截止後沒有回想；記憶延伸到 embeddings。摘要並主張：只要模型看過實現值，反事實預測能力無法識別。
   - 方法：數值回想測試、遮蔽後法說會的公司與時期重建、截止日前後比較。
   - 證據等級：III；Tier 2
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：支持 dreamy 9f「AAER 樣本上連類別計數都能部分配對」這類結果的方向；但其證據來自法說會文字，本研究的事實卡是結構化數字，可比性要在 Phase 3 討論。

3. **Wu, K., Yang, B., Ying, Z., & Zhou, D. (2025). *Anonymization and information loss* (arXiv:2511.15364). arXiv. https://arxiv.org/abs/2511.15364**
   - 識別碼：arXiv 2511.15364（arXiv API 確認，v2）；讀取：abstract_only；來自 dreamy 語料
   - 相關性：直接量化取捨的另一端：匿名化的資訊損失。
   - 主要發現：預測 S&P 信評調降時，原文顯著優於匿名化文字；差距不能用前視偏誤解釋，而是遮掉數字與人物（agent）實體造成資訊損失，並改變 LLM 對其餘文字的解讀；跨模型、任務、文字類型都存在。提出不需結果資料的「anonymization gap」指標。
   - 方法：原文 vs 匿名化文字的對照預測，拆解偏誤移除與資訊損失。
   - 證據等級：III；Tier 2
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：本研究「類別計數卡 3/54 可配對、AUC 仍 0.77」是資訊損失未顯現的例子；Wu 等的「遮數字損失最大」與此不同，差異可能來自任務或輸入形式，Phase 3 需比對。anonymization gap 可作為本研究不需標籤的效用指標候選。

4. **Glasserman, P., & Lin, C. (2024). Assessing look-ahead bias in stock return predictions generated by GPT sentiment analysis. *The Journal of Financial Data Science, 6*(1), 25–42. https://doi.org/10.3905/jfds.2023.1.143**
   - 識別碼：DOI 10.3905/jfds.2023.1.143（Crossref 確認；線上版 2023-12，卷期 6(1)）；讀取：abstract_only（SSRN 版摘要，DOI 10.2139/ssrn.4586726）；來自 dreamy 語料
   - 相關性：把「認出公司」的影響分成前視偏誤與「分心效應」兩種，說明匿名化不只是減少記憶。
   - 主要發現：時間內，匿名化標題的交易策略反而較好，表示分心效應大於前視偏誤；大公司更明顯；時間外前視偏誤不是問題，但分心仍可能存在。
   - 方法：新聞標題原文 vs 移除公司識別資訊的版本，比較情緒交易策略績效。
   - 證據等級：III；Tier 1
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：本研究的匿名化階梯若 AUC 不降甚至上升，需同時考慮分心效應；「大公司效果更強」對應第八輪「AAER 公司比時間外小公司容易被認出」的知名度分層。

5. **Greve, J., & Sablica, L. (2025). *Named entity swapping for metadata anonymization in a text corpus* (arXiv:2505.21128). arXiv. https://arxiv.org/abs/2505.21128**
   - 識別碼：arXiv 2505.21128（arXiv API 確認）；讀取：sections（§2.3、§2.4.3、§2.5、§3、§3.1.2–3.1.4、§3.2.1–3.2.2、§4、附錄 A）；外部新增
   - 相關性：唯一一篇把**統計揭露控制（SDC）的 data swapping** 用在「防止 LLM 認出法說會公司」的研究，並明確以風險—效用兩個指標校準匿名化程度，最接近主題 3 想畫的曲線。
   - 主要發現：在語意相近的文字片段之間交換具名實體，使實體組合無法唯一對應到公司。§3.2.2：GPT-4o 認出公司（以 ticker 作答）的準確率由交換前 0.888 降到 0.564，Gemini 2.5 Flash 由 0.934 降到 0.602（30 次重跑平均，McNemar 檢定顯著）。風險以樣本唯一值為基礎（式 2.16），效用以交換前後 embedding 對數概似比衡量（式 2.19）。
   - 方法：embedding 分群加權的實體交換、決策理論式的參數校準；以 2018 Q1 資訊業 35 份法說會（1,819 個片段）示範。
   - 證據等級：III（交換前後對照）；Tier 2
   - Method weaknesses（empirical；read: §2.3、§2.4.3、§2.5、§3、§3.2.1–3.2.2、§4、附錄 A）
     - checked: found: 外部效度、變數操作定義、內部效度 | checked: none found: 統計報告完整度、結論保守度 | not checked: 研究假設清楚度
     - 樣本只有單一產業、單一季度的 35 份法說會；推論到其他產業或長篇文件時會失準。[author-acknowledged, quote: "the aim of our work is mostly demonstrative"（§3.1.4）]
     - 交換只能套用在少數片段；若大部分片段未被交換，整份文件層級的辨識率會高於片段層級的結果。[author-acknowledged, quote: "the swapping can only be performed for a small fraction of the text chunks present in the data"（§4）]
     - NER 漏掉產品名等準識別子（例："iX"）；漏網的準識別子越多，交換後的辨識率越被低估其風險。[author-acknowledged, section: §4]
     - 辨識測試要求模型只回一個 ticker、沒有「不知道」選項，也沒有候選名單；在只有一個產業的小樣本中，猜測與真正辨識無法區分，會讓交換後 0.56–0.60 的準確率難以解讀為風險。[reader-inferred]
     - 正文說預測「公司名稱」，附錄 A 的提示詞要求回 ticker，兩者不一致。[reader-inferred；依 §3.2.2 與附錄 A]
   - 與本研究的關聯：提供「風險指標＋效用指標＋可調參數」的完整框架，可直接借來把本研究的 L1→L3、完整事實卡→類別計數卡→紅旗總數卡畫成風險—效用曲線。

6. **Efe, A., Sapra, S., & Ahmed, B. (2026). *Do earnings calls help predict financial restatements? Evaluating text beyond public firm information* (arXiv:2611.01123). arXiv. https://arxiv.org/abs/2611.01123**
   - 識別碼：arXiv 2611.01123（arXiv API 確認）；讀取：sections（摘要、§4、§5、Limitations、附錄 A「Prompts and firm recognition」）；來自 dreamy 語料
   - 相關性：與本研究同一類標籤（重編），並在**開放式**作答下量化遮蔽後的公司辨識率。
   - 主要發現：遮蔽公司名、ticker、人名後，Qwen3.5-27B 以完全相符的 ticker 認出 66% 的逐字稿（327 份中 217 份）；重編組 57%、對照組 71%；寬鬆標準 75%；連大寫字、數字、年份都移除的強遮蔽仍有 63%。作者確認 217 份正確者的輸入中都沒有 ticker。
   - 方法：109 份重編前法說會＋218 份配對對照；請模型直接說出公司與 ticker（開放式）。
   - 證據等級：IV（配對病例對照）；Tier 2
   - Method weaknesses（empirical；read: 摘要、§4、§5、Limitations、附錄 A）
     - checked: found: 外部效度、內部效度、變數操作定義 | checked: none found: 統計報告完整度、結論保守度 | not checked: 研究假設清楚度
     - 重編樣本少且只限有公開法說會的公司；推論到 AAER 或無法說會的小公司時會失準。[author-acknowledged, quote: "Restatements are relatively rare, and only some restating firms appear in public earnings-call corpora"（Limitations）]
     - 模型在重編之後才發布，可能已知結果；辨識率與分數同時受記憶影響。[author-acknowledged, quote: "it may also know their outcomes"（§5）]
     - 以完全相符的 ticker 計分，公司改過 ticker 時會漏算，使辨識率偏低。[author-acknowledged, section: 附錄 A]
     - 辨識檢驗只用 Qwen3.5 9B／27B 一個模型家族；換成知識較多的商用模型，辨識率可能更高。[reader-inferred]
   - 與本研究的關聯：「對照組比重編組更常被認出」與本研究第八輪的知名度觀察一致，可作為「辨識跟著知名度、不跟著標籤」的對照證據；其開放式作答方式與 peaceful E2 評分時的情境（沒有名單）相同。

7. **Sugiura, I., Ishida, T., Makino, T., Tazuke, C., Nakagawa, T., Nakago, K., & Ha, D. (2026). EDINET-Bench: Evaluating LLMs on complex financial tasks using Japanese financial statements. *International Conference on Learning Representations (ICLR 2026)*. arXiv:2506.08762. https://arxiv.org/abs/2506.08762**
   - 識別碼：arXiv 2506.08762（arXiv API 確認，comment: "Accepted to ICLR 2026"）；讀取：sections（§4.1、§5「Company name prediction」與「Year-wise performance analysis」、附錄 A 圖 7、表 8）；來自 dreamy 語料
   - 相關性：唯一找到的「只給財務報表表格、開放式猜公司名」的探針，最接近本研究的事實卡情境。
   - 主要發現：輸入資產負債表、現金流量表、損益表與摘要表（不含公司名與確切年份），開放式作答；7 個模型的公司名準確率都 ≤ 0.05（Claude 3.5 Sonnet 0.050、GPT-4o 0.000）。逐年舞弊偵測表現在近年沒有下降。作者承認不能據此斷定沒有污染。
   - 方法：公開 benchmark；GPT-4o 當評審判定名稱是否相符。
   - 證據等級：VI（描述性 benchmark 探針）；Tier 1（ICLR 2026，依 arXiv comment）
   - Method weaknesses（empirical；read: §4.1、§5、附錄 A、表 8）
     - checked: found: 內部效度、外部效度、變數操作定義 | checked: none found: 結論保守度 | not checked: 研究假設清楚度、統計報告完整度
     - 公司名探針只測「表格 → 名稱」，未測「表格 → 舞弊結果」；名稱猜不出不代表結果沒被記住。[author-acknowledged, quote: "we cannot conclude that the dataset is entirely free of contamination"（§5）]
     - 只用表格輸入，未測文字段落；含文字的完整報告辨識率可能較高。[reader-inferred]
     - 由 GPT-4o 判定名稱相符；日文公司名的變體多時，判定標準會影響準確率。[reader-inferred]
   - 與本研究的關聯：開放式、只給數字表格時辨識率極低，與 peaceful E2「評分時（無名單）全部 unknown」方向一致；與 dreamy 9c「完整事實卡給名單可配對 34/54」形成封閉式 vs 開放式的對比。

---

#### 子主題 B：LLM 對匿名文字的推論式再識別（開放世界與封閉世界）

8. **Staab, R., Vero, M., Balunović, M., & Vechev, M. (2024). Beyond memorization: Violating privacy via inference with large language models. *International Conference on Learning Representations (ICLR 2024)*. arXiv:2310.07298. https://arxiv.org/abs/2310.07298**
   - 識別碼：arXiv 2310.07298（arXiv API 確認）；ICLR 2024 由 WebSearch 結果（iclr.cc 海報頁、作者 GitHub）確認；讀取：abstract_only；外部新增
   - 相關性：把隱私風險從「記憶訓練資料」擴大到「推論時從文字推出屬性」，與本研究「認出公司」可來自推論（產業、規模組合）而非記憶的區分直接相關。
   - 主要發現：真實 Reddit 個人檔案上，LLM 推論位置、收入、性別等屬性 top-1 最高 85%、top-3 95%，成本約人工的 1/100、時間 1/240；文字匿名化與模型對齊目前都擋不住。
   - 方法：建構含人工標註屬性的資料集，比較多個 LLM 與人工標註者。
   - 證據等級：VI；Tier 1
   - Method weaknesses: not assessed (read scope: abstract_only)
   - 與本研究的關聯：本研究的類型卡（L1–L3）在給名單時仍可配對 20–26/28，可解讀為「屬性組合推論」而非記憶；Phase 3 可據此區分兩條再識別路徑。

9. **Lermen, S., Paleka, D., Swanson, J., Aerni, M., Carlini, N., & Tramèr, F. (2026). *Large-scale online deanonymization with LLMs* (arXiv:2602.16800). arXiv. https://arxiv.org/abs/2602.16800**
   - 識別碼：arXiv 2602.16800（arXiv API 確認，v2；journal_ref 列 USENIX Security 26，但未找到 usenix.org 頁面，故仍標 Tier 2）；讀取：sections（摘要、§1、§2.1、§3.1、§3.3、§4.3、§6.3、§6.4、§8）；外部新增
   - 相關性：明確區分**封閉世界**（給定候選資料庫）與網路代理的開放情境，並把「真實對象可能不在候選中」納入指標，正是主題 3「有名單 vs 沒名單」的評估方法論。
   - 主要發現：封閉世界中攻擊者應在沒有相符候選時棄權（§3.1）；precision 以「非棄權的猜測」為分母（§3.3）；§6.4 引入「查詢有對應」的先驗 π，區分可對應與不可對應查詢的錯誤率，並指出 π 只影響 precision；即使 π = 0.0001，90% precision 下 recall 仍至少 9%。HN→LinkedIn 封閉世界 54.2% recall @90% precision，經典 Narayanan 方法約 0.1%（表 1）；網路代理在 HN 認出 338 人中 226 人（90% precision），另有 86 次棄權（§2.1）。
   - 方法：LLM 特徵抽取 → embedding 語意檢索候選 → 推理驗證（ESRC 框架）；三個有真實身分的資料集。
   - 證據等級：III（與經典基準的對照）；Tier 2
   - Method weaknesses（empirical；read: §2.1、§3.1、§3.3、§4.3、§6.3–6.4、§8）
     - checked: found: 外部效度、內部效度、統計報告完整度 | checked: none found: 變數操作定義 | not checked: 研究假設清楚度、結論保守度
     - 有真實身分連結的檔案本身較容易被認出，會高估 recall。[author-acknowledged, quote: "might overestimate an attack's recall"（§3.3）]
     - 多數封閉世界實驗假設每個查詢都有對應（先驗 100%）；真實情境先驗低時 precision 會下降。[author-acknowledged, section: §3.1、§6.4]
     - 網路代理實驗樣本小，且只有單點 precision／recall，無法畫取捨曲線。[author-acknowledged, quote: "a single point estimate of precision and recall rather than a tunable tradeoff"（§2.1）]
     - 不能排除模型已記得 Reddit／HN 內容。[author-acknowledged, section: §8「Are our evaluations contaminated?」]
   - 與本研究的關聯：本研究「給名單配對」相當於先驗 100% 的封閉世界，「評分時無名單」接近開放世界；Lermen 的 π 與棄權設計，可用來把兩種辨識標準放在同一個 precision—recall 框架下比較。

10. **Wen, J., & Li, T. (2026). *AgentDoxx: Agentic re-identification of anonymized text with web search* (arXiv:2610.05586). arXiv. https://arxiv.org/abs/2610.05586**
    - 識別碼：arXiv 2610.05586（arXiv API 確認）；讀取：abstract_only；外部新增
    - 相關性：把再識別拆成「參數記憶」與「檢索」兩個來源，並測試實體遮蔽與「隱私指示」的效果。
    - 主要發現：822 份以真實人物公開資訊合成的訪談稿、15 種模型設定；不開搜尋時開放權重模型可認出 15–28%；目標一旦出現在檢索結果中，辨識成功率超過 88%；實體遮蔽後，分層樣本中 85.3% 至少有一個攻擊者成功；隱私指示只壓住「說出名字」，不壓住檢索——準確率 0% 的設定仍在最多 62% 的稿件中檢索到對象。
    - 方法：有真實身分的合成評估集；分析搜尋軌跡以區分檢索型與參數型辨識。
    - 證據等級：III；Tier 2
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：「準確率 0% 但仍檢索到對象」說明「模型說 unknown」不等於「沒認出」，對 peaceful E2 評分時全部 "unknown" 的解讀是重要提醒；也與主題 2（提示禁止 vs 結構性移除）相關。

11. **Thees, O., Müller, R., & Templ, M. (2026). Agentic AI-powered re-identification: An emerging, scalable threat to mobility microdata privacy. In *Privacy in Statistical Databases (PSD 2026)* (Lecture Notes in Computer Science, pp. 319–332). Springer. https://doi.org/10.1007/978-3-032-37883-5_21**
    - 識別碼：DOI 10.1007/978-3-032-37883-5_21（Crossref 確認）；arXiv 2606.27936；讀取：abstract_only（arXiv 摘要）；外部新增
    - 相關性：從統計揭露控制（SDC）社群的角度，說明 LLM agent 改變了「事實上匿名」（de facto anonymity）的前提。
    - 主要發現：LLM agent 從時空座標與公開來源自動再識別，25 個可再識別者中認出 18 人（72%），全部 43 案為 41.9%；作者主張這使 GDPR Recital 26「合理可能」的標準更容易成立，每個目標成本只需數分鐘與數美元。
    - 方法：可行性研究；模擬位置點錨定在真實住址與工作地址。
    - 證據等級：VI（可行性研究）；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：SDC 傳統假設「攻擊者需要人工、規模有限」；本研究的 LLM 情境同樣打破這個假設，粗化等級的設定需以 LLM 攻擊者為基準，而非人工攻擊者。

---

#### 子主題 C：文字匿名化的效用—風險取捨與再識別風險指標

12. **Pilán, I., Lison, P., Øvrelid, L., Papadopoulou, A., Sánchez, D., & Batet, M. (2022). The Text Anonymization Benchmark (TAB): A dedicated corpus and evaluation framework for text anonymization. *Computational Linguistics, 48*(4), 1053–1101. https://doi.org/10.1162/coli_a_00458**
    - 識別碼：DOI 10.1162/coli_a_00458（Crossref 確認）；arXiv 2202.00443；讀取：abstract_only；外部新增
    - 相關性：文字匿名化評估的標準資料集，把「隱私保護」與「效用保留」分開定義指標。
    - 主要發現：1,268 份歐洲人權法院判決，標註語意類別、識別子類型（直接／準識別子）、機密屬性與共指關係；超越只偵測預定類別的傳統去識別化，明確標出「為隱藏身分必須遮蔽」的片段；提出同時衡量隱私與效用的指標。
    - 方法：語料建構與標註；以基準模型示範指標。
    - 證據等級：VI（資料集與基準評估）；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：「直接識別子 vs 準識別子」的區分可用來分類本研究事實卡的欄位（公司名＝直接；產業、規模、事件類別＝準識別子）。

13. **Manzanares-Salor, B., Sánchez, D., & Lison, P. (2024). Evaluating the disclosure risk of anonymized documents via a machine learning-based re-identification attack. *Data Mining and Knowledge Discovery, 38*(6), 4040–4075. https://doi.org/10.1007/s10618-024-01066-3**
    - 識別碼：DOI 10.1007/s10618-024-01066-3（Crossref 確認）；讀取：abstract_only（Crossref 摘要）；外部新增
    - 相關性：主張以「實際再識別攻擊」而非「遮蔽了多少標註詞」來衡量揭露風險，與本研究以 LLM 配對率當風險指標的做法同一思路。
    - 主要發現：常用的 recall 指標（偵測到多少人工標註的識別詞）不是風險指標：需要唯一的標準答案、依賴主觀人工判斷、並把每個詞視為同等重要；改以自動化再識別攻擊（多類別分類，整合攻擊者可取得的背景資料）評估匿名化文件的殘餘風險。
    - 方法：以神經語言模型建構再識別分類器。
    - 證據等級：III；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：本研究「給名單配對」即為多類別分類式的再識別攻擊；此文提供把它正式化為揭露風險指標的依據。

14. **Staab, R., Vero, M., Balunović, M., & Vechev, M. (2025). Language models are advanced anonymizers. *International Conference on Learning Representations (ICLR 2025)*. arXiv:2402.13846. https://arxiv.org/abs/2402.13846**
    - 識別碼：arXiv 2402.13846（arXiv API 確認；arXiv 題名為 "Large language models are advanced anonymizers"）；ICLR 2025 由 WebSearch 結果（proceedings.iclr.cc、iclr.cc 海報頁）確認；讀取：abstract_only；外部新增
    - 相關性：以 LLM 推論攻擊為回饋的「對抗式匿名化」，與 Engelberg 的 entity neutering 同一邏輯，但來自隱私／NLP 社群。
    - 主要發現：提出在對抗式 LLM 推論下評估匿名化的新設定；以 LLM 推論結果引導改寫的匿名化框架，在 13 個 LLM、真實與合成文字上，效用與隱私都優於商用匿名化工具；人類研究（n = 50）偏好 LLM 匿名化的文字。
    - 方法：對抗式迭代匿名化；與基準工具比較。
    - 證據等級：III；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：本研究若要找「剛好認不出」的粗化等級，可借用「以攻擊者推論結果為停止條件」的設計。

15. **Loiseau, G., Sileo, D., Riquet, D., Meyer, M., & Tommasi, M. (2026). Adaptive text anonymization: Learning privacy-utility trade-offs via prompt optimization. In *Findings of the Association for Computational Linguistics: ACL 2026* (pp. 8207–8229). https://doi.org/10.18653/v1/2026.findings-acl.401**
    - 識別碼：DOI 10.18653/v1/2026.findings-acl.401（Crossref 確認）；arXiv 2602.20743；讀取：abstract_only（arXiv 摘要）；外部新增
    - 相關性：把「隱私—效用取捨前緣」（trade-off frontier）當成可依下游任務調整的目標，對應主題 3「資訊量 vs 可辨識度曲線」。
    - 主要發現：適當的取捨隨資料領域、隱私目標與下游用途而變；以任務特定的提示詞最佳化自動產生匿名化指示，在五個資料集上取捨都優於基準，並能找出位於前緣不同位置的新策略；開源模型表現接近大型封閉模型。
    - 方法：提示詞最佳化；跨五個資料集的 benchmark。
    - 證據等級：III；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：支持「沒有通用的最佳粗化等級，要依下游任務（舞弊判斷）來定」；本研究的效用端可直接用舞弊 AUC。

16. **Krčo, N., Yao, Z., Meeus, M., & de Montjoye, Y.-A. (2026). *RAT-Bench: A comprehensive benchmark for text anonymization* (arXiv:2602.12806). arXiv. https://arxiv.org/abs/2602.12806**
    - 識別碼：arXiv 2602.12806（arXiv API 確認）；讀取：abstract_only；外部新增
    - 相關性：以「在母體中的再識別風險」而非「遮掉多少識別子」評估匿名化工具，並處理不同識別子的不等影響。
    - 主要發現：用美國人口統計產生含直接與間接識別子的合成文字；依 LLM 攻擊者能正確推出的屬性，計算在美國母體中的再識別風險；最佳工具在直接識別子寫法不標準、或間接識別子足以再識別時仍不完美；LLM 匿名化工具（含迭代式）取捨較佳但成本較高。
    - 方法：合成資料 benchmark；比較 NER 型與 LLM 型匿名化工具。
    - 證據等級：III；Tier 2
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：本研究的「給 54 家名單配對」是樣本內的封閉式風險；RAT-Bench 的母體層級風險提供另一種基準——同樣的屬性組合在全體上市公司中是否唯一。

---

#### 子主題 D：經典概念——k-匿名、稀疏資料連結攻擊、統計揭露控制（seminal）

17. **Sweeney, L. (2002). k-anonymity: A model for protecting privacy. *International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems, 10*(5), 557–570. https://doi.org/10.1142/S0218488502001648** 〔seminal〕
    - 識別碼：DOI 10.1142/S0218488502001648（Crossref 確認）；讀取：abstract_only（Crossref 摘要）；外部新增
    - 相關性：「粗化到多少才夠」的正式定義：每筆紀錄至少與 k−1 筆無法區分。
    - 主要發現：提出 k-anonymity 保護模型與配套政策；並檢視在符合 k-匿名的釋出上，若不遵守配套政策仍可實現的再識別攻擊；是 Datafly、μ-Argus、k-Similar 等系統的基礎。
    - 方法：形式化模型與政策分析。
    - 證據等級：VII（理論模型）；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：本研究的類別計數卡可用「在樣本或全體上市公司中，有多少家共享同一組類別值」直接計算 k，作為不依賴 LLM 的粗化指標。

18. **Narayanan, A., & Shmatikov, V. (2008). Robust de-anonymization of large sparse datasets. In *2008 IEEE Symposium on Security and Privacy* (pp. 111–125). IEEE. https://doi.org/10.1109/SP.2008.33** 〔seminal〕
    - 識別碼：DOI 10.1109/SP.2008.33（Crossref 確認）；讀取：abstract_only（摘要經 WebSearch 結果取得）；外部新增
    - 相關性：高維稀疏資料的連結攻擊經典；說明少量背景知識即可在擾動過的資料中找到個人。
    - 主要發現：針對高維微觀資料（偏好、推薦、交易紀錄）的統計式去匿名化攻擊；以 Netflix Prize 50 萬名訂戶的匿名評分為例，用 IMDb 當背景知識比對出已知使用者的紀錄；資料被擾動、只釋出子集、或攻擊者背景知識有誤時仍有效。
    - 方法：統計比對攻擊的示範。
    - 證據等級：VI；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：財務事實卡是多欄位的高維紀錄；「少數欄位即可唯一對應」的機制可解釋為何完整事實卡給名單可配對 34/54。Lermen et al. 以此文作為非 LLM 基準（約 0.1% recall）。

19. **Rocher, L., Hendrickx, J. M., & de Montjoye, Y.-A. (2019). Estimating the success of re-identifications in incomplete datasets using generative models. *Nature Communications, 10*, Article 3069. https://doi.org/10.1038/s41467-019-10933-3** 〔seminal〕
    - 識別碼：DOI 10.1038/s41467-019-10933-3（Crossref 確認）；讀取：abstract_only（Crossref 摘要）；外部新增
    - 相關性：以「個體唯一性」估計再識別成功率，即使資料被大量抽樣也適用；是母體層級風險指標的代表。
    - 主要發現：以 copula 生成模型估計特定個人被正確再識別的機率；在 210 個母體上預測個體唯一性的 AUC 為 0.84–0.97；15 個人口屬性即可正確再識別 99.98% 的美國人；大量抽樣的匿名資料也難以符合 GDPR 的匿名標準。
    - 方法：生成式統計模型，在多個母體上驗證。
    - 證據等級：IV（觀察資料上的模型估計）；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：「樣本小不代表安全」——本研究 28 或 54 家的小樣本配對率，不能直接推到全體上市公司；可借其唯一性估計思路，估算一組類別值在全體公司中的唯一程度。

20. **Shlomo, N. (2010). Releasing microdata: Disclosure risk estimation, data masking and assessing utility. *Journal of Privacy and Confidentiality, 2*(1). https://doi.org/10.29012/jpc.v2i1.584** 〔seminal〕
    - 識別碼：DOI 10.29012/jpc.v2i1.584（Crossref 確認）；讀取：abstract_only（Crossref 摘要）；外部新增
    - 相關性：統計揭露控制（SDC）中「揭露風險—資料效用」（R-U）取捨方法的回顧，是主題 3 曲線的統計學傳統。
    - 主要發現：統計機構釋出微觀資料時，保護程度與存取方式的決策應以揭露風險與資料效用的客觀量化指標為依據；回顧揭露風險評估的發展，並說明如何與資料遮蔽（masking）、效用評估整合；以已知母體的普查抽樣示範 R-U 取捨方法。
    - 方法：方法回顧＋普查資料示範。
    - 證據等級：VI（非系統性方法回顧與示範）；Tier 1
    - Method weaknesses: not assessed (read scope: abstract_only)
    - 與本研究的關聯：提供把「粗化等級」當參數、同時畫出風險與效用的標準做法；本研究的匿名化階梯可直接對應 SDC 的 recoding／topcoding 類遮蔽。

### Search Limitations

- **讀取深度**：20 篇中 16 篇只讀摘要（`abstract_only`），方法弱點一律未評。4 篇（Greve & Sablica、Lermen et al.、Efe et al.、Sugiura et al.）讀了指定章節，方式是以 WebFetch 讀 arXiv HTML 版，由工具擷取章節內容與原文短句；未逐字通讀全文，方法弱點只限所列章節。
- **語料數字未重讀全文**：dreamy 語料中標為「全文」的 Lopez-Lira、Wu、Glasserman & Lin，本次只重讀摘要，故標 `abstract_only`；dreamy 引述的細節數字（如 Lopez-Lira 的 Apple、Meta、Microsoft 100%）未在本次讀取範圍內確認，未寫入本檔。
- **Engelberg et al. 的數字有兩個版本**（50 萬篇／隨機水準 vs 100 萬篇／約 90%），SSRN 本站無法連線，Phase 3 引用前需核對最新版。
- **無法連線的主機**：SSRN、tandfonline（Duncan & Stokes 2004 因此取不到摘要而排除）。OpenAlex、Semantic Scholar 依 protocol 不使用，因此沒有引用網絡（被引／引用）追蹤，ARS Step 4.5 的 S2 去重與 `semantic_scholar_unmatched` 訊號未計算。
- **檢索範圍**：英文為主；未檢索 CNKI、J-STAGE、Google Scholar；台灣、中國、歐洲財務文字的再識別研究未涵蓋。arXiv 以 `abs:` 欄位的布林檢索，對用詞不同的文獻（如 "firm fingerprinting"、"entity linking" 用於財報）可能漏檢。
- **缺口（以本次檢索為界）**：未找到以**結構化財務數字（比率、類別計數）**為輸入、系統性改變粗化等級並同時報告辨識率與下游任務效用的研究；最接近的是 EDINET-Bench 的單點表格探針與 Greve & Sablica 的文字實體交換。也未找到財務領域中正式比較封閉式（給名單）與開放式（無名單）辨識的研究；這個區分目前只在一般隱私文獻（Lermen et al.）中出現。
- **後 LLM 拐點預印本（contamination advisory，僅供參考）**：2024 年以後的 arXiv／SSRN 預印本共 8 篇（Engelberg、Lopez-Lira、Wu、Greve & Sablica、Efe、Lermen、Wen & Li、Krčo），依 ARS v3.7.3 規則 `preprint_post_llm_inflection = true`；全部已由 arXiv API 或 Crossref 確認存在且題名相符。
- **期刊／會議比例**：Tier 1 為 12/20（60%），剛好達到 ARS「至少 60% 同儕審查」的門檻；其中 EDINET-Bench（ICLR 2026）只依 arXiv comment 判定，Lermen et al. 的 USENIX Security 26 未獲獨立確認，仍列 Tier 2。
- **計數**：PRISMA 數字依查詢紀錄人工計數，WebSearch 的記錄數為估計值。
