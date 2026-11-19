"""Regression helpers (numpy only): OLS / person-fixed-effects / WLS with cluster-robust SEs (cluster = SEQN)."""
import numpy as np, pandas as pd

def _cr_se(X, u, groups, k_extra=0):
    XtXi = np.linalg.pinv(X.T @ X)
    meat = np.zeros((X.shape[1], X.shape[1]))
    codes, uniq = pd.factorize(groups)
    G = len(uniq)
    order = np.argsort(codes, kind="stable")
    Xs, us, cs = X[order], u[order], codes[order]
    bounds = np.r_[0, np.flatnonzero(np.diff(cs)) + 1, len(cs)]
    for a, b in zip(bounds[:-1], bounds[1:]):
        s = Xs[a:b].T @ us[a:b]
        meat += np.outer(s, s)
    N, k = X.shape
    c = G / (G - 1) * (N - 1) / (N - k - k_extra)
    return np.sqrt(np.diag(c * XtXi @ meat @ XtXi))

def fit(df, y, xcols, cluster="SEQN", fe=False, weight=None, const=True):
    d = df.dropna(subset=[y] + xcols).copy()
    yv = d[y].to_numpy(float); X = d[xcols].to_numpy(float)
    if fe:                                   # demean within person (removes baseline differences)
        g = d[cluster]
        yv = yv - pd.Series(yv, index=d.index).groupby(g).transform("mean").to_numpy()
        X = X - pd.DataFrame(X, index=d.index).groupby(g).transform("mean").to_numpy()
        const = False
    elif const:
        X = np.c_[np.ones(len(d)), X]
    names = (["const"] if const else []) + xcols
    w = np.ones(len(d)) if weight is None else d[weight].to_numpy(float)
    sw = np.sqrt(w)
    Xw, yw = X * sw[:, None], yv * sw
    beta = np.linalg.pinv(Xw.T @ Xw) @ Xw.T @ yw
    u = yw - Xw @ beta
    se = _cr_se(Xw, u, d[cluster].to_numpy(), k_extra=(d[cluster].nunique() if fe else 0))
    out = pd.DataFrame({"coef": beta, "se": se}, index=names)
    out["lo"] = out.coef - 1.96 * out.se; out["hi"] = out.coef + 1.96 * out.se
    out.attrs.update(n_days=len(d), n_people=d[cluster].nunique())
    return out
