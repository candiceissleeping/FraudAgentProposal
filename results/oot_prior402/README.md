# 時間外樣本（27 對）：問題公司在訓練截止前是否已有 8-K Item 4.02

查核日：2026-11-17。資料來源：EDGAR submissions API（`data.sec.gov/submissions/CIK*.json`，含舊年度分頁檔），以 CIK 篩選 `items` 欄含 4.02 的 8-K / 8-K/A。
樣本：`results/round9/pairs.json`（分支 `claude/dreamy-volta-i6oimk`）的 27 對；分數取自 `results/mem_isolated_oot/evaluation.md`（分支 `claude/peaceful-hawking-w6z0fz`）隔離 MEM 5 次平均。
模型訓練截止：2026-06。時間外事件（T 組的 4.02）全部在 2026-07-01 至 2026-10-31。

## 1. 截止前（2026-06 以前）已有 4.02 的問題公司：9 / 27

| pid | 公司（曾用名） | 時間外 4.02 | 截止前的 4.02（申報日） | 當時更正什麼 | 和 2026 事件是同一問題嗎 | 隔離 MEM 分數（對照） | 模型理由提到過往問題 |
|---|---|---|---|---|---|---|---|
| O01T | FutureTech II Acquisition（SPAC） | 2026-07-08 | 2024-11-26、2024-12-13 | 發起人延期貸款的會計處理、延期會議贖回金額超付；FY2023、2023Q3–2024Q2 | 不同期間（2026 年更正 2024Q3–2025Q2） | 22（44，輸） | 1/5（泛指「SPAC 產業常出錯」） |
| O03T | High Wire Networks（HWN、Spectrum Global） | 2026-07-15 | 2023-12-08、2024-11-22 | 2023：衍生性負債（2023Q1–Q2）；2024：2024Q2 10-Q 錯誤 | 不同（2026 是貸款違約未入帳） | 45（23，贏） | **4/5**：「history of material weaknesses」「derivative liabilities」 |
| O13T | HCW Biologics | 2026-08-14 | 2024-05-03 | FY2023 繼續經營判斷錯誤（被詐騙 130 萬美元、800 萬票據認購違約） | 不同（2026 是 2026Q1 10-Q） | 34（16，贏） | 0/5（只提訴訟、繼續經營） |
| O15T | Solesence（Nanophase） | 2026-08-21 | 2021-08-16 | 2021Q1 PPP 貸款豁免未入帳 | 不同（2026 是存貨成本分攤） | 17（49，輸） | 0/5（5/5 說「no known issues」） |
| O16T | Brownie's Marine Group | 2026-08-24 | 2015-02-25 | FY2013 存貨高估 10.7 萬美元 | 不同（2026 是 2026Q2 用錯年度資料） | 41（30，贏） | **5/5**：「prior restatements and material weaknesses」 |
| O18T | Nuburu（Tailwind Acquisition，SPAC） | 2026-09-16 | 2021-05-14、2022-01-28、2024-10-24、2025-04-15、2025-06-25（5 次） | SPAC 認股權證分類、A 類股暫時權益、可轉債公允價值與特別股分類、債務發行成本、2025Q1 可轉債公允價值 | 類型相近（2026 是 Tekne 可轉換應收票據公允價值），工具不同 | 51（26，贏） | 1/5（「control weaknesses」） |
| O20T | GlobalTech Corp | 2026-10-02 | 2023-09-07（8-K 與 8-K/A）、2023-09-21 | 共同控制下收購的錯誤更正揭露；FY2021–2023Q2 | 不同期間（2026 更正 FY2025、2026Q1） | 45（11，贏） | 0/5 |
| O21T | Sports Entertainment Gaming Global（**Lottery.com**、Trident Acquisitions） | 2026-10-08 | 2021-06-21、2022-07-22、2022-07-26 | 2021：SPAC 認股權證；2022：未揭露的信用額度（FY2021、2022Q1），同日 CEO 辭職 | **有關聯**：2026 年更正的是 2020–2021 的 Datassure 900 萬交易虛增營收與現金，正是 2022 年 Lottery.com 醜聞的期間 | 48（17，贏） | 1/5：「Former Lottery.com … fraud for 2021–22 periods」 |
| O22T | EON Resources（HNR Acquisition，SPAC） | 2026-10-13 | 2025-04-15、2026-02-27 | 2025：遠期購買協議負債（2024Q3）；2026-02：SEC 意見函後改非控制權益損益分攤 | 不同（2026-10 是 FY2025 折耗費用） | 39（30，贏） | 2/5（「prior material weaknesses」） |

