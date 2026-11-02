# 第七輪先導：近期 AAER 案例 + XBRL 自動計算（預先登錄）

本文件在計算任何特徵或分數之前提交。這是**先導**：目的是建立並驗證「XBRL 自動取數 → M、F、C」的流程，結果只做描述。

## 1. 樣本：問題公司（14 家）
- 來源：SEC 官方 AAER 清單，**2023 年 1 月以後發布**（`data/round7/aaer_list_2017_2026.json`）
- 納入條件：SEC 命令或起訴書的摘要寫明財務報表本身錯報（違反 GAAP），而且公司申報 10-K
- 排除：
  - 海外賄賂、政治獻金
  - 只是揭露不實
  - 只涉及非 GAAP 指標
  - 只錯報季報
  - 高管福利未揭露
  - 只有內控缺失、延遲申報、挪用公款
  - 外國發行人（20-F）或未上市公司
  - 已在舊樣本的公司（Roadrunner）
- 邊緣案例（UPS、Future FinTech、Singularity）依使用者決定**不納入**
- Y0：錯報期間內、問題公開前最後一份**原始** 10-K（不用 10-K/A）。Y-1 是前一份原始 10-K

| 公司 | CIK | AAER | Y0 期末 | Y0 10-K 申報編號 | Y-1 10-K 申報編號 |
|---|---|---|---|---|---|
| Latch | 1826000 | 4604 | 2021-12-31 | 0001826000-22-000020 | 0001193125-21-083025 ※ |
| Archer-Daniels-Midland | 7084 | 4582 | 2022-12-31 | 0000007084-23-000010 | 0000007084-22-000008 |
| Ammo | 1015383 | 4581 | 2023-03-31 | 0001493152-23-021280 | 0001493152-22-018107 |
| Adamis（DMK） | 887247 | 4555 | 2020-12-31 | 0001387131-21-004529 | 0001387131-20-003438 |
| Becton Dickinson | 10795 | 4547 | 2019-09-30 | 0000010795-19-000044 | 0000010795-18-000036 |
| Ideanomics | 837852 | 4512 | 2018-12-31 | 0001144204-19-017205 | 0001144204-18-018076 |
| CPI Aerostructures | 889348 | 4510 | 2018-12-31 | 0001387131-19-002402 | 0001387131-18-001191 |
| GTT Communications | 1315255 | 4459 | 2019-12-31 | 0001315255-20-000029 | 0001315255-19-000058 |
| Plug Power | 1093691 | 4452 | 2019-12-31 | 0001558370-20-002267 | 0001558370-19-001929 |
| Malvern Bancorp | 1550603 | 4441 | 2020-09-30 | 0001564590-21-003221 | 0001564590-19-046063 |
| USA Technologies | 896429 | 4417 | 2017-06-30 | 0001558370-17-006780 | 0001571049-16-018243 |
| SAExploration | 1514732 | 4402 | 2018-12-31 | 0001564590-19-009158 | 0001514732-18-000042 |
| Evoqua Water | 1604643 | 4390 | 2018-09-30 | 0001604643-18-000015 | 0001047469-17-007435 |
| Gentex | 355811 | 4373 | 2017-12-31 | 0000355811-18-000009 | 0000355811-17-000013 |

※ Latch 在 2021 年 6 月透過 SPAC 上市，FY2020 的 10-K 是 SPAC 空殼公司的年報，與 Latch 的營運無關。Latch 的 Y-1 數字只用 Y0 10-K 裡的比較欄位，跨年比對 III-1 視為無法檢查。

## 2. 對照組：程式自動選（每家問題公司配 1 家）
資料：SEC「Financial Statement Data Sets」每季的 `sub.txt`（申報當時的產業代碼 SIC、期末日、表單類型），以及 XBRL frames API 的總資產。

1. **候選池**：原始 10-K，期末日與問題公司的 Y0 期末日相差在 ±92 天內
2. **同產業**：申報當時的 4 位數 SIC 相同；同 SIC 的候選少於 3 家時，放寬到前 3 位，再不夠就前 2 位
3. **排除**：
   - 問題公司本身
   - 公司名稱出現在 2017–2026 年 AAER 清單的公司，名稱比對前去掉 Inc、Corp 等字尾
   - 沒有 Y-1 原始 10-K（期末日早約一年）
   - 總資產在 XBRL frames 中找不到
