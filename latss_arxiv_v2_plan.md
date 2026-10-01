# LATSS arXiv v2 — revision plan (response to reviewer critique)

Goal: convert the current paper (strong position note + one small experiment) into a
systematic empirical study of **signal power × search capacity × failure modes**, plus a
tighter conceptual section. Every task below is mapped to concrete code in this repo.

## The key insight that makes this affordable

The single biggest reviewer attack ("only 3 runs") and the most important missing experiment
("isolate the LLM's contribution") have the **same fix**: make **mechanical (non-LLM)
searchers** the statistical workhorse.

- Mechanical searchers (random-structure, GP, linear-DE) reuse the *exact* evaluation stack
  (`backtest_xs.score_matrix` → `top_k_weights` → `ccv_median_oos` → `rademacher_bar`), cost
  no LLM tokens, and can be run 30–1000× per cell and cranked to 10^5 candidates.
- That gives us high-N power curves, bar statistics, capacity-failure curves, and the
  same-class ablation cheaply — and *simultaneously* answers "does the LLM add anything?"
  because the LLM becomes one searcher among several being compared at a few anchor points.

So: **mechanical search carries the statistics; LLM runs are reserved for a small,
high-value comparison.** This is the critical path.

---

## Paper restructure (reviewer point 19)

```
1  Introduction
2  LATSS (architecture)
3  Experimental framework   (ground truth, search classes, optimizer, CV, null-max bar)
4  Does LATSS measure signal?      (null control · power curve · amplification · identification)
5  How does capacity break certification?  (search budget · sample length · #scrambles · same-class ablation)
6  Does the LLM contribute?        (random · GP · linear · LATSS; budget curves)
7  Real-data experiments           (NVDA expanded · multi-dataset pre-registered · forward test)
8  Search vs abduction             (compressed ~35%; reframed as capability-boundary hypothesis)
9  Threat model + Limitations
10 Conclusion
```

---

## Phase 0 — Instrumentation & harness (no LLM; ~0.5–1 day eng)

Prereq for everything. All in existing files.

- **Search telemetry** (point 4): in `run_mag7.evaluate` / the loop, log per run:
  `n_proposals, n_unique, n_evaluated, total_DE_evals, champion_rank, duplicate_rate,
  wall_clock, tokens, generations`. Emit to the run JSON.
- **Champion feature-usage parser** (point 10): detect which of `feat_a..d` the champion code
  references (regex on saved champion source) + rank of `feat_c` vs decoys. New helper.
- **Full null-distribution dump**: have `xs.rademacher_bar` optionally return the raw
  `bars` array (it already computes it, line 263) so we can plot the null and study q95
  stability. Expose `n_scramble` in the `run_mag7` caller (currently hardcoded 30 at
  `run_mag7.py:410`).
- **Batch runner + aggregator**: one script that runs a grid `(searcher, ground_truth, rho,
  capacity, sample_len, seed)` and writes a tidy CSV; one plotting module. (Generalizes the
  ad-hoc `RUN_MATRIX.md` batches.)

## Phase 1 — Non-LLM searchers (no LLM; ~1–2 days eng) — points 3, 18

Implement three drop-in searchers over the same `score(series, feats, tools, p)` contract:

- **Linear-DE**: `score = Σ βᵢ·featᵢ`, β fit by `differential_evolution` (no LLM). Bounded
  class, h≈d+1 — connects to the VC discussion.
- **Random-structure**: sample nonlinear expressions from the same operator/tool grammar the
  LLM uses; fit params by DE. High capacity, LLM-free.
- **GP**: minimal tree-based genetic programming over the same grammar (mutation/crossover).

All reuse `ccv_median_oos` and `rademacher_bar` unchanged. Validate they produce comparable
champions on a known signal before using them as baselines.

## Phase 2 — Core measurement experiments (mostly mechanical, high-N; compute-bound, no/low LLM)

