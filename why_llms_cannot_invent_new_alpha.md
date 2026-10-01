# Einstein Versus Newton: Why LLMs Cannot Invent New Alpha

Large language models can generate trading strategies no human has written before. That is not
in dispute, and this essay does not dispute it. The claim here is narrower and sharper, and it
turns entirely on what *invent* means.

By *invent new alpha* I do not mean "produce a factor formula nobody has published" — a search
system does that easily. I mean **originate a genuinely new hypothesis about where returns
come from: a variable, a mechanism, or a relationship that lies outside the space of
possibilities the system was given.** Under that definition the answer is no. An LLM can
produce novelty *within* a supplied hypothesis space; it cannot make the abductive jump that
creates a new one. Everything below argues that distinction, and shows why alpha is the case
where it bites hard.

So this is not an argument that LLMs cannot produce novelty. They demonstrably can. It is an
argument about *where the novelty comes from*.

## Search versus abduction

There are two fundamentally different operations.

**Search:** Here is a space of possible solutions. Try things.

**Abduction:** Something about reality does not make sense. What new concept or hypothesis
should exist that would make sense of it?

The first is a search problem, and an LLM coupled to an evaluator may be exceptional at it. The
second is the scientific leap. The difference is not that search is easy — searching a large
enough space is extraordinarily hard. The difference is that search assumes the space worth
searching has already been defined. Abduction is what happens when you do not yet know what
space you should be searching in the first place.

This is Tom Zahavy's argument in *LLMs Can't Jump*: current models are strong at induction
(extracting patterns from data) and increasingly strong at deduction (working out consequences
of premises), but struggle with the abductive step in genuine invention — generating the new
premise from which a new explanation follows. It is a position paper, a structural argument
that the mechanism for the jump is missing, rather than an impossibility theorem. But it is the
right frame, because the gap it names is exactly the one that has never been demonstrated to
close: no LLM system has been shown to originate a hypothesis outside the space it was handed.

## FunSearch does not refute this — it proves the distinction

The strongest apparent counterexample is FunSearch. DeepMind used a language model to generate
programs for open mathematical problems, and the system found previously unknown constructions
and improved known results — *Nature* reports "hitherto unknown" constructions and new bounds
for the cap-set problem. So the lazy claim that LLMs merely regurgitate their training data is
false. Coupled to a good evaluator, they produce genuinely new results.

But look at what FunSearch is given. The human supplies the problem. The human supplies the
evaluation function. The human supplies the representation in which candidate solutions are
expressed. Often the human supplies a program skeleton, leaving one component for the model to
evolve. The system then generates on the order of a million candidate programs and keeps the
ones that score better. That is not a criticism — it is why FunSearch works. The problem is
already formulated, and the model's generative capacity is brought to bear on the *search*.

That is the whole point. FunSearch shows an LLM can *participate in discovery*. It does not
show that the LLM can decide *what should be discovered*. It did not conclude that an entirely
different mathematical representation was needed and invent it; it searched, extraordinarily
well, inside a space a human defined. FunSearch is not evidence against the thesis. It is the
cleanest available illustration of it.

## Einstein did not search Newtonian physics harder


Nobody handed Einstein a defined problem to search. He did not find relativity by trying more
variations of Newtonian physics. He did something different: he saw that the existing framework
itself was wrong, and proposed a new premise — the equivalence principle — that changed what a
valid explanation could even look like. That move created a new search space. Once it existed,
much of the physics that followed was ordinary search; but someone first had to make the jump.

That is the operation an LLM has not been shown to perform. An LLM stands on the shoulders of
every giant at once — it has read everything. But standing on shoulders is only how you see
further along a view that already exists. A genuinely new hypothesis is a shoulder no one has
built yet: there is nothing there to stand on. "New" *within* a hypothesis space is not a new
hypothesis.

## Why alpha is where this bites

The usual architecture of an AI alpha system is straightforward:

> LLM → generate candidate → backtest → score → retain → mutate → repeat.

