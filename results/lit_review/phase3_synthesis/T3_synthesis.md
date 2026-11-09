# 主題 3 綜整（Phase 3，synthesis_agent）：匿名化與再識別的取捨——財務資訊要粗到什麼程度，LLM 才認不出公司、又不失判斷力？

- 角色：ARS deep-research `synthesis_agent`，只做 Phase 3（綜整、矛盾處理、缺口分析）；不起草報告正文、不做跨主題整合
- 輸入：`results/lit_review/phase2_bibliography/T3_bibliography.md`、`T3_sources.json`；來源查核 `results/lit_review/phase2_verification/verification.md`（本主題 20 篇全部 VERIFIED）
- 研究問題：給 LLM 的財務資訊，粗化到哪一級才能擋住「認出公司 → 用上記憶」，同時保留判斷舞弊所需的資訊？「有名單的封閉式辨識」與「沒有名單的開放式辨識」該用哪個當標準？
- 閱讀範圍聲明：16 篇只讀摘要（`abstract_only`）；4 篇讀了指定章節（`sections`：Greve 與 Sablica (2025) <!--ref:greve2025swapping--><!--anchor:section:3.2.2-->、Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:appendix-A-->、Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:5-->、Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:section:3.1-->；以 WebFetch 讀 arXiv HTML，由工具擷取章節與原文短句）。章節錨點與引文錨點只用於書目明確記錄章節或原文的內容。
- **Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract--> 的兩個摘要版本**：T3 書目記錄兩個數字不同的摘要版本（SSRN 本站無法連線，未能核對最新版）。本綜整**兩個版本都報告，不選擇其中一個**：
  - 版本甲：超過 50 萬篇新聞，遮蔽後的辨識率降到隨機水準
  - 版本乙：100 萬篇新聞，約 90% 的文章認不出公司或時期；這些文章的原文與遮蔽後情緒判斷 90% 一致、報酬預測力相近，差距可當前視偏誤的上限
- 日期：2026-11-09

## 預定主張清單

（取代 Claim Intent Manifest；本環境沒有 Material Passport。）

| 編號 | 預定主張 | 預定依據（key） | 不可越界的限制 |
|---|---|---|---|
| C1 | 只遮蔽公司名稱等直接識別子，通常不足以阻止 LLM 從文字脈絡推回公司或個人 | lopezlira2025memorization、efe2026earnings、staab2024beyond、lermen2026deanonymization、wen2026agentdoxx、greve2025swapping | 結論來自文字輸入；不外推到純數字表格 |
| C2 | 再識別率高度依賴輸入形式（文字 vs 表格）與評估設定（有無候選名單、能否棄權、母體大小），因此「封閉式」與「開放式」辨識不能互換 | sugiura2026edinet、efe2026earnings、lermen2026deanonymization、wen2026agentdoxx、krco2026ratbench、rocher2019estimating | 財務領域的正式比較在本次檢索範圍內未見 |
| C3 | 匿名化對下游判斷的影響方向不一：有研究報告資訊損失，也有研究報告移除身分後表現持平或變好 | wu2025anonymization、glasserman2024lookahead、engelberg2025neutering | Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract-->兩個摘要版本並陳，不選擇 |
| C4 | 以攻擊者結果為回饋的迭代式匿名化，與 SDC 的風險—效用框架，提供了把「粗化等級」當參數的方法 | engelberg2025neutering、staab2025anonymizers、loiseau2026adaptive、greve2025swapping、shlomo2010releasing | 不宣稱有通用最佳等級 |
| C5 | LLM 攻擊者降低了再識別的成本，使經典 SDC 的假設需要重新校準 | thees2026agentic、lermen2026deanonymization、staab2024beyond、narayanan2008robust、sweeney2002kanonymity | Thees 等為可行性研究，樣本小 |

總限制：不使用未限定的因果語言；本研究的匿名化階梯結果只出現在「與本研究實驗的對照」小節。

## Synthesis Report

### Literature Matrix

**Date compiled**：2026-11-09｜**Total sources**：20｜**Themes identified**：5

主題代號：
- **A** 只遮蔽直接識別子不足以阻止再識別
- **B** 再識別率取決於輸入形式與評估設定（封閉 vs 開放）
- **C** 匿名化對下游判斷的影響方向不一（資訊損失 vs 去除分心）
- **D** 以攻擊者回饋校準的匿名化與風險—效用框架
- **E** 經典 SDC 假設在 LLM 攻擊者下需要重新校準

符號：✓ 支持；✗ 相反或限制性證據；◐ 部分相關；— 未涉及。等級與 Tier 依 T3 書目。

