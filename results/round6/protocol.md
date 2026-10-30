# 第六輪預先登錄：LLM 判斷報表矛盾（方法 L）

本文件在任何 API 結果產生之前提交。之後若有修改，會另外標明，並說明原因。

## 1. 目的
- 第五輪的一致性檢查 C 只做算術勾稽，AUC 0.53
- 本輪讓 LLM 閱讀財報全文，找出**算術以外的矛盾**：附註與報表不一致、MD&A 與數字不一致、前一年數字被修改、說法前後不一等

## 2. 假設與判定標準

| 編號 | 假設 | 判定標準 |
|---|---|---|
| H4 | L 有鑑別力 | L 的 AUC（72 份）95% CI 下限 > 0.5 |
| H5 | L 能在規則 v2 之上加分 | AUC(R+L) − AUC(R)，配對 bootstrap 95% CI 下限 > 0 |
| H6（描述性） | L 不只是「認得公司」 | 在模型**沒有認出公司**的子樣本中，L 的 AUC 方向 > 0.5（樣本小，只描述，不檢定） |

## 3. 樣本與輸入
- 與第四、五輪相同的 72 份 10-K（36 組配對）
- 資料包由 `python -m experiment.edgar_risk.round6_llm build` 產生，存在 `data/round6/packets/Qxx.txt.gz`，`manifest.json` 記錄每份的 SHA-256
- **DOCUMENT A**：當年 10-K
  - 保留 Item 5–9A 和 Item 15（MD&A、財務報表、附註），以及 EX-13（年報）
  - 刪除 Item 1–4（業務、風險、法律訴訟）和 Item 10–14（公司治理），以減少辨識線索和與財報無關的紅旗
  - 若刪除後找不到 total assets / operating activities / net income / notes to，就改用全文
- **DOCUMENT B**：前一年 10-K，處理方式相同，另外再刪掉 MD&A。MicroStrategy 沒有前一年的 10-K
- 遮蔽：沿用第三、四輪的 `redact.py`
  - 公司名稱和別名改為 [COMPANY]，專有名詞改為 [NAME]，網址改為 [URL]
  - 年份改成相對年份（Y0 是最新的會計年度期末年）
- 數字不遮蔽。檢查矛盾需要數字，但數字本身仍可能讓模型認出公司

## 4. 模型與請求
- 預設模型 `claude-opus-5-5`，使用 Message Batches API。可以用 `--model` 更換，實際使用的模型記錄在 `results/round6/batches.json`
- 也可以改用 OpenAI：加上 `--provider openai --model <模型 ID>`，走 OpenAI Batch API（Chat Completions，JSON schema strict 模式），提示詞完全相同。不同模型視為不同的方法，結果分開報告，不能和 Claude 的結果混在一起平均
- 每份資料包發出三個請求：
  - `review` × 2：兩次獨立判斷矛盾，effort high，輸出用 JSON schema 限制
  - `identify` × 1：另外一個請求，只問「這是哪家公司」，effort low。用途是量化辨識污染；這個問題不會出現在 review 請求裡，以免引導模型去回想公司
- 提示詞全文寫在 `round6_llm.py` 的 `REVIEW_TASK` 和 `IDENTIFY_TASK`，提交後不再修改
- 模型不會收到組別標籤。`results/round4/key.json` 只有 `evaluate` 這一步會讀

## 5. 矛盾類別（模型逐項回報）

| 代碼 | 內容 |
|---|---|
| A1 | 單一報表本身加不起來（合計、小計、EPS 與淨利 / 股數） |
| A2 | 報表之間不一致（淨利、期末現金、保留盈餘、營運資金變動） |
| A3 | 附註或明細表與主表不一致（部門、負債、稅、備抵、存貨、固定資產、權益、季資料） |
| A4 | DOCUMENT A 中的 Y-1 數字，與 DOCUMENT B 原本報的不同 |
| A5 | MD&A 文字與數字矛盾（方向、大小、或給出的原因） |
| A6 | 兩段文字的事實、政策或估計互相矛盾 |
| A7 | 給出的解釋不足以說明變動的幅度 |

