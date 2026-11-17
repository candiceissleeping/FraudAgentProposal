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
WHITE, RED, SUB_BG = RGBColor(0xFF,0xFF,0xFF), RGBColor(0xB9,0x1C,0x1C), RGBColor(0xEE,0xF2,0xFF)
prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
L, W = Inches(0.6), Inches(12.1)

def cell(tbl, i, j, val, size, bold=False, color=INK, fill=WHITE, align=PP_ALIGN.LEFT, m=0.1):
    c = tbl.cell(i, j); c.vertical_anchor = MSO_ANCHOR.MIDDLE
    c.margin_left = c.margin_right = Inches(m); c.margin_top = c.margin_bottom = Inches(0.03)
    c.fill.solid(); c.fill.fore_color.rgb = fill
    tf = c.text_frame; tf.word_wrap = True; p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = val; style(r, size, bold, color)

# ---- slide 1: main ----
s = prs.slides.add_slide(prs.slide_layouts[6])
textbox(s, L, Inches(0.35), W, Inches(0.7), "0.69 來自模型對公司的了解，不是記得結果", 28, True)
textbox(s, L, Inches(1.05), W, Inches(0.7),
        "有具體了解的 11 家全部判對；只能看類型的 16 家接近隨機。"
        "時間外 27 家問題公司依模型自己寫的理由分類（只給公司名稱與年度，模型 5 次都說不知道這些公司後來出事）。", 14, False, MUTED)
rows = [
    ["模型對公司的了解", "模型的理由", "家數", "判對／平／判錯", "例子（模型寫的理由）"],
    ["有具體了解\n（截止前的公開資訊）", "過去有內控缺失或治理爭議", "5", "5／0／0", "High Wire Networks：「過去有重大內控缺失、衍生性負債」"],
    ["", "近期業務或交易的會計容易出錯", "4", "4／0／0", "BayFirst：「SBA 放款有損失，呆帳準備要靠判斷」"],
    ["", "財務困境", "2", "2／0／0", "HCW Biologics：「訴訟、繼續經營疑慮、下市風險」"],
    ["", "小計", "11", "11／0／0", ""],
    ["沒有具體了解\n（只看類型）", "公司類型：小型 OTC、殼公司、SPAC、新上市", "14", "8／0／6", "Panamera：「很小的殼型 OTC 公司，內控弱」"],
    ["", "營運在海外", "2", "1／1／0", "Northann：「中國相關的小型 Nasdaq 公司」"],
    ["", "小計", "16", "9／1／6", ""],
]
tbl = s.shapes.add_table(len(rows), 5, L, Inches(1.85), W, Inches(4.0)).table
for j, cw in enumerate([2.2, 4.1, 0.7, 1.6, 3.5]): tbl.columns[j].width = Inches(cw)
tbl.first_row = True; tbl.horz_banding = False
for i, row in enumerate(rows):
    tbl.rows[i].height = Inches(0.5)
    sub = row[1] == "小計"
    for j, val in enumerate(row):
        fill = HEAD_BG if i == 0 else (SUB_BG if sub and j > 0 else WHITE)
        if i == 0: cell(tbl, i, j, val, 14, True, INK, fill, PP_ALIGN.LEFT if j in (0, 1, 4) else PP_ALIGN.CENTER)
        elif j == 0: cell(tbl, i, j, val, 14, True, INK, WHITE)
        elif j in (2, 3): cell(tbl, i, j, val, 16 if sub else 14, sub, ACCENT if sub else INK, fill, PP_ALIGN.CENTER)
        elif j == 1: cell(tbl, i, j, val, 14, sub, INK, fill)
        else: cell(tbl, i, j, val, 12, False, MUTED, fill)
tbl.cell(1, 0).merge(tbl.cell(4, 0)); tbl.cell(5, 0).merge(tbl.cell(7, 0))
textbox(s, L, Inches(6.0), W, Inches(0.5),
        "只留理由為「公司類型」的 14 對：AUC 0.53（95% CI 0.30–0.76），與隨機分不出來。只數延遲申報次數的簡單基準在同一批樣本也是 0.69。", 14, True)
textbox(s, L, Inches(6.55), W, Inches(0.8),
        "依第 1 次執行的理由與分數（20 對／1 平／6 錯；5 次平均分數為 21／0／6，AUC 0.69）。理由類型為事後人工分類，取主要理由，尚未經第二人複核；"
        "判對 = 問題公司的風險分數高於同一對的對照公司。14 對樣本小，只能說沒有證據顯示高於 0.5。逐家理由見附錄。", 11, False, MUTED)