| Source | Year | Level | Tier | 讀取 | A | B | C | D | E |
|---|---|---|---|---|---|---|---|---|---|
| Engelberg 等 <!--ref:engelberg2025neutering--><!--anchor:section:abstract--> | 2025 | III | 2 | abstract（兩版本） | ◐（迭代改寫可大幅壓低辨識） | — | ✗（版本乙：情緒 90% 一致、預測力相近） | ✓ | — |
| Lopez-Lira 等 <!--ref:lopezlira2025memorization--><!--anchor:section:abstract--> | 2025 | III | 2 | abstract | ✓ | — | — | — | — |
| Wu 等 <!--ref:wu2025anonymization--><!--anchor:section:abstract--> | 2025 | III | 2 | abstract | — | — | ✓（資訊損失） | ◐ | — |
| Glasserman 與 Lin <!--ref:glasserman2024lookahead--><!--anchor:section:abstract--> | 2024 | III | 1 | abstract | — | — | ✗（時間內匿名化較好） | — | — |
| Greve 與 Sablica <!--ref:greve2025swapping--><!--anchor:section:3.2.2--> | 2025 | III | 2 | sections | ✓ | ✓ | ◐ | ✓ | ◐ |
| Efe 等 <!--ref:efe2026earnings--><!--anchor:section:appendix-A--> | 2026 | IV | 2 | sections | ✓ | ✓ | — | — | — |
| Sugiura 等 <!--ref:sugiura2026edinet--><!--anchor:section:5--> | 2026 | VI | 1 | sections | ✗（表格輸入辨識 ≤ 0.05） | ✓ | — | — | — |
| Staab 等 (2024) <!--ref:staab2024beyond--><!--anchor:section:abstract--> | 2024 | VI | 1 | abstract | ✓ | — | — | — | ✓ |
| Lermen 等 <!--ref:lermen2026deanonymization--><!--anchor:section:3.1--> | 2026 | III | 2 | sections | ✓ | ✓ | — | — | ✓ |
| Wen 與 Li <!--ref:wen2026agentdoxx--><!--anchor:section:abstract--> | 2026 | III | 2 | abstract | ✓ | ✓ | — | — | ✓ |
| Thees 等 <!--ref:thees2026agentic--><!--anchor:section:abstract--> | 2026 | VI | 1 | abstract | ✓ | — | — | — | ✓ |
| Pilán 等 <!--ref:pilan2022tab--><!--anchor:section:abstract--> | 2022 | VI | 1 | abstract | — | ◐ | — | ✓ | — |
| Manzanares-Salor 等 <!--ref:manzanaressalor2024disclosure--><!--anchor:section:abstract--> | 2024 | III | 1 | abstract | — | ✓ | — | ✓ | — |
| Staab 等 (2025) <!--ref:staab2025anonymizers--><!--anchor:section:abstract--> | 2025 | III | 1 | abstract | — | — | ✓ | ✓ | — |
| Loiseau 等 <!--ref:loiseau2026adaptive--><!--anchor:section:abstract--> | 2026 | III | 1 | abstract | — | — | ✓ | ✓ | — |
| Krčo 等 <!--ref:krco2026ratbench--><!--anchor:section:abstract--> | 2026 | III | 2 | abstract | ◐ | ✓ | ◐ | ✓ | — |
| Sweeney <!--ref:sweeney2002kanonymity--><!--anchor:section:abstract--> | 2002 | VII | 1 | abstract | — | — | — | ✓ | ✓ |
| Narayanan 與 Shmatikov <!--ref:narayanan2008robust--><!--anchor:section:abstract--> | 2008 | VI | 1 | abstract | ✓ | — | — | — | ✓ |
| Rocher 等 <!--ref:rocher2019estimating--><!--anchor:section:abstract--> | 2019 | IV | 1 | abstract | ✓ | ✓ | — | — | ✓ |
| Shlomo <!--ref:shlomo2010releasing--><!--anchor:section:abstract--> | 2010 | VI | 1 | abstract | — | — | ✓ | ✓ | ✓ |
| **Totals** | | | | | **9✓ 1✗ 2◐** | **8✓ 1◐** | **4✓ 2✗ 2◐** | **9✓ 1◐** | **8✓ 1◐** |

### Key Themes

#### Theme A：只遮蔽直接識別子，通常不足以阻止 LLM 推回身分
**Evidence Strength**：Moderate（跨領域多篇一致；但財務領域的直接證據只有 3 篇，且皆為文字輸入）
**Sources**：9 篇支持、1 篇提供相反證據、2 篇部分相關；Levels III–VI

**Synthesis**：

在財務文字上，三篇研究從不同角度得到相同方向的結果。Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract--> 的摘要稱遮蔽失敗，因為 LLM 能從很少的上下文重建實體與日期。Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:appendix-A--> 在遮蔽公司名、ticker、人名後，Qwen3.5-27B 仍以完全相符的 ticker 認出 66% 的法說會逐字稿（327 份中 217 份），寬鬆標準 75%，連大寫字、數字、年份都移除的強遮蔽仍有 63%；作者確認 217 份正確者的輸入中都沒有 ticker。Greve 與 Sablica (2025) <!--ref:greve2025swapping--><!--anchor:section:3.2.2--> 在具名實體交換之後，GPT-4o 以 ticker 認出公司的準確率仍有 0.564（交換前 0.888），Gemini 2.5 Flash 為 0.602（交換前 0.934）。

一般隱私文獻提供了機制：LLM 能從文字推論屬性組合，再由屬性組合推回身分。Staab 等 (2024) <!--ref:staab2024beyond--><!--anchor:section:abstract--> 在真實 Reddit 個人檔案上，LLM 推論位置、收入、性別等屬性 top-1 最高 85%，摘要稱文字匿名化與模型對齊目前都擋不住。Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:section:2.1--> 的網路代理在 HN 上以 90% precision 認出 338 人中的 226 人；Wen 與 Li (2026) <!--ref:wen2026agentdoxx--><!--anchor:section:abstract--> 在實體遮蔽後的分層樣本中，85.3% 至少有一個攻擊者成功；Thees 等 (2026) <!--ref:thees2026agentic--><!--anchor:section:abstract--> 的可行性研究中，LLM agent 從時空座標認出 25 個可再識別者中的 18 人。經典文獻早已說明背後的統計原因：Narayanan 與 Shmatikov (2008) <!--ref:narayanan2008robust--><!--anchor:section:abstract--> 顯示高維稀疏資料只需少量背景知識即可比對，Rocher 等 (2019) <!--ref:rocher2019estimating--><!--anchor:section:abstract--> 估計 15 個人口屬性即可正確再識別 99.98% 的美國人。

本主題中最重要的相反證據來自 Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:5-->：只輸入資產負債表、現金流量表、損益表與摘要表（不含公司名與確切年份）、開放式作答時，7 個模型的公司名準確率都 ≤ 0.05。這顯示「遮蔽不足」的結論在文字輸入上一致，但在純數字表格上可能不成立；差異的處理見 Contradictions & Resolutions。Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract--> 也顯示，若不是一次性遮蔽，而是反覆遮蔽並改寫直到另一個 LLM 認不出，辨識率可以壓得很低（版本甲：降到隨機水準；版本乙：約 90% 的文章認不出公司或時期）。

