# 第九輪評估輸出（程式產生）

配對數：27

## 成效

| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 | n（問題+對照） |
|---|---|---|---|---|
| H1 J0 事實卡（無名稱） | 0.77 | 0.64–0.89 | 20 / 2 / 5 | 27+27 |
| J0，排除 MEM 說知道的配對 | 0.77 | 0.64–0.89 | 20 / 2 / 5 | 27+27 |
| J0，只看 4.02 涵蓋 Y0 的配對 | 0.75 | 0.59–0.89 | 14 / 1 / 5 | 20+20 |
| J1 事實卡 + 真實名稱 | 0.78 | 0.66–0.89 | 22 / 1 / 4 | 27+27 |
| MEM 只有名稱 | 0.71 | 0.56–0.83 | 21 / 2 / 4 | 27+27 |
| F-score（程式） | 0.63 | 0.45–0.79 | 14 / 0 / 10 | 24+25 |
| M-score（程式） | 0.66 | 0.46–0.84 | 11 / 0 / 4 | 16+21 |

## 目標一：模型知不知道結果

- K1 MEM 探針說知道後來有問題：問題組 0/27，對照組 0/27（標準：問題組 ≤ 20%）
  - 知道的公司：[]
- K2 J0 評分者自述知道後來有問題：0/54；有猜名稱：0
- J1（看得到名稱）自述知道後來有問題：問題組 0，對照組 0
- H3 記憶效應指數（J1 − J0：問題組 -4.6，對照組 -8.3）= +3.6，95% CI -1.4 至 +8.7（第八輪 +16.6）
- 開放式辨識猜中：0/54 []

## H4 內容擾動

| 卡 | 擾動 | 改動欄位 | J0 | 擾動後 | Δ | 方向正確 |
|---|---|---|---|---|---|---|
| R9-01 | red_flags_added | F01, F02, F16, F14 | 32 | 68 | +36 | 是 |
| R9-02 | red_flags_added | F01, F02, F16, F14 | 62 | 82 | +20 | 是 |
| R9-03 | neutralised | F01, F02, F04, F11 | 45 | 35 | -10 | 是 |
| R9-04 | neutralised | F01, F02, F04, F05, F07, F11, F14 | 72 | 40 | -32 | 是 |
| R9-05 | red_flags_added | F01, F02, F16 | 40 | 78 | +38 | 是 |
| R9-06 | red_flags_added | F02, F16, F14 | 55 | 72 | +17 | 是 |
| R9-07 | neutralised | F11, F19 | 42 | 38 | -4 | 是 |
| R9-08 | neutralised | F01, F02, F04, F05, F11, F19 | 70 | 38 | -32 | 是 |
| R9-09 | neutralised | F01, F02, F04, F07, F11, F14, F19 | 72 | 38 | -34 | 是 |
| R9-10 | red_flags_added | F01, F02, F16, F14 | 22 | 62 | +40 | 是 |
| R9-11 | red_flags_added | F01, F02, F16, F14 | 35 | 72 | +37 | 是 |
| R9-12 | neutralised | F01, F02, F04, F05, F07, F11, F14, F16, F17, F18, F19 | 88 | 35 | -53 | 是 |

方向正確 12/12；|Δ| 中位數 34

## 補充分析（非預先登錄）

| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 | n（問題+對照） |
|---|---|---|---|---|
| J0，只看規模差 ≤ 3 倍的配對 | 0.74 | 0.59–0.87 | 17 / 2 / 5 | 24+24 |
| J0，只看 MEM 排錯或平手的配對 | 0.42 | 0.12–0.76 | 2 / 0 / 4 | 6+6 |
| J0 扣除 MEM 線性部分後的殘差 | 0.65 | 0.50–0.80 | 16 / 0 / 11 | 27+27 |

- J0 與 MEM 的 Spearman ρ（54 張卡）= 0.72；J0 對 MEM 的斜率 = 0.89
- 規模差 > 3 倍的配對：[('Trans American Aquaculture, Inc', '253x'), ('American Resources Corp', '3.92x'), ('SDR Drone, Inc.', '369x')]

## 逐卡

