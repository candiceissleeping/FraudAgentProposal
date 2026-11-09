# 主題 1 綜整（Phase 3，synthesis_agent）：LLM 財報舞弊分數的三分解——記得結果、公司類型、讀到的內容

- 角色：ARS deep-research `synthesis_agent`，只做 Phase 3（綜整、矛盾處理、缺口分析）；不起草報告正文、不做跨主題整合
- 輸入：`results/lit_review/phase2_bibliography/T1_bibliography.md`、`T1_sources.json`；來源查核 `results/lit_review/phase2_verification/verification.md`（本主題 20 篇全部 VERIFIED）
- 研究問題：LLM 判斷財報舞弊風險時，分數有多少來自「記得這家公司後來出事」、多少來自「公司類型的先驗」、多少來自「真正讀到的報表內容」？
- 閱讀範圍聲明：本主題 20 篇在 Phase 2 **全部只讀到摘要**（`abstract_only`）。因此以下所有綜整都只到「摘要層級」；方法弱點未評估；引用錨點一律為 `section:abstract`。Didisheim 等 (2025) <!--ref:didisheim2025predictable--><!--anchor:section:abstract--> 的摘要內容來自 WebSearch 對 ESSEC 頁面的轉述，不是原文摘要。
- 日期：2026-11-09

## 預定主張清單

（取代 Claim Intent Manifest；本環境沒有 Material Passport。以下為本綜整預定提出的實質主張，寫作前先列出。）

| 編號 | 預定主張 | 預定依據（key） | 不可越界的限制 |
|---|---|---|---|
| C1 | 在時間內樣本上，LLM 的財經預測力含有「記得結果」的成分，且此成分無法靠提示或簡單遮蔽排除 | sarkar2024lookahead、lopezlira2025memorization、levy2026caution、gao2025detecting、eliseev2026fake | 不宣稱記憶「解釋全部」預測力；不把財經報酬／總體預測的結果直接等同舞弊任務 |
| C2 | 前視偏誤的大小不是常數，隨模型容量、應用、資料粒度與實體知名度改變 | he2025chronologically、didisheim2025predictable、carlini2023quantifying、kandpal2023large、roberts2023data、glasserman2024assessing | 逐字記憶的規律不可直接外推到事件知識 |
| C3 | 身分資訊除了觸發記憶，也帶來「分心／脈絡」效應，方向可正可負；這與「公司類型先驗」概念相近但不相同 | glasserman2024assessing、eliseev2026fake、longpre2021entity、wu2024reasoning | 不把「分心效應」等同於本研究的「公司類型先驗」 |
| C4 | 現有記憶偵測工具（MIA、回想代理）效度有限，時間切分的對照可能混入分布漂移 | duan2024membership、roy2026memguard、shi2024detecting、oren2024proving、lopezlira2025memorization | 不宣稱 MIA「無效」，只說在所述條件下接近隨機 |
| C5 | 在舞弊／重編領域，本次檢索範圍內只有兩篇做了部分記憶控制，且都未把分數拆成三個成分 | efe2026earnings、sugiura2026edinet | 缺口以「本次檢索範圍內」為界，不宣稱沒有此類研究 |

總限制（適用全文）：不使用未限定的因果語言；所有數字都是摘要層級；本研究的實驗結果不是文獻證據，只能放在「與本研究實驗的對照」小節。

## Synthesis Report

### Literature Matrix

**Date compiled**：2026-11-09｜**Total sources**：20｜**Themes identified**：5

主題代號：
- **A** 時間內預測力含「記得結果」成分（且不易以提示／遮蔽排除）
- **B** 前視偏誤的大小隨模型、應用、粒度與知名度而變
- **C** 身分資訊的「分心／脈絡」效應（與公司類型先驗相關）
- **D** 記憶偵測工具的效度
- **E** 分解記憶與能力的研究設計

符號：✓ 支持該主題的主張；✗ 提供相反或限制性證據；◐ 部分相關（提供條件或間接證據）；— 未涉及。等級與 Tier 依 T1 書目。