- **E1 Power curve** (points 1, 2): ρ ∈ {0,0.1,…,1.0}, **N≥30 seeds/cell**, per searcher.
  Report `P(clear)`, median champion CV, median bar, **false-positive rate at ρ=0**.
  → *Figure: P(certification) vs true injected Sharpe* (the single highest-ROI addition).
- **E2 Search amplification** (point 2): scatter of champion active Sharpe vs oracle active
  Sharpe, with `y=x`, the Rademacher bar, individual runs, and CI bands. Shows LATSS
  discovers complex strategies *around* the signal, often above the oracle.
- **E3 Bar statistics** (point 5): full null distribution at **1000 scrambles**; q95
  stability curve over n_scramble ∈ {30,50,100,250,500,1000}. Answers "how many null draws
  until the bar stabilizes?" Raises the headline bar from 30→500–1000 scrambles.
- **E4 Capacity-induced failure** (point 6): ρ=0 (pure noise), sweep search budget
  {10,10²,10³,10⁴,10⁵} and sample length; plot `max CV_noise` and `q95(noise)` vs capacity.
  → *Heatmap: P(false certification | capacity, sample length)*. Mechanical searcher makes
  10⁵ candidates affordable. Turns the "necessary but not sufficient" assertion into a curve.
- **E5 Same-class ablation** (point 17): certify nonlinear champions against (a) a correct
  nonlinear bar vs (b) an under-powered linear bar; show the false-cert rate explodes under
  the mismatched bar. Direct demonstration of the same-class condition.
- **E6 Ablation table** (point 18): full LATSS vs {no-DE, no-CV (random split), no-bar,
  restricted-class, random-search} on {signal recovery, noise rejection, search efficiency,
  false-cert}.

## Phase 3 — LLM contribution + richer ground truth (LLM runs, smaller N)

