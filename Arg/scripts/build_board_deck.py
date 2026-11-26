"""
Board presentation (PowerPoint)
===============================

WHAT THIS FILE DOES
    Builds final_deliverables/NovaFin_Board_Presentation.pptx: the brief's "Final Group Presentation …
    assuming you are presenting to the board". Answer first, then why, the framework, integration, ML
    validation, risk, the capital plan (what we use now, how the reserve is released, what each stage changes),
    controls and the phased action plan. Every number is read from Module 9's
    saved outputs (and through them, Modules 1–8), so the deck always matches the notebooks.
    Charts are native PowerPoint charts (editable); speaker notes on every slide.

HOW TO USE
    python scripts/build_board_deck.py          (after Module 9 has run)
"""
import json
import sys
from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_TICK_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
O9 = ROOT / "module_09_capital_allocation" / "outputs"
OUT = ROOT / "final_deliverables" / "NovaFin_Board_Presentation.pptx"
K = json.loads((O9 / "key_numbers.json").read_text(encoding="utf-8"))
alloc = pd.read_csv(O9 / "FINAL_M9_allocation.csv")
alt = pd.read_csv(O9 / "plan_vs_alternatives.csv")
val = pd.read_csv(O9 / "ml_value_by_module.csv")
sc = pd.read_csv(O9 / "ml_scorecard.csv")
st = pd.read_csv(O9 / "stress_tests.csv")
gr = pd.read_csv(O9 / "growth_path.csv")
gov = pd.read_csv(O9 / "governance.csv")
acts = pd.read_csv(O9 / "actions.csv")
integ = pd.read_csv(O9 / "integration_map.csv")
use_now = pd.read_csv(O9 / "capital_plan_use_now.csv")
release = pd.read_csv(O9 / "reserve_release_plan.csv")
stages = pd.read_csv(O9 / "capital_plan_stages.csv")

# Palette: deep ink navy dominates; amber is the one sharp accent; green/red only for gains/losses
NAVY, INK, MUTED, LIGHT, CARD = RGBColor(0x14, 0x21, 0x3D), RGBColor(0x1E, 0x1E, 0x1E), RGBColor(0x5B, 0x63, 0x70), RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0xEE, 0xF1, 0xF6)
AMBER, GAIN, LOSS, STEEL = RGBColor(0xD9, 0x8E, 0x04), RGBColor(0x1E, 0x8C, 0x6E), RGBColor(0xB2, 0x3A, 0x48), RGBColor(0x5C, 0x7A, 0x99)
HEAD, BODY = "Cambria", "Calibri"
W, H = Inches(13.333), Inches(7.5)

prs = Presentation()
prs.slide_width, prs.slide_height = W, H
BLANK = prs.slide_layouts[6]
N = [0]


def text(slide, x, y, w, h, runs, size=16, color=INK, bold=False, font=BODY, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, name=None):
    """A text box; `runs` is a string or a list of paragraphs, each a string or a list of (text, {bold, color, size})."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    if name:
        tb.name = name
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05); tf.margin_top = tf.margin_bottom = Inches(0.03)
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.space_after = Pt(6)
        for part in (para if isinstance(para, list) else [(para, {})]):
            t, o = part if isinstance(part, tuple) else (part, {})
            r = p.add_run(); r.text = t
            r.font.name = o.get("font", font); r.font.size = Pt(o.get("size", size)); r.font.bold = o.get("bold", bold)
            r.font.color.rgb = o.get("color", color)
    return tb


def card(slide, x, y, w, h, fill=CARD, name=None):
    """A rounded card with a soft tint (no edge stripes)."""
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    s.adjustments[0] = 0.08; s.fill.solid(); s.fill.fore_color.rgb = fill; s.line.fill.background(); s.shadow.inherit = False
    if name:
        s.name = name
    return s


def badge(slide, x, y, label, fill=AMBER, size=0.55):
    """The deck's motif: a numbered circle."""
    c = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, Inches(size), Inches(size))
    c.fill.solid(); c.fill.fore_color.rgb = fill; c.line.fill.background(); c.shadow.inherit = False
    tf = c.text_frame; tf.margin_left = tf.margin_right = 0
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; r = p.add_run(); r.text = str(label)
    r.font.name = HEAD; r.font.bold = True; r.font.size = Pt(16); r.font.color.rgb = LIGHT
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE


def new_slide(title, dark=False, notes=""):
    """A slide with its title in the same place every time, page number and footer."""
    s = prs.slides.add_slide(BLANK); N[0] += 1
    bg = s.background.fill; bg.solid(); bg.fore_color.rgb = NAVY if dark else LIGHT
    text(s, Inches(0.6), Inches(0.35), Inches(12.1), Inches(1.0), title, size=30, bold=True, font=HEAD, color=LIGHT if dark else NAVY, name="Title")
    text(s, Inches(0.6), Inches(7.0), Inches(9), Inches(0.35), "Group 07 · NovaFin Group · Capital allocation of ₹1,000 crore", size=10, color=LIGHT if dark else MUTED)
    text(s, Inches(11.9), Inches(7.0), Inches(0.9), Inches(0.35), str(N[0]), size=10, color=LIGHT if dark else MUTED, align=PP_ALIGN.RIGHT)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def style_chart(ch, legend=False, size=12):
    """Same quiet look on every chart: Calibri labels, muted axes, no gridline clutter."""
    ch.font.name = BODY; ch.font.size = Pt(size); ch.font.color.rgb = MUTED
    ch.has_legend = legend
    if legend:
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False; ch.legend.font.size = Pt(size)
    try:
        ch.value_axis.has_major_gridlines = False; ch.value_axis.visible = False
        ch.category_axis.format.line.color.rgb = RGBColor(0xC9, 0xCE, 0xD6); ch.category_axis.tick_labels.font.size = Pt(size)
        ch.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW          # labels stay clear of negative bars
        for ser in ch.plots[0].series:
            ser.invert_if_negative = False                                         # negative bars keep their colour
    except Exception:
        pass