- 每項矛盾都必須附上：
  - 兩段逐字引文和出處（A 或 B）
  - 兩邊的金額
  - 報表本身是否已經解釋了差異（explained），以及解釋的引文
  - 嚴重度：low、medium、high

## 6. 計分（不經人工修改）
1. **引文驗證**：兩段引文都要在資料包中找得到，才算通過驗證
   - 比對前先轉小寫，並去掉空白、$ 和逗號
   - 若引文有 40 個字以上，開頭或結尾 40 個字吻合也算找到
2. **L（主要指標）**：Σ 嚴重度權重（low 1、medium 2、high 3），只計入「通過驗證且 explained = false」的矛盾，再取兩次 review 的平均
3. 次要指標：
   - L_unverified：不做引文驗證
   - rating：模型給的整體分數 0–100，取兩次平均
4. **辨識**：identify 的猜測若包含公司名稱或任一別名，就算認出
5. 人工**不**修改 L。有錯誤的話只描述，不重新計分

## 7. 評估
- AUC 與 bootstrap 95% CI，計算範圍：
  - 全部；
  - 沒認出的子樣本；
  - 有認出的子樣本；
  - 排除事後揭露的 3 組
- 配對 bootstrap：
  - (R+L) − R，用來判定 H5；
  - L − C，比較第五輪的一致性檢查
- 兩次 review 的一致性：
  - L 的 Spearman 等級相關；
  - 兩次是否都判定 L > 0 的一致率
- 組內勝率、L > 0 的命中率
- 描述性：L 有沒有找到第五輪 C 的 8 項無法解釋的矛盾

## 8. 已知限制
- 模型可能認得公司，也知道後來的結果。identify 只能量化這個問題，無法排除
- 我（設計者）知道標籤；提示詞和類別是在看過第五輪結果之後才寫的
- 引文驗證只能確認引文存在，不能確認矛盾真的成立
- 部分資料包超過 30 萬 token（CMS、Popular、Doral、AIG），長文件的閱讀品質可能較差

## 9. 執行方式（在本機用自己的 API key）

```bash
git pull
pip install -U anthropic
export ANTHROPIC_API_KEY=...        # 或先執行 ant auth login

# 0. 估算：計算每份資料包的 token 數（免費）
python -m experiment.edgar_risk.round6_llm count

# 1. 先導：先送 4 份，確認輸出正常
python -m experiment.edgar_risk.round6_llm submit --limit 4
python -m experiment.edgar_risk.round6_llm status     # 等到 ended（通常 1 小時內）
python -m experiment.edgar_risk.round6_llm collect
python -m experiment.edgar_risk.round6_llm score

# 2. 正式：送其餘資料包（Q05 以後）
python -m experiment.edgar_risk.round6_llm submit --only $(python -c "print(' '.join(f'Q{i:02d}' for i in range(5,73)))")
python -m experiment.edgar_risk.round6_llm status
python -m experiment.edgar_risk.round6_llm collect
python -m experiment.edgar_risk.round6_llm retry      # 失敗或被截斷的請求逐一重跑
python -m experiment.edgar_risk.round6_llm score

# 3. 提交結果（評估前）
git add results/round6 && git commit -m "Round 6: LLM review outputs" && git push
python -m experiment.edgar_risk.round6_llm evaluate
```

- 改用 OpenAI 時，每個指令都加上 `--provider openai`，`submit` 另外要加 `--model <模型 ID>`；金鑰放在 `OPENAI_API_KEY`
  - `count` 只用字元數估算 token（約 3.5 個字元 = 1 token），送出前請確認模型的 context window 放得下最大的資料包（約 35 萬 token）
- 不要把 API key 寫進任何檔案或提交到 git
- 費用估算（Opus 5.5、Batch 半價、兩次 review 加一次 identify）：
  - 輸入約 9M token × 3 個請求，約 50 美元
  - 輸出約 15–20 美元
  - 合計約 60–80 美元
  - 先導 4 份約 3–5 美元
- `count` 會回報實際的輸入 token 數，送出前可以先確認
