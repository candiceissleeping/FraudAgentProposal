# 實驗一 子代理試跑（smoke test）— 執行前登錄

- 目的：沒有 API 金鑰時，用 Claude Code 子代理當評分者，先檢查流程與輸出格式；**不用來判定 H1**。
- 樣本：試點中 pair_id 最小的 3 組配對（P002、P008、P023），共 6 家公司（D0010、D0014、D0024、D0042、D0055、D0059）。
- 每家 × 4 組（A0–A3）各 1 次 + 1 次身分測試（A1 資料包）= 30 個子代理；每個子代理是全新的對話，只讀一個檔案。
- Prompt：`experiment/yoy/subagent_score_prompt.txt`、`experiment/yoy/subagent_probe_prompt.txt`
  （與 API 版 `run_llm.py` 的 system prompt 與 JSON schema 相同，只多了「只能讀這一個檔案」的指示）。
- 輸入：`data/exp1/packets/` 的同一批資料包，只把超過 1,000 字元的行折行（字詞完全相同），存於 `data/exp1/agent_packets/`。
- 遮蔽對照表 `key.json` 與 10-K 原文在評分期間移出 repo，評分全部完成並提交後才放回並揭盲。
- 與 API 版的差異：無法保證 JSON 格式（解析失敗記為無效）、每份只評 1 次、模型與 effort 由 Claude Code 決定。
