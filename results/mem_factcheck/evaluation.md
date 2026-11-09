# 實驗 3：模型「知道出事」自述的查核結果

共 254 則自述；評分者為每家公司一個無工具的 Opus 5.5 session（全部通過 7 項無上網檢查），不知道自述來自哪個模型。

## M1、M2：第八輪問題公司的「知道」自述

| 模型 | 則數 | 正確且具體 | 正確但籠統 | **正確合計（M1）** | 錯誤 | 無紀錄支持 |
|---|---|---|---|---|---|---|
| Opus | 63 | 54（86%） | 7（11%） | **61（97%）** | 2（3%） | 0 |
| Sonnet | 65 | 45（69%） | 11（17%） | **56（86%）** | 9（14%） | 0 |
| Haiku | 47 | 19（40%） | 20（43%） | **39（83%）** | 8（17%） | 0 |

## M3：第八輪對照公司與時間外樣本的「知道」自述

| 模型 | 樣本／組 | 則數 | 有紀錄支持（正確） | 有紀錄但錯誤 | 無紀錄支持 |
|---|---|---|---|---|---|
| Opus | round8 C | 9 | 1 | 3 | 5（56%） |
| Sonnet | round8 C | 22 | 0 | 5 | 17（77%） |
| Sonnet | oot T | 11 | 1 | 0 | 10（91%） |
| Sonnet | oot C | 22 | 0 | 0 | 22（100%） |
| Haiku | round8 C | 10 | 5 | 0 | 5（50%） |
| Haiku | oot T | 2 | 2 | 0 | 0（0%） |
| Haiku | oot C | 3 | 0 | 0 | 3（100%） |

## 逐家（第八輪問題公司，三個模型合計）

| 公司 | 則數 | 正確且具體 | 正確但籠統 | 錯誤 |
|---|---|---|---|---|
| Latch, Inc. | 15 | 10 | 5 | 0 |
| Archer-Daniels-Midland Company | 15 | 15 | 0 | 0 |
| AMMO, Inc. | 12 | 7 | 4 | 1 |
| Adamis Pharmaceuticals Corporation | 10 | 7 | 3 | 0 |
| Becton, Dickinson and Company | 10 | 9 | 0 | 1 |
| Ideanomics, Inc. | 15 | 11 | 3 | 1 |
| CPI Aerostructures, Inc. | 15 | 13 | 1 | 1 |
| GTT Communications, Inc. | 15 | 3 | 5 | 7 |
| Plug Power Inc. | 15 | 9 | 4 | 2 |
| Malvern Bancshares, Inc. | 15 | 15 | 0 | 0 |
| USA Technologies, Inc. | 15 | 9 | 6 | 0 |
| SAExploration Holdings, Inc. | 15 | 8 | 7 | 0 |
| Evoqua Water Technologies Corp. | 8 | 2 | 0 | 6 |

## 逐家（對照公司與時間外樣本）

| pid | 公司 | 年度有紀錄 | 則數（Opus / Sonnet / Haiku） | 錯誤 | 無紀錄支持 |
|---|---|---|---|---|---|
| O03T | High Wire Networks, Inc. | yes | 0 / 1 / 2 | 0 | 0 |
| O04T | Trans American Aquaculture, Inc. | no | 0 / 4 / 0 | 0 | 4 |
| O05T | American Resources Corp. | no | 0 / 1 / 0 | 0 | 1 |
| O06C | Trio Petroleum Corp. | no | 0 / 1 / 0 | 0 | 1 |
| O07C | Worksport Ltd. | no | 0 / 1 / 0 | 0 | 1 |
| O08C | OMNIQ Corp. | no | 0 / 4 / 2 | 0 | 6 |
| O09C | Greenwave Technology Solutions, Inc. | no | 0 / 2 / 0 | 0 | 2 |
| O10C | Yunhong Green CTI Ltd. | no | 0 / 3 / 0 | 0 | 3 |
| O13T | HCW Biologics Inc. | no | 0 / 4 / 0 | 0 | 4 |
| O14T | Netcapital Inc. | no | 0 / 1 / 0 | 0 | 1 |
| O22C | Blue Dolphin Energy Co. | no | 0 / 4 / 0 | 0 | 4 |
| O24C | IMAX Corp. | no | 0 / 3 / 0 | 0 | 3 |
| O26C | Paysign, Inc. | no | 0 / 4 / 1 | 0 | 5 |
| P01C | AerSale Corporation | no | 0 / 3 / 0 | 0 | 3 |
| P03C | National Presto Industries, Inc. | no | 0 / 3 / 0 | 0 | 3 |
| P06C | TheMaven, Inc. | yes | 4 / 5 / 5 | 8 | 0 |
| P11C | Mitek Systems, Inc. | no | 0 / 1 / 0 | 0 | 1 |
| P12C | TransAtlantic Petroleum Ltd. | no | 0 / 5 / 0 | 0 | 5 |
| P13C | Welbilt, Inc. | no | 5 / 5 / 5 | 0 | 15 |

