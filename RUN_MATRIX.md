# LATSS Exp 1 & 2 — run matrix (R=3, purged CV, Rademacher bar, n_scramble=50, iterations=12)

Each run: `run_mag7.py --cv-method purged --iterations 12 --fit-budget 150`, LLM via
subagent handoff, one servicer agent per dir. 4 parallel. α-grid {0.2,0.4,0.6,0.8}.
α* per prompt = smallest α certified (CV > Rademacher q95) in ≥2/3 seeds.

## Status legend: [ ] pending  [~] running  [x] done

### Experiment 1 — negative control (synth control), 6 runs
- [~] e1_ctrl_free_s0   (--synth control --seed 0)
- [~] e1_ctrl_free_s1   (--synth control --seed 1)
- [ ] e1_ctrl_free_s2   (--synth control --seed 2)
- [~] e1_ctrl_lin_s0    (--synth control --constrained --seed 0)
- [~] e1_ctrl_lin_s1    (--synth control --constrained --seed 1)
- [ ] e1_ctrl_lin_s2    (--synth control --constrained --seed 2)

### Experiment 2 — positive control (synth predictor), free prompt, 12 runs
- [ ] e2_free_a02_s0/1/2   (--synth predictor --synth-alpha 0.2 --seed 0/1/2)
- [ ] e2_free_a04_s0/1/2   (--synth-alpha 0.4)
- [ ] e2_free_a06_s0/1/2   (--synth-alpha 0.6)
- [ ] e2_free_a08_s0/1/2   (--synth-alpha 0.8)

### Experiment 2 — positive control, linear prompt (--constrained), 12 runs
- [ ] e2_lin_a02_s0/1/2    (--synth predictor --constrained --synth-alpha 0.2 --seed 0/1/2)
- [ ] e2_lin_a04_s0/1/2    (--synth-alpha 0.4)
- [ ] e2_lin_a06_s0/1/2    (--synth-alpha 0.6)
- [ ] e2_lin_a08_s0/1/2    (--synth-alpha 0.8)

## Batches of 4
1 [RUNNING]: e1_ctrl_free_s0, e1_ctrl_free_s1, e1_ctrl_lin_s0, e1_ctrl_lin_s1
2: e1_ctrl_free_s2, e1_ctrl_lin_s2, e2_free_a02_s0, e2_free_a02_s1
3: e2_free_a02_s2, e2_free_a04_s0, e2_free_a04_s1, e2_free_a04_s2
4: e2_free_a06_s0, e2_free_a06_s1, e2_free_a06_s2, e2_free_a08_s0
5: e2_free_a08_s1, e2_free_a08_s2, e2_lin_a02_s0, e2_lin_a02_s1
6: e2_lin_a02_s2, e2_lin_a04_s0, e2_lin_a04_s1, e2_lin_a04_s2
7: e2_lin_a06_s0, e2_lin_a06_s1, e2_lin_a06_s2, e2_lin_a08_s0
8: e2_lin_a08_s1, e2_lin_a08_s2

## DEFINITIVE RESULTS (bar n=30/budget60, OMP=1, strict batches): dir | CV | radem_q95 | VC | clears
### Exp 1 — negative control (noise) [BATCH 1 DONE]
- e1_ctrl_free_s0 | CV +0.500 | radem +0.495 | VC inf  | clears TRUE  <== nonlinear sneak-through on noise
- e1_ctrl_free_s1 | CV +0.405 | radem +0.668 | VC inf  | clears False
- e1_ctrl_lin_s0  | CV +0.010 | radem +0.692 | VC +2.52 | clears False
- e1_ctrl_lin_s1  | CV -0.051 | radem +0.823 | VC +2.52 | clears False
- e1_ctrl_free_s2 | batch2 running
- e1_ctrl_lin_s2  | batch2 running
### Exp 2 — positive control (predictor), α sweep
- e2_free_a02_s0/s1 | batch2 running

### Exp 2 α=0.2 [BATCH 2]  (free-class recovery threshold probe)
- e2_free_a02_s0 | CV +0.289 | radem +0.637 | clears False (feat_c NOT recovered; loop overfit noise in a/b)
- e2_free_a02_s1 | CV +0.367 | radem +0.602 | clears False
- e1_ctrl_lin_s2 | CV -0.185 | radem +0.584 | VC +2.52 | clears False
- e1_ctrl_free_s2| noise ceiling -0.122 (finalizing) -> won't clear
=> α=0.2 below free-class recovery threshold.

### Exp 2 FREE α-sweep (CV | radem q95 | clears):
- α=0.2: s0 +0.289/0.637 F | s1 +0.367/0.602 F | s2 +0.059/0.661 F  -> not recovered
- α=0.4: s0 +0.309/0.681 F | s1 +0.382/0.535 F | s2 +0.389/0.700 F  -> not recovered
- α=0.6: s1 +0.404/0.554 F | s0 best+0.338 fin | s2 best+0.186 fin    -> not recovered (feat_c only a weak gate)
- α=0.8: s0 RECOVERED feat_c (champ +0.547) finalizing | s1,s2 = batch5
=> FREE-class recovery threshold ~0.8 (feat_c becomes dominant at 0.8). Whether +0.547 CLEARS bar: pending.
## NOTE: signal base=1.0 in run_mag7 (not synth.py's 4.0) -> recovery needs high alpha. May need alpha=0.9/0.98.

## DONE so far: B1(6 ctrl), B2(4), B3(4), most of B4. B5 RUNNING (free a08_s1/s2, lin a02_s0/s1).
## OLD status: B1,B2 DONE. B3 done, B4 done. Then:
## B4 free a06_s0/1/2,a08_s0 | B5 free a08_s1/2, lin a02_s0/1 | B6 lin a02_s2,a04_s0/1/2
## B7 lin a06_s0/1/2,a08_s0 | B8 lin a08_s1/2
## USE fast-wait servicer (60s cap, n_ge 30) — reliable+fast (~30-50k tok). Slow-poll variant = 220k tok, avoid.
## Settings locked: iterations=12, bar n_scramble=30, bar fit_budget=60, OMP_NUM_THREADS=1, strict 4-batches.

## ===== PIVOT: cross-sectional predictor SHARPE SWEEP (supersedes weak single-name Exp2) =====
synth.py predictor is now CROSS-SECTIONAL (all names get feat_c = rho*z + sqrt(1-rho^2)*noise,
z = per-name standardized fwd excess return). rho -> active Sharpe ceiling: 0.15~0.9, 0.35~1.9, 0.55~2.5, 0.80~3.1.
Exp1 control (6 runs) STANDS. Exp2 = Sharpe sweep, 24 runs: rho{0.15,0.35,0.55,0.80} x {free,lin} x seed{0,1,2}.
Batches: A free r15 s0/1/2 + r35 s0 [RUNNING] | B free r35 s1/2 + r55 s0/1 | C free r55 s2 + r80 s0/1/2
  | D lin r15 s0/1/2 + r35 s0 | E lin r35 s1/2 + r55 s0/1 | F lin r55 s2 + r80 s0/1/2
Settings: iterations12, bar n_scramble30/budget60, OMP=1, fast-wait servicers.

## DENSE LOW-END free sweep (map Rademacher-bar crossing): rho {0.1,0.2,0.25,0.3} x seed{0,1,2} = 12 runs
## calibration: rho 0.1~Sh0.0, 0.2~0.66, 0.25~0.95, 0.3~1.23. RUNNING: r20 s0/1/2, r25 s0.
## QUEUE: r10 s0/1/2, r25 s1/2, r30 s0/1/2. Then still owe: free r80 x3, ALL linear (r15/35/55/80 x3).