- **E7 LLM vs mechanical** (points 3, 4): at ~3 anchor ρ values, N≈10–20 LLM runs vs the
  mechanical searchers; search-budget curve (best CV vs #candidates evaluated) for
  LATSS/random/GP/linear. This is where the LLM either earns its place (detects weaker signal
  / fewer evals) or doesn't — either result is publishable.
- **E8 Ground-truth families** (point 9): extend `synth.py` beyond the linear oracle:
  nonlinear `y=f(x)`, interaction `x₁x₂`, conditional/regime `x₁ if x₂>0`, and **decoy
  dimensionality** (1 real predictor among 10/50/100 noise features). Mechanical for high-N;
  LLM at key points. Connects to the "vocabulary defines the space" thesis.
- **E9 Signal identification** (point 10): across all runs, frequency the champion uses
  `feat_c`, its structural importance, and rank vs decoys — a second outcome (discovery) on
  top of performance.

## Phase 4 — Real data (LLM runs)

- **E10 NVDA** (point 11): either expand to a full protocol (train/test windows, budget,
  discovered rule, params, CV distribution, turnover, costs, drawdown, CIs) or cut. Lean
  expand.
- **E11 Multi-dataset, pre-registered** (point 12): 2–4 real feature sets (technical /
  cross-sectional equity / macro / orthogonal); fix feature set + protocol *before* running;
  report in-sample champion, CV, bar, sealed forward result, turnover, costs. **Negative
  results are legitimate evidence** for the instrument thesis.

## Phase 5 — Writing & framing (no compute)

- **Restructure** to the outline above (point 19).
- **Compress abduction ~35%** (point 13): cut repeated search-vs-abduction restatements and
  trim the Einstein/FunSearch/world-model passages to their essentials.
- **Reframe the thesis** (points 14, 7): replace universal "cannot" with a **capability-
  boundary hypothesis** — "no current LATSS-style system has demonstrated reliable discovery
  of economically novel alpha outside its supplied hypothesis space." Frame abduction as a
  conceptual boundary, not a proven theorem.
- **Certification terminology** (point 7): split **statistical certification** (clears the
  empirical null) from **evidence of genuine signal** (certification + robustness + forward
  validation); use consistently.
- **Threat model** (point 16): explicit table of what LATSS protects against (parameter
  overfit, in-class selection bias, feature-selection search, LLM stochasticity) vs does not
  (bad data, survivorship, look-ahead, market impact, nonstationarity, regime change, hidden
  researcher DoF, post-hoc universe/vocabulary changes).
- **Active-Sharpe justification** (point 8): short subsection — why equal-weight benchmark,
  arithmetic active return, Sharpe vs IR, behavior for k>1 / long-short / volatile benchmark,
  symmetric rebalancing cost (already handled in `equalweight_returns`).
- **Literature** (point 15): add data-snooping, PBO (probability of backtest overfitting),
  multiple testing, model selection, GP-for-trading, symbolic regression, automated feature
  engineering — the real lineage of the null-max idea.

---

## Three experimentally-demonstrated propositions the v2 should establish

1. A sufficiently strong known signal is recoverable and certifiable by LATSS (E1, E2).
2. A correctly matched null-max bar tracks the apparent skill the search class manufactures
   (E3, E5).
3. As search capacity approaches the data's information content, the bar loses discriminatory
   power even when correctly computed (E4). → motivates the capability-boundary framing (§8).

## Minimum-viable arXiv v2 (maps the reviewer's top-5)

| Reviewer top-5 | This plan | LLM cost |
|---|---|---|
| 30–50 runs/cell | E1 (mechanical N≥30) + E7 (LLM N≈15 at anchors) | low |
| 500–1000 scrambles | E3 | none |
| search-capacity failure | E4 | none |
| non-LLM baselines | Phase 1 + E7 | none/low |
| real multi-dataset | E11 | medium |

## Compute realism

- Mechanical experiments (E1–E6, most of E8): CPU/DE-bound, embarrassingly parallel, hours→a
  couple of days on this box. No token cost.
- LLM runs (E7, E10, E11, LLM anchors of E8): the real budget lever. Each LATSS search ≈ the
  RUN_MATRIX cost (~30–50k tokens via the fast-wait servicer). Total LLM run count is the
  thing to cap.

## LOCKED SCOPE (decided)

- **LLM budget: Minimal (~20 runs total).** Mechanical searchers (Phase 1) carry ALL high-N
  power/capacity/bar statistics. The ~20 LLM runs go to E7 (LLM-vs-mechanical at ~3 anchor ρ)
  and E10 (NVDA). No LLM-led power curve, no LLM 3D sweep.
- **Scope: Minimum-viable (reviewer top-5) + cheap writing fixes.**
  IN: E1 power curve (mechanical, N≥30), E3 (1000 scrambles + stability), E4 (capacity
  failure), Phase 1 baselines + E5 same-class ablation + E7 (LLM contribution), E11 real
  multi-dataset. Plus restructure (§19, reordering only) and the active-Sharpe justification.
  OUT (deferred, not this revision): E6 full ablation table, E8 extra ground-truth families
  (keep only the decoy-dimensionality variant if cheap), E9 signal-identification as its own
  section, threat-model table, full literature expansion.
- **Framing: KEEP the strong claim.** Retain the universal "LLMs cannot invent new alpha"
  thesis and the abduction section at full length — do NOT reframe to a capability-boundary
  hypothesis and do NOT compress §6. New experiments are added alongside it. (Restructure =
  reorder so experiments precede abduction; abduction content is preserved, not cut.)

## Execution order (checklist)

1. Phase 0 — instrumentation: telemetry, null-dist dump, expose `n_scramble`, batch
   runner + CSV aggregator, plotting module.
2. Phase 1 — mechanical searchers: linear-DE, random-structure, GP over the existing
   `score()` contract; validate on a known signal.
3. E3 — bar statistics (1000 scrambles + q95 stability curve). *No LLM; do early — it also
   fixes the headline bar used everywhere else.*
4. E1 — power curve, mechanical, ρ∈{0..1}, N≥30/cell, per searcher. *Central figure.*
5. E2 — search-amplification scatter (falls out of E1 data).
6. E4 — capacity-failure heatmap (ρ=0, sweep budget & sample length).
7. E5 — same-class ablation (correct vs mismatched linear bar → false-cert rate).
8. E7 — LLM vs mechanical at ~3 anchor ρ (≈15 of the 20 LLM runs) + budget curve.
9. E11 — real multi-dataset, pre-registered protocol, forward test. (~5 LLM runs.)
10. E10 — NVDA expanded vignette (reuses an existing/1 new run).
11. Phase 5 (writing) — restructure/reorder, active-Sharpe subsection, fold all figures/
    tables in, keep abduction full-length and the strong claim.

Deferred items (E6, E8-extended, E9, threat model, literature) parked at the bottom of the
paper's future-work or a v3.

---

# Expanded §8 — "Search versus abduction" as a full section

Directive: make §8 bigger via **rigor and evidence**, not more analogy. The added length is
formalization, a measurement rubric, two experiments, and a systems audit — not more
Einstein/FunSearch restatement. The strong claim ("LLMs cannot invent new alpha") is kept;
these additions *earn* it.

## Proposed structure

```
8.1  Search vs abduction, formalized      (H, E, reachable set, the jump)      [new: formal]
8.2  A rubric for novelty                  (4-level table + falsifiability)     [new: framework]
8.3  Two ceilings: cognitive vs market-structure                               [expanded]
8.4  Experiment: the jump gap              (withhold-primitive + affordance)    [new: evidence]
8.5  Experiment: cutoff dissociation       (retrieval vs abduction)            [new: evidence]
8.6  Systems audit                         (where current alpha agents sit)     [new: table]
8.7  Beyond finance                        (discovery-difficulty spectrum)      [new]
8.8  A discovery that required a jump       (finance case study, replaces Einstein)
8.9  The ceiling, restated                 (strong claim, now earned)           [kept]
```

Priority order: 8.4/8.5 (experiments) > 8.2 (rubric) > 8.6 (audit) > 8.1 (formalization).

## 8.1 Formalization
Define a hypothesis space `H`, evaluator `E`, a searcher as `argmax_{h∈H} E(h)`, and abduction
as producing `h ∉ H` (extending `H`). Define an LLM's **reachable set** = closure of its
training distribution under recombination/interpolation; a **jump** = an element outside that
closure. Cast the "just propose the hypotheses one level up" rebuttal as a lemma: lifting from
formulas to ideas enlarges the vocabulary but stays inside the closure → still search. Tie to
Balestriero–Pesenti–LeCun (high-dim learning = interpolation, not extrapolation).

## 8.2 Novelty rubric (table + falsifiability)
Turn the 4-level taxonomy into a rubric with columns:
`level · definition · example · evidence that would demonstrate it · current state · what would
falsify "can't"`. Levels: syntactic / solution / hypothesis / economic. This is a reusable
contribution, not a list. **Falsifiability clause:** the ceiling is refuted by a system that,
given raw data and no supplied vocabulary, repeatedly finds durable *out-of-space* edges with a
human/oracle positive control clearing the same bar.

## 8.3 Two independent ceilings
Separate the tangled reasons alpha resists automated discovery: (a) **cognitive** — can't
originate the hypothesis; (b) **market-structure** — adversarial, perishable, crowding /
reflexivity, no clean causal oracle. State: novelty is *necessary but not sufficient* for
durable alpha.

## 8.6 Systems audit table
Classify each cited alpha agent (AlphaAgent, Alpha-GPT, CogAlpha, QuantaAlpha, AlphaLogics,
EFS, RD-Agent, AlphaGen, Hubble, …) by `primitive vocabulary · search space · machinery ·
highest novelty level claimed vs. demonstrated`. Result: all land at level 2. Note AlphaAgent's
AST-similarity penalty as field evidence that LLMs regenerate crowded factors (retrieval-novelty).

## 8.7 Beyond finance
Spectrum table across AI-discovery results (FunSearch, AlphaTensor, GNoME/materials, finance)
on `verifier cleanliness · contamination · adversariality · perishability · causal
identifiability`; finance as worst case. Each classified search-within-space vs. jump.

## 8.8 Finance case study (replaces Einstein)
Narrate the actual historical discovery of a real anomaly (post-earnings drift / low-vol /
momentum) — the human noticing what the reigning framework didn't predict — and argue no
current system performs that step. Keep Einstein as a one-line aside at most.

---

# E12 — "The jump": empirically probing the abduction ceiling

Anchors §8.4–8.5. Honest scope: you cannot prove a universal negative; the goal is a
well-powered **null** on a task where the jump is demonstrably possible (positive control
clears it) and contamination is controlled. Frame as strong supporting evidence, not proof.

## Operational definition of "a jump"
In a world whose true driver `V` is NOT in the supplied vocabulary, and given an affordance to
propose/request arbitrary new quantities, a **jump** = the agent proposes `V` (or a sufficient
statistic of it) without hints, at a rate above the base rate of proposing from its generic
menu. **Can't jump** = jump rate indistinguishable from that base rate across many worlds,
*when a positive control shows the jump is achievable*.

## E12a — Withhold-the-primitive power curve (in-repo, mechanical, high-N)
Re-run E1 with the true predictor absent from the given features (`feat_a,b,d` = noise; the
`feat_c` signal exists in the world but is not exposed). Recovery → null at every ρ. Then sweep
compute / iterations / (simulated) agents / context length and show none move it. Establishes
the **vocabulary-boundary**: recovery is gated by whether the primitive was supplied, not by
search effort. Caveat to state: a mechanical searcher fails identically — this proves the
vocabulary thesis, not yet an LLM-specific failure.

## E12b — The jump gap (the central experiment; ~part of the 20 LLM runs)
Two conditions over N independent hidden mechanisms:
- **Search:** correct primitive in the vocabulary → works (power curve).
- **Jump-required:** correct primitive withheld, but the LLM may **propose a new feature/data
  source in words**; a resolver scores whether the proposal names the true driver.
Compare LLM-propose vs. (i) base-rate null (generic-menu hit rate), (ii) mechanical searchers
that cannot propose. **Signature of no-jump: LLM-propose ≈ mechanical-stuck ≈ base rate** — the
proposal affordance adds nothing beyond search.
Controls (mandatory): human/oracle **positive control** clearing the jump condition;
base-rate null; many worlds × seeds; **affordance parity** (the LLM must actually be able to
propose new variables/pull new data, or you've tested the harness).

## E12c — Cutoff dissociation (LLM-specific, contamination-controlled)
Real anomalies first documented at known date `T`. Give model vintages cut off *before* `T`
only pre-`T` data and ask them to name the driver; compare vintages cut off *after* `T`. If
post-`T` models "succeed" only by having read it and pre-`T` models fail, the dissociation is
direct evidence of **retrieval, not abduction**. Partly outside the repo (needs multiple model
vintages + a small curated anomaly set).

## E12d — Novelty audit (small, supporting)
For hypotheses the LLM does propose, near-duplicate/embedding-search against a corpus to
quantify "new to you, not to the world" (ties to Si et al.). Shows proposals are recombinations.

## What E12 can and cannot establish
- CAN: vocabulary-boundary (E12a); that the proposal affordance doesn't beat search or base
  rate on originating out-of-space primitives (E12b); retrieval-vs-abduction dissociation
  (E12c). With a positive control, this is strong illustrative evidence for the ceiling.
- CANNOT: prove non-existence of the capability. State this plainly; the strong claim rests on
  the argument (§8.1–8.3), with E12 as hard-to-dismiss support.

## LLM budget note
E12b consumes the bulk of the ~20-run LLM budget alongside E7; E12c needs API access to older
model vintages (separate from the LATSS run budget). E12a/E12d are ~free.
