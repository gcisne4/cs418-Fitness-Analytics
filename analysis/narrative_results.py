"""Produces every number and figure for the three findings in README.md.
Run from repo root:  python analysis/narrative_results.py
Outputs: figures/finding-one.png, finding-two.png, finding-three.png and results/narrative_results.json
Method: each person is compared with themselves (person fixed effects = 'within-person'), days 2-8 only,
standard errors clustered by person (SEQN). All models control for monitoring day (day 2 = reference)."""
import sys, json, os; sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from prep import load
from models import fit

BLUE, ORANGE, INK, MUTED = "#2B6CB0", "#D9730D", "#222222", "#6b6b6b"
plt.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#999", "axes.titleweight": "bold", "axes.titlesize": 13})
os.makedirs("figures", exist_ok=True); os.makedirs("results", exist_ok=True)

df, st = load()
R = {"prep": st, "n_days": len(df), "n_people": int(df.SEQN.nunique())}
D = [f"d{k}" for k in range(3, 9)]
for k in range(3, 9): df[f"d{k}"] = (df.PAXDAYD == k).astype(int)
# movement per awake-worn minute = daily MIMS / awake-worn minutes (days with >= 300 awake-worn minutes)
df["m_awake"] = np.where(df.PAXWWMD >= 300, df.PAXMTSD / df.PAXWWMD.where(df.PAXWWMD > 0), np.nan)
df["m_awake600"] = np.where(df.PAXWWMD >= 600, df.PAXMTSD / df.PAXWWMD.where(df.PAXWWMD > 0), np.nan)
df["sex"] = np.where(df.female == 1, "Women", "Men")
groups = ["<18", "18-39", "40-64", "65+"]; glabs = ["Under 18", "18–39", "40–64", "65 and older"]
def row(r, name):
    x = r.loc[name]; return {k: float(x[k]) for k in ("coef", "lo", "hi")}
def wk(y, d=None, extra=None, **kw):
    d = df if d is None else d
    return fit(d, y, ["weekend"] + D + (extra or []), fe=True, **kw)

R["means"] = {"weekday_mims_per_valid_min": float(df[df.weekend == 0].mims_per_min.mean()),
              "weekday_mims_per_awake_min": float(df[df.weekend == 0].m_awake.mean()),
              "awake_days_kept": int(df.m_awake.notna().sum()), "awake_days_dropped": int(df.m_awake.isna().sum()),
              "mean_minutes_by_daytype": df.groupby("weekend")[["PAXWWMD", "PAXSWMD", "PAXNWMD", "PAXVMD", "PAXMTSD"]].mean().round(1).to_dict()}

# ================= Finding 1: weekends differ in TIME more than in effort =================
f1 = {"mims_per_min_unadjusted": fit(df, "mims_per_min", ["weekend"], fe=True),
      "mims_per_min": wk("mims_per_min"), "daily_mims": wk("PAXMTSD"), "m_awake": wk("m_awake"),
      "awake_min": wk("PAXWWMD"), "sleep_min": wk("PAXSWMD"), "nonwear_min": wk("PAXNWMD")}
R["finding1"] = {k: row(v, "weekend") for k, v in f1.items()}
R["finding1"]["mims_per_min_controlling_sleep_nonwear"] = row(wk("mims_per_min", extra=["PAXSWMD", "PAXNWMD"]), "weekend")
chk = {"valid>=1200 min": wk("m_awake", df[df.PAXVMD >= 1200]), "awake>=600 min": wk("m405", df.assign(m405=df.m_awake600)) if False else wk("m_awake600"),
       "Fridays dropped": wk("m_awake", df[df.PAXDAYWD != 6]), "survey-weighted": wk("m_awake", weight="WTMEC2YR"),
       "controlling for sleep minutes": wk("m_awake", extra=["PAXSWMD"])}
R["finding1_checks_m_awake"] = {k: row(v, "weekend") for k, v in chk.items()}
R["finding1_minutes_weighted"] = {y: row(wk(y, weight="WTMEC2YR"), "weekend") for y in ["PAXWWMD", "PAXSWMD", "PAXNWMD"]}
R["monitoring_day_effects_mims_per_min"] = {c: row(f1["mims_per_min"], c) for c in D}
R["finding1_pct_of_weekday"] = {"mims_per_min": R["finding1"]["mims_per_min"]["coef"] / R["means"]["weekday_mims_per_valid_min"] * 100,
                                "m_awake": R["finding1"]["m_awake"]["coef"] / R["means"]["weekday_mims_per_awake_min"] * 100}

