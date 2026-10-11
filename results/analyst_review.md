# EDGAR-CORPUS 10-K 風險評分報告（分析師覆核版）

10 家公司，每家讀一份 10-K（來源：EDGAR-CORPUS），只根據 **10-K 原文** 判分；每個理由都附原文引句與出處章節。
規則式（關鍵字）初步分數見 `rule_based_report.md`，完整命中證據見各 `<cik>_<year>.json`。

> ⚠️ **重要限制：本覆核不是盲測。** 評分者事先知道哪些公司後來出事（實驗設計本身就揭露了組別），
> 即使只引用 10-K 原文，挑選「哪段文字值得注意」仍受事後偏誤影響。規則式分數沒有這個問題，但準確度差很多（見文末比較）。

## 總表

| 排名 | 公司 | 10-K 年度 | 組別 | 規則式分數 | **最終分數** | 等級 | 一句話理由 |
|---|---|---|---|---|---|---|---|
| 1 | Enron | FY2000 | 問題組 | 28.4 | **80** | High | 與高階主管控制的合夥企業做自我避險交易，認列約 5 億美元收入 |
| 2 | WorldCom | FY2001 | 問題組 | 38.3 | **65** | Elevated | 借給 CEO 1.44 億美元並代償 1.99 億美元擔保；產業惡化、證券訴訟 |
| 3 | HealthSouth | FY2001 | 問題組 | 36.7 | **60** | Elevated | DOJ Medicare 和解與介入訴訟、證券集體訴訟、內部人關聯供應商 |
| 3 | Lehman Brothers | FY2007 | 問題組 | 35.0 | **60** | Elevated | 114 億美元資產轉入 Level III、25 億未實現損失、自訂槓桿指標 |
| 3 | Valeant | FY2014 | 問題組 | 66.7 | **60** | Elevated | 成長靠連年漲價、153 億美元負債的併購模式、多項政府調查 |
| 6 | Kraft Heinz | FY2017 | 問題組 | 68.3 | **55** | Elevated | 2017 年已重編兩季報表並揭露內控重大缺失 |
| 7 | Johnson & Johnson | FY2019 | 對照組 | 30.0 | **35** | Moderate | 滑石粉 / 鴉片類訴訟與 DOJ、SEC 傳票；但無會計警訊 |
| 8 | Costco | FY2019 | 對照組 | 48.3 | **30** | Moderate | 前一年度 IT 內控重大缺失（已補正）及相關證券訴訟 |
| 9 | Microsoft | FY2019 | 對照組 | 25.0 | **15** | Low | 匈牙利子公司 FCPA 和解 2,530 萬美元，其餘乾淨 |
| 10 | Apple | FY2019 | 對照組 | 11.7 | **10** | Low | 歐盟國家補助稅務爭議（已入託管），無會計警訊 |

等級：0–24 Low、25–49 Moderate、50–74 Elevated、75–100 High。
分數代表「10-K 文字中可見的財報可信度 / 治理 / 法律風險」，**不是**舞弊機率。

---

## 1. Enron Corp — FY2000 10-K（2001 年 4 月申報）— **80 / High**

規則式只給 28.4（抓到 mark-to-market 與一般「未合併關係企業」字樣），**真正的警訊藏在附註 16，關鍵字抓不到語意**。

| 證據 | 原文（Item 14，財報附註） | 為何是問題 |
|---|---|---|
| 交易對手由公司高階主管控制 | "Enron entered into transactions with limited partnerships (the Related Party) whose general partner's managing member is a senior officer of Enron." | 利益衝突；同一份 10-K 的 Item 1 列出 Andrew S. Fastow 為 EVP & CFO |
| 用自家股票替對手出資 | "Enron (i) contributed to newly-formed entities (the Entities) assets valued at approximately $1.2 billion, including $150 million in Enron notes payable, 3.7 million restricted shares of outstanding Enron common stock and the right to receive up to 18.0 million shares…" | 避險對手的資本就是 Enron 自己的股票 → 風險沒有真正移轉 |
| 靠這些「避險」認列收入 | "Enron recognized revenues of approximately $500 million related to the subsequent change in the market value of these derivatives, which offset market value changes of certain merchant investments" | 用關係人交易抵銷投資虧損，美化損益 |
| 資金繞一圈回到 Enron | "Cash in these Entities of $172.6 million is invested in Enron demand notes." / "$259 million is recorded at Enron's carryover basis of zero" | 循環交易特徵 |
| 出售資產給關係實體 | "gains from sales representing securitizations were $381 million and proceeds were $2,379 million ($545 million of the proceeds related to sales to Whitewing Associates, L.P.)" | 證券化利得部分來自關係實體 |
| 表外擔保無帳面價值 | "Guarantees of liabilities of unconsolidated entities and residual value guarantees have no carrying value and fair values which are not readily determinable" | 隱藏負債 |

**扣分理由**：關係人自我交易 + 自家股票支撐的避險 + 約 5 億美元由此產生的收入，是典型的財報操縱結構。
**保留**：10-K 本身沒有重編、會計師意見、調查等「硬」警訊，所以不給 90+。