| Source | Year | Level | Tier | 讀取 | A | B | C | D | E |
|---|---|---|---|---|---|---|---|---|---|
| Sarkar 與 Vafa <!--ref:sarkar2024lookahead--><!--anchor:section:abstract--> | 2024 | III | 2 | abstract | ✓ | — | — | — | ✓ |
| Glasserman 與 Lin <!--ref:glasserman2024assessing--><!--anchor:section:abstract--> | 2024 | III | 1 | abstract | ✗（時間內匿名化反而較好） | ✓ | ✓ | — | ✓ |
| Lopez-Lira 等 <!--ref:lopezlira2025memorization--><!--anchor:section:abstract--> | 2025 | III | 2 | abstract | ✓ | — | — | ✓（記憶證據只是下界） | ✓ |
| Levy <!--ref:levy2026caution--><!--anchor:section:abstract--> | 2026 | III | 1 | abstract | ✓ | — | — | — | — |
| Didisheim 等 <!--ref:didisheim2025predictable--><!--anchor:section:abstract--> | 2025 | III | 1 | abstract（WebSearch 轉述） | ◐ | ✓ | — | ◐ | — |
| Ludwig 等 <!--ref:ludwig2026large--><!--anchor:section:abstract--> | 2026 | VII | 1 | abstract | — | — | — | — | ✓ |
| Gao 等 <!--ref:gao2025detecting--><!--anchor:section:abstract--> | 2025 | III | 2 | abstract | ✓ | ✓ | — | ✓ | ✓ |
| Roy 與 Roy <!--ref:roy2026memguard--><!--anchor:section:abstract--> | 2026 | III | 2 | abstract | — | — | — | ✗（MIA 標準化後近隨機） | ◐ |
| Eliseev 與 Seleznev <!--ref:eliseev2026fake--><!--anchor:section:abstract--> | 2026 | III | 2 | abstract | ✓ | — | ✓ | ◐ | ✓ |
| He 等 <!--ref:he2025chronologically--><!--anchor:section:abstract--> | 2025 | III | 2 | abstract | ✗（該應用中偏誤不大） | ✓ | — | — | ✓ |
| Shi 等 <!--ref:shi2024detecting--><!--anchor:section:abstract--> | 2024 | III | 1 | abstract | — | — | — | ✓ | ◐ |
| Oren 等 <!--ref:oren2024proving--><!--anchor:section:abstract--> | 2024 | III | 1 | abstract | — | — | — | ✓ | — |
| Roberts 等 <!--ref:roberts2023data--><!--anchor:section:abstract--> | 2023 | IV | 2 | abstract | ✓ | ✓ | — | ◐ | ✓ |
| Duan 等 <!--ref:duan2024membership--><!--anchor:section:abstract--> | 2024 | III | 1 | abstract | — | — | — | ✗（分布漂移） | ✗（時間切分的混淆） |
| Carlini 等 <!--ref:carlini2023quantifying--><!--anchor:section:abstract--> | 2023 | III | 1 | abstract | — | ✓ | — | — | — |
| Kandpal 等 <!--ref:kandpal2023large--><!--anchor:section:abstract--> | 2023 | III | 1 | abstract | — | ✓ | ◐ | — | — |
| Longpre 等 <!--ref:longpre2021entity--><!--anchor:section:abstract--> | 2021 | III | 1 | abstract | — | — | ✓ | — | ✓ |
| Wu 等 <!--ref:wu2024reasoning--><!--anchor:section:abstract--> | 2024 | III | 1 | abstract | — | — | ◐ | — | ✓ |
| Sugiura 等 <!--ref:sugiura2026edinet--><!--anchor:section:abstract--> | 2026 | III | 1 | abstract | — | — | — | — | ◐ |
| Efe 等 <!--ref:efe2026earnings--><!--anchor:section:abstract--> | 2026 | IV | 2 | abstract | ◐ | — | ✓ | — | ◐ |
| **Totals** | | | | | **6✓ 2✗ 2◐** | **7✓** | **4✓ 2◐** | **4✓ 2✗ 3◐** | **10✓ 1✗ 4◐** |

（Didisheim 等 (2025) <!--ref:didisheim2025predictable--><!--anchor:section:abstract--> 的 A 欄為 ◐：依 WebSearch 轉述的摘要，偏誤在小模型、細粒度資料上可忽略，隱含較大模型或較粗粒度資料的偏誤不可忽略。）

### Key Themes

#### Theme A：時間內的預測力含有「記得結果」的成分，而且提示詞與遮蔽擋不住
**Evidence Strength**：Moderate
**Sources**：6 篇支持（Level III–IV；其中 5 篇為預印本，只有 Levy (2026) <!--ref:levy2026caution--><!--anchor:section:abstract--> 為同儕審查期刊論文），2 篇提供限制性證據，2 篇部分相關
**Synthesis**：

多條獨立的證據線在摘要層級指向同一件事：當研究樣本落在模型訓練期內，LLM 的預測表現不能直接解讀為「讀懂了輸入」。Sarkar 與 Vafa (2024) <!--ref:sarkar2024lookahead--><!--anchor:section:abstract--> 以「給定資訊集下本應不可預測的事件卻被預測對」作為直接檢定，在法說會風險因子與選舉預測兩個應用中都找到前視偏誤；Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract--> 進一步顯示模型能回想截止日前經濟與金融數列的精確數值、截止日後則無；Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract--> 以公司—日期層級的 Lookahead Propensity（LAP）發現，高 LAP 樣本的預測力被放大，而截止後交互項不再顯著。會計頂級期刊的 Levy (2026) <!--ref:levy2026caution--><!--anchor:section:abstract--> 在摘要中更直接主張商用 LLM 的前視偏誤「可能解釋」多種情境中很大一部分的預測力。Roberts 等 (2023) <!--ref:roberts2023data--><!--anchor:section:abstract--> 在程式題上以截止日自然實驗得到同方向的證據（截止前的通過率與題目知名度、發佈日期相關）。

這些研究共同指出兩個機制性細節。第一，「要求模型遵守歷史邊界」的提示詞無法阻止回想（Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract-->），以提示詞抵銷偏誤也有其限制（Sarkar 與 Vafa (2024) <!--ref:sarkar2024lookahead--><!--anchor:section:abstract-->）；第二，遮蔽實體後模型仍能從極少脈絡重建實體與日期（Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract-->）。Eliseev 與 Seleznev (2026) <!--ref:eliseev2026fake--><!--anchor:section:abstract--> 的「假日期檢定」從另一個方向印證：受測的現代 LLM 沒有一個通過第一個檢定。

