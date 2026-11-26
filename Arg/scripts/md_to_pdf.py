"""
Markdown → PDF (ReportLab), for the final report and code guide
================================================================

WHAT THIS FILE DOES
    Converts the subset of Markdown the project's reports use into a styled PDF: headings (#–####),
    paragraphs, bullet and numbered lists, tables, **bold**, *italic*, `code`, code blocks, quotes,
    images, rules (---) and page breaks (a line with only <<PAGEBREAK>>). Adds a contents page with page numbers
    and PDF bookmarks. Images and fonts are embedded, so the PDF reads the same on any machine.

HOW TO USE
    from md_to_pdf import build_pdf
    build_pdf(markdown_text, out_path, title="…", subtitle="…", base_dir=folder_for_relative_images, footer="…", authors="…")
"""
import re
from pathlib import Path

from reportlab import rl_config
rl_config.useA85 = 0             # store images as plain compressed data (about a fifth smaller, same quality)
rl_config.invariant = 1          # fixed creation date and document ID: same content → byte-identical PDF
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (HRFlowable, Image, Indenter, KeepTogether, PageBreak, Paragraph, Preformatted, SimpleDocTemplate,
                                Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

def _fonts() -> dict:
    """Font files that print ₹, −, ≈ and →: Segoe UI on Windows; on any other machine (Mac, Linux, Google Colab)
    DejaVu Sans, which ships with matplotlib (already in requirements.txt), so the PDFs build everywhere."""
    win = Path("C:/Windows/Fonts")
    if (win / "segoeui.ttf").exists() and (win / "segoeuib.ttf").exists():
        pick = lambda f, alt: win / f if (win / f).exists() else win / alt
        return {"Body": win / "segoeui.ttf", "Body-Bold": win / "segoeuib.ttf",
                "Body-Italic": pick("segoeuii.ttf", "segoeui.ttf"), "Mono": pick("consola.ttf", "segoeui.ttf")}
    import matplotlib
    mpl = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    return {"Body": mpl / "DejaVuSans.ttf", "Body-Bold": mpl / "DejaVuSans-Bold.ttf",
            "Body-Italic": mpl / "DejaVuSans-Oblique.ttf", "Mono": mpl / "DejaVuSansMono.ttf"}


for _name, _file in _fonts().items():
    pdfmetrics.registerFont(TTFont(_name, str(_file)))
from reportlab.lib.fonts import addMapping
addMapping("Body", 0, 0, "Body"); addMapping("Body", 1, 0, "Body-Bold"); addMapping("Body", 0, 1, "Body-Italic"); addMapping("Body", 1, 1, "Body-Bold")

NAVY, INK, GREY, RULE, ZEBRA = colors.HexColor("#1F3A5F"), colors.HexColor("#1b1b1b"), colors.HexColor("#5a5a5a"), colors.HexColor("#c9ced6"), colors.HexColor("#f3f5f8")
ST = {
    "h1": ParagraphStyle("h1", fontName="Body-Bold", fontSize=19, leading=24, textColor=NAVY, spaceBefore=6, spaceAfter=10, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="Body-Bold", fontSize=14.5, leading=19, textColor=NAVY, spaceBefore=12, spaceAfter=6, keepWithNext=1),
    "h3": ParagraphStyle("h3", fontName="Body-Bold", fontSize=12, leading=16, textColor=NAVY, spaceBefore=9, spaceAfter=4, keepWithNext=1),
    "h4": ParagraphStyle("h4", fontName="Body-Bold", fontSize=10.5, leading=14, textColor=INK, spaceBefore=7, spaceAfter=3, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="Body", fontSize=9.6, leading=13.6, textColor=INK, spaceAfter=5, alignment=TA_LEFT),
    "li": ParagraphStyle("li", fontName="Body", fontSize=9.6, leading=13.4, textColor=INK, spaceAfter=2),
    "quote": ParagraphStyle("quote", fontName="Body-Italic", fontSize=9.4, leading=13.2, textColor=GREY, leftIndent=12, spaceAfter=6),
    "cell": ParagraphStyle("cell", fontName="Body", fontSize=7.6, leading=9.8, textColor=INK),
    "head": ParagraphStyle("head", fontName="Body-Bold", fontSize=7.8, leading=10, textColor=colors.white),
    "code": ParagraphStyle("code", fontName="Mono", fontSize=7.8, leading=10, textColor=INK, backColor=ZEBRA, leftIndent=6, rightIndent=6, borderPadding=5, spaceAfter=8),
    "title": ParagraphStyle("title", fontName="Body-Bold", fontSize=26, leading=32, textColor=NAVY, spaceAfter=14),
    "subtitle": ParagraphStyle("subtitle", fontName="Body", fontSize=13, leading=18, textColor=GREY, spaceAfter=8),
}


def inline(t: str) -> str:
    """Markdown inline marks → ReportLab tags (text escaped first)."""
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"`([^`]+)`", r'<font name="Mono">\1</font>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    return t


def _table(rows: list, width: float):
    """A Markdown table as a styled ReportLab table with wrapped cells and proportional column widths."""
    head, body = rows[0], rows[1:]
    n = max(len(head), *[len(r) for r in body]) if body else len(head)
    head = head + [""] * (n - len(head))
    body = [r + [""] * (n - len(r)) for r in body]
    lens = [max([len(str(head[i]))] + [len(str(r[i])) for r in body]) for i in range(n)]
    lens = [min(max(l, 9), 60) for l in lens]
    widths = [width * l / sum(lens) for l in lens]
    # Never split a word or number: each column is at least as wide as its longest word (header in bold counts too),
    # and the columns above their minimum give up width to make room.
    char_w = ST["cell"].fontSize * 0.56
    longest = [max(len(w) for c in [head[i]] + [r[i] for r in body] for w in (str(c).replace("**", "").split() or [""])) for i in range(n)]
    mins = [min(lw, 22) * char_w * (1.12 if lw == max(len(w) for w in (str(head[i]).split() or [""])) else 1.0) + 9 for i, lw in enumerate(longest)]
    for _ in range(10):
        widths = [max(w, m) for w, m in zip(widths, mins)]
        extra = sum(widths) - width
        if extra <= 0.5:
            break
        free = [i for i in range(n) if widths[i] > mins[i] + 0.5]
        room = sum(widths[i] - mins[i] for i in free)
        if room <= 0:
            break
        for i in free:
            widths[i] -= extra * (widths[i] - mins[i]) / room
    data = [[Paragraph(inline(c), ST["head"]) for c in head]] + [[Paragraph(inline(c), ST["cell"]) for c in r] for r in body]
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.25, RULE),
             ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    style += [("BACKGROUND", (0, i), (-1, i), ZEBRA) for i in range(2, len(data), 2)]
    t.setStyle(TableStyle(style))
    return t


