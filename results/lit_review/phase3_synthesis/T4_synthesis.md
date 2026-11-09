# 主題 4 綜整（Phase 3，synthesis_agent）：LLM 自述知識的可靠度——模型說「我知道」時，真的知道嗎？

- 角色：ARS deep-research `synthesis_agent`，只做 Phase 3（綜整、矛盾處理、缺口分析）；不起草報告正文、不做跨主題整合
- 輸入：`results/lit_review/phase2_bibliography/T4_bibliography.md`、`T4_sources.json`；來源查核 `results/lit_review/phase2_verification/verification.md`（本主題 20 篇全部 VERIFIED）
- 研究問題：LLM 對「這家公司後來出事」的自述有多準？錯在哪裡：捏造、時間錯置，還是細節記錯？不同模型差多少？自述探針能否當記憶污染的偵測工具？
- 閱讀範圍聲明：本主題 20 篇**全部只讀到摘要**（`abstract_only`，部分另有 WebSearch 摘述）。所有綜整只到摘要層級，方法弱點未評估，引用錨點一律為 `section:abstract`。
- 證據等級說明（沿用 T4 書目）：ARS 的 I–VII 是為臨床與社會科學設計；本主題把有操控或對照的計算實驗記為 III、描述性 benchmark 記為 VI、綜述記為 V（Huang 等 (2025) <!--ref:huang2025survey--><!--anchor:section:abstract-->為敘事綜述，嚴格說低於 V）、理論論證記為 VII。
- 日期：2026-11-09

## 預定主張清單

（取代 Claim Intent Manifest；本環境沒有 Material Passport。）

| 編號 | 預定主張 | 預定依據（key） | 不可越界的限制 |
|---|---|---|---|
| C1 | LLM 有一定的自我知識，但口頭表達的信心偏向過度自信，且在新任務或專業任務上失準 | kadavath2022language、yin2023large、xiong2024can、kalai2025why | 不把機率式 P(IK) 的結果等同於自然語言自述 |
| C2 | 實體知名度同時提高模型「知道」的比例與「錯得有信心」的程度 | kandpal2023large、mallen2023when、sun2024head、ni2026popular、shah2025beyond | Shah 等 (2025) <!--ref:shah2025beyond--><!--anchor:section:abstract-->的題目是財務數值，不是執法事件 |
| C3 | 事實錯誤可分為不穩定的捏造與穩定的錯誤記憶；時間錯置與「事件—年份綁定」鬆散有關 | huang2025survey、farquhar2024detecting、dhingra2022time、cheng2024dated | 時間錯置作為獨立錯誤類型的直接研究很少 |
| C4 | 把輸出拆成原子事實、逐一對照權威來源，是查核自述的可行方法 | min2023factscore、wei2024measuring、shah2025beyond | 不宣稱自動評估器在財務執法紀錄上同樣準確 |
| C5 | 以回想或自述探針偵測記憶／污染的效度證據有限，時間切分的對照可能混入分布漂移 | golchin2024time、gao2025detecting、duan2024membership、fu2025does | 缺口以「本次檢索範圍內」為界 |

總限制：不使用未限定的因果語言；本研究實驗 D 的數字只出現在「與本研究實驗的對照」小節。

## Synthesis Report

### Literature Matrix

**Date compiled**：2026-11-09｜**Total sources**：20｜**Themes identified**：5

主題代號：
- **A** 自述知識邊界：存在但不完美，口頭信心偏高、跨分布失準
- **B** 知名度／長尾同時影響「知道多少」與「錯得多自信」
- **C** 錯誤類型：捏造、穩定錯誤記憶、時間錯置
- **D** 以權威來源做原子化查核
- **E** 回想／自述探針作為記憶與污染偵測工具的效度

符號：✓ 支持；✗ 相反或限制性證據；◐ 部分相關；— 未涉及。等級與 Tier 依 T4 書目。

