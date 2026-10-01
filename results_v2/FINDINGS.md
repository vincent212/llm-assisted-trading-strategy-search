# v2 mechanical-experiment findings (feed §4/§5 rewrite)

All numbers from `mech_search.py` + `exp_v2_synth.py`, reusing the exact eval stack
(`backtest_xs`), Mag-7 panel 2015→2026 (2952 bars, ~11.7y), purged 6-fold CV (embargo 250),
active Sharpe vs equal-weight. No LLM. CSVs in this directory.

## E3 — null-max bar (1000 scrambles)
| class | bar mean | bar q95 |
|---|---|---|
| random (high-capacity nonlinear, budget 200) | +0.562 | +0.844 |
| linear (bounded, DE-fit 4 weights) | −0.215 | +0.408 |

Capacity sets the bar. Bar-stability (q95 vs #scrambles): random stable by ~100 scrambles
(+0.87→+0.84); **linear q95 keeps climbing to 1000 (+0.22→+0.41), tail max +0.30→+1.09 — 30
scrambles materially under-estimates the low-capacity bar.** (`e3_bar_stability.csv`)

## E1 — power curve (N=30/cell; false-positive rate at ρ=0 is 0/30 for both classes)
Clearing boundary ~ρ 0.15–0.20 (oracle active Sharpe ~0.3–0.66), matches the original paper's
~0.66. **Not** a clean "simplicity buys sensitivity" result: at ρ=0.20/0.25 the random class
certifies *more* reliably (1.00 vs linear 0.70/0.80) because its champion overfits above its
higher bar. The two classes mostly just have different bars. (`e1_power_curve.csv`,
`e1_per_run.csv`)

## E4 — capacity sweep (nonlinear class, budget B=10→2000; n_pools=10)
Bar q95 rises monotonically with budget: 0.595 / 0.681 / 0.807 / 0.849 / 0.944 / 0.990.
False-positive rate at ρ=0 stays **0/10 at every budget**. Real-signal power does not collapse
in range: ρ=0.20 → P(clear)=1.00 at all B (champion 1.01→1.32 outpaces bar); ρ=0.15 noisy
0.2–0.8, no trend (champion and bar rise together). (`e4_capacity.csv`)

## FINDING (state with caveats — do NOT overclaim)

**Statement for the paper.** With the same-class empirical bar recomputed over the exact
search, the nominal false-positive rate is preserved across search budgets up to B=2000: the
price of capacity is a *rising bar* (reduced power), not false certification. The
Experiment-1 near-pass (+0.500 vs +0.495) is the q95 tail — a 1-in-20 false positive by
design — **not** a capacity "sneak-through."

**Grain of salt (must accompany the finding).**
1. **Largely by construction, not a discovery.** Matched-class bar + a valid null pins the FPR
   at ~1−q at any capacity; E4 only *confirms* this holds empirically to B=2000.
2. **Naive expectation is the opposite.** One expects a high-capacity search to sneak past the
   bar; that it does not here is encouraging but **preliminary**. It **warrants further study**
   before it is asserted generally.
3. **Untested regimes.** B capped at 2000 (finite/moderate); the VC limit (bar→∞ as h→∞)
   predicts a *power* collapse at extreme capacity that we have not reached.
4. **Null-validity hole.** Sign-flip tests *directional* signal only. A high-capacity class
   exploiting *non-directional* structure (vol/magnitude timing) could score higher on real
   signal-free returns than on sign-flipped ones → capacity-driven false positives the bar
   misses. Our AR(1)-noise features have no such channel, so E4 cannot see it.
5. **Setup-dependent.** Power survived capacity only because the synthetic oracle is strong and
   clean, so the champion amplifies real signal as fast as noise; not guaranteed on real data.

**Consequence for the manuscript.** The current "sneak-through / overfitting is unpreventable /
must impose a-priori simplicity" framing is not supported at tested capacities and must be
re-scoped: the bar controls false positives; the case for a simpler class is about **power**
(lower bar → certifies weaker real signal), which E1 did not yet cleanly demonstrate.

## E7 — LLM-vs-mechanical (subagent = Opus as mutation operator, iterations=12, 3 seeds/rho)
The LLM arm uses `LLM_PROVIDER=subagent` (the Claude Code subagent is the mutation operator —
state this in methods). Certified against the FIXED E3 nonlinear bar (q95 +0.844) for
apples-to-apples with mechanical E1 (`run_mag7` computes a per-run bar over the run's own
smaller population, ~0.45–0.71 — noted, not used for the comparison). (`e7_llm.csv`)

| rho | LLM clears (fixed bar) | LLM champion CVs | mechanical E1 P(clear) |
|---|---|---|---|
| 0.00 | 0/3 | 0.515, 0.225, −0.047 | 0.00 |
| 0.15 | 1/3 | 0.819, 0.906, 0.358 | 0.43 |
| 0.20 | 3/3 | 1.217, 1.021, 1.396 | 1.00 |

**Finding:** the LLM-driven search recovers signal at the **same boundary** as mechanical
random search and detects no weaker signal; champions anchor on feat_c (the real primitive).
The LLM adds no detection power over mechanical search of the same vocabulary — supporting the
ceiling argument (§8). False-positive control holds for the LLM arm too (0/3 at rho=0).

## E12a — withhold-the-primitive (vocabulary boundary; mechanical, N=30/rho)
Signal injected into feat_c, but the searcher's feat_c is overwritten with independent noise, so
the predictive primitive is NOT in the accessible vocabulary. Result: **P(clear)=0.00 at every
rho from 0.0 to 0.70** (median champ ~0.43, fixed bar 0.844) — zero recovery at any signal
strength, versus E1 (feat_c accessible) which recovers reliably from rho=0.20. (`e12a_withhold.csv`)

**Finding (§8 anchor):** search performance is gated by whether the predictive primitive is in
the supplied vocabulary, not by signal strength or search effort — the empirical core of
"searching the given space harder never surfaces what lies outside it." Caveat to state: a
mechanical searcher fails identically here, so this establishes the vocabulary boundary, not an
LLM-specific failure.

## E4 — capacity sweep to B=10^4 (nonlinear class, n_pools=30; `e4_capacity.csv`)
Noise bar q95 rises monotonically with search budget, no plateau:
B=10 .. 10^4 -> 0.587, 0.697, 0.790, 0.884, 0.947, 1.037, **1.199**.

- **FPR at rho=0 stays exactly 0/30 at EVERY budget including 10^4** — the bar self-calibrates;
  capacity does not manufacture false positives (now confirmed across 3 decades of budget).
- **rho=0.15 (threshold signal): champion and bar rise in lockstep** (champ median 0.66->1.18,
  bar 0.59->1.20; gap ~0), so P(clear) stays marginal 0.17-0.53 at all budgets — capacity
  neither rescues nor buries it.
- **rho=0.20 (clear signal): survives to 10^4** (P~1.0; champ median 1.01->1.41 > bar).

**Finding:** "capacity breaks certification" is NOT observed up to B=10^4. The robust effect is
(i) FPR control holds at all capacities (by construction + confirmed) and (ii) the bar and the
real-signal champion rise together. Grain of salt updated: tested to 10^4, not beyond; the VC
limit still predicts eventual power loss for a FIXED weak signal as the bar grows without bound,
consistent with the observed lockstep (the bar slowly catching the weak champion), but no
collapse within the tested range. Raw arrays: e4_noise_cummax.npy, e4_champ_rho*.npy.

## E12b — dropped to future work
Not constructible in the synthetic framework: the injected driver (feat_c) is arbitrary and
unnameable, so there is no hypothesis for the LLM (or a human) to abduce — no jump is possible
for anyone in a closed synthetic world. A real jump test needs a semantically nameable driver
+ a human/oracle positive control (a separate testbed). §8's empirical anchor is E12a + the
formal argument + the systems audit.

## Pending runs to firm this up (not yet run)
- Budget → 10⁴–10⁵: does FPR stay ~5% and does fixed-weak-signal power erode as the bar climbs?
- n_pools 30–50 at ρ=0 and ρ=0.15: measure FPR precisely (expect ~5%, not 0) and de-noise the boundary.
- Null-validity stress test: give the class a non-directional overfitting channel; check whether
  capacity then produces false positives the sign-flip bar misses.
