# 時間內 4.02 樣本隔離 MEM：結果

Opus 5.5，5 次執行 × 2 份名單（A、B），全部通過 7 項無上網檢查；原始紀錄在算分前已 commit。預先登錄：`protocol.md`。

## 1. 主要結果

| 樣本 | 事件時間 | 對數 | AUC | 95% CI | 組內勝／平／負 | 平均配對分數差 |
|---|---|---|---|---|---|---|
| **時間內（本實驗）** | 2023-01 至 2025-06 | 54 | **0.73** | 0.66–0.80 | 43／5／6 | 18.3 |
| 時間外（實驗 B） | 2026-07 至 2026-10 | 27 | 0.69 | 0.53–0.84 | 21／0／6 | 10.4 |

- AUC 差（時間內 − 時間外）：**+0.04**，95% CI -0.13 至 +0.21
- 平均配對分數差的差：+7.9 分，95% CI -1.9 至 +18.8

## 2. 模型說「知道後來出事」

- 問題公司 5 次中 ≥ 3 次說知道：16/54；對照公司：2/54
- 只用「知道」比例排序的 AUC：0.63
- 問題公司被記得（≥ 3/5 說知道）：16 對，AUC 0.98，平均配對分數差 50.7
- 問題公司未被記得：38 對，AUC 0.60，平均配對分數差 4.6

## 3. 敏感度分析
- 只用名單 A（27 對）：AUC 0.73
- 只用名單 B（27 對）：AUC 0.75
- 實驗 B 排除對照自 2021 年起曾申報 4.02 的配對（O09, O11, O13, O18）後：23 對，AUC 0.71

## 4. 逐對

