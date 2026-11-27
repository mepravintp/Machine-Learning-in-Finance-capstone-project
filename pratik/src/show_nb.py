import sys, nbformat
nb = nbformat.read(sys.argv[1], 4)
for i, c in enumerate(nb.cells):
    if c.cell_type != "code": continue
    for o in c.get("outputs", []):
        t = o.get("text") or o.get("data", {}).get("text/plain", "")
        if o.get("output_type") == "error": t = "ERROR " + o["ename"] + ": " + o["evalue"]
        if t: print(f"--- cell {i}\n{t[:1500]}")