4. **規模**：取 |ln(對照總資產 ÷ 問題公司總資產)| 最小的一家
5. 每家對照公司只能用一次。若被前面的配對用掉，就取下一家
6. 配對結果在計算任何分數之前提交

## 3. 數字來源：XBRL（不經人工讀表）
- 從 XBRL companyfacts API 取每家公司的事實，**只保留指定 10-K 申報編號中的事實**，也就是「當時申報的數字」
- 每個項目依序嘗試以下標籤，取第一個有值的：

| 項目 | XBRL 標籤（依序） |
|---|---|
| 營收 rev | Revenues、RevenueFromContractWithCustomerExcludingAssessedTax、SalesRevenueNet、RevenueFromContractWithCustomerIncludingAssessedTax |
| 銷貨成本 cogs | CostOfGoodsAndServicesSold、CostOfRevenue、CostOfGoodsSold、CostOfServices |
| 毛利 gp | GrossProfit |
| 銷管費用 sga | SellingGeneralAndAdministrativeExpense |
| 折舊 dep | DepreciationDepletionAndAmortization、DepreciationAndAmortization、Depreciation |
| 淨利 ni | NetIncomeLoss、ProfitLoss |
| 稀釋 EPS eps_d、股數 sh_d | EarningsPerShareDiluted；WeightedAverageNumberOfDilutedSharesOutstanding |
| 現金 cash | CashAndCashEquivalentsAtCarryingValue、CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents |
| 應收帳款 ar | AccountsReceivableNetCurrent |
| 存貨 inv | InventoryNet |
| 流動資產 tca、固定資產 ppe | AssetsCurrent；PropertyPlantAndEquipmentNet |
| 總資產 ta、流動負債 tcl | Assets；LiabilitiesCurrent |
| 長期負債 ltd | LongTermDebtNoncurrent、LongTermDebt |
| 總負債 tl、權益 eq | Liabilities；StockholdersEquity |
| 負債與權益合計 tle | LiabilitiesAndStockholdersEquity |
| 非控制權益 mi | MinorityInterest |
| 保留盈餘 re | RetainedEarningsAccumulatedDeficit |
| 現金流量表 | NetCashProvidedByUsedInOperatingActivities（cfo）、…InvestingActivities（cfi）、…FinancingActivities（cff）、EffectOfExchangeRateOnCash…（fx）、CashCashEquivalentsRestrictedCash…PeriodIncreaseDecrease…（dcash） |
| 營運資金變動 | IncreaseDecreaseInAccountsReceivable（ch_ar，取負號）、IncreaseDecreaseInInventories（ch_inv，取負號） |
| 股利 div | PaymentsOfDividendsCommonStock、PaymentsOfDividends |
| 籌資 issue | ProceedsFromIssuanceOfCommonStock、ProceedsFromIssuanceOfLongTermDebt 等任一大於 0 則為 1 |

- 期間：持續期間約一年（330–400 天）的事實，以及期末時點的事實；欄位年度依期末日與 Y0 期末日的差距決定
- 期初、期末現金（cash_beg、cash_end）取現金流量表所用的現金標籤在前一年與當年期末的值。現金流量表若包含受限制現金，II-2 比較時，資產負債表的現金加上 RestrictedCashCurrent、RestrictedCashNoncurrent（有標記才加）
- II-1（損益表淨利 = 現金流量表起始淨利）在 XBRL 中兩者是同一個標籤，檢查沒有意義，列為無法檢查
- 只有「不含匯率影響」的現金變動標籤時，現金變動 = 該值 + 匯率影響
- 金額換算成百萬美元

## 4. 方法（公式與第五輪相同，程式直接沿用 `round5.features` 與 `round5.run_checks`）
- **M**：Beneish M-score，門檻 −1.78。銀行（Malvern 與其對照）不計算
- **F**：Dechow F-score，門檻 1.0。銀行不計算
- **C**：報表一致性，**只用程式結果**（C_program）作為先導的主要指標
  - 可執行的檢查：I-1、I-3、I-4、I-5、I-6、II-2、II-3、II-4、II-5、III-1
  - 不執行：I-2、II-1、II-6、II-7、IV-1（沒有對應的 XBRL 或文字）
  - 程式判定失敗的項目，會人工檢查是否為 XBRL 標籤造成的擷取錯誤，**只描述，不改分數**
