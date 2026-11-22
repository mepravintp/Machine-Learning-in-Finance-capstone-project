"""NovaFin Module Guide: one page per module, told as a story with charts (HTML with tabs + PDF).

Layout of every module page:
  header (question, one-line answer, verdict) -> pipeline strip (Data -> ML -> Metric -> Risk -> Decision)
  -> four story panels (chart + one-line headline each) -> "So what for the Board" -> link to the notebook.
Technical detail stays in the notebooks; this guide only tells the story.

Run:  C:/Users/pravi/anaconda3/python.exe tools/make_module_guide.py
"""
import base64, io, json, subprocess
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"; OUT.mkdir(exist_ok=True)
RES = ROOT / "results"
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
NB_LINK = "../notebooks/{}"                      # relative link from deliverables/ to the notebooks

# ---------------------------------------------------------------------------------------------------------------
# Chart style: one simple message per chart
# ---------------------------------------------------------------------------------------------------------------
NAVY, TEAL, GREY, AMBER, RED = "#0f3d5c", "#2a9d8f", "#c3ccd3", "#e9c46a", "#e76f51"
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.spines.left": False, "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlecolor": NAVY,
                     "axes.titlelocation": "left", "xtick.color": "#44525e", "ytick.color": "#44525e"})

def fig_to_img(fig):
    """Matplotlib figure -> embedded <img> (base64 PNG)."""
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=170, bbox_inches="tight"); plt.close(fig)
    return f'<img src="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}">'

def hbar(labels, values, colors, fmt, xlabel="", ref=None, ref_label="", title=""):
    """Horizontal bar chart with value labels and a heading saying what is plotted."""
    fig, ax = plt.subplots(figsize=(4.3, 2.3))
    if title: ax.set_title(title, pad=10)
    y = np.arange(len(labels))[::-1]
    ax.barh(y, values, color=colors, height=0.62)
    for yi, v in zip(y, values):
        ax.text(v + max(values) * 0.02, yi, fmt(v), va="center", fontsize=9, color=NAVY, fontweight="bold")
    ax.set_yticks(y); ax.set_yticklabels(labels); ax.set_xticks([]); ax.set_xlabel(xlabel, color="#5b6b78")
    if ref is not None:
        ax.axvline(ref, color=RED, ls="--", lw=1); ax.text(ref, -0.85, ref_label, color=RED, fontsize=8, ha="center", va="top")
    ax.set_xlim(0, max(values) * 1.25)
    return fig

def funnel(stages, values, highlight=-1, title="", color=None):
    """Funnel as horizontal bars: how many survive each step."""
    color = color or NAVY
    fig, ax = plt.subplots(figsize=(4.3, 2.25))
    if title: ax.set_title(title, pad=10)
    mx = max(values); y = np.arange(len(values))[::-1]
    for i, (s, v, yi) in enumerate(zip(stages, values, y)):
        last = i == (len(values) + highlight) % len(values)
        ax.barh(yi, max(v, mx * 0.012), color=color, alpha=1.0 if last else 0.35 + 0.12 * i, height=0.66)
        ax.text(max(v, mx * 0.012) + mx * 0.02, yi, f"{v:,}  {s}", va="center", fontsize=8.6, color="#2b3a46",
                fontweight="bold" if last else "normal")
    ax.set_xlim(0, mx * 1.85); ax.axis("off")
    return fig

def columns(labels, values, color, fmt, title="", highlight=0):
    """Vertical column chart (THE DATA perspective): compare groups."""
    fig, ax = plt.subplots(figsize=(4.3, 2.15))
    if title: ax.set_title(title, pad=10)
    x = np.arange(len(labels))
    ax.bar(x, values, color=[color if i == highlight else GREY for i in range(len(values))], width=0.55)
    for xi, v in zip(x, values):
        ax.text(xi, v + max(values) * 0.03, fmt(v), ha="center", fontweight="bold", color="#1d2a35")
    ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_yticks([]); ax.set_ylim(0, max(values) * 1.22)
    ax.spines["bottom"].set_color("#c3ccd3")
    return fig

