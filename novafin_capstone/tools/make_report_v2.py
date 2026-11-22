"""NovaFin Capstone Report v2: Detailed Report + Code Guide in story format.

Every module = 2 pages: STORY (question, answer, step-by-step, 4 perspective charts, so what) + METHOD card.
Numbers come from results/ and data/, so the report stays in sync with the notebooks.
Run:  C:/Users/pravi/anaconda3/python.exe tools/make_report_v2.py
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from story_lib import (C, md, columns, dots, funnel, hbars, line, panel, story_page, method_card, assemble, file_img)

ROOT = Path(__file__).resolve().parents[1]
RES, DATA, OUT = ROOT / "results", ROOT / "data", ROOT / "deliverables"
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
J = lambda folder, name: json.loads((RES / folder / name).read_text(encoding="utf-8"))
pct = lambda v: f"{v:.0%}"

# ===============================================================================================================
# MODULE 1: Strategic initiatives
# ===============================================================================================================
def m1():
    init = pd.read_csv(DATA / "strategic_initiatives.csv")
    j = J("Module_01_Strategic_Initiatives", "initiatives.json")
    dec = pd.read_csv(RES / "Module_01_Strategic_Initiatives" / "initiatives_decisions.csv")
    funded = J("Module_09_Integrated_Allocation", "allocation.json")["funded_initiatives"]
    funded_cr = dec[dec.Initiative_ID.isin(funded)].Initial_Investment.sum()
    rr = init.groupby("Risk_Rating").Historical_Success.mean().reindex(["Low", "Medium", "High"])
    cv = j["model"]["cv_table"]; names = ["Logistic (3 drivers)", "Logistic regression", "Gradient boosting", "Random forest"]
    sens = j["sensitivity"]
    n_fund = int((dec.Decision == "Fund").sum())
    panels = [
        panel("data", "Low risk rating = clearest sign of success",
              columns([f"{k} risk" for k in rr.index], list(rr.values * 100), C["data"], lambda v: f"{v:.0f}%",
                      title="Share of past projects that succeeded, by risk rating"),
              "Low-risk initiatives succeeded 89% of the time vs ~70% for the rest. Investment size, GDP and rates showed no link."),
        panel("model", "Simple beats complex, but prediction is weak",
              dots(["Logistic, 3 drivers", "Logistic, all features", "Gradient boosting", "Random forest"],
                   [cv[n]["ROC-AUC mean"] for n in names], C["model"], 0.5, "coin flip = 0.50",
                   title="Prediction score of each model (ROC-AUC, 1.0 = perfect)", lo=0.38, hi=0.72),
              "With just 42 failures, flexible models memorise noise. The 3-variable model is best, but 0.63 is modest: ML is a risk check, not a picker."),
        panel("money", "Finance does the filtering: 180 → 5",
              funnel(["initiatives proposed", "NPV > 0 (5 years)", "value after failure risk", "Fund list", "funded in final ₹1,000 cr"],
                     [len(dec), int((dec.NPV > 0).sum()), int((dec.ENPV > 0).sum()), n_fund, len(funded)], C["money"],
                     title="How many projects pass each test"),
              "NPV over 5 years at 12%, minus the loss if a project fails, ranked by value per rupee. Realised success: Fund list 86% vs rejects 76%."),
        panel("risk", "It all depends on how long projects earn",
              line([3, 5, 7], [int(sens["Life 3 years"]["Fund"]), int(sens["Base (5y, 12%, base loss)"]["Fund"]), int(sens["Life 7 years"]["Fund"])],
                   C["risk"], ["3 yrs", "5 yrs", "7 yrs"], "assumed project life", "Projects on the Fund list vs assumed project life",
                   base_idx=1, extra=(f"{int(sens['Model stress: P(success) -10pp']['Fund'])} if success odds −10 pts",
                                      int(sens["Model stress: P(success) -10pp"]["Fund"]))),
              "Over 3 years nothing pays back; over 7 years the list doubles. Cutting every success odds by 10 points still leaves 12 good projects."),
    ]
    story = story_page("MODULE 1 · CORPORATE FINANCE", "Which strategic initiatives should get capital?",
        "For each of the <b>180 proposed projects</b>: should NovaFin <b>Fund</b>, <b>Review</b> or <b>Reject</b> it, and why?",
        f"<b>Fund 21</b>, Review 18, Reject 141. Of the 21, the <b>best 5 get ₹{funded_cr:.0f} cr</b> in the final ₹1,000 cr plan (all low-risk, ≥ 90% chance of success).",
        "ML weak · NPV decides", "amber",
        [("Started with", "180 past projects", "77% of them succeeded"), ("ML predicted", "Chance of success", "a modest predictor (0.63 out of 1)"),
         ("Money test", f"{n_fund} pass", "worth more than they cost, even allowing for failure"),
         ("Stress test", "12 still pass", "if every chance of success is 10 points lower"),
         ("Decision", f"5 funded · ₹{funded_cr:.0f} cr", "best value per rupee in the plan")],
        panels,
        ["<b>Fund on value, not on model scores.</b> NPV does the filtering; the model only adjusts for failure risk.",
         "<b>Ask for a Low risk rating and a growing segment.</b> They are the only traits that reliably raise success odds.",
         "<b>Release money in stages.</b> Value relies on years 4–5; stop funding a project that falls behind plan."],
        "01_strategic_initiatives.ipynb", "§1 EDA · §3 models · §5 SHAP · §6 NPV · §7 rule · §8 sensitivity",
        ["EDA of investment, ROI, risk, units", "predict success + explain drivers", "NPV, expected NPV, Fund / Review / Reject"])
    method = method_card("MODULE 1", "Strategic initiatives",
        """- **Data:** `strategic_initiatives.csv`, 180 × 14, no missing values; target `Historical_Success` (77% / 23%).
- **Features:** 13 numeric (investment, revenue Y1–Y3, cost, ROI, growth, GDP, rate, competition + revenue growth, Y1 margin, payback ratio) and 2 categorical (unit, risk rating).
- **Leakage:** revenue columns treated as ex-ante projections; `Initiative_ID` dropped.""",
        """- **Repeated stratified 5-fold CV × 10** (50 fits per model): too few failures (42) for one split.
- **Out-of-fold** P(success) for every project (never scored by a model that saw it), checked with a quintile calibration table.
- **Rule:** simplest model wins unless beaten by > 0.005 AUC.""",
        """| Model | CV ROC-AUC | Gain vs no-skill | Gap to best | Chosen |
|---|---|---|---|---|
| Logistic, 3 drivers (risk rating, growth, ROI) | **0.625 ± 0.10** | +0.125 | 0 | ✔ |
| Logistic, all 15 features | 0.559 | +0.059 | 0.066 | |
| Gradient boosting (depth 2) | 0.503 | +0.003 | 0.123 | |
| Random forest (leaf 5) | 0.446 | −0.054 | 0.179 | |

The small model wins in 80–96% of folds against each rival (t-stat of the gain −8 to −11). Drivers by SHAP and coefficients: Low risk rating ≫ growth > ROI.""",
        """- **Cash flow** = revenue − operating cost; NPV = −I₀ + Σ CFₜ/(1.12)ᵗ over 5 years (years 4–5 = year 3).
- **Risk-adjusted E[NPV]** = P × NPV − (1−P) × loss × I₀ (loss 30/50/70% by risk). **PI** = E[NPV] ÷ I₀.
- **Rule:** Fund if PI ≥ 0.10, P ≥ 0.75, risk ≠ High · Reject if E[NPV] ≤ 0 or P < 0.60 · else Review.""",
        """| Scenario | Fund |
|---|---|
| Base: 5 years, 12%, risk-based loss | 21 |
| 3-year / 7-year life | 0 / 42 |
| Discount 10% / 14% | 22 / 15 |
| Loss on failure × 1.5 / none | 19 / 24 |
| Success odds −10 pts | 12 |""",
        """Notebook `01_strategic_initiatives.ipynb` (§1 EDA, §3 CV comparison, §4 calibration, §5 SHAP, §6 NPV, §7 rule, §8 sensitivity) ·