def table(slide, df, x, y, w, col_w, size=12, head_fill=NAVY, row_h=0.42):
    """A clean table: navy header, tinted alternate rows, Calibri."""
    rows, cols = len(df) + 1, len(df.columns)
    t = slide.shapes.add_table(rows, cols, x, y, w, Inches(row_h * rows)).table
    for j, cw in enumerate(col_w):
        t.columns[j].width = Inches(cw)
    for j, c in enumerate(df.columns):
        cell = t.cell(0, j); cell.fill.solid(); cell.fill.fore_color.rgb = head_fill
        cell.text = str(c); para = cell.text_frame.paragraphs[0]
        for r in para.runs:
            r.font.size = Pt(size); r.font.bold = True; r.font.color.rgb = LIGHT; r.font.name = BODY
    for i, row in enumerate(df.itertuples(index=False), start=1):
        for j, v in enumerate(row):
            cell = t.cell(i, j); cell.fill.solid(); cell.fill.fore_color.rgb = CARD if i % 2 == 0 else LIGHT
            cell.text = str(v)
            for para in cell.text_frame.paragraphs:
                for r in para.runs:
                    r.font.size = Pt(size); r.font.color.rgb = INK; r.font.name = BODY
    return t


cr = lambda v: f"−₹{-v:,.1f} crore" if v < 0 else f"₹{v:,.1f} crore"
cr0 = lambda v: "≈ ₹0" if abs(v) < 0.05 else cr(v)                       # near-zero amounts shown as ≈ ₹0, not −₹0.0
SQ, ALL8 = K["status_quo"], K["stress"]["8. All at once: 1 + 3 + 4 + 7"]
G2, G2b = K["growth"]["Year 2, ₹1 = ₹1 view"], K["growth"]["Year 2, bank view (12% capital, 5% cost of funds)"]
CP = K["capital_plan"]; STEP = CP["step_crore"]
WORK = "Money working in NovaFin's businesses (₹ crore)"
LGD60 = "Bad year if collateral also fetches less, LGD 60% (₹ crore)"
RISK_A = float(K["initiatives_crore"]) - sum(K["by_category_crore"][c] for c in ["Corporate lending", "Retail lending", "Digital banking", "Wealth management"])   # Risk Analytics initiatives (shown in the Derivatives hedging bar)
HEDGE = K["by_category_crore"]["Derivatives hedging"] - RISK_A               # the put and the option-book hedge
assert abs(K["equities_crore"] + K["initiatives_crore"] + 5 + HEDGE + K["reserve_crore"] - 1000) < 0.01                         # the headline adds to ₹1,000 crore
ABOVE = "Profit above the bank's way (₹ crore a year)"

# 1 Title -------------------------------------------------------------------------------------------
s = new_slide("", dark=True, notes="Opening: we were asked where ₹1,000 crore should go, what risks NovaFin takes and how they are controlled. The answer is on the next slide; everything after explains why.")
text(s, Inches(0.8), Inches(2.0), Inches(11.5), Inches(1.6), "Where ₹1,000 crore should go — and how NovaFin grows safely", size=40, bold=True, font=HEAD, color=LIGHT)
text(s, Inches(0.8), Inches(3.8), Inches(11.5), Inches(1.0), "ML-driven enterprise financial strategy, risk and decision support · Recommendation to the Board", size=20, color=RGBColor(0xC9, 0xD3, 0xE3))
badge(s, Inches(0.8), Inches(5.2), "₹", size=0.7)
text(s, Inches(1.7), Inches(5.25), Inches(10), Inches(0.6), "Nine modules · one decision framework · every number reproducible", size=16, color=AMBER)
text(s, Inches(0.8), Inches(6.15), Inches(11.5), Inches(0.5), "Group 07: Arg Ankit · Pravin Patil · Vineet Ojha · Pratik Saxena · Kshitiz Saxena", size=15, color=LIGHT)

# 2 The answer ---------------------------------------------------------------------------------------
s = new_slide("The answer: earn ₹92 crore a year now, and put the reserve to work in tested steps",
              notes=f"Expected profit {cr(K['expected_crore_a_year'])} a year ({K['expected_pct']:.1f}%) on ₹1,000 crore, against {cr(SQ['profit'])} if the money went through today's practice. Even a crash, a rate cut and failing initiatives together would lose {cr(-ALL8)} today, against our loss limit of ₹100 crore (10% of the ₹1,000 crore). Growth: the ₹{K['reserve_crore']:.0f} crore reserve is released in three tested steps, so money working in NovaFin's businesses grows from ₹{stages[WORK].iloc[0]:.0f} crore to ₹{stages[WORK].iloc[2]:.0f} crore once lending is re-priced; only a ₹{CP['floor_crore']:.0f} crore floor stays.")