def dots(labels, values, color, ref, ref_label, title="", lo=0.3, hi=0.8):
    """Dot / lollipop chart on a score scale with a reference line (THE MODEL perspective)."""
    fig, ax = plt.subplots(figsize=(4.3, 2.15))
    if title: ax.set_title(title, pad=10)
    y = np.arange(len(labels))[::-1]
    ax.axvline(ref, color="#9aa6b0", ls="--", lw=1)
    ax.text(ref, -0.75, ref_label, color="#6b7883", fontsize=8, ha="center", va="top")
    for i, (yi, v) in enumerate(zip(y, values)):
        c = color if i == 0 else "#b9b0cc"
        ax.hlines(yi, ref, v, color=c, lw=2); ax.plot(v, yi, "o", ms=9, color=c)
        ax.text(v + (0.015 if v >= ref else -0.015), yi, f"{v:.2f}", va="center", ha="left" if v >= ref else "right",
                fontweight="bold", color="#1d2a35", fontsize=8.6)
    ax.set_yticks(y); ax.set_yticklabels(labels); ax.set_xlim(lo, hi); ax.set_ylim(-0.6, len(labels) - 0.4)
    ax.spines["bottom"].set_visible(False); ax.set_xticks([])          # values are printed on the dots
    return fig

def line_sens(xs, ys, color, xlabel, title="", extra=None, base_x=None):
    """Line chart of an outcome against an assumption (THE RISK perspective); extra = (label, value) stress marker."""
    fig, ax = plt.subplots(figsize=(4.3, 2.15))
    if title: ax.set_title(title, pad=10)
    ax.plot(xs, ys, "-o", color=color, lw=2.2, ms=7)
    for x, v in zip(xs, ys):
        ax.text(x, v + max(ys) * 0.07, f"{v}" + (" (base)" if x == base_x else ""), ha="center", fontweight="bold", color="#1d2a35")
    if extra:
        ax.plot(base_x, extra[1], "D", ms=7, mfc="white", mec=color, mew=2)
        ax.annotate(extra[0], (base_x, extra[1]), xytext=(12, -4), textcoords="offset points", fontsize=8, color="#6b4b00")
    ax.set_xticks(xs); ax.set_xticklabels([f"{x} yrs" for x in xs]); ax.set_xlabel(xlabel, color="#5b6b78")
    ax.set_yticks([]); ax.set_ylim(-max(ys) * 0.12, max(ys) * 1.3); ax.spines["bottom"].set_color("#c3ccd3")
    return fig

# Four perspectives, each with its own colour and chart type, repeated on every module page
PERSPECTIVES = {
    "data":  ("THE DATA", "what history shows", "#2a6f97", "#eaf2f8"),
    "model": ("THE MODEL", "what ML can predict", "#7b5ea7", "#f2edf8"),
    "money": ("THE MONEY", "what is worth funding", "#2a9d8f", "#e8f5f2"),
    "risk":  ("THE RISK", "what could change the answer", "#d9822b", "#fcf1e6"),
}

# ---------------------------------------------------------------------------------------------------------------
# Page building blocks
# ---------------------------------------------------------------------------------------------------------------
def pipeline(steps):
    """Data -> ML -> Metric -> Risk -> Decision strip. steps = [(label, value, note), ...]"""
    cells = "".join(f'<div class="step"><div class="slabel"><span class="snum">{i + 1}</span>{l}</div><div class="svalue">{v}</div><div class="snote">{n}</div></div>'
                    + ('<div class="arrow">➜</div>' if i < len(steps) - 1 else "") for i, (l, v, n) in enumerate(steps))
    return f'<div class="pipetitle">How we got there, step by step</div><div class="pipe">{cells}</div>'

def panel(kind, headline, chart_html, caption):
    """One story panel in a perspective colour: tag + headline (message) + chart + caption."""
    tag, sub, color, tint = PERSPECTIVES[kind]
    return (f'<div class="panel" style="border-top:5px solid {color}">'
            f'<div class="phead" style="background:{tint}"><div class="ptag" style="color:{color}">{tag} · <span>{sub}</span></div>'
            f'<div class="pmsg">{headline}</div></div>'
            f'<div class="pchart">{chart_html}</div><div class="pcap">{caption}</div></div>')

