# 第三輪評分（揭盲前提交）

依 `rubric_v2.md` 給分；每一分都引用資料包原文。提交後才揭盲，之後不修改。

> **辨識註記：** 10 份我都猜得出公司。遮蔽已移除名稱、人名、地名與年份，但候選名單的 15 組各屬不同產業，
> 看內容就能把範圍縮到 2 家（例如「處方藥」「從母公司分拆的汽車零件商」），R09 還漏遮了公司網址 `bwauto.com`。
> 因此本輪仍**不是有效的盲測**；猜測已填在 `recognized_as` 欄，揭盲時會計算猜中率。

| 包 | A | B | C | D | E | 規則 | 整體 | 猜測 |
|---|---|---|---|---|---|---|---|---|
| R01 | 0 | 0 | 0 | 13 | 0 | **13** | 8 | Walgreen |
| R02 | 15 | 0 | 0 | 3 | 0 | **18** | 30 | Delphi |
| R03 | 0 | 0 | 0 | 3 | 0 | **3** | 10 | Danaher |
| R04 | 0 | 15 | 15 | 15 | 0 | **45** | 55 | Tyco |
| R05 | 0 | 15 | 5 | 8 | 0 | **28** | 35 | Under Armour |
| R06 | 0 | 0 | 0 | 8 | 0 | **8** | 15 | Motorola |
| R07 | 0 | 10 | 10 | 8 | 10 | **38** | 60 | Lucent |
| R08 | 30 | 0 | 5 | 8 | 0 | **43** | 70 | Rite Aid |
| R09 | 0 | 0 | 0 | 3 | 0 | **3** | 8 | BorgWarner |
| R10 | 0 | 0 | 0 | 0 | 0 | **0** | 5 | Columbia |

## 逐項理由與論點

**R01 — 規則 13 / 整體 8**
- D 政府行動 +10："the company settled these and other governmental actions relating to the same conduct for $7.6 million"（部分調劑處方的請款）
- D 其他訴訟 +3：私人保險計畫的同類集體訴訟
- 論點：只有一件已和解的小額請款爭議；內控、會計、關係人都沒有警訊。

**R02 — 規則 18 / 整體 30**
- A 重編 +15："In late Y0, we determined that all of the payables… should be classified as debt. As a result, our year-end Y0 and Y-1 short-term debt balances include $168 million and $164 million… Our year-end Y-1 short-term debt balances also include $287 million of payables that are beyond…"（前一年度資產負債表被改列，屬判斷題：分類更正而非損益重編）
- D 其他 +3：EPA 環境同意令、產品責任
- 論點：供應商融資計畫讓公司「延長付款期限」，原本列應付帳款、現在改列負債，顯示營運資金與負債呈現曾被美化；其餘乾淨。

**R03 — 規則 3 / 整體 10**
- D 其他 +3：氣動工具產品責任訴訟（約 3,000 名原告，已原則和解）
- 未計分：合併追溯重編（機械性）；SFAS 142 預期商譽減損；明言 "does not have any unconsolidated special purpose entities"。
- 論點：大量併購但揭露透明，無治理或會計警訊。

**R04 — 規則 45 / 整體 55**
- B 內部人借款 +15："Loans are made to employees under the Company's Key Employee Loan Program… The loans are unsecured… the maximum amount outstanding under this program was $29.5 million"
- C 判斷性估計 +10："$894.4 million of cash was paid during the year for purchase accounting liabilities"；"purchased in-process research and development… at $184.3 million… written off"（⚠️ 我知道此公司後來的問題與併購準備有關，此項可能受事後偏誤影響）
- C 併購成長 +5："purchased businesses for an aggregate cost of $19,554.2 million"
- D 政府調查 +10："target of a federal grand jury investigation concerning alleged [NAME] Water Act violations"
- D 證券訴訟 +5："thirty-eight substantially identical class action lawsuits… in connection with [COMPANY]'s financial disclosures concerning certain mergers and acquisitions and [COMPANY]'s accounting therefor"
- 論點：年度併購近 200 億美元、無擔保高管借款、投資人已就併購會計提告，三者合起來是很強的警訊。

**R05 — 規則 28 / 整體 35**
- B 內部人實體交易 +10："purchased parcels of land from an entity controlled by the Company's CEO… The purchase price for these parcels totaled $70.3 million"；向 CEO 控制的公司租飛機
- B 創辦人控制 +5："Class [NAME] Common Stock… 10 votes per share… [COMPANY] has a majority voting control over the Company"
- C 有利的估計變更 +5："During the fourth quarter of Y0, as a change in estimate, we reversed $48.0 million of incentive compensation accruals"
- D 證券訴訟 +5：關於 "expected revenue growth" 揭露的 10b-5 訴訟
- D 其他 +3：新股類別引發的股東訴訟（支付 5,900 萬美元股利和解）
- 論點：創辦人一人控制、與其實體有 7,000 萬美元交易、第四季迴轉獎金應計，加上營收成長指引被告；另有代理 CFO 上任。

**R06 — 規則 8 / 整體 15**
- D 證券訴訟 +5（已和解）："failing to timely disclose a buildup of cellular phone inventory with its distributors"
- D 其他 +3：環境污染、手機輻射產品訴訟
- 論點：曾有通路庫存的揭露爭議但已和解；其他看不到會計或治理警訊。

**R07 — 規則 38 / 整體 60**
- B 未合併實體 + 公司提供保證 +10："creation of a non-consolidated [NAME] Purpose [NAME]… to sell on a limited-recourse basis up to a maximum of $970 of customer finance loans… [COMPANY] has also agreed… to indemnify"
- C 判斷性營收 +10："As part of the revenue recognition process, [COMPANY] determines whether the notes receivable under these contracts are reasonably assured of collection based on… the ability of [COMPANY] to sell these notes"；客戶融資 $1.3B 已撥款、$3.3B 承諾、保證客戶債務 $1.4B
- D 證券訴訟 +5："misrepresented [COMPANY]'s financial condition and failed to disclose material facts"
- D 其他 +3：勞資爭議（NLRB）
- E 信評調降 +10："Investors Service lowered [COMPANY]'s credit rating… remains on review for possible further downgrade… Standard & [NAME] lowered…"
- 論點：營收靠替客戶融資撐起，再把應收出售給未合併實體來美化營業現金流（$575M、$600M），同時信評被兩家調降——營收品質與流動性同時惡化。

**R08 — 規則 43 / 整體 70**
- A 重編 +15："The company has made certain adjustments in the fourth quarter of fiscal Y0 that resulted in the restatement of its results of operation for the prior three-quarters… expensing costs previously capitalized"；並調整 Y-1、Y-2 已報告結果
- A 內部調查 +15："disclosed the results on an internal review of related party transactions"
- C 有利估計變更 +5：店鋪退出計畫假設修正 ($27.5M、$21.9M) 與迴轉稅負 $21.0M
- D 證券訴訟 +5："allege that we improperly underpaid suppliers in an effort to artificially inflate our reported earnings"
- D 其他 +3：衍生訴訟
- 論點：當年度就重編三季、調整前兩年、內部檢查關係人交易、被指控壓低付款灌水盈餘，營業現金流從 $683M 掉到 $95M 並靠售後回租籌資——這是十份中最強的警訊組合。

**R09 — 規則 3 / 整體 8**：石綿與 PCB 環境訴訟（+3），保險涵蓋；內控有效。（漏遮網址 `bwauto.com`）

**R10 — 規則 0 / 整體 5**：關係人僅為中國合資夥伴的服務費與借款（非內部人）；網站資安事件；非 GAAP 只有固定匯率營收。無計分項目。
