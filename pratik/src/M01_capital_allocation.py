# %% [markdown]
# # Module 1: Strategic Capital Allocation
#
# **Business question:** NovaFin has 180 strategic initiatives competing for capital. Which should be funded?
#
# **The chain we follow in every module:** Data → ML prediction → Financial metric → Risk assessment → Business decision.
#
# Here that means: predict `P(success)` for each initiative → compute NPV → Expected NPV = P(success) × NPV → combine with risk rating → **Fund / Review / Reject**.
#
# **What you will learn:** EDA on a small dataset, why cross-validation matters when you only have 180 rows, comparing models honestly, SHAP explanations, NPV and expected NPV.

# %% [markdown]
# ## 0. Setup
# In Colab the cell below installs the extra libraries, mounts Google Drive and finds the data folder automatically.

# %%
import warnings; warnings.filterwarnings("ignore")
import sys, subprocess, importlib.util
if importlib.util.find_spec("google.colab"):             # Colab: install the extra libraries once
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "shap", "xgboost", "lightgbm", "imbalanced-learn"])
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt, seaborn as sns

try:                                    # Colab: mount Drive if available
    from google.colab import drive; drive.mount("/content/drive")
except ImportError:
    pass

CANDIDATES = [Path("/content/drive/MyDrive/NovaFin_Capstone/data"), Path("../../Project"), Path("/mnt/project-files/Project")]
DATA = next(p for p in CANDIDATES if (p / "strategic_initiatives.csv").exists())
OUT = DATA.parent / "outputs" if "drive" in str(DATA) else Path("../outputs")
OUT.mkdir(exist_ok=True, parents=True)
SEED = 42
sns.set_theme(style="whitegrid", palette="deep")
print("Data folder:", DATA)

# %% [markdown]
# ## 1. Load and inspect
# Always check shape, data types, missing values and the balance of the target first.

# %%
df = pd.read_csv(DATA / "strategic_initiatives.csv")
print(df.shape)
print("Missing values:", df.isna().sum().sum())
print("Success rate:", df["Historical_Success"].mean().round(3))
df.head()

# %%
df.describe().T.round(2)

# %% [markdown]
# **Note:** 77% of initiatives succeeded. So a model that always says "success" is already 77% accurate. That is why we judge models by **ROC-AUC** (how well they *rank* initiatives), not accuracy.

# %% [markdown]
# ## 2. Exploratory analysis
# The brief asks for: investment distribution, ROI distribution, risk categories, business-unit performance, growth vs ROI, and investment vs success.

# %%
fig, ax = plt.subplots(2, 3, figsize=(16, 9))
sns.histplot(df["Initial_Investment"], bins=25, ax=ax[0, 0]).set_title("Initial investment (₹ lakh)")
sns.histplot(df["Expected_ROI"], bins=25, ax=ax[0, 1]).set_title("Expected ROI (%)")
order = ["Low", "Medium", "High"]
sns.barplot(data=df, x="Risk_Rating", y="Historical_Success", order=order, ax=ax[0, 2], errorbar=None).set_title("Success rate by risk rating")
bu = df.groupby("Business_Unit")["Historical_Success"].mean().sort_values()
bu.plot.barh(ax=ax[1, 0], color="C0").set_title("Success rate by business unit")
sns.scatterplot(data=df, x="Business_Growth", y="Expected_ROI", hue="Historical_Success", ax=ax[1, 1]).set_title("Business growth vs ROI")
sns.boxplot(data=df, x="Historical_Success", y="Initial_Investment", ax=ax[1, 2]).set_title("Investment vs success")
plt.tight_layout(); plt.show()

# %%
summary_bu = df.groupby("Business_Unit").agg(n=("Initiative_ID", "count"), success_rate=("Historical_Success", "mean"),
                                            avg_investment=("Initial_Investment", "mean"), avg_roi=("Expected_ROI", "mean")).round(2)
summary_bu.sort_values("success_rate", ascending=False)

# %%
num = df.select_dtypes("number").drop(columns="Initiative_ID")
num.corr()["Historical_Success"].drop("Historical_Success").sort_values().plot.barh(figsize=(7, 4), title="Correlation with success")
plt.show()

# %% [markdown]
# **What the EDA says:** Low-risk initiatives succeed most often (~89% vs ~70%). Expected_ROI and Business_Growth have the strongest (but still weak) positive link with success; competition has a negative one. Investment size barely matters. With such weak single-variable signals, expect modest model performance.

