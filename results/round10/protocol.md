# 第十輪預先登錄：再加 10 組小公司

本文件在建立資料包與任何評分之前提交。設計與第九輪相同（`results/round9/protocol.md`），以下只列不同之處。

## 1. 樣本：10 家 SEC 確認年度財報錯報的小公司
來源：2016-06 至 2026-10 全部 AAER（`data/round9/aaer_index_2017_2026.json`，800 則）與近年 SEC 訴訟。逐案讀 SEC 摘要，排除：只錯報季報（Amyris、Celsius、Taronis、Key Tronic）、只有揭露或 Form NT 違規（2021-04 與 2023-08 兩批 Form 12b-25 案、Co-Diagnostics）、只有帳冊與內控（Acreage：年底現金為真實的來回轉帳）、大型公司、已在前幾輪使用的公司。

| 公司 | CIK | SEC 行動 | 錯報 | Y0 10-K（原始，申報日） |
|---|---|---|---|---|
| Pareteum | 1084384 | 命令 33-10975，2021-09 | 2018 營收高估（重編 3,240 萬 → 2,030 萬） | FY2018，2019-03-18 |
| Tandy Leather Factory | 909724 | AAER-4228，2021-07 | 存貨與銷貨成本，多年重編 | FY2018，2019-03-08 |
| Apex Global Brands（前 Cherokee） | 844161 | AAER-4199，2020-12 | 商標減損未認列（2017-01 至 2018-04） | FY 2018-01，2018-04-19 |
| Revolution Lighting | 917523 | AAER-4170，2020-09 | 灌高營收（2014–2018） | FY2017，2018-03-08 |
| Power Solutions International | 1137091 | AAER-4169，2020-09 | 灌高營收（2014 Q4–2016） | FY2015，2016-02-26 |
| Manitex International | 1302028 | AAER-4177，2020-09 | 透過關係人交易的會計舞弊（2013–2017） | FY2016，2017-03-10 |
| Sequential Brands | 1648428 | AAER-4277，2021-12 | 商譽減損未認列（2016–2017） | FY2016，2017-03-14 |
| HF Foods Group | 1680873 | AAER-4506，2024-06 | 虛構信用額度隱藏負債、關係人挪用（2018–2020） | FY2018，2019-04-01（2020-02 放空報告前） |
| Lottery.com | 1673481 | LR-26464，2026-01 | 2021 營收高估 >300% | FY2021，2022-04-01（2022-07 揭露前） |
| RTI Surgical | 1100441 | AAER-4318，2022-08 | 提前出貨認列營收（2015 Q1–2016 Q2） | FY2015，2016-03-07 |

說明：多數案件的 SEC 行動早於模型訓練截止日；Lottery.com（2026-01）接近截止日。小公司仍可能被模型記得，這正是本輪要量測的。

## 2. 對照組（`round10 controls`）
- 同第七、九輪規則，但**不要求對照公司有前一年 10-K**（第七輪需要 Y-1 計算財務特徵；本輪只用 Y0，且申報索引沒有 FY2014 的 10-K，若保留此條件，FY2015 的兩案找不到同產業對照）
- 若連 2 碼 SIC 都沒有候選，退回只依規模配對（本輪未發生）
- AAER 排除名單擴大到 2016-06 起
- 結果（`controls.json`）：Pareteum → Agilysys；Tandy → Rocky Brands（2 碼）；Apex → Differential Brands（2 碼）；Revolution Lighting → Orion Energy Systems；Power Solutions → BWX Technologies；Manitex → Axcelis；Sequential Brands → lululemon；HF Foods → Coffee Holding；Lottery.com → Enfusion；RTI Surgical → Exactech

## 3. 資料包與評分
- 同第九輪：L0′（新擷取、不遮蔽）與 L3c（第 3.1 版遮蔽），20 份 × 2 = 40 次評分，每次一個新的 agent，隨機中性檔名
- 提示詞同第九輪（L0′：第七輪 `RISK_TASK`；L3c：`RISK_TASK_L3B`）

## 4. 分析（與第九輪合併，13 對）
- 主要：只看「問題公司的評分 agent 回答**不知道後來出事**」的組，計算組內勝負與 AUC（對照公司全部納入比較）
- 次要：全部 13 對的 AUC、辨識率、「知道後來出事」比例；L0′ vs L3c
- 樣本仍小，只做描述

## 5. 修訂紀錄

- 2026-11-02，建包後、評分前：20 份 L3c 都含資產負債表（lululemon 的總資產列沒有「Total assets」標籤，已人工確認報表在內）；同數字兩種係數每份 0–6 個（權益變動表混合列），記錄不修改
