# 第七、八輪評分 agent 上網稽核（2026-11-04）

## 結果
| 對象 | 查到了嗎 | 上網嘗試 | 備註 |
|---|---|---|---|
| 第七輪方法 B：28 個評分 agent | 28/28 全部查到 | **0/28** | 286 次工具呼叫全是 `Read`，每個 agent 只讀自己那一份 `filing_N.txt`；28 個都有交回結果 |
| 第八輪 MEM 原始執行（1 個 agent，AUC 0.88） | **沒查到** | 未知 | 翻頁子代理在第一頁就被 Anthropic 安全機制終止，沒有存到任何事件 |
| 第八輪 MEM 重跑 1、2（AUC 0.88、0.88） | **查不到** | 未知 | 在一般 claude.ai 對話中執行，Claude Code 讀不到；輸出 JSON 沒有網址或來源字樣（不構成證據） |

第七輪的評分 agent 是 `general-purpose` 類型，**有 WebSearch 等全部工具可用**；不上網只靠提示詞中的
「Use only the Read tool on that one file; do not search the web, do not open any other files or directories, and do not run commands」。
28/28 遵守，與 `summary.md` 的 B 條件（提示禁止 0/9）一致。

## 去哪裡查、怎麼查
- 從 commit 的 `Claude-Session` 欄位找到執行的雲端 session：第七輪 `session_01XZo4WsMLeVgABnCKpHnKS3`，第八輪 `session_01UcZFK3DTj4hpCineb9sxBi`。
- 用 `list_events`（claude-code-remote）取出 session 的伺服器端事件紀錄（assistant + user），從最新往回翻到 2026-11-02 10:58 UTC，共 17 頁、1,059 個事件。
  子代理的工具呼叫也在紀錄中，帶有 `parent_tool_use_id`，可以對回是哪個評分 agent。
- 評分時段 11:28–12:44 UTC：380 次工具呼叫，交給 `experiment/websearch_check.py` 的同一個 `classify()` 判定。

## 檢查了哪些上網方式
WebSearch / WebFetch（含用 ToolSearch 載入）、Bash/Monitor 指令與寫入檔案中的 curl / wget / 網址 / requests / gh / git clone / pip install / ssh 等、
派子代理或 Workflow 或其他 session、research / 瀏覽器 / computer-use skill、外部 MCP 工具。評分 agent 這些全部是 0。

## 沒涵蓋到的
- 第八輪全部（包含 MEM）與 MEM 兩次 claude.ai 重跑，見上表。
- 主 session（協調者）本身有上網（用 Bash 下載 SEC 申報檔），這是預期的；評分 agent 拿到的只有協調者準備好的 10-K 文字檔，
  本稽核沒有逐字檢查那些檔案是否混入事後資訊。
- 依賴伺服器紀錄完整：28 個交回結果都在、讀檔次數合理，但無法獨立證明沒有遺漏事件。
- 記憶不是上網：第八輪已顯示 0.88 主要來自模型記得哪些公司出事，這不是任何上網偵測能排除的。
