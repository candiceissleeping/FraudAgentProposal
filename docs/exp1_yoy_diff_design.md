# 實驗一設計：跨年度 10-K 差異能否提升 LLM 舞弊偵測準確度

> 狀態：設計稿（尚未執行）。執行前須把本檔、樣本清單與 prompt 一起提交 git，作為預先登錄。

## 0. 研究問題

**H1：給 LLM「當年 10-K + 與前一年 10-K 的差異」，判斷舞弊的準確度高於只給「當年 10-K」。**

- 資料：EDGAR-CORPUS 10-K（本 repo 既有的抓取流程）
- 舞弊標籤：SEC AAER（Accounting and Auditing Enforcement Releases）
  （題目寫的 "AEER" 這裡當作 AAER 處理）

---

## 1. AuditAgent（ICAIF 2025）的做法

論文：Bai et al., *AuditAgent: Expert-Guided Multi-Agent Reasoning for Cross-Document Fraudulent Evidence Discovery*, arXiv:2510.00156。

> 註：此環境連不到 arXiv 全文，以下內容來自摘要與檢索到的內文片段；數字與細節正式引用前要再對照原文。

| 面向 | AuditAgent 的做法 |
|---|---|
| 任務 | **已知是舞弊的案件**中，在多年度財報裡找出**證據鏈的位置**（evidence localization），不是判斷「有沒有舞弊」 |
| 資料 | FinFraud-Real：中國證監會（CSRC）約 1,570 件裁罰案件；每件 = 舞弊摘要 + 涉案的多年度財報 + 裁罰書認定的事實（作為證據標註） |
| 方法 | ① 以變分貝氏模型，從歷史裁罰資料學「主體層級」舞弊風險先驗（例如哪類公司、哪個科目較常出事）；② 稀疏 + 稠密混合檢索，在長篇、多份報告中找段落；③ 多個專門 agent 依審計知識串聯跨年度證據 |
| 基底模型 | DeepSeek-R1 |
| 比較對象 | 單一 LLM（輸入過長時截斷）；通用 agent 框架 Search-o1 |
| 指標 | 只看 **Recall**：問題層級 R_I、證據層級 R_E，並提出多對多 recall（一案可有多種舞弊類型）；作者明說不重視 precision |
| 結果 | Recall 與可解釋性都優於通用 agent；單一 LLM 的 recall 隨輸入長度增加明顯下降 |

## 2. 適不適合直接拿來做這個實驗？——**不適合當主要設計，但有三點可以借用**

### 不適合的原因

1. **它沒有負樣本，量不出「偵測準確度」。**
   FinFraud-Real 全部是已裁罰公司，評的是「證據找到多少」（recall）。
   我們的問題是「加了年度差異，**分辨**舞弊與非舞弊公司是否更準」，必須要有對照公司，並看 AUC / accuracy。
   只看 recall 的系統，把每家公司都判成舞弊也能拿高分。
2. **混入太多其他變因，無法歸因到「年度差異」。**
   AuditAgent 同時改了風險先驗、檢索、多 agent。就算它比 baseline 好，也分不出是哪一部分的功勞。
   我們要回答的是單一因素的效果，所以需要**只改輸入、其他都固定**的消融設計。
3. **風險先驗會洩漏答案。** 以產業、規模等學到的舞弊先驗，本身就是一個預測器；
   放進來後，「LLM + 年度差異」的增益會和先驗的增益混在一起。
4. **資料不同。** 中國 A 股年報 + 證監會裁罰書，與 10-K + AAER 的格式、揭露規範都不同；
   它的程式與資料無法直接搬來。

### 可以借用的部分

| 借用 | 在本實驗中的用法 |
|---|---|
| 用裁罰文件標註**哪幾年**、**哪個科目**有問題 | 用 AAER 標出舞弊年度（firm-year 標籤）與舞弊類型（營收、存貨、費用、準備…） |
| 跨年度串聯證據的想法 | 就是本實驗的處理組：把 t 年與 t-1 年 10-K 的差異餵給 LLM |
| 問題層級 recall（R_I） | 原規劃為次要指標；但 Bao et al. 的標籤沒有舞弊科目，**本實驗無法計算**，需另取 CFRM 完整資料 |
| 「輸入越長、單一 LLM 越差」的發現 | 設計時要控制 token 長度，否則「多給一年」可能因為變長而變差，或因為資訊變多而變好，兩者混在一起 |

