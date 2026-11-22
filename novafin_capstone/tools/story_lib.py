"""Building blocks for the story-format report: charts (one per perspective), story page, method card, CSS.

Four perspectives repeat on every module page, each with its own colour:
  THE DATA (blue) · THE MODEL (purple) · THE MONEY (teal) · THE RISK (orange)
"""
import base64, io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import markdown

GREY = "#c3ccd3"
PERSPECTIVES = {
    "data":  ("THE DATA", "what history shows", "#2a6f97", "#eaf2f8"),
    "model": ("THE MODEL", "what ML can predict", "#7b5ea7", "#f2edf8"),
    "money": ("THE MONEY", "what is worth doing", "#2a9d8f", "#e8f5f2"),
    "risk":  ("THE RISK", "what could change the answer", "#d9822b", "#fcf1e6"),
}
C = {k: v[2] for k, v in PERSPECTIVES.items()}       # colour per perspective
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.spines.left": False, "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlecolor": "#0f3d5c",
                     "axes.titlelocation": "left", "xtick.color": "#44525e", "ytick.color": "#44525e"})

def md(text):
    """Markdown -> HTML (tables, lists)."""
    return markdown.markdown(text, extensions=["tables", "sane_lists"])

def fig_to_img(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=170, bbox_inches="tight"); plt.close(fig)
    return f'<img src="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}">'

def file_img(path):
    return f'<img src="data:image/png;base64,{base64.b64encode(open(path, "rb").read()).decode()}">'

# ---------------------------------------------------------------------------------------------------------------
# Charts: each returns an <img> tag
# ---------------------------------------------------------------------------------------------------------------
def columns(labels, values, color, fmt, title="", highlight=(0,), rotate=0, ref=None, ref_label=""):
    """Vertical columns: compare groups (default chart for THE DATA)."""
    fig, ax = plt.subplots(figsize=(4.3, 2.15))
    if title: ax.set_title(title, pad=10)
    x = np.arange(len(labels)); hi = set(highlight) if highlight is not None else set(range(len(values)))
    ax.bar(x, values, color=[color if i in hi else GREY for i in range(len(values))], width=0.6)
    top = max(max(values), ref or 0)
    for xi, v in zip(x, values):
        ax.text(xi, v + top * 0.03, fmt(v), ha="center", fontweight="bold", color="#1d2a35", fontsize=8.3)
    if ref is not None:
        ax.axhline(ref, color="#9aa6b0", ls="--", lw=1); ax.text(len(labels) - 0.5, ref, ref_label, color="#6b7883", fontsize=8, ha="right", va="bottom")
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=rotate, ha="right" if rotate else "center", fontsize=8 if rotate else 9)
    ax.set_yticks([]); ax.set_ylim(min(0, min(values) * 1.2), top * 1.25); ax.spines["bottom"].set_color(GREY)
    return fig_to_img(fig)

def dots(labels, values, color, ref, ref_label, title="", lo=None, hi=None, fmt=lambda v: f"{v:.2f}", best=0):
    """Dot chart against a reference line (default chart for THE MODEL). best = index highlighted."""
    fig, ax = plt.subplots(figsize=(4.3, 2.15))
    if title: ax.set_title(title, pad=10)
    y = np.arange(len(labels))[::-1]
    ax.axvline(ref, color="#9aa6b0", ls="--", lw=1)
    span = (hi if hi is not None else max(values + [ref])) - (lo if lo is not None else min(values + [ref]))
    for i, (yi, v) in enumerate(zip(y, values)):
        c = color if i == best else "#b9b0cc"
        ax.hlines(yi, ref, v, color=c, lw=2); ax.plot(v, yi, "o", ms=9, color=c)
        ax.text(v + (span * 0.025 if v >= ref else -span * 0.025), yi, fmt(v), va="center", ha="left" if v >= ref else "right",
                fontweight="bold", color="#1d2a35", fontsize=8.5)
    ax.text(ref, -0.75, ref_label, color="#6b7883", fontsize=8, ha="center", va="top")
    ax.set_yticks(y); ax.set_yticklabels(labels); ax.tick_params(axis="y", length=0)
    if lo is not None: ax.set_xlim(lo, hi)
    ax.set_ylim(-0.6, len(labels) - 0.4); ax.spines["bottom"].set_visible(False); ax.set_xticks([])
    return fig_to_img(fig)