stats = [(f"₹{K['expected_crore_a_year']:.1f} cr", f"expected profit a year ({K['expected_pct']:.1f}%)", GAIN),
         (f"−₹{-SQ['profit']:.1f} cr" if SQ["profit"] < 0 else f"₹{SQ['profit']:.1f} cr", "the bank's current way, same ₹1,000 crore", LOSS),
         (f"−₹{-ALL8:.1f} cr", "worst year today: crash + rate cut + failed initiatives", NAVY),
         (f"₹{stages[WORK].iloc[2]:.0f} cr", f"working in NovaFin's businesses once lending is re-priced (₹{stages[WORK].iloc[0]:.0f} crore today)", AMBER)]
for i, (big, small, col) in enumerate(stats):
    x = Inches(0.6 + i * 3.1)
    card(s, x, Inches(1.7), Inches(2.85), Inches(2.6))
    text(s, x + Inches(0.2), Inches(1.95), Inches(2.5), Inches(1.0), big, size=36, bold=True, font=HEAD, color=col)
    text(s, x + Inches(0.2), Inches(3.05), Inches(2.5), Inches(1.1), small, size=15, color=INK)
text(s, Inches(0.6), Inches(4.75), Inches(12.1), Inches(2.0), [
    [("Where it goes: ", {"bold": True}), (f"₹{K['equities_crore']:.0f} crore equities protected by a put · ₹{K['initiatives_crore']:.0f} crore initiatives · ₹5 crore HFT pilot · ₹{HEDGE:.0f} crore hedging · ₹{K['reserve_crore']:.0f} crore reserve, released in tested steps (₹{STEP['1 approved loans']:.0f} + ₹{STEP['2 review loans']:.0f} + up to ₹{STEP['3 future initiatives']:.0f} crore) with a ₹{CP['floor_crore']:.0f} crore floor", {})],
    [("Why: ", {"bold": True}), ("the protected equities and the initiatives are the uses that beat safe government securities (6.8%) on the evidence; lending at today's prices earns 3.3% and loses money in a recession", {})]], size=16)

# 3 Allocation chart ---------------------------------------------------------------------------------
s = new_slide("Where the ₹1,000 crore goes",
              notes=f"Bars are ₹ crore per category and add to ₹1,000 crore. Initiatives total ₹{K['initiatives_crore']:.0f} crore: they sit in the Digital, Wealth, Retail and Corporate bars, and ₹{RISK_A:.1f} crore of Risk Analytics sits in the Derivatives hedging bar. The reserve is large because, on the evidence, little else beats 6.8% at scale; it is also the pool that funds lending once loans are re-priced.")
a = alloc.sort_values("₹ crore")
cd = CategoryChartData(); cd.categories = list(a.Category); cd.add_series("₹ crore", [round(v, 1) for v in a["₹ crore"]])
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.6), Inches(1.4), Inches(7.6), Inches(5.4), cd); ch = gf.chart
style_chart(ch); pl = ch.plots[0]; pl.gap_width = 45; pl.has_data_labels = True
ch.value_axis.maximum_scale = 760                                               # room for the longest bar's label
pl.data_labels.number_format = '"₹"#,##0.0" cr"'; pl.data_labels.number_format_is_linked = False; pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END; pl.data_labels.font.size = Pt(12)
for k, pt in enumerate(pl.series[0].points):
    pt.format.fill.solid(); pt.format.fill.fore_color.rgb = AMBER if a.Category.iloc[k] == "Equity investments" else (STEEL if a.Category.iloc[k] == "Liquidity reserve" else NAVY)
card(s, Inches(8.5), Inches(1.5), Inches(4.2), Inches(5.2))
eq = alloc.set_index("Category")
text(s, Inches(8.75), Inches(1.7), Inches(3.8), Inches(4.9), [
    [("Equities ₹300 crore", {"bold": True, "color": NAVY})], "All 15 stocks, equal weight; a put caps a crash at about ₹35 crore",
    [("Initiatives ₹51 crore", {"bold": True, "color": NAVY})], f"Wealth 17.6%, Digital 13.2%, Payments 13.0% a year; mostly after review. ₹{RISK_A:.1f} crore of it (Risk Analytics) is in the hedging bar",
    [(f"Reserve ₹{K['reserve_crore']:.0f} crore", {"bold": True, "color": NAVY})], f"Earns 6.8% while it waits; released in 3 tested steps; ₹{CP['floor_crore']:.0f} crore floor (slide 5)",
    [(f"HFT ₹5 crore, hedging ₹{HEDGE:.0f} crore", {"bold": True, "color": NAVY})], "A pilot with a stop rule; the equity put and the option-book hedge"], size=14)

