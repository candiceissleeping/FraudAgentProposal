# Fraud Agent Proposal — EDGAR-CORPUS 10-K 風險實驗

## 實驗目標
從 [EDGAR-CORPUS](https://huggingface.co/datasets/eloukas/edgar-corpus) 選 10 家公司，閱讀各自的 10-K，
找出公司「有問題」的證據（也可能沒有問題），最後給每家公司一個 **0–100 風險分數**，並附上判分原因（引用 10-K 原文）。

## 實驗設計
| 組別 | 公司（10-K 申報年度） | 用途 |
|---|---|---|
| Treatment（事後證實有問題） | Enron (FY2000), WorldCom (FY2001), HealthSouth (FY2001), Lehman Brothers (FY2007), Valeant (FY2014), Kraft Heinz (FY2017) | 檢驗方法能否在問題公開**之前**的 10-K 找到警訊 |
| Control（無已知會計舞弊） | Microsoft, Costco, Johnson & Johnson, Apple（皆 FY2019） | 檢驗誤報率 |

公司清單在 `config/companies.json`。每家選的是問題爆發**前**最後一份 10-K，避免直接讀到事後揭露。
注意：EDGAR-CORPUS 的 `year` 是**會計年度**（例如 WorldCom 2002 是 2004 年才申報、已含重編的 FY2002 10-K）。
GE 原本在名單中，但其 FY2016 10-K 在資料集中為空（年報以引用方式併入），改用 Kraft Heinz。

**結果：**
- 第一輪：[`results/analyst_review.md`](results/analyst_review.md)（最終分數與理由）、`results/rule_based_report.md`（關鍵字初評）
- 第二輪（遮蔽名稱 + 預先登錄規則，5 組同產業配對）：[`results/blind_review.md`](results/blind_review.md)
  - 流程：`blind_rubric.md` → `python -m experiment.edgar_risk.blind` → `blind_scores.md` → `--unblind`
- 第三輪（候選名單隨機抽樣 + 強化遮蔽 + 揭盲前提交三種分數）：[`results/round3/review.md`](results/round3/review.md)
  - 流程：`config/round3_pool.json` + `results/round3/rubric_v2.md` → `python -m experiment.edgar_risk.round3 draw` → `scores.csv` → `round3 unblind`
- 第四輪（36 組配對、每產業 ≥3 組、遮蔽加上網址 / 電子郵件）：[`results/round4/review.md`](results/round4/review.md)
  - 關鍵字 AUC 0.56、規則 v2 0.66、整體判斷 0.78（受辨識污染，62/72 被認出）
  - 流程：`config/round4_pool.json` + `results/round4/protocol.md` → `round3 draw --round 4` → `scores.csv` → `round3 unblind --round 4` → `round4_sensitivity`
- 全部 102 份總表：`results/summary_table.csv`

## 流程
1. **抓資料** `python -m experiment.edgar_risk.fetch`
   逐年串流 Hugging Face 上的原始 jsonl（每年約 1.2 GB），只保留目標公司的列，不存整個檔案。
   離線模式：`--local-jsonl <檔案>`。
2. **規則式評分** `python -m experiment.edgar_risk.score`
   在 Item 1A / 3 / 7 / 8 / 9 / 9A 中逐句比對紅旗，排除否定句（如 "no material weakness"）。
   產出 `results/<cik>_<year>.json`（完整證據）與 `results/rule_based_report.md`。
3. **分析師覆核**：人工（或 LLM）閱讀步驟 2 的證據與原文，調整分數並寫下理由，輸出 `results/analyst_review.md`。

## 評分規則（rule-based）
| 類別 | 上限分數 |
|---|---|
| Going-concern 疑慮 | 25 |
| 財報重編 Restatement | 20 |
| 內控重大缺失 Material weakness | 20 |
| 監管 / 刑事調查（SEC、DOJ、subpoena） | 15 |
| 證券集體訴訟 | 10 |
| 更換會計師 / 意見不合 | 10 |
| 表外 / 關係人結構（SPE、VIE、Repo） | 10 |
| 激進會計（bill-and-hold、mark-to-model、費用資本化） | 10 |
| 流動性 / 債務契約壓力 | 10 |
| 大額減損 | 5 |

每類分數 = 上限 × min(命中句數, 3) / 3；總分上限 100。
等級：0–24 Low、25–49 Moderate、50–74 Elevated、75–100 High。

## 限制
- **事後偏誤**：Treatment 公司是因為事後出事才被選中；分析師覆核階段必須只引用 10-K 原文，不可引用事後知識。
- 舞弊常常**不會**寫在 10-K 裡（Enron、WorldCom 的 10-K 表面看起來可能很乾淨），規則式分數低不代表公司安全。
- 2003 年前的 10-K 沒有 Item 9A（SOX 404 之前），內控類訊號天生較少。
- 關鍵字比對無法理解語意；判斷交由第 3 步覆核。

## 測試
`python -m unittest discover -s tests -t .`