def page(code, title, question, answer, verdict, verdict_cls, steps, panels, so_what, notebook, sections, brief_tasks):
    sw = "".join(f"<li>{s}</li>" for s in so_what)
    tasks = " · ".join(f'<span class="task">{t}</span>' for t in brief_tasks)
    return f"""
<div class="mod">
  <div class="mhead">
    <div><div class="mcode">{code}</div><h2>{title}</h2></div>
    <div class="verdict {verdict_cls}">{verdict}</div>
  </div>
  <div class="qa"><div class="q"><b>What the Board needs decided</b>{question}</div><div class="ans"><b>Our answer</b>{answer}</div></div>
  <div class="brief">Brief asked: {tasks}</div>
  <div class="more">Technical detail → <a href="{NB_LINK.format(notebook)}">{notebook}</a> · {sections}</div>
  {pipeline(steps)}
  <div class="grid">{''.join(panels)}</div>
  <div class="sowhat"><b>So what for the Board</b><ul>{sw}</ul></div>
</div>"""

# ---------------------------------------------------------------------------------------------------------------
# MODULE 1: Strategic initiatives
# ---------------------------------------------------------------------------------------------------------------
def module1():
    init = pd.read_csv(ROOT / "data" / "strategic_initiatives.csv")
    j = json.loads((RES / "Module_01_Strategic_Initiatives" / "initiatives.json").read_text(encoding="utf-8"))
    dec = pd.read_csv(RES / "Module_01_Strategic_Initiatives" / "initiatives_decisions.csv")
    alloc = json.loads((RES / "Module_09_Integrated_Allocation" / "allocation.json").read_text(encoding="utf-8"))
    funded = alloc["funded_initiatives"]

    # Panel 1: what the data said: success by risk rating
    rr = init.groupby("Risk_Rating").Historical_Success.mean().reindex(["Low", "Medium", "High"])
    c1 = fig_to_img(columns([f"{k} risk" for k in rr.index], rr.values * 100, PERSPECTIVES["data"][2],
                            lambda v: f"{v:.0f}%", title="Share of past projects that succeeded, by risk rating"))
    # Panel 2: what ML could do: simple beats complex
    cv = j["model"]["cv_table"]
    names = ["Logistic (3 drivers)", "Logistic regression", "Gradient boosting", "Random forest"]
    labels = ["Logistic, 3 drivers", "Logistic, all features", "Gradient boosting", "Random forest"]
    c2 = fig_to_img(dots(labels, [cv[n]["ROC-AUC mean"] for n in names], PERSPECTIVES["model"][2], 0.5, "coin flip = 0.50",
                         title="Prediction score of each model (ROC-AUC, 1.0 = perfect)", lo=0.38, hi=0.72))
    # Panel 3: turning it into money: the decision funnel
    n_npv = int((dec.NPV > 0).sum()); n_enpv = int((dec.ENPV > 0).sum()); n_fund = int((dec.Decision == "Fund").sum())
    c3 = fig_to_img(funnel(["initiatives proposed", "NPV > 0 (5 years)", "value after failure risk", "Fund list", "funded in final ₹1,000 cr"],
                           [len(dec), n_npv, n_enpv, n_fund, len(funded)], title="How many projects pass each test",
                           color=PERSPECTIVES["money"][2]))
    # Panel 4: how robust: the key assumption
    sens = j["sensitivity"]
    life = [int(sens["Life 3 years"]["Fund"]), int(sens["Base (5y, 12%, base loss)"]["Fund"]), int(sens["Life 7 years"]["Fund"])]
    stress = int(sens["Model stress: P(success) -10pp"]["Fund"])
    c4 = fig_to_img(line_sens([3, 5, 7], life, PERSPECTIVES["risk"][2], "assumed project life",
                              title="Projects on the Fund list vs assumed project life", base_x=5,
                              extra=(f"{stress} if success odds −10 pts", stress)))

    funded_cr = dec[dec.Initiative_ID.isin(funded)].Initial_Investment.sum()
    panels = [
        panel("data", "Low risk rating = clearest sign of success", c1,
              "Low-risk initiatives succeeded 89% of the time vs ~70% for the rest. Investment size, GDP and rates showed no link."),
        panel("model", "Simple beats complex, but prediction is weak", c2,
              "With just 42 failures, flexible models memorise noise. A 3-variable logistic model is best, but AUC 0.63 is modest, so ML is a risk check, not a picker."),
        panel("money", "Finance does the filtering: 180 → 5", c3,
              f"NPV over 5 years at 12%, minus the loss if a project fails, ranked by value per rupee. The Fund list's realised success is 86% vs 76% for rejects."),
        panel("risk", "It all depends on how long projects earn", c4,
              "Over 3 years nothing pays back; over 7 years the list doubles. Cutting every success odds by 10 points still leaves 12 good projects."),
    ]
    return page(
        code="MODULE 1 · CORPORATE FINANCE", title="Which strategic initiatives should get capital?",
        question="For each of the <b>180 proposed projects</b>: should NovaFin <b>Fund</b>, <b>Review</b> or <b>Reject</b> it, and why?",
        answer=f"<b>Fund 21</b>, Review 18, Reject 141. Of the 21, the <b>best 5 get ₹{funded_cr:.0f} cr</b> in the final ₹1,000 cr plan (all low-risk, at least 90% chance of success).",
        verdict="ML weak · NPV decides", verdict_cls="amber",
        steps=[("Started with", "180 past projects", "77% of them succeeded"),
               ("ML predicted", "Chance of success", "a modest predictor (score 0.63 out of 1)"),
               ("Money test", f"{n_fund} pass", "worth more than they cost, even allowing for failure"),
               ("Stress test", "12 still pass", "if every chance of success is 10 points lower"),
               ("Decision", f"5 funded · ₹{funded_cr:.0f} cr", "best value per rupee in the ₹1,000 cr plan")],
        panels=panels,
        so_what=["<b>Fund on value, not on model scores.</b> NPV does the filtering; the model only adjusts for failure risk.",
                 "<b>Ask for a Low risk rating and a growing segment.</b> They are the only traits that reliably raise success odds.",
                 "<b>Release money in stages.</b> The value relies on projects earning in years 4–5, so stop funding if a project falls behind plan."],
        notebook="01_strategic_initiatives.ipynb",
        sections="§1 EDA · §3 model comparison · §5 SHAP · §6 NPV · §7 decision rule · §8 sensitivity",
        brief_tasks=["EDA of investment, ROI, risk, units", "predict success + explain drivers", "NPV, expected NPV, Fund / Review / Reject"])