| 卡 | 組 | 公司 | MEM | MEM 知道 | J0 | J1 | F | 4.02 涵蓋 Y0 |
|---|---|---|---|---|---|---|---|---|
| R9-01 | 對照 | KIORA PHARMACEUTICALS INC | 12 |  | 32 | 14 | 0.50 |  |
| R9-02 | 對照 | KonaTel, Inc. | 25 |  | 62 | 35 | 0.24 |  |
| R9-03 | 問題 | FutureTech II Acquisition Corp. | 25 |  | 45 | 25 | 0.77 | 1 |
| R9-04 | 問題 | SDR Drone, Inc. | 40 |  | 72 | 72 | 0.10 | 1 |
| R9-05 | 對照 | Newton Golf Company, Inc. | 25 |  | 40 | 35 | 0.12 |  |
| R9-06 | 對照 | Protopia Global Holdings Inc. | 45 |  | 55 | 42 | 0.78 |  |
| R9-07 | 問題 | GoPro, Inc. | 8 |  | 42 | 30 | 0.89 | 1 |
| R9-08 | 問題 | Trans American Aquaculture, Inc | 50 |  | 70 | 65 | 1.09 | 1 |
| R9-09 | 問題 | Nuburu, Inc. | 45 |  | 72 | 72 | 0.01 | 0 |
| R9-10 | 對照 | Crexendo, Inc. | 12 |  | 22 | 16 | 0.69 |  |
| R9-11 | 對照 | Paysign, Inc. | 15 |  | 35 | 27 | 0.81 |  |
| R9-12 | 問題 | Sports Entertainment Gaming Global Corp | 45 |  | 88 | 85 | 1.31 | 1 |
| R9-13 | 問題 | HCW Biologics Inc. | 25 |  | 55 | 40 | 0.16 | 0 |
| R9-14 | 對照 | YUNHONG GREEN CTI LTD. | 40 |  | 45 | 45 | 0.54 |  |
| R9-15 | 問題 | Netcapital Inc. | 55 |  | 60 | 62 |  | 1 |
| R9-16 | 問題 | CREDITRISKMONITOR COM INC | 8 |  | 12 | 8 | 0.46 | 1 |
| R9-17 | 對照 | Marygold Companies, Inc. | 15 |  | 42 | 22 |  |  |
| R9-18 | 問題 | GlobalTech Corp | 45 |  | 68 | 78 | 1.64 | 1 |
| R9-19 | 問題 | American Resources Corp | 50 |  | 50 | 66 | 1.23 | 1 |
| R9-20 | 對照 | ESS Tech, Inc. | 20 |  | 42 | 32 | 0.17 |  |
| R9-21 | 對照 | Worksport Ltd | 25 |  | 66 | 45 | 0.31 |  |
| R9-22 | 問題 | Globaltek Ventures, Inc. | 40 |  | 62 | 66 | 2.45 | 1 |
| R9-23 | 對照 | Skyline Bankshares, Inc. | 6 |  | 14 | 8 |  |  |
| R9-24 | 對照 | Galaxy Gaming, Inc. | 10 |  | 30 | 18 | 0.44 |  |
| R9-25 | 問題 | Datavault AI Inc. | 45 |  | 55 | 55 | 9.55 | 1 |
| R9-26 | 問題 | High Roller Technologies, Inc. | 25 |  | 62 | 42 | 0.40 | 1 |
| R9-27 | 對照 | Greenlane Holdings, Inc. | 35 |  | 68 | 62 | 0.70 |  |
| R9-28 | 對照 | OMNIQ Corp. | 50 |  | 45 | 58 | 0.51 |  |
| R9-29 | 對照 | WINDTREE THERAPEUTICS INC /DE/ | 40 |  | 58 | 42 | 1.57 |  |
| R9-30 | 問題 | EON Resources Inc. | 40 |  | 72 | 64 | 2.02 | 1 |
| R9-31 | 問題 | Optimum Communications, Inc. | 10 |  | 22 | 22 | 1.07 | 1 |
| R9-32 | 對照 | DUKE Robotics Corp. | 30 |  | 42 | 35 | 0.76 |  |
| R9-33 | 對照 | BLUE DOLPHIN ENERGY CO | 30 |  | 35 | 35 | 0.23 |  |
| R9-34 | 問題 | Securetech Innovations, Inc. | 35 |  | 66 | 65 | 0.00 | 1 |
| R9-35 | 問題 | Panamera Holdings Corp | 45 |  | 58 | 55 | 0.00 | 1 |
| R9-36 | 對照 | Omnitek Engineering Corp | 25 |  | 58 | 42 | 0.76 |  |
| R9-37 | 對照 | Artiva Biotherapeutics, Inc. | 8 |  | 20 | 10 | 0.45 |  |
| R9-38 | 問題 | Northann Corp. | 40 |  | 55 | 55 |  | 0 |
| R9-39 | 對照 | NACCO INDUSTRIES INC | 6 |  | 18 | 14 | 0.25 |  |
| R9-40 | 問題 | OLENOX INDUSTRIES INC. | 50 |  | 66 | 72 | 0.58 | 1 |
| R9-41 | 對照 | IMAX CORP | 6 |  | 12 | 15 | 0.79 |  |
| R9-42 | 問題 | Brownie's Marine Group, Inc | 35 |  | 45 | 45 | 0.62 | 0 |
| R9-43 | 問題 | BayFirst Financial Corp. | 20 |  | 25 | 24 |  | 1 |
| R9-44 | 問題 | HIGH WIRE NETWORKS, INC. | 40 |  | 62 | 52 | 1.42 | 0 |
| R9-45 | 對照 | Trio Petroleum Corp | 35 |  | 55 | 42 | 1.06 |  |
| R9-46 | 對照 | U. S. Premium Beef, LLC | 5 |  | 38 | 15 | 0.61 |  |
| R9-47 | 對照 | Liberty Global Ltd. | 8 |  | 30 | 22 | 1.15 |  |
| R9-48 | 對照 | PIXELWORKS, INC | 12 |  | 25 | 22 | 1.31 |  |
| R9-49 | 問題 | Capstone Holding Corp. | 30 |  | 62 | 42 | 2.63 | 1 |
| R9-50 | 對照 | BONK, INC. | 50 |  | 62 | 58 | 0.09 |  |
| R9-51 | 問題 | New ERA Energy & Digital, Inc. | 50 |  | 70 | 68 | 1.40 | 0 |
| R9-52 | 問題 | Pelthos Therapeutics Inc. | 20 |  | 55 | 32 | 0.00 | 0 |
| R9-53 | 對照 | Greenwave Technology Solutions, Inc. | 45 |  | 38 | 55 | 0.16 |  |
| R9-54 | 問題 | SOLESENCE, INC. | 15 |  | 58 | 42 | 1.50 | 1 |
