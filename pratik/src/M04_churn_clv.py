# %% [markdown]
# # Module 4: Customer Analytics: Churn & Customer Lifetime Value
#
# **Business question:** Which customers should relationship managers prioritise for retention? If NovaFin can contact only **1,000 customers**, who should they be?
#
# **Chain:** customer data → P(churn) → customer lifetime value (CLV) → value at risk = P(churn) × CLV → 2×2 segments → target list of 1,000.
#
# **What you will learn:** modelling a very rare event (89 churners in 5,000), recognising when a model has *no* signal, building a CLV formula, segmentation, and ranking under a budget.

# %% [markdown]
# ## 0. Setup

# %%
import warnings; warnings.filterwarnings("ignore")
import sys, subprocess, importlib.util
if importlib.util.find_spec("google.colab"):             # Colab: install the extra libraries once
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "shap", "xgboost", "lightgbm", "imbalanced-learn"])
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt, seaborn as sns
try:
    from google.colab import drive; drive.mount("/content/drive")
except ImportError:
    pass
CANDIDATES = [Path("/content/drive/MyDrive/NovaFin_Capstone/data"), Path("../../Project"), Path("/mnt/project-files/Project")]
DATA = next(p for p in CANDIDATES if (p / "nova_customers.csv").exists())
OUT = DATA.parent / "outputs" if "drive" in str(DATA) else Path("../outputs")
OUT.mkdir(exist_ok=True, parents=True)
SEED = 42
sns.set_theme(style="whitegrid", palette="deep")

# %% [markdown]
# ## 1. Load and inspect
# This file is analysed on its own: its customer IDs do not match the loan or transaction files.

# %%
df = pd.read_csv(DATA / "nova_customers.csv")
print(df.shape, "| missing:", df.isna().sum().sum())
print(f"Churn rate: {df.Churn_Flag.mean():.2%} ({df.Churn_Flag.sum()} churners)")
df.head()

# %% [markdown]
# ## 2. Exploratory analysis
# Do churners look different from customers who stay?

# %%
feats = ["Age", "Annual_Income", "Account_Balance", "Products_Held", "Transactions_Per_Month", "Digital_Usage",
         "Complaints", "Loan_Balance", "Investment_Balance", "Relationship_Length_Years"]
comp = df.groupby("Churn_Flag")[feats].mean().T
comp["difference %"] = (comp[1] / comp[0] - 1) * 100
comp.round(1)

# %%
fig, ax = plt.subplots(1, 4, figsize=(17, 4))
for a, c in zip(ax, ["Complaints", "Products_Held", "Digital_Usage", "Relationship_Length_Years"]):
    df.groupby(c if df[c].nunique() < 20 else pd.qcut(df[c], 5), observed=True)["Churn_Flag"].mean().plot.bar(ax=a, title=f"Churn rate by {c}", rot=45)
plt.tight_layout(); plt.show()

# %% [markdown]
# **What the EDA says:** churners and stayers look almost identical: every average differs by a few percent, and churn rates by complaints, products or digital usage show no clear pattern. Expect a weak model. Spotting this early is part of good analysis.

# %% [markdown]
# ## 3. Churn models
# With only 89 churners, a single test set would hold ~27 of them, too few to trust. We use **repeated stratified 5-fold CV** (50 scores per model) and class weights.

# %%
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold, cross_val_score, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score, average_precision_score

X = df[feats].copy()
X["Total_Balance"] = X["Account_Balance"] + X["Investment_Balance"]
X["Balance_to_Income"] = X["Total_Balance"] / X["Annual_Income"]
y = df["Churn_Flag"]
spw = (y == 0).sum() / (y == 1).sum()
models = {
    "Logistic (balanced)": make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", C=0.1, max_iter=2000)),
    "Random forest": RandomForestClassifier(n_estimators=400, min_samples_leaf=20, class_weight="balanced_subsample", random_state=SEED, n_jobs=-1),
    "XGBoost": XGBClassifier(n_estimators=200, max_depth=2, learning_rate=0.05, scale_pos_weight=spw, random_state=SEED, verbosity=0),
}
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=SEED)
scores = {n: cross_val_score(m, X, y, cv=cv, scoring="roc_auc") for n, m in models.items()}
pd.DataFrame({n: [s.mean(), s.std(), np.percentile(s, 5), np.percentile(s, 95)] for n, s in scores.items()}, index=["mean AUC", "std", "5th pct", "95th pct"]).T.round(3)

# %% [markdown]
# **Reading the result:** every model's AUC is around 0.5, and the 5th–95th percentile range spans 0.5. **The churn label cannot be predicted from these variables.** A good analyst reports that clearly rather than presenting a random model as insight.
#
# **What it means for NovaFin:** the bank is not capturing the data that signals churn (for example falling balances month to month, competitor offers, service events). Recommendation: start collecting behavioural *trends*, not just snapshots.
#
# We still produce out-of-fold churn scores (they will sit close to the 1.8% base rate) to show the full method, which will work once better data exists.

# %%
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
raw = cross_val_predict(models["Logistic (balanced)"], X, y, cv=skf, method="predict_proba")[:, 1]
# class weights inflate probabilities; rescale so the average equals the true churn rate
df["P_Churn"] = raw * y.mean() / raw.mean()
print("Out-of-fold AUC:", round(roc_auc_score(y, df.P_Churn), 3), "| mean P(churn):", round(df.P_Churn.mean(), 4))

# %% [markdown]
# ## 4. Customer Lifetime Value
# **Check the provided column first.** A linear regression of `Estimated_CLV` on the other columns fits almost perfectly, so it is a fixed formula, not data.

