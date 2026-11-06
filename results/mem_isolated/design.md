# 第八輪 MEM 純記憶實驗：無法上網的實驗環境設計（2026-11-06）

## 0. 要證明什麼、要排除什麼
第八輪 MEM（只給公司名稱與會計年度）AUC 0.88（原始）／0.88／0.88（兩次 claude.ai 重跑）。
要主張「這個分數只來自模型記憶」，必須排除四種資訊來源：

| 來源 | 原始 MEM（Claude Code 子代理） | claude.ai 重跑 1、2 | 本設計 |
|---|---|---|---|
| 上網（搜尋、抓網頁、指令） | 事後稽核 0 次，但 WebSearch **有提供**，只靠提示詞 | 查不到紀錄，只靠提示詞 | **工具全部移除**，機器驗證 |
| 讀到本機的標籤／結果檔（`config/`、`results/`） | 稽核未讀，但有 Read 工具、repo 裡就有答案 | 無檔案 | 無檔案工具，且在空目錄執行 |
| 過去對話／記憶功能帶入先前結果 | 無 | **可能**（claude.ai 記憶、搜尋過去對話、Project 知識） | 不讀任何設定、不保存 session |
| 輸入格式洩漏 | 有（已由重跑排除） | 已統一格式、打亂 | 統一格式，每次不同種子打亂 |

## 1. Claude App 與 terminal CLI 哪個適合
| | claude.ai App | Claude Code CLI（`claude -p`） | 直接呼叫 Messages API |
|---|---|---|---|
| 怎麼關掉上網 | 在介面關掉 Web search、Research、連接器、程式執行；靠人操作，無法事後證明當時是關的 | `--tools ""` 移除所有內建工具；`--strict-mcp-config` 不載入 MCP；啟動事件列出實際可用工具 | 請求裡不放 `tools`／`mcp_servers`，模型就沒有任何工具 |
| 其他污染 | 記憶、搜尋過去對話、Project 檔案、個人偏好可能帶入先前的第八輪結果 | `--setting-sources ""` 不讀 CLAUDE.md／hooks／記憶；空目錄執行 | 無 |
| 可留存的證據 | 只有畫面；匯出資料格式不固定 | 完整 stream-json：工具清單、每個訊息區塊、伺服器端計數器 | 原始 request／response JSON、`request-id`、`usage.server_tool_use` |
| 可重複、可自動化 | 否 | 是 | 是 |
| 需要 | 訂閱 | 訂閱或 API 金鑰（本環境已可用） | API 金鑰與額度 |

**結論：用 CLI（主要）或 API（替代），不用 App。** App 的兩次重跑可以留作補充，但不能當「沒有上網」的證據，
而且無法排除記憶功能帶入先前結果。CLI 加上本設計的參數後，與 API 一樣是「模型手上沒有任何工具」，
並且同一個環境裡已經能跑，所以列為主要方案。

## 2. Sandbox 適不適合
- **網路 sandbox 不能保證「沒有搜尋」。** 模型本身必須連到 Anthropic API，而 WebSearch 是在 Anthropic 伺服器端執行的
  （本次正控制驗證：Claude Code 的 WebSearch 由伺服器端另一個模型 `claude-haiku-5-5` 執行搜尋）。
  只允許連 `api.anthropic.com` 的防火牆擋不住它。
- sandbox 只對「模型能跑指令」的情況有用（擋 Bash 的 curl、pip 等）。本設計直接拿掉所有工具，模型無法執行指令，sandbox 變成多餘的保險。
- 真正的保證來自**移除工具**，證據來自**啟動時的工具清單＋伺服器端計數器**，不是網路層。
- 要多一層保險可以：(a) 在 Anthropic Console 的組織設定關閉 web search（只適用 API）；(b) 在 Docker `--network` 只放行 API 主機的容器裡跑；兩者都不是必要條件。

## 3. 所有可能上網或取得外部資訊的管道
| 管道 | 例子 | 本設計如何關閉 |
|---|---|---|
| 內建網路工具 | WebSearch（伺服器端）、WebFetch | `--tools ""` |
| 指令執行 | Bash、Monitor、PowerShell：curl、wget、python requests、git clone、pip、gh、ssh、nslookup | `--tools ""` |
| 先寫腳本再執行 | Write／Edit／NotebookEdit 寫出含網址的腳本 | `--tools ""`（沒有寫檔工具） |
| 載入延後工具 | ToolSearch 載入 WebSearch／MCP | `--tools ""`（ToolSearch 也被移除） |
| 交給別人做 | Agent／Task 子代理、Workflow、SendMessage、建立其他雲端 session、排程 | `--tools ""`；驗證 `subagent_stats.spawned == 0` |
| Skill | deep-research、瀏覽器、computer-use skill | 沒有 Skill 工具，無法呼叫（啟動事件仍列出 skill 名稱，但無工具可用） |
| MCP 伺服器 | GitHub、Google Drive、Claude Docs、claude-code-remote、瀏覽器 | `--strict-mcp-config` 且不給 `--mcp-config`；驗證 `mcp_servers == []` |
| 本機檔案 | repo 中的標籤、`results/round8/*`、AAER | 沒有 Read／Grep／Glob；在新的空目錄執行 |
| 設定與記憶 | CLAUDE.md、自動記憶、hooks、權限設定、外掛 | `--setting-sources ""`、`--no-session-persistence` |
| API 層 | `web_search`／`web_fetch` 伺服器工具、`mcp_servers` 參數、code execution（本身無網路） | CLI 不送；API 方案的請求裡不放 |
| claude.ai 專屬 | Web search 開關、Research、連接器、程式執行網路權限、Claude in Chrome、記憶／過去對話、Project | 不使用 App |