但這個主題不能被讀成「記憶解釋一切」。He 等 (2025) <!--ref:he2025chronologically--><!--anchor:section:abstract--> 以只用當時可得文字訓練的時點一致模型，發現在新聞預測次日報酬的應用中，其即時輸出的 Sharpe 與大得多的 Llama 相當，摘要的解讀是該應用中前視偏誤不大；Glasserman 與 Lin (2024) <!--ref:glasserman2024assessing--><!--anchor:section:abstract--> 則發現訓練期內移除公司識別資訊的標題反而表現較好。這兩篇是本主題中「記憶未必推高結果」的主要反證，處理見 Contradictions & Resolutions。

Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract--> 的摘要還提出一個對本主題的方法論邊界：只要模型看過實現值，訓練期內的預測能力就「不可識別」，任何記憶證據都只是下界。這表示「扣除可偵測的記憶後剩下的分數」不能被直接當成真實能力的估計。

在舞弊／重編領域，直接證據很薄。Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract--> 的 LLM 分數較高，但該 LLM 能在 66% 的遮蔽逐字稿中說出確切股票代號，且模型在重編發生後才發布——摘要層級只能說「記憶可能介入」，並未量化其貢獻。

#### Theme B：前視偏誤的大小依模型、應用、資料粒度與實體知名度而變
**Evidence Strength**：Moderate（一般 NLP 的規律有多篇 Tier 1 支持；但多為逐字或事實 QA 記憶，外推到「事件結果」記憶須保留）
**Sources**：7 篇，Level III–IV
**Synthesis**：

在一般 NLP 文獻中，記憶量的變化有可重複的規律。Carlini 等 (2023) <!--ref:carlini2023quantifying--><!--anchor:section:abstract--> 報告記憶量隨模型容量、樣本重複次數與提示脈絡長度呈對數線性增加；Kandpal 等 (2023) <!--ref:kandpal2023large--><!--anchor:section:abstract--> 報告 QA 正確率與預訓練中含相同實體的文件數有強相關與因果關係；Roberts 等 (2023) <!--ref:roberts2023data--><!--anchor:section:abstract--> 的截止前通過率與題目在 GitHub 的知名度相關。金融文獻中出現同方向的結果：Didisheim 等 (2025) <!--ref:didisheim2025predictable--><!--anchor:section:abstract-->（摘要經 WebSearch 轉述）指出記憶驅動的可預測性隨資料頻率、模型大小與彙總層級規律變化，小模型與細粒度資料的偏誤可忽略；Glasserman 與 Lin (2024) <!--ref:glasserman2024assessing--><!--anchor:section:abstract--> 發現大公司（模型知道得較多）的效應更強。

He 等 (2025) <!--ref:he2025chronologically--><!--anchor:section:abstract--> 把這個異質性提升為一般性結論：前視偏誤是「模型與應用特定」的。Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract--> 的 LAP 本身就是公司—日期層級的異質性量測。

把這些結果放在一起，可以得到一個整合性的解讀：前視偏誤可以理解為「模型容量 × 結果在語料中的曝光量 × 任務對該結果的依賴程度」的函數，而不是單一常數。這是綜整層級的推論，不是任何單篇文獻的主張；且 Carlini 等 (2023) <!--ref:carlini2023quantifying--><!--anchor:section:abstract--> 與 Kandpal 等 (2023) <!--ref:kandpal2023large--><!--anchor:section:abstract--> 量的是逐字記憶或事實 QA，而本研究關心的是「某公司後來出事」這類事件知識，兩者的對應程度在本次檢索範圍內沒有直接驗證。

#### Theme C：身分資訊的作用不只記憶，還有「分心／脈絡」效應
**Evidence Strength**：Emerging
**Sources**：4 篇支持（Level III–IV），2 篇提供間接證據
**Synthesis**：

Glasserman 與 Lin (2024) <!--ref:glasserman2024assessing--><!--anchor:section:abstract--> 把公司識別資訊的影響拆成兩個方向相反的成分：前視偏誤（記得結果，推高表現）與「分心效應」（對公司的一般知識干擾判讀，拉低表現）；在其時間內樣本中，後者大於前者，且時間外前視偏誤消失但分心仍可能存在。Eliseev 與 Seleznev (2026) <!--ref:eliseev2026fake--><!--anchor:section:abstract--> 以日期反事實區分前視偏誤與「脈絡偏誤」（context bias）。NLP 的知識衝突文獻提供機制上的對應：Longpre 等 (2021) <!--ref:longpre2021entity--><!--anchor:section:abstract--> 以實體替換讓脈絡與參數記憶衝突，量測到模型對記憶資訊的過度依賴；Wu 等 (2024) <!--ref:wu2024reasoning--><!--anchor:section:abstract--> 在 11 個任務的反事實變體上看到表現一致且大幅下降，顯示模型常依賴不可遷移的窄程序。Kandpal 等 (2023) <!--ref:kandpal2023large--><!--anchor:section:abstract--> 則提示：在知識覆蓋稀疏（長尾）時，模型無法依賴特定實體的記憶。

在會計情境中，Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract--> 以「公開公司資訊」為基準，發現法說會文字相對此基準沒有可偵測的排序增益（加入文字的 AUROC 增益 95% CI −0.05 至 0.11），且文字分類器勝過隨機多半來自 SPAC 相關重編——這可讀作「公司層級的公開特徵可能已承載大部分可得訊號」，與「公司類型先驗」的概念相近。

需要強調的是，「分心效應」「脈絡偏誤」與本研究的「公司類型先驗」是三個相近但不相同的構念：前兩者是文獻作者在報酬或總體預測中的定義，後者是本研究在舞弊判斷中的操作化（只給公司類型資訊時的分數）。本綜整不把它們視為同一件事。

