---
title: AI Valuation & Strategic Disclosure Game
emoji: 📈
colorFrom: blue
colorTo: indigo
sdk: static
pinned: false
---

# AI Valuation & Strategic Disclosure Game

This interactive game is a behavioral laboratory for a Computational Microeconomics PS2 research project.

## Research Question

When firms know how an AI evaluator scores their disclosures, can a history-aware evaluator and an auction-based capital-allocation mechanism reduce strategic disclosure while preserving informative pricing?

## Economic Environment

The game studies the following feedback loop:

Firm
→ Strategic Disclosure
→ AI Valuation
→ Investor Bid
→ Capital Allocation
→ Firm Performance
→ AI Historical Learning

The key research problem is that an AI evaluator may learn from outcomes that were partly caused by its own previous capital-allocation decisions.

## Roles

### Investor

The investor observes:

- AI valuation
- Private signal
- Competing bid

The investor then submits a bid.

The game uses a simplified first-price allocation rule:

- the highest bid wins;
- the winner pays their own bid.

### Firm

The firm observes its underlying quality and chooses strategic manipulation of its disclosure.

Higher manipulation may increase the AI valuation, but manipulation has a quadratic cost.

## AI Evaluators

The experiment compares three evaluator designs.

### 1. No Memory

The AI evaluates the current disclosure without using previous outcomes.

### 2. Naive History

The AI uses previous firm performance when updating its valuation.

However, it does not remove the effect of previous capital allocation.

This creates the central feedback problem:

AI valuation
→ capital
→ firm performance
→ AI learning

### 3. Capital-Purged History

The AI attempts to remove the estimated effect of previous capital before learning from historical performance.

The adjustment is:

performance − ρ × capital

where ρ is the assumed productivity of capital.

## Main Outcomes

The game records:

- true firm quality
- strategic manipulation
- disclosure
- AI valuation
- private signal
- investor bid
- competing bid
- allocation
- payment
- capital
- firm performance
- utility
- manipulation cost

These outcomes correspond to the computational experiment described in the PS2 proposal.

## Research Predictions

### H1 — Strategic Disclosure

Firms have an incentive to adjust disclosure when they know the AI evaluation rule.

### H2 — Feedback Bias

Naive historical learning can reinforce strategic disclosure because the AI may interpret capital-induced performance as evidence that its earlier valuation was correct.

### H3 — Capital-Purged Learning

Removing the estimated capital-induced component of historical performance should reduce feedback-driven evaluator bias.

### H4 — Behavioral Departure

Human investors may not behave exactly according to the theoretical benchmark and may place excessive weight on AI-generated valuations.

## Important Simplifications

This is a controlled experimental environment rather than a full model of real IPO markets.

The game intentionally simplifies:

- the number of investors
- the number of shares
- the auction
- firm production
- AI learning
- investor information

The purpose is to isolate the strategic interaction between disclosure, AI valuation, capital allocation, and historical learning.

## Data

At the end of an experiment, the player can export a CSV file containing the observed game history.

The exported data can be used to compare:

- theoretical predictions
- computational simulations
- human behavioral decisions

## Disclaimer

This is an academic research experiment.

It is not investment advice and should not be interpreted as a recommendation to buy, sell, or hold any financial asset.