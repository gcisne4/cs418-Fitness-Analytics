"""Build the day-level NHANES analysis table (PAXDAY_G joined to DEMO_G).
Run from repo root:  python analysis/prep.py   (needs data/cdc/PAXDAY_G.xpt, DEMO_G.xpt)"""
import numpy as np, pandas as pd

def load(root="."):
    p = pd.read_sas(f"{root}/data/cdc/PAXDAY_G.xpt", format="xport")
    d = pd.read_sas(f"{root}/data/cdc/DEMO_G.xpt", format="xport")
    for c in ["PAXDAYD", "PAXDAYWD"]:
        p[c] = p[c].apply(lambda x: int(x.decode() if isinstance(x, bytes) else x))
    # near-zero artifacts (EDA: values < 1e-70 are read errors for zero)
    num = [c for c in p.select_dtypes("number").columns if c not in ("SEQN",)]
    for c in num:
        p.loc[(p[c] > 0) & (p[c] < 1e-70), c] = 0.0
    stats = {"pax_rows": len(p), "pax_people": p.SEQN.nunique(), "demo_rows": len(d)}
    # join counts on the full file (all monitoring days), key = SEQN
    stats["join_matched_people"] = len(set(p.SEQN) & set(d.SEQN))
    stats["pax_people_unmatched"] = len(set(p.SEQN) - set(d.SEQN))
    stats["demo_people_without_monitor"] = len(set(d.SEQN) - set(p.SEQN))
    p = p[p.PAXDAYD.between(2, 8)].copy()
    stats["days_2_8_rows"] = len(p)
    p["mims_per_min"] = np.where(p.PAXVMD > 0, p.PAXMTSD / p.PAXVMD.where(p.PAXVMD > 0), np.nan)
    p["weekend"] = p.PAXDAYWD.isin([1, 7]).astype(int)   # 1=Sunday, 7=Saturday
    stats["null_ratio_rows"] = int(p.mims_per_min.isna().sum())
    keep = ["SEQN", "RIAGENDR", "RIDAGEYR", "RIDRETH1", "INDFMPIR", "DMDEDUC2", "WTMEC2YR", "SDMVPSU", "SDMVSTRA"]
    df = p.merge(d[keep], on="SEQN", how="left", indicator=True)
    df = df.drop(columns="_merge").dropna(subset=["mims_per_min"])
    df["age_group"] = pd.cut(df.RIDAGEYR, [0, 17.99, 39.99, 64.99, 200],
                             labels=["<18", "18-39", "40-64", "65+"])
    df["female"] = (df.RIAGENDR == 2).astype(int)
    return df, stats

if __name__ == "__main__":
    df, s = load()
    print(s); print(len(df), df.SEQN.nunique())
    print("income missing (people):", df.groupby("SEQN").INDFMPIR.first().isna().sum())
    print("education non-missing (people):", df.groupby("SEQN").DMDEDUC2.first().notna().sum())
    print(df.groupby("SEQN").age_group.first().value_counts().to_dict())