def funnel(stages, values, color, title=""):
    """Funnel: how many pass each test (default chart for THE MONEY)."""
    fig, ax = plt.subplots(figsize=(4.3, 2.25))
    if title: ax.set_title(title, pad=10)
    mx = max(values); y = np.arange(len(values))[::-1]
    for i, (s, v, yi) in enumerate(zip(stages, values, y)):
        last = i == len(values) - 1
        w = max(v, mx * 0.012)
        ax.barh(yi, w, color=color, alpha=1.0 if last else 0.35 + 0.12 * i, height=0.66)
        ax.text(w + mx * 0.02, yi, f"{v:,}  {s}", va="center", fontsize=8.6, color="#2b3a46", fontweight="bold" if last else "normal")
    ax.set_xlim(0, mx * 1.85); ax.axis("off")
    return fig_to_img(fig)

def hbars(labels, values, color, fmt, title="", highlight=(0,), ref=None, ref_label=""):
    """Horizontal bars with values (alternative chart for THE MONEY)."""
    fig, ax = plt.subplots(figsize=(4.3, 2.2))
    if title: ax.set_title(title, pad=10)
    y = np.arange(len(labels))[::-1]; mx = max(abs(v) for v in values)
    ax.barh(y, values, color=[color if i in set(highlight) else GREY for i in range(len(values))], height=0.6)
    for yi, v in zip(y, values):
        ax.text(v + (mx * 0.02 if v >= 0 else -mx * 0.02), yi, fmt(v), va="center", ha="left" if v >= 0 else "right",
                fontweight="bold", color="#1d2a35", fontsize=8.5)
    if ref is not None:
        ax.axvline(ref, color="#9aa6b0", ls="--", lw=1); ax.text(ref, -0.9, ref_label, color="#6b7883", fontsize=8, ha="center", va="top")
    ax.set_yticks(y); ax.set_yticklabels(labels); ax.set_xticks([]); ax.tick_params(axis="y", length=0)
    lo = min(0, min(values)) * 1.35; ax.set_xlim(lo if lo else 0, mx * 1.3); ax.axvline(0, color=GREY, lw=0.8)
    return fig_to_img(fig)

def line(xs, ys, color, xticklabels, xlabel="", title="", base_idx=None, extra=None, hline=None, fmt=lambda v: f"{v:g}"):
    """Outcome vs an assumption (default chart for THE RISK). extra = (label, value) marker at the base point;
    hline = (value, label) limit line."""
    fig, ax = plt.subplots(figsize=(4.3, 2.15))
    if title: ax.set_title(title, pad=10)
    ax.plot(xs, ys, "-o", color=color, lw=2.2, ms=7)
    rng = (max(ys + ([hline[0]] if hline else [])) - min(ys + [0])) or 1
    for i, (x, v) in enumerate(zip(xs, ys)):
        ax.text(x, v + rng * 0.08, fmt(v) + (" (base)" if i == base_idx else ""), ha="center", fontweight="bold", color="#1d2a35", fontsize=8.5)
    if extra and base_idx is not None:
        ax.plot(xs[base_idx], extra[1], "D", ms=7, mfc="white", mec=color, mew=2)
        ax.annotate(extra[0], (xs[base_idx], extra[1]), xytext=(10, -4), textcoords="offset points", fontsize=8, color="#6b4b00")
    if hline:
        ax.axhline(hline[0], color="#b23a2b", ls="--", lw=1); ax.text(xs[-1], hline[0], hline[1], color="#b23a2b", fontsize=8, ha="right", va="bottom")
    ax.set_xticks(xs); ax.set_xticklabels(xticklabels); ax.set_xlabel(xlabel, color="#5b6b78")
    lo = min(ys + [0]); ax.set_yticks([]); ax.set_ylim(lo - rng * 0.15, max(ys + ([hline[0]] if hline else [])) + rng * 0.3)
    if lo < 0: ax.axhline(0, color=GREY, lw=0.8)
    ax.spines["bottom"].set_color(GREY)
    return fig_to_img(fig)

