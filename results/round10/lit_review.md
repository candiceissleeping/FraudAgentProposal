# 文獻探討：LLM 財報舞弊偵測可比較的 benchmark 與記憶問題

> 版本：v2（2026-11-03），取代同日 v1。形式：敘事回顧（deep-research `lit-review` 模式：文獻蒐集 → 來源查證 → 綜合 → 反方檢查），**不是**系統性回顧，不宣稱涵蓋全部文獻。
> 檢索：三個主題各一個文獻蒐集 agent（共約 90 次網路搜尋），再由一個查證 agent 獨立重查（約 75 次工具呼叫；可連 export.arxiv.org、api.crossref.org、raw.githubusercontent.com，所以讀到部分 arXiv 全文）。MDPI、HAL、SSRN、NBER 等主機在本環境無法連線。
> 查證規則：灰色地帶一律判為不通過。一個數字只有在原文或摘要明確寫出時才標「已確認」；只出現在部落格、二手表格或沒有標示指標的片段裡的數字，**不得當成 benchmark**。
> 每篇的讀取程度：**全文**＝本文作者或查證 agent 讀過 PDF；**摘要**＝只讀到摘要或出版資訊；**二手**＝只有轉述。
> 工作底稿（不在 repo）：三份主題書目、一份查證表，共 26 項更正，都已併入本文。
> AI 使用聲明：檢索、查證、整理與撰寫由 AI 工具（Claude）協助完成；引用前請研究者核對原文。

## 1. 問題與結論摘要
**問題**：有沒有能直接和本研究比較的「LLM 用於財報舞弊偵測、報告 AUC」的研究？如果有，該用哪個標籤、哪份資料？

**結論**：
1. 有可以並列比較的數字，但**沒有一篇能被嚴格重現**：模型停用、提示詞未公布，或資料要付費。
2. 最適合的 benchmark 有四個，各對應一種標籤與資料，見 §4：
   - (a) Bao 的 AAER 資料＋FraudDebate-Agent
   - (b) UMAR 的重編標籤（Audit Analytics）
   - (c) 免費的 8-K 4.02 重編標籤
   - (d) EDINET-Bench（公開資料，已含記憶探針）
3. **沒有任何一篇以 AAER 或重編為標籤的 LLM 研究，檢驗過模型是否記得結果。** 唯一做過記憶探針的 EDINET-Bench 只問「能否說出公司名」，而且輸入只有數字表格。記憶文獻則一致警告：只遮名稱不夠。這就是本研究的空缺。

## 2. 本研究採用的比較原則
- **AUC 不受盛行率影響，但只在同一份資料上可比**。各研究的舞弊比例差很多：FraudDebate 約 0.7%、Waffo Dzuyo 約 5%、UMAR 8.2%、EDINET-Bench 約 50%。所以跨研究的 AUC 只能看大概的落點。
- **PR-AUC 與 Precision@k 受盛行率影響**，只能在同一份資料上比較。
- **基準要在自己的資料上重跑**（例如 XGBoost、RUSBoost）。和論文數字接近時，才能說兩份資料可比。

## 3. 文獻總表

