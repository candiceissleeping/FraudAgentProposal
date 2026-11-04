# 第七、八輪評分 agent 上網稽核（2026-11-04）

## 結果
| 對象 | 查到了嗎 | 上網嘗試 | 備註 |
|---|---|---|---|
| 第七輪方法 B：28 個評分 agent | 28/28 全部查到 | **0/28** | 286 次工具呼叫全是 `Read`，每個 agent 只讀自己那一份 `filing_N.txt`；28 個都有交回結果 |
| 第八輪 MEM 原始執行（1 個 agent，AUC 0.88） | **查到了** | **0** | 15:09:21 UTC 啟動，共 4 次工具呼叫：`Read` memory_prompt.md、`Read` cards/memory_only.txt、`Write` probe/memory.json（5,445 bytes）、交回。repo 中 commit `cbc00ea` 的 memory.json 正好 5,445 bytes，是這個 agent 寫的版本，之後沒有被改過 |
| 第八輪其他評分 / 探針 agent | 166 個啟動全部查到 | **0/166** | 見下方「第八輪明細」。有 8 次啟動因同時執行的子代理數量超過上限而被拒絕（0 次工具呼叫），之後重新啟動 |
| 第八輪 MEM 重跑 1、2（AUC 0.88、0.88） | **查不到** | 未知 | 在一般 claude.ai 對話中執行，Claude Code 讀不到；輸出 JSON 沒有網址或來源字樣（不構成證據） |

第七輪的評分 agent 是 `general-purpose` 類型，**有 WebSearch 等全部工具可用**；不上網只靠提示詞中的
「Use only the Read tool on that one file; do not search the web, do not open any other files or directories, and do not run commands」。
28/28 遵守，與 `summary.md` 的 B 條件（提示禁止 0/9）一致。

## 第八輪明細（session `session_01UcZFK3DTj4hpCineb9sxBi`，2026-11-02 14:20–15:30 UTC）
167 次 `Agent` 呼叫全部是 `general-purpose` 類型（**有 WebSearch / WebFetch 可用**）。提示詞沒有明文禁止上網，
只寫了「Read ONLY the file you were given; do not open any other file or directory」，MEM 的提示詞另外寫了「using only what you already know」。

| 組別 | 啟動時間 (UTC) | 啟動數 | 工具呼叫 | 上網嘗試 | 讀了哪些檔案 |
|---|---|---|---|---|---|
| MEM（只給公司名稱和會計年度） | 15:09 | 1 | Read 2、Write 1 | 0 | `data/round8/memory_prompt.md`、`data/round8/cards/memory_only.txt` |
| 事實擷取 Extract R8-01…28 | 15:07–15:09 | 36（28 個有效 + 8 個因超過同時執行上限被拒絕，之後重新啟動） | Read 88、Grep 27、Bash 298、Write 4、Edit 1 | 0 | `extract_prompt.md`、自己那份 `redacted/R8-NN.txt`、自己的輸出 `extract/R8-NN.json`；另外 2 個 agent 讀了自己 Bash 指令的輸出暫存檔 |
| J0/J1/J2 評分 | 15:11–15:14 | 84 | Read 168、Write 84、Edit 2 | 0 | `judge_prompt.md`＋自己那張 `cards/R8-NN_Jk.txt` |
| PX 評分 | 15:14–15:15 | 14 | Read 28、Write 14 | 0 | `judge_prompt.md`＋自己那張 `cards/R8-NN_PX.txt` |
| C0 評分（8b 粗化卡） | 15:16–15:17 | 28 | Read 56、Write 28 | 0 | `judge_prompt.md`＋自己那張 `cards/R8-NN_C0.txt` |
| 重新辨識探針（開放 ×2、封閉、8b 封閉） | 15:10–15:15 | 4 | Read 9、Write 2、Bash 2 | 0 | 各自的 `probe_*_prompt.md`＋`cards/probe_*.txt`；Bash 只寫自己的輸出 `probe/*.json` |

- 合計：子代理 973 次工具呼叫（Read 351、Bash 300、Write 133、Grep 27、Edit 3、交回 159），**上網嘗試 0**，也沒有子代理再派子代理。
- **有沒有讀自己輸入以外的檔案**：逐一比對每個 agent 的 Read/Grep/Glob 路徑和 Bash 指令中的路徑，**沒有任何 agent 碰到 `config/`、`results/`、標籤或 AAER 檔案**，
  也沒有 agent 碰到別家公司的編號（每個 agent 碰到的 `R8-NN` 都和它提示詞中的編號一致）。
  唯一的「額外」路徑是 2 個擷取 agent 讀了自己 Bash 指令的輸出暫存檔（`tool-results/*.txt`），內容就是它自己那份年報。