另有 3 家只在時間外事件之後補了 8-K/A 或第二份 8-K（American Resources 2026-07-29、Northann 2026-08-24、Panamera 2026-11-13），不算截止前。其餘 15 家在 EDGAR 上沒有任何更早的 4.02。

## 2. 對照公司也查了：13 / 27 有截止前的 4.02

| pid | 對照公司 | 截止前 4.02 |
|---|---|---|
| O01C | Windtree Therapeutics（Discovery Labs） | 2010 |
| O07C | Worksport | 2017 |
| O08C | OMNIQ（Quest Solution） | 2011（3 份） |
| O09C | Greenwave（MassRoots） | 2021 |
| O10C | Yunhong Green CTI（CTI Industries） | 2006、2020 |
| O11C | Greenlane Holdings | 2023 |
| O13C | Kiora（EyeGate） | 2022 |
| O18C | ESS Tech（ACON S2，SPAC） | 2021（2 份） |
| O20C | Crexendo（iMergent） | 2005 |
| O22C | Blue Dolphin Energy | 2005 |
| O23C | Omnitek Engineering | 2014 |
| O24C | IMAX | 2007（2 份） |
| O25C | Galaxy Gaming | 2017 |

## 3. 數字

| 子集 | 對數 | 問題公司平均分數 | 對照公司平均分數 | 組內勝 / 負 | AUC |
|---|---|---|---|---|---|
| 全部 | 27 | 36.8 | 26.4 | 21 / 6 | 0.69 |
| 問題公司截止前有 4.02 | 9 | 38.0 | 27.3 | 7 / 2 | 0.73 |
| 問題公司截止前沒有 4.02 | 18 | 36.2 | 25.9 | 14 / 4 | 0.68 |
| 兩邊都沒有任何截止前 4.02 | 10 | — | — | 9 / 1 | 0.85 |

對照公司：有 4.02 的 13 家平均 30.5 分，沒有的 14 家 22.6 分。

## 4. 初步判讀（描述性，事後分析，未預先登錄）
1. 「0/27 知道出事」只代表模型不知道 **2026 年的那次** 4.02。模型對部分公司的**過往**問題是有記憶的：Brownie's（5/5 提到過去重編）、High Wire（4/5）、SEGG 被認出是 Lottery.com（1/5）；對照組 Yunhong（5/5「prior restatement」）、Paysign（5/5「prior restatements and SEC matter」）也一樣。
2. 但截止前的 4.02 在對照組（13/27）比問題組（9/27）還多，而且模型也會因此把對照組分數拉高（30.5 vs 22.6）。所以「記得過往重編」不會單方面推高 AUC；把有過往 4.02 的 9 對拿掉，AUC 仍是 0.68。
3. 唯一「同一件事其實截止前就已公開」的是 SEGG / Lottery.com（2026 年更正的正是 2022 年醜聞涉及的 2020–21 交易）。拿掉這一對不影響結論。
4. 兩邊都乾淨的 10 對 AUC 反而 0.85（n 很小），組成多是「小型 OTC 公司 vs 大型老牌公司」（例如 U.S. Premium Beef、NACCO、Liberty Global 當對照），支持之前的解讀：0.69 主要來自公司類型的先驗，不是記得出事。

## 5. 限制
- 只依 EDGAR `items` 欄位；沒有發 8-K 4.02、只在 10-K 裡更正的「小 r 重編」查不到（例如 Paysign 2019–20 的重編在此查不到 4.02，但模型記得）。
- 只查同一 CIK；換 CIK 的前身公司（例如被併入的營運公司）沒有查。
- 「當時更正什麼」取自各份 8-K 的 Item 4.02 前 1,500 字，原文在 `treated_402_text.json`。

## 檔案
- `treated_402_history.json`、`control_402_history.json`：27 家問題公司、27 家對照公司全部 4.02 申報（含曾用名、首次申報日）
- `treated_402_text.json`：截止前 4.02 的 Item 4.02 原文節錄
- `model_basis_mentions_history.txt`：隔離 MEM 5 次中，模型理由提到過往重編、內控缺失等字詞的公司與原文
- 程式：`experiment/oot_prior402/`（`scan402.py`、`scan402_ctrl.py` 讀 `pairs.json`；`fetch402.py` 下載 8-K 原文）