### 3.1 LLM 或語言模型、母體排序型（報告 AUC）
| 研究 | 資料與標籤 | 切分 | LLM 的角色與輸入 | 已確認的數字 | 記憶 | 讀取 | 證據等級 |
|---|---|---|---|---|---|---|---|
| **Yue, Yang & Liu (2026)** FraudDebate-Agent, *Mathematics* 14(15):2695 | Bao 資料（AAER）＋EDGAR-CORPUS MD&A；測試 FY2003–2008，16,180 公司年度、118 件舞弊 | 時間外 | FinBERT 讀 MD&A；LLM（Llama-3-70B、gpt-4-turbo-2024-04-09）辯論，輸入含 `[CIK-FY]`、未遮蔽的 MD&A 句子 | 完整方法 0.806、NDCG@1% 0.047、P@1% 6.4%；三 agent 平均 0.770；**GPT-4 zero-shot 0.681**、XGBoost 0.738、RUSBoost 0.725、FinBERT 0.703、HAN 0.745、F-score LR 0.690（表 3） | 未討論 | 全文 | 同儕審查（MDPI，審查期短；以「預印本以上」看待） |
| **Wang, Wang, Lu, Peng & Lin (2026)** UMAR, arXiv 2606.15640 | **Audit Analytics 不可依賴（non-reliance）重編**，申報後兩年內；大型加速申報公司 FY2019–2023，3,200 公司年度，正例 8.2%（263） | **時間順序**：訓練 2019–21（1,920）、校準 2022（640）、**測試 2023（640，約 52 正例）** | MD&A 文字、比率、CAM 三個 agent，Dempster–Shafer 融合 | **AUROC 0.782**、PR-AUC 0.341、ECE 0.052；LR 0.672、RF 0.713、XGBoost 0.738、FinBERT 0.721、Longformer 0.709、**單一 LLM（GPT-4o）0.695**、雙 agent LLM 0.741 | 未討論 | 全文（查證 agent） | 預印本（6 頁） |
| **Waffo Dzuyo, Guibon, Cerisara & Belmar-Letelier (2026)**, arXiv 2607.19259（HAL「Read Between the Lines」；據片段為 FinLLM@IJCAI 2026） | AAER（3,300 件 → 1,451 個舞弊公司季度，2000–2022）；**10-Q 公司季度**，268,936 份、13,332 家、2009–2024；舞弊約 5% | 新任務 **CI-FSFD**：測試公司在訓練中完全沒出現（5 折） | 微調 Fino1-8B 讀 LLM 摘要的 MD&A；另有 zero-shot | CI-FSFD：Fino1-8B 0.74（文字）、0.72（文字＋財務）、RF 0.70；**zero-shot LLM 約 0.50**；隨機切分最高 0.96 | 作者承認 CI-FSFD 不能完全防前視偏誤 | 全文（查證 agent） | 預印本／workshop |
| **Sugiura 等 (2026)** EDINET-Bench, ICLR 2026, arXiv 2506.08762 | 日本 EDINET；舞弊標籤來自修正報告（由 Claude 3.7 Sonnet 分類後人工複核）；訓練 865、測試 224（約一半舞弊） | 公司不重疊 | zero-shot 前沿 LLM，讀摘要、三大報表、文字 | Claude 3.5 Sonnet 0.73（全部輸入）；RF 0.75；LR 0.68（**只用摘要**；全部輸入時 LR 為 0.57–0.59） | **有探針**：從表格猜公司名，準確率 ≤ 0.05；逐年結果近年沒有下降 | 全文（查證 agent） | 同儕審查（ICLR） |
| **Efe, Sapra & Ahmed (2026)**, arXiv 2611.01123 | **8-K Item 4.02**（8,903 份，2005–2024）；法說會逐字稿 | — | 9B、27B LLM 讀遮蔽後的逐字稿 | 文字增益的 AUROC CI −0.05 至 0.11（不顯著）；組內 AUROC 基準 0.651、加文字 0.628；**遮蔽後 66% 的逐字稿被認出股票代號**（327 份中 217 份） | **有**：辨識檢驗 | 全文（查證 agent） | 預印本 |
| **Bhattacharya & Mićković (2024)**, *IJAIS* 53:100682 | 10-K MD&A | — | 微調 BERT | 比文字基準好 15%、比數字基準好 12%（相對值，沒有 AUC） | 未提及 | 摘要 | 同儕審查 |
| **Dai, Qian, Wang, Liu & Wang (2026)** FSFDLLM, *Intelligent Computing* 5:0274 | 「真實上市公司資料」，國別未寫 | — | LLM 文字特徵＋推理 | 摘要只說 F1 與 AUC 勝過基準；片段裡的 0.8628 沒有指標標示，**不能使用** | — | 摘要 | 同儕審查 |
| **Nie, Long, Fang & Gao (2025)**, *JDIS* 10(4):291–315 | 中國 5,304 家上市公司，2015–2020（資料庫在摘要中寫作 CSMAD） | — | LLM 摘要＋多模態 | GBDT AUC > 0.850；多模態 +7.4%；LLM 比傳統方法好 19.3%（0.817、0.894 未找到） | — | 摘要 | 同儕審查 |
| **Yu, Wu, Han, Ding & Wei (2026)**, *ACM TOIT* 26(2) | 1995–2019 年報 | — | 段落對齊的變動軌跡＋舞弊詞類（ParaEmb-FraudW2V） | 沒有找到數字 | — | 摘要 | 同儕審查 |
| **Ergun & Sefer (2025)**, *ISAFM* 32(4) e70021 | MD&A 1995–2024 | — | FinBERT、FinLlama、FinGPT 向量＋LSTM | 只說「平均優於」；二手的 0.86、0.91 不能使用 | 樣本與 FinLlama、FinGPT 的訓練期重疊 | 摘要 | 同儕審查 |
| **Kirkos, Boskou 等 (2024)**, SSRN 4842962 | — | — | ChatGPT-4 提示 | 約 67% 未查證；沒有 AUC | — | 摘要 | 預印本 |
| **ohartman/restatement-risk**（GitHub） | **8-K 4.02，三年內**；訓練用 2019 年以前申報的 10-K，測試 2019–2023 申報的 17,755 份；基準率 5.2% | 時間外 | 非 LLM（森林模型） | AUC 0.748（0.733–0.762）；只用報表 0.737；重新估計的 F-score 0.541；用其標籤評估 Bertomeu 已公布的分數為 0.629 | 已排除 5 種洩漏 | README 全文 | 灰色文獻 |