| Source | Year | Level | Tier | A | B | C | D | E |
|---|---|---|---|---|---|---|---|---|
| Kadavath 等 <!--ref:kadavath2022language--><!--anchor:section:abstract--> | 2022 | III | 2 | ✗（格式內校準良好）／◐（新任務變差） | — | — | — | ◐ |
| Yin 等 <!--ref:yin2023large--><!--anchor:section:abstract--> | 2023 | VI | 1 | ✓ | — | — | — | — |
| Xiong 等 <!--ref:xiong2024can--><!--anchor:section:abstract--> | 2024 | III | 1 | ✓ | — | — | — | — |
| Wei 等 <!--ref:wei2024measuring--><!--anchor:section:abstract--> | 2024 | VI | 2 | ◐ | — | — | ✓ | — |
| Ni 等 <!--ref:ni2026popular--><!--anchor:section:abstract--> | 2026 | III | 1 | ✓ | ✓ | ◐ | — | — |
| Huang 等 <!--ref:huang2025survey--><!--anchor:section:abstract--> | 2025 | V | 1 | — | — | ✓ | — | — |
| Kalai 等 <!--ref:kalai2025why--><!--anchor:section:abstract--> | 2025 | VII | 2 | ✓ | — | ◐ | — | — |
| Farquhar 等 <!--ref:farquhar2024detecting--><!--anchor:section:abstract--> | 2024 | III | 1 | — | — | ✓ | — | — |
| Petroni 等 <!--ref:petroni2019language--><!--anchor:section:abstract--> | 2019 | VI | 1 | — | ◐ | — | — | ◐ |
| Kandpal 等 <!--ref:kandpal2023large--><!--anchor:section:abstract--> | 2023 | III | 1 | — | ✓ | — | — | — |
| Mallen 等 <!--ref:mallen2023when--><!--anchor:section:abstract--> | 2023 | III | 1 | — | ✓ | — | — | — |
| Sun 等 <!--ref:sun2024head--><!--anchor:section:abstract--> | 2024 | VI | 1 | — | ✓ | — | ◐ | — |
| Dhingra 等 <!--ref:dhingra2022time--><!--anchor:section:abstract--> | 2022 | III | 1 | — | — | ✓ | — | — |
| Cheng 等 <!--ref:cheng2024dated--><!--anchor:section:abstract--> | 2024 | VI | 1 | — | — | ✓ | — | ◐ |
| Min 等 <!--ref:min2023factscore--><!--anchor:section:abstract--> | 2023 | VI | 1 | — | — | — | ✓ | — |
| Shah 等 <!--ref:shah2025beyond--><!--anchor:section:abstract--> | 2025 | IV | 1 | — | ✓ | — | ✓ | — |
| Golchin 與 Surdeanu <!--ref:golchin2024time--><!--anchor:section:abstract--> | 2024 | III | 1 | — | — | — | — | ✓ |
| Gao 等 <!--ref:gao2025detecting--><!--anchor:section:abstract--> | 2025 | III | 2 | — | — | — | — | ✓ |
| Duan 等 <!--ref:duan2024membership--><!--anchor:section:abstract--> | 2024 | III | 1 | — | — | — | — | ✗（分布漂移） |
| Fu 等 <!--ref:fu2025does--><!--anchor:section:abstract--> | 2025 | V | 1 | — | — | — | — | ✗（假設未驗證） |
| **Totals** | | | | **4✓ 1✗ 1◐** | **5✓ 1◐** | **4✓ 2◐** | **3✓ 1◐** | **2✓ 2✗ 3◐** |

（Kadavath 等 (2022) <!--ref:kadavath2022language--><!--anchor:section:abstract--> 在 A 欄同時是反證與部分支持：選擇題與是非題在適當格式下校準良好，但 P(IK) 在新任務上校準較差；A 欄的計數中算作 1✗。）

### Key Themes

#### Theme A：模型有一定的自我知識，但口頭自述偏向過度自信，跨分布與專業任務上失準
**Evidence Strength**：Moderate
**Sources**：4 篇支持、1 篇提供限制性證據（同時部分支持）、1 篇部分相關；Levels III–VII
**Synthesis**：

本主題最直接的前例給出的是一個有條件的正面答案。Kadavath 等 (2022) <!--ref:kadavath2022language--><!--anchor:section:abstract--> 發現大型模型在適當格式下對選擇題與是非題校準良好，P(True) 的表現與規模化趨勢都不錯；但他們也報告 P(IK)（模型預測自己答不答得出來的機率）在新任務上的校準較差。這是本主題中「自我知識可靠」的主要證據，也同時劃出了它的邊界。

當評估轉到更接近本研究的條件——只看文字輸出、以自然語言表達——證據偏向負面。Xiong 等 (2024) <!--ref:xiong2024can--><!--anchor:section:abstract--> 在黑箱情境下發現 LLM 口頭表達信心時傾向過度自信；能力越強的模型校準與失誤預測越好；白箱方法較好但差距小（AUROC 0.522 vs 0.605）；需要專業知識的任務上所有方法都表現不佳。Yin 等 (2023) <!--ref:yin2023large--><!--anchor:section:abstract--> 以 SelfAware 資料集比較 20 個模型辨認「無法回答的問題」的能力，發現模型有一定的自我知識，in-context learning 與 instruction tuning 能提升，但與人類仍有明顯差距。Ni 等 (2026) <!--ref:ni2026popular--><!--anchor:section:abstract--> 發現錯誤答案中越知名者信心越高。

Kalai 等 (2025) <!--ref:kalai2025why--><!--anchor:section:abstract--> 提供了一個結構性的解釋：幻覺持續存在，是因為多數評估的評分方式獎勵猜測、懲罰表達不確定。Wei 等 (2024) <!--ref:wei2024measuring--><!--anchor:section:abstract--> 的 SimpleQA 正好把這個問題放進評分設計：答案分為正確、錯誤、未作答，理想模型應盡量答對，並對沒有把握的題目不作答。

整合來看，「模型說我知道」的可靠度取決於三個條件：(1) 自述的形式（訓練過的機率輸出 vs 自然語言）；(2) 任務是否在模型熟悉的分布內；(3) 提問方式是否讓「不知道」成為可被接受的答案。這是本綜整的整合性解讀。