#### Theme B：再識別率取決於輸入形式與評估設定；封閉式與開放式辨識不能互換
**Evidence Strength**：Moderate（方法論上有明確框架；財務領域的直接比較在本次檢索範圍內未見）
**Sources**：8 篇支持、1 篇部分相關；Levels III–VI

**Synthesis**：

「LLM 認不認得出這家公司」沒有單一答案，它取決於至少四個評估設定。

1. **有沒有候選名單（封閉 vs 開放）**。Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:section:3.1--> 明確區分給定候選資料庫的封閉世界與網路代理的開放情境，並主張封閉世界中攻擊者應在沒有相符候選時棄權；HN→LinkedIn 封閉世界 recall 為 54.2% @90% precision，經典 Narayanan 方法約 0.1%（Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:section:table-1-->）。
2. **能不能棄權、查詢有沒有對應**。Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:section:3.1--> 以「非棄權的猜測」為 precision 的分母（Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:section:3.3-->），並在 §6.4 引入「查詢有對應」的先驗 π：π 只影響 precision，即使 π = 0.0001，90% precision 下 recall 仍至少 9%（Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:section:6.4-->）。他們也自承多數封閉世界實驗假設每個查詢都有對應，且有真實身分連結的檔案本身較容易被認出，可能高估攻擊的 recall（Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:quote:might%20overestimate%20an%20attack%27s%20recall-->）。相對地，Greve 與 Sablica (2025) <!--ref:greve2025swapping--><!--anchor:section:appendix-A--> 的辨識測試要求模型只回一個 ticker、沒有「不知道」選項、也沒有候選名單；T3 書目指出，在只有一個產業的小樣本中，猜測與真正辨識無法區分。
3. **輸入是文字還是表格**。Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:appendix-A--> 的開放式作答在法說會文字上達 66%，Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:5--> 的開放式作答在財務表格上 ≤ 0.05。兩者都沒有候選名單，差異主要落在輸入形式（另有模型家族與語言的差異）。
4. **風險以樣本還是母體計算**。Manzanares-Salor 等 (2024) <!--ref:manzanaressalor2024disclosure--><!--anchor:section:abstract--> 主張以實際再識別攻擊（多類別分類）而非「遮掉多少標註詞」衡量揭露風險；Krčo 等 (2026) <!--ref:krco2026ratbench--><!--anchor:section:abstract--> 進一步以 LLM 攻擊者推出的屬性，計算在美國母體中的再識別風險；Rocher 等 (2019) <!--ref:rocher2019estimating--><!--anchor:section:abstract--> 則說明大量抽樣的資料也難以符合匿名標準。Pilán 等 (2022) <!--ref:pilan2022tab--><!--anchor:section:abstract--> 提供區分直接識別子與準識別子的標註架構。

Wen 與 Li (2026) <!--ref:wen2026agentdoxx--><!--anchor:section:abstract--> 補上第五個面向：**「說出名字」與「認出對象」不是同一件事**。在他們的實驗中，隱私指示只壓住「說出名字」、不壓住檢索——名字準確率 0% 的設定，仍在最多 62% 的稿件中檢索到對象。這表示以「模型是否說出公司名」作為辨識指標，可能低估實際的辨識。

整合起來，封閉式辨識（有名單、可能被迫作答）量的是「在已知候選中能否配對」，開放式辨識（無名單、可棄權）量的是「在真實作答情境中會不會主動認出」。前者較接近 SDC 的最壞情況風險，後者較接近評分當下的實際情境。這是本綜整的整合性解讀，文獻只在 Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:section:6.4--> 的一般隱私情境中把兩者放在同一框架下。

#### Theme C：匿名化對下游判斷的影響方向不一
**Evidence Strength**：Contested
**Sources**：4 篇支持「有效用成本或取捨」、2 篇提供相反證據、2 篇部分相關；Levels III–VI

**Synthesis**：

這是本主題中與「記憶假說」關係最直接、也最有爭議的部分。如果 LLM 的財務判斷主要來自記憶，匿名化應該降低表現、且降幅可當前視偏誤的估計。文獻的結果並不一致。

- **匿名化造成資訊損失（表現下降，且下降不來自前視偏誤）**：Wu 等 (2025) <!--ref:wu2025anonymization--><!--anchor:section:abstract--> 預測 S&P 信評調降時，原文顯著優於匿名化文字，但差距不能用前視偏誤解釋，而是遮掉數字與人物（agent）實體造成的資訊損失，並改變 LLM 對其餘文字的解讀；此現象跨模型、任務、文字類型都存在。這是「匿名化成本超過前視增益」的直接證據，對記憶假說是反面證據。
- **匿名化使表現持平或變好**：Glasserman 與 Lin (2024) <!--ref:glasserman2024lookahead--><!--anchor:section:abstract--> 發現時間內匿名化標題的交易策略反而較好，表示「分心效應」大於前視偏誤，且大公司更明顯。Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract--> 版本乙的摘要稱，認不出的文章原文與遮蔽後情緒判斷 90% 一致、報酬預測力相近，差距可當前視偏誤的上限；版本甲只報告辨識率降到隨機水準，摘要中沒有記錄效用的對應數字。這兩項都意味：在其任務中，移除身分並未帶來明顯的效用損失，前視偏誤的上限不大。
- **取捨是任務特定的**：Loiseau 等 (2026) <!--ref:loiseau2026adaptive--><!--anchor:section:abstract--> 認為適當的隱私—效用取捨隨資料領域、隱私目標與下游用途而變；Staab 等 (2025) <!--ref:staab2025anonymizers--><!--anchor:section:abstract--> 的 LLM 匿名化在效用與隱私上都優於商用工具；Shlomo (2010) <!--ref:shlomo2010releasing--><!--anchor:section:abstract--> 主張以揭露風險與資料效用的客觀量化指標作為釋出決策依據。Greve 與 Sablica (2025) <!--ref:greve2025swapping--><!--anchor:section:abstract--> 提出以交換前後 embedding 對數概似比衡量效用；Krčo 等 (2026) <!--ref:krco2026ratbench--><!--anchor:section:abstract--> 發現 LLM 匿名化工具的取捨較好但成本較高。

