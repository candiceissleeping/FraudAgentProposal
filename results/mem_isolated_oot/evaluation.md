# 時間外樣本（第九輪 27 對）隔離 MEM：結果

5 次 `claude -p --tools ""` 執行，全部通過 7 項無上網檢查（`verification.csv`），原始紀錄在算分前已 commit。

| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 | 問題公司「知道出事」 | 對照公司「知道出事」 | 與原始 MEM 的 Spearman ρ |
|---|---|---|---|---|---|---|
| run1 | 0.72 | 0.58–0.85 | 20 / 1 / 6 | 0/27 | 0/27 | 0.93 |
| run2 | 0.67 | 0.52–0.82 | 21 / 1 / 5 | 0/27 | 0/27 | 0.94 |
| run3 | 0.68 | 0.53–0.82 | 19 / 3 / 5 | 0/27 | 0/27 | 0.94 |
| run4 | 0.72 | 0.57–0.85 | 20 / 1 / 6 | 0/27 | 0/27 | 0.92 |
| run5 | 0.68 | 0.53–0.81 | 21 / 1 / 5 | 0/27 | 0/27 | 0.96 |
| **隔離 5 次平均分數** | **0.69** | 0.54–0.83 | 21 / 0 / 6 | | | 0.96 |
| round 9 original | 0.71 | 0.57–0.84 | 21 / 2 / 4 | 0/27 | 0/27 | 1.00 |

隔離各次之間的 Spearman ρ：最低 0.91，中位數 0.94

## 預先登錄檢驗的結果（2026-11-07）
| 代號 | 結果 |
|---|---|
| O1 | 5/5 通過 7 項無上網檢查；canary：無工具時答「不知道」並全過，開放搜尋時被偵測 |
| O2 | 問題組「知道後來出事」每次 **0/27**（對照組也是 0/27），通過 |
| O3 | AUC 0.67–0.72，**5 次平均分數 0.69（95% CI 0.54–0.83）**，組內 21 勝 / 0 平 / 6 負 |
| O4 | 第八輪隔離重跑（AAER 樣本）平均分數 AUC 0.88；本樣本 0.69 |
| O5 | 第九輪原始 MEM 0.71；與本次平均分數的 Spearman ρ 0.96。統一名稱格式、改在隔離環境後結果不變 |
| O6 | 5 次之間 Spearman ρ 最低 0.91，中位數 0.94 |

## 判讀（依 protocol §5）
- 屬於「O2 通過且 AUC 明顯高於 0.5」：模型完全不知道結果（0/27），只憑名稱與年度仍有 AUC 約 0.69，CI 下界 0.54 > 0.5。
  名稱本身帶有「公司類型先驗」（例如：OTC 小型公司、轉型中的殼公司給 40–55 分；IMAX、Liberty Global、NACCO 這類大型老牌公司給 5–10 分）。
- 分數分布不同：本樣本最高約 55 分，沒有任何公司超過 60；第八輪模型說「知道出事」的問題公司多為 80–95 分。
- 兩個樣本組成不同（本樣本是小型 4.02 公司，第八輪是 AAER 公司），所以 0.88 − 0.69 的差距不能直接當作「記得結果」的貢獻。
  依 protocol，下一步需要在第八輪同一批 28 家上做「知道／不知道」分層（實驗 2），才能拆開第八輪 0.88 中先驗與記憶各占多少。

## 逐家（分數）