## 2. WorldCom — FY2001 10-K（2002 年 3 月申報）— **65 / Elevated**

規則式 38.3。真正的舞弊（把約 38 億美元 line costs 資本化）**在 10-K 中看不到**，報表上 line cost 比率仍被報導為 41.9%。

| 證據 | 原文 | 為何是問題 |
|---|---|---|
| 借錢給 CEO | "we have also agreed to loan up to $165 million in principal amount to Mr. Ebbers… the aggregate principal amount of indebtedness owed by Mr. Ebbers to us under these loans was approximately $144.3 million." (Item 7) | 嚴重治理警訊 |
| 代 CEO 償還銀行債 | "WorldCom made aggregate payments of approximately $198.7 million to Bank of America pursuant to the guaranty… deposited… approximately $35 million to collateralize a letter of credit" (Item 7) | 公司資金承擔 CEO 個人股票質押風險 |
| 大額投資沖銷 | "pre-tax costs of $865 million… related to the write-off of investments in certain publicly traded and privately held companies" (Item 7) | 產業泡沫破裂中 |
| 證券詐欺訴訟 | "the consolidated amended complaint asserts claims for violation of Section 10(b)… and Rule 10b-5" (Item 14) | 已有投資人指控誤導 |

**扣分理由**：CEO 借款規模（合計約 3.8 億美元曝險）＋產業崩跌＋證券訴訟。
**保留**：未見重編、內控缺失或會計師更換；費用資本化無法從文字直接看出。

## 3. HealthSouth — FY2001 10-K（2002 年申報）— **60 / Elevated**

| 證據 | 原文 | 為何是問題 |
|---|---|---|
| DOJ Medicare 和解 | "On May 22, 2001, we announced a settlement with the United States Department of Justice in connection with a lawsuit… alleged that we had improperly included various costs on Medicare cost reports" (Item 3) | 已有不當申報紀錄 |
| DOJ 介入吹哨者訴訟 | "In late December 2001, the United States Department of Justice filed a Notice of Election to Intervene in Part…" (Item 3) | 調查仍在擴大 |
| 證券集體訴訟 | "plaintiffs… alleging that, during the period April 24, 1997 through September 30, 1998, the defendants misrepresented or failed to disclose…" (Item 3) | 過去已被指控財報誤導 |
| 內部人關聯供應商 | "Various persons affiliated or associated with the Company, including various of the Company's Directors and executive officers, also purchased shares… During 2001, the Company paid $100,044,296 for the purchase of goods, supplies and related services. In addition, the Company provided a guaranty of $15,000,000…" (Item 8, 附註 15) | 董事 / 主管持股的公司每年拿到 1 億美元採購 |
| 高度估計的營收 | "Revenues from third-party payors also include estimated retroactive adjustments…" (Item 7) | 契約調整估計正是後來灌水手法所在 |

**扣分理由**：反覆的政府與投資人指控 + 關係人交易。**保留**：無重編 / 內控缺失。

## 3. Lehman Brothers — FY2007 10-K（2008 年 1 月申報）— **60 / Elevated**

| 證據 | 原文 | 為何是問題 |
|---|---|---|
| 大量資產移入 Level III | "reclassification of approximately $11.4 billion of mortgage and asset-backed securities, including approximately $5.3 billion in U.S. subprime residential mortgage-related assets… into the Level III category" (Item 7) | 估值改以模型為主，管理層裁量大增 |
| Level III 虧損 | "The net unrealized loss on Level III non-derivative financial instruments was approximately $2.5 billion" (Item 8) | 次貸部位已在虧損 |
| 自訂槓桿指標 | "We believe that a more meaningful, comparative ratio… is net leverage… We calculate net assets by excluding from total assets… collateralized lending agreements" (Item 7) | 以非 GAAP 指標淡化槓桿 |
| 評等敏感 | "the liquidity pool is sized to cover the impact of a one notch downgrade" (Item 7) | 流動性高度依賴信評 |

**扣分理由**：估值不透明＋次貸曝險＋槓桿依賴。
**保留**：這比較像「償債 / 估值風險」而非舞弊；Repo 105（真正的粉飾手法）**在 10-K 中完全未揭露**，文字分析抓不到。

## 3. Valeant — FY2014 10-K（2015 年 2 月申報）— **60 / Elevated**

規則式 66.7 偏高：其中 going-concern 16.7 分是**誤判**（命中的是 FASB 新準則說明文字）。

| 證據 | 原文 | 為何是問題 |
|---|---|---|
| 成長靠漲價 | "deeper discounts due to the price increases we implemented in each of the last three years" (Item 7) | 營收品質依賴定價而非銷量 |
| 營收依賴通路庫存估計 | "Our distribution agreements with the three largest wholesalers… contain target inventory levels between ½ and 1½ months supply… inventory data… may itself rely on certain estimates" (Item 7) | 通路塞貨風險 |
| 併購 + 高負債 | "Long-term debt… $15.3 billion as of December 31, 2014" (Item 7)；"Our current indebtedness contains certain restrictive covenants…" (Item 1A) | 槓桿併購模式 |
| 合併未具名 VIE | "the Company completed other smaller acquisitions, including the consolidation of variable interest entities, which are not material" (Item 15) | 未說明是哪些實體（後來證實包含 Philidor，但 10-K 本身未點名） |
| 多項政府調查 | FTC civil investigative demand；HHS OIG subpoenas (Item 15) | 監管風險 |