fig, axs = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1.15, 1]})
ax = axs[0]
items = [("Awake-worn time", "awake_min", ORANGE), ("Sleep time", "sleep_min", BLUE), ("Non-wear time", "nonwear_min", BLUE)][::-1]
for i, (lab, k, c) in enumerate(items):
    x = R["finding1"][k]
    ax.errorbar(x["coef"], i, xerr=[[x["coef"] - x["lo"]], [x["hi"] - x["coef"]]], fmt="o", color=c, ms=9, capsize=5, lw=2)
    ax.text(x["hi"] + 3, i, f'{x["coef"]:+.0f} min', va="center", fontsize=11)
ax.axvline(0, color="#888", ls="--", lw=1); ax.set_yticks(range(3)); ax.set_yticklabels([i[0] for i in items])
ax.set_xlim(-60, 70); ax.set_xlabel("Weekend minus weekday, minutes per day (95% CI)"); ax.set_title("Where the weekend minutes go", loc="left")
ax = axs[1]
items = [("Per valid minute", "mims_per_min"), ("Per awake-worn minute", "m_awake")][::-1]
for i, (lab, k) in enumerate(items):
    x = R["finding1"][k]; pct = R["finding1_pct_of_weekday"][k]
    c = ORANGE if k == "m_awake" else BLUE
    ax.errorbar(x["coef"], i, xerr=[[x["coef"] - x["lo"]], [x["hi"] - x["coef"]]], fmt="o", color=c, ms=9, capsize=5, lw=2)
    ax.text(x["hi"] + 0.04, i, f'{x["coef"]:.2f}  ({pct:.1f}%)', va="center", fontsize=11)
ax.axvline(0, color="#888", ls="--", lw=1); ax.set_yticks(range(2)); ax.set_yticklabels([i[0] for i in items])
ax.set_xlim(-0.9, 0.9); ax.set_ylim(-0.6, 1.6); ax.set_xlabel("Weekend minus weekday, MIMS per minute (95% CI)"); ax.set_title("Movement rate", loc="left")
fig.suptitle("People are awake-and-wearing the monitor ~40 fewer minutes on weekends, but move at nearly the same rate", x=0.01, ha="left", fontsize=13.5, fontweight="bold")
plt.tight_layout(rect=(0, 0, 1, 0.93)); plt.savefig("figures/finding-one.png", dpi=200, bbox_inches="tight"); plt.close()

# ================= Finding 2: the time shift depends on age =================
for g in groups: df[f"we_{g}"] = df.weekend * (df.age_group == g)
we_cols = [f"we_{g}" for g in groups]
def by_group(y, cols=we_cols, **kw):
    r = fit(df, y, cols + D, fe=True, **kw); return {g: row(r, f"we_{g}") for g in groups}, r
R["finding2"] = {}
for y, nm in [("PAXWWMD", "awake_min"), ("PAXSWMD", "sleep_min"), ("PAXNWMD", "nonwear_min"), ("mims_per_min", "mims_per_min"), ("m_awake", "m_awake")]:
    R["finding2"][nm], _ = by_group(y)
df["we_65"] = df.weekend * (df.age_group == "65+")
R["finding2_65_vs_under65_awake_min"] = row(fit(df, "PAXWWMD", ["weekend", "we_65"] + D, fe=True), "we_65")
R["finding2_65_vs_under65_awake_min_weighted"] = row(fit(df, "PAXWWMD", ["weekend", "we_65"] + D, fe=True, weight="WTMEC2YR"), "we_65")
R["finding2_65_vs_under65_awake_min_valid1200"] = row(fit(df[df.PAXVMD >= 1200], "PAXWWMD", ["weekend", "we_65"] + D, fe=True), "we_65")
R["finding2_awake_min_weighted"], _ = by_group("PAXWWMD", weight="WTMEC2YR")
R["finding2_65_vs_under65_mims_per_min"] = row(fit(df, "mims_per_min", ["weekend", "we_65"] + D, fe=True), "we_65")
R["finding2_n_people"] = {k: int(v) for k, v in df.groupby("SEQN").age_group.first().value_counts().items()}
R["finding2_mean_awake_min_by_daytype"] = df.groupby(["age_group", "weekend"], observed=True).PAXWWMD.mean().round(0).unstack().to_dict()

