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

textbox(s, Inches(0.6), Inches(0.4), Inches(12.1), Inches(0.8),
        "A（0.88）與 B（0.69）不能直接比較：兩者的標籤不同", 28, True)
textbox(s, Inches(0.6), Inches(1.15), Inches(12.1), Inches(0.5),
        "AAER 樣本多數被模型記得，8-K 4.02 樣本多數沒有", 16, False, MUTED)

rows = [
    ["", "AAER（SEC 執法）", "8-K 4.02（公司自行宣布重編）"],
    ["事件性質", "多為詐欺或重大錯報，有處分、訴訟", "多為會計錯誤，不全是詐欺"],
    ["新聞報導", "多，常有後續報導", "少，多半只有一份 8-K"],
    ["模型記得的問題公司（時間內）", "32/41（78%）", "16/54（30%）"],
    ["時間內 AUC", "0.89（41 對）", "0.73（54 對）"],
    ["時間外 AUC", "僅 2 對，無法做", "0.69（27 對，實驗 B）"],
]
emph = {(3, 1), (3, 2)}
x, y, w = Inches(0.6), Inches(1.85), Inches(12.1)
tbl = s.shapes.add_table(len(rows), 3, x, y, w, Inches(4.2)).table
for j, cw in enumerate([3.5, 4.3, 4.3]): tbl.columns[j].width = Inches(cw)
tbl.first_row = True; tbl.horz_banding = False
for i, row in enumerate(rows):
    tbl.rows[i].height = Inches(0.7)
    for j, val in enumerate(row):
        c = tbl.cell(i, j); c.vertical_anchor = MSO_ANCHOR.MIDDLE
        c.margin_left = c.margin_right = Inches(0.15)
        c.fill.solid(); c.fill.fore_color.rgb = HEAD_BG if i == 0 else (ROW_ALT if i % 2 == 0 else RGBColor(0xFF,0xFF,0xFF))
        tf = c.text_frame; tf.word_wrap = True; p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
        r = p.add_run(); r.text = val
        if (i, j) in emph: style(r, 20, True, ACCENT)
        else: style(r, 16, bold=(i == 0 or j == 0), color=INK)

textbox(s, Inches(0.6), Inches(6.2), Inches(12.1), Inches(0.5),
        "78% vs 30%，Fisher 精確檢定 p < 0.0001。所以 0.88 − 0.69 的差距有一部分來自標籤不同，不能全部歸給記憶。", 15, True)
textbox(s, Inches(0.6), Inches(6.75), Inches(12.1), Inches(0.4),
        "「記得」= 問題公司 5 次中 ≥3 次說知道後來出事。只給公司名稱與年度，Opus 5.5 無工具環境。時間外 = 訓練截止（2026-06）後申報的 4.02。", 11, False, MUTED)

out = "/home/user/FraudAgentProposal/results/slides/AAER_vs_402.pptx"
prs.save(out); print(out)