results `Module_01_Strategic_Initiatives/initiatives.json`, `initiatives_decisions.csv` (all 180 decisions) · figures `init_eda`, `init_model`, `init_shap`, `init_decision`.""")
    return story + method

# ===============================================================================================================
# MODULE 2: Credit risk
# ===============================================================================================================
def m2():
    loans = pd.read_csv(DATA / "nova_loans.csv")
    dec = pd.read_csv(RES / "Module_02_Credit_Risk" / "credit_decisions.csv")
    cs = pd.cut(loans.Credit_Score, [0, 600, 650, 700, 750, 900], labels=["<600", "600-650", "650-700", "700-750", "750+"])
    dr = loans.groupby(cs, observed=True).Default_Flag.mean() * 100
    appr = dec[dec.Decision == "Approve"]
    ecl_mult = [float((np.minimum(appr.Predicted_PD * m, 1) * 0.4 * appr.EAD).sum() / appr.EAD.sum() * 100) for m in (1.0, 1.5, 2.0)]
    panels = [
        panel("data", "Weaker credit scores default far more often",
              columns(list(dr.index), list(dr.values), C["data"], lambda v: f"{v:.0f}%", title="Default rate by credit score band", highlight=(0,)),
              "Default rises steadily as credit scores fall; debt-to-income and past defaults show the same pattern. The data carry real signal."),
        panel("model", "Logistic regression is best and the most transparent",
              dots(["Logistic regression", "Random forest", "Gradient boosting"], [0.729, 0.706, 0.702], C["model"], 0.5, "coin flip = 0.50",
                   title="Prediction score of each model (cross-validated ROC-AUC)", lo=0.45, hi=0.8),
              "All three models are well above chance; logistic regression leads by about 2× the fold-to-fold noise and its PDs are already calibrated."),
        panel("money", "Only the good, well-priced loans earn their keep",
              funnel(["loan applications", "positive expected value", "PD < 35% and positive value", "approved: PD < 11%"],
                     [len(dec), int((dec.Expected_Net_Value > 0).sum()), int((dec.Decision != "Reject").sum()), int((dec.Decision == "Approve").sum())],
                     C["money"], title="How many loans pass each test"),
              "Two thirds of the book destroys value at today's pricing. The 836 approved loans (₹68 cr) keep expected loss at 2.8%."),
        panel("risk", "A 50% rise in defaults breaks the risk appetite",
              line([1.0, 1.5, 2.0], ecl_mult, C["risk"], ["PD × 1.0", "PD × 1.5", "PD × 2.0"], "stress on probability of default",
                   "Expected loss of the approved book (% of exposure)", base_idx=0, hline=(3.0, "appetite 3%"), fmt=lambda v: f"{v:.1f}%"),
              "The approved book sits just inside the 3% appetite; PD × 1.5 pushes expected loss to about 4.2%. The margin is thin."),
    ]
    story = story_page("MODULE 2 · CREDIT RISK", "Which loans should NovaFin approve?",
        "For each of the <b>5,000 loan applications</b>: <b>Approve</b>, <b>Review</b> or <b>Reject</b>, keeping expected credit loss within <b>3%</b>?",
        "<b>Approve 836</b> loans (₹68 cr, expected loss 2.8%), Review 815, Reject 3,349. Lending gets capital only for this approved segment.",
        "ML useful", "green",
        [("Started with", "5,000 loans", "20% defaulted, book ₹640 cr"), ("ML predicted", "Probability of default", "good predictor (0.75 out of 1)"),
         ("Money test", "ECL = PD × 40% × loan", "and value after funding cost"), ("Stress test", "PD × 1.5 → 4.2%", "breaks the 3% appetite"),
         ("Decision", "836 approved · ₹68 cr", "PD < 11% and positive value")],
        panels,
        ["<b>Approve only low-PD, positive-value loans.</b> The rest of the book is mispriced: reprice the review queue rather than lend more.",
         "<b>Lending is a thin-margin business here</b> (≈ 0.5–0.6% a year after expected loss), so it gets capital only for the approved segment.",
         "<b>Watch defaults closely:</b> a 50% rise in PD breaks the appetite, so the approved-book ECL is a monitored trigger."],
        "02_credit_risk.ipynb", "§1 EDA · §4 models · §5 calibration · §6 SHAP · §8 bands · §9 ECL · §11 rule · §12 stress",
        ["predict default", "PD per loan + risk category", "ECL and Approve / Review / Reject"])
    method = method_card("MODULE 2", "Credit risk",
        """- **Data:** `nova_loans.csv`, 5,000 × 14; default 20%; amounts in rupees. `Loan_ID` created from the row number.
- **Features:** EMI, payment-to-income, loan-to-income, loan-to-value, total debt-to-income + the raw borrower fields.
- **Leakage check:** dropping `Interest_Rate` changes AUC by < 0.005, so the model does not lean on pricing.""",
        """- **Stratified 80/20** split + **5-fold CV** on the training part.
- **Calibration:** decile calibration curve; Platt scaling compared (calibration gap 0.031 → raw kept; out-of-fold gap 0.008).
- **Out-of-fold PDs** for all 5,000 loans feed ECL.""",
        """| Model | CV ROC-AUC | Test ROC-AUC | Gain vs no-skill | Chosen |
|---|---|---|---|---|
| Logistic regression | **0.729** | 0.746 | +0.229 | ✔ |
| Random forest | 0.706 | 0.752 | +0.206 | |
| Gradient boosting | 0.702 | 0.745 | +0.202 | |

PD bands A < 10% · B 10–20% · C 20–35% · D > 35%; realised default 7% → 14% → 26% → 47%. The brief's 5/15/30% bands put only 7% of loans in "Low".""",
        """- **ECL = PD × LGD (40%) × EAD** (loan amount).
- **Expected net value** = interest − 6% funding cost − expected loss.
- **Approval cut-off** searched on the value / ECL frontier; reject if PD ≥ 35% or value ≤ 0.""",
        """| Stress on approved book | ECL % |
|---|---|
| Base PD, LGD 40% | 2.8% |
| PD × 1.5 | ≈ 4.2% |
| PD × 1.5, LGD 50% | 5.3% |
| Funding cost 4% / 8% | margin 1.2% / 0.3% |""",
        """Notebook `02_credit_risk.ipynb` · results `Module_02_Credit_Risk/credit.json`, `credit_decisions.csv` (Loan_ID, PD, band, EAD, ECL, value, decision) ·
figures `credit_eda`, `credit_model_curves`, `credit_shap`, `credit_bands`, `credit_value`, `credit_frontier`.""")
    return story + method

# ===============================================================================================================
# MODULE 3: Fraud
# ===============================================================================================================
def m3():
    tx = pd.read_csv(DATA / "nova_transactions.csv")
    ratio = tx.Amount / tx.Historical_Avg_Transaction
    q = pd.qcut(ratio, 5, labels=["lowest 20%", "2nd", "3rd", "4th", "highest 20%"])
    fr = tx.groupby(q, observed=True).Fraud_Flag.mean() * 100
    f = J("Module_03_Fraud_Detection", "fraud.json")
    st = f["stress"]
    panels = [
        panel("data", "Fraud = an amount far above the customer's normal",
              columns(list(fr.index), list(fr.values), C["data"], lambda v: f"{v:.1f}%", title="Fraud rate by amount ÷ customer's usual spend (quintiles)",
                      highlight=(4,)),
              "In the top fifth of 'unusual' amounts the fraud rate is several times the 2.3% average. Location, merchant and hour do not matter."),
        panel("model", "Labels beat anomaly detection",
              dots(["Random forest", "Gradient boosting", "Logistic regression", "Amount-ratio rule", "Isolation Forest"],
                   [0.142, 0.127, 0.094, 0.094, 0.044], C["model"], 0.024, "random = 0.024",
                   title="Precision-recall score on the untouched test period (PR-AUC)", lo=0.0, hi=0.17, fmt=lambda v: f"{v:.3f}"),
              "The random forest finds fraud 6× better than chance. Isolation Forest (no labels) flags unusual, not fraudulent, transactions."),
        panel("money", "38% lower fraud cost than doing nothing",
              hbars(["Random forest", "Amount-ratio rule", "Isolation Forest", "No model", "Check everything"],
                    [8.98, 10.48, 14.31, 14.40, 29.28], C["money"], lambda v: f"₹{v:.1f} lakh", title="Operating cost on the test period (₹ lakh)"),
              "₹10,000 per missed fraud + ₹500 per false alarm. Checking 7.5% of transactions catches 51% of fraud: ₹90,000 saved per 1,000 transactions."),
        panel("risk", "The saving holds when costs change",
              line([5, 10, 20], [round(st["Missed fraud ₹5,000"]["saving"] * 100), round(st["Base (₹10,000 / ₹500)"]["saving"] * 100),
                                 round(st["Missed fraud ₹20,000"]["saving"] * 100)],
                   C["risk"], ["₹5,000", "₹10,000", "₹20,000"], "cost of one missed fraud", "Saving vs no model (%)", base_idx=1,
                   extra=(f"{round(st['Model degraded (noise 0.15)']['saving'] * 100)}% if model degrades", round(st["Model degraded (noise 0.15)"]["saving"] * 100)),
                   fmt=lambda v: f"{v:.0f}%"),
              "Whether fraud losses halve or double, the model still saves 20–50%; even a noticeably weaker model saves 28%."),
    ]
    story = story_page("MODULE 3 · FRAUD DETECTION", "Which transactions should the fraud team check?",
        "Flag suspicious transactions so NovaFin <b>catches most fraud</b> without <b>wasting money on false alarms</b>.",
        "Investigate the <b>top 7.5%</b> of transactions by model score: catches <b>51% of fraud</b> and cuts fraud cost by <b>38%</b>.",
        "ML useful", "green",
        [("Started with", "30,000 transactions", "2.3% fraud, Jan 2025 – Aug 2026"), ("ML predicted", "Fraud probability", "6× better than chance"),
         ("Money test", "₹10,000 vs ₹500", "missed fraud vs false alarm"), ("Stress test", "20–50% saving", "under every cost change"),
         ("Decision", "Check top 7.5%", "38% lower cost · no capital needed")],
        panels,
        ["<b>Put the model live at the cost-optimal threshold</b>: it is an operating-cost saving, not a capital line.",
         "<b>Use Isolation Forest only as a second line</b> to spot new patterns; it cannot replace a model trained on known fraud.",
         "<b>Monitor monthly</b> (precision-recall, alert volume) and retrain when fraudsters adapt."],
        "03_fraud.ipynb", "§1 EDA · §2 features · §4 models · §5 Isolation Forest · §8 cost threshold · §9 stress",
        ["EDA of fraud by type, amount, location, behaviour", "supervised model", "Isolation Forest", "cost-based threshold"])
    method = method_card("MODULE 3", "Fraud detection",
        """- **Data:** `nova_transactions.csv`, 30,000 × 12, fraud 2.3% (684).
- **Features:** log amount, **amount ÷ customer average**, hour, night, weekend, prior transactions, hours since last, new device / new city (history from **earlier** transactions only), type, merchant, location.
- IDs (transaction, customer, device) excluded.""",
        """- **Time split:** train 2025 (60%) · validation Jan–Apr 2026 (20%) · **test May–Aug 2026** (20%, 144 frauds).
- Model and threshold chosen on **validation**, frozen for test.
- Class weighting for the rare class; PR-AUC as the main ranking metric.""",
        """| Method (test period) | PR-AUC | ROC-AUC | Cost ₹ lakh | Saving | Chosen |
|---|---|---|---|---|---|
| Random forest | **0.142** | 0.805 | **8.98** | 37.6% | ✔ |
| Gradient boosting | 0.127 | 0.808 | 9.10 | 36.8% | |
| Logistic regression | 0.094 | 0.775 | 9.90 | 31.2% | |
| Amount-ratio rule (no ML) | 0.094 | 0.772 | 10.48 | 27.3% | |
| Isolation Forest (no labels) | 0.044 | 0.623 | 14.31 | 0.7% | |""",
        """- **Cost(t) = 10,000 × missed frauds + 500 × false alarms**, scanned over 800 thresholds on validation.
- Textbook threshold 500 / 10,500 ≈ 4.8% fails because class-weighted probabilities are inflated, which is why the threshold is learned from the cost curve.""",
        """| Case | Saving vs no model |
|---|---|
| Base (₹10,000 / ₹500) | 38% |
| Missed fraud ₹5,000 / ₹20,000 | 20% / 50% |
| Investigation ₹1,000 | 20% |
| Model degraded (noise) | 28–38% |""",
        """Notebook `03_fraud.ipynb` · results `Module_03_Fraud_Detection/fraud.json` · figures `fraud_eda`, `fraud_curves`, `fraud_shap`, `fraud_cost_curve`.""")
    return story + method