fig, ax = plt.subplots(figsize=(8.8, 4.9))
for i, g in enumerate(groups):
    x = R["finding2"]["awake_min"][g]; c = ORANGE if g == "65+" else BLUE
    ax.errorbar(i, x["coef"], yerr=[[x["coef"] - x["lo"]], [x["hi"] - x["coef"]]], fmt="o", color=c, ms=10, capsize=6, lw=2)
    ax.text(i + 0.13, x["coef"], f'{x["coef"]:.0f} min', va="center", color=INK)
ax.axhline(0, color="#888", ls="--", lw=1)
ax.set_xticks(range(4)); ax.set_xticklabels(glabs); ax.set_xlim(-0.5, 3.7); ax.set_ylim(-62, 3)
ax.set_ylabel("Weekend minus weekday awake-worn minutes\n(per day, 95% CI)"); ax.set_xlabel("Age group")
ax.set_title("Adults 65+ lose ~25 awake minutes on weekends; everyone else loses 40 to 48", loc="left")
plt.tight_layout(); plt.savefig("figures/finding-two.png", dpi=200, bbox_inches="tight"); plt.close()

# ================= Finding 3: the effort shift depends on sex; income does not =================
cells = [(g, s) for g in groups for s in ["Men", "Women"]]
for g, s in cells: df[f"c_{g}_{s}"] = df.weekend * ((df.age_group == g) & (df.sex == s))
f3 = fit(df, "m_awake", [f"c_{g}_{s}" for g, s in cells] + D, fe=True)
R["finding3_cells_m_awake"] = {f"{g}|{s}": row(f3, f"c_{g}_{s}") for g, s in cells}
df["we_female"] = df.weekend * df.female
for g in ["18-39", "40-64", "65+"]: df[f"x_{g}"] = df.weekend * (df.age_group == g)
df["we_inc"] = df.weekend * (df.INDFMPIR - df.INDFMPIR.mean())
base = ["weekend", "x_18-39", "x_40-64", "x_65+"]
bysex = {s: row(fit(df[df.sex == s], "m_awake", ["weekend"] + D, fe=True), "weekend") for s in ["Men", "Women"]}
R["finding3_by_sex_m_awake"] = bysex
j = fit(df, "m_awake", base + ["we_female", "we_inc"] + D, fe=True)
R["finding3_joint_m_awake"] = {"women_minus_men": row(j, "we_female"), "per_unit_income_ratio": row(j, "we_inc"), "n_people": j.attrs["n_people"]}
R["finding3_women_minus_men"] = {
    "unadjusted_for_age": row(fit(df, "m_awake", ["weekend", "we_female"] + D, fe=True), "we_female"),
    "valid>=1200": row(fit(df[df.PAXVMD >= 1200], "m_awake", base + ["we_female"] + D, fe=True), "we_female"),
    "awake>=600": row(fit(df, "m_awake600", base + ["we_female"] + D, fe=True), "we_female"),
    "controlling sleep minutes": row(fit(df, "m_awake", base + ["we_female"] + D + ["PAXSWMD"], fe=True), "we_female"),
    "survey-weighted": row(fit(df, "m_awake", base + ["we_female"] + D, fe=True, weight="WTMEC2YR"), "we_female")}
R["finding3_by_age_women_minus_men"] = {g: row(fit(s, "m_awake", ["weekend", "we_female"] + D, fe=True), "we_female") for g, s in df.groupby("age_group", observed=True)}
R["finding3_awake_min_women_minus_men"] = row(fit(df, "PAXWWMD", base + ["we_female"] + D, fe=True), "we_female")
R["finding3_income_awake_min"] = row(fit(df, "PAXWWMD", base + ["we_female", "we_inc"] + D, fe=True), "we_inc")
R["finding3_income_n_missing_people"] = int(df.groupby("SEQN").INDFMPIR.first().isna().sum())

