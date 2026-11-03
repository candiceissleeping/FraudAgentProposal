# 第九輪 b 評估輸出（程式產生）

設計：[`protocol.md`](protocol.md)

## 9b-A AAER 時間外案例

| 配對 | 組 | 公司 | Y0 | A1(a) 知道會計問題 | A1(b) 知道 SEC 執法 | MEM 分數 | J0 | J1 | J0 自述知道 |
|---|---|---|---|---|---|---|---|---|---|
| P01 | 問題 | Latch, Inc. | 2021 | 是 | 否 | 85 | 72 | 78 | False |
| P01 | 對照 | WATSCO INC | 2021 | 否 | 否 | 4 | 30 | 14 | False |
| P02 | 問題 | Travel + Leisure Co. | 2019 | 否 | 否 | 8 | 24 | 22 | False |
| P02 | 對照 | BOYD GAMING CORP | 2019 | 否 | 否 | 5 | 18 | 10 | False |
| P03 | 問題 | The Bancorp, Inc. | 2024 | 否 | 否 | 20 | 22 | 22 | False |
| P03 | 對照 | NICOLET BANKSHARES INC | 2024 | 否 | 否 | 5 | 14 | 10 | False |

- A1(b) 問題組知道 SEC 執法：**0/3**（標準 0/3）
- A1(a) 問題組知道該期間有會計問題或重編：1/3
- A2 J0 自述知道後來有問題：0/6
- A2 開放式辨識猜中：0/6 []
- A3 J0 組內（問題 vs 對照）：勝 / 勝 / 勝

## 9b-B 第九輪封閉式辨識（54 家名單 + 54 張 J0 卡）

- 配對正確：**34/54**（只靠產業大類隨機猜的期望 7.0，單尾 p = 8.13e-20）
  - 問題組 14/27，對照組 20/27
- 指派到正確配對（本身或配對公司）：36/54
- 指派的公司與卡片同組（問題／對照）：44/54
- 配對正確者中，MEM 說知道後來有問題：0 []
- 配對正確的卡：['American Resources Corp', 'Artiva Biotherapeutics, Inc.', 'BLUE DOLPHIN ENERGY CO', 'BONK, INC.', 'BayFirst Financial Corp.', "Brownie's Marine Group, Inc", 'CREDITRISKMONITOR COM INC', 'Capstone Holding Corp.', 'Crexendo, Inc.', 'Datavault AI Inc.', 'ESS Tech, Inc.', 'Galaxy Gaming, Inc.', 'GoPro, Inc.', 'Greenlane Holdings, Inc.', 'HCW Biologics Inc.', 'IMAX CORP', 'KIORA PHARMACEUTICALS INC', 'KonaTel, Inc.', 'Liberty Global Ltd.', 'Marygold Companies, Inc.', 'NACCO INDUSTRIES INC', 'Netcapital Inc.', 'Newton Golf Company, Inc.', 'Nuburu, Inc.', 'OMNIQ Corp.', 'Optimum Communications, Inc.', 'Paysign, Inc.', 'SOLESENCE, INC.', 'Skyline Bankshares, Inc.', 'Sports Entertainment Gaming Global Corp', 'Trans American Aquaculture, Inc', 'Trio Petroleum Corp', 'U. S. Premium Beef, LLC', 'YUNHONG GREEN CTI LTD.']