# ---------------------------------------------------------------------------------------------------------------
# Overview tab: how to read + the ML scorecard
# ---------------------------------------------------------------------------------------------------------------
OVERVIEW = """
<div class="mod">
  <div class="mhead"><div><div class="mcode">NOVAFIN CAPSTONE · MODULE GUIDE</div><h2>One page per module, told as a story</h2></div></div>
  <p class="lead">Each page answers one Board question in the same order:
  <b>question → answer → how we got there (Data → ML → Metric → Risk → Decision) → four charts that build the story → so what</b>.
  Technical detail lives in the linked notebook.</p>
  <table class="score"><tr><th>Module</th><th>Board question</th><th>ML verdict</th><th>Decision</th></tr>
  <tr><td>M1 Initiatives</td><td>Which projects to fund?</td><td><span class="verdict amber">ML weak · NPV decides</span></td><td>5 funded · ₹487 cr</td></tr>
  <tr><td>M2 Credit</td><td>Which loans to approve?</td><td><span class="verdict green">ML useful</span></td><td>Approve 836 · ECL 2.8%</td></tr>
  <tr><td>M3 Fraud</td><td>Which transactions to check?</td><td><span class="verdict green">ML useful</span></td><td>38% lower cost</td></tr>
  <tr><td>M4 Churn &amp; CLV</td><td>Whom should RMs call?</td><td><span class="verdict red">No churn signal</span></td><td>value-led list · net ₹23 lakh</td></tr>
  <tr><td>M5–6 Equity</td><td>Can ML pick stocks?</td><td><span class="verdict red">Not significant</span></td><td>equal-weight · ₹250 cr</td></tr>
  <tr><td>M7 HFT</td><td>Can the order book be traded?</td><td><span class="verdict amber">Signal real · profit fragile</span></td><td>₹10 cr pilot</td></tr>
  <tr><td>M8 Derivatives</td><td>Can ML price options?</td><td><span class="verdict red">Black-Scholes wins</span></td><td>hedge · ₹20 cr buffer</td></tr>
  <tr><td>Liquidity</td><td>How much cash to keep?</td><td><span class="verdict grey">Stress test</span></td><td>₹175 cr reserve</td></tr>
  <tr><td>M9 Allocation</td><td>Where does ₹1,000 cr go?</td><td><span class="verdict green">Integrated</span></td><td>16.5% return · stress ₹116 cr</td></tr></table>
</div>"""

