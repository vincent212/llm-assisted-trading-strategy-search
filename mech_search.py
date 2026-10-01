"""
Mechanical (non-LLM) searchers over the SAME cross-sectional score() contract the LLM uses,
reusing the exact evaluation stack (backtest_xs.ccv_median_oos + rademacher_bar). Purpose:
carry the high-N statistics for the v2 experiments (power curve, capacity failure, bar
stability, same-class ablation) at zero LLM-token cost, and serve as baselines that isolate
the LLM's contribution.

Three searchers, matching the strategy classes discussed in the paper:
  * linear_search      — bounded LINEAR class: score = sum_i w_i * feat_i, weights DE-fit.
  * random_search      — high-capacity NONLINEAR class: random expression trees over the four
                         features (baked-in constants => parameterless => no DE => cheap, so
                         search budget can be cranked to 1e5 for the capacity experiments).
  * gp_search          — genetic programming over the same tree grammar (mutation + tournament).

All operate on the four opaque synthetic features feat_a..feat_d (synth.py), name-symmetric,
scored on active return vs the equal-weight benchmark exactly like the LLM loop.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

import backtest as bt
import backtest_xs as xs

FEATS = ["feat_a", "feat_b", "feat_c", "feat_d"]
UNARY = ["neg", "abs", "sign", "clip", "z"]
BINARY = ["+", "-", "*", "safediv", "max", "min", "gate"]


# ---- random expression trees over the four features ------------------------

def rand_tree(rng, depth, p_leaf=0.35):
    """A nested spec tuple. Constants are baked in at generation time, so the resulting
    score() has an EMPTY param space and ccv_median_oos skips differential evolution."""
    if depth <= 0 or rng.random() < p_leaf:
        return ("leaf", int(rng.integers(0, 4)))
    if rng.random() < 0.45:
        op = str(rng.choice(UNARY))
        return ("u", op, rand_tree(rng, depth - 1, p_leaf),
                float(rng.uniform(0.5, 2.0)), int(rng.integers(10, 120)))
    op = str(rng.choice(BINARY))
    return ("b", op, rand_tree(rng, depth - 1, p_leaf), rand_tree(rng, depth - 1, p_leaf),
            float(rng.uniform(-1.0, 1.0)))


def _eval_spec(spec, F):
    """Evaluate a spec against F = [feat_a..feat_d] Series for ONE name -> Series."""
    t = spec[0]
    if t == "leaf":
        return F[spec[1]]
    if t == "u":
        _, op, arg, c, n = spec
        x = _eval_spec(arg, F)
        if op == "neg":
            return -x
        if op == "abs":
            return x.abs()
        if op == "sign":
            return pd.Series(np.sign(x.to_numpy()), index=x.index)
        if op == "clip":
            return x.clip(-c, c)
        if op == "z":
            m = x.rolling(n).mean()
            s = x.rolling(n).std()
            return (x - m) / (s + 1e-9)
    if t == "b":
        _, op, a, b, thr = spec
        A = _eval_spec(a, F)
        B = _eval_spec(b, F)
        if op == "+":
            return A + B
        if op == "-":
            return A - B
        if op == "*":
            return A * B
        if op == "safediv":
            return A / (B.abs() + 1e-9)
        if op == "max":
            return pd.concat([A, B], axis=1).max(axis=1)
        if op == "min":
            return pd.concat([A, B], axis=1).min(axis=1)
        if op == "gate":
            return A.where(B > thr, 0.0)
    raise ValueError(f"bad spec {spec!r}")


def tree_depth(spec):
    if spec[0] == "leaf":
        return 1
    if spec[0] == "u":
        return 1 + tree_depth(spec[2])
    return 1 + max(tree_depth(spec[2]), tree_depth(spec[3]))


def make_score_fn(spec):
    """A parameterless score(series, feats, tools, p) that evaluates the spec."""
    def score(series, feats, tools, p):
        F = [feats[k].fillna(0.0) for k in FEATS]
        s = _eval_spec(spec, F)
        return pd.Series(np.asarray(s, dtype=float).ravel(), index=series.index).fillna(0.0)
    return score


# ---- fast CV for parameterless candidates ----------------------------------

def _cv_score_parameterless(fn, panel, rets, tools, splits, bench, cost=0.0005, k=1, feats=None):
    """Median-OOS active Sharpe for a candidate with NO tunable params. The score matrix is
    identical across folds, so compute it ONCE and slice per test fold (ccv_median_oos would
    recompute it k times). Returns median over folds of the fold's OOS active Sharpe."""
    W = xs.top_k_weights(xs.score_matrix(fn, panel, tools, {}, feats), k)
    r = xs.portfolio_returns(W, rets, cost) - bench
    fold = [bt._sharpe_arr(r[test]) for _, test in splits]
    return float(np.median(fold))


# ---- searchers -------------------------------------------------------------