#### Theme B：實體知名度同時影響「知道多少」與「錯得多有信心」
**Evidence Strength**：Moderate（知名度提高正確率的部分有多篇 Tier 1 一致支持，可視為接近 Strong；知名度提高錯誤信心的部分只有 2 篇）
**Sources**：5 篇支持、1 篇部分相關；Levels III–VI
**Synthesis**：

知識探測文獻一致顯示，模型知道多少與實體在預訓練資料中的曝光量有關。Kandpal 等 (2023) <!--ref:kandpal2023large--><!--anchor:section:abstract--> 發現答對事實題的能力與預訓練時看過的相關文件數有強相關與因果關係，大模型較能學到長尾知識，但需把規模放大好幾個數量級；Mallen 等 (2023) <!--ref:mallen2023when--><!--anchor:section:abstract--> 在 PopQA 上發現模型對較不知名的事實表現差，放大規模無法明顯改善長尾記憶，但對高知名度實體，未經檢索的模型仍有競爭力；Sun 等 (2024) <!--ref:sun2024head--><!--anchor:section:abstract--> 依 head、torso、tail 分層，發現 torso 到 tail 實體的事實知識尤其差。Petroni 等 (2019) <!--ref:petroni2019language--><!--anchor:section:abstract--> 的奠基研究已觀察到某些類型的事實知識比其他類型容易學到。

但知名度也是「錯得有信心」的來源。Ni 等 (2026) <!--ref:ni2026popular--><!--anchor:section:abstract--> 發現幻覺答案不是隨機的，傾向比正確答案更知名、或更常與問題實體共同出現；加入知名度訊號後，錯誤答案的平均信心由 0.765 降到 0.254、整體 ECE 由 0.356 降到 0.050。財務領域的 Shah 等 (2025) <!--ref:shah2025beyond--><!--anchor:section:abstract--> 以超過 19.7 萬題、對照實際財務資料，發現 LLM 對大型公司與較近年份較清楚，但同時對大型公司、尤其近年資料更容易產生幻覺；公司規模、散戶投資、機構關注與財報可讀性都和準確度有關。

這兩組結果在摘要層級看似矛盾（知名度提高正確率 vs 知名度提高幻覺），處理見 Contradictions & Resolutions。對本主題的含意是：以公司知名度分層報告自述準確度，是文獻支持的做法；而且應同時報告「說知道的比例」與「說知道時的正確率」，因為知名度可能同時推高兩者的分母。

#### Theme C：錯誤類型——不穩定的捏造、穩定的錯誤記憶、時間錯置
**Evidence Strength**：Emerging（分類框架有綜述支持；時間錯置作為獨立類型只有 2 篇間接證據）
**Sources**：4 篇支持、2 篇部分相關；Levels III–VII
**Synthesis**：

Huang 等 (2025) <!--ref:huang2025survey--><!--anchor:section:abstract--> 的綜述提供 LLM 時代的幻覺分類，並把「知識邊界」的理解列為未來方向。在這個大框架下，有兩個對本主題特別重要的區分。

第一是**捏造 vs 穩定錯誤**。Farquhar 等 (2024) <!--ref:farquhar2024detecting--><!--anchor:section:abstract--> 以語意熵偵測幻覺中的一個子類：confabulation（任意且錯誤的生成）；方法依多次抽樣後語意等價分群的熵判斷。依其定義，語意熵偵測的是「每次說法不同」的錯誤；如果模型每次都穩定地說出同一個錯誤，語意熵會偏低而偵測不到——這是依該方法的原理所做的推論，T4 書目也作此解讀。Kalai 等 (2025) <!--ref:kalai2025why--><!--anchor:section:abstract--> 的統計論證說明，當錯誤陳述與事實難以區分時，預訓練本身就會產生幻覺；Ni 等 (2026) <!--ref:ni2026popular--><!--anchor:section:abstract--> 則顯示錯誤答案傾向被較知名或較常共現的內容取代——這可以是一種穩定、有方向的錯誤。

第二是**時間錯置**。Dhingra 等 (2022) <!--ref:dhingra2022time--><!--anchor:section:abstract--> 指出，只用特定時段或混合大範圍時段資料訓練的模型各有問題，把文字與時間戳一起建模能改善對訓練期間事實的記憶。Cheng 等 (2024) <!--ref:cheng2024dated--><!--anchor:section:abstract--> 發現模型的「有效知識截止日」常與開發者公布值不同，且因子資源與主題而異，原因包括 CommonCrawl 新快照含大量舊資料與去重問題。兩者合起來支持一個機制性假說：當訓練文字的時間標記不可靠時，「事件」與「年份」的綁定會鬆散，模型可能記得事件卻記錯年份。在本次檢索範圍內，未見直接以「真實事件、錯誤年份」為錯誤類型的研究。

#### Theme D：以權威來源做原子化查核，是評估自述正確性的可行方法
**Evidence Strength**：Moderate
**Sources**：3 篇支持、1 篇部分相關；Levels IV–VI
**Synthesis**：

