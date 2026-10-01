"""
Production runner for the v2 mechanical (non-LLM) synthetic experiments:
  E3 — null-max bar: 1000-scramble distribution per class + q95-stability curve.
  E1 — power curve : P(certification) vs true injected Sharpe, N seeds per rho, per searcher,
                     certified against the class-matched E3 bar.
Outputs tidy CSVs (+ raw npy for the null distributions) under results_v2/. No LLM, no tokens.

Usage:
  python exp_v2_synth.py --exp e3 --n-scramble 1000 --budget 200
  python exp_v2_synth.py --exp e1 --n-seeds 30 --budget 200
"""
from __future__ import annotations
import os, csv, time, argparse
import numpy as np

import data_mag7, backtest as bt, backtest_xs as xs, alpha_tools as tools, synth as synth_mod
import mech_search as ms

OUT = os.path.join(os.path.dirname(__file__), "results_v2")
RHO_GRID = [0.0, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.70]
PREFIXES = [30, 50, 100, 250, 500, 1000]


def setup(cost=0.0005):
    panel = data_mag7.get_panel(data_mag7.MAG7, start="2015-01-01")
    rets = xs._returns_matrix(panel)
    bench = xs.equalweight_returns(rets, cost)
    splits = bt.make_purged_kfold_splits(panel.index, n_folds=6, embargo=250)
    return panel, rets, bench, splits


