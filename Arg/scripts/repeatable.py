"""
Repeatable output files
=======================

WHAT THIS FILE DOES
    Excel (.xlsx) and PowerPoint (.pptx) files are zip archives that store the time they were written
    (inside docProps/core.xml and on every zip entry). Rebuilding a workbook or deck with identical
    content therefore produces a different file, which shows up as a change in git although nothing
    changed. normalise_office_file() rewrites those timestamps to one fixed value, so a rebuild with the
    same content gives a byte-identical file and git shows only genuine changes.

HOW TO USE
    from repeatable import normalise_office_file, FIXED_STAMP
    normalise_office_file(path)          # after saving an .xlsx or .pptx
"""
import re
import zipfile
from pathlib import Path

FIXED_STAMP = "2026-11-22T00:00:00Z"            # the date the project's results were finalised
FIXED_ZIP_TIME = (2026, 11, 22, 0, 0, 0)


def _normalise_zip_bytes(data: bytes, stamp: str) -> bytes:
    """Fix the stored times of an Office zip held in memory (also inside it: embedded .xlsx, e.g. chart data in a deck)."""
    import io
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        entries = [(i.filename, z.read(i.filename), i.compress_type) for i in z.infolist()]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, part, ctype in entries:
            if name == "docProps/core.xml":
                text = part.decode("utf-8")
                text = re.sub(r"(<dcterms:(created|modified)[^>]*>)[^<]*(</dcterms:\2>)", rf"\g<1>{stamp}\g<3>", text)
                part = text.encode("utf-8")
            elif name.lower().endswith((".xlsx", ".pptx", ".docx")):
                part = _normalise_zip_bytes(part, stamp)              # an embedded Office file: same treatment
            info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_TIME)
            info.compress_type = ctype
            info.external_attr = 0o600 << 16
            z.writestr(info, part)
    return buf.getvalue()


def normalise_office_file(path, stamp: str = FIXED_STAMP) -> Path:
    """Rewrite an .xlsx/.pptx so its stored times are fixed: core.xml created/modified, each zip entry's time,
    and the same inside any embedded Office file (the chart data workbooks in a PowerPoint deck)."""
    path = Path(path)
    path.write_bytes(_normalise_zip_bytes(path.read_bytes(), stamp))
    return path
