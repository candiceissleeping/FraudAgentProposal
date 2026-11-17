from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

FONT = "Microsoft JhengHei"
INK, MUTED, ACCENT, HEAD_BG, ROW_ALT, LINE = (RGBColor(0x1F,0x29,0x37), RGBColor(0x6B,0x72,0x80),
    RGBColor(0x1D,0x4E,0xD8), RGBColor(0xE8,0xEE,0xF8), RGBColor(0xF7,0xF8,0xFA), RGBColor(0xD1,0xD5,0xDB))

def style(run, size, bold=False, color=INK):
    f = run.font; f.size = Pt(size); f.bold = bold; f.color.rgb = color; f.name = FONT
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rpr.find(qn(tag))
        if el is None:
            el = rpr.makeelement(qn(tag), {}); rpr.append(el)
        el.set("typeface", FONT)

def textbox(slide, x, y, w, h, text, size, bold=False, color=INK):
    tb = slide.shapes.add_textbox(x, y, w, h); tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; r = p.add_run(); r.text = text; style(r, size, bold, color)
    return tb

prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
s = prs.slides.add_slide(prs.slide_layouts[6])
prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
s = prs.slides.add_slide(prs.slide_layouts[6])
L, W = Inches(0.6), Inches(12.1)
textbox(s, L, Inches(0.35), W, Inches(0.7), "標籤固定為 8-K 4.02：時間內 0.73、時間外 0.69，差距不顯著", 28, True)
textbox(s, L, Inches(1.05), W, Inches(0.75),
        "這個比較在問什麼：同樣是 4.02 樣本，只改「事件在訓練截止（2026-06）前（模型可能記得）或之後（不可能記得）」，"
        "其餘條件全部相同，看只給公司名稱時 AUC 差多少，用來單獨估計記憶的影響。", 14, False, MUTED)

rows = [
    ["", "時間內 4.02", "時間外 4.02（實驗 B）"],
    ["事件期間", "2023-01 至 2025-06（截止前）", "2026-07 至 2026-10（截止後）"],
    ["問題公司怎麼選", "合格 380 家中隨機抽 54 家", "窗口內合格 28 家全數納入，1 家找不到對照"],
    ["樣本數", "54 對（108 家公司）", "27 對（54 家公司）"],
    ["模型執行次數", "2 份名單 × 5 次 = 10 次", "1 份名單 × 5 次 = 5 次"],
    ["模型記得的問題公司", "16/54（30%）", "0/27（0%）"],
    ["AUC（95% CI）", "0.73（0.66–0.80）", "0.69（0.54–0.83）"],
    ["組內勝／平／負", "43／5／6", "21／0／6"],
]
emph = {(6, 1), (6, 2)}
tbl = s.shapes.add_table(len(rows), 3, L, Inches(1.9), W, Inches(4.0)).table
for j, cw in enumerate([3.0, 4.55, 4.55]): tbl.columns[j].width = Inches(cw)
tbl.first_row = True; tbl.horz_banding = False
for i, row in enumerate(rows):
    tbl.rows[i].height = Inches(0.5)
    for j, val in enumerate(row):
        c = tbl.cell(i, j); c.vertical_anchor = MSO_ANCHOR.MIDDLE
        c.margin_left = c.margin_right = Inches(0.12); c.margin_top = c.margin_bottom = Inches(0.04)
        c.fill.solid(); c.fill.fore_color.rgb = HEAD_BG if i == 0 else (ROW_ALT if i % 2 == 0 else RGBColor(0xFF,0xFF,0xFF))
        tf = c.text_frame; tf.word_wrap = True; p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
        r = p.add_run(); r.text = val
        if (i, j) in emph: style(r, 18, True, ACCENT)
        else: style(r, 14, bold=(i == 0 or j == 0), color=INK)

textbox(s, L, Inches(6.05), W, Inches(0.5),
        "差距 +0.04（95% CI −0.13 至 +0.21，包含 0）。原因：4.02 新聞少，時間內也只有 30% 被模型記得。", 15, True)
textbox(s, L, Inches(6.55), W, Inches(0.8),
        "相同條件：同一種標籤、同一套選樣規則（排除 SPAC，需有原始 10-K 與 XBRL；對照為同產業、規模最接近、無 4.02 的公司）、"
        "逐字相同的提示詞、同一無工具環境（Opus 5.5），只給公司名稱與會計年度。"
        "AUC = 隨機各抽一家問題公司與對照公司，問題公司分數較高的機率；0.5 = 隨機。「記得」= 5 次中 ≥3 次說知道後來出事。", 11, False, MUTED)

out = "/home/user/FraudAgentProposal/results/slides/402_in_vs_out.pptx"
prs.save(out); print(out)