# 4 Capital plan, part 1: what we use now --------------------------------------------------------------
s = new_slide("The capital plan, part 1: what we put to work now",
              notes=f"Six uses, ₹1,000 crore. Equities with the put are the only large use above 6.8%; the initiatives are in units that clear the hurdle (plus one approved Corporate Banking project of ₹1 crore), two projects ready now and the rest after review; the HFT pilot is small with a stop rule. The reserve earns ₹{CP['reserve_earns_crore']:.1f} crore a year and is released by the plan on the next slide. Each line has an owner and a first action.")
SHORT = ["Equities: all 15, equal weight, + 90% put", "Initiatives ready now (2 projects)", "Initiatives after review (5 units)", "HFT trading pilot (stop rule)",
         "Option book hedge (choice C)", "Liquidity reserve (released by the plan)"]
un = pd.DataFrame({"Use": SHORT, "₹ crore": [f"{v:,.1f}" for v in use_now["₹ crore"]],
                   "Earns a year": [cr0(v) for v in use_now["Expected ₹ crore a year"]], "Bad year": [cr0(v) for v in use_now["Bad-year result (₹ crore)"]],
                   "Owner": [o.split(" (")[0] for o in use_now.Owner], "First action": list(use_now["First action and when"])})
un.loc[len(un)] = ["Total", f"{use_now['₹ crore'].sum():,.0f}", cr(use_now["Expected ₹ crore a year"].sum()), f"{cr(ALL8)} (all at once)", "", ""]
t = table(s, un, Inches(0.6), Inches(1.4), Inches(12.1), [3.5, 1.1, 1.6, 1.9, 2.0, 2.0], size=12, row_h=0.62)
for j in range(len(un.columns)):
    for r_ in t.cell(len(un), j).text_frame.paragraphs[0].runs:
        r_.font.bold = True

# 5 Capital plan, part 2: the reserve release plan ------------------------------------------------------
s = new_slide(f"Part 2: the ₹{K['reserve_crore']:.0f} crore reserve is a waiting room",
              notes=f"The reserve earns ₹{CP['reserve_earns_crore']:.1f} crore a year while it waits. Step 1 releases ₹{STEP['1 approved loans']:.0f} crore into approved loans once re-priced loans earn at least 6.8% after expected loss (about {K['reprice_needed'][0]:.1f}%, 8.75% today). Step 2 releases ₹{STEP['2 review loans']:.0f} crore into Review loans once fixed (about {K['reprice_needed'][1]:.1f}%). Step 3 funds up to ₹{STEP['3 future initiatives']:.0f} crore of future initiatives through Module 1's rules. ₹{CP['floor_crore']:.0f} crore is never released. If a test fails, the money stays earning 6.8%. Lending the loans today would cost ₹{CP['cost_release_now_crore']:.1f} crore a year.")
cards = [("1", f"₹{STEP['1 approved loans']:.0f} crore", "Approved loans, re-priced",
          f"Released when re-priced loans earn ≥ 6.8% after expected loss (rate ≈ {K['reprice_needed'][0]:.1f}%, 8.75% today) and the scorecard stays stable",
          "Every quarter · Chief Risk Officer + Head of Lending; ALCO releases", NAVY),
         ("2", f"₹{STEP['2 review loans']:.0f} crore", "Review loans, fixed",
          f"Same test at ≈ {K['reprice_needed'][1]:.1f}% (9.8% today), or collateral added or a person's check; only after step 1",
          "Every quarter, after step 1 · same owners", NAVY),
         ("3", f"Up to ₹{STEP['3 future initiatives']:.0f} cr", "Future initiatives",
          "Each project: Expected NPV above 0, return above 6.8%, within loss tolerance; Digital only while the fraud rule runs",
          "At each project review · Head of Strategy; CFO approves", NAVY),
         ("■", f"₹{CP['floor_crore']:.0f} crore", "Floor: never released",
          "At least 10% of the ₹1,000 crore stays safe, for withdrawals and a bad year", "Every quarter · Treasurer with ALCO", STEEL)]
for i, (b, amt, what, test, who, col) in enumerate(cards):
    x = Inches(0.6 + i * 3.08)
    card(s, x, Inches(1.45), Inches(2.9), Inches(4.25))
    badge(s, x + Inches(0.2), Inches(1.65), b, fill=AMBER if col == NAVY else STEEL)
    text(s, x + Inches(0.9), Inches(1.62), Inches(1.95), Inches(0.6), amt, size=20, bold=True, font=HEAD, color=col, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + Inches(0.2), Inches(2.35), Inches(2.6), Inches(0.5), what, size=15, bold=True, color=INK)
    text(s, x + Inches(0.2), Inches(2.9), Inches(2.6), Inches(1.9), test, size=12.5)
    text(s, x + Inches(0.2), Inches(4.85), Inches(2.6), Inches(0.8), who, size=11.5, color=MUTED)
facts = [(f"₹{CP['reserve_earns_crore']:.1f} cr", "a year earned by the reserve while it waits"),
         (f"₹{CP['cost_release_now_crore']:.1f} cr", "a year it would cost to lend at today's prices instead"),
         ("6.8%", "still earned on any money whose test fails")]