def linear_search(panel, rets, tools, splits, bench, seed=0, k=1, feats=None, fit_budget=150,
                  cost=0.0005):
    """Bounded LINEAR class: score = wa*a + wb*b + wc*c + wd*d, weights fit by DE."""
    def score(series, feats, tools, p):
        return (p["wa"] * feats["feat_a"].fillna(0.0) + p["wb"] * feats["feat_b"].fillna(0.0)
                + p["wc"] * feats["feat_c"].fillna(0.0) + p["wd"] * feats["feat_d"].fillna(0.0))
    space = {"wa": ("float", -1.0, 1.0), "wb": ("float", -1.0, 1.0),
             "wc": ("float", -1.0, 1.0), "wd": ("float", -1.0, 1.0)}
    d = xs.ccv_median_oos(score, space, panel, rets, tools, splits, bench,
                          budget=fit_budget, cost=cost, seed=seed, k=k, feats=feats)
    return {"median_oos": d["median_oos"], "kind": "linear", "diag": d}


def random_search(panel, rets, tools, splits, bench, n_candidates=200, seed=0, depth=3,
                  k=1, feats=None, cost=0.0005):
    """High-capacity nonlinear class: evaluate n_candidates random trees, keep the best CV.
    Returns (best_dict, all_scores). n_candidates is the SEARCH BUDGET (capacity knob)."""
    rng = np.random.default_rng(seed)
    scores = np.full(n_candidates, np.nan)
    best = None
    for i in range(n_candidates):
        spec = rand_tree(rng, depth)
        fn = make_score_fn(spec)
        try:
            s = _cv_score_parameterless(fn, panel, rets, tools, splits, bench, cost, k, feats)
        except Exception:
            s = np.nan
        scores[i] = s
        if np.isfinite(s) and (best is None or s > best["median_oos"]):
            best = {"median_oos": float(s), "spec": spec, "kind": "random"}
    return best, scores


def noise_bestfit_distribution(panel, rets, tools, splits, seed=0, n_scramble=1000,
                               searcher="random", budget=200, depth=3, k=1, feats=None,
                               cost=0.0005):
    """The null-max (empirical Rademacher) distribution for a mechanical class: for each of
    n_scramble sign-flips of the return matrix, the best-in-class CV fit to that noise. The
    q95 of the returned array is the bar; taking q95 over growing prefixes gives the E3
    bar-stability curve. Sign-flipping the returns destroys any feat->return relation, so the
    distribution is ~independent of the feature signal level (compute it once per class)."""
    rng = np.random.default_rng(seed)
    T, N = rets.shape
    out = np.full(n_scramble, np.nan)
    for s in range(n_scramble):
        rscr = rets * rng.choice([-1.0, 1.0], size=(T, N))
        bscr = xs.equalweight_returns(rscr, cost)
        sd = int(rng.integers(0, 2**31 - 1))
        if searcher == "linear":
            out[s] = linear_search(panel, rscr, tools, splits, bscr, seed=sd, k=k,
                                   feats=feats, cost=cost)["median_oos"]
        else:
            b, _ = random_search(panel, rscr, tools, splits, bscr, n_candidates=budget,
                                 seed=sd, depth=depth, k=k, feats=feats, cost=cost)
            out[s] = b["median_oos"] if b is not None else np.nan
    return out[np.isfinite(out)]


def gp_search(panel, rets, tools, splits, bench, pop_size=40, generations=10, seed=0, depth=3,
              k=1, feats=None, cost=0.0005, tournament=3, p_mut=0.4):
    """Genetic programming over the tree grammar: tournament selection + subtree mutation.
    Search budget ~= pop_size * generations candidate evaluations."""
    rng = np.random.default_rng(seed)

    def fitness(spec):
        try:
            return _cv_score_parameterless(make_score_fn(spec), panel, rets, tools, splits,
                                           bench, cost, k, feats)
        except Exception:
            return -np.inf

    def mutate(spec, d):
        if rng.random() < 0.5 or spec[0] == "leaf":
            return rand_tree(rng, max(1, d))
        if spec[0] == "u":
            return ("u", spec[1], mutate(spec[2], d - 1), spec[3], spec[4])
        which = 2 if rng.random() < 0.5 else 3
        parts = list(spec)
        parts[which] = mutate(spec[which], d - 1)
        return tuple(parts)

    pop = [rand_tree(rng, depth) for _ in range(pop_size)]
    fits = [fitness(s) for s in pop]
    n_eval = pop_size
    best_i = int(np.argmax(fits))
    best = {"median_oos": float(fits[best_i]), "spec": pop[best_i], "kind": "gp"}
    for _ in range(generations - 1):
        newpop = [best["spec"]]                                 # elitism
        while len(newpop) < pop_size:
            idx = rng.integers(0, pop_size, tournament)
            parent = pop[idx[int(np.argmax([fits[j] for j in idx]))]]
            child = mutate(parent, depth) if rng.random() < p_mut else parent
            newpop.append(child)
        pop = newpop
        fits = [fitness(s) for s in pop]
        n_eval += pop_size
        gi = int(np.argmax(fits))
        if fits[gi] > best["median_oos"]:
            best = {"median_oos": float(fits[gi]), "spec": pop[gi], "kind": "gp"}
    best["n_eval"] = n_eval
    return best