這三組結果可以部分調和：Wu 等 (2025) <!--ref:wu2025anonymization--><!--anchor:section:abstract-->遮掉的是數字與人物實體（內容資訊），Glasserman 與 Lin (2024) <!--ref:glasserman2024lookahead--><!--anchor:section:abstract--> 與 Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract-->移除的是公司識別資訊（身分資訊），兩者遮掉的東西不同；任務也不同（信評調降 vs 報酬與情緒）。但在摘要層級，無法判定差異主要來自遮蔽範圍、任務，還是方法，因此本綜整把這組矛盾標為部分未解決。

#### Theme D：以攻擊者回饋校準匿名化，以及「風險—效用」框架
**Evidence Strength**：Moderate（方法框架明確，跨隱私與金融兩個社群）
**Sources**：9 篇支持、1 篇部分相關；Levels III–VII

**Synthesis**：

隱私／NLP 社群與金融社群各自發展出同一個邏輯：以「攻擊者能否認出」作為匿名化是否足夠的判準，而不是以「遮掉了多少詞」為判準。Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract--> 讓 LLM agent 反覆遮蔽並改寫，直到另一個 LLM 認不出為止；Staab 等 (2025) <!--ref:staab2025anonymizers--><!--anchor:section:abstract--> 以 LLM 推論結果引導改寫；Loiseau 等 (2026) <!--ref:loiseau2026adaptive--><!--anchor:section:abstract--> 以任務特定的提示詞最佳化自動產生匿名化指示，找出位於取捨前緣不同位置的策略。Manzanares-Salor 等 (2024) <!--ref:manzanaressalor2024disclosure--><!--anchor:section:abstract--> 從評估端主張以實際再識別攻擊衡量殘餘風險；Krčo 等 (2026) <!--ref:krco2026ratbench--><!--anchor:section:abstract--> 與 Pilán 等 (2022) <!--ref:pilan2022tab--><!--anchor:section:abstract--> 提供 benchmark 與標註架構。

統計揭露控制（SDC）的傳統為這些做法提供了量化語言。Sweeney (2002) <!--ref:sweeney2002kanonymity--><!--anchor:section:abstract--> 的 k-匿名把「粗化到多少才夠」定義為每筆紀錄至少與 k−1 筆無法區分；Shlomo (2010) <!--ref:shlomo2010releasing--><!--anchor:section:abstract--> 回顧把揭露風險與資料效用同時量化、並與資料遮蔽整合的 R-U 取捨方法。Greve 與 Sablica (2025) <!--ref:greve2025swapping--><!--anchor:section:abstract--> 是本次檢索中唯一把 SDC 的 data swapping 用在「防止 LLM 認出法說會公司」的研究，以樣本唯一值為風險、embedding 概似比為效用，並以決策理論校準參數；但作者自承研究主要是示範性的（Greve 與 Sablica (2025) <!--ref:greve2025swapping--><!--anchor:quote:the%20aim%20of%20our%20work%20is%20mostly%20demonstrative-->；單一產業、單一季度、35 份法說會），且交換只能套用在一小部分文字片段上（Greve 與 Sablica (2025) <!--ref:greve2025swapping--><!--anchor:quote:the%20swapping%20can%20only%20be%20performed%20for%20a%20small%20fraction%20of%20the%20text%20chunks%20present%20in%20the%20data-->），NER 也漏掉產品名等準識別子（Greve 與 Sablica (2025) <!--ref:greve2025swapping--><!--anchor:section:4-->）。

需要保留的是：以「攻擊者認不出」為停止條件，隱含假設「認不出就不會用上記憶」。Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:quote:we%20cannot%20conclude%20that%20the%20dataset%20is%20entirely%20free%20of%20contamination--> 自承不能據此斷定資料完全沒有污染——他們的公司名探針只測「表格 → 名稱」，未測「表格 → 舞弊結果」。這個假設在本次檢索範圍內沒有被直接驗證（見 Gap 3）。

#### Theme E：經典 SDC 假設在 LLM 攻擊者下需要重新校準
**Evidence Strength**：Emerging（方向一致，但 LLM 時代的直接證據多為 2026 年預印本或可行性研究）
**Sources**：8 篇支持、1 篇部分相關；Levels III–VII

**Synthesis**：

SDC 的經典工具假設攻擊者需要人工、規模有限。Thees 等 (2026) <!--ref:thees2026agentic--><!--anchor:section:abstract--> 從 SDC 社群內部指出，LLM agent 使每個目標的再識別成本降到數分鐘與數美元，使 GDPR Recital 26「合理可能」的標準更容易成立；Staab 等 (2024) <!--ref:staab2024beyond--><!--anchor:section:abstract--> 估計 LLM 推論的成本約為人工的 1/100、時間 1/240；Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:section:table-1--> 的 LLM 管線在封閉世界中 recall 54.2% @90% precision，遠高於經典 Narayanan 方法的約 0.1%；Wen 與 Li (2026) <!--ref:wen2026agentdoxx--><!--anchor:section:abstract--> 顯示目標一旦出現在檢索結果中，辨識成功率超過 88%。

經典文獻本身已預示了這個轉變的方向：Sweeney (2002) <!--ref:sweeney2002kanonymity--><!--anchor:section:abstract--> 就檢視過在符合 k-匿名的釋出上，若不遵守配套政策仍可實現的再識別攻擊；Narayanan 與 Shmatikov (2008) <!--ref:narayanan2008robust--><!--anchor:section:abstract--> 說明資料被擾動或只釋出子集時攻擊仍有效；Rocher 等 (2019) <!--ref:rocher2019estimating--><!--anchor:section:abstract--> 說明大量抽樣的匿名資料也難以符合 GDPR 的匿名標準；Shlomo (2010) <!--ref:shlomo2010releasing--><!--anchor:section:abstract--> 的 R-U 方法以已知母體示範。LLM 帶來的變化不是「再識別變得可能」，而是「再識別的成本與所需的背景知識大幅下降」，使原本只在理論上存在的攻擊變得實際。這是本綜整的整合性解讀。