Min 等 (2023) <!--ref:min2023factscore--><!--anchor:section:abstract--> 的 FActScore 把長文生成拆成原子事實，逐一對照可靠知識來源；以人物傳記為題，ChatGPT 的原子事實支持率只有 58%，自動估計器的誤差低於 2%。Wei 等 (2024) <!--ref:wei2024measuring--><!--anchor:section:abstract--> 的 SimpleQA 要求每題只有單一無爭議答案，並以「正確／錯誤／未作答」三分評分。Sun 等 (2024) <!--ref:sun2024head--><!--anchor:section:abstract--> 也設計了接近「模型有信心內化之知識」的評估指標。

Shah 等 (2025) <!--ref:shah2025beyond--><!--anchor:section:abstract--> 是唯一把這套邏輯搬到美國上市公司的研究：以實際財務資料當 ground truth、以公司特徵為解釋變數。這提供了兩個可借用的設計：權威資料作為 ground truth、公司特徵作為準確度的解釋變數。

需要保留的是：FActScore 的知識來源是維基百科、SimpleQA 是對抗式蒐集的短答題、Shah 等 (2025) <!--ref:shah2025beyond--><!--anchor:section:abstract-->的題目是財務數值。在執法事件（重編、SEC 處分）這類類別界線本身需要判定規則的事實上，原子化查核的「單一無爭議答案」前提可能不成立——例如「重編」與「SEC 處分」是否算同一類事件。這是本綜整對外推的保留。

#### Theme E：回想／自述探針作為記憶與污染偵測工具，效度證據有限
**Evidence Strength**：Contested
**Sources**：2 篇支持、2 篇提出效度質疑、3 篇部分相關；Levels III–VI
**Synthesis**：

兩篇研究以黑箱的行為探針偵測記憶，並報告了正面結果。Golchin 與 Surdeanu (2024) <!--ref:golchin2024time--><!--anchor:section:abstract--> 給模型資料集名、分割與例句開頭，請它補完；輸出與原文完全或近乎相同即判為污染；最佳方法與人類專家判定相比準確率 92%–100%。Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract--> 以「只給公司與日期」的回想查詢估計 LAP，LAP 在樣本期內為正、截止後幾乎歸零，且高 LAP 樣本的預測力被放大。

但效度問題有兩個來源。第一，Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract--> 指出先前看似成功的成員推論，可歸因於成員與非成員來自相同領域但時間範圍不同的分布偏移。Fu 等 (2025) <!--ref:fu2025does--><!--anchor:section:abstract--> 回顧 50 篇污染偵測研究，歸納八類假設並檢視是否經嚴謹驗證；個案研究顯示資料在見過與未見過之間有分布偏移時，MIA 很容易失效，且模型可能學到資料分布而非記住個別實例。第二，Cheng 等 (2024) <!--ref:cheng2024dated--><!--anchor:section:abstract--> 的「有效截止日」發現意味：以公布截止日界定「截止後」樣本，本身可能有誤差。

這兩方並非單純矛盾。Golchin 與 Surdeanu (2024) <!--ref:golchin2024time--><!--anchor:section:abstract--> 偵測的是逐字補完（資料集分割層級），Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract-->偵測的是事件結果的回想，Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract-->與 Fu 等 (2025) <!--ref:fu2025does--><!--anchor:section:abstract-->評估的主要是實例層級的 MIA。但三者共同指出一個尚未被回答的問題：以「模型說它知道」或「模型回想得出」作為「模型在訓練中見過這件事」的證據，需要什麼假設、這些假設是否成立。Kadavath 等 (2022) <!--ref:kadavath2022language--><!--anchor:section:abstract--> 的 P(IK) 與 Petroni 等 (2019) <!--ref:petroni2019language--><!--anchor:section:abstract--> 的知識探測，是這類探針的方法源頭，但它們量的是「答不答得出」，而不是「見過與否」。

### Contradictions & Resolutions