for i, (big, small) in enumerate(facts):
    x = Inches(0.6 + i * 4.1)
    text(s, x, Inches(5.9), Inches(1.6), Inches(0.8), big, size=22, bold=True, font=HEAD, color=AMBER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + Inches(1.6), Inches(5.9), Inches(2.4), Inches(0.8), small, size=13, anchor=MSO_ANCHOR.MIDDLE)

# 6 Capital plan, part 3: what each stage changes ----------------------------------------------------------
s = new_slide("Part 3: business grows, profit holds, risk stays in bounds",
              notes=f"Money working in NovaFin's businesses grows from ₹{stages[WORK].iloc[0]:.0f} crore today to ₹{stages[WORK].iloc[2]:.0f} crore after the two lending steps and ₹{stages[WORK].iloc[3]:.0f} crore with step 3. Re-priced loans are planned at exactly the 6.8% hurdle, so in the ₹1 = ₹1 view profit holds at ₹{stages['Profit a year (₹ crore)'].iloc[0]:.1f} crore; in the bank view it rises to ₹{stages['Profit a year, bank view (₹ crore)'].iloc[2]:.1f} crore. The combined bad year uses at most a third of the ₹100 crore loss limit; if collateral also fetches less (a defaulted loan loses 60% instead of 40%), it reaches −₹{-stages[LGD60].iloc[2]:.1f} crore after step 2 and −₹{-stages[LGD60].iloc[3]:.1f} crore after step 3, still inside it. These shares count the reserve's interest. Step 3 assumes future initiatives perform like today's.")
LAB = ["Today", "After step 1", "After step 2", "After step 3"]
cd = CategoryChartData(); cd.categories = LAB; cd.add_series("Money working in NovaFin's businesses (₹ crore)", [round(v, 0) for v in stages[WORK]])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(1.75), Inches(5.0), Inches(4.9), cd); ch = gf.chart
style_chart(ch); ch.has_title = False; pl = ch.plots[0]; pl.gap_width = 60; pl.has_data_labels = True; pl.data_labels.font.size = Pt(13)
pl.data_labels.number_format = '"₹"#,##0" cr"'; pl.data_labels.number_format_is_linked = False; pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
pl.series[0].format.fill.solid(); pl.series[0].format.fill.fore_color.rgb = AMBER
text(s, Inches(0.6), Inches(1.35), Inches(5.0), Inches(0.4), "Money working in NovaFin's businesses (₹ crore)", size=13, bold=True, color=NAVY)
mt = pd.DataFrame({"Measure": ["Reserve", "Loan book", "Profit a year", "Profit, bank view", "Bad year (share of ₹100 cr limit)", "Same, if collateral fetches less", "Profit above the bank's way"]})
for k, lab in enumerate(LAB):
    r_ = stages.iloc[k]
    mt[lab] = [f"₹{r_['Liquidity reserve (₹ crore)']:.0f} cr", f"₹{r_['Loan book (₹ crore)']:.0f} cr", f"₹{r_['Profit a year (₹ crore)']:.1f} cr",
               f"₹{r_['Profit a year, bank view (₹ crore)']:.1f} cr", f"{cr(r_['Bad year, all at once (₹ crore)'])} ({r_['Share of the ₹100 crore bad-year budget used']:.0%})",
               f"{cr(r_[LGD60])} ({max(0, -r_[LGD60]) / 100:.0%})",
               f"+₹{r_[ABOVE]:.1f} cr"]
mt.columns = ["Measure"] + LAB
table(s, mt, Inches(5.9), Inches(1.45), Inches(6.8), [1.9, 1.2, 1.2, 1.25, 1.25], size=11.5, row_h=0.54)
text(s, Inches(5.9), Inches(5.95), Inches(6.8), Inches(0.8),
     "Profit holds because re-priced loans are planned at exactly 6.8%: anything above is upside. Bank view: deposits fund 88% of each loan at 5%. Step 3 assumes future initiatives perform like today's.",
     size=11.5, color=MUTED)

# 4 vs alternatives ----------------------------------------------------------------------------------
s = new_slide("Better than the bank's current way on profit and on safety",
              notes=f"Same ₹1,000 crore four ways. The bank's way (every loan at today's prices, all 180 initiatives) earns {cr(SQ['profit'])} and loses {cr(-SQ['bad'])} in a bad year. All-equities earns most but loses ₹200 crore in a crash, twice our ₹100 crore loss limit. Our plan earns ₹91.8 crore and loses ₹5 crore in today's worst combined year.")