### Contradictions & Resolutions

| Claim A | Claim B | Resolution |
|---|---|---|
| Wu 等 (2025) <!--ref:wu2025anonymization--><!--anchor:section:abstract-->：原文顯著優於匿名化文字，差距來自資訊損失而非前視偏誤 | Glasserman 與 Lin (2024) <!--ref:glasserman2024lookahead--><!--anchor:section:abstract-->：時間內匿名化標題表現較好（分心 > 前視）；Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract--> 版本乙：遮蔽後情緒 90% 一致、預測力相近 | **部分可調和，部分未解決**。遮蔽對象不同（Wu 等 (2025) <!--ref:wu2025anonymization--><!--anchor:section:abstract-->遮數字與人物實體；後兩者移除公司身分）、任務不同（信評調降 vs 報酬／情緒）。但兩方都對「記憶推高表現」提出了反面證據：Wu 等 (2025) <!--ref:wu2025anonymization--><!--anchor:section:abstract-->說差距不是前視偏誤，Glasserman 與 Lin (2024) <!--ref:glasserman2024lookahead--><!--anchor:section:abstract--> 與 Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract-->（版本乙）說移除身分不太傷效用。摘要層級無法判定差異的主因。Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract-->版本甲未記錄效用數字。 |
| Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:appendix-A-->：遮蔽法說會開放式辨識 66% | Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:5-->：財務表格開放式辨識 ≤ 0.05 | **可調和（條件性差異）**。輸入形式不同（文字 vs 純數字表格），另有模型家族（Qwen vs 7 個商用與開源模型）與語言（英文 vs 日文）差異。T3 書目指出 Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:5-->由 GPT-4o 判定日文名稱是否相符、Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:appendix-A-->只用一個模型家族——兩者的辨識率都可能被低估。 |
| Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract-->：遮蔽失敗 | Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract-->：迭代遮蔽＋改寫可使辨識降到隨機（版本甲）或約 90% 文章認不出（版本乙） | **可調和**。前者是一次性遮蔽，後者是以辨識失敗為停止條件的迭代改寫。兩個版本的 Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract-->數字都支持「迭代改寫比一次性遮蔽有效」，但兩者對「多徹底」的描述不同，需核對最新版。 |
| Greve 與 Sablica (2025) <!--ref:greve2025swapping--><!--anchor:section:3.2.2-->：實體交換後辨識 0.564–0.602 | Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract-->：可降到隨機或約 90% 認不出 | **可調和**。Greve 與 Sablica (2025) <!--ref:greve2025swapping--><!--anchor:section:4--> 的交換只能套用在少數片段（作者自承），且辨識測試沒有「不知道」選項；兩者的停止條件與計分方式不同，數字不可直接比較。 |
| Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:section:3.1-->：封閉世界中攻擊者應能棄權，precision 以非棄權猜測計算 | Greve 與 Sablica (2025) <!--ref:greve2025swapping--><!--anchor:section:appendix-A-->：要求只回一個 ticker、無「不知道」選項 | **方法論差異（可調和）**。這不是結論的矛盾，而是指標定義的差異；後者的設定使猜測與辨識無法區分。 |
| Wen 與 Li (2026) <!--ref:wen2026agentdoxx--><!--anchor:section:abstract-->：名字準確率 0% 的設定仍在最多 62% 稿件中檢索到對象 | Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:appendix-A-->、Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:5-->：以「說出名稱」作為辨識指標 | **未解決（flagged）**。Wen 與 Li (2026) <!--ref:wen2026agentdoxx--><!--anchor:section:abstract--> 的證據來自可檢索的情境，在無工具情境中，模型「內部認出但不說」無法直接觀察。以說出名稱為指標可能低估辨識，但低估多少，在本次檢索範圍內沒有估計。 |
| Staab 等 (2024) <!--ref:staab2024beyond--><!--anchor:section:abstract-->：文字匿名化擋不住 LLM 推論 | Staab 等 (2025) <!--ref:staab2025anonymizers--><!--anchor:section:abstract-->：LLM 匿名化在效用與隱私上優於商用工具 | **可調和（時間與方法演進）**。前者評估的是既有匿名化工具，後者提出以 LLM 推論為回饋的新方法；同一團隊的前後研究。 |
| Sweeney (2002) <!--ref:sweeney2002kanonymity--><!--anchor:section:abstract-->：k-匿名作為保護模型 | Narayanan 與 Shmatikov (2008) <!--ref:narayanan2008robust--><!--anchor:section:abstract-->、Rocher 等 (2019) <!--ref:rocher2019estimating--><!--anchor:section:abstract-->：高維、抽樣資料仍可再識別 | **可調和**。Sweeney (2002) <!--ref:sweeney2002kanonymity--><!--anchor:section:abstract--> 本身就指出不遵守配套政策時仍可被攻擊；後兩者說明在高維資料上，達到有意義的 k 會付出很大的效用代價。 |

#### Cross-Paper Tension Inventory (#262)