---

## 3. 本實驗設計

### 3.1 分析單位與樣本

- **單位：firm-year。** 預測時點 = 公司申報 t 年 10-K 的當下，只能用 t 年與 t-1 年的 10-K。
- **舞弊組（positive）**：AAER 事件中**第一個不實陳述的會計年度**作為 t。
  - 理由：t-1 年仍乾淨、t 年開始造假，年度差異最可能出現訊號；若 t-1 也已造假，差異裡看不到轉折。
  - 次要分析：所有不實陳述年度都納入。
- **標籤來源（已決定）**：Bao et al. (2020, JAR) 公開的 `AAER_firm_year.csv`
  （github.com/JarFraud/FraudDetection，固定在 commit `2d10bc6`）。
  - 來自 Berkeley CFRM 的 AAER 資料庫，加上作者手動補到 2018 年底（AAER #4012）。
  - **檔案本身就有 CIK**，舞弊組不需要 gvkey → CIK 對應；gvkey 只出現在他們的 Compustat 特徵檔，本實驗不用。
  - 共 1,746 個不實陳述 firm-years、729 個 AAER 事件、716 家公司。
- **標籤規則**（`experiment/yoy/labels.py`）：
  - 剔除低報盈餘（`UNDERSTATEMENT = 1`）的事件：不是本實驗要偵測的類型
  - t 必須在 1994–2020（t-1 也要在 EDGAR-CORPUS 1993–2020 內）
  - 剔除 t-1 已被同公司另一個 AAER 認定不實的事件（沒有乾淨的前一年）
  - 結果：**476 個候選舞弊 firm-years**（剔除：年份不在資料集 221、低報 30、前一年已不實 2）
- **對照組（negative）**：同會計年度 t、同 SIC 二位碼、**從未**出現在任何 AAER 的公司，1:1 配對；
  同產業內選「LLM 會讀到的章節總字數」最接近者（取對數差），每家對照公司只用一次。
  - 原本想用總資產配對，但 Compustat 只能用 gvkey 連結，沒有公開的 gvkey → CIK 對照表；
    改用文字長度配對，同時也讓兩組的 LLM 輸入長度相近，避免「文件長短」成為線索。
  - SIC 來自 SEC `data.sec.gov` submissions API（`experiment/yoy/sic.py`），是公司**目前**的 SIC，不是當年的。
- **可用 10-K 的條件**（兩組相同，`experiment/yoy/build_sample.py`）：
  - t 與 t-1 的 10-K 在 EDGAR-CORPUS 都存在，且 Item 7（MD&A）與財報各 ≥ 2,000 字元；
    財報 = Item 8，舊式 10-K 則用 Item 14 + 15
    （本 repo 已遇過 GE、BellSouth 的 10-K 為空，年報以引用方式併入）
  - 同一公司同一年有多份時取最長的一份
  - EDGAR-CORPUS 的 `year` 是會計年度（見 README），t 與 t-1 都以會計年度對齊
  - 每一步剔除數量寫入 `results/exp1_attrition.md`
- **樣本數**：
  - 先做**試點 30 組配對**（60 firm-years，以固定 seed `20261017` 從全部配對中抽出），用來檢查流程、估計各組分數的相關性與變異。
  - 主實驗目標 **200 組配對**（400 firm-years）。以試點結果做 bootstrap 檢定力分析後再定案；
    要偵測 ΔAUC ≈ 0.05 通常需要數百個正樣本，前兩輪的 10 家完全不夠。

### 3.2 實驗組別（同一個 LLM、同一個 prompt，只改輸入）