# %% [markdown]
# ## 3. Feature engineering
# - Map `Risk_Rating` to an ordered number (Low=0, Medium=1, High=2).
# - One-hot encode `Business_Unit`.
# - Add finance ratios: **revenue multiple** (3-year revenue ÷ investment) and **operating margin**.
# - Drop `Initiative_ID` (an ID carries no information, and using it would be a mistake).
#
# **Leakage check:** `Expected_ROI` is a forecast made *before* the project, so it is allowed. (Its correlation with the realised cash-flow ROI is only ~0.5, so it is not a hidden copy of the outcome.)

# %%
X = df.drop(columns=["Initiative_ID", "Historical_Success"]).copy()
y = df["Historical_Success"]
X["Risk_Rating"] = X["Risk_Rating"].map({"Low": 0, "Medium": 1, "High": 2})
rev3 = X[["Revenue_Year1", "Revenue_Year2", "Revenue_Year3"]].sum(axis=1)
X["Revenue_Multiple"] = rev3 / X["Initial_Investment"]
X["Operating_Margin"] = 1 - 3 * X["Operating_Cost"] / rev3
X = pd.get_dummies(X, columns=["Business_Unit"], dtype=float)
X.shape

# %% [markdown]
# ## 4. Models and validation
# With only 180 rows a single train/test split is unreliable (the test set would hold ~10 failures). We use **repeated stratified 5-fold cross-validation** (5 folds × 10 repeats = 50 scores per model) and compare the mean and spread of ROC-AUC.
#
# Models: a dummy baseline, logistic regression (simple, explainable), random forest and XGBoost (non-linear).

# %%
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold, cross_val_score, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from xgboost import XGBClassifier

models = {
    "Baseline (always majority)": DummyClassifier(strategy="prior"),
    "Logistic regression": make_pipeline(StandardScaler(), LogisticRegression(C=0.3, max_iter=1000)),
    "Random forest": RandomForestClassifier(n_estimators=400, max_depth=4, min_samples_leaf=5, random_state=SEED),
    "XGBoost": XGBClassifier(n_estimators=200, max_depth=2, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=SEED, verbosity=0),
}
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=SEED)
scores = {name: cross_val_score(m, X, y, cv=cv, scoring="roc_auc") for name, m in models.items()}
cv_table = pd.DataFrame({k: [v.mean(), v.std()] for k, v in scores.items()}, index=["mean AUC", "std"]).T.round(3)
cv_table

# %%
pd.DataFrame(scores).plot.box(figsize=(9, 4), title="ROC-AUC across 50 CV folds", rot=10); plt.axhline(0.5, ls="--", c="grey"); plt.show()

# %% [markdown]
# **How to read this:** AUC 0.5 = random guessing, 1.0 = perfect. Logistic regression reaches only ~0.55, and the tree models fall *below* 0.5 because they overfit 180 rows. The spread (±0.09) is larger than the gaps between models.
#
# **Finding for the board:** past success is barely predictable from these characteristics. That is an honest, useful result: P(success) should be a small adjustment, and the funding decision must rest mainly on NPV and risk. NovaFin should also collect richer initiative data (team, execution track record) before trusting a success model.

# %% [markdown]
# ## 5. Explainability: what makes an initiative succeed?
# Logistic-regression coefficients (on standardised features) give direction and strength. SHAP shows the same for the tree model, feature by feature.

# %%
lr = models["Logistic regression"].fit(X, y)
coef = pd.Series(lr[-1].coef_[0], index=X.columns).sort_values()
coef.plot.barh(figsize=(7, 6), title="Logistic regression coefficients (standardised)"); plt.show()

# %%
import shap
rf = models["Random forest"].fit(X, y)
sv = shap.TreeExplainer(rf).shap_values(X)
sv = sv[:, :, 1] if np.ndim(sv) == 3 else sv[1]
shap.summary_plot(sv, X, max_display=12, show=False); plt.title("SHAP: random forest"); plt.tight_layout(); plt.show()

# %% [markdown]
# ## 6. Out-of-fold P(success)
# To score every initiative fairly, each one gets its probability from a model that **did not see it in training** (`cross_val_predict`). Otherwise our expected NPV would be over-optimistic.
#
# We use **logistic regression**, the best model in cross-validation. The tree models scored below 0.5: with 180 rows they memorise noise (overfitting).

# %%
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
p_lr = cross_val_predict(models["Logistic regression"], X, y, cv=skf, method="predict_proba")[:, 1]
from sklearn.metrics import roc_auc_score
df["P_Success"] = p_lr
print("Out-of-fold AUC:", round(roc_auc_score(y, df["P_Success"]), 3))