```yaml
cross_paper_tensions:
  - pair_id: CP-001
    paper_a: "wu2025anonymization"
    paper_b: "glasserman2024lookahead"
    candidate_basis: "opposite finding direction"
    overlap_topic: "匿名化使 LLM 財務預測表現下降還是上升；差距是否反映前視偏誤"
    a_finding: "原文顯著優於匿名化；差距來自資訊損失，不是前視偏誤"
    a_evidence_pointer: "T3_bibliography.md #3 主要發現（arXiv 摘要）"
    b_finding: "時間內匿名化標題策略較好；分心效應大於前視偏誤"
    b_evidence_pointer: "T3_bibliography.md #4 主要發現（SSRN 摘要）"
    pair_assessment: "contradiction"
    resolution_status: "flagged_unresolved"
    scholar_confirmation: "pending"
  - pair_id: CP-002
    paper_a: "wu2025anonymization"
    paper_b: "engelberg2025neutering"
    candidate_basis: "opposite finding direction"
    overlap_topic: "匿名化的效用成本"
    a_finding: "匿名化造成顯著資訊損失"
    a_evidence_pointer: "T3_bibliography.md #3 主要發現"
    b_finding: "版本乙：遮蔽後情緒 90% 一致、報酬預測力相近；版本甲：未記錄效用數字"
    b_evidence_pointer: "T3_bibliography.md #1 主要發現（兩個摘要版本）"
    pair_assessment: "conditional_difference"
    resolution_status: "flagged_unresolved"
    scholar_confirmation: "pending"
  - pair_id: CP-003
    paper_a: "efe2026earnings"
    paper_b: "sugiura2026edinet"
    candidate_basis: "opposite finding direction"
    overlap_topic: "LLM 在開放式作答下能否從財務資料認出公司"
    a_finding: "遮蔽法說會逐字稿 66% 以完全相符 ticker 認出；強遮蔽仍 63%"
    a_evidence_pointer: "T3_bibliography.md #6 主要發現（sections：摘要、§4、§5、附錄 A）"
    b_finding: "只給財務表格時 7 個模型公司名準確率都 ≤ 0.05"
    b_evidence_pointer: "T3_bibliography.md #7 主要發現（sections：§5）"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶2"
    scholar_confirmation: "pending"
  - pair_id: CP-004
    paper_a: "lopezlira2025memorization"
    paper_b: "engelberg2025neutering"
    candidate_basis: "opposite finding direction"
    overlap_topic: "遮蔽能否阻止 LLM 認出財務文字中的公司"
    a_finding: "遮蔽失敗，LLM 能從很少上下文重建實體與日期"
    a_evidence_pointer: "T3_bibliography.md #2 主要發現"
    b_finding: "迭代遮蔽＋改寫後辨識降到隨機（版本甲）或約 90% 認不出（版本乙）"
    b_evidence_pointer: "T3_bibliography.md #1 主要發現"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶3"
    scholar_confirmation: "pending"
  - pair_id: CP-005
    paper_a: "greve2025swapping"
    paper_b: "engelberg2025neutering"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "財務文字匿名化後的辨識率"
    a_finding: "實體交換後 GPT-4o 0.564、Gemini 0.602"
    a_evidence_pointer: "T3_bibliography.md #5 主要發現（§3.2.2）"
    b_finding: "降到隨機（版本甲）或約 90% 認不出（版本乙）"
    b_evidence_pointer: "T3_bibliography.md #1 主要發現"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶4"
    scholar_confirmation: "pending"
  - pair_id: CP-006
    paper_a: "lermen2026deanonymization"
    paper_b: "greve2025swapping"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "再識別指標的定義（棄權、候選名單）"
    a_finding: "封閉世界應允許棄權；precision 以非棄權猜測為分母；先驗 π 影響 precision"
    a_evidence_pointer: "T3_bibliography.md #9 主要發現（§3.1、§3.3、§6.4）"
    b_finding: "辨識測試要求只回一個 ticker，無不知道選項、無候選名單"
    b_evidence_pointer: "T3_bibliography.md #5 方法弱點（§3.2.2、附錄 A；書目推論）"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶5"
    scholar_confirmation: "pending"
  - pair_id: CP-007
    paper_a: "wen2026agentdoxx"
    paper_b: "sugiura2026edinet"
    candidate_basis: "agent-noted cross-cluster"
    overlap_topic: "「說出名稱」能否作為辨識的指標"
    a_finding: "名字準確率 0% 的設定仍在最多 62% 稿件中檢索到對象"
    a_evidence_pointer: "T3_bibliography.md #10 主要發現（摘要）"
    b_finding: "以開放式公司名準確率作為辨識探針，≤ 0.05；作者不能斷定沒有污染"
    b_evidence_pointer: "T3_bibliography.md #7 主要發現與方法弱點（§5）"
    pair_assessment: "conditional_difference"
    resolution_status: "flagged_unresolved"
    scholar_confirmation: "pending"
  - pair_id: CP-008
    paper_a: "staab2024beyond"
    paper_b: "staab2025anonymizers"
    candidate_basis: "opposite finding direction"
    overlap_topic: "文字匿名化能否抵擋 LLM 推論"
    a_finding: "文字匿名化與模型對齊目前都擋不住"
    a_evidence_pointer: "T3_bibliography.md #8 主要發現"
    b_finding: "以 LLM 推論引導的匿名化在效用與隱私上優於商用工具"
    b_evidence_pointer: "T3_bibliography.md #14 主要發現"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶7"
    scholar_confirmation: "pending"
  - pair_id: CP-009
    paper_a: "sweeney2002kanonymity"
    paper_b: "rocher2019estimating"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "形式化匿名標準能否保護高維資料"
    a_finding: "k-匿名保護模型；不遵守配套政策時仍可被攻擊"
    a_evidence_pointer: "T3_bibliography.md #17 主要發現"
    b_finding: "15 個人口屬性可再識別 99.98% 美國人；抽樣資料難符 GDPR 匿名標準"
    b_evidence_pointer: "T3_bibliography.md #19 主要發現"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > Contradictions & Resolutions, ¶8"
    scholar_confirmation: "pending"
  - pair_id: CP-010
    paper_a: "manzanaressalor2024disclosure"
    paper_b: "pilan2022tab"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "文字匿名化的風險如何衡量"
    a_finding: "以標註詞的 recall 不是風險指標；應以自動化再識別攻擊衡量"
    a_evidence_pointer: "T3_bibliography.md #13 主要發現（Crossref 摘要）"
    b_finding: "以人工標註的識別子與機密屬性建構 benchmark，提出同時衡量隱私與效用的指標"
    b_evidence_pointer: "T3_bibliography.md #12 主要發現"
    pair_assessment: "conditional_difference"
    resolution_status: "flagged_unresolved"
    scholar_confirmation: "pending"
  - pair_id: CP-011
    paper_a: "krco2026ratbench"
    paper_b: "lermen2026deanonymization"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "再識別風險的計算基準（母體 vs 候選集）"
    a_finding: "以母體層級再識別風險評估匿名化工具"
    a_evidence_pointer: "T3_bibliography.md #16 主要發現"
    b_finding: "封閉世界候選集＋先驗 π 的 precision—recall 框架"
    b_evidence_pointer: "T3_bibliography.md #9 主要發現（§6.4）"
    pair_assessment: "no_material_conflict"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"
  - pair_id: CP-012
    paper_a: "thees2026agentic"
    paper_b: "shlomo2010releasing"
    candidate_basis: "agent-noted cross-cluster"
    overlap_topic: "SDC 風險評估的攻擊者假設"
    a_finding: "LLM agent 使再識別成本降到數分鐘、數美元，GDPR「合理可能」標準更易成立"
    a_evidence_pointer: "T3_bibliography.md #11 主要發現（arXiv 摘要）"
    b_finding: "以揭露風險與效用的客觀量化指標決定釋出方式，R-U 取捨方法"
    b_evidence_pointer: "T3_bibliography.md #20 主要發現"
    pair_assessment: "no_material_conflict"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"
```