| Claim A | Claim B | Resolution |
|---|---|---|
| Kadavath 等 (2022) <!--ref:kadavath2022language--><!--anchor:section:abstract-->：大型模型在適當格式下校準良好，大致知道自己知道什麼 | Xiong 等 (2024) <!--ref:xiong2024can--><!--anchor:section:abstract-->：口頭表達信心傾向過度自信；Yin 等 (2023) <!--ref:yin2023large--><!--anchor:section:abstract-->：辨認知識邊界的能力與人類仍有明顯差距 | **可調和（條件性差異）**。Kadavath 等 (2022) <!--ref:kadavath2022language--><!--anchor:section:abstract-->的良好校準限於選擇題、是非題與適當格式，且 P(IK) 需監督式訓練、在新任務上變差；Xiong 等 (2024) <!--ref:xiong2024can--><!--anchor:section:abstract-->量的是黑箱口頭信心，Yin 等 (2023) <!--ref:yin2023large--><!--anchor:section:abstract-->量的是辨認無法回答的問題。差異主要來自自述的形式與分布。這組證據中，Kadavath 等 (2022) <!--ref:kadavath2022language--><!--anchor:section:abstract-->是「自述可以可靠」的反面證據，應保留。 |
| Kandpal 等 (2023) <!--ref:kandpal2023large--><!--anchor:section:abstract-->、Mallen 等 (2023) <!--ref:mallen2023when--><!--anchor:section:abstract-->：知名度越高，答對率越高 | Ni 等 (2026) <!--ref:ni2026popular--><!--anchor:section:abstract-->：錯誤答案中越知名者信心越高；Shah 等 (2025) <!--ref:shah2025beyond--><!--anchor:section:abstract-->：對大型公司更清楚，但也更容易幻覺 | **部分可調和，部分未解決**。知名度同時提高「有答案可給」與「給答案時的信心」；Ni 等 (2026) <!--ref:ni2026popular--><!--anchor:section:abstract-->描述的是錯誤答案的組成，而非知名實體的整體錯誤率，因此與前兩篇不直接衝突。但 Shah 等 (2025) <!--ref:shah2025beyond--><!--anchor:section:abstract-->在同一樣本中同時觀察到「更清楚」與「更常幻覺」，摘要層級無法判斷幻覺率是以全部題目還是以作答題目為分母。 |
| Golchin 與 Surdeanu (2024) <!--ref:golchin2024time--><!--anchor:section:abstract-->：黑箱補完法與人類專家判定一致 92%–100% | Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract-->、Fu 等 (2025) <!--ref:fu2025does--><!--anchor:section:abstract-->：MIA 多數接近隨機；偵測假設常未經驗證 | **可調和（層級不同）**。前者偵測資料集分割層級的逐字污染並以專家判定為準；後者評估實例層級的成員推論。Fu 等 (2025) <!--ref:fu2025does--><!--anchor:section:abstract-->的「八類假設」仍適用於前者，摘要層級無法確認前者的假設是否全部成立。 |
| Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract-->：LAP 在截止前為正、截止後歸零 | Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract-->：時間範圍不同的對照可被分布偏移解釋 | **未解決（flagged）**。Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract-->以交互項設計增加了一層結構，可能部分緩解漂移，但摘要層級無法確認。 |
| Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract-->：以訓練截止日為界的前後對照 | Cheng 等 (2024) <!--ref:cheng2024dated--><!--anchor:section:abstract-->：有效截止日常與公布值不同，且因資源與主題而異 | **可調和**。後者不否定前者的結果，但提醒「截止後」的界定需要實證確認（例如以探針估計有效截止日），不能只依公布值。 |
| Farquhar 等 (2024) <!--ref:farquhar2024detecting--><!--anchor:section:abstract-->：語意熵可偵測 confabulation | Dhingra 等 (2022) <!--ref:dhingra2022time--><!--anchor:section:abstract-->：時間知識的錯誤可來自訓練資料的時間結構 | **非矛盾，互補**。語意熵依原理偵測不穩定的錯誤；源自時間結構的錯誤可能是穩定的，需要外部紀錄查核而非一致性檢驗。 |

#### Cross-Paper Tension Inventory (#262)