# %%
from sklearn.linear_model import LinearRegression
lin = LinearRegression().fit(df[feats], df["Estimated_CLV"])
print("R² of Estimated_CLV on the other columns:", round(lin.score(df[feats], df["Estimated_CLV"]), 5))
pd.Series(lin.coef_, index=feats).round(4)

# %% [markdown]
# It is roughly 4% of income + 3% of account balance + 1.8% of investments + 1.2% of loans − ₹5,000 per complaint. It ignores churn and time. We build our own, finance-based CLV:
#
# $$CLV = \sum_{t=1}^{5} \frac{M \cdot (1-p)^{t}}{(1+d)^{t}}$$
#
# **Assumptions:** annual margin M = 2.0% of account balance (deposit spread) + 2.5% of loan balance (net interest margin) + 1.0% of investment balance (fees) − ₹1,000 servicing cost per complaint; p = annual churn probability; d = 10% discount rate; 5-year horizon.

# %%
H, DISC = 5, 0.10
df["Annual_Margin"] = (0.020 * df.Account_Balance + 0.025 * df.Loan_Balance + 0.010 * df.Investment_Balance - 1000 * df.Complaints).clip(lower=0)
ret = 1 - df["P_Churn"]
df["CLV"] = sum(df["Annual_Margin"] * ret ** t / (1 + DISC) ** t for t in range(1, H + 1))
print("Correlation of our CLV with Estimated_CLV:", round(df[["CLV", "Estimated_CLV"]].corr().iloc[0, 1], 3))
df[["CLV", "Estimated_CLV"]].describe().round(0)

# %% [markdown]
# ## 5. 2×2 segmentation
# - **CLV split:** median CLV.
# - **Churn split:** top 20% of predicted churn risk = High churn.

# %%
hi_clv = df.CLV >= df.CLV.median()
hi_churn = df.P_Churn >= df.P_Churn.quantile(0.80)
df["Segment"] = np.select([hi_clv & ~hi_churn, hi_clv & hi_churn, ~hi_clv & ~hi_churn], ["Protect", "Priority retention", "Maintain"], "Low-cost intervention")
seg = df.groupby("Segment").agg(customers=("Customer_ID", "count"), avg_CLV=("CLV", "mean"), total_CLV_cr=("CLV", lambda s: s.sum() / 1e7),
                                avg_P_churn=("P_Churn", "mean"), actual_churn=("Churn_Flag", "mean")).round(4)
seg.loc[["Protect", "Priority retention", "Maintain", "Low-cost intervention"]]

# %%
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(data=df, x="P_Churn", y="CLV", hue="Segment", s=12, ax=ax, alpha=0.6)
ax.set(yscale="log", title="Customer segments"); ax.axvline(df.P_Churn.quantile(0.8), c="grey", ls="--"); ax.axhline(df.CLV.median(), c="grey", ls="--"); plt.show()

# %% [markdown]
# ## 6. The 1,000 customers to contact
# Rank by **expected value at risk** = P(churn) × CLV, the money NovaFin expects to lose from each customer, and take the top 1,000.

# %%
df["Value_at_Risk"] = df["P_Churn"] * df["CLV"]
top = df.nlargest(1000, "Value_at_Risk")
rng = np.random.default_rng(SEED)
rand = df.iloc[rng.choice(len(df), 1000, replace=False)]
compare = pd.DataFrame({
    "Top 1,000 by value at risk": [top.Value_at_Risk.sum() / 1e7, top.CLV.sum() / 1e7, top.Churn_Flag.sum()],
    "Random 1,000": [rand.Value_at_Risk.sum() / 1e7, rand.CLV.sum() / 1e7, rand.Churn_Flag.sum()],
}, index=["Value at risk (₹ crore)", "CLV covered (₹ crore)", "Actual churners reached"]).round(3)
compare["lift"] = (compare.iloc[:, 0] / compare.iloc[:, 1]).round(2)
compare

# %%
top.Segment.value_counts()

# %% [markdown]
# **Answer to the executive question:** contact the 1,000 customers with the highest value at risk, mostly *Priority retention* and *Protect* customers. Because churn is not predictable, the ranking is driven by **CLV**: the list covers about 2.5× more customer value than a random 1,000. It does not reach more actual churners than random, and we should say so.

# %% [markdown]
# ## 7. Save outputs

# %%
top[["Customer_ID", "P_Churn", "CLV", "Value_at_Risk", "Segment"]].round(4).to_csv(OUT / "m4_top1000_contact_list.csv", index=False)
df[["Customer_ID", "P_Churn", "CLV", "Estimated_CLV", "Segment"]].round(4).to_csv(OUT / "m4_customers_scored.csv", index=False)
pd.Series({"cv_auc": np.mean(scores["Logistic (balanced)"]), "total_clv_cr": df.CLV.sum() / 1e7, "top1000_clv_cr": top.CLV.sum() / 1e7,
           "top1000_value_at_risk_cr": top.Value_at_Risk.sum() / 1e7, "investment_balance_cr": df.Investment_Balance.sum() / 1e7}).to_csv(OUT / "m4_summary.csv")
print("Saved")

# %% [markdown]
# ## 8. Conclusions
# 1. **Churn is not predictable** with the current data (cross-validated AUC ≈ 0.5 for every model). This is the key, honest finding.
# 2. `Estimated_CLV` is a fixed linear formula; we built a CLV from margins, retention and discounting instead.
# 3. **Target list:** the top 1,000 by value at risk, which covers about 2.5× the customer value of a random list.
# 4. **Recommendation:** run the retention campaign as a controlled test (contact half, hold out half) to measure the real effect, and collect monthly behaviour trends so a churn model can work next year.
# 5. **Limits:** assumed margins and discount rate; churn probability is near the base rate for everyone.
