# NovaFin Capstone (Group 7)

Executed notebooks, one per module, plus their saved outputs.

- `notebooks/` — open these in Colab or Jupyter. Run M01–M08 in any order, then M09.
- `outputs/` — CSV results each notebook saves; M09 reads them.
- `figures/` — charts exported from the notebooks (for the report and deck).
- `src/` — the same notebooks as plain Python (`# %%` cells) and `build_nb.py`, which rebuilds and executes a notebook:
  `python src/build_nb.py src/M02_credit_risk.py notebooks/M02_credit_risk.ipynb`

Colab setup: put the 7 in-scope data files in `My Drive/NovaFin_Capstone/data/` (keep the HFT file zipped).
Each notebook installs shap, xgboost, lightgbm and imbalanced-learn, mounts Drive and writes to `NovaFin_Capstone/outputs/`.