| 組別 | 輸入內容 | 用來回答 |
|---|---|---|
| **A0 基準** | t 年 10-K | 純 LLM 判斷舞弊 |
| **A1 長度對照** | t 年 10-K + t-1 年 10-K **原文**（截到與 A2 差異段落相同 token 數） | 「多給文字」本身有沒有幫助 |
| **A2 處理組** | t 年 10-K + **結構化年度差異**（t vs t-1） | 本實驗主要假設 |
| A3 僅差異（次要） | 只有年度差異 | 差異本身含多少訊號 |
| B0 非 LLM 參考 | ① 年度文字差異度 = 1 − 各章節年度相似度平均（Brown & Tucker 2011；Cohen, Malloy & Nguyen 2020 "Lazy Prices"）；② 既有關鍵字分數。兩者都不需訓練，避免在小樣本上擬合 | LLM 是否比便宜的文字差異指標更有用 |

**關鍵**：A2 和 A1 的輸入長度相同。
- A2 − A0：加入年度資訊的總效果
- A2 − A1：在相同長度下，「整理成差異」比「直接給兩年原文」多出的效果
- 若 A2 > A0 但 A2 ≈ A1，結論是「多一年資料有用」，而不是「差異 feature 有用」

**t 年 10-K 的內容在 A0、A1、A2 完全相同**：固定取 Item 1A、3、7、7A、8（含附註）、9、9A，
每章節依固定上限截斷，總長固定（例如 24k tokens）。A1/A2 額外的部分另有固定上限（例如 8k tokens）。

### 3.3 年度差異怎麼產生（不用 LLM，可重現）

對每個章節（1A 風險因子、3 法律訴訟、7 MD&A、8 財報附註、9/9A 會計師與內控）：

1. 切成段落，去除頁首、目錄等雜訊。
2. 用 TF-IDF cosine 將 t 年段落與 t-1 年段落配對：
   - 相似度 ≥ 0.95：視為未變，不輸出
   - 0.5–0.95：**修改**，輸出前後兩版（附註中的會計政策、收入認列、估計變更多半落在這裡）
   - t 年找不到配對：**新增**
   - t-1 年找不到配對：**刪除**（被移除的風險揭露也可能是訊號）
3. 每章節開頭列出整體相似度，例如 `Item 7 與前一年相似度 0.62（新增 14 段、刪除 9 段、修改 21 段）`。
4. 依「章節優先順序 → 變動幅度」排序，截到固定 token 上限。排序規則事先寫死，不針對個別公司調整。

（延伸，非本實驗範圍：2009 年後可用 XBRL / SEC Financial Statement Data Sets 加入數字的年增率。）

### 3.4 LLM 設定

- 同一模型（`claude-opus-5-5`，effort `high`）跑所有組別，經 Message Batches API 送出（`experiment/yoy/run_llm.py`）。
  此模型不接受 temperature 等取樣參數，因此每份資料包**重跑 3 次取平均**，並可用來估計重跑變異。
- 不設定拒答時的備援模型：每份文件都必須由同一模型評分；拒答或格式錯誤記錄為無效並在報告中列出。
- System prompt 說明樣本中約一半是舞弊公司（四組相同）；否則 Accuracy@50 沒有意義。AUC 不受此影響。
- 建議至少兩個模型（一個閉源、一個開源）檢查結論是否穩定。
- 輸出固定 JSON：
  ```json
  {"fraud_probability": 0-100,
   "fraud_types": ["revenue", "expense", "reserve", ...],
   "evidence": [{"section": "Item 7", "source": "current|prior|diff", "quote": "..."}]}
  ```
- 所有 prompt 在執行前提交 git。

### 3.5 防止洩漏（前兩輪最大的問題）

第二輪揭盲時 10 家公司全部被認出，代表 LLM 可能靠「記得這家公司出過事」而不是靠閱讀內容。本實驗必須：

1. **遮蔽**：公司名、子公司、人名、品牌、會計師事務所名稱；年份改成相對年份（Year T、Year T-1）。
   遮蔽清單由 EDGAR 公司名稱 + NER 自動產生，再人工抽查。
2. **身分測試**：用 A1 資料包（含兩年原文，最容易認出）另外問模型「這是哪一家公司、哪一年？」。
   猜測中出現該公司 EDGAR 名稱（或其特徵字）即算認出；報告認出比例，並在**排除含被認出公司的配對**後重算主要指標。
3. **時間**：只用 t 與 t-1 的原始 10-K，不用之後的申報；舞弊組的 t 年 10-K 必須早於 AAER 或公開揭露日期。
4. **評分者不知道標籤**：LLM 評分與標籤對應在跑完之後才合併。

