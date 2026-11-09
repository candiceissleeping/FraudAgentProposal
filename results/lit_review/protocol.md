# 文獻探討檢索規範（整合性回顧，ARS deep-research `lit-review` 模式）

- 執行日期：2026-11-09
- 回顧形式：整合性回顧（integrative review），由使用者指定；ARS 的回顧形式提醒依規則略過（作者已指定形式）
- 主題：`results/research_topics.md` 的 5 個研究主題
- 起點文獻：dreamy-volta 分支第十輪文獻回顧（複本：`phase2_bibliography/dreamy_round10_lit_review.md`），約 30 篇，偏主題 1、5
- 流程：Phase 2 書目（每主題一個子代理）→ Phase 2 來源查核（程式核對 DOI／arXiv＋WebSearch 抽查）→ Phase 3 綜整

## 檢索來源
| 來源 | 用途 | 狀態 |
|---|---|---|
| WebSearch | 主要檢索、找出版處 | 可用 |
| arXiv API（https://export.arxiv.org/api/query） | 預印本檢索與 ID 查核 | 可用 |
| Crossref API（https://api.crossref.org/works） | 期刊與會議論文檢索、DOI 查核 | 可用 |
| OpenAlex、Semantic Scholar | 引用網絡、去重 | 無 API 金鑰（429），不使用；ARS 的 S2 去重步驟依其降級規則略過 |
| MDPI、SSRN、NBER 網站 | 全文 | 先前無法連線；以 Crossref 書目與摘要代替 |

## 收錄標準（每個主題相同）
| 項目 | 收錄 | 排除 |
|---|---|---|
| 相關性 | 直接回應該主題的研究問題 | 只是順帶提到 |
| 年份 | 2020 年以後為主；經典會計舞弊、記憶與污染的奠基文獻不限年份 | — |
| 類型 | 期刊、會議論文（Tier 1）；預印本（Tier 2，標示）；必要時少量官方或技術文件（Tier 3，每主題至多 2 篇） | 部落格、新聞、行銷文章；掠奪性期刊 |
| 可查核性 | 有 DOI、arXiv ID 或穩定網址，且題名、作者、年份可核對 | 查不到存在證據者（ARS 規則：灰色地帶＝剔除） |
| 語言 | 英文為主；有中文文獻也可 | — |
| 數量 | 每主題 10–20 篇 | — |

## 每篇的書目紀錄
- APA 7 書目、識別碼（DOI／arXiv ID／網址）
- 相關性、主要發現、方法、證據等級（I–VII）、Tier
- 閱讀範圍：`abstract_only`／`sections`／`full_text`。只讀到摘要時，「方法弱點」依 ARS 規則寫 `not assessed (read scope: abstract_only)`，不推測
- 與本研究實驗（A–E、第八～十輪）的關聯

## 查核規則（Phase 2 來源查核）
- 有 DOI：以 Crossref `/works/{doi}` 取回題名與年份，比對題名相似度與年份（±1）
- 有 arXiv ID：以 arXiv API 取回題名，比對
- 兩者皆無：WebSearch 以「題名＋第一作者＋年份」查找
- 結果：`VERIFIED`（DOI 或 arXiv 相符）、`PLAUSIBLE`（WebSearch 確認存在）、`DOI_MISMATCH`、`UNVERIFIABLE`／`FABRICATED` → 剔除，不進入綜整