# ===============================================================================================================
# MODULE 4: Churn and CLV
# ===============================================================================================================
def m4():
    cust = pd.read_csv(DATA / "nova_customers.csv")
    q = pd.qcut(cust.Digital_Usage, 5, labels=["lowest", "2nd", "3rd", "4th", "highest"])
    ch = cust.groupby(q, observed=True).Churn_Flag.mean() * 100
    j = J("Module_04_Churn_CLV", "churn.json"); bt = j["targeting_backtest"]
    panels = [
        panel("data", "Churners look just like everyone else",
              columns(list(ch.index), list(ch.values), C["data"], lambda v: f"{v:.1f}%", title="Churn rate by digital-usage quintile",
                      highlight=None, ref=cust.Churn_Flag.mean() * 100, ref_label="average 1.8%"),
              "Churn sits near the 1.8% average in every group (usage, products, complaints, tenure); no variable separates churners."),
        panel("model", "No model can predict churn here",
              dots(["Gradient boosting", "Logistic regression", "Random forest"], [0.510, 0.494, 0.488], C["model"], 0.5, "coin flip = 0.50",
                   title="Prediction score of each model (cross-validated ROC-AUC)", lo=0.42, hi=0.58),
              "All three models score like a coin flip; their tiny gains are smaller than the fold-to-fold noise. An honest negative result."),
        panel("money", "So target by value: 3× more value reached",
              hbars(["Churn × lifetime value", "Lifetime value only", "Churn score only", "Random 1,000"],
                    [bt["EVaR (churn x CLV)"]["value of churners reached (₹ cr)"], bt["CLV only"]["value of churners reached (₹ cr)"],
                     bt["Churn score only"]["value of churners reached (₹ cr)"], bt["Random 1,000"]["value of churners reached (₹ cr)"]],
                    C["money"], lambda v: f"₹{v:.2f} cr", title="Lifetime value of real churners reached by each 1,000-call list", highlight=(0, 1)),
              "Churn hits rich and ordinary customers alike, so calling the most valuable customers protects the most money."),
        panel("risk", "The campaign pays unless calls rarely work",
              line([10, 20, 30, 50], [-2.4, 10.2, 22.8, 47.9], C["risk"], ["10%", "20%", "30%", "50%"], "share of would-be churners an RM call saves",
                   "Net value of 1,000 RM calls at ₹1,500 each (₹ lakh)", base_idx=2, fmt=lambda v: f"₹{v:.0f}L"),
              "At a 30% save rate the campaign nets ₹22.8 lakh (ROI 152%). It turns negative only if calls save fewer than about 1 in 10."),
    ]
    story = story_page("MODULE 4 · CHURN & CUSTOMER VALUE", "If we can call only 1,000 customers, whom should we call?",
        "Predict which customers will <b>leave</b>, value each customer, and pick the <b>1,000</b> that relationship managers should contact.",
        "Churn is <b>not predictable</b> from this data, so call the <b>1,000 highest-value customers at risk</b>: net <b>₹22.8 lakh</b> (ROI 152%).",
        "No churn signal", "red",
        [("Started with", "5,000 customers", "1.8% churned (89)"), ("ML predicted", "Chance of leaving", "no better than a coin flip"),
         ("Money test", "Lifetime value", "₹174 cr total; top 20% hold 42%"), ("Stress test", "Pays if ≥ 1 in 10 saved", "save-rate × call-cost grid"),
         ("Decision", "1,000 RM calls", "ranked by churn × value")],
        panels,
        ["<b>Don't trust a churn score built on this data</b>; it would give relationship managers false precision.",
         "<b>Protect value, not probability:</b> the RM list is ranked by lifetime value at risk (saved for the RM team).",
         "<b>The franchise value is in deposits (3% margin) and wealth (1.8% fee)</b>, which supports the digital and wealth lines."],
        "04_churn_clv.ipynb", "§1 EDA · §2 models · §3 CLV formula + lifetime CLV · §4 segments + targeting · §5 economics",
        ["churn prediction", "customer lifetime value", "4 segments + whom to call (1,000)"])
    method = method_card("MODULE 4", "Churn and CLV",
        """- **Data:** `nova_customers.csv`, 5,000 × 13; churn 1.8% (89). Amounts in rupees.
- **Features:** all customer fields + total assets, assets ÷ income, loans ÷ income. **`Estimated_CLV` excluded** from churn features (agreed leakage rule).""",
        """- **Repeated stratified 5-fold CV × 5**; out-of-fold churn score for every customer, rescaled to the 1.8% average.
- **Signal check:** gain over no-skill ÷ fold-to-fold std (signal-to-noise); top-decile lift.
- Targeting rules **backtested** against actual churners.""",
        """| Model | CV ROC-AUC | Gain vs no-skill | Signal-to-noise |
|---|---|---|---|
| Gradient boosting | 0.510 | +0.010 | 0.18 |
| Logistic regression | 0.494 | −0.006 | −0.11 |
| Random forest | 0.488 | −0.012 | −0.23 |

No model is worth choosing; top-decile lift ≈ 1.1. Value-led targeting is used instead.""",
        """- **Supplied CLV is an exact one-year margin** (R² = 1): 4% income + 3% deposits + 1.2% loans + 1.8% investments − ₹5,000 per complaint.
- **Lifetime CLV** = margin × Σ (1 − churn)ᵗ⁻¹ ÷ 1.12ᵗ over 10 years (≈ 5.3× margin).
- **Value at risk** = P(churn) × lifetime CLV; value protected = save rate × Σ value at risk − call cost.""",
        """| Save rate \\ cost per call | ₹500 | ₹1,500 | ₹3,000 |
|---|---|---|---|
| 10% | +7.6 | −2.4 | −17.4 |
| 30% | +32.8 | **+22.8** | +7.8 |
| 50% | +57.9 | +47.9 | +32.9 |

(net ₹ lakh; churn flag assumed annual)""",
        """Notebook `04_churn_clv.ipynb` · results `Module_04_Churn_CLV/churn.json`, **`churn_top1000.csv` (the RM call list)** · figures `churn_eda`, `churn_clv`.""")
    return story + method

