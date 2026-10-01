"""Review fixes for the v2 synthetic experiments.

(1) e1_fresh_null: E1 at rho=0 with an independent noise-feature realization per run
    (feature seed differs per run), so the 30 runs are independent draws over the noise
    features; certified against the same E3 bars.
(2) oracle: oracle active Sharpe per rho on the exact E1/E3 panel (2,952 bars), averaged over
    30 noise realizations, plus the value for the seed-0 realization E1 searched.
"""
import csv, os, sys, time
import numpy as np, pandas as pd
import backtest as bt, backtest_xs as xs, synth as synth_mod, mech_search as ms
import alpha_tools as tools

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results_v2")
PANEL = os.path.join(HERE, ".cache", "panel_AAPL-MSFT-GOOGL-AMZN-NVDA-META-TSLA_2015-01-01_2026-09-30.parquet")
RHO_GRID = [0.0, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.70]
COST = 0.0005


def setup():
    panel = pd.read_parquet(PANEL)
    rets = xs._returns_matrix(panel)
    bench = xs.equalweight_returns(rets, COST)
    splits = bt.make_purged_kfold_splits(panel.index, n_folds=6, embargo=250)
    return panel, rets, bench, splits


def q95(name):
    return float(np.quantile(np.load(os.path.join(OUT, f"e3_null_{name}.npy")), 0.95))


def e1_fresh_null(n=30, budget=200, depth=3, feat_seed0=1000):
    panel, rets, bench, splits = setup()
    bars = {"random": q95("random"), "linear": q95("linear")}
    rows = []
    for sd in range(n):
        feats = synth_mod.make_features(panel, predictor=True, rho=0.0, base=1.0, horizon=21,
                                        seed=feat_seed0 + sd)
        b, _ = ms.random_search(panel, rets, tools, splits, bench, n_candidates=budget,
                                seed=sd, depth=depth, k=1, feats=feats, cost=COST)
        rnd = b["median_oos"] if b is not None else float("nan")
        lin = ms.linear_search(panel, rets, tools, splits, bench, seed=sd, k=1,
                               feats=feats, cost=COST)["median_oos"]
        rows.append({"run": sd, "feat_seed": feat_seed0 + sd,
                     "random_cv": round(float(rnd), 4), "random_clear": bool(rnd > bars["random"]),
                     "linear_cv": round(float(lin), 4), "linear_clear": bool(lin > bars["linear"])})
        print(f"run {sd:2d}: random {rnd:+.3f} linear {lin:+.3f}", flush=True)
    with open(os.path.join(OUT, "e1_fresh_null.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("bars", bars, "| random clears", sum(r["random_clear"] for r in rows),
          "| linear clears", sum(r["linear_clear"] for r in rows), f"of {n}")


def oracle(n_real=30):
    panel, rets, bench, _ = setup()
    rows = []
    for rho in RHO_GRID:
        v = []
        for s in range(n_real):
            f = synth_mod.make_features(panel, predictor=True, rho=rho, base=1.0, horizon=21, seed=s)
            W = xs.top_k_weights(f["feat_c"].to_numpy(), 1)
            v.append(bt._sharpe_arr(xs.portfolio_returns(W, rets, COST) - bench))
        rows.append({"rho": rho, "oracle_mean": round(float(np.mean(v)), 3),
                     "oracle_sd": round(float(np.std(v, ddof=1)), 3),
                     "oracle_seed0": round(float(v[0]), 3)})
        print(rows[-1], flush=True)
    with open(os.path.join(OUT, "oracle_sharpe.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    {"e1_fresh_null": e1_fresh_null, "oracle": oracle}[sys.argv[1]]()