def md_to_flowables(md: str, base_dir: Path, width: float, img_cm: float = 9) -> list:
    """Parse the Markdown subset line by line into flowables."""
    out, lines, i = [], md.splitlines(), 0
    while i < len(lines):
        line = lines[i].rstrip()
        s = line.strip()
        if s == "<<PAGEBREAK>>":
            out.append(PageBreak()); i += 1; continue
        if s.startswith("```"):
            j = i + 1; buf = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                buf.append(lines[j]); j += 1
            longest = max([pdfmetrics.stringWidth(b, "Mono", ST["code"].fontSize) for b in buf] or [1])
            size = ST["code"].fontSize * min(1.0, (width - 24) / longest)          # shrink so no line runs off the page
            out.append(Preformatted("\n".join(buf), ParagraphStyle("codefit", parent=ST["code"], fontSize=size, leading=size * 1.28))); i = j + 1; continue
        if re.fullmatch(r"-{3,}", s):
            out.append(HRFlowable(width="100%", thickness=0.6, color=RULE, spaceBefore=4, spaceAfter=6)); i += 1; continue
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*:?-{2,}", lines[i + 1].strip()):
            cells = lambda t: [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", t.strip().strip("|"))]
            rows = [cells(s)]
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(cells(lines[j])); j += 1
            out += [_table(rows, width), Spacer(1, 7)]; i = j; continue
        m = re.match(r"^(#{1,4})\s+(.*)", s)
        if m:
            lvl = len(m.group(1)); out.append(Paragraph(inline(m.group(2)), ST[f"h{lvl}"])); i += 1; continue
        m = re.match(r"^!\[[^\]]*\]\(([^)]+)\)", s)
        if m:
            p = (base_dir / m.group(1)).resolve()
            if not p.exists():
                raise FileNotFoundError(f"Image missing: {m.group(1)}")          # never drop a chart silently
            else:
                img = Image(str(p)); r = min(width / img.imageWidth, img_cm * cm / img.imageHeight, 1.0)
                img.drawWidth, img.drawHeight = img.imageWidth * r, img.imageHeight * r
                if out and isinstance(out[-1], Paragraph) and out[-1].style.name == "p":   # a caption stays on its chart's page
                    cap = out.pop(); heads = []
                    while out and isinstance(out[-1], Paragraph) and out[-1].style.name in ("h1", "h2", "h3", "h4"):
                        heads.insert(0, out.pop())
                    out += heads + ([KeepTogether([cap, img])] if not heads else [cap, img]) + [Spacer(1, 6)]
                    if heads:
                        cap.keepWithNext = 1
                else:
                    out += [img, Spacer(1, 6)]
            i += 1; continue
        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip()); i += 1
            if any(b.startswith(("|", "- ")) for b in buf):                      # a quoted table or list: keep its layout
                out += [Indenter(left=12), *md_to_flowables("\n".join(buf), base_dir, width - 12), Indenter(left=-12)]; continue
            out.append(Paragraph(inline(" ".join(buf)), ST["quote"])); continue
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)", line)
        if m:
            indent = len(m.group(1)) // 2
            bullet = "•" if m.group(2) in "-*" else m.group(2)
            st = ParagraphStyle("lix", parent=ST["li"], leftIndent=12 + 12 * indent, bulletIndent=2 + 12 * indent)
            out.append(Paragraph(inline(m.group(3)), st, bulletText=bullet)); i += 1; continue
        if not s:
            i += 1; continue
        buf = [s]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||>|```|!\[|\s*([-*]|\d+\.)\s)", lines[i]) and lines[i].strip() != "<<PAGEBREAK>>":
            buf.append(lines[i].strip()); i += 1
        out.append(Paragraph(inline(" ".join(buf)), ST["p"]))
    return out


class _Doc(SimpleDocTemplate):
    """Adds each chapter (h1) and section (h2) to the contents page and the PDF bookmarks."""
    def beforeDocument(self):
        self._n, self._top = 0, False

    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name in ("h1", "h2"):
            level = 0 if f.style.name == "h1" or not self._top else 1      # a section before the first chapter sits at the top level
            self._top = True
            key = f"h{self._n}"; self._n += 1
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(f.getPlainText(), key, level, closed=level == 0)
            self.notify("TOCEntry", (level, f.text if hasattr(f, "text") else f.getPlainText(), self.page, key))


def build_pdf(md: str, out_path: Path, title: str, subtitle: str, base_dir: Path, footer: str, authors: str = "", img_cm: float = 9) -> Path:
    """Title page (with the team), contents page, then the content, with page numbers and a footer line. Charts are at most img_cm tall."""
    doc = _Doc(str(out_path), pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.6 * cm, bottomMargin=1.6 * cm,
               title=title, author=authors)
    width = A4[0] - 3.6 * cm

    def on_page(c, d):
        c.saveState(); c.setFont("Body", 7.5); c.setFillColor(GREY)
        c.drawString(1.8 * cm, 0.9 * cm, footer); c.drawRightString(A4[0] - 1.8 * cm, 0.9 * cm, f"Page {d.page}"); c.restoreState()

    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("toc1", fontName="Body-Bold", fontSize=9.6, leading=12, textColor=NAVY, spaceBefore=1),
                       ParagraphStyle("toc2", fontName="Body", fontSize=8.6, leading=10.4, textColor=INK, leftIndent=14)]
    story = [Spacer(1, 5 * cm), Paragraph(inline(title), ST["title"]), Paragraph(inline(subtitle), ST["subtitle"])]
    story += [Spacer(1, 1.2 * cm), Paragraph(inline(authors), ST["subtitle"])] if authors else []
    story += [PageBreak(), Paragraph("Contents", ParagraphStyle("contents", parent=ST["h1"])), toc, PageBreak()]
    story += md_to_flowables(md, base_dir, width, img_cm)
    doc.multiBuild(story, onFirstPage=lambda c, d: None, onLaterPages=on_page)
    return out_path