- 每個 agent 的明細在 `round8_agents.csv`（只從 tool_use 產生，不含提示詞全文或思考內容）。
- 同一時段主 session（協調者）有 15 次網路相關指令（下載 SEC 申報檔、git clone 技能 repo、git push 等），這是預期的，不屬於評分 agent。

## 去哪裡查、怎麼查
- 從 commit 的 `Claude-Session` 欄位找到執行的雲端 session：第七輪 `session_01XZo4WsMLeVgABnCKpHnKS3`，第八輪 `session_01UcZFK3DTj4hpCineb9sxBi`。
- 用 `list_events`（claude-code-remote）取出 session 的伺服器端事件紀錄（assistant + user），從最新往回翻到 2026-11-02 10:58 UTC，共 17 頁、1,059 個事件。
  子代理的工具呼叫也在紀錄中，帶有 `parent_tool_use_id`，可以對回是哪個評分 agent。
- 評分時段 11:28–12:44 UTC：380 次工具呼叫，交給 `experiment/websearch_check.py` 的同一個 `classify()` 判定。
- 第八輪（2026-11-04 補查）：同樣用 `list_events`（limit=100、kinds=assistant+user），從最新一頁（11/3 15:37）往回翻到 session 開頭
  （11/2 14:22:29，`has_more` 為 false），共 239 頁、17,573 個事件。每頁存成檔案後只用 `experiment/session_audit/accumulate.py` 累積，
  再用 `analyze.py r8 2026-11-02T14:20 2026-11-02T15:30` 和一個只看 tool_use 的逐 agent 比對腳本分析。翻頁在主對話中進行，沒有派子代理，
  也沒有直接讀原始頁面；分析只用 tool_use / tool_result 欄位，不讀思考內容。這次沒有被安全機制擋下。
  - 最新那一頁（11/3 13:00–15:37）直接顯示在對話中、沒有存成檔案，因為它在第八輪時段之外，只取了 cursor，沒有寫進資料庫。

## 檢查了哪些上網方式
WebSearch / WebFetch（含用 ToolSearch 載入）、Bash/Monitor 指令與寫入檔案中的 curl / wget / 網址 / requests / gh / git clone / pip install / ssh 等、
派子代理或 Workflow 或其他 session、research / 瀏覽器 / computer-use skill、外部 MCP 工具。評分 agent 這些全部是 0。

## 沒涵蓋到的
- MEM 兩次 claude.ai 重跑（不在 Claude Code session 裡），見上表。
- 偵測器只看得到紀錄裡的工具呼叫。看不到的管道：模型本身的記憶（這正是 MEM 測的東西）、伺服器端在工具呼叫之外加入的內容。
  Bash 指令只用關鍵字比對（curl / wget / 網址 / requests / gh / git clone / pip / ssh 等），如果指令把網址拆開或藏在別的腳本檔裡，可能偵測不到；
  但第八輪子代理的 300 次 Bash 都是對自己年報的 `grep`/`sed`/`cut`/`head`/`cat`/`wc`/`python3`/`mkdir` 處理，碰到的路徑都在 `data/round8/` 底下。
- 附帶觀察（不在本次範圍）：同一個 session 在 15:30 之後到 11/3 13:00 還有第九輪等 604 次子代理啟動；其中評分 / 擷取 / 探針類 602 個都是 0 次上網，
  只有 2 個文獻搜尋 agent（「Survey LLM fraud detection papers」「Read FraudDebate-Agent paper details」）有上網，這是它們的任務本身。
- 主 session（協調者）本身有上網（用 Bash 下載 SEC 申報檔），這是預期的；評分 agent 拿到的只有協調者準備好的 10-K 文字檔，
  本稽核沒有逐字檢查那些檔案是否混入事後資訊。
- 依賴伺服器紀錄完整：28 個交回結果都在、讀檔次數合理，但無法獨立證明沒有遺漏事件。
- 記憶不是上網：第八輪已顯示 0.88 主要來自模型記得哪些公司出事，這不是任何上網偵測能排除的。