- **CFO/NI**（第五輪的探索性發現，AUC 0.69）：本輪**預先登錄**的檢驗。數值越低越可疑；淨利為負時，比值的方向沒有意義，這種情況照實記錄，不另外處理

## 5. 評估（描述性）
- 各方法的 AUC 與 bootstrap 95% CI（14 對 14）
- 組內勝 / 平 / 負
- 門檻命中率：M > −1.78、F > 1.0、C > 0
- 和第五輪結果並列比較
- 樣本太小，不判定假設成立與否

## 6. 已知限制
- 我（設計者）知道哪些是問題公司。但數字由程式取得，對照組由程式選出，人工判斷只出現在「是否為擷取錯誤」的描述中
- XBRL 標籤因公司而異。取不到的項目會讓 M、F 缺值；缺值規則與第五輪相同
- 小型公司（Ammo、Adamis、SAExploration、CPI Aero）的 XBRL 品質可能較差
- AAER 列出的錯報不一定落在 Y0 年報的所有數字上，例如 ADM 只錯報部門利潤

## 7. 修訂紀錄
- 2026-11-02（計算任何特徵之前）：
  - 對照組程式修正兩個錯誤：名稱很短的 AAER 公司（例如「3M」）原本沒有被排除；總資產為 0 的公司會讓程式出錯
  - XBRL 擷取後檢查各項目的覆蓋率，發現不少公司使用其他標籤，於是加入備用標籤：
    - 營收 SalesRevenueGoodsNet、SalesRevenueServicesNet；成本 CostOfGoodsAndServiceExcludingDepreciation…；折舊 DepreciationAmortizationAndAccretionNet
    - EPS 與股數的 BasicAndDiluted 版本；現金 Cash、CashAndDueFromBanks；應收 ReceivablesNetCurrent、AccountsNotesAndLoansReceivableNetCurrent
    - 固定資產含融資租賃使用權資產的版本；長期負債 LongTermDebtAndCapitalLeaseObligations；權益含非控制權益的版本
    - 現金流量三大類的 ContinuingOperations 版本；應收變動 IncreaseDecreaseInReceivables、IncreaseDecreaseInAccountsAndNotesReceivable
  - 只看了各項目「有沒有值」，沒有看任何分數

## 8. 基準方法 B：把整份 10-K 直接交給 LLM 打風險分數（使用者新增，送出 API 之前登錄）
- 目的：最簡單的 LLM 對照基準，看「什麼都不設計，直接問」能得到多少
- 輸入：28 家公司 Y0 的 10-K 主文件加 EX-13，轉成純文字，**不遮蔽**公司名稱，也不刪段落；只去掉 inline XBRL 的隱藏標頭（`data/round7/packets/`，SHA-256 記錄在 `manifest.json`）
- 提示詞：`round7_llm.py` 的 `RISK_TASK`
  - 要求模型依這份 10-K，給出「財報有重大錯報（舞弊或嚴重會計錯誤）」的風險分數 0–100，並列出主要理由
  - 另外回答：是否認得這家公司、是否知道這個期間後來有會計問題、重編或 SEC 執法
- 模型：使用者本機的 OpenAI gpt-5.5，effort high，Batch API；每份 1 次（`--runs 1`），預算允許時可加跑第 2 次
- 指標：風險分數的 AUC、組內勝負，與 M、F、C 並列
- **預期限制**：不遮蔽名稱，模型很可能認得公司，並知道後來的 SEC 案件。分數會混入事後知識，所以這是「上限參考」，不是方法的真實能力。另外依「是否知道後來有問題」分組描述
- 2026-11-02：使用者要求先在雲端 session 跑 2 份。因為無法使用使用者的 OpenAI 金鑰，改由**新開的 Claude agent** 評分。agent 看不到這段對話或標籤，檔名改為中性名稱，提示詞與 RISK_TASK 相同。結果存於 `llm_risk_scores_claude_agent.csv`，和 gpt-5.5 的結果分開報告
