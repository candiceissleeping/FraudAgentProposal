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