**Coverage Note**：20 papers in corpus; 12 candidate pairs considered（basis：shared construct／opposite finding direction／agent-noted cross-cluster；沒有引用網絡資料，未使用 bibliographic coupling；沒有 scholar flag）。This is a **scoped advisory scan, not complete pairwise contradiction detection** — cross-neighborhood pairs not surfaced here may exist and are not claimed absent（例如 Loiseau 等 (2026) <!--ref:loiseau2026adaptive--><!--anchor:section:abstract--> 的任務特定取捨與 Wu 等 (2025) <!--ref:wu2025anonymization--><!--anchor:section:abstract--> 的跨任務資訊損失之間、Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:appendix-A--> 的「對照組比重編組更常被認出」與 Glasserman 與 Lin (2024) <!--ref:glasserman2024lookahead--><!--anchor:section:abstract--> 的「大公司效應更強」之間，未逐一評估）。CP-001、CP-002、CP-004、CP-005 涉及 Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract-->兩個摘要版本，評估同時考慮兩版。Scholar confirms each `resolution_pointer` and may flag additional cross-pairs.

### Knowledge Gaps

1. **在本次檢索範圍內，未見以結構化財務數字（比率、類別計數）為輸入、系統性改變粗化等級，並同時報告辨識率與下游任務效用的研究**（Empirical）。最接近的是 Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:5--> 的單點表格探針與 Greve 與 Sablica (2025) <!--ref:greve2025swapping--><!--anchor:section:3.2.2--> 的文字實體交換。含意：「資訊量 vs 可辨識度」曲線在財務數字上沒有既有估計。
2. **在本次檢索範圍內，未見財務領域正式比較封閉式（給名單）與開放式（無名單）辨識的研究**（Methodological）。這個區分目前只在一般隱私文獻（Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:section:6.4-->）中出現。
3. **「辨識失敗」與「結果記憶未被使用」之間的關係未被檢驗**（Theoretical）。Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:5--> 的探針只測名稱、未測結果；Wen 與 Li (2026) <!--ref:wen2026agentdoxx--><!--anchor:section:abstract--> 顯示說不出名字不等於沒認出；Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract--> 以辨識失敗為停止條件。在本次檢索範圍內，未見研究直接檢驗「認不出公司時，模型是否仍能用上該公司的結果記憶」。
4. **非美國財務文字的再識別**（Geographic）。T3 書目中有明確地區者 7/9 為美國資料；台灣、中國、歐洲財務文字的再識別研究未檢索。
5. **LLM 攻擊者下的 SDC 門檻設定**（Theoretical）。Thees 等 (2026) <!--ref:thees2026agentic--><!--anchor:section:abstract--> 與 Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:section:table-1--> 顯示攻擊成本大降，但在本次檢索範圍內未見為 LLM 攻擊者重新校準 k 值或風險門檻的研究。
6. **Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract-->兩個摘要版本的數字差異**（Empirical，查核層級）：需核對 SSRN 最新版後，才能確定迭代改寫能把辨識壓到多低、以及其效用代價。

### Evidence Convergence Map

```
Strong:      [          ] （無；財務領域直接證據少且多為預印本）
Moderate:    [=======   ] Theme D 攻擊者回饋與風險—效用框架（9 支持／1 部分，Levels III–VII）
Moderate:    [======    ] Theme A 只遮蔽直接識別子不足（9 支持／1 相反／2 部分；財務僅 3 篇且皆文字）
Moderate:    [======    ] Theme B 輸入形式與評估設定決定辨識率（8 支持／1 部分）
Emerging:    [=====     ] Theme E SDC 假設需為 LLM 攻擊者重校（8 支持／1 部分；LLM 時代證據多為 2026 預印本）
Contested:   [====      ] Theme C 匿名化對下游判斷的影響方向（4 支持取捨／2 相反／2 部分）
Gap:         [          ] 財務數字的粗化曲線；財務領域封閉 vs 開放辨識比較（0 篇，在本次檢索範圍內）
```

### Theoretical Integration

本主題可放進 SDC 的「揭露風險—資料效用」（R-U）框架（Shlomo (2010) <!--ref:shlomo2010releasing--><!--anchor:section:abstract-->），但 LLM 情境需要在兩個軸上各加一層。