## 4. 驗證方式
### 4.1 每一次執行的自動檢查（`experiment/mem_isolated.py` 的 `verify()`，缺少證據即判失敗）
| 檢查 | 欄位 | 來源 |
|---|---|---|
| tools_empty | `system/init.tools == []` | CLI 啟動時實際提供給模型的工具 |
| mcp_empty | `system/init.mcp_servers == []` | 同上 |
| no_tool_blocks | 所有 assistant 訊息沒有 `tool_use`／`server_tool_use`／`*_tool_result` | 模型輸出 |
| server_web_zero | `result.usage.server_tool_use` 搜尋／抓取都是 0，且 `modelUsage` 中**每個模型**的 `webSearchRequests == 0` | **API 伺服器計費計數**，不是模型自述 |
| no_subagents | `subagent_stats.spawned == 0` | CLI |
| single_turn | `num_turns == 1`（沒有任何工具往返） | CLI |
| completed | `subtype == "success"` | CLI |

每次的原始 stream-json 存在 `raw/`，SHA-256 記在 `verification.csv`，**在算 AUC 之前先 commit**，之後不能改。

### 4.2 正控制與行為檢驗（已執行，2026-11-06，Claude Code 2.1.318，claude-opus-5-5）
| 執行 | 設定 | 結果 |
|---|---|---|
| canary_hardened | 本設計參數，問 2026-11-05 台股收盤（訓練截止 2026-06 之後） | 7 項檢查全過；回答「我不知道……在我的訓練資料截止時間之後」 |
| canary_web_allowed | 只開放 WebSearch | 搜到並答出 41,574.72 點；**檢查判定失敗**（tools_empty、no_tool_blocks、server_web_zero、single_turn 都失敗），證明驗證器抓得到真的搜尋 |

重要發現：正控制中 `result.usage.server_tool_use.web_search_requests` 是 **0**，搜尋只記在
`modelUsage["claude-haiku-5-5"].webSearchRequests = 1`。**只看 `usage` 會漏掉 Claude Code 的搜尋**，必須看 `modelUsage` 的每一個模型。
（先前的稽核是看 tool_use 區塊，不受影響。）

### 4.3 時間外樣本（最強的實質檢驗，建議加入）
在 28 家之外，加入**訓練截止日（2026-06）之後才公開出事**的公司（2026-07 以後的 AAER、8-K Item 4.02 重編），以及同時期的對照公司。
- 只靠記憶：這些公司的分數應該和對照公司差不多，`knows_later_problems` 應為 false。
- 如果這些公司也被打高分、或說「知道後來出事」，代表有記憶以外的資訊來源。
- 名單由協調者從 SEC 網站整理，評分 session 本身不能上網。

### 4.4 「看完整思考 log」可行嗎
- **看不到完整思考。** 目前的模型（含 Opus 5.5）不會回傳原始思考內容，最多只有摘要（`display: "summarized"`），預設是空的。
- **也不需要。** 模型只能透過工具呼叫碰到網路；思考本身不會連網。工具清單為空、輸出沒有工具區塊、伺服器計數為 0，
  這三項就是「沒有上網」的直接證據，比讀思考內容更可靠（思考內容是模型自述，不是紀錄）。
- 思考摘要和 `basis` 欄位可以當質性資料（例如「我記得這家公司 2020 年重編」），用來說明分數來自哪段記憶，但不當作沒上網的證據。

## 5. 實驗步驟
1. `python -m experiment.mem_isolated canary`：每次正式執行前先跑，兩項都必須符合預期（已完成一次，見 4.2）。
2. `python -m experiment.mem_isolated run --runs 5 --seed 20261106`：28 家（`data/mem_isolated/input_round8.txt`，已統一格式），每次不同順序、全新 session。
3. `python -m experiment.mem_isolated verify results/mem_isolated/raw/run*.jsonl`：全部 PASS 才使用；commit 原始紀錄與雜湊。
4. 之後才對標籤算 AUC、組內勝負、與原始 MEM 的 Spearman ρ（沿用 `round8.py` 的 `auc`／`auc_ci`）。
5. 判讀：5 次 AUC 都接近 0.88 → 原始 MEM 的分數可由純記憶重現，「整份 10-K 0.90 是記憶造成」的結論成立。

## 6. 限制
- 證據依賴 Claude Code 的 stream-json 與 API 計數器正確；這是目前能拿到最接近伺服器端的紀錄。
- `claude -p` 主 session 的系統提示詞與原始 MEM 子代理不同，且提示改為直接回覆 JSON（沒有 Write 工具），分數可能略有差異；這不影響「是否上網」的結論。
- 模型版本會變：每次記錄 `init.model`、實際服務的模型與 CLI 版本（已在 `verification.csv`）。