def run_e3(n_scramble=1000, budget=200, depth=3, seed=7, cost=0.0005):
    os.makedirs(OUT, exist_ok=True)
    panel, rets, bench, splits = setup(cost)
    ctrl = synth_mod.make_features(panel, predictor=False, seed=99)      # all-noise feats
    rows = []
    for searcher in ("random", "linear"):
        t = time.time()
        dist = ms.noise_bestfit_distribution(panel, rets, tools, splits, seed=seed,
                                             n_scramble=n_scramble, searcher=searcher,
                                             budget=budget, depth=depth, k=1, feats=ctrl, cost=cost)
        np.save(os.path.join(OUT, f"e3_null_{searcher}.npy"), dist)
        for pfx in PREFIXES:
            if pfx <= len(dist):
                d = dist[:pfx]
                rows.append({"searcher": searcher, "n_scramble": pfx,
                             "bar_mean": round(float(d.mean()), 4),
                             "bar_q95": round(float(np.quantile(d, 0.95)), 4),
                             "bar_max": round(float(d.max()), 4)})
        print(f"[e3] {searcher}: n={len(dist)} q95={np.quantile(dist,0.95):+.3f} "
              f"mean={dist.mean():+.3f} ({time.time()-t:.0f}s)")
    with open(os.path.join(OUT, "e3_bar_stability.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["searcher", "n_scramble", "bar_mean", "bar_q95", "bar_max"])
        w.writeheader(); w.writerows(rows)
    print(f"[e3] wrote results_v2/e3_bar_stability.csv ({len(rows)} rows)")


def _bar_q95(searcher):
    p = os.path.join(OUT, f"e3_null_{searcher}.npy")
    return float(np.quantile(np.load(p), 0.95)) if os.path.exists(p) else None


def run_e1(n_seeds=30, budget=200, depth=3, cost=0.0005):
    os.makedirs(OUT, exist_ok=True)
    panel, rets, bench, splits = setup(cost)
    bars = {"random": _bar_q95("random"), "linear": _bar_q95("linear")}
    if any(v is None for v in bars.values()):
        raise SystemExit("run --exp e3 first (need results_v2/e3_null_*.npy for the bars)")
    per_run, summary = [], []
    for rho in RHO_GRID:
        feats = synth_mod.make_features(panel, predictor=True, rho=rho, base=1.0, horizon=21, seed=0)
        for searcher in ("random", "linear"):
            t = time.time(); champs = []
            for sd in range(n_seeds):
                if searcher == "linear":
                    c = ms.linear_search(panel, rets, tools, splits, bench, seed=sd, k=1,
                                         feats=feats, cost=cost)["median_oos"]
                else:
                    b, _ = ms.random_search(panel, rets, tools, splits, bench,
                                            n_candidates=budget, seed=sd, depth=depth, k=1,
                                            feats=feats, cost=cost)
                    c = b["median_oos"] if b is not None else float("nan")
                champs.append(c)
                per_run.append({"rho": rho, "searcher": searcher, "seed": sd,
                                "champion_cv": round(float(c), 4)})
            champs = np.array(champs, dtype=float); bar = bars[searcher]
            summary.append({"rho": rho, "searcher": searcher, "bar_q95": round(bar, 4),
                            "p_clear": round(float((champs > bar).mean()), 3),
                            "median_champ": round(float(np.nanmedian(champs)), 4),
                            "n_seeds": n_seeds})
            print(f"[e1] rho={rho:.2f} {searcher:>6}: P(clear)={float((champs>bar).mean()):.2f} "
                  f"median={np.nanmedian(champs):+.3f} bar={bar:+.3f} ({time.time()-t:.0f}s)")
    with open(os.path.join(OUT, "e1_per_run.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["rho", "searcher", "seed", "champion_cv"])
        w.writeheader(); w.writerows(per_run)
    with open(os.path.join(OUT, "e1_power_curve.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["rho", "searcher", "bar_q95", "p_clear", "median_champ", "n_seeds"])
        w.writeheader(); w.writerows(summary)
    print(f"[e1] wrote results_v2/e1_power_curve.csv + e1_per_run.csv")


B_GRID = [10, 30, 100, 300, 1000, 3000, 10000]


def _pool_cv(specs, panel, rets, tools, splits, bench, feats, cost=0.0005, k=1):
    """CV median-OOS active Sharpe for each structure in a pool (parameterless, fast path)."""
    tests = [t for _, t in splits]
    cv = np.full(len(specs), np.nan)
    for i, spec in enumerate(specs):
        try:
            W = xs.top_k_weights(xs.score_matrix(ms.make_score_fn(spec), panel, tools, {}, feats), k)
            r = xs.portfolio_returns(W, rets, cost) - bench
            cv[i] = float(np.median([bt._sharpe_arr(r[t]) for t in tests]))
        except Exception:
            pass
    return cv


def run_e4(bmax=2000, n_scramble=100, n_pools=10, depth=3, seed=11,
           rhos=(0.0, 0.15, 0.20), cost=0.0005):
    """Capacity-failure: sweep the nonlinear search budget B (via cumulative max over a pool of
    bmax random structures) and measure (a) the noise bar q95(B) and (b) P(clear) for fixed
    signals. If P(clear) for a real signal falls as B grows, capacity is burying the signal."""
    os.makedirs(OUT, exist_ok=True)
    panel, rets, bench, splits = setup(cost)
    T, N = rets.shape
    rng = np.random.default_rng(seed)
    ctrl = synth_mod.make_features(panel, predictor=False, seed=99)

    # noise: a fresh pool per scramble (the pool IS the search); cumulative max over B
    t0 = time.time()
    noise_cummax = np.full((n_scramble, bmax), -np.inf)
    for s in range(n_scramble):
        specs = [ms.rand_tree(rng, depth) for _ in range(bmax)]
        rscr = rets * rng.choice([-1.0, 1.0], size=(T, N))
        bscr = xs.equalweight_returns(rscr, cost)
        cv = _pool_cv(specs, panel, rscr, tools, splits, bscr, ctrl, cost)
        noise_cummax[s] = np.fmax.accumulate(np.nan_to_num(cv, nan=-np.inf))
    np.save(os.path.join(OUT, "e4_noise_cummax.npy"), noise_cummax)
    grid = [B for B in B_GRID if B <= bmax]
    bar_of_B = {B: float(np.quantile(noise_cummax[:, B - 1], 0.95)) for B in grid}
    print(f"[e4] noise bars: " + "  ".join(f"B={B}:{bar_of_B[B]:+.3f}" for B in B_GRID)
          + f"  ({time.time()-t0:.0f}s)")

    rows = []
    for rho in rhos:
        feats = synth_mod.make_features(panel, predictor=True, rho=rho, base=1.0, horizon=21, seed=0)
        champ = np.full((n_pools, bmax), -np.inf)
        for p in range(n_pools):
            specs = [ms.rand_tree(rng, depth) for _ in range(bmax)]
            cv = _pool_cv(specs, panel, rets, tools, splits, bench, feats, cost)
            champ[p] = np.fmax.accumulate(np.nan_to_num(cv, nan=-np.inf))
        np.save(os.path.join(OUT, f"e4_champ_rho{rho:.2f}.npy"), champ)
        for B in grid:
            champs = champ[:, B - 1]
            bar = bar_of_B[B]
            rows.append({"rho": rho, "budget": B, "bar_q95": round(bar, 4),
                         "median_champ": round(float(np.median(champs)), 4),
                         "p_clear": round(float((champs > bar).mean()), 3), "n_pools": n_pools})
        print(f"[e4] rho={rho:.2f}: " + "  ".join(
            f"B={B}:P={float((champ[:,B-1]>bar_of_B[B]).mean()):.2f}" for B in grid))
    with open(os.path.join(OUT, "e4_capacity.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["rho", "budget", "bar_q95", "median_champ", "p_clear", "n_pools"])
        w.writeheader(); w.writerows(rows)
    print("[e4] wrote results_v2/e4_capacity.csv")


def run_e5(n_seeds=30, budget=200, depth=3, cost=0.0005):
    """Same-class ablation: certify NONLINEAR champions against (a) the correct nonlinear bar
    and (b) a mismatched LINEAR bar (a class smaller than the search). At rho=0 the correct bar
    gives ~5% false-cert; the mismatched bar should let many noise champions through."""
    os.makedirs(OUT, exist_ok=True)
    panel, rets, bench, splits = setup(cost)
    bar_correct = _bar_q95("random")     # nonlinear, matches the search
    bar_mismatch = _bar_q95("linear")    # too-small class
    if bar_correct is None or bar_mismatch is None:
        raise SystemExit("run --exp e3 first (need e3_null_random.npy and e3_null_linear.npy)")
    rows = []
    for rho in (0.0, 0.15):
        feats = synth_mod.make_features(panel, predictor=True, rho=rho, base=1.0, horizon=21, seed=0)
        champs = []
        for sd in range(n_seeds):
            b, _ = ms.random_search(panel, rets, tools, splits, bench, n_candidates=budget,
                                    seed=sd, depth=depth, k=1, feats=feats, cost=cost)
            champs.append(b["median_oos"] if b is not None else np.nan)
        champs = np.array(champs, dtype=float)
        for label, bar in (("correct_nonlinear", bar_correct), ("mismatched_linear", bar_mismatch)):
            rows.append({"rho": rho, "bar": label, "bar_q95": round(bar, 4),
                         "false_cert_rate" if rho == 0.0 else "cert_rate":
                         round(float((champs > bar).mean()), 3), "n_seeds": n_seeds})
        print(f"[e5] rho={rho}: correct(bar={bar_correct:+.2f}) "
              f"clear={(champs>bar_correct).mean():.2f} | "
              f"mismatched-linear(bar={bar_mismatch:+.2f}) clear={(champs>bar_mismatch).mean():.2f}")
    with open(os.path.join(OUT, "e5_ablation.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["rho", "bar", "bar_q95", "false_cert_rate", "cert_rate", "n_seeds"])
        w.writeheader(); w.writerows(rows)
    print("[e5] wrote results_v2/e5_ablation.csv")


def run_e12a(n_seeds=30, budget=200, depth=3, cost=0.0005, seed_noise=777):
    """Withhold-the-primitive: the signal is injected into feat_c, but the searcher's feat_c is
    OVERWRITTEN with independent noise, so the predictive primitive is not in the accessible
    vocabulary. Power should stay at null across all rho (compare to E1, which recovers)."""
    os.makedirs(OUT, exist_ok=True)
    panel, rets, bench, splits = setup(cost)
    bar = _bar_q95("random")
    if bar is None:
        raise SystemExit("run --exp e3 first (need e3_null_random.npy)")
    T, N = rets.shape
    rng = np.random.default_rng(seed_noise)
    rows = []
    for rho in RHO_GRID:
        feats = synth_mod.make_features(panel, predictor=True, rho=rho, base=1.0, horizon=21, seed=0)
        feats = dict(feats)
        noise_c = synth_mod._ar1_noise(T, N, seed=int(rng.integers(0, 2**31 - 1)))
        feats["feat_c"] = __import__("pandas").DataFrame(noise_c, index=panel.index, columns=panel.columns)
        champs = []
        for sd in range(n_seeds):
            b, _ = ms.random_search(panel, rets, tools, splits, bench, n_candidates=budget,
                                    seed=sd, depth=depth, k=1, feats=feats, cost=cost)
            champs.append(b["median_oos"] if b is not None else np.nan)
        champs = np.array(champs, dtype=float)
        rows.append({"rho": rho, "bar_q95": round(bar, 4),
                     "p_clear": round(float((champs > bar).mean()), 3),
                     "median_champ": round(float(np.nanmedian(champs)), 4), "n_seeds": n_seeds})
        print(f"[e12a] rho={rho:.2f}: P(clear)={float((champs>bar).mean()):.2f} "
              f"median={np.nanmedian(champs):+.3f} (feat_c withheld)")
    with open(os.path.join(OUT, "e12a_withhold.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["rho", "bar_q95", "p_clear", "median_champ", "n_seeds"])
        w.writeheader(); w.writerows(rows)
    print("[e12a] wrote results_v2/e12a_withhold.csv")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", choices=["e1", "e3", "e4", "e5", "e12a"], required=True)
    ap.add_argument("--bmax", type=int, default=2000)
    ap.add_argument("--n-pools", type=int, default=10)
    ap.add_argument("--n-scramble", type=int, default=1000)
    ap.add_argument("--n-seeds", type=int, default=30)
    ap.add_argument("--budget", type=int, default=200)
    ap.add_argument("--depth", type=int, default=3)
    a = ap.parse_args()
    if a.exp == "e3":
        run_e3(n_scramble=a.n_scramble, budget=a.budget, depth=a.depth)
    elif a.exp == "e4":
        run_e4(bmax=a.bmax, n_scramble=a.n_scramble, n_pools=a.n_pools, depth=a.depth)
    elif a.exp == "e5":
        run_e5(n_seeds=a.n_seeds, budget=a.budget, depth=a.depth)
    elif a.exp == "e12a":
        run_e12a(n_seeds=a.n_seeds, budget=a.budget, depth=a.depth)
    else:
        run_e1(n_seeds=a.n_seeds, budget=a.budget, depth=a.depth)