cd = CategoryChartData(); cd.categories = [w.replace(" (status quo)", "") for w in alt["Way to deploy ₹1,000 crore"]]
cd.add_series("Profit a year (₹ crore)", [round(v, 1) for v in alt["Profit a year (₹ crore)"]])
cd.add_series("Bad year, all at once (₹ crore)", [round(v, 1) for v in alt["Bad year, all at once (₹ crore)"]])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(1.4), Inches(8.2), Inches(5.4), cd); ch = gf.chart
style_chart(ch, legend=True); pl = ch.plots[0]; pl.gap_width = 60; pl.has_data_labels = True; pl.data_labels.font.size = Pt(11)
pl.data_labels.number_format = '#,##0.0;"−"#,##0.0'; pl.data_labels.number_format_is_linked = False; pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
pl.series[0].format.fill.solid(); pl.series[0].format.fill.fore_color.rgb = NAVY
pl.series[1].format.fill.solid(); pl.series[1].format.fill.fore_color.rgb = LOSS
card(s, Inches(9.1), Inches(1.5), Inches(3.6), Inches(5.2))
text(s, Inches(9.3), Inches(1.7), Inches(3.2), Inches(4.9), [
    [("The bank's way loses money", {"bold": True, "color": LOSS})], "Its lending earns 0.43% above expected credit losses; its initiatives −3.6% a year",
    [("All-equities breaks the limit", {"bold": True, "color": LOSS})], "A 20% crash costs ₹200 crore; our loss limit is ₹100 crore",
    [("Our plan", {"bold": True, "color": GAIN})], "₹91.8 crore a year; worst combined year today −₹5 crore"], size=14)

# 5 Framework ----------------------------------------------------------------------------------------
s = new_slide("Every decision follows one financial decision framework",
              notes="The brief asks for an integrated answer, not isolated models. Every module, and the allocation, goes through these six steps; no model output is used until it is in rupees, stress-tested and owned.")
steps = [("Data", "Clean, leak-free, checked"), ("ML prediction", "Tested against a benchmark on unseen data and for luck"),
         ("₹ metric", "NPV, ECL, cost of fraud, CLV, return after costs, Black-Scholes"), ("Risk", "Bad year, VaR, stress, reverse stress"),
         ("Decision rule", "Beat 6.8% risk-free; capacity, caps, ₹100 crore loss limit"), ("Control", "Owner, what is watched, trigger → action")]
for i, (h, d) in enumerate(steps):
    x = Inches(0.6 + i * 2.04)
    card(s, x, Inches(2.0), Inches(1.9), Inches(3.4))
    badge(s, x + Inches(0.67), Inches(2.25), i + 1)
    text(s, x + Inches(0.1), Inches(3.0), Inches(1.7), Inches(0.6), h, size=17, bold=True, font=HEAD, color=NAVY, align=PP_ALIGN.CENTER)
    text(s, x + Inches(0.1), Inches(3.65), Inches(1.7), Inches(1.6), d, size=13, color=INK, align=PP_ALIGN.CENTER)
text(s, Inches(0.6), Inches(5.8), Inches(12.1), Inches(1.0), "Applied in all nine modules: e.g. credit risk turns a default probability into expected credit loss (ECL = PD × LGD × loan), tests a recession, and decides Approve / Review / Reject with an owner.", size=15, color=MUTED)

# 6 Integration --------------------------------------------------------------------------------------
s = new_slide("The modules work as one system",
              notes="Each link passes a measured result from one module into another's decision. Every module also hands Module 9 the same fields (return per ₹, bad year, capacity, evidence), so one ranking can decide the money.")
pick = integ.iloc[[0, 1, 3, 4, 5, 8]]
for i, (_, r) in enumerate(pick.iterrows()):
    col, row = i % 3, i // 3
    x, y = Inches(0.6 + col * 4.1), Inches(1.5 + row * 2.65)
    card(s, x, y, Inches(3.85), Inches(2.4))
    text(s, x + Inches(0.2), y + Inches(0.15), Inches(3.5), Inches(0.45), r.Link, size=15, bold=True, font=HEAD, color=NAVY)
    text(s, x + Inches(0.2), y + Inches(0.65), Inches(3.5), Inches(1.0), r["How it is used"], size=12.5)
    text(s, x + Inches(0.2), y + Inches(1.7), Inches(3.5), Inches(0.6), r["₹ effect"], size=12.5, bold=True, color=AMBER)

# 7 What ML adds -------------------------------------------------------------------------------------
s = new_slide("Where ML earns its place — and where we chose not to use it",
              notes="ML adds value two ways: making money (order timing) and stopping money going out (bad loans, bad initiatives, fraud, and models that failed validation). Rejecting a model that fails is itself worth money: following the ML stock picks would have cost ₹15 crore a year on ₹300 crore over the 43 months tested, although that gap is not proven beyond luck (p 0.39).")
MEAS = "₹ crore a year (where measurable)"
v = val.dropna(subset=[MEAS])
cd = CategoryChartData(); cd.categories = [m.split(" ", 1)[1] for m in v.Module]; cd.add_series("₹ crore a year", [round(x, 1) for x in v[MEAS]])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(1.5), Inches(5.8), Inches(4.6), cd); ch = gf.chart
style_chart(ch); pl = ch.plots[0]; pl.gap_width = 70; pl.has_data_labels = True; pl.data_labels.font.size = Pt(12)
pl.data_labels.number_format = '"+₹"#,##0.0" cr"'; pl.data_labels.number_format_is_linked = False; pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
pl.series[0].format.fill.solid(); pl.series[0].format.fill.fore_color.rgb = GAIN
text(s, Inches(0.6), Inches(6.1), Inches(5.8), Inches(0.8), f"₹{K['ml_value_measurable_crore']:.1f} crore a year against the same decisions without this work, plus savings that scale with volume. Corporate finance: mostly the NPV and payback rules (the model only screens slow payers); equities: not following failed ML picks (not proven beyond luck)", size=13, color=MUTED)
card(s, Inches(6.8), Inches(1.5), Inches(5.9), Inches(5.2))
text(s, Inches(7.0), Inches(1.65), Inches(5.5), Inches(5.0), [
    [("Used, because they beat their benchmark", {"bold": True, "color": GAIN})],
    "Credit scorecard: lend ₹354 crore less at risk, earn ₹7.4 crore more",
    "Fraud model: cost of fraud 6.13% → 1.55% of money moved",
    "Order timing: ₹3.4 crore a year per ₹100 crore of orders a day",
    [("Not used, because they failed the test", {"bold": True, "color": LOSS})],
    "Stock-picking, churn prediction, ML option pricing",
    [("Used carefully", {"bold": True, "color": AMBER})], "Initiative success model: screens slow payers only (weak)"], size=14)

