# 時間內 AAER 樣本隔離 MEM：結果

Opus 5.5，3 份名單 × 5 次，全部通過 7 項無上網檢查；原始紀錄在算分前已 commit。預先登錄：`protocol.md`。

## 1. 主要結果

| 樣本 | 對數 | AUC | 95% CI | 平均配對分數差 | 問題公司 ≥3/5 說知道 | 對照 ≥3/5 說知道 |
|---|---|---|---|---|---|---|
| AAER 全部 | 41 | 0.89 | 0.81–0.96 | 46.5 | 32 | 4 |
| 　第八輪 14 對 | 14 | 0.87 | 0.70–1.00 | 45.4 | 12 | 2 |
| 　第九輪 f 27 對 | 27 | 0.91 | 0.83–0.98 | 47.1 | 20 | 2 |
| 4.02 時間內（短名單） | 54 | 0.73 | 0.66–0.80 | 18.6 | 16 | 3 |

- 問題公司被記得（≥ 3/5）：AAER 32/41（78%），4.02 16/54（30%）；Fisher 精確檢定 p = 0.0000
- 至少 1 次說知道：AAER 32/41，4.02 21/54

## 2. 依「問題公司是否被記得」分組

| 樣本 | 對數 | AUC | 95% CI | 平均配對分數差 | 問題公司 ≥3/5 說知道 | 對照 ≥3/5 說知道 |
|---|---|---|---|---|---|---|
| AAER：被記得 | 32 | 0.99 | 0.97–1.00 | 60.0 | 32 | 3 |
| AAER：沒被記得 | 9 | 0.57 | 0.33–0.83 | -1.4 | 0 | 1 |
| 4.02：被記得 | 16 | 0.99 | 0.96–1.00 | 50.5 | 16 | 2 |
| 4.02：沒被記得 | 38 | 0.61 | 0.55–0.69 | 5.2 | 0 | 1 |

## 3. 規模

問題公司 Y0 總資產，以兩個樣本合併的中位數（345 百萬美元）分組。

| 標籤 | 規模 | 問題公司家數 | 被記得（≥ 3/5） | 比例 |
|---|---|---|---|---|
| AAER | 小 | 14 | 12 | 86% |
| AAER | 大 | 27 | 20 | 74% |
| 4.02 | 小 | 33 | 8 | 24% |
| 4.02 | 大 | 21 | 8 | 38% |

## 4. 敏感度

- 排除對照在 Y0 前一年至後五年內曾申報 4.02 的配對（E06, E11, E13, E16, E25, E26, E34）：34 對，AUC 0.90

## 5. 逐對