# ---------------------------------------------------------------------------------------------------------------
# Page parts
# ---------------------------------------------------------------------------------------------------------------
def panel(kind, headline, chart_html, caption):
    tag, sub, color, tint = PERSPECTIVES[kind]
    return (f'<div class="panel" style="border-top:5px solid {color}">'
            f'<div class="phead" style="background:{tint}"><div class="ptag" style="color:{color}">{tag} · <span>{sub}</span></div>'
            f'<div class="pmsg">{headline}</div></div><div class="pchart">{chart_html}</div><div class="pcap">{caption}</div></div>')

def pipeline(steps):
    cells = "".join(f'<div class="step"><div class="slabel"><span class="snum">{i + 1}</span>{l}</div><div class="svalue">{v}</div><div class="snote">{n}</div></div>'
                    + ('<div class="arrow">➜</div>' if i < len(steps) - 1 else "") for i, (l, v, n) in enumerate(steps))
    return f'<div class="pipetitle">How we got there, step by step</div><div class="pipe">{cells}</div>'

def story_page(code, title, question, answer, verdict, verdict_cls, steps, panels, so_what, notebook, sections, brief_tasks):
    sw = "".join(f"<li>{s}</li>" for s in so_what)
    tasks = " · ".join(f'<span class="task">{t}</span>' for t in brief_tasks)
    return f"""<div class="mod story">
  <div class="mhead"><div><div class="mcode">{code} · STORY</div><h2>{title}</h2></div><div class="verdict {verdict_cls}">{verdict}</div></div>
  <div class="qa"><div class="q"><b>What the Board needs decided</b>{question}</div><div class="ans"><b>Our answer</b>{answer}</div></div>
  <div class="brief">Brief asked: {tasks}</div>
  <div class="more">Technical detail → <a href="../notebooks/{notebook}">{notebook}</a> · {sections}</div>
  {pipeline(steps)}
  <div class="grid">{''.join(panels)}</div>
  <div class="sowhat"><b>So what for the Board</b><ul>{sw}</ul></div>
</div>"""

def method_card(code, title, input_prep, validation, comparison, financial, assumptions, code_ptr):
    """Second page per module: the methodology for examiners and technical readers."""
    return f"""<div class="mod method">
  <div class="mhead"><div><div class="mcode">{code} · METHOD</div><h2>{title}: how it was done</h2></div></div>
  <div class="mgrid">
    <div class="mbox"><div class="mtitle">Input &amp; preparation</div>{md(input_prep)}</div>
    <div class="mbox"><div class="mtitle">Validation design</div>{md(validation)}</div>
    <div class="mbox wide"><div class="mtitle">Model comparison: what each choice gained</div>{md(comparison)}</div>
    <div class="mbox"><div class="mtitle">Financial layer</div>{md(financial)}</div>
    <div class="mbox"><div class="mtitle">Assumptions &amp; sensitivity</div>{md(assumptions)}</div>
    <div class="mbox wide code"><div class="mtitle">Code &amp; outputs</div>{md(code_ptr)}</div>
  </div>
</div>"""