## 6. Kraft Heinz — FY2017 10-K（2018 年 2 月申報）— **55 / Elevated**

| 證據 | 原文 | 為何是問題 |
|---|---|---|
| 已重編季報 | "In November 2017, we restated our consolidated financial statements for the quarters ended April 1, 2017 and July 1, 2017 in order to correctly classify cash receipts from the payments on sold receivables… to cash provided by investing activities (from cash provided by operating activities)" (Item 1A) | 營業現金流被高估 |
| 內控重大缺失 | "In connection with these restatements, management identified a material weakness in our internal control…"；"While we have remediated the previously-identified material weakness…" | 財報流程曾失靈 |
| 高度依賴成本削減 | "Integration Program… cumulative pre-tax costs of approximately $2.1 billion" (Item 7) | 節省目標壓力（後來問題正出在採購折讓） |
| 商譽緩衝薄 | "Each of our goodwill reporting units had excess fair value over its carrying value of at least 10%" (Item 7) | 減損風險（事後：2019 年 2 月宣布約 154 億美元商譽與無形資產減損） |

**保留**：重編性質屬分類錯誤、金額不影響淨利，且已補正。

## 7. Johnson & Johnson — FY2019 — **35 / Moderate**

法律 / 產品責任風險高，但**財報可信度沒有警訊**（Item 9A 結論為有效）。
- "In February 2018, a securities class action lawsuit was filed… alleging that Johnson & Johnson violated the federal securities laws by failing to adequately disclose the alleged asbestos contamination in body powders containing talc" (Item 8)
- "the Company has received preliminary inquiries and subpoenas… from… the Department of Justice, the Securities and Exchange Commission…" (Item 8)
- 鴉片類訴訟："an agreement in principle that would include the Company paying $4 billion" (Item 8)；"In August 2019, Johnson & Johnson received a grand jury subpoena" (Item 8)

## 8. Costco — FY2019 — **30 / Moderate**

- "We previously identified a material weakness in our internal control related to ineffective information technology general controls" (Item 1A) — FY2018 揭露、FY2019 已補正。
- "The Company and its CEO and CFO are defendants in putative class actions brought on behalf of shareholders who acquired Company stock between June 6 and October 25, 2018." (Item 8) — 與上述內控缺失相關。
- 鴉片類 MDL 被告（藥局業務）。
其他會計指標乾淨；規則式 48.3 偏高，因為過去的內控缺失被重複提及多次。

## 9. Microsoft — FY2019 — **15 / Low**

- "our Hungarian subsidiary entered into a non-prosecution agreement… with the U.S. Department of Justice… and we agreed to the terms of a cease and desist order with the Securities and Exchange Commission. These agreements required us to pay $25.3 million" (Item 1A)
- Item 9A：揭露控制與程序 "are effective"。其餘規則命中皆為樣板文字（減損政策說明、「無表外安排」）。

## 10. Apple — FY2019 — **10 / Low**

- "the entire adjusted recovery amount of €12.9 billion plus interest of €1.2 billion was funded into escrow… pending the conclusion of all appeals" (Item 7) — 稅務爭議，非財報可信度問題。
- Item 9A 有效；"did not restate total net sales" 為新準則採用說明。

---

## 實驗結果

| 指標 | 規則式（關鍵字） | 分析師覆核 |
|---|---|---|
| 問題組平均 | 45.6 | 63.3 |
| 對照組平均 | 28.8 | 22.5 |
| 問題組高於「所有」對照組的家數 | 2 / 6 | 6 / 6 |
| 最大失誤 | Enron 只拿 28.4（低於 Costco 48.3） | — |

### 發現
1. **關鍵字法不夠**：最強的 Enron 證據是一段「看起來很正常」的關係人附註，沒有任何紅旗關鍵字；反之，Costco 已補正的內控缺失被重複提到就拿高分。
2. **舞弊本身通常不在 10-K 裡**：WorldCom 的費用資本化、Lehman 的 Repo 105、Kraft Heinz 的採購折讓都沒有出現在文字中；能看到的是**周邊徵兆**（治理、關係人、估值裁量、曾經重編）。
3. **要分開「法律風險」與「財報可信度」**：J&J 的法律曝險其實比 HealthSouth 大，但沒有會計警訊，因此分數較低。
4. 規則式仍有可見的誤判（FASB 準則說明被當成 going concern、「本公司無表外安排」被當成表外安排）。我刻意停止針對這 10 家調規則，以免過度擬合測試集。

### 建議下一步
- **盲測**：遮蔽公司名稱與年份，加入更多隨機非舞弊公司，讓 LLM（或不知情的分析師）評分，才能排除事後偏誤。
- 把附註中的**關係人交易、CEO 借款、Level III 變動**做成結構化特徵，取代單純關鍵字。
- 擴大樣本（例如 SEC AAER 執法名單 vs. 同產業配對公司），計算 AUC。