# ===============================================================================================================
# MODULE 5: Equity returns
# ===============================================================================================================
def m5():
    e = J("Module_05_Equity_Returns", "equity.json")
    stats = pd.DataFrame(e["stock_stats"]).T.sort_values("Ann_Return", ascending=False)
    pred = pd.read_csv(RES / "Module_05_Equity_Returns" / "equity_predictions.csv", parse_dates=["Date"]).dropna(subset=["Fwd_Ret"])
    top = pred.groupby("Date").apply(lambda d: d.nlargest(5, "Pred_Ridge").Fwd_Ret.mean() - d.Fwd_Ret.mean())
    cum = (1 + top).cumprod() - 1
    pts = [0, len(cum) // 4, len(cum) // 2, 3 * len(cum) // 4, len(cum) - 1]
    q = e["quality"]
    panels = [
        panel("data", "Stocks differ a lot over five years",
              columns(list(stats.index), list(stats.Ann_Return * 100), C["data"], lambda v: f"{v:.0f}", title="Average annual return per stock, 2021–26 (%)",
                      highlight=(0, 1, 2), rotate=45),
              "Returns range from about 0% to 34% a year, so picking the right stocks would matter, if their future order could be predicted."),
        panel("model", "No model ranks next month's winners reliably",
              dots(["Ridge", "Gradient boosting", "Random forest", "Momentum (no ML)"],
                   [q["Ridge"]["mean IC"], q["Gradient boosting"]["mean IC"], q["Random forest"]["mean IC"], q["Momentum"]["mean IC"]],
                   C["model"], 0.0, "no skill = 0", title="Rank IC: does the forecast order match next month's order?", lo=-0.05, hi=0.08, fmt=lambda v: f"{v:.3f}"),
              "Ridge has the best rank IC (0.056) but its t-stat is 1.2, below 2, over 38 months. Not statistically reliable."),
        panel("money", "Holding all 15 beats picking 5",
              hbars(["Equal-weight, all 15", "Top 5 by gradient boosting", "Top 5 by Ridge", "Top 5 by momentum", "Top 5 by random forest"],
                    [e["portfolios"]["Equal-weight (all 15)"]["Sharpe"], e["portfolios"]["Top 5: Gradient boosting"]["Sharpe"],
                     e["portfolios"]["Top 5: Ridge"]["Sharpe"], e["portfolios"]["Top 5: Momentum"]["Sharpe"], e["portfolios"]["Top 5: Random forest"]["Sharpe"]],
                    C["money"], lambda v: f"{v:.2f}", title="Risk-adjusted return (Sharpe ratio) after 10 bps costs"),
              "Concentrating in 5 stocks doubles volatility; no top-5 portfolio beats equal-weight significantly (all p > 0.4)."),
        panel("risk", "The ML edge is not stable over time",
              line(list(range(5)), [round(cum.iloc[i] * 100, 1) for i in pts], C["risk"],
                   [d.strftime("%b %y") for d in cum.index[pts]], "out-of-sample months", "Cumulative extra return of Ridge top-5 vs average (%)",
                   fmt=lambda v: f"{v:+.1f}%"),
              "The extra return drifts up and down month to month (rank IC positive in only 57% of months); it could vanish in another sample."),
    ]
    story = story_page("MODULE 5 · EQUITY MARKETS", "Can ML pick the stocks that will do best?",
        "Forecast next month's return for <b>15 stocks</b>, rank them, and buy the top ones: does it beat simply <b>holding all 15</b>?",
        "<b>No reliable edge.</b> The best signal (rank IC 0.056) is not significant, and <b>holding all 15 equally</b> gives the best risk-adjusted return.",
        "Not significant", "red",
        [("Started with", "15 stocks, 5.5 years", "daily prices and volume"), ("ML predicted", "Next-month rank", "walk-forward, 38 months"),
         ("Money test", "Top-5 portfolio", "after 10 bps trading costs"), ("Stress test", "t-stat 1.2", "below 2: not reliable"),
         ("Decision", "Diversify", "ML only as a small tilt (Module 6)")],
        panels,
        ["<b>Do not concentrate on ML stock picks;</b> diversification does more for risk-adjusted return here.",
         "<b>Judge a stock signal by its ranking skill after costs</b>, not by R² or a lucky backtest.",
         "<b>Pass the forecasts to portfolio construction</b> (Module 6), where they can tilt, not drive, the weights."],
        "05_equity_returns.ipynb", "§1 audit · §2 features · §4 walk-forward · §5 IC table · §6 top-5 portfolios · §7 drivers",
        ["predict future returns with several models", "rank stocks and build a portfolio at each rebalance"])
    method = method_card("MODULE 5", "Equity returns",
        """- **Data:** `nova_market_data.csv`, 15 tickers × 1,457 days (Jan 2021 – Aug 2026). Supplied `Return`, `Momentum_20D`, `Volatility_20D` verified as past-only.
- **Features at each month-end:** 1- and 3-month return, 6-1 momentum, 1- and 3-month volatility, 6-month beta, volume trend, distance from 6-month high, range, macro columns.
- **Target:** next-month return minus the 15-stock average.""",
        """- **Walk-forward:** at each of 38 month-ends (Jul 2023 →) refit on all earlier months only, then forecast.
- **Metrics:** monthly rank IC (Spearman) and its t-stat, hit rate, top-5 equal-weight portfolio after 10 bps per unit traded.""",
        """| Model | Mean rank IC | IC t-stat | Top-5 Sharpe | Chosen |
|---|---|---|---|---|
| Ridge | **0.056** | 1.23 | 0.72 | ✔ (best IC) |
| Gradient boosting | 0.014 | 0.35 | 1.03 | |
| Random forest | 0.004 | 0.09 | 0.24 | |
| Momentum (no ML) | −0.024 | −0.49 | 0.34 | |
| Equal-weight all 15 (no view) | – | – | **1.32** | |""",
        """- **Portfolio return** = average next-month return of the 5 picks − 2 × 10 bps × share of names changed.
- **Sharpe** = (annual return − 7%) ÷ annual volatility; max drawdown; paired t-test of monthly difference vs equal-weight.""",
        """- Rebalance monthly; top 5 of 15; 24 months minimum training; costs 10 bps.
- Data caveats: macro columns differ by stock on the same day (not real macro); stocks almost uncorrelated (0.004); survivorship (today's names).""",
        """Notebook `05_equity_returns.ipynb` · results `Module_05_Equity_Returns/equity.json`, `equity_predictions.csv` (used by Module 6) · figures `equity_eda`, `equity_backtest`, `equity_shap`.""")
    return story + method

# ===============================================================================================================
# MODULE 6: Portfolio optimisation
# ===============================================================================================================
def m6():
    p = J("Module_06_Portfolio_Optimisation", "portfolio.json"); perf = p["performance"]
    e = J("Module_05_Equity_Returns", "equity.json")
    single_vol = float(np.mean([v["Ann_Vol"] for v in e["stock_stats"].values()])) * 100
    names = {"Equal-weight": "Equal_weight", "ML tilt": "ML_tilt", "ML mean-variance": "ML_mean_variance",
             "Minimum variance": "Minimum_variance", "Markowitz max-Sharpe": "Markowitz_max_Sharpe"}
    final = {k: float((1 + pd.read_csv(RES / "Module_06_Portfolio_Optimisation" / f"backtest_{v}.csv").net).prod() * 100) for k, v in names.items()}
    stress = p["stress"]["Equal-weight"]
    order = ["ML tilt", "ML mean-variance", "Equal-weight", "Minimum variance", "Markowitz max-Sharpe"]
    panels = [
        panel("data", "Spreading money across stocks cuts risk sharply",
              columns(["one stock", "5 stocks (ML top 5)", "all 15, equal"], [single_vol, e["portfolios"]["Top 5: Ridge"]["Ann. vol"] * 100,
                      perf["Equal-weight"]["Ann. vol"] * 100], C["data"], lambda v: f"{v:.0f}%", title="Annual volatility", highlight=(2,)),
              "A single stock swings ±29% a year; holding all 15 equally cuts that to 6%, because these stocks barely move together."),
        panel("model", "ML portfolios look better, but not provably",
              dots(order, [perf[k]["Sharpe"] for k in order], C["model"], perf["Equal-weight"]["Sharpe"], "equal-weight = 1.30",
                   title="Sharpe ratio after costs (higher = better risk-adjusted)", lo=0.0, hi=1.6, best=0),
              "ML tilt (+0.13) and ML mean-variance (+0.08) beat equal-weight but not significantly (p 0.16 / 0.12); classic Markowitz fails."),
        panel("money", "What ₹100 cr became over 38 months",
              hbars(order, [final[k] for k in order], C["money"], lambda v: f"₹{v:.0f} cr", title="Value of ₹100 cr invested Jul 2023, after costs",
                    highlight=(2,), ref=100, ref_label="start ₹100 cr"),
              "Equal-weight grew steadily with tiny drawdowns; ML mean-variance earned more but traded its whole portfolio every month."),
        panel("risk", "In a crash, diversification stops working",
              columns(["normal month", "crisis month", "market −25%"], [stress["VaR 99% 1m, normal"] * 100, stress["VaR 99% 1m, crisis"] * 100,
                      abs(stress["Loss in -25% market shock"]) * 100], C["risk"], lambda v: f"{v:.0f}%",
                      title="Possible loss of the equal-weight sleeve (99% VaR / shock)", highlight=(1, 2)),
              "When correlations jump to 0.6 and volatility doubles, the monthly 99% VaR rises from 5% to 30%. Size the equity line on the crisis number."),
    ]
    story = story_page("MODULE 6 · PORTFOLIO OPTIMISATION", "How should the equity money be spread?",
        "Turn forecasts into an <b>actual portfolio</b>: compare <b>equal-weight</b>, <b>traditional Markowitz</b> and <b>ML-based</b> portfolios after costs.",
        "<b>Equal-weight</b> (Sharpe 1.30) is chosen; ML portfolios are not proven better. The equity line gets <b>₹250 cr</b>, planned at 13.3% a year.",
        "Not significant", "red",
        [("Started with", "5 strategies", "same 38 months, same costs"), ("ML predicted", "Return forecasts", "from Module 5 (Ridge)"),
         ("Money test", "Sharpe after costs", "equal-weight 1.30"), ("Stress test", "Crisis VaR 30%", "vs 5% in normal months"),
         ("Decision", "Equal-weight · ₹250 cr", "ML tilt kept on watch")],
        panels,
        ["<b>Invest the equity line equal-weight</b>: simplest, cheapest to trade, and best proven risk-adjusted return.",
         "<b>Run the ML tilt as a paper portfolio</b>; adopt it only if its edge survives another year.",
         "<b>Size equity on the crisis loss</b> (≈ 25–30%), which is why the allocation caps equity at 25% of capital."],
        "06_portfolio.ipynb", "§1 building blocks · §2 backtest · §3 metrics + comparison · §4 sensitivity · §5 stress",
        ["equal-weight vs Markowitz vs ML-return portfolio", "backtest and performance metrics"])
    method = method_card("MODULE 6", "Portfolio optimisation",
        """- **Inputs:** daily returns of 15 stocks; ML forecasts from Module 5 (`equity_predictions.csv`).
- **Strategies:** equal-weight · Markowitz max-Sharpe (1-year sample means & covariance) · minimum variance (Ledoit-Wolf covariance) · ML mean-variance (Ridge forecasts) · ML tilt of equal-weight.""",
        """- Same 38 out-of-sample months (Jul 2023 – Aug 2026), **monthly rebalance**, long-only, ≤ 30% per stock, 10 bps per unit traded.
- Weights use **only data up to the rebalance date**; weights drift with prices between rebalances.""",
        """| Strategy | Return | Vol | Sharpe | Max DD | Turnover/mo | p vs EW | Chosen |
|---|---|---|---|---|---|---|---|
| ML tilt | 18.2% | 7.0% | 1.43 | −3.0% | 31% | 0.16 | |
| ML mean-variance | 23.0% | 10.5% | 1.38 | −5.5% | 103% | 0.12 | |
| **Equal-weight** | 16.1% | 6.3% | 1.30 | −2.4% | 7% | – | ✔ |
| Minimum variance | 15.9% | 6.3% | 1.28 | −2.7% | 7% | 0.44 | |
| Markowitz max-Sharpe | 8.4% | 12.3% | 0.15 | −13.3% | 37% | 0.27 | |

Rule: a more complex strategy must add > 0.10 Sharpe **and** p < 0.10; none does.""",
        """- **Markowitz:** maximise (w'μ − r_f) ÷ √(w'Σw); **GMVP:** minimise w'Σw (Session 13).
- **Metrics:** Sharpe, Sortino, max drawdown, 1-month 99% VaR = −(μ − 2.33σ), turnover, effective N = 1 ÷ Σw².""",
        """- Costs 0 / 10 / 30 bps: ML mean-variance Sharpe 1.49 / 1.38 / 1.15 vs equal-weight 1.32 / 1.30 / 1.26.
- Markowitz with 126 / 252 / 504-day windows: Sharpe −0.17 / 0.15 / 0.33 (unstable).
- Crisis: correlations 0.6, volatility × 2 → VaR 30% for every strategy.""",
        """Notebook `06_portfolio.ipynb` · results `Module_06_Portfolio_Optimisation/portfolio.json` + monthly `backtest_*.csv` · figure `portfolio_backtest`.""")
    return story + method

# ===============================================================================================================
# MODULE 7: HFT
# ===============================================================================================================
def m7():
    h = pd.read_csv(DATA / "nova_hft_orderbook.csv", usecols=["OBI_Level1", "Price_Move_Class"])
    b = pd.cut(h.OBI_Level1, [-1.01, -0.6, -0.2, 0.2, 0.6, 1.01], labels=["strong sell", "sell", "balanced", "buy", "strong buy"])
    up = h.groupby(b, observed=True).Price_Move_Class.apply(lambda s: (s == "UP").mean() * 100)
    j = J("Module_07_HFT", "hft.json"); s = j["stress"]
    panels = [
        panel("data", "The order book tilts the next move",
              columns(list(up.index), list(up.values), C["data"], lambda v: f"{v:.0f}%", title="Share of next 100 ms moves that go UP, by order-book imbalance",
                      highlight=(4,)),
              "When buy orders dominate the book, the price usually ticks up next; when sell orders dominate, it ticks down. Correlation 0.51."),
        panel("model", "ML adds little over a one-line rule",
              dots(["Multinomial logistic", "Random forest", "Gradient boosting", "Rule: sign of imbalance"],
                   [0.4431, 0.4432, 0.4432, 0.4409], C["model"], 0.199, "no skill = 0.20",
                   title="Direction accuracy across UP / DOWN / FLAT (macro-F1)", lo=0.15, hi=0.5, fmt=lambda v: f"{v:.3f}"),
              "All three models tie and barely beat the trader's rule of thumb; FLAT moves are never predicted. The simplest model is kept."),
        panel("money", "Profitable on paper…",
              hbars(["ML signal (logistic)", "Rule: sign of imbalance"], [j["signal_test"]["Multinomial logistic"]["Net ₹ lakh/day"],
                    j["signal_test"]["Rule: sign of OBI"]["Net ₹ lakh/day"]], C["money"], lambda v: f"₹{v:.1f} lakh",
                    title="Net profit per day on the 4 test days (₹10 lakh per trade)"),
              "≈ 3,800 trades a day, 62% right, 1.65 bp net per trade after crossing the spread and 0.5 bp fees."),
        panel("risk", "…but the edge disappears with real-world friction",
              line([1, 2, 3], [round(s["Base"]["Net ₹ lakh/day"], 1), round(s["Costs x2"]["Net ₹ lakh/day"], 1), round(s["Costs x3"]["Net ₹ lakh/day"], 1)],
                   C["risk"], ["costs × 1", "costs × 2", "costs × 3"], "trading costs", "Net profit per day under stress (₹ lakh)", base_idx=0,
                   extra=(f"{s['Delay 1 event']['Net ₹ lakh/day']:.1f} if 1 event late", round(s["Delay 1 event"]["Net ₹ lakh/day"], 1)), fmt=lambda v: f"{v:+.1f}"),
              "Double the costs or react one event late and the profit turns into a loss. This synthetic market is far more generous than a real one."),
    ]
    story = story_page("MODULE 7 · HIGH-FREQUENCY TRADING", "Can the order book be traded profitably?",
        "Use <b>limit-order-book</b> data to predict the next <b>100 ms</b> move (UP / DOWN / FLAT): does it earn money after costs?",
        "The signal is real, but the <b>profit is fragile</b>: it vanishes if costs double or orders arrive late. Fund only a <b>₹10 cr pilot</b>; use the signal for <b>execution timing</b>.",
        "Signal real · profit fragile", "amber",
        [("Started with", "120,000 book events", "10 stocks, 20 trading days"), ("ML predicted", "Next 100 ms direction", "UP / DOWN / FLAT"),
         ("Money test", "₹6.3 lakh/day", "after spread and fees"), ("Stress test", "Costs × 2 → loss", "also 1-event delay"),
         ("Decision", "₹10 cr pilot", "kill switch; execution first")],
        panels,
        ["<b>No material capital for proprietary HFT</b>: plan on zero return; cap the pilot at ₹10 cr with a hard stop-loss.",
         "<b>Use the signal to time client orders:</b> buying on 'buy now' calls avoids about 7 bp per child order.",
         "<b>Re-test on real market data</b> before trusting any HFT profit."],
        "07_hft.ipynb", "§1 EDA · §2 features · §4 models · §5 signal backtest · §6 stress · §7 execution use",
        ["short-horizon direction prediction (UP/DOWN/FLAT)", "turn probabilities into a trading signal and backtest"])
    method = method_card("MODULE 7", "High-frequency trading",
        """- **Data:** `nova_hft_orderbook.csv`, 120,000 events × 33, 10 stocks, 20 days. Target `Price_Move_Class` (UP 42%, DOWN 42%, FLAT 16%; FLAT = |move| < 1.2 bp).
- **Leakage:** `Future_Return_100ms` and `Future_Price_100ms` excluded from features.
- **Features:** imbalance (levels 1–3), microprice − mid, spread, depth, arrival/cancel rates, volatility, trade side, event type + previous-event history within stock-day.""",
        """- **Split by trading day:** 12 train · 4 validation · 4 test (never random).
- Model by validation macro-F1; trade threshold chosen on validation, frozen for test.
- Profit per trade = direction × next move − full spread − 0.5 bp fees.""",
        """| Model | Macro-F1 (val) | Net ₹ lakh/day (test) | Net bp/trade | Chosen |
|---|---|---|---|---|
| Multinomial logistic | 0.443 | 6.30 | 1.65 | ✔ simplest |
| Random forest | 0.443 | 6.23 | 1.62 | |
| Gradient boosting | 0.443 | 6.32 | 1.66 | |
| Rule: sign of imbalance | 0.441 | 4.64 | 0.78 | |
| No-skill (class mix) | 0.199 | – | – | |""",
        """- **Signal:** long if P(UP) > 0.55, short if P(DOWN) > 0.55, else no trade.
- **Execution test:** next move when the model says "buy now" (+3.4 bp) vs "wait" (−3.9 bp).""",
        """| Stress | Net ₹ lakh/day |
|---|---|
| Base | +6.3 |
| Costs × 2 / × 3 | −0.8 / −8.0 |
| 1 / 3 events late | −1.1 / −4.1 |
| Costs × 2 + 1 late | −8.0 |

Caveat: average move (4.7 bp) is 3.5× the spread (1.3 bp), which is unrealistic.""",
        """Notebook `07_hft.ipynb` · results `Module_07_HFT/hft.json` · figures `hft_eda`, `hft_model`, `hft_pnl`.""")
    return story + method

# ===============================================================================================================
# MODULE 8: Derivatives
# ===============================================================================================================
def m8():
    o = pd.read_csv(DATA / "nova_options.csv")
    err = o.Market_Price - o.Black_Scholes_Price
    tb = pd.cut(o.Time_to_Maturity, [0, 0.25, 0.75, 1.25, 2.01], labels=["< 3 m", "3–9 m", "9–15 m", "15–24 m"])
    rm = err.groupby(tb, observed=True).apply(lambda e: np.sqrt((e ** 2).mean()))
    j = J("Module_08_Derivatives", "options.json"); pr = j["pricing"]; st = j["stress"]; v = j["var"]; hd = j["hedge"]
    panels = [
        panel("data", "Market prices sit close to Black-Scholes",
              columns(list(rm.index), list(rm.values), C["data"], lambda v: f"₹{v:.1f}", title="Typical gap between market price and Black-Scholes (RMSE, ₹)",
                      highlight=None),
              "Our Black-Scholes matches the supplied price to ₹0.27. Gaps to the market are larger for longer, pricier options: noise of a few percent."),
        panel("model", "ML cannot beat the theory here",
              dots(["Black-Scholes", "BS + ML correction", "Gradient boosting", "Random forest"],
                   [pr["Black-Scholes (theory)"]["RMSE ₹"], pr["Hybrid: BS + ML correction"]["RMSE ₹"], pr["Gradient boosting"]["RMSE ₹"],
                    pr["Random forest"]["RMSE ₹"]], C["model"], pr["Black-Scholes (theory)"]["RMSE ₹"], "Black-Scholes = 9.48",
                   title="Pricing error on test options (RMSE ₹, lower = better)", lo=8, hi=16, fmt=lambda x: f"₹{x:.2f}"),
              "Every ML model adds error (plain Ridge: ₹59.5). Market prices are theory plus noise, so there is nothing extra to learn."),
        panel("money", "The book earns time decay; hedging is cheap",
              columns(["premium received", "time decay / yr", "re-hedging cost / yr"], [hd["premium_received_cr"], hd["theta_income_cr_per_year"],
                      hd["annual_rehedge_cost_cr"]], C["money"], lambda x: f"₹{x:.1f} cr", title="Short options book: income vs hedge cost (₹ cr)", highlight=(0, 1)),
              "Selling 100 of every option brings ₹19.4 cr of premium and ≈ ₹7.5 cr a year of time decay; daily delta hedging costs ≈ ₹2.2 cr."),
        panel("risk", "Hedging removes everyday risk, not volatility risk",
              columns(["1-day VaR unhedged", "1-day VaR hedged", "volatility +10 pts", "crash (hedged)"],
                      [v["Unhedged short book"]["VaR 99% 1-day ₹ cr"], v["Delta-hedged book"]["VaR 99% 1-day ₹ cr"],
                       abs(st["Vol spike only: +10 pts"]["Delta-hedged ₹ cr"]), abs(st["Crash: spot -20%, vol +10 pts"]["Delta-hedged ₹ cr"])],
                      C["risk"], lambda x: f"₹{x:.2f} cr" if x < 1 else f"₹{x:.1f} cr", title="Possible loss of the book (₹ cr)", highlight=(2, 3), rotate=15),
              "The delta hedge cuts 1-day VaR by 80%. A volatility jump still costs ₹5.4 cr and a crash ₹10 cr: that needs a buffer and a vega limit."),
    ]
    story = story_page("MODULE 8 · DERIVATIVES", "Can ML price options, and how do we hedge them?",
        "Compare <b>ML option prices</b> with the <b>Black-Scholes</b> benchmark, then measure and <b>hedge</b> the risk of NovaFin's options book.",
        "<b>Black-Scholes wins</b> (ML adds error). Delta hedging cuts daily risk by <b>80%</b>; hold a <b>₹20 cr buffer</b> and a vega limit for volatility shocks.",
        "Black-Scholes wins", "red",
        [("Started with", "10,000 options", "15 underlyings, calls and puts"), ("ML predicted", "Option price", "vs Black-Scholes benchmark"),
         ("Money test", "₹19.4 cr premium", "time decay ₹7.5 cr / yr"), ("Stress test", "Crash −₹10 cr", "volatility jump −₹5.4 cr"),
         ("Decision", "Hedge + ₹20 cr buffer", "delta hedge daily · vega limit")],
        panels,
        ["<b>Keep Black-Scholes for pricing and hedging</b>; ML would need a real volatility surface to add value.",
         "<b>Delta-hedge the book daily</b>: cheap (≈ ₹2.2 cr a year) and removes most everyday risk.",
         "<b>Hold a ₹20 cr buffer and a vega limit</b> for crashes and volatility jumps that hedging cannot remove."],
        "08_options.ipynb", "§1 Black-Scholes · §2 ML pricing · §3 Greeks · §4 hedge + VaR · §5 stress · §6 hedge cost",
        ["Black-Scholes theoretical price vs market", "ML pricing vs Black-Scholes", "Greeks, simple hedge, VaR"])
    method = method_card("MODULE 8", "Derivatives",
        """- **Data:** `nova_options.csv`, 10,000 options (4,945 calls / 5,055 puts) on 15 stocks; maturity 0.03–2 years; volatility 8–54%.
- **ML target:** price ÷ strike (removes scale). **Features:** log-moneyness, intrinsic value ÷ K, maturity, volatility, σ√T, rate, call/put.
- **Leakage:** the supplied Black-Scholes price is not an ML input (only the labelled hybrid uses it).""",
        """- **80/20 split** stratified by option type + **5-fold CV** on the training part.
- Errors analysed by moneyness and maturity bucket.
- **VaR:** historical simulation, 252 real days of joint stock returns, book re-priced exactly each day.""",
        """| Method (test) | RMSE ₹ | vs Black-Scholes | Chosen |
|---|---|---|---|
| **Black-Scholes** | **9.48** | benchmark | pricing model |
| Hybrid: BS + ML correction | 10.32 | +0.84 | |
| Gradient boosting | 12.74 | +3.26 | ✔ best ML |
| Random forest | 14.64 | +5.16 | |
| Ridge (linear) | 59.53 | +50.06 | |""",
        """- **Black-Scholes:** d₁ = [ln(S/K) + (r + σ²/2)T] ÷ σ√T; C = S·N(d₁) − K·e⁻ʳᵀ·N(d₂); P = K·e⁻ʳᵀ·N(−d₂) − S·N(−d₁).
- **Greeks:** delta, gamma, vega, theta of the short book (100 of each option).
- **Hedge:** trade −(book delta) shares per stock; re-hedging cost ≈ 10 bps × daily delta change.""",
        """| Case | Unhedged | Delta-hedged |
|---|---|---|
| 1-day 99% VaR | ₹0.28 cr | ₹0.06 cr |
| Crash: −20%, vol +10 | −₹5.4 cr | −₹10.0 cr |
| Volatility +10 pts | −₹5.4 cr | −₹5.4 cr |
| Rally: +10%, vol −3 | −₹2.1 cr | +₹0.2 cr |""",
        """Notebook `08_options.ipynb` · results `Module_08_Derivatives/options.json` · figures `options_bs_error`, `options_ml_vs_bs`, `options_var`.
*Note:* Black-Scholes and the Greeks are in the course's derivatives sessions (in progress) and are required by the brief.""")
    return story + method

# ===============================================================================================================
# LIQUIDITY
# ===============================================================================================================
def liq():
    l = pd.read_csv(DATA / "nova_liquidity.csv"); TO = 1 / 100
    j = J("Extra_Liquidity_Reserve", "liquidity.json"); s = j["stress"]; fc = j["forecast"]
    panels = [
        panel("data", "Cash leaves every day; wholesale money fills the gap",
              columns(["outflows", "inflows", "net gap", "wholesale funding"], [l.Expected_Outflows.mean() * TO, l.Expected_Inflows.mean() * TO,
                      l.Liquidity_Gap.mean() * TO, l.Wholesale_Funding.mean() * TO], C["data"], lambda v: f"₹{v:.1f} cr",
                      title="Average daily cash flows (₹ cr per day)", highlight=(2, 3)),
              "On 87% of days more cash leaves than arrives (≈ ₹4.9 cr net), covered almost exactly by borrowed wholesale money (≈ ₹5.0 cr)."),
        panel("model", "Daily gaps are mostly noise",
              dots(["Ridge", "20-day average", "Gradient boosting", "Naive: tomorrow = today"],
                   [fc["Ridge"]["RMSE ₹ cr"], fc["20-day average"]["RMSE ₹ cr"], fc["Gradient boosting"]["RMSE ₹ cr"], fc["Naive (tomorrow = today)"]["RMSE ₹ cr"]],
                   C["model"], fc["Naive (tomorrow = today)"]["RMSE ₹ cr"], "naive = 6.50", title="Forecast error for tomorrow's gap (RMSE ₹ cr, lower = better)",
                   lo=3.5, hi=7.2, best=1),
              "Models beat 'tomorrow = today' but explain almost nothing (R² ≈ 0). Forecasts help monitoring; they cannot replace a cash reserve."),
        panel("money", "The current buffer cannot cover a 30-day stress",
              columns(["buffer today", "freeze", "+ 10% run", "+ 20% run"], [j["buffer_now_cr"], s["A. Funding freeze"]["30-day need, 99% ₹ cr"],
                      s["B. Freeze + deposit run"]["30-day need, 99% ₹ cr"], s["C. Severe"]["30-day need, 99% ₹ cr"]], C["money"], lambda v: f"₹{v:.0f} cr",
                      title="Buffer vs 30-day cash need under stress (99%, ₹ cr)", highlight=(0, 2)),
              "If wholesale funding freezes and 10% of deposits leave, NovaFin needs ₹286 cr in 30 days against a ₹114 cr buffer."),
        panel("risk", "Without a reserve, cash runs out in weeks",
              line([0, 10, 20], [round(s["A. Funding freeze"]["survival days"]), round(s["B. Freeze + deposit run"]["survival days"]),
                                 round(s["C. Severe"]["survival days"])], C["risk"], ["0%", "10%", "20%"], "share of deposits withdrawn in 30 days",
                   "Days today's buffer lasts once wholesale funding stops", base_idx=1, hline=(30, "LCR horizon 30 days"), fmt=lambda v: f"{v:.0f} d"),
              "23 days with a pure funding freeze, 15 with a 10% run, 11 with a 20% run: all short of the 30-day regulatory horizon."),
    ]
    story = story_page("EXTRA · LIQUIDITY RESERVE", "How much of the ₹1,000 cr must stay as cash?",
        "Size the <b>liquidity reserve</b> so NovaFin survives <b>30 days</b> of a wholesale-funding freeze plus a deposit run.",
        "Hold a <b>₹175 cr reserve</b> in cash and government securities (covers a freeze + 10% deposit run); plan a further ₹84 cr for a severe run.",
        "Stress test", "grey",
        [("Started with", "1,216 days of cash flows", "2022 – 2026, ₹ lakh"), ("ML predicted", "Tomorrow's gap", "early-warning, R² ≈ 0"),
         ("Money test", "Need ₹286 cr", "30 days, 99%, freeze + 10% run"), ("Stress test", "Buffer lasts 15 days", "vs 30 required"),
         ("Decision", "Reserve ₹175 cr", "+ ₹84 cr contingency plan")],
        panels,
        ["<b>Fund the ₹175 cr reserve before any growth capital is drawn.</b>",
         "<b>Reduce reliance on wholesale funding</b>: it covers the daily gap almost exactly and would vanish first in a crisis.",
         "<b>Use the gap forecast as an early-warning trigger</b> (coverage < 110% → stop wholesale-funded growth)."],
        "09_liquidity_stress.ipynb", "§1 identities · §2 gap forecast · §3 30-day stress · §4 reserve + triggers",
        ["liquidity reserve sizing (brief lists liquidity reserves as a destination)"])
    method = method_card("EXTRA", "Liquidity reserve",
        """- **Data:** `nova_liquidity.csv`, 1,216 days (2022 – Aug 2026), read in **₹ lakh** (README) → deposits ₹506 cr, buffer ₹114 cr.
- **Identities recovered exactly:** gap = outflows − inflows; buffer = cash + 80% of securities (20% haircut).
- **Forecast features:** recent gaps (lags, 5- and 20-day means), today's flows, day of week, month-end.""",
        """- **Time split:** first 70% of days train, last 30% test, never shuffled.
- **Stress:** historical simulation over **every 30-day window** in history (≈ 1,190 windows); 99th percentile of the cumulative need.""",
        """| Forecaster | RMSE ₹ cr | Saved vs naive | Chosen |
|---|---|---|---|
| Ridge | 4.60 | 1.91 | |
| 20-day average | 4.68 | 1.82 | ✔ simplest within 2% |
| Gradient boosting | 4.75 | 1.75 | |
| Naive (tomorrow = today) | 6.50 | 0 | |""",
        """- **LCR logic (Basel III, Session 7):** the buffer must cover 30 days of net outflows under stress.
- **Daily need** = outflows + run-off × deposits ÷ 30 − inflows × factor − wholesale (0 in a freeze).
- **Reserve** = 99% 30-day need − today's buffer, rounded up.""",
        """| Scenario | Need | Shortfall | Survival |
|---|---|---|---|
| A. Funding freeze | ₹199 cr | ₹85 cr | 23 days |
| **B. Freeze + 10% run** | ₹286 cr | **₹172 cr** | 15 days |
| C. Freeze + 20% run | ₹372 cr | ₹259 cr | 11 days |""",
        """Notebook `09_liquidity_stress.ipynb` · results `Extra_Liquidity_Reserve/liquidity.json` · figures `liquidity_eda`, `liquidity_stress`.""")
    return story + method

# ===============================================================================================================
# MODULE 9: Integrated allocation
# ===============================================================================================================
def m9():
    a = J("Module_09_Integrated_Allocation", "allocation.json")
    board = {k: v for k, v in a["allocation_board"].items() if k != "TOTAL"}
    order = sorted(board, key=lambda k: -board[k]["₹ crore"])
    lines = a["lines"]
    cand = {"Wealth initiatives": lines["Wealth mgmt (initiatives)"], "Corporate initiatives": lines["Corporate banking (initiatives)"],
            "Digital initiatives": lines["Digital banking (initiatives)"], "Equity": lines["Equity investments"],
            "Corporate loans": lines["Corporate lending (loans)"], "Retail loans": lines["Retail lending (loans)"]}
    score = {k: (v["Return"] - 0.07) / v["Stress loss"] for k, v in cand.items()}
    sc = sorted(score, key=lambda k: -score[k])
    alts = a["alternatives"]; ss = a["sensitivity_stats"]
    sens_keys = [("Base", "base"), ("Initiatives earn 10 pts less (3-year view)", "initiatives −10"), ("Equity return −5 pts", "equity −5"),
                 ("Credit stress: lending return −4 pts", "lending −4"), ("Severe liquidity reserve", "severe reserve"), ("Tighter appetite: stress ≤ 10%", "stress ≤ 10%")]
    panels = [
        panel("data", "Each line offers a different return",
              hbars(list(cand), [v["Return"] * 100 for v in cand.values()], C["data"], lambda v: f"{v:.1f}%",
                    title="Expected annual return on capital by candidate line (%)", highlight=(0, 1, 2), ref=7, ref_label="risk-free 7%"),
              "Initiative returns come from Module 1 (PI ÷ 5 years over the 12% hurdle); lending from Module 2 at a 12.5% capital ratio; equity from Module 6."),
        panel("model", "Ranked by return per rupee at risk",
              dots(sc, [score[k] for k in sc], C["model"], 0, "no excess return",
                   title="Ranking score = (return − 7%) ÷ stress loss rate", lo=-0.2, hi=max(score.values()) * 1.25, fmt=lambda v: f"{v:.2f}"),
              "Low-risk initiatives earn the most per rupee that could be lost; equity and loans rank lower because their stress losses are 20–25%."),
        panel("money", "Where the ₹1,000 cr goes",
              hbars(order, [board[k]["₹ crore"] for k in order], C["money"], lambda v: f"₹{v:.0f} cr", title="Recommended allocation by Board category (₹ cr)",
                    highlight=tuple(range(len(order)))),
              "Mandatory first (reserve, hedging buffer, HFT pilot), then down the ranking within limits: 16.5% expected return a year."),
        panel("risk", "The answer holds when assumptions move",
              columns([lbl for _, lbl in sens_keys], [ss[k]["Expected return %"] * 100 for k, _ in sens_keys], C["risk"], lambda v: f"{v:.1f}%",
                      title="Expected return of the allocation under each scenario (%)", highlight=(0,), rotate=20),
              "The allocation itself barely changes; only the expected return moves (11.6–16.5%). A combined crisis year still nets +₹49 cr."),
    ]
    story = story_page("MODULE 9 · INTEGRATED CAPITAL ALLOCATION", "Where should the ₹1,000 crore go?",
        "Allocate <b>₹1,000 cr</b> across NovaFin's businesses using every module's results, and show <b>what risks</b> we take and <b>how they are controlled</b>.",
        "<b>Grow</b> (₹487 cr in 5 initiatives + ₹58 cr lending), <b>earn steadily</b> (₹250 cr equity), <b>protect</b> (₹175 cr reserve, ₹20 cr hedge buffer, ₹10 cr HFT pilot): <b>16.5% a year</b>.",
        "Integrated decision", "green",
        [("Started with", "9 module results", "no number typed by hand"), ("Common yardstick", "Return · stress · capacity", "for every line"),
         ("Money test", "Rank by return ÷ risk", "fund whole projects only"), ("Stress test", "₹116 cr stress loss", "limit ₹150 cr; crisis year +₹49 cr"),
         ("Decision", "₹1,000 cr split", "16.5% expected return")],
        panels,
        ["<b>Approve the allocation and the risk-appetite limits</b> (reserve ≥ ₹175 cr, ≤ 30% per category, initiatives ≤ 50%, equity ≤ 25%, stress loss ≤ 15%).",
         "<b>Fund the reserve and the hedging buffer first</b>, then release initiative money in stage-gated tranches.",
         "<b>Return-chasing would earn 22% but fails every limit</b> (no reserve, ₹971 cr in initiatives); our split trades a little return for survival."],
        "10_allocation.ipynb", "§2 yardstick · §3 limits · §4 ranking allocation · §5 alternatives · §6 sensitivity · §7 crisis · §9 controls",
        ["construct your own allocation of ₹1,000 cr and explain it", "risks & limitations, governance"])
    method = method_card("MODULE 9", "Integrated allocation",
        """- **Inputs:** every module's result file (`results/*/*.json`) + the initiative decision table + the liquidity reserve.
- **Yardstick per line:** expected annual return on capital · stress loss rate · capacity (min / max ₹).""",
        """- **Not a prediction task:** validated by comparing with simple alternatives, sensitivity on each key assumption, and a combined crisis test.""",
        """| Allocation | Expected return | Stress loss | Meets every limit? | Chosen |
|---|---|---|---|---|
| Return-chasing (no limits) | 22.0% | 8.5% | No: no reserve, ₹971 cr initiatives | |
| **Recommended** | **16.5% (₹165 cr / yr)** | 11.6% (₹116 cr) | Yes | ✔ |
| Equal split (₹125 cr per category) | 12.3% | 8.2% | Yes | |
| All in liquid assets | 6.5% | 0% | Yes | |""",
        """- **Initiatives:** 12% + PI ÷ 5; stress = loss-on-failure × (failure prob + 10 pts).
- **Lending:** 7% + spread after EL ÷ 12.5% capital ratio; stress = extra ECL at PD × 1.5, LGD 50% ÷ 12.5%.
- **Equity:** 13.3% long-run; stress 25%. **Reserve** 6.5%, no stress. **Hedging buffer** 7% − re-hedge cost.
- **Rule (Session 5 capital rationing, risk-adjusted):** mandatory lines → rank by (return − 7%) ÷ stress → fund within limits → leftover stays liquid.""",
        """| Scenario | Expected return |
|---|---|
| Base | 16.5% |
| Initiatives −10 pts (3-year view) | 11.6% |
| Equity −5 pts / lending −4 pts | 15.2% / 16.2% |
| Severe reserve / stress ≤ 10% | 16.0% / 16.1% |
| Combined crisis year | +₹49 cr net |""",
        """Notebook `10_allocation.ipynb` · results `Module_09_Integrated_Allocation/allocation.json`, `final_allocation_board.csv`, `final_allocation_lines.csv`, `funded_initiatives.csv` · figure `allocation`.""")
    return story + method

# ===============================================================================================================
# Front and back matter
# ===============================================================================================================
SUMMARY = f"""<div class="mod">
<div class="mhead"><div><div class="mcode">NOVAFIN CAPSTONE · DETAILED REPORT &amp; CODE GUIDE · v2</div><h2>Executive summary: deploying ₹1,000 crore with ML</h2></div></div>
<p class="lead"><b>The Board asked:</b> how should NovaFin use ML to grow while keeping credit, fraud, market, liquidity and derivatives risk acceptable, and where should the new ₹1,000 crore go?</p>
<div class="kpis"><div><b>16.5%</b><span>expected return a year (₹165 cr)</span></div><div><b>₹116 cr</b><span>stress loss (limit ₹150 cr)</span></div>
<div><b>+₹49 cr</b><span>even if every stress hits at once</span></div><div><b>₹175 cr</b><span>liquidity reserve</span></div></div>
{md('''| Board category | ₹ crore | Share | What it funds |
|---|---|---|---|
| Equity investments | 250 | 25% | equal-weight 15-stock sleeve |
| Wealth management | 221 | 22% | initiative 1075 (Low risk, P(success) 0.92) |
| Liquidity reserves | 175 | 18% | cash + government securities |
| Digital banking | 163 | 16% | initiatives 1041, 1149, 1038 |
| Corporate lending | 120 | 12% | initiative 1062 + capital for approved corporate loans |
| Retail lending | 41 | 4% | capital for ≈ ₹330 cr of approved retail loans |
| Risk management / hedging | 20 | 2% | derivatives hedging buffer |
| High-frequency trading | 10 | 1% | pilot with kill switch |''')}
<h3>What ML delivered, module by module</h3>
<table><tr><th>Module</th><th>Board question</th><th>ML verdict</th><th>Decision</th></tr>
<tr><td>M1 Initiatives</td><td>Which projects to fund?</td><td><span class="verdict amber">ML weak · NPV decides</span></td><td>5 funded · ₹487 cr</td></tr>
<tr><td>M2 Credit</td><td>Which loans to approve?</td><td><span class="verdict green">ML useful</span></td><td>836 approved · ECL 2.8%</td></tr>
<tr><td>M3 Fraud</td><td>Which transactions to check?</td><td><span class="verdict green">ML useful</span></td><td>38% lower cost</td></tr>
<tr><td>M4 Churn &amp; CLV</td><td>Whom should RMs call?</td><td><span class="verdict red">No churn signal</span></td><td>value-led list · net ₹23 lakh</td></tr>
<tr><td>M5 Equity</td><td>Can ML pick stocks?</td><td><span class="verdict red">Not significant</span></td><td>diversify</td></tr>
<tr><td>M6 Portfolio</td><td>How to spread equity?</td><td><span class="verdict red">Not significant</span></td><td>equal-weight · ₹250 cr</td></tr>
<tr><td>M7 HFT</td><td>Can the order book be traded?</td><td><span class="verdict amber">Signal real · profit fragile</span></td><td>₹10 cr pilot</td></tr>
<tr><td>M8 Derivatives</td><td>Can ML price options?</td><td><span class="verdict red">Black-Scholes wins</span></td><td>hedge · ₹20 cr buffer</td></tr>
<tr><td>Liquidity</td><td>How much cash to keep?</td><td><span class="verdict grey">Stress test</span></td><td>₹175 cr reserve</td></tr>
<tr><td>M9 Allocation</td><td>Where does ₹1,000 cr go?</td><td><span class="verdict green">Integrated</span></td><td>16.5% return</td></tr></table>
<p class="lead"><b>The lesson:</b> ML adds value where there is real signal and a clear cost function (credit, fraud, trade execution). Where it does not, the simpler model or the theory wins, and the capital decision rests on finance: NPV, ECL, diversification and stress tests.</p>
</div>"""

APPROACH = f"""<div class="mod">
<div class="mhead"><div><div class="mcode">APPROACH</div><h2>How every module was built</h2></div></div>
<div class="pipetitle">The chain the Board asked for, applied in every module</div>
<div class="pipe"><div class="step"><div class="slabel"><span class="snum">1</span>Data</div><div class="snote">clean, explore, engineer features known at decision time</div></div><div class="arrow">➜</div>
<div class="step"><div class="slabel"><span class="snum">2</span>ML prediction</div><div class="snote">≥ 3 models, simplest wins unless clearly beaten</div></div><div class="arrow">➜</div>
<div class="step"><div class="slabel"><span class="snum">3</span>Financial metric</div><div class="snote">NPV, ECL, cost, CLV, Sharpe, VaR</div></div><div class="arrow">➜</div>
<div class="step"><div class="slabel"><span class="snum">4</span>Risk assessment</div><div class="snote">sensitivity and stress tests</div></div><div class="arrow">➜</div>
<div class="step"><div class="slabel"><span class="snum">5</span>Business decision</div><div class="snote">fund, approve, check, call, allocate</div></div></div>
{md('''| Data | Validation | Why |
|---|---|---|
| Cross-sectional: initiatives, loans, customers, options | stratified k-fold (repeated when small) | no time order; keep class balance |
| Time series: transactions, market, liquidity | time split / walk-forward | no look-ahead bias |
| HFT order book | split by trading day | events within a day are not independent |

**Leakage rules:** no future columns (HFT `Future_*`), history from earlier rows only, `Estimated_CLV` kept out of churn, supplied Black-Scholes price kept out of the ML pricer.
**Explainability:** SHAP or coefficients for every chosen model. **Units:** loans and customers in rupees; initiatives assumed ₹ crore; liquidity in ₹ lakh.

**Course alignment:** only methods from sessions 1–19 were used. Untaught techniques were replaced (chi-square → group rates + t-stat; Brier → calibration gap; bootstrap / Monte Carlo VaR → historical simulation; solvers → profitability-index ranking). Black-Scholes, the Greeks and HFT direction prediction are kept because the brief requires them.

**How to read the module pages:** each module has a **Story** page (question → answer → step-by-step → four perspectives → so what) and a **Method** page (input, validation, model comparison, financial layer, assumptions, code). The four perspectives always appear in the same colours: **THE DATA** (blue), **THE MODEL** (purple), **THE MONEY** (teal), **THE RISK** (orange).''')}
</div>"""

RISKS = f"""<div class="mod">
<div class="mhead"><div><div class="mcode">RISKS, LIMITATIONS &amp; GOVERNANCE</div><h2>What could go wrong, and how it is controlled</h2></div></div>
{md('''| Risk | Control | Trigger | Owner |
|---|---|---|---|
| Credit | approve only PD < 0.11 with positive value; reprice the review queue | approved ECL > 3% | CRO |
| Initiatives | stage-gated tranches; re-score P(success) yearly | 2 quarters behind plan → stop next tranche | CFO |
| Equity | equal-weight, 25% cap, quarterly rebalance | drawdown > 10% → halve the sleeve | CIO |
| Derivatives | daily delta hedge; vega limit; ₹20 cr buffer | volatility exposure over limit → buy protection | Head of derivatives |
| HFT | ₹10 cr pilot, kill switch | daily loss > ₹0.5 cr or total > ₹2 cr → stop | Head of trading |
| Liquidity | ₹175 cr reserve | coverage < 110% → stop wholesale-funded growth | Treasurer / ALCO |
| Fraud | cost-optimal threshold; monthly PR-AUC | PR-AUC −30% or alerts × 2 → retrain | Head of fraud ops |
| Model risk | model inventory, annual validation, SHAP on file | any drift alarm → revalidate | Model risk committee |

**Data limitations.** Synthetic data with unrealistic features (near-zero stock correlations; HFT moves 3.5× the spread; macro columns that vary by stock; a churn flag that looks random). Small samples (180 initiatives with 42 failures; 4 HFT test days). Unit assumptions (initiatives in crore, liquidity in lakh).

**Model risk.** Weak or absent signals in initiatives, churn and equity; regime change in fraud and HFT. Key assumptions (5-year project life, loss on failure, 12.5% capital ratio, save rate, run-off rates) are stated and stress-tested on each Method page.

**Governance.** Every model has an owner, a monitoring metric and a retraining trigger; every decision can be explained (SHAP or coefficients); simple models were preferred whenever complexity did not pay.''')}
</div>"""

CODE = f"""<div class="mod">
<div class="mhead"><div><div class="mcode">CODE GUIDE</div><h2>Reusable Python / Colab framework</h2></div></div>
{md('''**Folder structure**

| Folder / file | Content |
|---|---|
| `data/` | the eight CSV files |
| `src/novafin.py` | shared assumptions, loaders, metrics, `compare_models()`, `use_module()`, `save_result()` / `load_result()` |
| `notebooks/00 … 10` | one notebook per module, run in order; each saves its hand-off results |
| `results/<Module_NN_Name>/`, `figures/<Module_NN_Name>/` | outputs per module |
| `tools/` | report, guide and deck generators (`make_report_v2.py`, `story_lib.py`) |
| `CENTRAL.md`, `PROGRESS.md` | module index with comparison tables; status with numbers and figures |

**How to run.** Locally: `pip install pandas numpy scikit-learn matplotlib seaborn shap scipy jupyter`, then run notebooks 00 → 10.
Colab: upload the folder to Drive, mount it, `cd notebooks/` and run (`find_root()` locates the project). Change any assumption in `ASSUMPTIONS` (`src/novafin.py`) and re-run: every module picks it up.

**Notebook template (every module).** 1 audit + EDA → 2 features + leakage check → 3 split (stratified / time / walk-forward / by day) →
4 compare ≥ 3 models with `compare_models()` against a no-skill baseline → 5 validate + explain (calibration, SHAP) → 6 financial layer →
7 decision + stress test → 8 risks and limitations → 9 `save_result()` for the allocation.''')}
<pre>import sys; sys.path.insert(0, '../src')
from novafin import *                    # ASSUMPTIONS, SEED, load(), metrics, plots, hand-off helpers
RES, FIG = use_module('03')              # outputs -> results/Module_03_Fraud_Detection/, figures/...
tx = load('transactions')                # any dataset by short name
binary_report(y, p)                      # ROC-AUC, Gini, KS, PR-AUC, calibration gap
compare_models(table, 'PR-AUC', chosen='Random forest', baseline='No-skill')   # benefit-of-choice table
save_result('fraud', payload); load_result('fraud')                              # hand-off between modules

# walk-forward (Modules 5-6): train only on the past
for t in dates[24:]:
    model.fit(data[data.Date &lt; t][X], data[data.Date &lt; t].y); preds.append(model.predict(data[data.Date == t][X]))

# cost-based threshold (Modules 3, 7): choose on validation, apply to test
best_t = min(thresholds, key=lambda t: 10_000 * missed(t) + 500 * false_alarms(t))

# finance layer
ECL  = PD * ASSUMPTIONS['LGD'] * EAD                                     # Module 2
ENPV = p * NPV - (1 - p) * loss_rate * I0;  PI = ENPV / I0               # Module 1
VaR99 = -np.quantile(historical_pnl, 0.01)                               # Modules 8 and liquidity</pre>
{md('''**Appendix: key assumptions.** LGD 40% · fraud ₹10,000 / ₹500 · ₹1,000 cr · 1,000 contacts (brief) · hurdle 12% · risk-free 7% · cost of funds 6% · ECL appetite 3% · project life 5 years · loss on failure 30/50/70% · capital ratio 12.5% · save rate 30%, call ₹1,500 · equity costs 10 bps · options book short 100 each · liquidity stress: freeze + 10% run, 30 days, 99%.''')}
</div>"""

SECTIONS = [("summary", "Summary", SUMMARY), ("approach", "Approach", APPROACH),
            ("m1", "M1 Initiatives", m1()), ("m2", "M2 Credit", m2()), ("m3", "M3 Fraud", m3()), ("m4", "M4 Churn & CLV", m4()),
            ("m5", "M5 Equity", m5()), ("m6", "M6 Portfolio", m6()), ("m7", "M7 HFT", m7()), ("m8", "M8 Derivatives", m8()),
            ("liq", "Liquidity", liq()), ("m9", "M9 Allocation", m9()), ("risks", "Risks & Controls", RISKS), ("code", "Code Guide", CODE)]

html = assemble(SECTIONS, "NovaFin Capstone Report v2")
(OUT / "NovaFin_Capstone_Report_v2.html").write_text(html, encoding="utf-8")
dst, tmp = OUT / "NovaFin_Capstone_Report_v2.pdf", OUT / "_tmp_NovaFin_Capstone_Report_v2.pdf"
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={tmp.resolve()}",
                (OUT / "NovaFin_Capstone_Report_v2.html").resolve().as_uri()], capture_output=True, text=True, timeout=300)
try:
    tmp.replace(dst); print("updated: NovaFin_Capstone_Report_v2.html and .pdf")
except PermissionError:
    print(dst.name, "NOT updated: close it in your viewer and run again (new copy left as", tmp.name + ")")