#### Theme D：記憶偵測工具的效度有限
**Evidence Strength**：Contested（正反兩方都有 Level III、Tier 1 證據）
**Sources**：4 篇提出或支持偵測方法，2 篇提出強烈的效度質疑，3 篇提供條件性證據
**Synthesis**：

一方的證據顯示記憶可以在黑箱下被偵測甚至被「證明」：Shi 等 (2024) <!--ref:shi2024detecting--><!--anchor:section:abstract--> 的 Min-K% Prob 不需參考模型，在 WIKIMIA 上比先前方法提高 7.4%；Oren 等 (2024) <!--ref:oren2024proving--><!--anchor:section:abstract--> 以標準排列與打亂排列的似然比較提供可證明的污染保證，並在稽核五個公開模型時未見普遍污染。金融文獻則發展了行為式代理：Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract--> 的 LAP、Didisheim 等 (2025) <!--ref:didisheim2025predictable--><!--anchor:section:abstract--> 的「無脈絡回想歷史報酬」。

另一方的證據則對這些工具的效度提出系統性質疑。Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract--> 在 160M–12B 的 Pile 模型上發現 MIA 多數情況幾乎不優於隨機，並把先前看似成功的情境歸因於分布漂移——例如成員與非成員來自同一領域但不同時間範圍。Roy 與 Roy (2026) <!--ref:roy2026memguard--><!--anchor:section:abstract--> 在金融情境得到相近的負面結果：以截止日定義樣本內時，「時間接近度」特徵的 ROC-AUC 為 1.000，但那只是定義變數的單調轉換；MIA 分數的區辨力大多來自模型間尺度差異，模型內標準化後降到 0.487–0.537；計入交易成本後，以污染分數過濾的策略都沒有改善。Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract--> 則從另一端提醒：任何記憶證據都只是下界。

這兩方的衝突並非單純的「有效 vs 無效」，處理見 Contradictions & Resolutions（CP-005、CP-006）。對本主題最直接的含意是：本研究使用的閉源模型不提供 token 機率，Min-K% 一類方法無法直接套用（此為 T1 書目的方法註記），而行為式探針（回想、自述）在本次檢索範圍內缺乏與外部紀錄對照的效度驗證——這一點連到主題 4。

#### Theme E：分解「記憶」與「能力」的研究設計工具箱
**Evidence Strength**：Moderate（作為設計共識；但在舞弊領域的實際應用很少）
**Sources**：10 篇支持，1 篇提出限制，4 篇部分相關
**Synthesis**：

文獻中可辨認出五類設計，各自針對不同的成分：

1. **確保無訓練洩漏的計量條件**：Ludwig 等 (2026) <!--ref:ludwig2026large--><!--anchor:section:abstract--> 把「LLM 訓練資料與研究樣本之間沒有訓練洩漏」列為預測用途有效結論的條件，並指出量測用途需要小型驗證樣本，否則模型或提示詞的選擇會讓估計大幅改變。
2. **時間外樣本／截止日自然實驗**：Roberts 等 (2023) <!--ref:roberts2023data--><!--anchor:section:abstract-->、Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract-->、Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract--> 都以截止日前後對照作為記憶存在與否的判準。
3. **時點一致模型**：He 等 (2025) <!--ref:he2025chronologically--><!--anchor:section:abstract--> 從模型端移除未來資訊，Sarkar 與 Vafa (2024) <!--ref:sarkar2024lookahead--><!--anchor:section:abstract--> 也建議使用只含分析期以前語料的模型。
4. **反事實／實體替換**：Longpre 等 (2021) <!--ref:longpre2021entity--><!--anchor:section:abstract-->（實體替換）、Wu 等 (2024) <!--ref:wu2024reasoning--><!--anchor:section:abstract-->（反事實任務）、Eliseev 與 Seleznev (2026) <!--ref:eliseev2026fake--><!--anchor:section:abstract-->（假日期）、Glasserman 與 Lin (2024) <!--ref:glasserman2024assessing--><!--anchor:section:abstract-->（匿名化標題）。
5. **分層交互檢定**：Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract--> 的「LAP × 預測」交互項。

這套工具箱的主要弱點來自 Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract-->：設計 2 的時間內外對照可能混入分布漂移，因此時間外樣本與時間內樣本的差距不能全歸於記憶。

在舞弊／重編領域，本次檢索只找到兩篇部分應用這些設計的研究：Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract--> 同時有公開資訊基準與模型再識別檢查；Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:abstract--> 是同儕審查、資料公開的日本年報 benchmark，其摘要指出最先進 LLM 在舞弊偵測上僅略勝邏輯斯迴歸（其記憶探針的細節本主題書目未讀到；主題 3 書目以章節閱讀記錄了公司名探針，見 T3 綜整）。兩者都沒有把分數拆成三個成分。

### Contradictions & Resolutions