```yaml
cross_paper_tensions:
  - pair_id: CP-001
    paper_a: "kadavath2022language"
    paper_b: "xiong2024can"
    candidate_basis: "opposite finding direction"
    overlap_topic: "模型對自己知識的判斷是否可靠"
    a_finding: "適當格式下校準良好；P(IK) 可訓練但新任務校準較差"
    a_evidence_pointer: "T4_bibliography.md #1 Key Findings（摘要）"
    b_finding: "口頭信心傾向過度自信；專業任務上所有方法表現不佳"
    b_evidence_pointer: "T4_bibliography.md #3 Key Findings（摘要）"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶1"
    scholar_confirmation: "pending"
  - pair_id: CP-002
    paper_a: "kadavath2022language"
    paper_b: "yin2023large"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "自我知識的程度"
    a_finding: "大型模型大致知道自己知道什麼（格式內）"
    a_evidence_pointer: "T4_bibliography.md #1 Key Findings"
    b_finding: "20 個 LLM 有一定自我知識，但與人類有明顯差距"
    b_evidence_pointer: "T4_bibliography.md #2 Key Findings"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶1"
    scholar_confirmation: "pending"
  - pair_id: CP-003
    paper_a: "mallen2023when"
    paper_b: "ni2026popular"
    candidate_basis: "opposite finding direction"
    overlap_topic: "實體知名度與回答品質"
    a_finding: "對較不知名的事實表現差；高知名度實體未經檢索仍有競爭力"
    a_evidence_pointer: "T4_bibliography.md #11 Key Findings"
    b_finding: "幻覺答案傾向更知名；錯誤答案中越知名者信心越高"
    b_evidence_pointer: "T4_bibliography.md #5 Key Findings"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶2"
    scholar_confirmation: "pending"
  - pair_id: CP-004
    paper_a: "kandpal2023large"
    paper_b: "shah2025beyond"
    candidate_basis: "opposite finding direction"
    overlap_topic: "知名度（文件數／公司規模）與事實正確性"
    a_finding: "答對率與相關文件數有強相關與因果關係"
    a_evidence_pointer: "T4_bibliography.md #10 Key Findings"
    b_finding: "對大型公司更清楚，但也更容易幻覺，尤其近年資料"
    b_evidence_pointer: "T4_bibliography.md #16 Key Findings"
    pair_assessment: "contradiction"
    resolution_status: "flagged_unresolved"
    scholar_confirmation: "pending"
  - pair_id: CP-005
    paper_a: "mallen2023when"
    paper_b: "kandpal2023large"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "放大規模能否改善長尾知識"
    a_finding: "放大規模無法明顯改善長尾記憶"
    a_evidence_pointer: "T4_bibliography.md #11 Key Findings"
    b_finding: "大模型較能學到長尾，但需放大好幾個數量級"
    b_evidence_pointer: "T4_bibliography.md #10 Key Findings"
    pair_assessment: "no_material_conflict"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"
  - pair_id: CP-006
    paper_a: "golchin2024time"
    paper_b: "fu2025does"
    candidate_basis: "opposite finding direction"
    overlap_topic: "黑箱污染偵測的效度"
    a_finding: "guided instruction 補完法與專家判定一致 92%–100%"
    a_evidence_pointer: "T4_bibliography.md #17 Key Findings"
    b_finding: "50 篇偵測研究的八類假設多未經嚴謹驗證；分布偏移時 MIA 易失效"
    b_evidence_pointer: "T4_bibliography.md #20 Key Findings"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶3"
    scholar_confirmation: "pending"
  - pair_id: CP-007
    paper_a: "gao2025detecting"
    paper_b: "duan2024membership"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "時間切分的對照能否當記憶證據"
    a_finding: "LAP 截止前為正、截止後歸零"
    a_evidence_pointer: "T4_bibliography.md #18 Key Findings"
    b_finding: "時間範圍不同的成員／非成員對照可被分布偏移解釋"
    b_evidence_pointer: "T4_bibliography.md #19 Key Findings"
    pair_assessment: "conditional_difference"
    resolution_status: "flagged_unresolved"
    scholar_confirmation: "pending"
  - pair_id: CP-008
    paper_a: "gao2025detecting"
    paper_b: "cheng2024dated"
    candidate_basis: "agent-noted cross-cluster"
    overlap_topic: "訓練截止日作為記憶邊界"
    a_finding: "以截止日為界，截止後 LAP 幾乎歸零"
    a_evidence_pointer: "T4_bibliography.md #18 Key Findings"
    b_finding: "有效截止日常與公布值不同，因資源與主題而異"
    b_evidence_pointer: "T4_bibliography.md #14 Key Findings"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶5"
    scholar_confirmation: "pending"
  - pair_id: CP-009
    paper_a: "farquhar2024detecting"
    paper_b: "dhingra2022time"
    candidate_basis: "agent-noted cross-cluster"
    overlap_topic: "事實錯誤的偵測與來源"
    a_finding: "語意熵偵測 confabulation（任意、錯誤的生成）"
    a_evidence_pointer: "T4_bibliography.md #8 Key Findings（Crossref 摘要）"
    b_finding: "時間戳建模改善時變事實的記憶與校準"
    b_evidence_pointer: "T4_bibliography.md #13 Key Findings"
    pair_assessment: "no_material_conflict"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"
  - pair_id: CP-010
    paper_a: "kalai2025why"
    paper_b: "wei2024measuring"
    candidate_basis: "shared RQ subtopic"
    overlap_topic: "評分方式與「不知道」的處理"
    a_finding: "多數評估獎勵猜測、懲罰不確定，使幻覺持續"
    a_evidence_pointer: "T4_bibliography.md #7 Key Findings"
    b_finding: "SimpleQA 以正確／錯誤／未作答三分，鼓勵不作答"
    b_evidence_pointer: "T4_bibliography.md #4 Key Findings"
    pair_assessment: "no_material_conflict"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"
  - pair_id: CP-011
    paper_a: "xiong2024can"
    paper_b: "shah2025beyond"
    candidate_basis: "agent-noted cross-cluster"
    overlap_topic: "模型能力與錯誤的關係"
    a_finding: "能力越強的模型校準越好"
    a_evidence_pointer: "T4_bibliography.md #3 Key Findings"
    b_finding: "公司規模與關注度越高，越常幻覺（公司特徵，不是模型特徵）"
    b_evidence_pointer: "T4_bibliography.md #16 Key Findings"
    pair_assessment: "insufficient_overlap"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"
```

**Coverage Note**：20 papers in corpus; 11 candidate pairs considered（basis：shared construct／shared RQ subtopic／opposite finding direction／agent-noted cross-cluster；沒有引用網絡資料，未使用 bibliographic coupling；沒有 scholar flag）。This is a **scoped advisory scan, not complete pairwise contradiction detection** — cross-neighborhood pairs not surfaced here may exist and are not claimed absent（例如 Min 等 (2023) <!--ref:min2023factscore--><!--anchor:section:abstract--> 的自動估計器與 Shah 等 (2025) <!--ref:shah2025beyond--><!--anchor:section:abstract--> 的財務 ground truth 在評分可靠度上的差異、Sun 等 (2024) <!--ref:sun2024head--><!--anchor:section:abstract--> 與 Ni 等 (2026) <!--ref:ni2026popular--><!--anchor:section:abstract--> 對 head 實體的不同觀察，未逐一評估）。所有 evidence pointer 只到摘要層級。Scholar confirms each `resolution_pointer` and may flag additional cross-pairs.

### Knowledge Gaps