| 配對 | 來源 | 問題公司 | 分數 | 知道 | 總資產（百萬） | 對照公司 | 分數 | 知道 |
|---|---|---|---|---|---|---|---|---|
| E01 | round8 | Latch, Inc. (2021) | 86 | 5/5 | 450 | AerSale Corp. | 15 | 0/5 |
| E02 | round8 | Archer-Daniels-Midland Co. (2022) | 55 | 5/5 | 59,774 | Bunge Ltd. | 7 | 0/5 |
| E03 | round8 | Ammo, Inc. (2023) | 75 | 5/5 | 413 | National Presto Industries Inc. | 6 | 0/5 |
| E04 | round8 | Adamis Pharmaceuticals Corp. (2020) | 55 | 5/5 | 31 | PDS Biotechnology Corp. | 11 | 0/5 |
| E05 | round8 | Becton Dickinson & Co. (2019) | 25 | 5/5 | 51,765 | Boston Scientific Corp. | 7 | 0/5 |
| E06 | round8 | Ideanomics, Inc. (2018) | 64 | 5/5 | 94 | theMaven, Inc. | 60 | 5/5 |
| E07 | round8 | Cpi Aerostructures Inc. (2018) | 89 | 5/5 | 47 | Ducommun Inc. | 8 | 0/5 |
| E08 | round8 | GTT Communications, Inc. (2019) | 88 | 5/5 | 4,758 | Consolidated Communications Holdings, Inc. | 8 | 0/5 |
| E09 | round8 | Plug Power Inc. (2019) | 83 | 5/5 | 660 | Thermon Group Holdings, Inc. | 8 | 0/5 |
| E10 | round8 | Malvern Bancorp, Inc. (2020) | 62 | 5/5 | 1,208 | Provident Financial Holdings Inc. | 6 | 0/5 |
| E11 | round8 | Usa Technologies Inc. (2017) | 88 | 5/5 | 68 | Mitek Systems Inc. | 10 | 0/5 |
| E12 | round8 | SAExploration Holdings, Inc. (2018) | 93 | 5/5 | 102 | Transatlantic Petroleum Ltd. | 20 | 0/5 |
| E13 | round8 | Evoqua Water Technologies Corp. (2018) | 23 | 0/5 | 1,664 | Welbilt, Inc. | 81 | 5/5 |
| E14 | round8 | Gentex Corp. (2017) | 4 | 0/5 | 2,352 | Visteon Corp. | 8 | 0/5 |
| E15 | round9f | Overseas Shipholding Group Inc. (2010) | 85 | 5/5 | 3,854 | Tidewater Inc. | 15 | 1/5 |
| E16 | round9f | Osiris Therapeutics, Inc. (2014) | 94 | 5/5 | 88 | Protalix BioTherapeutics, Inc. | 11 | 0/5 |
| E17 | round9f | Akorn Inc. (2014) | 60 | 5/5 | 1,894 | UNITED THERAPEUTICS Corp. | 7 | 0/5 |
| E18 | round9f | Maxwell Technologies Inc. (2011) | 87 | 5/5 | 155 | Ultralife Corp. | 11 | 0/5 |
| E19 | round9f | Kbr, Inc. (2013) | 80 | 5/5 | 5,438 | Fluor Corp. | 18 | 0/5 |
| E20 | round9f | Alliance One International, Inc. (2013) | 31 | 0/5 | 1,895 | Andersons Inc. | 8 | 0/5 |
| E21 | round9f | Santander Consumer USA Holdings Inc. (2014) | 70 | 5/5 | 32,369 | Nelnet Inc. | 8 | 0/5 |
| E22 | round9f | Hertz Global Holdings Inc. (2011) | 87 | 5/5 | 17,674 | Omnicom Group Inc. | 6 | 0/5 |
| E23 | round9f | Comscore, Inc. (2013) | 45 | 5/5 | 363 | Dice Holdings, Inc. | 6 | 0/5 |
| E24 | round9f | Ppg Industries Inc. (2016) | 71 | 5/5 | 15,771 | Air Products & Chemicals Inc. | 4 | 0/5 |
| E25 | round9f | Stonemor Partners L.P. (2013) | 65 | 5/5 | 1,475 | Weight Watchers International Inc. | 7 | 0/5 |
| E26 | round9f | Quantum Corp. (2016) | 84 | 5/5 | 231 | A10 Networks, Inc. | 40 | 5/5 |
| E27 | round9f | American Realty Capital Properties, Inc. (2013) | 92 | 5/5 | 7,809 | Alexandria Real Estate Equities Inc. | 5 | 0/5 |
| E28 | round9f | Super Micro Computer, Inc. (2015) | 87 | 5/5 | 1,090 | Apple Inc. | 2 | 0/5 |
| E29 | round9f | Borgwarner Inc. (2012) | 7 | 0/5 | 6,401 | Autoliv Inc. | 7 | 0/5 |
| E30 | round9f | Power Solutions International, Inc. (2014) | 79 | 5/5 | 267 | Capstone Turbine Corp. | 51 | 4/5 |
| E31 | round9f | Revolution Lighting Technologies, Inc. (2014) | 46 | 4/5 | 127 | Orion Energy Systems, Inc. | 17 | 0/5 |
| E32 | round9f | Interface Inc. (2016) | 63 | 5/5 | 766 | Albany International Corp. | 8 | 0/5 |
| E33 | round9f | Manitex International, Inc. (2014) | 36 | 4/5 | 314 | Brooks Automation Inc. | 7 | 0/5 |
| E34 | round9f | Cherokee Inc. (2018) | 22 | 0/5 | 97 | Superior Uniform Group Inc. | 7 | 0/5 |
| E35 | round9f | Igen Networks Corp. (2018) | 39 | 0/5 | 1 | DarkPulse, Inc. | 47 | 0/5 |
| E36 | round9f | PARETEUM Corp. (2018) | 95 | 5/5 | 158 | Agilysys Inc. | 9 | 0/5 |
| E37 | round9f | WEX Inc. (2013) | 6 | 0/5 | 3,432 | MSCI Inc. | 4 | 0/5 |
| E38 | round9f | Baxter International Inc. (2017) | 76 | 5/5 | 17,111 | Stryker Corp. | 6 | 1/5 |
| E39 | round9f | Synchronoss Technologies Inc. (2013) | 64 | 5/5 | 527 | EPAM Systems, Inc. | 5 | 0/5 |
| E40 | round9f | Chs Inc. (2014) | 7 | 0/5 | 15,296 | Sysco Corp. | 4 | 0/5 |
| E41 | round9f | Tupperware Brands Corp. (2016) | 20 | 0/5 | 1,588 | Entegris Inc. | 5 | 0/5 |
