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
WHITE = RGBColor(0xFF,0xFF,0xFF)
prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
s = prs.slides.add_slide(prs.slide_layouts[6])
L, W = Inches(0.6), Inches(12.1)
textbox(s, L, Inches(0.35), W, Inches(0.7), "讀年報的幫助出現在模型不了解的公司：0.58 → 0.70", 28, True)
textbox(s, L, Inches(1.05), W, Inches(0.75),
        "同一批時間外 27 對（8-K 4.02，事件在訓練截止後），比較兩種輸入：只給公司名稱與年度，以及給整份 10-K。"
        "依模型只看名稱時寫的理由，分成對公司有、沒有具體了解兩組。", 14, False, MUTED)
rows = [
    ["子集", "對數", "只給名稱", "整份 10-K"],
    ["全部", "27", "0.71", "0.76"],
    ["模型對公司有具體了解", "11", "0.90", "0.88"],
    ["模型對公司沒有具體了解", "16", "0.58", "0.70"],
]
emph = {(3, 2), (3, 3)}
tbl = s.shapes.add_table(len(rows), 4, L, Inches(2.0), W, Inches(3.2)).table
for j, cw in enumerate([5.2, 1.7, 2.6, 2.6]): tbl.columns[j].width = Inches(cw)
tbl.first_row = True; tbl.horz_banding = False
for i, row in enumerate(rows):
    tbl.rows[i].height = Inches(0.8)
    for j, val in enumerate(row):
        c = tbl.cell(i, j); c.vertical_anchor = MSO_ANCHOR.MIDDLE
        c.margin_left = c.margin_right = Inches(0.15)
        c.fill.solid(); c.fill.fore_color.rgb = HEAD_BG if i == 0 else (ROW_ALT if i % 2 == 0 else WHITE)
        p = c.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
        r = p.add_run(); r.text = val
        if (i, j) in emph: style(r, 24, True, ACCENT)
        else: style(r, 18, bold=(i == 0 or j == 0), color=INK)
textbox(s, L, Inches(5.4), W, Inches(0.8),
        "模型本來就了解的公司，只看名字已經 0.90，讀年報沒有再提高。"
        "模型不了解的公司，讀年報後多 0.12（95% CI +0.03 至 +0.21）。", 15, True)
textbox(s, L, Inches(6.3), W, Inches(1.0),
        "數字為 AUC。95% CI：全部 0.71（0.56–0.85）、0.76（0.60–0.89），差 +0.05（−0.03 至 +0.12）；有具體了解 0.90（0.81–0.99）、0.88（0.72–1.00）；"
        "沒有具體了解 0.58（0.38–0.78）、0.70（0.46–0.89）。"
        "初步結果，尚不能當結論：分組為事後人工分類；「沒有具體了解」組包含所有只看名稱時判錯的配對，換輸入後容易回升（迴歸平均）；只有 16 對。", 11, False, MUTED)
out = "/home/user/FraudAgentProposal/results/slides/10k_vs_name_by_knowledge.pptx"
prs.save(out); print(out)
