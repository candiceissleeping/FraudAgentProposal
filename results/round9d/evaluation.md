# 第九輪 d 評估輸出（程式產生）

設計：[`protocol.md`](protocol.md)

## D1 封閉式辨識（32 家名單）

- closed_1.json：**7/32**（隨機期望 1.0，單尾 p = 4.92e-05）['CPI Aerostructures', 'Malvern Bancorp', 'GTT Communications', 'USA Technologies', 'Becton Dickinson', 'The Bancorp, Inc.', 'Gentex']
- closed_2.json：**4/32**（隨機期望 1.0，單尾 p = 0.0171）['Evoqua Water', 'Malvern Bancorp', 'The Bancorp, Inc.', 'Gentex']
- D1 判定（兩次都 ≤ 3）：未通過

## 9d-b L2b 卡（不顯示可計算項數）封閉式辨識

- closed_1.json：**7/32**（隨機期望 1.0，單尾 p = 4.92e-05）['Evoqua Water', 'CPI Aerostructures', 'Ideanomics', 'GTT Communications', 'AERSALE CORP', 'The Bancorp, Inc.', 'PROVIDENT FINANCIAL HOLDINGS INC']
- closed_2.json：**5/32**（隨機期望 1.0，單尾 p = 0.00297）['THEMAVEN, INC.', 'Malvern Bancorp', 'GTT Communications', 'Travel + Leisure Co.', 'The Bancorp, Inc.']
- 判定（兩次都 ≤ 3）：未通過

## D2 第九輪 L2 封閉式辨識重複

- closed_L2.json：3/54
- closed_L2_r2.json：2/54
- closed_L2_r3.json：2/54
- 平均 2.33/54（標準 ≤ 3）：通過

## D3–D5 評分

| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 |
|---|---|---|---|
| D4 J0-L2（L2 卡，無名稱），16 對 | 0.63 | 0.42–0.81 | 9 / 1 / 6 |
| J0-L2，只看截止前 AAER（13 對） | 0.59 | 0.35–0.80 | 6 / 1 / 6 |
| J1-L2（L2 卡 + 真實名稱），16 對 | 0.78 | 0.59–0.93 | 12 / 1 / 3 |
| J1-L2，只看截止前 AAER（13 對） | 0.76 | 0.56–0.93 | 9 / 1 / 3 |
| 9d-c J0-L3（只有紅旗總數，LLM 評分），16 對 | 0.62 | 0.41–0.80 | 10 / 2 / 4 |
| 9d-c 程式：揭露紅旗總數 + 數字訊號數（不用 LLM） | 0.64 | 0.43–0.82 | 10 / 2 / 4 |
- 9d-c L3 封閉式辨識 closed_1.json：**0/32**（標準 ≤ 3）[]
- 9d-c L3 封閉式辨識 closed_2.json：**2/32**（標準 ≤ 3）['TRANSATLANTIC PETROLEUM LTD.', 'Malvern Bancorp']
- 9d-c J0-L3 自述知道後來有問題：0/32

- D3 J0-L2 自述知道後來有問題：**0/32** []；有猜名稱：0 []
- 對照：J1-L2（看得到名稱）自述知道後來有問題：13/32（問題組 12）
- D5 記憶效應指數（16 對）：問題組 +3.1，對照組 -7.7 → **+10.8**（95% CI +4.9 至 +16.9）
- D5 記憶效應指數（截止前 13 對）：問題組 +2.8，對照組 -8.4 → **+11.2**（95% CI +4.4 至 +18.4）

## 逐卡

| 卡 | 配對 | 組 | 公司 | 截止後 AAER | J0-L2 | J1-L2 | J1 知道 |
|---|---|---|---|---|---|---|---|
| A-01 | D13 | 問題 | Evoqua Water |  | 42.0 | 35.0 | False |
| A-02 | D06 | 對照 | THEMAVEN, INC. |  | 72.0 | 62.0 | False |
| A-03 | D08 | 對照 | CONSOLIDATED COMMUNICATIONS HOLDINGS, INC. |  | 20.0 | 15.0 | False |
| A-04 | D01 | 問題 | Latch | 是 | 48.0 | 62.0 | True |
| A-05 | D07 | 問題 | CPI Aerostructures |  | 66.0 | 72.0 | True |
| A-06 | D12 | 對照 | TRANSATLANTIC PETROLEUM LTD. |  | 30.0 | 30.0 | False |
| A-07 | D10 | 問題 | Malvern Bancorp |  | 50.0 | 68.0 | True |
| A-08 | D05 | 對照 | BOSTON SCIENTIFIC CORP |  | 45.0 | 22.0 | False |
| A-09 | D04 | 對照 | PDS BIOTECHNOLOGY CORP |  | 32.0 | 22.0 | False |
| A-10 | D07 | 對照 | DUCOMMUN INC /DE/ |  | 15.0 | 14.0 | False |
| A-11 | D13 | 對照 | WELBILT, INC. |  | 68.0 | 70.0 | True |
| A-12 | D02 | 問題 | Archer-Daniels-Midland |  | 35.0 | 24.0 | True |
| A-13 | D11 | 對照 | MITEK SYSTEMS INC |  | 45.0 | 32.0 | False |
| A-14 | D06 | 問題 | Ideanomics |  | 72.0 | 72.0 | True |
| A-15 | D09 | 對照 | THERMON GROUP HOLDINGS, INC. |  | 18.0 | 15.0 | False |
| A-16 | D14 | 對照 | VISTEON CORP |  | 15.0 | 12.0 | False |
| A-17 | D08 | 問題 | GTT Communications |  | 42.0 | 55.0 | True |
| A-18 | D15 | 問題 | Travel + Leisure Co. | 是 | 27.0 | 22.0 | False |
| A-19 | D02 | 對照 | BUNGELTD |  | 62.0 | 34.0 | False |
| A-20 | D11 | 問題 | USA Technologies |  | 30.0 | 35.0 | True |
| A-21 | D12 | 問題 | SAExploration |  | 25.0 | 40.0 | True |
| A-22 | D05 | 問題 | Becton Dickinson |  | 30.0 | 22.0 | True |
| A-23 | D09 | 問題 | Plug Power |  | 30.0 | 30.0 | True |
| A-24 | D01 | 對照 | AERSALE CORP |  | 32.0 | 25.0 | False |
| A-25 | D16 | 問題 | The Bancorp, Inc. | 是 | 32.0 | 35.0 | False |
| A-26 | D14 | 問題 | Gentex |  | 14.0 | 8.0 | False |
| A-27 | D10 | 對照 | PROVIDENT FINANCIAL HOLDINGS INC |  | 12.0 | 10.0 | False |
| A-28 | D04 | 問題 | Adamis |  | 60.0 | 72.0 | True |
| A-29 | D15 | 對照 | BOYD GAMING CORP |  | 15.0 | 12.0 | False |
| A-30 | D16 | 對照 | NICOLET BANKSHARES INC |  | 12.0 | 8.0 | False |
| A-31 | D03 | 問題 | Ammo |  | 55.0 | 55.0 | True |
| A-32 | D03 | 對照 | NATIONAL PRESTO INDUSTRIES INC |  | 35.0 | 22.0 | False |
