# 在另一個環境跑 Opus 5.5：名單 A–F（30 次請求）

整個資料夾 `mem_isolated_opus_periods/` 可以單獨帶走，不需要 repo。

## 方式一：有 Claude Code 的機器（建議）
需要：已登入的 Claude Code（`claude --version` 有版本號）、python3。

```bash
python3 run_all.py canary
```
要看到第一行 `tools=[] mcp=[] tool_calls=[] searches=0`，回答是不知道；第二行列出 `WebSearch`。第一行不對就停。

```bash
python3 run_all.py run
```
30 次，每次約半分鐘到一分鐘。中斷後重跑同一行會跳過已完成的。每行結尾應該是 `complete=True ... tool_calls=0 searches=0 ok=True`。

跑完把 `raw/` 整個資料夾帶回來（32 個 `.jsonl`）。

## 方式二：claude.ai 網頁
沒有原始紀錄，無法做 7 項無上網檢查，結果只能列為「未經檢查」。

每一份 `prompts/*.txt`：
1. 開新對話，模型選 Opus 5.5，關掉網路搜尋與所有工具／連接器，不要放在有記憶或專案知識的專案裡
2. 把檔案全文貼上送出，不要加任何字
3. 把回答的 JSON 存成 `replies/<同名>.json`（例如 `replies/A_run1.json`）

30 份都做完後把 `replies/` 帶回來。

## 不要做的事
- 不要改提示檔；`prompts/manifest.tsv` 有每份的 sha256
- 不要看了回答之後挑著重跑；不完整的回答腳本會自己重送一次，兩份都留著
