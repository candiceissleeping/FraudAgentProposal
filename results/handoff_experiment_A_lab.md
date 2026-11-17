# 交接：在實驗室電腦重跑「實驗 A：第八輪 MEM 隔離重跑」

> 給實驗室電腦上的 Claude Code 讀。整份照做即可；遇到和預期不符的地方先停下來回報，不要自行改設計。

## 1. 這個實驗在做什麼（一段話版）

第八輪有一個條件叫 **MEM（只靠記憶）**：不給年報，只給 LLM「公司名稱＋會計年度」，要它對每家公司打「該年度財報被重大誤述（舞弊或嚴重會計錯誤）的風險」0–100 分，並回答它是否知道這家公司那段期間後來有重編或 SEC 執法。28 家公司 = 14 家 SEC 會計執法（AAER）的問題公司 + 14 家程式選出的同產業、同規模對照公司。原始結果 AUC 0.88，幾乎等於第七輪「把整份 10-K 交給 LLM」的 0.90。

0.88 只有在**確定模型沒有上網**時才能解讀成「模型記得哪些公司後來出事」。實驗 A 就是在一個**所有工具都被移除**的 Claude Code session 裡重跑 MEM，並用 log 機器驗證它真的沒上網。

先前結果（雲端 5 次 + 使用者 Mac 1 次 = 6 次，全部 Opus 5.5）：

| | AUC |
|---|---|
| 雲端 run1–5 | 0.86／0.89／0.88／0.88／0.88 |
| 雲端 5 次平均分數 | **0.88**（95% CI 0.69–1.00），組內 12 勝／0 平／2 負 |
| 使用者 Mac run1 | 0.86（11／0／3） |
| 原始第八輪 MEM、claude.ai 重跑 ×2 | 0.88、0.88、0.88 |

- 6 次全部通過 7 項「無法上網」檢查
- 與原始 MEM 的 Spearman ρ 0.96–0.98；各次之間最低 0.95
- 每次都輸同兩對：**P13**（Evoqua < Welbilt；對照公司 Welbilt 自己也重編過，模型記得）、**P14**（Gentex < Visteon；模型不記得 Gentex 出事，每次只給 4–5 分）

**這次在實驗室電腦重跑的目的**：換一台機器、換一個 CLI 版本，看結果是否仍落在上述範圍。

## 2. 無法上網的環境怎麼做到

每次評分都是一個全新的 `claude -p`，在新建的空目錄裡執行：

```
claude -p "<提示詞＋28 家名單>" --model claude-opus-5-5 --tools "" --strict-mcp-config \
       --setting-sources "" --no-session-persistence --output-format stream-json --verbose
```

| 參數 | 擋掉什麼 |
|---|---|
| `--tools ""` | 全部內建工具：WebSearch、WebFetch、Bash、讀寫檔、子代理、Skill、ToolSearch |
| `--strict-mcp-config`（不給 `--mcp-config`） | 所有 MCP 伺服器 |
| `--setting-sources ""` | CLAUDE.md、記憶、hooks、權限設定 |
| `--no-session-persistence` | 這次內容不會被下一次讀到 |
| 空目錄 | repo 裡的標籤與結果檔 |

模型只能產生文字，上網一定要透過工具；工具清單是空的，就沒有任何上網管道。網路防火牆或 sandbox **不是**這裡的保證（WebSearch 在 Anthropic 伺服器端執行，擋網路擋不住它）。

`experiment/mem_isolated.py` 的 `verify()` 對每份 stream-json log 做 7 項檢查，缺證據就判失敗：

| 檢查 | 依據 |
|---|---|
| tools_empty | 啟動事件 `tools == []` |
| mcp_empty | 啟動事件 `mcp_servers == []` |
| no_tool_blocks | 所有輸出區塊只有 thinking／text |
| server_web_zero | `usage.server_tool_use` 搜尋與抓取都是 0，**且 `modelUsage` 裡每一個模型**的 `webSearchRequests == 0`（Claude Code 的搜尋記在另一個模型名下，只看主模型會漏掉） |
| no_subagents | `subagent_stats.spawned == 0` |
| single_turn | `num_turns == 1` |
| completed | `subtype == "success"` |

## 3. 執行步驟

### 0) 準備
- 需要：已登入的 Claude Code（`claude --version` 有版本號）、git、python3（只用內建模組）
- 確認可用 `claude-opus-5-5`；若這台機器的 CLI 不認得這個 ID，**停下來回報**，不要換模型
- 取得程式與資料（實驗 A 的檔案都在這個分支）：

```bash
git clone -b claude/peaceful-hawking-w6z0fz https://github.com/candiceissleeping/FraudAgentProposal.git
```
```bash
cd FraudAgentProposal && git checkout -b lab/mem-isolated-rerun
```

- 結果寫到**新資料夾** `results/mem_isolated_lab/`，**不要動** `results/mem_isolated/`（那是先前的正式結果）。評估需要的對照檔先複製過去：

```bash
mkdir -p results/mem_isolated_lab && cp -r results/mem_isolated/key.tsv results/mem_isolated/reference results/mem_isolated_lab/
```

### 1) 先登錄再執行
在跑任何 LLM 之前，寫 `results/mem_isolated_lab/protocol.md`（幾行即可）並 commit：機器、作業系統、`claude --version`、模型 `claude-opus-5-5`、沿用雲端 5 次的同一組名單、預期範圍（AUC 0.86–0.89、平均 0.88、ρ ≥ 0.95、輸 P13 與 P14）。專案原則是「設計先 commit，結果後算」。