CSS = """
@page { size: A4; margin: 8mm 10mm 7mm; }
* { box-sizing: border-box; }
body { font-family: 'Segoe UI', Arial, sans-serif; color: #1d2a35; margin: 0; background: #eef2f5; font-size: 10pt; }
.wrap { max-width: 980px; margin: 0 auto; padding: 0 16px 30px; }
.mod { background: #fff; border-radius: 8px; padding: 16px 20px 12px; margin: 14px 0; box-shadow: 0 1px 6px rgba(0,0,0,.08); }
.mhead { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; border-bottom: 3px solid #2a9d8f; padding-bottom: 6px; }
.mcode { font-size: 8.5pt; letter-spacing: .08em; color: #2a9d8f; font-weight: 700; }
h2 { margin: 2px 0 0; font-size: 17pt; color: #0f3d5c; } h3 { color: #0f3d5c; margin: 12px 0 4px; }
.verdict { display: inline-block; padding: 4px 10px; border-radius: 14px; font-weight: 700; font-size: 9pt; white-space: nowrap; }
.green { background: #dff3ea; color: #1f7a55; } .amber { background: #fdf0d5; color: #8a6100; }
.red { background: #fbe3df; color: #a63a2b; } .grey { background: #e7ecf0; color: #44525e; }
.qa { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 12px 0 8px; }
.qa > div { border-radius: 8px; padding: 8px 12px; font-size: 11.5pt; line-height: 1.4; }
.qa .q { background: #f4f7f9; border: 1px solid #dde4ea; } .qa .ans { background: #e6f5f1; border: 1px solid #bfe3d9; color: #0f3d5c; }
.qa > div > b:first-child { display: block; font-size: 8.5pt; text-transform: uppercase; letter-spacing: .07em; color: #2a9d8f; margin-bottom: 3px; }
.brief { font-size: 8.5pt; color: #5b6b78; margin: 4px 0 4px; } .task { background: #f4f7f9; border: 1px solid #dde4ea; border-radius: 10px; padding: 1px 7px; }
.more { font-size: 8.5pt; color: #5b6b78; margin: 0 0 6px; } .more a, .mod a { color: #2a6f97; font-weight: 600; }
.pipetitle { font-size: 8.5pt; text-transform: uppercase; letter-spacing: .07em; color: #5b6b78; font-weight: 700; margin: 6px 0 4px; }
.pipe { display: flex; align-items: stretch; gap: 3px; margin: 0 0 14px; }
.step { flex: 1; background: #f1f8f6; border: 1px solid #cfe7e0; border-radius: 8px; padding: 6px 8px; }
.slabel { font-size: 8pt; color: #2a9d8f; font-weight: 700; display: flex; align-items: center; gap: 5px; }
.snum { display: inline-block; width: 15px; height: 15px; border-radius: 50%; background: #2a9d8f; color: #fff; text-align: center; font-size: 7.5pt; line-height: 15px; flex: none; }
.svalue { font-size: 11pt; font-weight: 700; color: #0f3d5c; margin: 2px 0 1px; } .snote { font-size: 8pt; color: #44525e; line-height: 1.3; }
.arrow { align-self: center; color: #9fc9bf; font-size: 13pt; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.panel { border: 1px solid #dde4ea; border-radius: 8px; padding: 0 0 9px; page-break-inside: avoid; overflow: hidden; background: #fff; }
.phead { padding: 7px 12px; margin-bottom: 6px; }
.ptag { font-size: 8pt; font-weight: 800; letter-spacing: .08em; } .ptag span { font-weight: 600; letter-spacing: 0; opacity: .85; }
.pmsg { font-weight: 700; color: #0f3d5c; font-size: 10.5pt; margin-top: 2px; }
.pchart { padding: 0 12px; } .pchart img { width: 100%; display: block; }
.pcap { font-size: 8.8pt; color: #44525e; line-height: 1.4; margin-top: 8px; padding: 0 12px; }
.sowhat { background: #f6f0fa; border-left: 5px solid #7b5ea7; border-radius: 6px; padding: 8px 14px 3px; margin-top: 16px; }
.sowhat b { color: #5e4387; } .sowhat ul { margin: 3px 0 4px; padding-left: 18px; } .sowhat li { margin: 2px 0; font-size: 9.5pt; }
.mgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px; }
.mbox { border: 1px solid #dde4ea; border-radius: 8px; padding: 8px 12px; font-size: 9.2pt; line-height: 1.42; page-break-inside: avoid; }
.mbox.wide { grid-column: 1 / -1; } .mbox p { margin: 3px 0; } .mbox ul, .mbox ol { margin: 3px 0; padding-left: 18px; }
.mtitle { font-size: 8.5pt; font-weight: 800; letter-spacing: .07em; text-transform: uppercase; color: #2a6f97; margin-bottom: 4px; }
.mbox.code { background: #f7f9fb; } .mbox code { font-family: Consolas, monospace; font-size: 8.6pt; }
table { border-collapse: collapse; width: 100%; font-size: 8.8pt; margin: 4px 0; }
th { background: #0f3d5c; color: #fff; text-align: left; padding: 4px 6px; } td { border-bottom: 1px solid #e3e8ec; padding: 3px 6px; vertical-align: top; }
.lead { font-size: 10.5pt; line-height: 1.5; }
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 10px 0; }
.kpis div { border: 1px solid #dde4ea; border-top: 4px solid #2a9d8f; border-radius: 6px; padding: 8px 10px; }
.kpis b { display: block; font-size: 17pt; color: #0f3d5c; } .kpis span { font-size: 8.8pt; color: #5b6b78; }
pre { background: #f4f7f9; border-left: 3px solid #2a9d8f; padding: 6px 9px; font-size: 8.2pt; white-space: pre-wrap; }
.tabbar { position: sticky; top: 0; z-index: 10; background: #fff; border-bottom: 2px solid #0f3d5c; display: flex; flex-wrap: wrap; gap: 4px; padding: 8px 16px 0; justify-content: center; }
.tab { border: 1px solid #c9d3db; border-bottom: none; background: #eef2f5; color: #0f3d5c; font: 600 9.3pt 'Segoe UI', Arial, sans-serif; padding: 6px 10px; border-radius: 6px 6px 0 0; cursor: pointer; }
.tab:hover { background: #dfe8ee; } .tab.active { background: #0f3d5c; color: #fff; border-color: #0f3d5c; }
.subtabs { display: flex; gap: 6px; justify-content: center; margin: 12px 0 0; }
.subtab { border: 1px solid #c9d3db; background: #fff; color: #0f3d5c; border-radius: 16px; padding: 4px 14px; font: 600 9pt 'Segoe UI', Arial, sans-serif; cursor: pointer; }
.subtab.active { background: #2a9d8f; color: #fff; border-color: #2a9d8f; }
.section { display: none; } .section.active { display: block; }
.section .mod.story, .section .mod.method { display: none; } .section .mod.show { display: block; }
@media print {
  body { background: #fff; } .wrap { padding: 0; max-width: none; } .tabbar, .subtabs { display: none !important; }
  .section, .section .mod.story, .section .mod.method { display: block !important; }
  .mod { box-shadow: none; margin: 0; padding: 0; border-radius: 0; zoom: .9; page-break-after: always; }
  .grid { gap: 11px; } .pipe { margin-bottom: 10px; } .sowhat { margin-top: 11px; }
}
"""