| Claim A | Claim B | Resolution |
|---|---|---|
| Levy (2026) <!--ref:levy2026caution--><!--anchor:section:abstract-->：商用 LLM 的前視偏誤可能解釋多種情境中很大一部分的預測力 | He 等 (2025) <!--ref:he2025chronologically--><!--anchor:section:abstract-->：在新聞預測次日報酬中，時點一致模型與大模型 Sharpe 相當，該應用的前視偏誤不大；Didisheim 等 (2025) <!--ref:didisheim2025predictable--><!--anchor:section:abstract-->：小模型與細粒度資料的偏誤可忽略 | **可調和（條件性差異）**。三者在摘要中都承認偏誤存在與否取決於模型與應用；He 等 (2025) <!--ref:he2025chronologically--><!--anchor:section:abstract--> 明言「模型與應用特定」。差異可能來自任務（會計數值推理 vs 報酬預測）、模型規模與資料粒度。摘要層級無法判定 Levy (2026) <!--ref:levy2026caution--><!--anchor:section:abstract--> 的「大部分」適用於哪些情境。 |
| Sarkar 與 Vafa (2024) <!--ref:sarkar2024lookahead--><!--anchor:section:abstract-->、Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract-->：時間內有前視偏誤，會推高表現 | Glasserman 與 Lin (2024) <!--ref:glasserman2024assessing--><!--anchor:section:abstract-->：時間內移除公司識別資訊反而表現較好（分心 > 前視） | **可調和，但對本研究是重要警示**。Glasserman 與 Lin (2024) <!--ref:glasserman2024assessing--><!--anchor:section:abstract--> 量的是「淨效果」（前視 + 分心），前視偏誤存在不代表淨效果一定為正。這是「記憶不一定推高結果」的直接證據。在舞弊任務中兩者的相對大小，本次檢索範圍內沒有研究量過。 |
| Shi 等 (2024) <!--ref:shi2024detecting--><!--anchor:section:abstract-->、Oren 等 (2024) <!--ref:oren2024proving--><!--anchor:section:abstract-->：黑箱可偵測／證明污染 | Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract-->：MIA 多數幾乎不優於隨機；Roy 與 Roy (2026) <!--ref:roy2026memguard--><!--anchor:section:abstract-->：金融 MIA 標準化後近隨機 | **部分可調和**。Oren 等 (2024) <!--ref:oren2024proving--><!--anchor:section:abstract--> 偵測的是整個基準的排列偏好（資料集層級），Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract--> 與 Roy 與 Roy (2026) <!--ref:roy2026memguard--><!--anchor:section:abstract--> 評估的是實例層級 MIA；層級不同。但 Shi 等 (2024) <!--ref:shi2024detecting--><!--anchor:section:abstract--> 的 WIKIMIA 以模型訓練前後產生的資料建構金標準，正落在 Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract--> 所說「不同時間範圍造成分布漂移」的批評範圍內——這一部分在摘要層級**未能解決**。 |
| Roberts 等 (2023) <!--ref:roberts2023data--><!--anchor:section:abstract-->、Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract-->：截止前後對照揭示污染／前視偏誤 | Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract-->：時間切分的成員／非成員比較可被分布漂移污染 | **未解決（flagged）**。Roberts 等 (2023) <!--ref:roberts2023data--><!--anchor:section:abstract--> 以知名度與發佈日期的關係、Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract--> 以 LAP 交互項，都比單純時間內外比較多一層結構，可能部分緩解漂移問題；但摘要層級無法確認他們是否控制了漂移。 |
| Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract-->：LLM 能在遮蔽逐字稿中說出股票代號，記憶可能介入 | Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:abstract-->：LLM 在舞弊偵測上只略勝邏輯斯迴歸 | **非矛盾，而是不同證據面向**。Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract--> 證明的是「認得公司」，不是「記得結果並用於評分」；Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:abstract--> 報告的是整體表現。兩者都未拆解成分。 |
| Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract-->：遮蔽失敗，模型能重建實體 | Glasserman 與 Lin (2024) <!--ref:glasserman2024assessing--><!--anchor:section:abstract-->：匿名化標題在時間內表現不同（較好），表示匿名化確實改變了模型的輸入處理 | **可調和**。兩者問的是不同問題：Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract--> 問「遮蔽後模型還認不認得」，Glasserman 與 Lin (2024) <!--ref:glasserman2024assessing--><!--anchor:section:abstract--> 問「匿名化後表現如何改變」。匿名化可以同時「擋不住辨識」又「改變表現」。匿名化本身的取捨屬主題 3。 |

#### Cross-Paper Tension Inventory (#262)

