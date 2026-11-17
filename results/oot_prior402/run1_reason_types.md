# 時間外 27 家問題公司：MEM 第 1 次執行的理由分類

來源：`results/mem_isolated_oot/run1.json`（分支 `claude/peaceful-hawking-w6z0fz`），只給公司名稱與會計年度，Opus 5.5 無工具環境。
判斷：同一對中問題公司分數 > 對照公司為「對」，相等為「平」，小於為「錯」。第 1 次執行共 20 對／1 平／6 錯。
理由類型：依模型寫的 basis 人工歸類（單人、事後分類），取主要理由。

| pid | 問題公司 | 分數 | 對照公司 | 分數 | 判斷 | 理由類型 | 模型理由（原文） |
|---|---|---|---|---|---|---|---|
| O01 | FutureTech II Acquisition | 25 | Windtree Therapeutics | 45 | 錯 | 公司類型 | SPAC; simple trust accounting though extension/redemption issues common |
| O02 | BayFirst Financial | 25 | Skyline Bankshares | 12 | 對 | 業務／會計判斷 | Small bank with SBA lending losses and strategic changes; credit-reserve judgment risk |
| O03 | High Wire Networks | 45 | KonaTel | 30 | 對 | 過去有前例 | Micro-cap with acquisitions/divestitures, derivative liabilities, prior material weaknesses |
| O04 | Trans American Aquaculture | 55 | U.S. Premium Beef | 10 | 對 | 公司類型 | Tiny OTC development-stage company; going concern and weak controls |
| O05 | American Resources | 50 | NACCO Industries | 8 | 對 | 過去有前例 | Complex related-party structures, spin-offs, idled coal assets, prior governance concerns |
| O06 | New Era Energy & Digital | 45 | Trio Petroleum | 40 | 對 | 業務／會計判斷 | Recent small-cap IPO with pivot to digital infrastructure; acquisition accounting |
| O07 | Securetech Innovations | 50 | Worksport | 30 | 對 | 公司類型 | Tiny OTC issuer; minimal operations |
| O08 | CreditRiskMonitor.com | 12 | OMNIQ | 45 | 錯 | 公司類型 | Small, stable subscription business; simple accounting |
| O09 | Olenox Industries | 50 | Greenwave Technology Solutions | 55 | 錯 | 公司類型 | Micro-cap energy roll-up/reverse-merger profile; high control and valuation risk |
| O10 | Northann | 45 | Yunhong Green CTI | 45 | 平 | 地區（中國） | Small China-linked Nasdaq issuer; limited transparency and controls |
| O11 | Capstone Holding | 35 | Greenlane Holdings | 45 | 錯 | 公司類型 | Micro-cap building products holding company; small-scale controls |
| O12 | Pelthos Therapeutics | 30 | Artiva Biotherapeutics | 12 | 對 | 業務／會計判斷 | Post-reverse-merger (Channel Therapeutics) commercial biotech; new accounting areas |
| O13 | HCW Biologics | 40 | Kiora Pharmaceuticals | 15 | 對 | 財務困境 | Distressed biotech with litigation, going concern and delisting risk |
| O14 | Netcapital | 55 | Marygold Companies | 20 | 對 | 過去有前例 | History of large equity-security receivables valued judgmentally; large impairments, going concern |
| O15 | Solesence | 20 | BONK | 45 | 錯 | 公司類型 | Small materials company (formerly Nanophase); no known issues |
| O16 | Brownie's Marine Group | 45 | Newton Golf Company | 35 | 對 | 過去有前例 | OTC micro-cap with acquisitions and reported control weaknesses |
| O17 | SDR Drone | 50 | Duke Robotics | 45 | 對 | 公司類型 | Obscure micro-cap; limited operating history |
| O18 | Nuburu | 55 | ESS Tech | 30 | 對 | 財務困境 | Distressed de-SPAC with strategic pivots, heavy dilution, going concern |
| O19 | Optimum Communications | 12 | Liberty Global | 8 | 對 | 公司類型 | Renamed Altice USA; heavy leverage but large audited filer |
| O20 | GlobalTech | 50 | Crexendo | 15 | 對 | 地區（海外） | OTC holding company with foreign operations; limited transparency |
| O21 | Sports Entertainment Gaming Global | 55 | Pixelworks | 20 | 對 | 公司類型 | Obscure OTC issuer; shell-like risk profile |
| O22 | EON Resources | 45 | Blue Dolphin Energy | 30 | 對 | 過去有前例 | De-SPAC oil producer; debt stress, warrant/earnout accounting, prior material weaknesses |
| O23 | Globaltek Ventures | 55 | Omnitek Engineering | 35 | 對 | 公司類型 | Obscure OTC issuer; high shell/control risk |
| O24 | GoPro | 15 | IMAX | 10 | 對 | 公司類型 | Established Big-4-audited issuer; going-concern/debt pressure but no known accounting issues |
| O25 | High Roller Technologies | 30 | Galaxy Gaming | 15 | 對 | 公司類型 | Recent small-cap IPO online casino operator; limited track record |
| O26 | Datavault AI | 45 | Paysign | 25 | 對 | 業務／會計判斷 | Formerly WiSA; heavy dilution, unusual IP/asset transactions and valuation judgments |
| O27 | Panamera Holdings | 45 | Protopia Global Holdings | 55 | 錯 | 公司類型 | Tiny shell-like OTC issuer; small auditor, weak controls typical |

