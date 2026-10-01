# Overfitting is unpreventable and all data is in-sample: the quant must impose a priori simplicity

*Draft v0.1. Sections marked [PENDING] await the parameter sweeps; every number stated
elsewhere is measured and reproducible from the accompanying code.*

## Abstract

Large-language-model-driven program search can propose and refine trading strategies
automatically. Applied to a universe of correlated equities with technical inputs, such
a search does not produce a durable edge; it overfits, and the apparent skill does not
persist. This paper reframes the question. Rather than asking whether the loop discovers
alpha, it asks whether the loop is a sound *instrument*: given an input that genuinely
predicts, does the search recover it, and can that recovery be certified without a
hold-out? The study injects synthetic signals of controlled strength into an otherwise
noise-only feature set and evaluates the search entirely in sample against three
capacity-based skill bars — a Vapnik–Chervonenkis worst-case bound, an empirical
Rademacher bar, and the Deflated Sharpe Ratio. Three results follow. First, the widely
used shift-the-signal permutation test certifies pure noise and must be discarded.
Second, the cross-validation scheme is itself load-bearing: permissive resampling
inflates apparent skill and simultaneously lowers the noise bar, so the same strategy is
"significant" under one scheme and indistinguishable from noise under a purged,
chronological scheme. Third, an unconstrained code-writing search has no finite
Vapnik–Chervonenkis bar, and an empirical bar it can exceed by luck given enough search.
Because overfitting cannot be prevented and, under such a search, no partition of the
data is truly out of sample, the only remaining defense is to restrict the strategy
class a priori. Simplicity is not a preference; it is a requirement for certifiability.

## 1. Introduction

A search procedure that can express arbitrary strategies and is optimized against a
finite sample will fit that sample, including its noise. When the searcher is a large
language model emitting arbitrary code, the expressive capacity is effectively unbounded,
and the usual defense — reserving a hold-out period — fails in principle: a sufficiently
expressive, sufficiently persistent search will fit the hold-out as well, either directly
or through the analyst's iteration across "held-out" evaluations. The practical
consequence is that all data in the analyst's possession is, for certification purposes,
in sample.

This motivates a shift from out-of-sample testing to in-sample capacity control. A
strategy is credited with skill only when its in-sample performance exceeds what its own
strategy class can reach on data with the signal destroyed. The central object is
therefore the *bar*: the highest score luck can produce across the class. The
contribution of this paper is to make that object operational for an LLM-driven search,
to show that common alternatives are invalid, and to demonstrate that the bar can only be
made meaningful by constraining the class.

## 2. The search loop

LATSS (LLM-Assisted Trading Strategy Search) maintains a population of candidate
strategies. Each candidate is a scoring function over a fixed feature set; a
cross-sectional selector holds, each period, the highest-scoring names in a fixed
universe, equally weighted. Candidate parameters are fit by differential evolution and
scored by cross-validated active return against an equal-weight benchmark. A language
model proposes and mutates candidates from the population's history. The loop is the
object under study; the universe (seven large-capitalization equities) and the input
features are interchangeable test-beds.

## 3. Methodology

### 3.1 Synthetic validation

The selector is given four opaquely named per-name features.
In the negative control all four are persistent noise. In the positive control one
hidden feature carries, for a single target name, that name's forward excess return over
the universe, standardized and corrupted by additive noise of controlled magnitude; the
remaining features and names are noise. The signal-to-noise ratio is a tunable parameter.
The search is not told which feature, if any, predicts.



### 3.3 Three capacity bars

- **Vapnik–Chervonenkis bar (analytical, worst case).** For a class of
  Vapnik–Chervonenkis dimension *h* over *m* samples spanning *Y* years, the highest
  Sharpe ratio luck can produce is bounded by a term of order the square root of
  *2 h log(e m / h) / Y*. For a linear combination of four features the dimension is
  approximately five and the bound is approximately 2.5; for an unbounded code-writing
  class the dimension is infinite and no finite bound exists.
- **Empirical Rademacher bar (operative).** The returns are sign-flipped to destroy any
  relationship with the features; the strategy class is refit to the scrambled returns;
  the best-in-class cross-validated score is recorded. Repeated, the distribution of
  best-noise fits gives the bar (its mean and ninety-fifth percentile). This bar is at
  most the Vapnik–Chervonenkis bar and measures overfitting on the data at hand.
- **Deflated Sharpe Ratio (reported for completeness).** The observed Sharpe ratio is
  deflated for the number of trials, skewness, kurtosis, and sample length. Because it
  depends on a trial count that is ill-defined for exhaustive automated search, it is
  reported with that caveat; capacity, not trial count, is the appropriate invariant.

A strategy is credited with skill only when its cross-validated score exceeds the
empirical Rademacher bar with headroom.

### 3.4 Cross-validation

Two schemes are compared. A permissive scheme assigns whole calendar quarters at random
to training and test folds; adjacent quarters overlap and the split is not chronological.
A purged scheme uses contiguous chronological folds, purges training observations that
overlap the test window, and embargoes a gap larger than the longest feature lookback.

## 4. Results