### 3.6 評估指標

| 層級 | 指標 | 說明 |
|---|---|---|
| **主要** | **ROC-AUC 差（A2 − A0）** | 配對 bootstrap（以配對組為單位重抽 2,000 次）或 DeLong 檢定，報 95% CI |
| 主要 | ROC-AUC 差（A2 − A1） | 判斷增益來自「差異」還是「多一年文字」 |
| 次要 | 配對內正確率 | 每組配對中舞弊公司分數較高的比例；組別間用 McNemar 檢定 |
| 次要 | Accuracy / F1（門檻 50）、PR-AUC、Brier | Accuracy 受門檻與 1:1 比例影響，只作參考；另以 1:4 對照比例報 PR-AUC，較接近真實盛行率 |
| 可解釋性 | 問題層級 recall（借自 AuditAgent 的 R_I） | 標籤缺舞弊科目，本實驗不計算；`fraud_types` 只做描述性統計 |
| 機制 | 證據來源比例 | A2 判對的案例中，有多少引用來自 `diff` |

**判定規則（事先登錄）**：
- H1 成立：A2 − A0 的 AUC 差 95% CI 不含 0，**且** A2 − A1 ≥ 0。
- 若 A2 > A0 但 A2 < A1：年度資訊有用，但差異的整理方式不好，應改進差異產生方法。
- 若排除被認出的樣本後效果消失：結果來自記憶，不採信。

### 3.7 次要分析

- 章節消融：A2 只放單一章節的差異（1A、3、7、8、9A），看增益來自哪裡。
- 依舞弊類型分組（營收、費用、準備…）。
- SOX 前後（2002 年前沒有 Item 9A，內控訊號天生較少）。

---

## 4. 執行步驟

1. 取得 AAER 標籤 → 索引 EDGAR-CORPUS → 查 SIC → 產生配對樣本 `config/exp1_sample.json`，記錄剔除流程（見下方指令）。
2. 抓 t 與 t-1 的 10-K（沿用 `experiment/edgar_risk/fetch.py`，需支援同一家公司多個年度）。
3. 實作差異產生器與遮蔽，輸出各組的資料包。
4. **提交本檔、樣本清單、prompt、判定規則到 git（預先登錄）。**
5. 試點 30 組 → 檢查流程與檢定力 → 決定主實驗樣本數。
6. 主實驗：A0 / A1 / A2 / A3 / B0 全部跑完後才合併標籤計算指標。

### 產生樣本的指令

```bash
python -m experiment.yoy.labels                  # 下載 AAER 標籤並列出候選數
python -m experiment.yoy.index_corpus            # 索引 1993–2020 所有 10-K 的章節長度（約 30 GB 串流，不存全文）
SEC_USER_AGENT="Name email" python -m experiment.yoy.sic   # 需能連到 data.sec.gov
python -m experiment.yoy.build_sample            # → config/exp1_sample.json、results/exp1_attrition.md
python -m experiment.yoy.fetch_sample --pilot    # 抓試點公司 t 與 t-1 的 10-K 全文
python -m experiment.yoy.packets --pilot         # 遮蔽 + 產生 A0–A3 資料包
python -m experiment.yoy.run_llm submit --run pilot    # 需 Anthropic API 金鑰
python -m experiment.yoy.run_llm collect --run pilot
python -m experiment.yoy.evaluate --run pilot    # → results/exp1_pilot/report.md
```

## 5. 已知限制

- AAER 只涵蓋**被 SEC 抓到**的舞弊；對照組中可能有未被發現的舞弊公司，會使所有組別的 AUC 被低估，但不影響組別間比較的方向。
- 第一年造假的公司，舞弊可能本來就不會寫進 10-K；差異只能捕捉「揭露方式的改變」。
- EDGAR-CORPUS 只有文字，沒有結構化財務數字；數字差異要另外接 XBRL。
- 遮蔽無法做到完美，身分測試是必要的補強。
- 對照組沒有依規模配對（見 3.1），以文字長度代替；SIC 是目前的產業代碼，少數公司可能已改變產業。