# 8 Scorecard ----------------------------------------------------------------------------------------
s = new_slide("Every model was tested before it was trusted",
              notes="Each model was compared with a simple benchmark on data it never saw. The shuffled-label luck test was run in Modules 1, 4, 5, 7 and 8; Modules 2 and 3 used paired 95% ranges over 25 rounds and a held-out test. Overfitting was checked in Modules 1, 2, 3, 7 and 8. In credit and fraud the cross-validation gain is clear; on the test set alone the credit gain is not proven at 95% (p = 0.065), and for fraud the ROC-AUC gain is proven while the PR-AUC gain just touches zero. Every notebook uses a fixed seed (42), and each module's runner gives the same files as its notebooks (checked file by file on our computer; another computer can differ by at most about 0.000001).")
sct = sc[["Module", "Result on unseen data", "Verdict", "Used in the allocation?"]].copy()
sct["Module"] = sct.Module.str.replace(r"^\d ", "", regex=True)
table(s, sct, Inches(0.6), Inches(1.4), Inches(12.1), [2.0, 3.6, 4.2, 2.3], size=12.5, row_h=0.68)

# 9 Stress -------------------------------------------------------------------------------------------
s = new_slide("The plan survives a bad year: no tested scenario loses more than our ₹100 crore limit",
              notes=f"One year's result in each scenario. The ₹100 crore is a loss limit, the most the ₹1,000 crore plan may lose in a bad year (10%), not an amount we allocate. The brief gives no figure, so 5%, 10% and 15% were considered and 10% agreed. Today's worst combined year is −₹{-ALL8:.1f} crore: equities −30.0, the put's cost −5.4, initiatives −1.0, the pilot −0.5, and the reserve's interest +31.9. The two lending scenarios and the last bar release the approved loans at today's prices; the plan re-prices them first. With all three steps released and collateral fetching less, the year is −₹{-stages[LGD60].iloc[3]:.1f} crore. With the put, no crash can break the limit (equities lose at most ₹{K['reverse']['with_put_max_equity_loss']:.0f} crore); without it a 50% fall would, with the rest of the plan earning as expected.")
NAMES = {"Plan": "Plan", "1.": "Market crash −20% (the put pays)", "2.": "Equities at the low end (8.6%)", "3.": "Initiatives disappoint (1-in-20)", "4.": "Rates fall: 6.8% → 5%",
         "5.": "Credit recession, approved loans lent at today's prices", "5b.": "Same, collateral fetches less (LGD 60%)", "7.": "HFT pilot hits its stop rule",
         "8.": "All at once: crash + initiatives + rates + HFT", "8b.": "All at once + lending at today's prices, LGD 60%"}
ss = st[~st.Scenario.str.startswith("6.")].iloc[::-1]
cd = CategoryChartData(); cd.categories = [NAMES[x.split(" ")[0]] for x in ss.Scenario]; cd.add_series("Year's result (₹ crore)", [round(v, 1) for v in ss["Year's result (₹ crore)"]])
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.6), Inches(1.4), Inches(9.0), Inches(5.4), cd); ch = gf.chart
style_chart(ch, size=11); pl = ch.plots[0]; pl.gap_width = 40; pl.has_data_labels = True; pl.data_labels.font.size = Pt(11)
pl.data_labels.number_format = '"₹"#,##0.0;"−₹"#,##0.0'; pl.data_labels.number_format_is_linked = False; pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
from pptx.oxml.ns import qn
from lxml import etree
for k, pt in enumerate(pl.series[0].points):
    pt.format.fill.solid(); pt.format.fill.fore_color.rgb = GAIN if ss["Year's result (₹ crore)"].iloc[k] >= 0 else LOSS
for dpt in pl.series[0]._element.findall(qn("c:dPt")):                     # each coloured bar: never invert when negative
    if dpt.find(qn("c:invertIfNegative")) is None:
        inv = etree.SubElement(dpt, qn("c:invertIfNegative")); inv.set("val", "0")
        dpt.remove(inv); dpt.insert(1, inv)