**FraudDebate 數字的說明**：查證 agent 讀不到 MDPI 全文，所以把基準數字標成「找不到」。本文作者已從使用者提供的 PDF 表 3 直接確認。另外有兩個巧合值得查核，但**不構成結論**：
- FraudDebate 的 XGBoost 0.738 和 UMAR 的 XGBoost 0.738 相同，但兩篇的資料與標籤都不同。
- FraudDebate 的 RUSBoost 0.725 是在文字可用的子樣本上算的，卻和 Bao 原文在全樣本上的數字到小數點後三位都相同。

### 3.2 非 LLM 的經典基準
| 研究 | 標籤 | 已確認 | 注意事項 |
|---|---|---|---|
| **Bao, Ke, Li, Yu & Zhang (2020)**, *JAR* 58(1):199–235 | AAER；28 項原始數字；測試 2003–2008 | RUSBoost AUC 0.725（第三方重做 0.715 vs 原報 0.723） | **2022 勘誤**（*JAR* 60(4):1635–1646）：程式錯誤「導致績效指標高估」，更正後的 AUC 沒查到。**Walker (2021, 2022, *EJW*)**：指控作者未揭露就修改舞弊標籤；不修改的話，模型贏不過 F-score。後續有 JAR 調查報告、Klein (2023)、Gow (2022)「Bao et al. (2020) 該撤回嗎？」。logit 0.672、SVM 0.626 只出現在部落格 |
| **Bertomeu, Cheynel, Floyd & Pan (2021)**, *RAST* 26(2):468–519 | 據灰色來源為 8-K 4.02 | 沒有找到主要 AUC | 會計變數要和審計、市場變數交互作用才重要 |
| **Brown, Crowley & Elliott (2020)**, *JAR* 58(1):237–291 | AAER＋故意錯報的重編與 10-K/A；1994–2012 | 偵測率最多提升 59%（不是 AUC） | 主題模型 |
| **Zavitsanos 等 (ICAIF '21)**, arXiv 2305.17457 | AAER **與** Audit Analytics 各兩組資料；1998–2008，32,443 筆，約 1% 正例 | 指標是 R-precision | 滑動窗口測試 2003–2008；強調「真實的時間順序評估」 |
| **Barton, Burnett, Gunny & Miller (2024)**, *Management Science* 70(1):32–53 | — | — | 區分「做了錯報」與「被發現」的機率 |

### 3.3 記憶、前視偏誤與匿名化
| 研究 | 發現 | 對本研究的意義 | 讀取 | 等級 |
|---|---|---|---|---|
| **Glasserman & Lin (2024)**, *JFDS* 6(1):25–42 | 匿名化的新聞標題在時間內反而表現較好，表示「分心效應」大於前視偏誤；大公司效果更強 | 認得公司不一定讓結果變好，要分開量 | 全文 | 同儕審查 |
| **Lopez-Lira, Tang & Zhu (2025)**, SSRN 5217505／arXiv 2504.14765 | 遮蔽後的法說會中，GPT-4o 認出 Apple、Meta、Microsoft **100%**，七大科技股都在 85% 以上；經 entity neutering 後仍能重新識別 | **直接支持**本輪試跑（B 組 16/20）：只遮名稱不夠 | 全文 | 預印本 |
| **Engelberg, Manela, Mullins & Vulicevic (2025)** Entity Neutering, SSRN 5182756 | 用 LLM 遮蔽並改寫，直到識別率降到隨機；超過 50 萬篇文章；情緒判斷和原文一致率超過 90%；已延伸到 MD&A 與法說會 | 可當作 **B2（強遮蔽）** 的現成方法 | 摘要 | 預印本 |
| **Wu, Yang, Ying & Zhou (2026 v2)** Anonymization and Information Loss, arXiv 2511.15364 | 主任務是預測 S&P 信評調降；**匿名化的資訊損失大於前視偏誤**，損失來自遮掉數字與人物實體 | 遮蔽梯子的取捨：遮越多、資訊越少 | 全文 | 預印本 |
| **Gao, Jiang & Yan**, arXiv 2512.23847 | 用模型「回想結果」的信心（LAP）偵測前視偏誤；時間內為正，截止後歸零；模型為 Llama-3.3-70B | 可借用為記憶指標 | 全文 | 預印本 |
| **Sarkar & Vafa (2024)**, SSRN 4754678（ICML 2025 workshop） | 單邊檢定；法說會風險因子與選舉都有前視偏誤；改提示詞效果有限 | 提示「不要用後來的資訊」不可靠 | 摘要 | 預印本 |
| **Levy**, Caution Ahead, *JAR* 64(3):1139–1188 (2026) | 數值推理差；商用 LLM 有顯著前視偏誤 | 會計頂刊已正式承認這個問題 | 摘要 | **同儕審查** |
| **Ludwig, Mullainathan & Rambachan**, *Annual Review of Economics* 18:283–316 (2026) | 用 LLM 做預測時，需要「沒有訓練洩漏」的條件 | 方法論依據 | 摘要 | **同儕審查** |
| **He, Lv, Manela & Wu**, ChronoBERT／ChronoGPT, arXiv 2502.21206 | 時點一致的模型；前視偏誤的大小因模型與應用而異 | 替代方案：用截止日早於樣本的模型 | 摘要 | 預印本 |
| **Kelly, Malamud, Schwab & Xu**, NBER w35247 | 最大 40 億參數、2013–2024 的時點一致模型；Sharpe 約 0.7 → 1.0–1.5 | 同上（規模化版本） | 摘要 | 預印本 |
| **Kim, Muhn & Nikolaev (2024)** | 匿名化財報＋公司名探針（0.07%）＋截止後測試 | **已撤回**（arXiv v3，2025-02-20，原因是重做時發現資料不一致）：方法可當先例，**數字不可引用** | 二手 | 已撤回 |

### 3.4 題庫型（不適合當 AUC benchmark）
AuditFraudBench（arXiv 2606.08345；全文）、AuditBench（Wang 等 2025；AAAI workshop）、FinVerBench（arXiv 2605.29586）、VERA-8B（arXiv 2608.28402）。這些研究沒有正常公司或連續分數，測的是理解與推理。其中 AuditFraudBench 的提示詞含公司名稱，也沒有討論記憶。

## 4. 可用的 benchmark：四個選項

| 選項 | 標籤 | 可比較的數字 | 優點 | 缺點 | 和本研究的配合 |
|---|---|---|---|---|---|
| **(a) Bao 的 AAER，FY2003–2008**（現行第十輪） | AAER | FraudDebate 表 3：GPT-4 zero-shot 0.681、XGBoost 0.738、完整方法 0.806；Bao RUSBoost 0.725 | 標準資料、公開、時間外；同一份資料上有 LLM 數字 | Bao 有勘誤與爭議；GPT-4 Turbo 已停用；樣本年代早於所有 LLM 的截止日，**記憶風險最高** | 已在進行；**正好用來量記憶** |
| **(b) UMAR 式重編（Audit Analytics）** | non-reliance 重編，兩年內 | UMAR 0.782；GPT-4o 單一 LLM 0.695；XGBoost 0.738；LR 0.672 | 時間順序切分；有單一 LLM 基準；年代新 | **Audit Analytics 要付費**；測試只有 640 筆、約 52 個正例；大型公司 | 沒有授權就無法直接複製 |
| **(c) 免費 8-K 4.02 重編**（大 R） | 8-K Item 4.02，兩到三年內 | GitHub 專案 0.748（非 LLM，灰色文獻）；Efe 等的 AUROC 0.63–0.65 | **免費**；第九輪已有掃描程式；可以做 2019–2023（時間內）與 2026（時間外）兩段 | 沒有同儕審查的 LLM 數字；4.02 不等於舞弊 | **最可行的第二個 benchmark**：同一個標籤，時間內 vs 時間外，直接量記憶灌水多少 |
| **(d) EDINET-Bench** | 日本修正報告 | Claude 3.5 Sonnet 0.73、RF 0.75 | **資料公開（HF）**、ICLR 同儕審查、已有記憶探針 | 日文；舞弊約五成；只有表格探針 | 可以直接跑你的方法來比較；要處理日文 |

**建議順序**：
1. 先完成 (a)，這是第十輪本身。
2. 第二個 benchmark 選 (c)：免費，又能延伸第九輪。
3. (d) 列為可選：能和同儕審查的公開基準正面比較。
4. (b) 只當參考數字，除非取得 Audit Analytics 授權。

## 5. 綜合：一致的發現與空缺
1. **LLM 單獨用不強**：
   - GPT-4 zero-shot 0.681 低於 XGBoost 0.738（FraudDebate）
   - GPT-4o 單一 LLM 0.695 也低於 XGBoost 0.738（UMAR）
   - 在沒看過的公司上，zero-shot 約 0.50（Waffo Dzuyo）
   - EDINET-Bench 中，LLM 和 RF 差不多

   LLM 的提升都出現在**多 agent 或微調**之後，而且幅度不大：+0.03 至 +0.04。
2. **評估方式決定結果**：隨機切分最高 0.96，換成沒看過的公司就只有 0.74（Waffo Dzuyo）。Bao 的勘誤與 Walker 的批評，也都和連續舞弊跨訓練與測試期有關。
3. **記憶**：
   - 會計與金融頂刊已正式承認前視偏誤（Levy, *JAR* 2026；Ludwig 等，*ARE* 2026）。
   - 實證上，遮蔽後的文字仍有 66–100% 被認出（Efe 等；Lopez-Lira 等）。
   - 匿名化的資訊損失可能大於前視偏誤（Wu 等），所以需要逐級取捨，不能一刀切。
4. **空缺**：
   - 在以 AAER 或重編為標籤的 LLM 舞弊研究中，沒有一篇量過「模型是否記得結果」，也沒有一篇比較「有無身分」的 AUC 差異。
   - EDINET-Bench 只用表格做公司名探針；Efe 等量了辨識率，但對象是法說會，不是舞弊判斷的分數。

## 6. 本研究的定位（依文獻修正）
> 在標準 AAER 資料（Bao＋EDGAR-CORPUS）上，第一次把 LLM 舞弊分數分解為「認出公司的效果」（A − B）、「純記憶」（只給名稱的 C 組）與「可驗證內容」（事實卡 D、比率卡 E）。並以辨識探針（開放與封閉式）和時間外樣本（第九輪 2026 年的 4.02 與 AAER），驗證去除記憶後仍存在的區分力。方法上延伸 Engelberg 等 (2025) 的 entity neutering、Lopez-Lira 等 (2025) 的再識別檢驗，以及 Glasserman & Lin (2024) 的匿名化比較，把它們用到舞弊偵測這個「結果早已公開」的情境。

## 7. 反方檢查與限制
（§7.1 由反方檢查 agent 補上，見下方）
- **讀取深度**：記憶相關的多篇與會計期刊文章只讀到摘要；MDPI、SSRN、NBER 無法連線。
- **以英文為主**，可能漏掉中文與日文文獻。
- **2026 年的 arXiv 論文多數未經同儕審查**；UMAR 只有 6 頁、測試只有約 52 個正例。
- FraudDebate 與其他論文數字相同的巧合（§3.1 的說明），需要人工查核。

## 參考文獻（含 DOI 或網址）
- Bao, Y., Ke, B., Li, B., Yu, Y. J., & Zhang, J. (2020). *JAR*, 58(1), 199–235. Erratum (2022). *JAR*, 60(4), 1635–1646. https://doi.org/10.1111/1475-679X.12454
- Barton, F. J., Burnett, B. M., Gunny, K., & Miller, B. P. (2024). *Management Science*, 70(1), 32–53.
- Bertomeu, J., Cheynel, E., Floyd, E., & Pan, W. (2021). *Review of Accounting Studies*, 26(2), 468–519.
- Bhattacharya, I., & Mićković, A. (2024). *IJAIS*, 53, 100682.
- Brown, N. C., Crowley, R. M., & Elliott, W. B. (2020). *JAR*, 58(1), 237–291.
- Dai, Y., Qian, Y., Wang, X., Liu, Y., & Wang, C. (2026). FSFDLLM. *Intelligent Computing*, 5, 0274. https://doi.org/10.34133/icomputing.0274
- Efe, Sapra, & Ahmed (2026). arXiv:2611.01123.
- Engelberg, J., Manela, A., Mullins, W., & Vulicevic, L. (2025). Entity Neutering. https://doi.org/10.2139/ssrn.5182756
- Ergun & Sefer (2025). *ISAFM*, 32(4), e70021. https://doi.org/10.1002/isaf.70021
- Gao, Jiang, & Yan. Detecting Lookahead Bias in LLM Forecasts. arXiv:2512.23847.
- Glasserman, P., & Lin, C. (2024). *JFDS*, 6(1), 25–42. https://doi.org/10.3905/jfds.2023.1.143
- He, Lv, Manela, & Wu (2025). Chronologically Consistent LLMs. arXiv:2502.21206.
- Kelly, B., Malamud, S., Schwab, & Xu (2026). Scaling Point-in-Time Language Models. NBER w35247.
- Kim, A., Muhn, M., & Nikolaev, V. (2024). arXiv:2407.17866（已撤回）.
- Kirkos, E., Boskou, G., et al. (2024). SSRN 4842962.
- Levy. Caution Ahead. *JAR*, 64(3), 1139–1188 (2026). https://doi.org/10.1111/1475-679X.70058
- Lopez-Lira, A., Tang, Y., & Zhu, M. (2025). The Memorization Problem. SSRN 5217505; arXiv:2504.14765.
- Ludwig, J., Mullainathan, S., & Rambachan, A. (2026). *Annual Review of Economics*, 18, 283–316. https://doi.org/10.1146/annurev-economics-120925-105620
- Nie, H., Long, Z., Fang, Z., & Gao, L. (2025). *JDIS*, 10(4), 291–315. https://doi.org/10.2478/jdis-2025-0046
- Sarkar, S., & Vafa, K. (2024). Lookahead Bias in Pretrained Language Models. https://doi.org/10.2139/ssrn.4754678
- Sugiura, I., Ishida, T., Makino, T., Tazuke, C., Nakagawa, T., Nakago, K., & Ha, D. (2026). EDINET-Bench. ICLR 2026. arXiv:2506.08762.
- Waffo Dzuyo, Guibon, Cerisara, & Belmar-Letelier (2026). arXiv:2607.19259.
- Walker, S. (2021, 2022). *Econ Journal Watch*; Gow, I. (2022). SSRN; Klein (2023). *EJW*, 20(2), 460–464.
- Wang, Y., Wang, M., Lu, Y., Peng, Z., & Lin, S. (2026). UMAR. arXiv:2606.15640.
- Wu, Yang, Ying, & Zhou (2026). Anonymization and Information Loss. arXiv:2511.15364.
- Yu, Y., Wu, Z., Han, Y., Ding, Y., & Wei, W. (2026). *ACM TOIT*, 26(2). https://doi.org/10.1145/3796514
- Yue, X., Yang, J., & Liu, W. (2026). FraudDebate-Agent. *Mathematics*, 14(15), 2695. https://doi.org/10.3390/math14152695
- Zavitsanos, E., et al. (2021). ICAIF '21; arXiv:2305.17457.
- 題庫型：Liu, Z., et al. (2026). AuditFraudBench, arXiv:2606.08345；Wang, R., Liu, J., Zhao, W., Li, S., & Zhang, D. (2025). AuditBench；FinVerBench, arXiv:2605.29586；VERA-8B, arXiv:2608.28402.