## 依理由類型

| 理由類型 | 家數 | 對／平／錯 | 問題公司平均分數 |
|---|---|---|---|
| 公司類型（規模、OTC、殼、SPAC、新上市、大型穩健） | 14 | 8／0／6 | 36 |
| 過去有前例（過往內控缺失、治理問題、會計爭議） | 5 | 5／0／0 | 48 |
| 業務／會計判斷（轉型、併購、估值、放款損失） | 4 | 4／0／0 | 36 |
| 財務困境（繼續經營、稀釋、下市風險） | 2 | 2／0／0 | 48 |
| 地區（中國、海外營運） | 2 | 1／1／0 | 48 |

## 排除「過去有前例」後的 AUC（事後分析）

AUC 為全部問題公司 × 對照公司的比較（平手算一半），括號內為配對 bootstrap 95% CI（10,000 次）。

| 子集 | 對數 | AUC，5 次平均分數 | 勝／平／負 | AUC，第 1 次 | 勝／平／負 |
|---|---|---|---|---|---|
| 全部 | 27 | 0.69（0.53–0.85） | 21／0／6 | 0.72（0.58–0.84） | 20／1／6 |
| 排除問題公司理由為「過去有前例」的 5 對（O03、O05、O14、O16、O22） | 22 | 0.64（0.46–0.81） | 16／0／6 | 0.67（0.52–0.80） | 15／1／6 |
| 再排除對照公司理由提到過往問題的 4 對（O09、O10、O24、O26） | 18 | 0.65（0.43–0.84） | 13／0／5 | 0.68（0.50–0.84） | 13／0／5 |
| 只留問題公司理由為「公司類型」的 14 對 | 14 | 0.53（0.30–0.76） | 8／0／6 | 0.59（0.39–0.77） | 8／0／6 |
| 只有「過去有前例」的 5 對 | 5 | 1.00 | 5／0／0 | 1.00 | 5／0／0 |

注意：依模型理由排除是事後、與分數相關的篩選（理由寫「過去有前例」的公司分數本來就高、5 對全勝），AUC 下降有一部分是篩選造成的。
依客觀條件（EDGAR 上截止前有 4.02 的 9 家）排除時 AUC 為 0.68，見 `README.md`。

## 讀年報是否超過只給名稱：依理由分組（事後分析）

分數取自第九輪 g（分支 `claude/dreamy-volta-i6oimk`，`results/round9g/evaluation.md`）的逐對表：MEM＝第九輪原始只給名稱（單次）、RAW＝整份 10-K 不遮蔽、J0＝事實卡不給名稱。
分組依本檔上方的理由類型（隔離 MEM 第 1 次執行）。括號內為配對 bootstrap 95% CI。

| 子集 | 對數 | 只給名稱 | 整份 10-K | 事實卡（無名稱） | 10-K − 名稱 | 事實卡 − 名稱 |
|---|---|---|---|---|---|---|
| 全部 | 27 | 0.71（0.56–0.85） | 0.76（0.60–0.89） | 0.77（0.66–0.88） | +0.05（−0.03 至 +0.12） | +0.06（−0.05 至 +0.17） |
| 有具體了解 | 11 | 0.90（0.81–0.99） | 0.88（0.72–1.00） | 0.85（0.73–1.00） | −0.01（−0.17 至 +0.07） | −0.05（−0.17 至 +0.08） |
| 沒有具體了解 | 16 | 0.58（0.38–0.78） | 0.70（0.46–0.89） | 0.73（0.55–0.89） | +0.12（+0.03 至 +0.21） | +0.15（−0.00 至 +0.27） |
| 　其中只看公司類型 | 14 | 0.55（0.34–0.77） | 0.68（0.42–0.89） | 0.70（0.50–0.87） | +0.12（+0.01 至 +0.23） | +0.15（−0.03 至 +0.28） |

注意：分組與只給名稱的對錯相關（「有具體了解」組在只給名稱時全部判對），因此「沒有具體了解」組的增幅有一部分是迴歸平均造成的；分組為事後、單人分類；樣本小。此表只用來形成下一步要預先登錄的假設。