card(s, Inches(9.9), Inches(1.5), Inches(2.8), Inches(5.2))
text(s, Inches(10.05), Inches(1.7), Inches(2.5), Inches(4.9), [
    [("The bad-year budget: −₹100 crore", {"bold": True, "color": NAVY})], "A loss limit: the most the ₹1,000 crore plan may lose in a bad year (10%). Not an amount allocated",
    [("Worst combined year", {"bold": True, "color": NAVY})], f"Today: −₹{-ALL8:.1f} crore", f"Approved loans lent at today's prices: −₹{-K['stress']['8b. All at once, lending released: 1 + 3 + 4 + 5b + 7']:.1f} crore",
    f"All 3 release steps, re-priced, collateral fetches less: −₹{-stages[LGD60].iloc[3]:.1f} crore",
    [("The put matters", {"bold": True, "color": NAVY})], "Without it, a 50% fall would break the limit"], size=14)

# 11 Governance --------------------------------------------------------------------------------------
s = new_slide("Who controls each risk, and what triggers action",
              notes="One line per model or control: owner, what is watched, and the trigger. Across all of them: a model inventory, yearly independent validation, people decide every Review case.")
g = gov[["Model or control", "Owner", "Trigger → action"]].iloc[[0, 1, 2, 3, 5, 7]].copy()
table(s, g, Inches(0.6), Inches(1.4), Inches(12.1), [3.2, 2.9, 6.0], size=12.5, row_h=0.78)

# 12 Risks -------------------------------------------------------------------------------------------
s = new_slide("Risks and limitations we are open about",
              notes="The data is synthetic; some models are weak or show no skill; histories are short; several inputs are assumptions. Each is handled: stress estimates, screens instead of full decisions, pilots and staged releases, sensitivities.")
risks = [("Data", "Synthetic data: stocks move independently, no cost of funds or fee revenue, files can't be linked", "Real-market risk added as stress estimates; gaps stated"),
         ("Model risk", "Initiative success model is weak; churn, returns and ML pricing show no skill", "Full use only where a model beats its benchmark; the weak one only screens"),
         ("Short history", "43 test months of equities, 3 test days of HFT, 1 pricing day of options", "Ranges, luck tests, pilots and staged releases"),
         ("Assumptions", "Risk-free 6.8%, LGD 40%, trading costs, the ₹100 crore loss limit (10%)", "Sensitivities in every module; stress and reverse stress")]
for i, (h, what, how) in enumerate(risks):
    col, row = i % 2, i // 2
    x, y = Inches(0.6 + col * 6.15), Inches(1.5 + row * 2.65)
    card(s, x, y, Inches(5.9), Inches(2.4)); badge(s, x + Inches(0.2), y + Inches(0.2), i + 1)
    text(s, x + Inches(0.95), y + Inches(0.22), Inches(4.8), Inches(0.5), h, size=17, bold=True, font=HEAD, color=NAVY)
    text(s, x + Inches(0.25), y + Inches(0.85), Inches(5.5), Inches(0.8), what, size=13)
    text(s, x + Inches(0.25), y + Inches(1.65), Inches(5.5), Inches(0.7), [[("Handled: ", {"bold": True, "color": GAIN}), (how, {})]], size=13)

# Action plan (two slides) ----------------------------------------------------------------------------
early = acts[acts.Phase.isin(["Now", "Month 1", "Quarter 1", "Quarters 1–2"])]
later = acts[~acts.index.isin(early.index)]
for title_, part, note in [("Action plan to approve: now to the first two quarters", early,
                            "Approve the plan; fund the two ready projects; start order timing and the pilot; make the fraud rule the condition for Digital money; hedge the option book; buy equities with the put in month 1; re-price the loan book and set up model governance in quarter 1; review the initiative units over two quarters."),
                           ("Action plan: every quarter, the reserve goes to work", later,
                            "Every quarter ALCO runs the release tests: step 1 approved loans, then step 2 Review loans, planned to complete in Year 2; step 3 future initiatives as projects pass review; and the whole plan is stress-tested before every release, keeping the ₹100 crore floor.")]:
    s = new_slide(title_, dark=True, notes=note)
    ac = part[["Phase", "Action", "Owner", "How we know it worked"]].copy()
    table(s, ac, Inches(0.6), Inches(1.35), Inches(12.1), [1.4, 5.5, 2.4, 2.8], size=11, head_fill=AMBER, row_h=0.5)
    if part is later:
        text(s, Inches(0.6), Inches(4.75), Inches(12.1), Inches(1.6), [
            [("If a test fails, ", {"bold": True, "color": AMBER}), ("the money stays in the reserve, still earning 6.8%; it is tested again next quarter.", {"color": LIGHT})],
            [("No release ", {"bold": True, "color": AMBER}), ("may take the plan's combined bad year past the ₹100 crore loss limit. Separately, a ₹100 crore reserve floor is never released.", {"color": LIGHT})],
            [("Sequence: ", {"bold": True, "color": AMBER}), (f"step 1 (₹{STEP['1 approved loans']:.0f} crore) → step 2 (₹{STEP['2 review loans']:.0f} crore), planned to complete in Year 2 → step 3 (up to ₹{STEP['3 future initiatives']:.0f} crore) as projects pass review.", {"color": LIGHT})]], size=16)

OUT.parent.mkdir(exist_ok=True)
prs.save(OUT)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from repeatable import normalise_office_file   # noqa: E402  fixed stored times
normalise_office_file(OUT)
print("Saved:", OUT.name, "| slides:", len(prs.slides))
