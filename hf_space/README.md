---
title: AI Valuation & Strategic Disclosure Game
emoji: 📈
colorFrom: blue
colorTo: indigo
sdk: static
pinned: false
---

# AI Valuation & Strategic Disclosure — behavioral companion to Team FP3

**COMSCI/ECON 206 Computational Microeconomics · Autumn 2026 · Team FP3**
Feiyu Li · Xuantong Fu · Instructor: Prof. Luyao Zhang
Paper and code: https://github.com/dku-comsci-econ206-Autumn2026/ps2-fp3

## ⚠️ Evidence status

**This Space is an exploratory classroom instrument, not an experiment.**
Completed sample size and matched treatment outputs are not established. Nothing observed
here is used to support a population-level claim about investor behavior, and no result
from this Space appears as evidence in the paper's Results section. It exists to make one
modelling assumption *inspectable*, and to let a reader feel the decision the model
attributes to investors.

## The question the paper asks

> **When may an AI valuation rule safely revise itself from outcomes it helped cause —
> and does the allocation mechanism decide whether that condition can hold?**

## The assumption this Space probes

The paper's equilibrium rests on one behavioral assumption: that investors **strip the
predictable inflation out of the public AI signal** before bidding. Formally, an investor
forms

```
E[θ | s] = (invert the published rule) − (the average manipulation they expect)
```

and then precision-weights that against their own private signal. If real players instead
anchor on the headline score — *algorithm appreciation*, Logg, Minson & Moore (2019) —
then the model's claim that "no investor is fooled on average" is too generous, and the
welfare cost of strategic disclosure is larger than the paper reports.

The competing predictions are sharp:

| | Prediction |
|---|---|
| **Equilibrium benchmark** | weight on the public signal falls as the evaluator's disclosure sensitivity rises |
| **Algorithm appreciation / anchoring** | weight stays flat, or rises with the signal's confidence framing |

What would have to be true to settle it: a pre-registered design, `n ≥ 200`, audit status
disclosed as the treatment, and the weight on the public signal as the outcome. That study
is item three of the paper's Future Research Roadmap. It has not been run.

## The feedback loop you are inside

```
Firm → strategic disclosure → AI valuation → investor bid
     → capital allocation → firm performance → AI retrains on that performance
                                                        ↑
                        part of the AI's evidence is its own earlier decision
```

In the paper's simulation, an evaluator that retrains naively on this loop roughly
**doubles** strategic disclosure (mean manipulation 0.406 → 0.824 under uniform-price
allocation, 20 seeds). The proposed fix is not accountability in general but
**identification**: the rule may revise itself only while its own capital footprint is
statistically identifiable (first-stage `F ≥ 10`), and is frozen otherwise. Gating on that
condition cuts worst-case bias from 2.563 to 0.275.

## Roles

**Investor.** Observes the AI valuation, a private signal and a competing bid, then bids.
**Firm.** Observes its own quality and chooses how much to inflate its disclosure, at a
quadratic cost.

## AI evaluator modes

1. **No memory** — the committed rule; scores the current disclosure only.
2. **Naive history** — learns from past performance without removing the effect of the
   capital it previously allocated. This is the failure mode.
3. **Capital-purged** — removes the estimated capital-induced component before learning.
4. **Audited freeze** *(the paper's proposal)* — capital-purged, but permitted to publish
   a revision only when its first stage is strong enough for that correction to be
   identified; otherwise frozen at the last audited rule, resuming automatically once
   identification returns.

## Scope and boundary

- All parameters are the paper's synthetic calibration. **No real issuer data.**
- The allocation here is a simplification of the paper's uniform-price auction, in which
  160 units of demand chase a 100-share offering and low bidders receive **zero**.
- Real multi-unit bidders shade demand; this interface does not model that.
- The game's single-winner rule is a teaching simplification and is *not* the mechanism
  used for any number reported in the paper.

## Data

The player can export a CSV of the session history (quality, manipulation, disclosure,
AI valuation, private signal, bids, allocation, payment, capital, performance, utility,
manipulation cost) to compare against the simulation. Treat any such comparison as
illustrative.

## Disclaimer

Academic coursework. Not investment advice, and not a recommendation to buy, sell or hold
any financial asset. MIT licence. AI assistance is disclosed in Appendix A.1 of the paper.