```yaml
cross_paper_tensions:
  - pair_id: CP-001
    paper_a: "levy2026caution"
    paper_b: "he2025chronologically"
    candidate_basis: "opposite finding direction"
    overlap_topic: "前視偏誤在金融任務中解釋了多少預測力"
    a_finding: "商用 LLM 有顯著前視偏誤，可能解釋多種情境中很大一部分的預測力"
    a_evidence_pointer: "T1_bibliography.md #4 主要發現（Crossref 摘要）"
    b_finding: "新聞預測次日報酬中，時點一致模型 Sharpe 與大模型相當，該應用前視偏誤不大；偏誤為模型與應用特定"
    b_evidence_pointer: "T1_bibliography.md #10 主要發現（arXiv 摘要）"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶1"
    scholar_confirmation: "pending"
  - pair_id: CP-002
    paper_a: "didisheim2025predictable"
    paper_b: "levy2026caution"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "記憶驅動的可預測性是否普遍"
    a_finding: "偏誤隨頻率、模型大小、彙總層級規律變化；小模型與細粒度資料可忽略（WebSearch 轉述）"
    a_evidence_pointer: "T1_bibliography.md #5 主要發現（WebSearch 摘要片段）"
    b_finding: "前視偏誤可能解釋很大一部分預測力"
    b_evidence_pointer: "T1_bibliography.md #4 主要發現"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶1"
    scholar_confirmation: "pending"
  - pair_id: CP-003
    paper_a: "glasserman2024assessing"
    paper_b: "sarkar2024lookahead"
    candidate_basis: "opposite finding direction"
    overlap_topic: "時間內身分資訊使表現上升還是下降"
    a_finding: "時間內移除公司識別資訊的標題表現較好，分心效應大於前視偏誤"
    a_evidence_pointer: "T1_bibliography.md #2 主要發現（arXiv 摘要）"
    b_finding: "兩個應用中都找到前視偏誤"
    b_evidence_pointer: "T1_bibliography.md #1 主要發現"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶2"
    scholar_confirmation: "pending"
  - pair_id: CP-004
    paper_a: "glasserman2024assessing"
    paper_b: "lopezlira2025memorization"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "遮蔽／匿名化對 LLM 的影響"
    a_finding: "匿名化改變表現（時間內較好）"
    a_evidence_pointer: "T1_bibliography.md #2 主要發現"
    b_finding: "遮蔽後模型仍能從極少脈絡重建實體與日期，遮蔽失敗"
    b_evidence_pointer: "T1_bibliography.md #3 主要發現"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶6"
    scholar_confirmation: "pending"
  - pair_id: CP-005
    paper_a: "shi2024detecting"
    paper_b: "duan2024membership"
    candidate_basis: "opposite finding direction"
    overlap_topic: "黑箱成員推論／預訓練資料偵測是否有效；時間切分金標準的效度"
    a_finding: "Min-K% Prob 在以訓練前後資料建構的 WIKIMIA 上比先前方法高 7.4%"
    a_evidence_pointer: "T1_bibliography.md #11 主要發現"
    b_finding: "MIA 多數幾乎不優於隨機；先前成功可歸因於成員與非成員時間範圍不同的分布漂移"
    b_evidence_pointer: "T1_bibliography.md #14 主要發現"
    pair_assessment: "contradiction"
    resolution_status: "flagged_unresolved"
    scholar_confirmation: "pending"
  - pair_id: CP-006
    paper_a: "oren2024proving"
    paper_b: "duan2024membership"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "黑箱污染偵測的可行性"
    a_finding: "排列似然比較可提供可證明的污染保證（資料集層級）"
    a_evidence_pointer: "T1_bibliography.md #12 主要發現"
    b_finding: "實例層級 MIA 幾乎不優於隨機"
    b_evidence_pointer: "T1_bibliography.md #14 主要發現"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶3"
    scholar_confirmation: "pending"
  - pair_id: CP-007
    paper_a: "roy2026memguard"
    paper_b: "gao2025detecting"
    candidate_basis: "shared RQ subtopic"
    overlap_topic: "金融情境中記憶／污染分數能否作為有用的指標"
    a_finding: "MIA 分數模型內標準化後 0.487–0.537；以污染分數過濾的策略計入成本後無改善"
    a_evidence_pointer: "T1_bibliography.md #8 主要發現"
    b_finding: "高 LAP 公司—日期的預測力被放大，截止後交互項不顯著"
    b_evidence_pointer: "T1_bibliography.md #7 主要發現"
    pair_assessment: "conditional_difference"
    resolution_status: "flagged_unresolved"
    scholar_confirmation: "pending"
  - pair_id: CP-008
    paper_a: "roberts2023data"
    paper_b: "duan2024membership"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "截止日前後對照能否作為記憶／污染證據"
    a_finding: "截止前通過率與 GitHub 知名度、發佈日期顯著相關，構成污染強證據"
    a_evidence_pointer: "T1_bibliography.md #13 主要發現"
    b_finding: "時間範圍不同的成員／非成員比較可被分布漂移解釋"
    b_evidence_pointer: "T1_bibliography.md #14 主要發現"
    pair_assessment: "conditional_difference"
    resolution_status: "flagged_unresolved"
    scholar_confirmation: "pending"
  - pair_id: CP-009
    paper_a: "gao2025detecting"
    paper_b: "lopezlira2025memorization"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "截止日後記憶是否消失"
    a_finding: "LAP 截止後幾乎歸零"
    a_evidence_pointer: "T1_bibliography.md #7 主要發現"
    b_finding: "截止日後無回想"
    b_evidence_pointer: "T1_bibliography.md #3 主要發現"
    pair_assessment: "no_material_conflict"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"
  - pair_id: CP-010
    paper_a: "carlini2023quantifying"
    paper_b: "didisheim2025predictable"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "記憶隨模型大小增加"
    a_finding: "記憶量隨容量、重複、脈絡長度對數線性增加"
    a_evidence_pointer: "T1_bibliography.md #15 主要發現"
    b_finding: "較小模型偏誤可忽略"
    b_evidence_pointer: "T1_bibliography.md #5 主要發現"
    pair_assessment: "no_material_conflict"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"
  - pair_id: CP-011
    paper_a: "efe2026earnings"
    paper_b: "sugiura2026edinet"
    candidate_basis: "shared RQ subtopic"
    overlap_topic: "LLM 在舞弊／重編偵測的表現與記憶"
    a_finding: "LLM 分數較高，但能從 66% 遮蔽逐字稿說出股票代號；文字相對公開資訊無可偵測增益"
    a_evidence_pointer: "T1_bibliography.md #20 主要發現"
    b_finding: "最先進 LLM 在舞弊偵測上僅略勝邏輯斯迴歸"
    b_evidence_pointer: "T1_bibliography.md #19 主要發現（摘要）"
    pair_assessment: "insufficient_overlap"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"
  - pair_id: CP-012
    paper_a: "longpre2021entity"
    paper_b: "wu2024reasoning"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "模型依賴參數記憶 vs 輸入內容"
    a_finding: "實體替換衝突下模型過度依賴記憶資訊"
    a_evidence_pointer: "T1_bibliography.md #17 主要發現"
    b_finding: "反事實變體上表現一致且大幅下降"
    b_evidence_pointer: "T1_bibliography.md #18 主要發現"
    pair_assessment: "no_material_conflict"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"
```

