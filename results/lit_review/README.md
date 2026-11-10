# 文獻探討：整合性回顧（ARS deep-research `lit-review`，2026-11-09）

依 `results/research_topics.md` 的 5 個研究主題，用 Academic Research Skills（v3.24.1）的 deep-research `lit-review` 模式完成。

## 從哪裡開始讀
1. **`phase3_synthesis/integration.md`**：跨主題整合——五個環節的架構、一致的發現、主題之間的張力、10 項研究缺口與本研究的對照
2. **`phase3_synthesis/T1`–`T5_synthesis.md`**：各主題綜整（文獻矩陣、主要論點與證據強度、矛盾與解釋、研究缺口）
3. **`references.md`**：88 篇文獻總表（去重、含別名與查核狀態）
4. **`phase4_gap_audit/audit.md`**（2026-11-10 新增）：對 10 項研究缺口做反例檢索與引述核對的結果。**其中的判定與改寫都是提議，尚未確認；Phase 3 綜整檔的缺口文字還沒有依此修改，引用缺口前請先看這份**

## 檔案
| 階段 | 檔案 | 內容 |
|---|---|---|
| 規範 | `protocol.md` | 檢索來源、收錄標準、查核規則 |
| Phase 2 書目 | `phase2_bibliography/T{1..5}_bibliography.md`、`T{1..5}_sources.json` | 每主題 20 篇的附註書目（檢索策略、篩選流程、分佈提醒、逐篇註記） |
| Phase 2 書目 | `phase2_bibliography/dreamy_round10_lit_review.md` | 起點文獻（dreamy-volta 第十輪文獻回顧的複本） |
| Phase 2 查核 | `phase2_verification/verification.md`、`.json`、`manual_checks.json` | 逐筆查核結果 |
| Phase 3 綜整 | `phase3_synthesis/T{1..5}_synthesis.md`、`integration.md` | 各主題綜整與跨主題整合 |
| Phase 4 缺口查核 | `phase4_gap_audit/audit.md`、`A_sources.json`、`verification.json` | 缺口判定（提議）、引述更正（提議）、第二輪新增的 60 篇文獻與其查核結果 |
| 總表 | `references.md`、`references.json` | 去重後的文獻總表（第一輪 88 篇＋第二輪新增 60 篇，分段列出） |

## 數字
- 5 個主題各 20 篇，合計 100 筆，去重後 **88 篇**
- 查核：**87 篇 VERIFIED**（DOI 經 Crossref 或 arXiv ID 經 arXiv API，題名與年份相符）、**1 篇 PLAUSIBLE**（Coleman, 2026，Anthropic 工程部落格；無識別碼，網路搜尋與原始頁面確認題名、作者、日期）；沒有任何一筆被判為無法查核或捏造
- 期刊或會議論文 62 篇、預印本 25 篇、技術文件 1 篇
- 第二輪（缺口查核，2026-11-10）新增 **60 篇**，全部 VERIFIED（同一套查核規則）；期刊或會議 23 篇、預印本或工作論文 37 篇。其中 18 篇由協調者親自讀過摘要或章節，42 篇只由檢索子代理讀、協調者核對存在與摘要引句。這 60 篇**沒有**併入 Phase 3 的綜整，也不計入上面的 88 篇

## 流程與工具
- Phase 2 書目：5 個子代理各負責一個主題，依 ARS `bibliography_agent` 規範檢索（WebSearch、arXiv API、Crossref API）
- Phase 2 查核：`experiment/lit_review_verify.py` 程式化比對；沒有識別碼者以網路搜尋人工確認
- Phase 3 綜整：綜整子代理依 ARS `synthesis_agent` 規範撰寫各主題；跨主題整合由協調者撰寫
- 未安裝的 ARS 元件：`shared/` 與 `scripts/`（執行紀錄、引用審核腳本），因此沒有 Material Passport、claim–reference 自動審核與 provenance finalizer；引用標記已寫入，可供之後審核

## 主要限制
- 絕大多數文獻只讀到摘要；引用前應閱讀原文確認
- OpenAlex、Semantic Scholar 沒有 API 金鑰，沒有引用網絡追蹤；SSRN、NBER 無法連線；以英文為主
- 研究缺口一律以「本次檢索範圍內未見」為界，不代表確定不存在