SECTIONS = [("overview", "Overview", OVERVIEW), ("m1", "M1 Initiatives", module1()),
            ("m2", "M2 Credit", None), ("m3", "M3 Fraud", None), ("m4", "M4 Churn & CLV", None), ("m5", "M5 Equity", None),
            ("m6", "M6 Portfolio", None), ("m7", "M7 HFT", None), ("m8", "M8 Derivatives", None),
            ("liq", "Liquidity", None), ("m9", "M9 Allocation", None)]
PENDING = '<div class="mod"><h2>{}</h2><p class="lead">This page will follow the Module 1 story layout once that layout is approved.</p></div>'

CSS = """
@page { size: A4; margin: 8mm 10mm 7mm; }
* { box-sizing: border-box; }
body { font-family: 'Segoe UI', Arial, sans-serif; color: #1d2a35; margin: 0; background: #eef2f5; font-size: 10pt; }
.wrap { max-width: 980px; margin: 0 auto; padding: 0 16px 30px; }
.mod { background: #fff; border-radius: 8px; padding: 16px 20px 12px; margin: 14px 0; box-shadow: 0 1px 6px rgba(0,0,0,.08); }
.mhead { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; border-bottom: 3px solid #2a9d8f; padding-bottom: 6px; }
.mcode { font-size: 8.5pt; letter-spacing: .08em; color: #2a9d8f; font-weight: 700; }
h2 { margin: 2px 0 0; font-size: 17pt; color: #0f3d5c; }
.verdict { display: inline-block; padding: 4px 10px; border-radius: 14px; font-weight: 700; font-size: 9pt; white-space: nowrap; }
.green { background: #dff3ea; color: #1f7a55; } .amber { background: #fdf0d5; color: #8a6100; }
.red { background: #fbe3df; color: #a63a2b; } .grey { background: #e7ecf0; color: #44525e; }
.qa { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 12px 0 8px; }
.qa > div { border-radius: 8px; padding: 8px 12px; font-size: 11.5pt; line-height: 1.4; }
.qa .q { background: #f4f7f9; border: 1px solid #dde4ea; color: #1d2a35; }
.qa .ans { background: #e6f5f1; border: 1px solid #bfe3d9; color: #0f3d5c; }
.qa > div > b:first-child { display: block; font-size: 8.5pt; text-transform: uppercase; letter-spacing: .07em; color: #2a9d8f; margin-bottom: 3px; }
.brief { font-size: 8.5pt; color: #5b6b78; margin: 4px 0 8px; }
.task { background: #f4f7f9; border: 1px solid #dde4ea; border-radius: 10px; padding: 1px 7px; }
.pipetitle { font-size: 8.5pt; text-transform: uppercase; letter-spacing: .07em; color: #5b6b78; font-weight: 700; margin: 6px 0 4px; }
.pipe { display: flex; align-items: stretch; gap: 3px; margin: 0 0 14px; }
.step { flex: 1; background: #f1f8f6; border: 1px solid #cfe7e0; color: #1d2a35; border-radius: 8px; padding: 6px 8px; text-align: left; }
.slabel { font-size: 8pt; color: #2a9d8f; font-weight: 700; display: flex; align-items: center; gap: 5px; }
.snum { display: inline-block; width: 15px; height: 15px; border-radius: 50%; background: #2a9d8f; color: #fff; text-align: center; font-size: 7.5pt; line-height: 15px; flex: none; }
.svalue { font-size: 11pt; font-weight: 700; color: #0f3d5c; margin: 2px 0 1px; } .snote { font-size: 8pt; color: #44525e; line-height: 1.3; }
.arrow { align-self: center; color: #9fc9bf; font-size: 13pt; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.panel { border: 1px solid #dde4ea; border-radius: 8px; padding: 0 0 9px; page-break-inside: avoid; overflow: hidden; background: #fff; }
.phead { padding: 7px 12px 7px; margin-bottom: 6px; }
.ptag { font-size: 8pt; font-weight: 800; letter-spacing: .08em; } .ptag span { font-weight: 600; letter-spacing: 0; text-transform: none; opacity: .85; }
.pmsg { font-weight: 700; color: #0f3d5c; font-size: 10.5pt; margin-top: 2px; }
.pchart { padding: 0 12px; } .panel .pcap { padding: 0 12px; }
.pnum { display: inline-block; width: 18px; height: 18px; border-radius: 50%; background: #2a9d8f; color: #fff; text-align: center;
        font-size: 8.5pt; line-height: 18px; margin-right: 6px; }
.panel img { width: 100%; display: block; }
.pcap { font-size: 8.8pt; color: #44525e; line-height: 1.4; margin-top: 8px; }
.sowhat { background: #f6f0fa; border-left: 5px solid #7b5ea7; border-radius: 6px; padding: 8px 14px 3px; margin-top: 16px; }
.sowhat b { color: #5e4387; } .sowhat ul { margin: 3px 0 4px; padding-left: 18px; } .sowhat li { margin: 2px 0; font-size: 9.5pt; }
.more { font-size: 8.5pt; color: #5b6b78; margin: 0 0 6px; } .more a { color: #2a6f97; font-weight: 600; }
.lead { font-size: 11pt; line-height: 1.5; }
table.score { border-collapse: collapse; width: 100%; font-size: 10pt; margin-top: 8px; }
table.score th { background: #0f3d5c; color: #fff; text-align: left; padding: 6px 8px; } table.score td { border-bottom: 1px solid #e3e8ec; padding: 6px 8px; }
.tabbar { position: sticky; top: 0; z-index: 10; background: #fff; border-bottom: 2px solid #0f3d5c; display: flex; flex-wrap: wrap;
          gap: 4px; padding: 8px 16px 0; justify-content: center; }
.tab { border: 1px solid #c9d3db; border-bottom: none; background: #eef2f5; color: #0f3d5c; font: 600 9.5pt 'Segoe UI', Arial, sans-serif;
       padding: 6px 11px; border-radius: 6px 6px 0 0; cursor: pointer; }
.tab:hover { background: #dfe8ee; } .tab.active { background: #0f3d5c; color: #fff; border-color: #0f3d5c; }
.tab.pending { color: #8a97a2; font-weight: 400; } .tab.pending::after { content: " · pending"; font-size: 8pt; }
.section { display: none; } .section.active { display: block; }
@media print {
  body { background: #fff; } .wrap { padding: 0; max-width: none; } .tabbar { display: none !important; }
  .section { display: block !important; page-break-after: always; } .section.is-pending { display: none !important; }
  .mod { box-shadow: none; margin: 0; padding: 0; border-radius: 0; zoom: .9; }
  .grid { gap: 11px; } .pipe { margin-bottom: 10px; } .sowhat { margin-top: 11px; }
}
"""
JS = """<script>
(function () {
  var tabs = document.querySelectorAll('.tab'), secs = document.querySelectorAll('.section');
  function show(id) {
    if (!document.getElementById('sec-' + id)) id = 'overview';
    secs.forEach(function (s) { s.classList.toggle('active', s.dataset.id === id); });
    tabs.forEach(function (t) { t.classList.toggle('active', t.dataset.target === id); });
    if (history.replaceState) history.replaceState(null, '', '#' + id);
    window.scrollTo(0, 0);
  }
  tabs.forEach(function (t) { t.addEventListener('click', function () { show(t.dataset.target); }); });
  show((location.hash || '#overview').slice(1));
})();
</script>"""
tabs = "".join(f'<button class="tab{"" if b else " pending"}" data-target="{s}">{l}</button>' for s, l, b in SECTIONS)
secs = "".join(f'<section class="section{"" if b else " is-pending"}" id="sec-{s}" data-id="{s}">{b if b else PENDING.format(l)}</section>'
               for s, l, b in SECTIONS)
html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>NovaFin Module Guide</title><style>{CSS}</style></head><body><nav class="tabbar">{tabs}</nav>'
        f'<div class="wrap">{secs}</div>{JS}</body></html>')
(OUT / "NovaFin_Module_Guide.html").write_text(html, encoding="utf-8")

dst, tmp = OUT / "NovaFin_Module_Guide.pdf", OUT / "_tmp_NovaFin_Module_Guide.pdf"
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={tmp.resolve()}", (OUT / "NovaFin_Module_Guide.html").resolve().as_uri()],
               capture_output=True, text=True, timeout=180)
try:
    tmp.replace(dst); print("updated:", "NovaFin_Module_Guide.html", "and", dst.name)
except PermissionError:
    print(dst.name, "NOT updated: close it in your viewer and run again (new copy left as", tmp.name + ")")