**Coverage Note**：20 papers in corpus; 12 candidate pairs considered（basis：shared RQ subtopic／shared construct／opposite finding direction；本次未使用 bibliographic coupling，因為沒有引用網絡資料；也沒有 scholar flag）。This is a **scoped advisory scan, not complete pairwise contradiction detection** — cross-neighborhood pairs not surfaced here may exist and are not claimed absent（例如 Ludwig 等 (2026) <!--ref:ludwig2026large--><!--anchor:section:abstract--> 的「驗證樣本」條件與 Roy 與 Roy (2026) <!--ref:roy2026memguard--><!--anchor:section:abstract--> 的負面結果之間、Kandpal 等 (2023) <!--ref:kandpal2023large--><!--anchor:section:abstract--> 的長尾與 Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract--> 的 SPAC 集中之間，未逐一評估）。所有 evidence pointer 只到摘要層級。Bibliographic coupling was used as an inclusion signal only（本次未用）。Scholar confirms each `resolution_pointer` and may flag additional cross-pairs.

### Knowledge Gaps

1. **在本次檢索範圍內，未見在舞弊或重編標籤上把 LLM 分數同時拆成「記得結果」「公司類型先驗」「讀到的內容」三個成分的研究**（Empirical）。最接近的 Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract--> 有公開資訊基準與再識別檢查，Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:abstract--> 有公開 benchmark，但都停在「認出公司」或整體表現。含意：三成分分解是本研究可以填補的空缺，但需注意本次檢索未涵蓋 SSRN／NBER 全文、中日文資料庫。
2. **在本次檢索範圍內，未見針對「事件結果知識」（而非逐字文本或數值序列）的記憶量測工具及其效度驗證**（Methodological）。Shi 等 (2024) <!--ref:shi2024detecting--><!--anchor:section:abstract-->、Oren 等 (2024) <!--ref:oren2024proving--><!--anchor:section:abstract-->、Carlini 等 (2023) <!--ref:carlini2023quantifying--><!--anchor:section:abstract--> 量的是逐字或資料集層級記憶；Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract--> 與 Didisheim 等 (2025) <!--ref:didisheim2025predictable--><!--anchor:section:abstract--> 的回想代理在摘要中未見與外部紀錄對照。含意：本研究若用自述探針作為事件記憶指標，需要自行建立效度證據（連到主題 4）。
3. **時間內外對照的分布漂移控制**（Methodological）。Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract--> 的批評在本次檢索範圍內沒有在金融或會計情境中被系統回應；時間外樣本與時間內樣本在公司組成、標籤與年代上的差異如何與記憶分開，仍缺方法。
4. **「分心效應」在舞弊判斷中的方向與大小**（Theoretical／Empirical）。Glasserman 與 Lin (2024) <!--ref:glasserman2024assessing--><!--anchor:section:abstract--> 的分心效應來自報酬預測；在本次檢索範圍內未見舞弊任務中的對應量測，因此「名稱先驗」中分心與真實類型先驗的比例未知。
5. **證據的時效與出版狀態**（Temporal）。直接相關的金融記憶研究多為 2025–2026 年預印本（Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract-->、Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract-->、Roy 與 Roy (2026) <!--ref:roy2026memguard--><!--anchor:section:abstract-->、Eliseev 與 Seleznev (2026) <!--ref:eliseev2026fake--><!--anchor:section:abstract-->、Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract-->、He 等 (2025) <!--ref:he2025chronologically--><!--anchor:section:abstract-->），結論可能隨版本更新而改變。

### Evidence Convergence Map

```
Strong:      [          ] （無；所有主題都只讀到摘要，且核心金融證據多為預印本）
Moderate:    [======    ] Theme A 時間內預測力含記憶成分（6 支持／2 限制，Levels III–IV）
Moderate:    [======    ] Theme B 偏誤大小的異質性（7 篇，Levels III–IV）
Moderate:    [=====     ] Theme E 分解設計工具箱（10 篇；舞弊領域應用僅 2 篇部分）
Contested:   [====      ] Theme D 記憶偵測工具效度（4 支持／2 反對，Levels III）
Emerging:    [===       ] Theme C 身分資訊的分心／脈絡效應（4 支持／2 間接，Levels III–IV）
Gap:         [          ] 舞弊標籤上的三成分分解（0 篇，在本次檢索範圍內）
```

### Theoretical Integration

本主題的文獻可以放進一個「訊號來源分解」的框架。LLM 對某公司的輸出分數可以概念化為三個來源的組合：(1) 參數中關於「這家公司後來發生什麼」的事件記憶；(2) 參數中關於「這類公司通常如何」的一般知識（文獻中以「分心效應」或「脈絡偏誤」部分捕捉）；(3) 從輸入內容推出的訊號。