1. **在本次檢索範圍內，未見以 SEC 執法紀錄（AAER、8-K 4.02）查核 LLM 對公司事件之記憶的研究**（Empirical／領域）。最接近的 Shah 等 (2025) <!--ref:shah2025beyond--><!--anchor:section:abstract--> 查核的是財務數值，Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract--> 的回想查詢未對照外部紀錄。含意：「LLM 記得哪些公司出過事、記得多準」沒有既有估計。
2. **「時間錯置」（記得真實事件、套錯年份）作為獨立錯誤類型的直接研究**（Theoretical／Empirical）。本次檢索只找到 Dhingra 等 (2022) <!--ref:dhingra2022time--><!--anchor:section:abstract--> 與 Cheng 等 (2024) <!--ref:cheng2024dated--><!--anchor:section:abstract--> 兩篇間接相關的研究；Huang 等 (2025) <!--ref:huang2025survey--><!--anchor:section:abstract--> 的分類在摘要層級未見對應細類。T4 書目也記錄 Herel 等與 LLMLagBench 因只讀到題名或二手摘述而未收，可在下一輪補入。
3. **自述探針的效度假設未經驗證**（Methodological）。Fu 等 (2025) <!--ref:fu2025does--><!--anchor:section:abstract--> 指出污染偵測的假設多未經嚴謹驗證；在本次檢索範圍內，未見研究檢驗「模型說它知道某事件 ⇒ 該事件在訓練資料中」這個假設，也未見以自然語言自述（而非機率）作為記憶指標的效度研究。
4. **跨模型家族（尤其 Claude 系列）的自述差異，以及自述與人類專家查核的比較**（Empirical）。T4 書目記錄在本次檢索範圍內未找到直接文獻。
5. **財務領域的覆蓋**（Empirical）：20 篇中只有 2 篇屬財務或公司領域（Shah 等 (2025) <!--ref:shah2025beyond--><!--anchor:section:abstract-->、Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract-->），且都不是執法事件。

### Evidence Convergence Map

```
Strong:      [          ] （無；全部只讀摘要）
Moderate:    [=======   ] Theme B 知名度同時影響知道與錯得自信（5 支持／1 部分；正確率部分接近 Strong）
Moderate:    [======    ] Theme A 自述知識邊界不完美（4 支持／1 限制／1 部分，Levels III–VII）
Moderate:    [=====     ] Theme D 權威來源原子化查核（3 支持／1 部分，Levels IV–VI）
Emerging:    [====      ] Theme C 錯誤類型（4 支持／2 部分；時間錯置僅 2 篇間接）
Contested:   [====      ] Theme E 探針作為記憶偵測工具的效度（2 支持／2 質疑／3 部分）
Gap:         [          ] 以 SEC 執法紀錄查核事件記憶；自然語言自述作為記憶指標的效度（0 篇，在本次檢索範圍內）
```

### Theoretical Integration

本主題的文獻可整合為一個「自述的兩段式結構」：模型說「我知道某公司出過事，問題是 X」可以拆成 (1) **知不知道的判斷**（是否宣稱知道），與 (2) **內容的正確性**（宣稱的內容是否與權威紀錄相符）。

- 第 (1) 段屬於校準與自我知識的問題（Theme A）。Kadavath 等 (2022) <!--ref:kadavath2022language--><!--anchor:section:abstract--> 與 Xiong 等 (2024) <!--ref:xiong2024can--><!--anchor:section:abstract--> 顯示，它的可靠度取決於自述形式與分布；Kalai 等 (2025) <!--ref:kalai2025why--><!--anchor:section:abstract--> 說明提問與評分方式會系統性地推高「宣稱知道」的比例。
- 第 (2) 段屬於事實性的問題（Theme C、D）。它的錯誤可分為不穩定的捏造（Farquhar 等 (2024) <!--ref:farquhar2024detecting--><!--anchor:section:abstract--> 可偵測）與穩定的錯誤記憶；後者又可能有方向：被更知名的內容取代（Ni 等 (2026) <!--ref:ni2026popular--><!--anchor:section:abstract-->），或事件與年份綁定鬆散（Dhingra 等 (2022) <!--ref:dhingra2022time--><!--anchor:section:abstract-->）。
- **知名度**橫跨兩段（Theme B）：它提高宣稱知道的比例，也影響內容的正確性與錯誤的方向（Mallen 等 (2023) <!--ref:mallen2023when--><!--anchor:section:abstract-->、Shah 等 (2025) <!--ref:shah2025beyond--><!--anchor:section:abstract-->）。
- 當自述被用作**記憶偵測工具**（Theme E）時，還需要第三個條件：(3) 宣稱知道且內容正確，是否意味著訓練中見過該事件。Fu 等 (2025) <!--ref:fu2025does--><!--anchor:section:abstract--> 與 Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract--> 顯示，這類「見過」的推論在文獻中常依賴未驗證的假設。

這個框架的含意是：評估自述探針需要分開報告三個量——宣稱率、宣稱時的正確率（對照權威紀錄）、錯誤的類型分布——而且要以知名度分層。這是本綜整的整合性推論。

### 與本研究實驗的對照

（以下為本研究自身實驗，取自 `results/research_topics.md`，**不是文獻**，不作為已確立的發現。）

