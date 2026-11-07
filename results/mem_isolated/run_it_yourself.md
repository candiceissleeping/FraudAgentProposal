# 自己在 terminal 跑一次（先確認不能上網，再跑 run1）

## 需要
- 已安裝並登入 Claude Code（`claude --version` 有版本號）、git、python3
- macOS 或 Linux（Windows 請用 WSL）
- 這個 repo 的 `claude/peaceful-hawking-w6z0fz` 分支，只會用到 3 個檔案：
  - `data/mem_isolated/prompt.md`：提示詞
  - `results/mem_isolated/inputs/run1.txt`：run1 的 28 家名單（和雲端那次同一個順序）
  - `experiment/mem_isolated.py`：`watch` 即時顯示＋檢查（只用到 Python 內建模組）

## 0. 準備
```bash
git clone -b claude/peaceful-hawking-w6z0fz https://github.com/candiceissleeping/FraudAgentProposal.git ~/FraudAgentProposal
```
```bash
export REPO=~/FraudAgentProposal
```
```bash
mkdir -p ~/mem_jail ~/mem_out && cd ~/mem_jail
```
`~/mem_jail` 是空目錄，Claude 在這裡執行；紀錄存到另一個目錄 `~/mem_out`。

## 1. 先問一定答不出來的問題（訓練截止 2026-06 之後的事）
```bash
claude -p "2026 年 11 月 6 日台股加權指數（TAIEX）收盤是多少點？如果你無法確定，請直接說不知道，不要猜。" --model claude-opus-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format stream-json --verbose < /dev/null | tee ~/mem_out/canary.jsonl | python3 "$REPO/experiment/mem_isolated.py" watch
```
要看到：`可用工具=[]`、`MCP 伺服器=[]`、回答「不知道」、`各模型搜尋次數` 全是 0、最後「全部通過：無法上網」。
任何一項不對就停下來，不要跑 run1。

## 1b.（建議）正控制：開放搜尋，確認畫面抓得到
```bash
claude -p "2026 年 11 月 6 日台股加權指數（TAIEX）收盤是多少點？如果你無法確定，請直接說不知道，不要猜。" --model claude-opus-5-5 --tools WebSearch --allowedTools WebSearch --strict-mcp-config --setting-sources "" --no-session-persistence --output-format stream-json --verbose < /dev/null | tee ~/mem_out/canary_web.jsonl | python3 "$REPO/experiment/mem_isolated.py" watch
```
要看到：`[!! 工具呼叫] tool_use WebSearch`、答出點數、最後「有項目失敗」。這證明真的有搜尋時，畫面和檢查都看得到。

## 2. run1（和步驟 1 完全相同的參數，只換提示詞）
```bash
claude -p "$(cat "$REPO/data/mem_isolated/prompt.md" "$REPO/results/mem_isolated/inputs/run1.txt")" --model claude-opus-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format stream-json --verbose < /dev/null | tee ~/mem_out/my_run1.jsonl | python3 "$REPO/experiment/mem_isolated.py" watch
```
約 30 秒、約 0.09 美元。畫面依序出現：`[啟動]`（工具清單）→ `[思考中]` → `[回答]`（28 家 JSON）→ `[結束]`（伺服器端計數）→ `[檢查]`。

## 3. 之後
- `~/mem_out/my_run1.jsonl` 是完整原始紀錄；可以放進 repo 的 `results/mem_isolated/manual/` 再算分，和雲端 run1 比較。
- 模型每次回答有些隨機，分數會和雲端 run1 略有不同（雲端 5 次 AUC 在 0.86–0.89 之間）。

## 參數意思
| 參數 | 作用 |
|---|---|
| `--tools ""` | 移除所有內建工具（WebSearch、WebFetch、Bash、讀寫檔、子代理、Skill…） |
| `--strict-mcp-config` | 不載入任何 MCP 伺服器（沒給設定檔＝零個） |
| `--setting-sources ""` | 不讀你的 CLAUDE.md、記憶、hooks、權限設定 |
| `--no-session-persistence` | 不保存 session |
| `--output-format stream-json --verbose` | 每個事件一行 JSON，`tee` 存檔、`watch` 即時顯示 |
| `< /dev/null` | 不等鍵盤輸入 |