- 成分 (1) 的存在與異質性由 Theme A、B 支持；其上界與時間結構由 Ludwig 等 (2026) <!--ref:ludwig2026large--><!--anchor:section:abstract--> 的「無訓練洩漏」條件與 Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract--> 的「不可識別」論點界定。
- 成分 (2) 的概念在 Glasserman 與 Lin (2024) <!--ref:glasserman2024assessing--><!--anchor:section:abstract--> 與 Eliseev 與 Seleznev (2026) <!--ref:eliseev2026fake--><!--anchor:section:abstract--> 中出現，但它們的定義與本研究的「公司類型先驗」不同，屬於可借用但須重新操作化的概念。
- 成分 (3) 的檢驗邏輯來自 NLP 的知識衝突與反事實傳統：Longpre 等 (2021) <!--ref:longpre2021entity--><!--anchor:section:abstract--> 與 Wu 等 (2024) <!--ref:wu2024reasoning--><!--anchor:section:abstract--> 用「改變輸入、看輸出跟誰走」的方式，把讀與背分開。

框架層級的含意是：三個成分無法只靠一種設計識別。時間外樣本可壓低成分 (1)，但無法區分 (2) 與 (3)；類型對照可估計 (2)，但在時間內仍混入 (1)；反事實替換可檢驗輸出是否「跟著身分走」，但不直接給出成分大小。這是本綜整對文獻的整合性推論，不是任何單篇文獻的主張。Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract--> 提醒，任何依賴時間切分的估計都需處理分布漂移。

### 與本研究實驗的對照

（以下為本研究自身實驗結果與文獻的對照，取自 `results/research_topics.md`。這些結果**不是文獻**，未經同儕審查，不作為已確立的發現。）

- **「只給名稱 AUC 0.88（A）」與「時間外只給名稱 0.69（B）」的差距**：方向上與 Theme A 的「時間內含記憶成分」一致；但依 Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract-->，兩組在公司組成、標籤（AAER vs 4.02）與年代上不同，差距不能全歸於記憶。Glasserman 與 Lin (2024) <!--ref:glasserman2024assessing--><!--anchor:section:abstract--> 的分心效應也提示 0.69 中的「名稱先驗」可能不只是公司類型資訊。
- **扣掉「說知道」後剩 0.54（E1）**：邏輯上類似 Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract--> 的 LAP 分層；但依 Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract-->，可偵測的記憶只是下界，0.54 不應被解讀為「已完全移除記憶」。
- **記得越少的模型 AUC 越低（C）**：與 Carlini 等 (2023) <!--ref:carlini2023quantifying--><!--anchor:section:abstract-->、Didisheim 等 (2025) <!--ref:didisheim2025predictable--><!--anchor:section:abstract--> 的容量規律方向一致；但 Roy 與 Roy (2026) <!--ref:roy2026memguard--><!--anchor:section:abstract--> 提醒跨模型比較會混入模型能力差異。
- **名稱對調後分數跟著名稱走（第八輪 J1/J2）**：屬於 Longpre 等 (2021) <!--ref:longpre2021entity--><!--anchor:section:abstract-->、Eliseev 與 Seleznev (2026) <!--ref:eliseev2026fake--><!--anchor:section:abstract--> 的「改身分標記、看輸出跟誰走」設計家族。
- **時間外事實卡 0.77、整份 10-K 0.76**：可對照 Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:abstract-->「LLM 僅略勝 LR」與 Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:abstract-->「文字相對公開資訊無可偵測增益」——後者對「讀到的內容」成分是一個需要正視的反面參照。

### Synthesis Limitations

- **閱讀深度**：20 篇全部只讀到摘要，方法弱點未評估；本綜整中的「可調和」判斷都只依摘要所述的設計差異，可能在讀全文後改變。Didisheim 等 (2025) <!--ref:didisheim2025predictable--><!--anchor:section:abstract--> 的內容來自 WebSearch 轉述，可信度低於原文摘要。
- **錨點**：所有引用錨點為 `section:abstract`；本主題書目未記錄可用的逐字引文，因此沒有 `quote` 錨點。
- **預印本比例**：8/20 為預印本，且最直接的金融記憶研究多在其中；Sarkar 與 Vafa (2024) <!--ref:sarkar2024lookahead--><!--anchor:section:abstract--> 的 ICML workshop 收錄只見於 dreamy 紀錄，未經查核。
- **證據等級的跨主題不一致**：同一篇文獻在不同主題書目中被給了不同等級（例如 Sarkar 與 Vafa (2024) <!--ref:sarkar2024lookahead--><!--anchor:section:abstract--> 在 T1 為 III、在 T2 為 IV；Roberts 等 (2023) <!--ref:roberts2023data--><!--anchor:section:abstract--> 在 T1 為 IV／Tier 2、在 T5 為 III／Tier 1 並以 ICLR 2024 題名記錄）。本綜整依 T1 書目，跨主題整合時需統一。
- **檢索範圍**：非窮盡式系統檢索；未涵蓋 SSRN／NBER 全文、Google Scholar 被引網絡、中日文資料庫；T1 書目列出的 HindsightBench、NumLeak、DatedGPT、FinCAD 等已查核但因上限未收錄，本綜整不引用。
- **矛盾掃描**：Cross-Paper Tension Inventory 是有範圍的建議性掃描，不是完整的兩兩比較。
- 本檔未經任何外部審查或稽核步驟。
