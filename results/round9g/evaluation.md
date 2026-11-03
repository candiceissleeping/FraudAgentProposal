# 第九輪 g 評估輸出（程式產生）

設計：[`protocol.md`](protocol.md)

完成評分：54/54

| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 | n |
|---|---|---|---|---|
| **G1 RAW：整份 10-K，不遮蔽** | 0.76 | 0.62–0.88 | 22 / 0 / 5 | 27+27 |
| 參考：J0 事實卡（第九輪） | 0.77 | 0.64–0.89 | 20 / 2 / 5 | 27+27 |
| 參考：MEM 只給名稱（第九輪） | 0.71 | 0.56–0.83 | 21 / 2 / 4 | 27+27 |

- **G2 RAW − J0 的 AUC 差：-0.02（配對 bootstrap 95% CI -0.12 至 +0.09）**
- G3 自述知道後來有問題：問題組 0/27，對照組 0/27 []
- G4 自述認得公司：51/54；名稱猜中：50/54

| G5 扣除 MEM 線性部分後的殘差 | AUC | 95% CI | 組內勝 / 平 / 負 | n |
|---|---|---|---|---|
| RAW 殘差 | 0.66 | 0.51–0.80 | 20 / 0 / 7 | 27+27 |
| J0 殘差（參考） | 0.65 | 0.50–0.79 | 16 / 0 / 11 | 27+27 |

- Spearman ρ：RAW vs J0 = 0.76；RAW vs MEM = 0.88；J0 vs MEM = 0.72

## 逐對

| 配對 | 問題公司 | RAW | J0 | MEM | 對照公司 | RAW | J0 | MEM |
|---|---|---|---|---|---|---|---|---|
| P01 | FutureTech II Acquisition Corp. | 45.0 | 45 | 25 | WINDTREE THERAPEUTICS INC /DE/ | 27.0 | 58 | 40 |
| P02 | BayFirst Financial Corp. | 30.0 | 25 | 20 | Skyline Bankshares, Inc. | 8.0 | 14 | 6 |
| P03 | HIGH WIRE NETWORKS, INC. | 48.0 | 62 | 40 | KonaTel, Inc. | 72.0 | 62 | 25 |
| P04 | Trans American Aquaculture, Inc | 85.0 | 70 | 50 | U. S. Premium Beef, LLC | 6.0 | 38 | 5 |
| P05 | American Resources Corp | 82.0 | 50 | 50 | NACCO INDUSTRIES INC | 10.0 | 18 | 6 |
| P06 | New ERA Energy & Digital, Inc. | 62.0 | 70 | 50 | Trio Petroleum Corp | 58.0 | 55 | 35 |
| P07 | Securetech Innovations, Inc. | 74.0 | 66 | 35 | Worksport Ltd | 40.0 | 66 | 25 |
| P08 | CREDITRISKMONITOR COM INC | 7.0 | 12 | 8 | OMNIQ Corp. | 82.0 | 45 | 50 |
| P09 | OLENOX INDUSTRIES INC. | 78.0 | 66 | 50 | Greenwave Technology Solutions, Inc. | 66.0 | 38 | 45 |
| P10 | Northann Corp. | 74.0 | 55 | 40 | YUNHONG GREEN CTI LTD. | 72.0 | 45 | 40 |
| P11 | Capstone Holding Corp. | 45.0 | 62 | 30 | Greenlane Holdings, Inc. | 70.0 | 68 | 35 |
| P12 | Pelthos Therapeutics Inc. | 30.0 | 55 | 20 | Artiva Biotherapeutics, Inc. | 6.0 | 20 | 8 |
| P13 | HCW Biologics Inc. | 66.0 | 55 | 25 | KIORA PHARMACEUTICALS INC | 22.0 | 32 | 12 |
| P14 | Netcapital Inc. | 75.0 | 60 | 55 | Marygold Companies, Inc. | 22.0 | 42 | 15 |
| P15 | SOLESENCE, INC. | 28.0 | 58 | 15 | BONK, INC. | 78.0 | 62 | 50 |
| P16 | Brownie's Marine Group, Inc | 62.0 | 45 | 35 | Newton Golf Company, Inc. | 35.0 | 40 | 25 |
| P17 | SDR Drone, Inc. | 85.0 | 72 | 40 | DUKE Robotics Corp. | 18.0 | 42 | 30 |
| P18 | Nuburu, Inc. | 62.0 | 72 | 45 | ESS Tech, Inc. | 25.0 | 42 | 20 |
| P19 | Optimum Communications, Inc. | 15.0 | 22 | 10 | Liberty Global Ltd. | 9.0 | 30 | 8 |
| P20 | GlobalTech Corp | 72.0 | 68 | 45 | Crexendo, Inc. | 14.0 | 22 | 12 |
| P21 | Sports Entertainment Gaming Global Corp | 82.0 | 88 | 45 | PIXELWORKS, INC | 14.0 | 25 | 12 |
| P22 | EON Resources Inc. | 78.0 | 72 | 40 | BLUE DOLPHIN ENERGY CO | 45.0 | 35 | 30 |
| P23 | Globaltek Ventures, Inc. | 78.0 | 62 | 40 | Omnitek Engineering Corp | 45.0 | 58 | 25 |
| P24 | GoPro, Inc. | 22.0 | 42 | 8 | IMAX CORP | 12.0 | 12 | 6 |
| P25 | High Roller Technologies, Inc. | 62.0 | 62 | 25 | Galaxy Gaming, Inc. | 12.0 | 30 | 10 |
| P26 | Datavault AI Inc. | 80.0 | 55 | 45 | Paysign, Inc. | 22.0 | 35 | 15 |
| P27 | Panamera Holdings Corp | 52.0 | 58 | 45 | Protopia Global Holdings Inc. | 70.0 | 55 | 45 |