Give it a vocabulary of indicators and it searches combinations. Give it raw price and volume
and a fixed operator language and it searches factor formulas. Give it a large data lake and it
searches a larger space still. [LATSS](https://vincentmayeski.substack.com/p/using-ai-in-trading-strategy-development)
is one instance of this pattern, and it is genuinely useful.

But notice everything decided before the search begins: what data is relevant, what the
prediction target is, what horizon matters, what counts as an observation, which
transformations are available, what a candidate factor looks like, what the evaluator is, and
what tests define success. The machine searches inside that world. A factor-mining agent handed
RSI, volume, volatility, and momentum with a fixed operator language can find an expression
nobody has ever written — and that expression is still a construction from the vocabulary it
was given. It has not discovered a new economic primitive.

Now suppose the real source of an anomaly is a phenomenon nobody thought was relevant: a
variable that is not in the factor vocabulary, not in the operator language, not in the
database, that nobody specified should be measured. Searching the given space harder will never
surface it, because the missing ingredient is outside the space. More compute does not solve
this. More agents do not. More sophisticated tree search does not. A larger context window
certainly does not. The system would have to generate a reason to look somewhere nobody told it
to look — the jump — and that is the thing it cannot do.

## But can't it just propose the hypotheses?

The obvious response is to move the search up a level: instead of searching factor formulas
inside a fixed vocabulary, have the model propose the hypotheses themselves — new variables,
new mechanisms, new datasets. And it can. Ask an LLM for candidate sources of edge and it
generates them fluently: filing sentiment, supplier-network effects, options positioning, and
so on. This is genuinely useful, and probably the most promising near-term use of LLMs in
research.

But look at what those proposals are. Each is an idea the model read somewhere — a
recombination of hypotheses people have already written down. Moving the search from formulas
to ideas enlarges the vocabulary; it does not escape it. The proposed "new variable" is new to
you, not new to the world. The abductive jump is a hypothesis that is not in that space at all:
the thing no one — including everyone whose writing trained the model — has yet thought to look
for. Generating hypotheses is still search. The jump is inventing one the space did not
contain.

## Alpha is also unusually hostile to search

Mathematics gives FunSearch a clean evaluator: a construction satisfies the constraints or it
does not; an algorithm can be benchmarked; a proof can be verified; the objective is defined in
advance. Finance offers none of this cleanly. When an agent finds a factor that predicts
returns, a successful backtest does not tell you what caused the relationship — genuine
mechanism, accidental correlation, hidden exposure to a known risk, a regime artifact, data
leakage, overfitting, a transaction-cost illusion, or an edge that vanishes once enough capital
finds it. The evaluator never tells you what the missing hypothesis should have been; it only
tells you whether a candidate survived. And alpha is adversarial and perishable: a mathematical
construction does not disappear because someone else learns it, but an economic edge does.

## Novelty is not discovery

It helps to separate kinds of novelty, because they are not the same achievement:

- **Syntactic** — a formula nobody has written. Obviously within reach.
- **Solution** — a previously unknown construction for a defined problem. Demonstrated by FunSearch.
- **Hypothesis / mechanism** — a new explanation for an unexplained phenomenon. Not demonstrated.
- **Economic discovery** — a new, durable, uncrowded source of returns. No convincing demonstration.

Blind expert reviewers even rate LLM research ideas as more novel than their own (Si et al.,
2024) — but that measures how novel an idea *looks*, not whether it turns out to be real. That
gap is where alpha lives.

## The current ceiling

The ceiling is not that LLMs can't search — search is their strength. It is the line between
*searching* a hypothesis space and *creating* one, and today's alpha agents live entirely on
the near side. Crossing it would mean a system that, given raw market data and no predefined
vocabulary, repeatedly finds durable, economically intelligible sources of return no one told
it to look for. None has.

So the summary is not a hedge. An LLM-driven framework recombines a human-supplied vocabulary
into strategies, fits them, and certifies the survivors — new expressions inside the space it
was given. It does not originate the new hypothesis that would enlarge that space: the
abductive jump, the Einstein move, which is exactly what genuinely new alpha requires. Search
can find the needle; it cannot decide the haystack is in the wrong field.

---

**References.** Romera-Paredes et al., *Mathematical discoveries from program search with large
language models* (FunSearch), *Nature*, 2023. Tom Zahavy, *LLMs Can't Jump* (position paper),
DeepMind, 2026 —
[tomzahavy.com/projects/llms-cant-jump](https://www.tomzahavy.com/projects/llms-cant-jump).
Si, Yang & Hashimoto, *Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with
100+ NLP Researchers*, 2024 ([arXiv:2409.04109](https://arxiv.org/abs/2409.04109)). Balestriero,
Pesenti & LeCun, *Learning in High Dimension Always Amounts to Extrapolation*, 2021
([arXiv:2110.09485](https://arxiv.org/abs/2110.09485)). Yann LeCun on world models
([MIT Technology Review](https://www.technologyreview.com/2026/01/22/1131661/yann-lecuns-new-venture-ami-labs/)).