### 2) Canary（環境驗證）
```bash
python3 -m experiment.mem_isolated canary --out results/mem_isolated_lab
```
- `canary_hardened`（無工具，問 2026-11-05 台股收盤，訓練截止之後）：應印 `[OK ] ... all_pass=True`，回答「不知道」
- `canary_web_allowed`（正控制，只開 WebSearch）：應搜到點數，`all_pass=False`，因為預期失敗所以仍印 `[OK ]`
- 任何一行出現 `[BAD]` → 停下來回報，不要跑正式 run（例如登入過期時兩個 canary 都會失敗）

### 3) 正式 5 次（沿用雲端的同 5 份名單，只換機器）
```bash
python3 -m experiment.mem_isolated run --out results/mem_isolated_lab --runs 5 --listings results/mem_isolated/inputs
```
- 每次約 30 秒、約 0.09 美元；回答不完整會自動用同一份名單重跑一次（舊檔留成 `run{k}_incomplete1.jsonl`）
- 產出：`raw/run1–5.jsonl`（原始 log）、`run1–5.json`（分數）、`inputs/run1–5.txt`、`verification.csv`
- 每行都應是 `[OK ] runk: all_pass=True ... complete=True`

### 4) 第 6 次：人可以即時看的一次（對應先前使用者 Mac 那次）
先在 repo 根目錄記下路徑，再移到一個空目錄執行：
```bash
export REPO="$PWD" && mkdir -p /tmp/mem_jail && cd /tmp/mem_jail
```
```bash
claude -p "$(cat "$REPO/data/mem_isolated/prompt.md" "$REPO/results/mem_isolated/inputs/run1.txt")" --model claude-opus-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format stream-json --verbose < /dev/null | tee "$REPO/results/mem_isolated_lab/manual_run1.jsonl" | python3 "$REPO/experiment/mem_isolated.py" watch
```
```bash
cd "$REPO"
```
畫面依序出現 `[啟動]`（可用工具=[]）→ `[思考中]` → `[回答]`（28 家 JSON）→ `[結束]`（各模型搜尋次數全 0）→ 最後「全部通過：無法上網」。

### 5) 先 commit 原始紀錄，再算分
```bash
python3 -m experiment.mem_isolated verify results/mem_isolated_lab/raw/run*.jsonl results/mem_isolated_lab/manual_run1.jsonl
```
全部 `PASS` 後，把 `results/mem_isolated_lab/` 整個 commit。`evaluate` 會檢查原始檔已 commit 且未修改，否則拒絕計算。

### 6) 算分
```bash
python3 -m experiment.mem_isolated evaluate --out results/mem_isolated_lab --title "第八輪 MEM 隔離重跑（實驗室電腦）"
```
產出 `results/mem_isolated_lab/evaluation.md`（每次 AUC、CI、組內勝負、「知道」比例、與原始 MEM 的 ρ、逐家分數）。

第 6 次（manual）用同一組函式算：
```bash
python3 - results/mem_isolated_lab/manual_run1.jsonl results/mem_isolated/inputs/run1.txt results/mem_isolated/key.tsv <<'EOF'
import sys, csv
from experiment import mem_isolated as m
raw, listing, keyf = sys.argv[1:]
v = m.verify(m.load_events(raw)); print("all_pass", v["all_pass"])
key = {r["company"]: r["pid"] for r in csv.DictReader(open(keyf), delimiter="\t")}
d = m._by_pid(m.parse_scores(v["answer"]), open(listing).read(), key)
a, lo, hi, w, t, l = m._pairs_auc({p: s for p, (s, k) in d.items()})
print(f"AUC {a:.2f} ({lo:.2f}-{hi:.2f}) W/T/L {w}/{t}/{l}",
      "knows T", sum(k for p,(s,k) in d.items() if p.endswith("T")), "C", sum(k for p,(s,k) in d.items() if p.endswith("C")))
EOF
```
（這段在先前的 Mac 紀錄上測過，得到 AUC 0.86、11/0/3，與先前報告一致。）

### 7) 寫結果並推上去
在 `results/mem_isolated_lab/README.md` 寫：機器與 CLI 版本、6 次是否全部通過檢查、6 次 AUC 與平均、和雲端 5 次（0.86–0.89／0.88）與原始 MEM（0.88）的比較、輸掉哪幾對、和雲端同名單那次的 ρ。commit 後 push 到 `lab/mem-isolated-rerun`（不要 push 到 `claude/peaceful-hawking-w6z0fz`）。

## 4. 判讀
| 結果 | 意思 |
|---|---|
| 6 次全部通過檢查，AUC 約 0.86–0.89，ρ ≥ 0.95，輸 P13、P14 | 重現成功：0.88 換機器仍穩定，來源是模型記憶 |
| AUC 明顯不同（例如 < 0.80） | 先檢查實際服務的模型（`verification.csv` 的 `served_models`）、CLI 版本、回答是否完整，再回報；不要重跑到「對」為止 |
| 任何一次檢查失敗 | 那一次不能算純記憶結果；保留原始檔並回報原因 |

## 5. 注意事項
- 模型每次回答有隨機性；單家公司分數變動 ±10–20 屬正常（例如 AMMO 在先前 6 次中介於 60–85）
- 不要把 `--tools ""` 換成「在提示詞裡說不要上網」：實驗 F 顯示，沒有工具的情況下模型仍會把 `curl` 之類的呼叫寫進文字，只靠提示詞無法保證
- 不要用 claude.ai App 跑：網路開關無法事後證明，且記憶／過去對話可能帶入先前結果
- 參考檔案：`results/mem_experiments_report.md`（實驗 A–E 完整報告）、`results/mem_isolated/design.md`（環境設計理由）、`results/mem_isolated/evaluation.md`（先前結果）、`results/mem_isolated/run_it_yourself.md`（手動版步驟）
