"""Turn a percent-format .py file (# %% / # %% [markdown]) into an executed .ipynb."""
import sys, re, nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path

def parse(src):
    cells, kind, buf = [], None, []
    def flush():
        if kind is None: return
        text = "\n".join(buf).strip("\n")
        if kind == "md":
            text = "\n".join(re.sub(r"^# ?", "", l) for l in text.splitlines())
            cells.append(nbformat.v4.new_markdown_cell(text))
        elif text.strip():
            cells.append(nbformat.v4.new_code_cell(text))
    for line in src.splitlines():
        if line.startswith("# %%"):
            flush(); buf = []
            kind = "md" if "[markdown]" in line else "code"
        else:
            buf.append(line)
    flush()
    return cells

src, out = Path(sys.argv[1]), Path(sys.argv[2])
nb = nbformat.v4.new_notebook(cells=parse(src.read_text()))
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
ExecutePreprocessor(timeout=1800, kernel_name="python3").preprocess(nb, {"metadata": {"path": str(out.parent)}})
nbformat.write(nb, out)
print("wrote", out)