- **實驗 D：254 則自述對照 SEC 紀錄，第八輪問題公司 Opus 97%、Sonnet 86%、Haiku 83% 相符；說得出問題類型的比例 86%、69%、40%**：在框架中對應第 (2) 段的「宣稱時的正確率」，以 SEC 紀錄為權威來源，屬 Min 等 (2023) <!--ref:min2023factscore--><!--anchor:section:abstract--> 的原子化查核邏輯（可進一步拆成「有無事件」「事件類型」「年份」「科目」等原子事實）。模型間的順序與 Xiong 等 (2024) <!--ref:xiong2024can--><!--anchor:section:abstract-->「能力越強校準越好」的方向一致。
- **Sonnet 對沒有紀錄的公司常說「知道」（時間外 33 則中 32 則無紀錄支持）**：對應第 (1) 段的過度宣稱，與 Kadavath 等 (2022) <!--ref:kadavath2022language--><!--anchor:section:abstract-->「P(IK) 在新任務上校準變差」、Kalai 等 (2025) <!--ref:kalai2025why--><!--anchor:section:abstract-->「評分獎勵猜測」的機制相容；但它不符合「能力越強校準越好」的單調趨勢（Sonnet 在此比 Haiku 差），值得在討論中說明。探針題目是否提供明確的「不知道」選項，會影響這個結果（Kalai 等 (2025) <!--ref:kalai2025why--><!--anchor:section:abstract-->、Wei 等 (2024) <!--ref:wei2024measuring--><!--anchor:section:abstract-->）。
- **時間錯置：三個模型都記得 Welbilt 真實的 2016 年重編，卻套到被問的 2018 年**：屬於穩定的錯誤記憶，語意熵（Farquhar 等 (2024) <!--ref:farquhar2024detecting--><!--anchor:section:abstract-->）依原理可能偵測不到；機制上與 Dhingra 等 (2022) <!--ref:dhingra2022time--><!--anchor:section:abstract--> 的「事件—年份綁定」假說一致。這類錯誤在本次檢索範圍內缺乏直接研究（Gap 2）。
- **細節記錯：GTT 把「營業成本」記成「營收」；Evoqua 說被重編（實際只有 SEC 處分）**：可用 Ni 等 (2026) <!--ref:ni2026popular--><!--anchor:section:abstract--> 的「被較常見內容取代」作為機制假說（營收、重編是較常見的舞弊敘事）；這是假說，不是文獻的結論。Evoqua 的例子也說明 Theme D 的保留：「重編 vs 處分」需要事先定義判定規則。
- **自述探針能否當記憶污染偵測工具**：依 Theme E，本研究以 SEC 紀錄查核自述的正確性，比 Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract--> 的 LAP 多了外部對照；但「說知道且正確 ⇒ 訓練中見過」仍是 Fu 等 (2025) <!--ref:fu2025does--><!--anchor:section:abstract--> 所說的未驗證假設，時間內外的比較也受 Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract--> 的分布偏移限制。

### Synthesis Limitations

- **閱讀深度**：20 篇全部只讀摘要或 WebSearch 摘述，方法弱點未評估；關鍵數字（如 Ni 等 (2026) <!--ref:ni2026popular--><!--anchor:section:abstract-->的 ECE、Shah 等 (2025) <!--ref:shah2025beyond--><!--anchor:section:abstract-->的公司特徵效果）只能引用摘要所寫。
- **錨點**：所有引用錨點為 `section:abstract`；T4 書目未記錄逐字引文，因此沒有 `quote` 錨點。
- **證據等級的調整**：本主題沿用 T4 書目把 I–VII 對應到計算實驗的做法，與臨床或社會科學的等級意義不同；Huang 等 (2025) <!--ref:huang2025survey--><!--anchor:section:abstract-->的 V 嚴格說偏高。
- **出版狀態**：Cheng 等 (2024) <!--ref:cheng2024dated--><!--anchor:section:abstract-->、Duan 等 (2024) <!--ref:duan2024membership--><!--anchor:section:abstract-->、Shah 等 (2025) <!--ref:shah2025beyond--><!--anchor:section:abstract-->的 COLM 收錄依 arXiv 註記與 WebSearch；Ni 等 (2026) <!--ref:ni2026popular--><!--anchor:section:abstract-->的 DOI 字串格式與一般 ACL DOI 不同，已由 Crossref 查核相符。4 篇為預印本（Kadavath 等 (2022) <!--ref:kadavath2022language--><!--anchor:section:abstract-->、Wei 等 (2024) <!--ref:wei2024measuring--><!--anchor:section:abstract-->、Kalai 等 (2025) <!--ref:kalai2025why--><!--anchor:section:abstract-->、Gao 等 (2025) <!--ref:gao2025detecting--><!--anchor:section:abstract-->）。
- **known-item 偏誤**：奠基文獻部分依領域知識列為候選再查核，可能偏向高被引的英文 NLP 文獻。
- **矛盾掃描**：Cross-Paper Tension Inventory 是有範圍的建議性掃描，不是完整的兩兩比較。
- 本檔未經任何外部審查或稽核步驟。