| 配對 | 問題公司 | 分數 | 知道 | 對照公司 | 分數 | 知道 |
|---|---|---|---|---|---|---|
| I01 | Bancorp, Inc. | 17 | 0/5 | Nicolet Bankshares Inc. | 6 | 0/5 |
| I02 | Quantum Energy Inc. | 49 | 0/5 | Us Energy Corp. | 19 | 0/5 |
| I03 | BigBear.ai Holdings, Inc. | 77 | 5/5 | Weave Communications, Inc. | 8 | 0/5 |
| I04 | Greenway Technologies Inc. | 51 | 0/5 | RespireRx Pharmaceuticals Inc. | 35 | 0/5 |
| I05 | Heat Biologics, Inc. | 15 | 0/5 | Milestone Pharmaceuticals Inc. | 7 | 0/5 |
| I06 | Hoops Scouting Usa | 45 | 0/5 | Tofla Megaline Inc. | 45 | 0/5 |
| I07 | BYTE Acquisition Corp. | 15 | 0/5 | Data443 Risk Mitigation, Inc. | 42 | 0/5 |
| I08 | SITIME Corp. | 6 | 0/5 | Ambarella Inc. | 6 | 0/5 |
| I09 | Faraday Future Intelligent Electric Inc. | 69 | 5/5 | Kandi Technologies Group, Inc. | 44 | 1/5 |
| I10 | Pennsylvania Real Estate Investment Trust | 19 | 0/5 | Alexander & Baldwin, Inc. | 6 | 0/5 |
| I11 | Lazydays Holdings, Inc. | 32 | 0/5 | GPB Automotive Portfolio, L.P. | 43 | 5/5 |
| I12 | COMSovereign Holding Corp. | 65 | 5/5 | Vislink Technologies, Inc. | 34 | 0/5 |
| I13 | InFinT Acquisition Corp. | 16 | 0/5 | Global Technology Acquisition Corp. I | 16 | 0/5 |
| I14 | Maui Land & Pineapple Co. Inc. | 9 | 0/5 | Comstock Holding Companies, Inc. | 12 | 0/5 |
| I15 | Allogene Therapeutics, Inc. | 6 | 0/5 | Sana Biotechnology, Inc. | 6 | 0/5 |
| I16 | Hyzon Motors Inc. | 91 | 5/5 | Fuelcell Energy Inc. | 14 | 0/5 |
| I17 | SAB Biotherapeutics, Inc. | 20 | 0/5 | Renovacor, Inc. | 16 | 0/5 |
| I18 | Gatos Silver, Inc. | 74 | 5/5 | McEwen Mining Inc. | 14 | 0/5 |
| I19 | VNUE, Inc. | 50 | 0/5 | Medies | 49 | 0/5 |
| I20 | Skillz Inc. | 39 | 3/5 | Cars.com Inc. | 6 | 0/5 |
| I21 | Uniti Group Inc. | 10 | 0/5 | Apple Hospitality REIT, Inc. | 5 | 0/5 |
| I22 | Agrify Corp. | 56 | 5/5 | Calavo Growers Inc. | 25 | 2/5 |
| I23 | Marathon Digital Holdings, Inc. | 77 | 5/5 | America First Multifamily Investors, L.p. | 10 | 0/5 |
| I24 | Assure Holdings Corp. | 50 | 1/5 | Avinger Inc. | 16 | 0/5 |
| I25 | Discover Financial Services | 33 | 5/5 | Toyota Motor Credit Corp. | 7 | 0/5 |
| I26 | 1606 Corp. | 52 | 0/5 | Virtual Interactive Technologies Corp. | 48 | 0/5 |
| I27 | Capital City Bank Group Inc. | 6 | 0/5 | Mid Penn Bancorp Inc. | 6 | 0/5 |
| I28 | Logiq, Inc. | 48 | 0/5 | Society Pass Incorporated. | 40 | 0/5 |
| I29 | Evolv Technologies Holdings, Inc. | 82 | 5/5 | AstroNova, Inc. | 12 | 0/5 |
| I30 | Inspired Entertainment, Inc. | 75 | 5/5 | Avid Technology, Inc. | 10 | 0/5 |
| I31 | Bright Mountain Media, Inc. | 53 | 3/5 | Innovative Solutions & Support Inc. | 7 | 0/5 |
| I32 | iANTHUS CAPITAL HOLDINGS, Inc. | 36 | 0/5 | Limoneira Co. | 8 | 0/5 |
| I33 | Plum Acquisition Corp. I | 16 | 0/5 | OneSpan Inc. | 18 | 0/5 |
| I34 | Tupperware Brands Corp. | 79 | 5/5 | Armstrong World Industries Inc. | 5 | 0/5 |
| I35 | Edgemode, Inc. | 53 | 0/5 | Welsis Corp. | 50 | 0/5 |
| I36 | Cellectar Biosciences, Inc. | 13 | 0/5 | Longeveron Inc. | 13 | 0/5 |
| I37 | Cytosorbents Corp. | 12 | 0/5 | Sensus Healthcare, Inc. | 11 | 0/5 |
| I38 | Calumet Specialty Products Partners, L.P. | 12 | 0/5 | Cvr Energy Inc. | 8 | 0/5 |
| I39 | Laser Photonics Corp. | 63 | 5/5 | Expion360 Inc. | 28 | 0/5 |
| I40 | Lincoln National Corp. | 27 | 2/5 | Jackson Financial Inc. | 31 | 3/5 |
| I41 | First Northwest Bancorp | 12 | 0/5 | ESSA Bancorp, Inc. | 7 | 0/5 |
| I42 | Cottonwood Communities, Inc. | 10 | 0/5 | SmartStop Self Storage REIT, Inc. | 8 | 0/5 |
| I43 | Phoenix Motor Inc. | 40 | 0/5 | Nxu, Inc. | 37 | 0/5 |
| I44 | Dzs Inc. | 86 | 5/5 | Clearfield, Inc. | 8 | 0/5 |
| I45 | BIMI International Medical Inc. | 57 | 0/5 | Cosmos Health Inc. | 39 | 0/5 |
| I46 | Atlantic Coastal Acquisition Corp. II | 17 | 0/5 | BioCardia, Inc. | 15 | 0/5 |
| I47 | Biocept Inc. | 22 | 0/5 | Biodesix Inc. | 12 | 0/5 |
| I48 | OneMeta Inc. | 46 | 0/5 | KwikClick, Inc. | 46 | 0/5 |
| I49 | Luxurban Hotels Inc. | 65 | 5/5 | Broad Street Realty, Inc. | 42 | 1/5 |
| I50 | Coeptis Therapeutics Holdings, Inc. | 37 | 0/5 | BTCS Inc. | 27 | 0/5 |
| I51 | AZEK Co. Inc. | 9 | 0/5 | Aptargroup, Inc. | 5 | 0/5 |
| I52 | Genius Brands International, Inc. | 28 | 0/5 | Cinedigm Corp. | 22 | 0/5 |
| I53 | Rithm Capital Corp. | 9 | 0/5 | Crown Castle Inc. | 9 | 0/5 |
| I54 | Optical Cable Corp. | 8 | 0/5 | Aqua Metals, Inc. | 17 | 0/5 |