| pid | 公司 | run1 | run2 | run3 | run4 | run5 | 平均 | 原始 MEM |
|---|---|---|---|---|---|---|---|---|
| O01C | Windtree Therapeutics, Inc. | 45 | 50 | 35 | 40 | 50 | 44 | 40 |
| O01T | FutureTech II Acquisition Corp. | 25 | 25 | 15 | 25 | 20 | 22 | 25 |
| O02C | Skyline Bankshares, Inc. | 12 | 6 | 8 | 5 | 8 | 8 | 6 |
| O02T | BayFirst Financial Corp. | 25 | 15 | 20 | 15 | 25 | 20 | 20 |
| O03C | KonaTel, Inc. | 30 | 20 | 20 | 20 | 25 | 23 | 25 |
| O03T | High Wire Networks, Inc. | 45 | 45 | 40 | 45 | 50 | 45 | 40 |
| O04C | U.S. Premium Beef, LLC | 10 | 5 | 8 | 5 | 8 | 7 | 5 |
| O04T | Trans American Aquaculture, Inc. | 55 | 50 | 45 | 50 | 55 | 51 | 50 |
| O05C | NACCO Industries, Inc. | 8 | 5 | 8 | 5 | 8 | 7 | 6 |
| O05T | American Resources Corp. | 50 | 45 | 45 | 45 | 55 | 48 | 50 |
| O06C | Trio Petroleum Corp. | 40 | 30 | 35 | 35 | 40 | 36 | 35 |
| O06T | New Era Energy & Digital, Inc. | 45 | 40 | 35 | 40 | 45 | 41 | 50 |
| O07C | Worksport Ltd. | 30 | 25 | 25 | 25 | 35 | 28 | 25 |
| O07T | Securetech Innovations, Inc. | 50 | 40 | 35 | 45 | 40 | 42 | 35 |
| O08C | OMNIQ Corp. | 45 | 60 | 50 | 55 | 60 | 54 | 50 |
| O08T | CreditRiskMonitor.com, Inc. | 12 | 7 | 10 | 5 | 8 | 8 | 8 |
| O09C | Greenwave Technology Solutions, Inc. | 55 | 55 | 50 | 45 | 60 | 53 | 45 |
| O09T | Olenox Industries Inc. | 50 | 45 | 40 | 40 | 50 | 45 | 50 |
| O10C | Yunhong Green CTI Ltd. | 45 | 30 | 40 | 40 | 45 | 40 | 40 |
| O10T | Northann Corp. | 45 | 40 | 40 | 40 | 45 | 42 | 40 |
| O11C | Greenlane Holdings, Inc. | 45 | 45 | 45 | 40 | 50 | 45 | 35 |
| O11T | Capstone Holding Corp. | 35 | 30 | 30 | 30 | 40 | 33 | 30 |
| O12C | Artiva Biotherapeutics, Inc. | 12 | 8 | 10 | 10 | 12 | 10 | 8 |
| O12T | Pelthos Therapeutics Inc. | 30 | 25 | 25 | 25 | 25 | 26 | 20 |
| O13C | Kiora Pharmaceuticals, Inc. | 15 | 15 | 15 | 15 | 20 | 16 | 12 |
| O13T | HCW Biologics Inc. | 40 | 30 | 30 | 35 | 35 | 34 | 25 |
| O14C | Marygold Companies, Inc. | 20 | 12 | 15 | 15 | 15 | 15 | 15 |
| O14T | Netcapital Inc. | 55 | 45 | 45 | 50 | 55 | 50 | 55 |
| O15C | BONK, Inc. | 45 | 50 | 50 | 45 | 55 | 49 | 50 |
| O15T | Solesence, Inc. | 20 | 15 | 15 | 15 | 20 | 17 | 15 |
| O16C | Newton Golf Company, Inc. | 35 | 30 | 25 | 25 | 35 | 30 | 25 |
| O16T | Brownie's Marine Group, Inc. | 45 | 40 | 40 | 40 | 40 | 41 | 35 |
| O17C | Duke Robotics Corp. | 45 | 35 | 30 | 40 | 40 | 38 | 30 |
| O17T | SDR Drone, Inc. | 50 | 45 | 40 | 45 | 50 | 46 | 40 |
| O18C | ESS Tech, Inc. | 30 | 22 | 25 | 25 | 30 | 26 | 20 |
| O18T | Nuburu, Inc. | 55 | 45 | 50 | 50 | 55 | 51 | 45 |
| O19C | Liberty Global Ltd. | 8 | 6 | 8 | 5 | 8 | 7 | 8 |
| O19T | Optimum Communications, Inc. | 12 | 25 | 12 | 40 | 15 | 21 | 10 |
| O20C | Crexendo, Inc. | 15 | 10 | 10 | 10 | 12 | 11 | 12 |
| O20T | GlobalTech Corp. | 50 | 40 | 40 | 45 | 50 | 45 | 45 |
| O21C | Pixelworks, Inc. | 20 | 15 | 15 | 15 | 22 | 17 | 12 |
| O21T | Sports Entertainment Gaming Global Corp. | 55 | 50 | 40 | 45 | 50 | 48 | 45 |
| O22C | Blue Dolphin Energy Co. | 30 | 30 | 25 | 30 | 35 | 30 | 30 |
| O22T | EON Resources Inc. | 45 | 35 | 40 | 35 | 40 | 39 | 40 |
| O23C | Omnitek Engineering Corp. | 35 | 30 | 25 | 30 | 30 | 30 | 25 |
| O23T | Globaltek Ventures, Inc. | 55 | 45 | 35 | 50 | 50 | 47 | 40 |
| O24C | IMAX Corp. | 10 | 5 | 8 | 5 | 8 | 7 | 6 |
| O24T | GoPro, Inc. | 15 | 7 | 10 | 10 | 15 | 11 | 8 |
| O25C | Galaxy Gaming, Inc. | 15 | 10 | 12 | 10 | 15 | 12 | 10 |
| O25T | High Roller Technologies, Inc. | 30 | 25 | 30 | 25 | 35 | 29 | 25 |
| O26C | Paysign, Inc. | 25 | 15 | 20 | 20 | 22 | 20 | 15 |
| O26T | Datavault AI Inc. | 45 | 45 | 40 | 45 | 50 | 45 | 45 |
| O27C | Protopia Global Holdings Inc. | 55 | 50 | 40 | 50 | 50 | 49 | 45 |
| O27T | Panamera Holdings Corp. | 45 | 50 | 40 | 45 | 55 | 47 | 45 |
