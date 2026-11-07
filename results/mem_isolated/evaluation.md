# 第八輪 MEM 隔離重跑：結果

5 次 `claude -p --tools ""` 執行，全部通過 7 項無上網檢查（`verification.csv`），原始紀錄在算分前已 commit。

| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 | 問題公司「知道出事」 | 對照公司「知道出事」 | 與原始 MEM 的 Spearman ρ |
|---|---|---|---|---|---|---|
| run1 | 0.86 | 0.67–1.00 | 11 / 1 / 2 | 12/14 | 2/14 | 0.97 |
| run2 | 0.89 | 0.70–1.00 | 12 / 0 / 2 | 12/14 | 1/14 | 0.96 |
| run3 | 0.88 | 0.70–1.00 | 12 / 0 / 2 | 13/14 | 2/14 | 0.98 |
| run4 | 0.88 | 0.69–1.00 | 11 / 1 / 2 | 13/14 | 2/14 | 0.97 |
| run5 | 0.88 | 0.69–1.00 | 12 / 0 / 2 | 13/14 | 2/14 | 0.96 |
| **隔離 5 次平均分數** | **0.88** | 0.69–1.00 | 12 / 0 / 2 | | | 0.98 |
| claude.ai rerun 1 | 0.88 | 0.70–1.00 | 12 / 0 / 2 | 12/14 | 2/14 | 0.96 |
| claude.ai rerun 2 | 0.88 | 0.70–1.00 | 12 / 0 / 2 | 13/14 | 2/14 | 0.96 |
| round 8 original | 0.88 | 0.70–1.00 | 11 / 1 / 2 | 13/14 | 2/14 | 1.00 |

隔離各次之間的 Spearman ρ：最低 0.95，中位數 0.97

## 判讀（2026-11-07）
- 5 次都在**沒有任何工具**的 session 中執行（工具清單空、MCP 空、無工具呼叫、伺服器端搜尋計數 0、無子代理、單輪），AUC 0.86–0.89，平均分數 0.88，與原始 MEM（0.88）和 claude.ai 兩次重跑（0.88、0.88）相同。
- 與原始 MEM 的 Spearman ρ 0.96–0.98，各次之間最低 0.95：模型每次給的排序幾乎一樣。
- 每次輸的都是同兩對：P13（Evoqua < Welbilt；對照公司 Welbilt 本身重編過，模型記得）、P14（Gentex < Visteon；模型不記得 Gentex 出事，5 次都給 4–5 分）。
- 結論：第八輪 MEM 的 0.88 可以在確定無法上網的環境中重現，來源是模型記憶；這支持「第七輪整份 10-K 的 0.90 主要來自模型記得哪些公司出事」。
- 本次只證明「沒有上網」；時間外樣本（訓練截止 2026-06 之後才出事的公司）尚未執行，見 `design.md` 4.3。

## 逐家（分數）

| pid | 公司 | run1 | run2 | run3 | run4 | run5 | 平均 | 原始 MEM |
|---|---|---|---|---|---|---|---|---|
| P01C | AerSale Corporation | 15 | 12 | 20 | 12 | 20 | 16 | 12 |
| P01T | Latch, Inc. | 85 | 92 | 88 | 85 | 88 | 88 | 85 |
| P02C | Bunge Limited | 8 | 8 | 8 | 6 | 8 | 8 | 6 |
| P02T | Archer-Daniels-Midland Company | 65 | 75 | 55 | 45 | 55 | 59 | 55 |
| P03C | National Presto Industries, Inc. | 8 | 10 | 10 | 8 | 6 | 8 | 10 |
| P03T | AMMO, Inc. | 82 | 85 | 60 | 70 | 85 | 76 | 72 |
| P04C | PDS Biotechnology Corporation | 8 | 8 | 12 | 8 | 10 | 9 | 10 |
| P04T | Adamis Pharmaceuticals Corporation | 50 | 60 | 60 | 65 | 45 | 56 | 70 |
| P05C | Boston Scientific Corporation | 6 | 10 | 8 | 6 | 8 | 8 | 6 |
| P05T | Becton, Dickinson and Company | 30 | 30 | 40 | 30 | 25 | 31 | 30 |
| P06C | TheMaven, Inc. | 70 | 55 | 55 | 55 | 60 | 59 | 60 |
| P06T | Ideanomics, Inc. | 70 | 65 | 70 | 55 | 70 | 66 | 60 |
| P07C | Ducommun Incorporated | 8 | 8 | 10 | 6 | 8 | 8 | 8 |
| P07T | CPI Aerostructures, Inc. | 92 | 95 | 90 | 90 | 90 | 91 | 85 |
| P08C | Consolidated Communications Holdings, Inc. | 10 | 8 | 10 | 8 | 10 | 9 | 10 |
| P08T | GTT Communications, Inc. | 92 | 92 | 95 | 90 | 95 | 93 | 88 |
| P09C | Thermon Group Holdings, Inc. | 8 | 8 | 10 | 8 | 10 | 9 | 8 |
| P09T | Plug Power Inc. | 85 | 90 | 85 | 85 | 85 | 86 | 80 |
| P10C | Provident Financial Holdings, Inc. | 6 | 6 | 7 | 5 | 6 | 6 | 6 |
| P10T | Malvern Bancshares, Inc. | 70 | 70 | 65 | 75 | 75 | 71 | 55 |
| P11C | Mitek Systems, Inc. | 18 | 15 | 12 | 15 | 8 | 14 | 10 |
| P11T | USA Technologies, Inc. | 92 | 95 | 90 | 90 | 92 | 92 | 90 |
| P12C | TransAtlantic Petroleum Ltd. | 15 | 20 | 15 | 15 | 15 | 16 | 18 |
| P12T | SAExploration Holdings, Inc. | 92 | 97 | 97 | 95 | 95 | 95 | 95 |
| P13C | Welbilt, Inc. | 85 | 85 | 85 | 85 | 80 | 84 | 65 |
| P13T | Evoqua Water Technologies Corp. | 22 | 25 | 60 | 60 | 25 | 38 | 55 |
| P14C | Visteon Corporation | 8 | 8 | 8 | 8 | 8 | 8 | 6 |
| P14T | Gentex Corporation | 5 | 5 | 5 | 4 | 5 | 5 | 4 |