# %% [markdown]
# ## 7. NPV and Expected NPV
# **Assumptions (state these in the report):**
# 1. Annual cash flow = Revenue_Year_t − Operating_Cost.
# 2. **Project life = 5 years**: years 4 and 5 repeat the year-3 cash flow. With only 3 years almost no project pays back its investment (only 3% have positive NPV), which is unrealistic for strategic initiatives.
# 3. **Units:** all money is in ₹ lakh, as the data README says (100 lakh = 1 crore).
# 4. **Discount rate** = Interest_Rate + risk premium (Low +2%, Medium +4%, High +6%).
#
# $$NPV = -I_0 + \sum_{t=1}^{5} \frac{CF_t}{(1+r)^t} \qquad ENPV = P(\text{success}) \times NPV$$

# %%
PREMIUM = {"Low": 0.02, "Medium": 0.04, "High": 0.06}
def npv(d, life=5, premium=PREMIUM):
    r = d["Interest_Rate"] / 100 + d["Risk_Rating"].map(premium)
    cf = [d[f"Revenue_Year{t}"] - d["Operating_Cost"] for t in (1, 2, 3)]
    cf += [cf[2]] * (life - 3)
    return -d["Initial_Investment"] + sum(cf[t] / (1 + r) ** (t + 1) for t in range(life))

df["Discount_Rate"] = df["Interest_Rate"] / 100 + df["Risk_Rating"].map(PREMIUM)
df["NPV"] = npv(df)
df["ENPV"] = df["P_Success"] * df["NPV"]
df[["Initiative_ID", "Business_Unit", "Initial_Investment", "Risk_Rating", "P_Success", "NPV", "ENPV"]].sort_values("ENPV", ascending=False).head(10).round(2)

# %% [markdown]
# **Sensitivity:** how many initiatives have positive NPV under different project lives? This shows the board how much the answer depends on our assumption.

# %%
sens = pd.DataFrame({f"{life}-year life": [(npv(df, life) > 0).mean(), npv(df, life).median()] for life in (3, 5, 7)},
                    index=["share with NPV > 0", "median NPV"]).round(2)
sens

# %% [markdown]
# ## 8. Decision: Fund / Review / Reject
# Rules (thresholds are our judgement; justify them in the report):
# - **Fund:** ENPV > 0, P(success) ≥ 0.70 and risk Low or Medium. High expected value and acceptable risk.
# - **Review:** ENPV > 0 but High risk or P(success) < 0.70. Potentially attractive but uncertain.
# - **Reject:** ENPV ≤ 0. Low expected value.

# %%
def decide(r):
    if r["ENPV"] <= 0:
        return "Reject"
    if r["Risk_Rating"] == "High" or r["P_Success"] < 0.70:
        return "Review"
    return "Fund"
df["Decision"] = df.apply(decide, axis=1)
dec = df.groupby("Decision").agg(n=("Initiative_ID", "count"), investment=("Initial_Investment", "sum"), total_ENPV=("ENPV", "sum")).round(1)
dec

# %%
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(data=df, x="P_Success", y="NPV", hue="Decision", style="Risk_Rating", palette={"Fund": "C2", "Review": "C1", "Reject": "C3"}, ax=ax)
ax.axhline(0, c="grey", ls="--"); ax.axvline(0.70, c="grey", ls=":"); ax.set_title("Initiative decisions"); plt.show()

# %%
by_bu = (df.pivot_table(index="Business_Unit", columns="Decision", values="Initiative_ID", aggfunc="count", fill_value=0)
         .join(df[df.Decision == "Fund"].groupby("Business_Unit").agg(Fund_investment=("Initial_Investment", "sum"), Fund_ENPV=("ENPV", "sum")))
         .fillna(0).round(1).sort_values("Fund_ENPV", ascending=False))
by_bu

# %% [markdown]
# ## 9. Save outputs for Module 9 (integrated allocation)

# %%
cols = ["Initiative_ID", "Business_Unit", "Initial_Investment", "Risk_Rating", "P_Success", "Discount_Rate", "NPV", "ENPV", "Decision"]
df[cols].round(4).to_csv(OUT / "m1_initiatives.csv", index=False)
by_bu.to_csv(OUT / "m1_by_business_unit.csv")
print("Saved", OUT / "m1_initiatives.csv")

# %% [markdown]
# ## 10. Conclusions
# 1. **Success is hard to predict:** best cross-validated AUC ≈ 0.55 (logistic regression). Low risk rating, higher expected ROI and business growth push success up; competition pushes it down.
# 2. **Financials drive the decision:** under a 5-year life, about a third of initiatives have positive NPV. The result is sensitive to project life, so state it clearly.
# 3. **Recommendation:** fund the initiatives in the *Fund* group (see table above), send *Review* initiatives to a committee with extra due diligence, and reject the rest. Wealth, Payments and Digital Banking carry the most fundable expected value.
# 4. **Limits:** 180 rows, synthetic data, NPV depends on assumed life and discount premiums.