- **風險軸**：傳統上以唯一性或 k 值計算（Sweeney (2002) <!--ref:sweeney2002kanonymity--><!--anchor:section:abstract-->、Rocher 等 (2019) <!--ref:rocher2019estimating--><!--anchor:section:abstract-->）。LLM 時代需區分兩條再識別路徑：(1) 推論路徑——從準識別子組合推出身分（Staab 等 (2024) <!--ref:staab2024beyond--><!--anchor:section:abstract-->、Narayanan 與 Shmatikov (2008) <!--ref:narayanan2008robust--><!--anchor:section:abstract-->）；(2) 記憶路徑——模型在訓練中見過這些文字或事件（Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract-->）。也需區分兩種測量情境：封閉式（候選名單、可能被迫作答）與開放式（無名單、可棄權）（Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:section:6.4-->）。
- **效用軸**：傳統上以資料的統計性質衡量。LLM 情境中，效用是下游判斷的表現，而匿名化對它的影響有兩個方向相反的成分：資訊損失（Wu 等 (2025) <!--ref:wu2025anonymization--><!--anchor:section:abstract-->）與去除分心（Glasserman 與 Lin (2024) <!--ref:glasserman2024lookahead--><!--anchor:section:abstract-->）。Loiseau 等 (2026) <!--ref:loiseau2026adaptive--><!--anchor:section:abstract--> 指出取捨是任務特定的。

在這個框架下，本主題的研究問題（「要粗到什麼程度」）可以重述為：在舞弊判斷這個下游任務上，找出 R-U 前緣上「風險低於某門檻、效用損失最小」的粗化等級；而「封閉式 vs 開放式」的選擇，等於選擇風險軸的定義（最壞情況 vs 實際作答情境）。此外，上述框架都只量「認出身分」，不量「用上記憶」——Gap 3 是這個框架目前最大的空白。這是本綜整的整合性推論。

### 與本研究實驗的對照

（以下為本研究自身實驗，取自 `results/research_topics.md`，**不是文獻**，不作為已確立的發現。）

- **dreamy 匿名化階梯：完整事實卡給名單可配對 34/54；類別計數卡 3/54 且 AUC 不變（0.77）；AAER 樣本上連類別計數都能部分配對，只有紅旗總數卡通過**：這正是 Gap 1 所說「結構化財務數字、多個粗化等級、同時報告辨識與效用」的設計。「完整事實卡可配對」與 Narayanan 與 Shmatikov (2008) <!--ref:narayanan2008robust--><!--anchor:section:abstract--> 的高維稀疏機制一致；「類別計數卡辨識下降但 AUC 不變」與 Wu 等 (2025) <!--ref:wu2025anonymization--><!--anchor:section:abstract--> 的「遮數字損失最大」方向不同，可能與 Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract--> 版本乙的「效用相近」較接近——差異可能來自任務或輸入形式，尚待檢驗。
- **peaceful E2：類型卡 L1／L2／L3 給名單配對 26、24、20/28，但評分時（無名單）全部 "unknown"**：這是封閉式與開放式辨識落差的實例，與 Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:section:3.1--> 的框架對應；但 Wen 與 Li (2026) <!--ref:wen2026agentdoxx--><!--anchor:section:abstract--> 提醒，「說 unknown」不等於「沒認出」，因此 E2 的開放式結果不能直接解讀為「記憶未被使用」（Gap 3）。
- **AAER 公司比時間外小公司容易被認出**：與 Glasserman 與 Lin (2024) <!--ref:glasserman2024lookahead--><!--anchor:section:abstract--> 的「大公司效應更強」方向一致；Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:appendix-A--> 也記錄對照組（71%）比重編組（57%）更常被認出，可解讀為「辨識跟著知名度、不跟著標籤」，但這是本綜整的推論。
- **封閉式 vs 開放式該用哪個當標準**：依本綜整的框架，封閉式適合作為匿名化的「最壞情況」門檻，開放式適合描述評分情境；兩者並報，並以 Krčo 等 (2026) <!--ref:krco2026ratbench--><!--anchor:section:abstract--> 與 Rocher 等 (2019) <!--ref:rocher2019estimating--><!--anchor:section:abstract--> 的母體層級思路，提醒 28 或 54 家的樣本內配對率不能推到全體上市公司。

### Synthesis Limitations

- **閱讀深度**：16 篇只讀摘要，方法弱點未評估；4 篇讀了指定章節，但未逐字通讀全文，方法弱點只限所列章節。
- **Engelberg 等 (2025) <!--ref:engelberg2025neutering--><!--anchor:section:abstract--> 的數字**：兩個摘要版本並存，未能核對 SSRN 最新版；本綜整所有涉及其數字的判斷都同時列出兩版。
- **dreamy 語料的細節**：T3 書目指出 dreamy 引述的 Lopez-Lira 等 (2025) <!--ref:lopezlira2025memorization--><!--anchor:section:abstract-->的細節數字（如特定公司的回想率）未在本次讀取範圍內確認，本綜整未使用。
- **錨點**：`abstract_only` 來源一律為 `section:abstract`；`sections` 來源只在書目明確記錄章節或原文時使用章節或引文錨點；Efe 等 (2026) <!--ref:efe2026earnings--><!--anchor:section:appendix-A-->的辨識細節數字以 `appendix-A`（書目記錄的「Prompts and firm recognition」）為錨點，若下游核對發現出自 §4，需修正。
- **證據等級跨主題不一致**：Sugiura 等 (2026) <!--ref:sugiura2026edinet--><!--anchor:section:5-->在 T3 為 VI、在 T1 為 III、在 T5 為 IV；本檔依 T3。
- **出版狀態**：8 篇為 2024 年後預印本；Lermen 等 (2026) <!--ref:lermen2026deanonymization--><!--anchor:section:3.1-->的 USENIX Security 26 收錄未獲獨立確認；EDINET-Bench 的 ICLR 2026 收錄只依 arXiv comment。
- **矛盾掃描**：Cross-Paper Tension Inventory 是有範圍的建議性掃描，不是完整的兩兩比較。
- 本檔未經任何外部審查或稽核步驟。
