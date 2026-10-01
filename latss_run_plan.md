# Run plan — Experiments 1 and 2

Concrete steps to fill the grid for both experiments. Driver: `run_mag7.py`. The LLM
search uses the subagent file-handoff (`LLM_PROVIDER=subagent`), which needs one Claude
Code session servicing `<out-dir>/mutation_request.json` per run directory.

## Grid

- **Prompt regime:** `--constrained` (linear) vs default (nonlinear / free).
- **Cross-validation:** `--cv-method purged` vs `--cv-method random`.
- **Bars:** both computed automatically in every run (VC from the class, Rademacher
  empirical). VC is finite (h≈5) under `--constrained`, infinite otherwise.

Experiment 1 = `--synth control` over the 2×2 (prompt × CV) = **4 configs**.
Experiment 2 = `--synth predictor` over the 2×2, swept over α = **4 configs × α grid**.

## 0. Prep (before any run)

1. **Rademacher stability.** `finalize` calls `rademacher_bar(..., n_scramble=15)`. Raise
   to `n_scramble=200` and thread a fixed RNG seed so the q95 bar is stable near the
   recovery threshold (at 15 the clears/buried verdict is within sampling noise).
2. **Repeats.** The subagent search is stochastic; champions vary run to run. Run each
   cell **R = 5** times with `--seed 0..4` and report the distribution, not one run.
3. **Isolation.** One `--out-dir` per concurrent run (e.g. `runs_e1_free_purged_s0`),
   each with its own servicing session, so the handoff files do not collide.
4. **Search depth.** Use `--iterations 12 --splits 60 --fit-budget 150` for every cell
   (bounded cost; enough mutations to leave the seeds). Hold these fixed across the grid.

## 1. Experiment 1 — negative control (4 configs × R)

For each (prompt, CV, seed):

```
LLM_PROVIDER=subagent SUBAGENT_DIR=$PWD/<dir> \
  .venv/bin/python -u run_mag7.py --synth control [--constrained] \
  --cv-method {purged|random} --iterations 12 --splits 60 --fit-budget 150 \
  --seed <s> --out-dir $PWD/<dir>
```

Record per run: champion code, CV active Sharpe, shift-null p, VC bar, Rademacher
mean/q95, `clears_rademacher`.

## 2. Experiment 2 — positive control, α-sweep (4 configs × α × R)

α grid: coarse **{0.1, 0.3, 0.5, 0.7, 0.9}**, then bisect once in the interval where the
verdict flips to locate α\* to ±0.05.

For each (prompt, CV, α, seed):

```
LLM_PROVIDER=subagent SUBAGENT_DIR=$PWD/<dir> \
  .venv/bin/python -u run_mag7.py --synth predictor --synth-alpha <α> [--constrained] \
  --cv-method {purged|random} --iterations 12 --splits 60 --fit-budget 150 \
  --seed <s> --out-dir $PWD/<dir>
```

### Criteria (per cell, per α)

- **Recovered:** the champion is driven by `feat_c` (feat_c is the dominant term / the
  held name is the target most bars).
- **Certified:** CV active Sharpe > Rademacher q95. (Under `--constrained` also compare to
  the finite VC bar ≈ 2.5; under the free prompt VC is infinite.)
- **α\*** for the cell = smallest α that is both recovered and certified in ≥ 3 of 5 seeds.

## 3. Outputs

- Experiment 1 table: 4 rows (prompt × CV), columns = CV Sharpe, shift-null p, VC bar,
  Rademacher q95, clears — aggregated over the 5 seeds.
- Experiment 2 table: 4 rows (prompt × CV), column = α\* (and the per-α recovered/certified
  counts behind it).
- Every individual run's JSON is saved under its `--out-dir`.

## Run count

Experiment 1: 4 × 5 = **20 runs**. Experiment 2: 4 × 5 α-levels × 5 = **100 runs**
(plus ~4 × 5 bisection runs). Total ≈ **140 search runs**, each 12 iterations.