## 人工抽查一致率

抽查 51 則（種子 20261109，人工判定在評分者執行前 commit）。

| 欄位 | 一致 |
|---|---|
| issue | 43/51（84%） |
| consequence | 47/51（92%） |
| contradiction | 47/51（92%） |
| **總判定** | **48/51（94%）** |

總判定不一致的自述（人工 → 評分者）：K089 correct_vague → wrong；K194 correct_specific → correct_vague；K026 correct_specific → wrong

評分者抄錯 record_exists 的則數：0（已改用事實表的值）

## 依 protocol §5 的判讀（2026-11-09）
- **評分可靠**：人工抽查總判定一致 48/51（94%），高於 80% 門檻。三則不一致中兩則是評分者比人工更嚴（K089、K026 判為錯誤），一則是「具體／籠統」的差別（K194）；32 個評分 session 都通過 7 項無上網檢查、第一次就完整回答
- **M1 三個模型都 ≥ 80%**：第八輪問題公司的「知道」自述，Opus 97%、Sonnet 86%、Haiku 83% 與 SEC 紀錄相符 → 依預先登錄的標準，「知道」自述大多是真實記憶，實驗 2「區分力來自記得結果」的推論成立
- **M2（正確且具體）差別大**：Opus 86%、Sonnet 69%、Haiku 40%。Haiku 多半只記得「出過事、重編過」，說不出是什麼問題
- **錯誤多是細節記錯，不是憑空捏造**：GTT 把「營業成本」記成「營收」、或把不可依賴期間記成 2016–2018（實際 2017–2019）；Evoqua 說 FY2018 被重編（實際沒有重編，只有 SEC 處分）。所有問題公司在被問的年度都有公開紀錄，沒有「無紀錄支持」的自述
- **M3：對照公司與時間外樣本的「知道」多半沒有紀錄支持**
  - Sonnet：第八輪對照 17/22（77%）、時間外問題 10/11、時間外對照 22/22 無紀錄支持 → Sonnet 會對沒有紀錄的公司說「知道出事」，這說明了它對照組「知道」較多、AUC 比 Opus 低的原因（實驗 2 的事後觀察得到支持）
  - Opus：時間外樣本 0 則；第八輪對照 9 則中 5 則無紀錄支持（都是 Welbilt）
  - **Welbilt**：三個模型 15 則全部說「知道」，內容（所得稅相關重編、重大缺失）與真實紀錄相符，但那次重編的是 2016 年，不是被問的 2018 年 → 模型記得真實事件，卻套到錯的年度。這正是 MEM 每次都輸掉 Evoqua／Welbilt 這一對的原因
  - **TheMaven**：2018 年確有季報不可依賴的紀錄，但 14 則中 8 則說有 SEC 執法，AAER 清單沒有 → 判為錯誤
- **限制**：「紀錄」只包含 EDGAR 8-K 4.02 與 AAER 清單；SEC 對延遲申報公司的其他程序（非 AAER）、10-K 內揭露的調查等不在範圍內，所以「SEC 執法」類自述可能被判得偏嚴。評分者與被評的是同一系列模型，但有人工抽查 94% 一致作為檢查