JS = """<script>
(function () {
  var tabs = document.querySelectorAll('.tab'), secs = document.querySelectorAll('.section');
  function showSub(sec, which) {
    sec.querySelectorAll('.mod').forEach(function (m) {
      var isStory = m.classList.contains('story'), isMethod = m.classList.contains('method');
      if (!isStory && !isMethod) return;
      m.classList.toggle('show', (which === 'story' && isStory) || (which === 'method' && isMethod));
    });
    sec.querySelectorAll('.subtab').forEach(function (b) { b.classList.toggle('active', b.dataset.view === which); });
  }
  function show(id) {
    if (!document.getElementById('sec-' + id)) id = secs[0].dataset.id;
    secs.forEach(function (s) { s.classList.toggle('active', s.dataset.id === id); });
    tabs.forEach(function (t) { t.classList.toggle('active', t.dataset.target === id); });
    if (history.replaceState) history.replaceState(null, '', '#' + id);
    window.scrollTo(0, 0);
  }
  tabs.forEach(function (t) { t.addEventListener('click', function () { show(t.dataset.target); }); });
  secs.forEach(function (s) {
    if (!s.querySelector('.mod.story')) return;
    var bar = document.createElement('div'); bar.className = 'subtabs';
    [['story', 'Story'], ['method', 'Method']].forEach(function (v) {
      var b = document.createElement('button'); b.className = 'subtab'; b.dataset.view = v[0]; b.textContent = v[1];
      b.addEventListener('click', function () { showSub(s, v[0]); }); bar.appendChild(b);
    });
    s.insertBefore(bar, s.firstChild); showSub(s, 'story');
  });
  show((location.hash || '#').slice(1));
})();
</script>"""

def assemble(sections, title):
    """sections = [(id, tab label, html)] -> full HTML document with tabs."""
    tabs = "".join(f'<button class="tab" data-target="{s}">{l}</button>' for s, l, _ in sections)
    secs = "".join(f'<section class="section" id="sec-{s}" data-id="{s}">{h}</section>' for s, _, h in sections)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{title}</title><style>{CSS}</style></head><body><nav class="tabbar">{tabs}</nav><div class="wrap">{secs}</div>{JS}</body></html>')
