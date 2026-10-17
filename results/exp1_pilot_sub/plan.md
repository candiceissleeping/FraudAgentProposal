# 實驗一 30 組試點（子代理版，精簡）— 執行前登錄

## 為什麼這樣設計
試跑（`results/exp1_smoke/`）顯示：遮蔽 v1、v2 都擋不住模型認出公司（6/6），而且只給公司名稱的記憶基準 K0 就能排對 3/3 組。
因此本試點把「記憶」當成要控制的變因，而不是假設遮蔽能消除它。

## 樣本與組別
- 30 組試點配對（`config/exp1_sample.json` 中 `pilot: true`），60 家公司，**全部重評**（含試跑過的 3 組）。
- 輸入：遮蔽 v2 資料包（`data/exp1v2/`，雜湊 `results/exp1_packets_pilot_v2.sha256`）。
- 組別（每家各 1 次，共 180 個子代理）：
  - **A0**：當年 10-K
  - **A2**：當年 10-K + 年度差異
  - **K0（記憶基準 v2）**：只給公司名稱（含曾用名）與會計年度，不給財報；另外回答是否記得該年度的 SEC 執法行動（yes / no / unsure）
- 指示檔：`experiment/yoy/subagent_score_instructions.txt`（與 API 版 system prompt 和 JSON schema 相同）、`experiment/yoy/subagent_memory_instructions.txt`。
- 每個子代理只能讀「指示檔 + 一份資料包」（K0 只能讀指示檔）；逐一稽核工具呼叫，違規者記為 `isolation_breach` 不採用。
- 評分期間答案對照表與 10-K 原文移出 repo；全部回覆提交後才揭盲。

## 事先登錄的分析
1. **主要**：「記憶乾淨」子樣本 = 配對中兩家公司 K0 的 `recalls_sec_enforcement_for_year` 都是 `no` 或 `unsure`。
   在這個子樣本上報告 A2 − A0 的 ΔAUC（配對 bootstrap 95% CI）與配對內正確率（McNemar）。
2. **次要**：全部 30 組的 A2 − A0；A0 − K0、A2 − K0。
3. **描述**：K0 回答 `yes` 的比例、以及 `yes` 時 K0 分數是否接近 100（記憶的強度）。
4. 試點用途：估計變異與「記憶乾淨」子樣本占比，決定主實驗所需樣本數；**不據此判定 H1**。