# income: tertiles of income-to-poverty ratio (people with income missing are dropped from these models)
_inc = df.groupby("SEQN").INDFMPIR.first()
_t = pd.qcut(_inc.dropna(), 3, labels=["Lower third", "Middle third", "Upper third"])
df["inc3"] = df.SEQN.map(_t.astype(str)).replace("nan", np.nan)
tl = ["Lower third", "Middle third", "Upper third"]
for t in tl: df[f"we_{t}"] = df.weekend * (df.inc3 == t)
fi = fit(df, "m_awake", [f"we_{t}" for t in tl] + D, fe=True)
R["finding3_income_tertiles_m_awake"] = {t: row(fi, f"we_{t}") for t in tl}
R["finding3_income_tertile_cutoffs"] = [float(x) for x in _inc.dropna().quantile([1/3, 2/3])]
R["finding3_income_tertile_n_people"] = {k: int(v) for k, v in _t.value_counts().items()}
R["finding3_income_weighted"] = row(fit(df, "m_awake", base + ["we_female", "we_inc"] + D, fe=True, weight="WTMEC2YR"), "we_inc")
for k, nm in [(1, "MexAm"), (2, "OthHisp"), (4, "NHBlack"), (5, "OtherRace")]: df[f"we_race_{nm}"] = df.weekend * (df.RIDRETH1 == k)
R["finding3_income_adj_race"] = row(fit(df, "m_awake", base + ["we_female", "we_inc"] + [c for c in df if c.startswith("we_race_")] + D, fe=True), "we_inc")
R["finding3_income_adults_only"] = row(fit(df[df.RIDAGEYR >= 18], "m_awake", ["weekend", "x_40-64", "x_65+", "we_female", "we_inc"] + D, fe=True), "we_inc")
R["finding3_income_valid1200"] = row(fit(df[df.PAXVMD >= 1200], "m_awake", base + ["we_female", "we_inc"] + D, fe=True), "we_inc")

fig, axs = plt.subplots(1, 2, figsize=(13, 4.9), gridspec_kw={"width_ratios": [1.6, 1]})
ax = axs[0]; off = {"Men": -0.12, "Women": 0.12}; col = {"Men": BLUE, "Women": ORANGE}
for s_ in ["Men", "Women"]:
    for i, g in enumerate(groups):
        x = R["finding3_cells_m_awake"][f"{g}|{s_}"]
        ax.errorbar(i + off[s_], x["coef"], yerr=[[x["coef"] - x["lo"]], [x["hi"] - x["coef"]]], fmt="o", color=col[s_], ms=9, capsize=5, lw=2, label=s_ if i == 0 else None)
ax.axhline(0, color="#888", ls="--", lw=1); ax.set_xticks(range(4)); ax.set_xticklabels(glabs); ax.set_xlabel("Age group")
ax.set_ylabel("Weekend minus weekday movement per\nawake-worn minute (MIMS, 95% CI)"); ax.set_ylim(-0.85, 0.65); ax.legend(frameon=False, loc="upper right", ncol=2)
ax.set_title("By sex and age", loc="left", fontsize=12)
ax = axs[1]
for i, t in enumerate(tl):
    x = R["finding3_income_tertiles_m_awake"][t]
    ax.errorbar(i, x["coef"], yerr=[[x["coef"] - x["lo"]], [x["hi"] - x["coef"]]], fmt="o", color=BLUE, ms=9, capsize=5, lw=2)
ax.axhline(0, color="#888", ls="--", lw=1); ax.set_xticks(range(3)); ax.set_xticklabels(["Lower\nthird", "Middle\nthird", "Upper\nthird"])
ax.set_xlabel("Household income (income-to-poverty ratio)"); ax.set_ylim(-0.85, 0.65); ax.set_title("By income", loc="left", fontsize=12)
fig.suptitle("Women and higher-income people move relatively more on weekends, per awake minute", x=0.01, ha="left", fontsize=13.5, fontweight="bold")
plt.tight_layout(rect=(0, 0, 1, 0.93)); plt.savefig("figures/finding-three.png", dpi=200, bbox_inches="tight"); plt.close()

json.dump(R, open("results/narrative_results.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print("saved results/narrative_results.json")