# ---- slide 2: appendix ----
D = [
("FutureTech II Acquisition",25,"Windtree Therapeutics",45,"錯","公司類型","SPAC；信託帳戶會計簡單，但延期與贖回常出問題"),
("BayFirst Financial",25,"Skyline Bankshares",12,"對","業務／會計判斷","小型銀行，SBA 放款損失、策略改變，呆帳準備需判斷"),
("High Wire Networks",45,"KonaTel",30,"對","過去有前例","微型股，併購與出售、衍生性負債、過去有重大內控缺失"),
("Trans American Aquaculture",55,"U.S. Premium Beef",10,"對","公司類型","很小的 OTC 開發階段公司；繼續經營疑慮、內控弱"),
("American Resources",50,"NACCO Industries",8,"對","過去有前例","關係人結構複雜、分拆、閒置煤礦，過去有治理疑慮"),
("New Era Energy & Digital",45,"Trio Petroleum",40,"對","業務／會計判斷","新上市小型股，轉型做數位基礎設施；收購會計"),
("Securetech Innovations",50,"Worksport",30,"對","公司類型","很小的 OTC 公司，幾乎沒有營運"),
("CreditRiskMonitor.com",12,"OMNIQ",45,"錯","公司類型","小型、穩定的訂閱業務，會計簡單"),
("Olenox Industries",50,"Greenwave Technology",55,"錯","公司類型","微型能源整併、借殼上市型態，內控與估值風險高"),
("Northann",45,"Yunhong Green CTI",45,"平","地區","小型中國相關 Nasdaq 公司，透明度與內控有限"),
("Capstone Holding",35,"Greenlane Holdings",45,"錯","公司類型","微型建材控股公司，內控規模小"),
("Pelthos Therapeutics",30,"Artiva Biotherapeutics",12,"對","業務／會計判斷","反向合併後開始商業化的生技公司，有新的會計領域"),
("HCW Biologics",40,"Kiora Pharmaceuticals",15,"對","財務困境","困境中的生技公司，有訴訟、繼續經營疑慮、下市風險"),
("Netcapital",55,"Marygold Companies",20,"對","過去有前例","過去以判斷估值大額股權應收款，大額減損，繼續經營疑慮"),
("Solesence",20,"BONK",45,"錯","公司類型","小型材料公司（原 Nanophase），無已知問題"),
("Brownie's Marine Group",45,"Newton Golf Company",35,"對","過去有前例","OTC 微型股，有併購，曾揭露內控缺失"),
("SDR Drone",50,"Duke Robotics",45,"對","公司類型","不知名微型股，營運歷史短"),
("Nuburu",55,"ESS Tech",30,"對","財務困境","困境中的 de-SPAC 公司，多次轉型、大幅稀釋、繼續經營疑慮"),
("Optimum Communications",12,"Liberty Global",8,"對","公司類型","原 Altice USA；負債高，但是受審計的大型申報人"),
("GlobalTech",50,"Crexendo",15,"對","地區","OTC 控股公司，有海外營運，透明度有限"),
("Sports Entertainment Gaming Global",55,"Pixelworks",20,"對","公司類型","不知名 OTC 公司，像殼公司"),
("EON Resources",45,"Blue Dolphin Energy",30,"對","過去有前例","de-SPAC 石油公司，債務壓力、認股權證會計，過去有重大內控缺失"),
("Globaltek Ventures",55,"Omnitek Engineering",35,"對","公司類型","不知名 OTC 公司，殼公司與內控風險高"),
("GoPro",15,"IMAX",10,"對","公司類型","老牌、四大查帳；有債務壓力但無已知會計問題"),
("High Roller Technologies",30,"Galaxy Gaming",15,"對","公司類型","新上市的小型線上賭場，歷史短"),
("Datavault AI",45,"Paysign",25,"對","業務／會計判斷","原 WiSA；大幅稀釋、不尋常的 IP 與資產交易、估值判斷"),
("Panamera Holdings",45,"Protopia Global Holdings",55,"錯","公司類型","很小的殼型 OTC 公司，小型會計師事務所，內控弱"),
]
assert len(D) == 27 and sum(d[4] == "對" for d in D) == 20 and sum(d[4] == "錯" for d in D) == 6
s2 = prs.slides.add_slide(prs.slide_layouts[6])
textbox(s2, Inches(0.4), Inches(0.2), Inches(12.5), Inches(0.5), "附錄：時間外 27 家問題公司的分數與模型理由（第 1 次執行）", 20, True)
hdr = ["問題公司", "分數", "對照公司", "分數", "判斷", "理由類型", "模型理由（中譯）"]
t2 = s2.shapes.add_table(len(D) + 1, 7, Inches(0.4), Inches(0.75), Inches(12.5), Inches(6.3)).table
for j, cw in enumerate([2.6, 0.5, 2.1, 0.5, 0.5, 1.4, 4.9]): t2.columns[j].width = Inches(cw)
t2.first_row = True; t2.horz_banding = False
for j, h in enumerate(hdr): cell(t2, 0, j, h, 10, True, INK, HEAD_BG, PP_ALIGN.CENTER if j in (1, 3, 4) else PP_ALIGN.LEFT, 0.06)
t2.rows[0].height = Inches(0.22)
for i, d in enumerate(D, 1):
    t2.rows[i].height = Inches(0.22)
    fill = ROW_ALT if i % 2 == 0 else WHITE
    for j, v in enumerate(d):
        wrong = d[4] != "對"
        cell(t2, i, j, str(v), 9, bold=(j == 4 and wrong), color=(RED if (j == 4 and wrong) else INK), fill=fill,
             align=PP_ALIGN.CENTER if j in (1, 3, 4) else PP_ALIGN.LEFT, m=0.06)
textbox(s2, Inches(0.4), Inches(7.08), Inches(12.5), Inches(0.3),
        "分數 0–100，越高風險越高。判斷：問題公司分數高於對照為「對」。理由類型為事後人工分類。原始輸出：results/mem_isolated_oot/run1.json（英文）。", 9, False, MUTED)

out = "/home/user/FraudAgentProposal/results/slides/069_reason_types.pptx"
prs.save(out); print(out)
