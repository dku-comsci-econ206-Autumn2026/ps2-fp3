# PS2-FP3: Strategic Disclosure, AI Valuation, and Capital Allocation

## Project overview

This repository contains the computational and reproducibility artifacts for our COMSCI/ECON 206 PS2 project.

### Project title

**Learning from Its Own Footprint: Strategic Disclosure, Capital Feedback, and the Design of AI Valuation Rules in IPO Allocation**

### Research question

> **When firms know how an AI evaluator scores their disclosures, can a history-aware evaluator and an auction-based allocation mechanism reduce strategic disclosure while preserving informative pricing?**

The project studies a sequential financial environment in which:

1. A firm has private fundamental quality.
2. The firm chooses how much to disclose and may strategically manipulate its disclosure.
3. An AI evaluator converts disclosure into a public valuation signal.
4. Investors combine the public AI signal with private information and submit bids.
5. An allocation mechanism determines price and capital received.
6. Capital affects realized firm performance.
7. A history-aware evaluator may learn from those realized outcomes.

The central problem is a feedback loop:

**Disclosure → AI valuation → Capital allocation → Firm performance → AI's future calibration**

If the evaluator's own valuation affects the capital received by firms, then later performance can partly reflect the evaluator's previous decisions. The project therefore asks whether evaluator memory and the capital-allocation mechanism should be designed jointly.

---

# Research design

The project combines three perspectives.

## 1. Game theory

The issuer strategically chooses disclosure.

For issuer `t`:

`d_t = theta_t + m_t`

where:

- `theta_t` = fundamental firm quality
- `m_t` = strategic manipulation
- `d_t` = disclosed quality

Manipulation has quadratic cost:

`c(m_t) = m_t^2 / (2 gamma)`

The evaluator produces a public signal:

`s_t = (1-beta) mu_0 + beta [a + b(d_t + eta_t)]`

where `b` is the evaluator's learned sensitivity to disclosure.

The model uses incomplete information and sequential decisions, with **Perfect Bayesian Equilibrium (PBE)** as the game-theoretic solution concept.

The firm's strategic best response is increasing in the perceived sensitivity of the evaluator. Therefore, changing the evaluator's rule can change the firm's incentive to manipulate disclosure.

---

## 2. Social choice

The project does not treat AI prediction accuracy as the only objective.

The main stakeholders are:

- issuing firms;
- institutional investors;
- retail investors;
- exchanges and regulators;
- future firms and investors affected by the evaluator's history.

The simulation therefore tracks multiple outcomes:

- informative pricing;
- allocation efficiency;
- strategic disclosure/manipulation;
- manipulation cost;
- retail access;
- evaluator feedback bias.

These objectives can conflict. For example, increasing institutional allocation may change retail access, while making an evaluator transparent can improve accountability but also make its scoring rule easier for firms to optimize against.

---

## 3. Mechanism design

The project compares two capital-allocation mechanisms.

### M1: Uniform-price auction

Investors submit bids.

Bids are ranked and accepted until the available shares are allocated. Winners pay the lowest accepted bid.

The implementation uses:

- 100 shares per issuance;
- 50 investors;
- 15 institutional investors;
- 35 retail investors.

### M2: Stylized bookbuilding

The implementation uses a simplified bookbuilding mechanism with:

- 85% of shares allocated to institutional investors;
- 15% allocated to retail investors;
- an 8% pricing discount;
- an allocation shock used to generate variation in proceeds.

This is a stylized computational representation rather than a complete model of real-world IPO bookbuilding. Real bookbuilding includes additional certification, relationship, and underwriter effects that are outside the current model.

---

# Evaluator treatments

The computational experiment compares three evaluator designs.

| Evaluator | Description |
|---|---|
| `no_memory` | Fixed-rule benchmark using the true disclosure sensitivity |
| `naive_history` | Learns disclosure sensitivity directly from realized outcomes |
| `capital_purged` | Attempts to remove the capital footprint using allocation variation as an instrument |

The key comparison is whether history-aware learning accidentally interprets performance caused by previous capital allocation as evidence about disclosure quality.

The `capital_purged` treatment therefore tries to separate:

**true disclosure information**

from

**performance caused by capital allocation.**

A first-stage strength diagnostic is also recorded.

---

# Computational experiment

The canonical experiment uses:

- **200 synthetic issuers**
- **10 cohorts**
- **20 issuers per cohort**
- **2 burn-in cohorts**
- **100 shares per issuance**
- **15 institutional investors**
- **35 retail investors**
- **Seeds 42, 43, 44, 45, 46**
- **3 evaluator treatments**
- **2 allocation mechanisms**

The full experiment therefore compares:

**3 evaluator treatments × 2 allocation mechanisms × 5 seeds**

Headline statistics exclude the first two cohorts as burn-in.

---

# Model parameters

The canonical implementation is contained in `src/model.py`.

Important parameters include:

| Parameter | Value |
|---|---:|
| Number of issuers | 200 |
| Cohorts | 10 |
| Issuers per cohort | 20 |
| Burn-in cohorts | 2 |
| Shares | 100 |
| gamma | 0.006 |
| sigma_theta | 1.0 |
| sigma_eta | 0.5 |
| mu_0 | 8.5 |
| beta | 0.60 |
| b_true | 1.02 |
| sigma_epsilon | 0.8 |
| Institutional investors | 15 |
| Retail investors | 35 |
| Institutional signal SD | 1.0 |
| Retail signal SD | 2.5 |
| lambda_P | 1.0 |
| kappa_0 | 0.0 |
| Bookbuilding institutional share | 0.85 |
| Bookbuilding discount | 0.08 |
| v mean | 2.2 |
| v SD | 0.4 |
| rho mean | 0.50 |
| rho SD | 0.12 |
| Uniform-price allocation shock SD | 0.08 |
| Bookbuilding allocation shock SD | 0.20 |

The last group of parameters (`v`, `rho`, and allocation-shock parameters) are explicit implementation values in the canonical Python model. They should therefore be treated as part of the computational calibration.

---

# Repository structure

```text
ps2-fp3-main/
│
├── README.md
├── LICENSE
├── requirements.txt
│
├── main.tex
├── main.pdf
├── references.bib
├── references_manual.tex
├── acmart.cls
├── ACM-Reference-Format.bst
├── acmart.dtx
├── acmart.ins
│
├── sections/
│   └── proposal.tex
│
├── appendices/
│   └── supporting.tex
│
├── figures/
│   └── ps2_teaser.tex
│
├── src/
│   ├── model.py
│   ├── evaluator.py
│   ├── auction.py
│   ├── simulation.py
│   └── run_experiment.py
│
├── notebooks/
│   └── PS2-FP3-TeamStrategicSignal.ipynb
│
└── hf_space/
    ├── index.html
    ├── style.css
    ├── script.js
    ├── README.md
    └── gitattributes
```

---

# Python files

## `src/model.py`

Defines the canonical mathematical model and parameter configuration.

It implements:

- issuer type generation;
- strategic disclosure;
- manipulation cost;
- firm best response;
- AI public signal;
- realized firm performance.

The main configuration object is `Config`.

---

## `src/evaluator.py`

Implements the three evaluator memory treatments:

```text
no_memory
naive_history
capital_purged
```

The evaluator records:

- disclosure;
- realized performance;
- capital;
- allocation shock;
- firm quality;
- capital productivity.

The `capital_purged` treatment uses the allocation shock as an instrument for capital and reports a first-stage F statistic.

---

## `src/auction.py`

Implements the two allocation mechanisms:

```text
uniform_price
bookbuilding
```

It also constructs the Bayesian benchmark investor bids by combining:

- the public AI signal;
- institutional private signals;
- retail private signals.

---

## `src/simulation.py`

Runs the sequential firm/evaluator/investor/allocation/performance process.

Each observation records:

- firm quality;
- private value;
- capital productivity;
- manipulation;
- disclosure;
- AI signal;
- price;
- capital;
- allocation shock;
- realized performance;
- manipulation cost;
- price error;
- retail allocation;
- feedback bias;
- first-stage F statistic.

---

## `src/run_experiment.py`

This is the main one-command computational experiment.

It runs:

```text
3 evaluator treatments
×
2 allocation mechanisms
×
5 random seeds
```

and writes the resulting numerical outputs to the `results/` directory.

Generated outputs include:

```text
results/main_results.csv
results/summary_results.csv
results/fresh_run_record.json
results/manipulation.png
results/price_rmse.png
results/allocation_efficiency.png
results/feedback_bias.png
results/retail_access.png
```

---

# How to run the Python experiment

From the repository root:

```bash
pip install -r requirements.txt
python src/run_experiment.py
```

The experiment should create:

```text
results/
```

with the full simulation output, summary statistics, reproducibility record, and figures.

The five canonical Python files should not be manually modified when reproducing the reported results.

---

# Main computational results

The current canonical run produces the following headline results.

## Mean strategic manipulation

| Evaluator | Uniform-price | Bookbuilding |
|---|---:|---:|
| No memory | 0.408 | 0.408 |
| Naive history | 1.367 | 0.921 |
| Capital-purged history | 1.277 | 1.002 |

History-aware evaluation produces substantially more manipulation than the no-memory benchmark in the current synthetic experiment.

---

## Price RMSE

| Evaluator | Uniform-price | Bookbuilding |
|---|---:|---:|
| No memory | 0.551 | 0.776 |
| Naive history | 30.328 | 12.302 |
| Capital-purged history | 26.478 | 14.321 |

The current simulation therefore does not show that history-aware evaluation automatically improves pricing accuracy.

---

## Feedback bias

Feedback bias is measured as the learned disclosure sensitivity relative to the true sensitivity.

| Evaluator | Uniform-price | Bookbuilding |
|---|---:|---:|
| No memory | 0.461 | 0.403 |
| Naive history | 5.344 | 2.012 |
| Capital-purged history | 4.894 | 2.527 |

The capital-purged treatment reduces the bias relative to naive history under the uniform-price mechanism, but not under bookbuilding.

Therefore, the current evidence does **not** establish that capital purging reliably solves the feedback problem.

---

## Retail allocation

| Evaluator | Uniform-price | Bookbuilding |
|---|---:|---:|
| No memory | 70% | 15% |
| Naive history | 70% | 15% |
| Capital-purged history | 70% | 15% |

The difference here comes from the allocation mechanism itself: the bookbuilding implementation reserves 15% of shares for retail investors, while the uniform-price implementation does not impose that reservation.

---

# Interpretation of the results

The current simulation supports the following bounded interpretation:

1. A fixed evaluator provides the lowest manipulation benchmark.
2. Naive history can create a strong feedback problem because the evaluator learns from outcomes that are partly affected by its previous capital allocations.
3. Capital purging can reduce this bias in some mechanism environments.
4. The correction is not uniformly successful across mechanisms.
5. Therefore, evaluator design and allocation design cannot be treated as completely independent.
6. More work is required before claiming that the proposed correction is robust.

These are **synthetic simulation results**. They are not estimates from real IPO or equity-market data.

---

# Reproducibility

**Final GitHub commit:** `b8a7ac63afeb58d9d7335a38dd1344c8edad57e7`

The project uses five canonical seeds:

```text
42
43
44
45
46
```

The full experiment contains:

```text
200 issuers
×
6 mechanism/evaluator treatments
×
5 seeds
```

The first two cohorts are treated as burn-in and excluded from the headline analysis.

The accompanying Colab notebook also records SHA-256 hashes of the five Python files and the software versions used for a fresh run.

---

# Google Colab notebook

The runnable verification notebook is:

https://colab.research.google.com/drive/1o-t9W3shjHubzSBcB8QK6KYFumrJmEbh

The notebook:

1. installs the required packages;
2. asks the user to upload the five canonical Python files;
3. verifies their SHA-256 hashes;
4. verifies the model configuration;
5. verifies the three evaluator treatments;
6. verifies the two allocation mechanisms;
7. runs a complete example simulation;
8. runs the full experiment;
9. checks experiment dimensions and burn-in;
10. displays the generated figures;
11. records the software environment and file hashes;
12. produces the final numerical table used by the paper.

The notebook is intentionally independent of GitHub at runtime: the five Python files can be uploaded directly to Colab.

---

# Hugging Face behavioral artifact

The project also provides an interactive behavioral artifact:

https://huggingface.co/spaces/dku-comsci-econ206-2026/strategic-disclosure-game

The interface presents a simplified strategic environment in which users can interact with:

- firm disclosure decisions;
- AI valuation;
- investor private information;
- investor bids;
- allocation;
- realized outcomes.

The behavioral artifact is designed to examine whether people rely on the public AI signal in the way assumed by the computational benchmark.

The Hugging Face interaction is **exploratory behavioral evidence**.

Classroom/self-selected play is not treated as population-level behavioral evidence.

In particular, stronger behavioral claims require:

- a completed sample size;
- clearly matched treatment conditions;
- recorded interaction data;
- comparison with the rational benchmark.

---

# Overleaf / manuscript

The main manuscript is compiled from:

```text
main.tex
```

The two-page main proposal is contained in:

```text
sections/proposal.tex
```

The supporting material is contained in:

```text
appendices/supporting.tex
```

The manuscript contains:

- research question;
- verified literature gap;
- strategic model;
- PBE solution concept;
- social-choice objectives;
- mechanism-design analysis;
- uniform-price versus bookbuilding comparison;
- computational results;
- behavioral-artifact limitations;
- practical implication;
- formal response to feedback;
- acknowledgements;
- team and individual contributions;
- AI-use disclosure;
- reproducibility information.

---

# Artifact links

### GitHub

https://github.com/dku-comsci-econ206-Autumn2026/ps2-fp3

### Google Colab

https://colab.research.google.com/drive/1o-t9W3shjHubzSBcB8QK6KYFumrJmEbh

### Hugging Face

https://huggingface.co/spaces/dku-comsci-econ206-2026/strategic-disclosure-game

### Poster

The A0 poster is submitted separately as the required PPTX and PDF. There is currently no public poster URL.

---

# PS2 artifact map

| Artifact | Role |
|---|---|
| Overleaf | Mathematical model, research argument, literature gap, interpretation, and formal response |
| GitHub | Canonical source code and reproducibility files |
| Google Colab | Fresh-run computational verification |
| Hugging Face | Interactive behavioral artifact |
| A0 Poster | Integrated visual presentation of the research question, model, evidence, limitations, and practical implications |

The artifacts are intended to describe the same core model and research question.

---

# Limitations

The current project has several important limitations.

## Synthetic data

The computational results are generated from a synthetic model rather than real IPO data.

Therefore, the numerical results should not be interpreted as empirical estimates of actual financial-market behavior.

## Stylized bookbuilding

The bookbuilding mechanism is deliberately simplified.

Real-world bookbuilding includes additional institutional, certification, information, and underwriter effects that are not represented here.

## Behavioral evidence

The Hugging Face artifact provides exploratory interaction rather than a representative behavioral experiment.

No population-level behavioral claim should be made without a completed and appropriately matched sample.

## Identification

The capital-purged evaluator relies on allocation variation to identify the capital footprint.

The current results show that this correction is not uniformly successful across the two mechanisms.

## Accountability rule

The proposed audit-triggered freeze is a planned design extension.

The current computational experiment does not establish that this accountability rule improves outcomes.

Future work should test:

- alternative error thresholds;
- alternative audit rules;
- endogenous allocation shocks;
- heterogeneous capital productivity;
- alternative signal noise;
- real IPO data;
- completed behavioral samples.

---

# Accountability and AI correction

A further design extension motivated by feedback received during the project is an accountability mechanism for evaluator failure.

The proposed rule is:

1. Monitor forecast error.
2. Test whether the evaluator's allocation footprint appears to explain part of the error.
3. If both conditions exceed an audit threshold, freeze the evaluator update.
4. Restore the last audited parameter.
5. Trigger human review after repeated failures.

This is a **proposed mechanism**, not a tested empirical result.

An important remaining research question is how to set the audit threshold without creating new incentives to manipulate the audit process.

---

# AI-use disclosure

The project used OpenAI ChatGPT (GPT-5.6 Luna) during September 2026 for:

- research-question refinement;
- mathematical-model clarification;
- LaTeX drafting and debugging;
- Python implementation and debugging;
- Hugging Face interface development;
- Colab/notebook organization;
- poster editing.

The human authors independently selected the research question, strategic environment, evaluator treatments, auction comparison, objectives, and core model.

AI-generated suggestions were treated as drafts. The authors checked:

- equations;
- model consistency;
- simulation logic;
- file consistency;
- artifact behavior;
- numerical outputs;
- links;
- final claims.

Generative AI was not treated as empirical evidence.

The human authors remain responsible for the submitted research, code, claims, citations, and artifacts.

---

# Acknowledgements

We thank Professor Luyao Zhang for her guidance and feedback throughout the development of the project, including her formal feedback on PS1 and her collaborative-learning feedback.

We thank Professor Ken Rogerson for discussions and feedback.

We thank Han Zhang for his discussion of evaluator accountability and the question of how an AI system should be corrected or penalized when its own predictions and feedback become unreliable.

We thank our named peer reviewers for their comments and suggestions during the PS2 peer-review process.

We also thank the COMSCI/ECON 206 classroom community for collaborative learning, questions, and discussion.

---

# Citation and references

The project draws on the following foundations, among others:

- Harsanyi, J. C. (1967/1968). Games with incomplete information played by Bayesian players.
- Vickrey, W. (1961). Counterspeculation, auctions, and competitive sealed tenders.
- Milgrom, P. R., & Weber, R. J. (1982). A theory of auctions and competitive bidding.
- Perdomo, J. C., et al. (2020). Performative prediction.
- Lacker, J. M., & Weinberg, J. A. (1989). Optimal contracts under costly state falsification.
- Crocker, K. J., & Morgan, J. (1998/2007). Costly state falsification and strategic disclosure.
- Benveniste, L. M., & Spindt, P. A. (1989). How investment bankers determine the offer price and allocation of new issues.
- Sherman, A. E. (2005). Global trends in IPO methods.
- Degeorge, F., Derrien, F., & Womack, K. L. (2010). IPO allocation and pricing.
- Logg, J. M., Minson, J. A., & Moore, D. A. (2019). Algorithm appreciation.

The complete bibliography is maintained in:

```text
references.bib
```

and the current compiled bibliography is maintained in:

```text
references_manual.tex
```

---

# Current project status

The project should be interpreted as a computational research proposal with a completed synthetic simulation pipeline and an exploratory behavioral artifact.

### Established by the current computational run

- The canonical five-file implementation runs.
- The 3 × 2 evaluator/mechanism comparison runs.
- The reported manipulation, pricing-error, feedback-bias, allocation, and retail-access metrics can be regenerated.
- Naive history produces substantially more feedback bias than the no-memory benchmark in the current simulation.
- Capital purging does not reliably eliminate the bias across mechanisms.

### Not established by the current evidence

- A causal claim about real IPO markets.
- Population-level behavioral effects.
- That the capital-purging mechanism is universally effective.
- That the proposed audit-triggered correction rule works.
- That one mechanism is universally superior to the other.

These boundaries are intentional: unfinished extensions are labelled as planned rather than presented as completed evidence.

---

# Quick reproduction checklist

From the repository root:

```bash
pip install -r requirements.txt
python src/run_experiment.py
```

Then check:

```text
results/main_results.csv
results/summary_results.csv
results/fresh_run_record.json
results/manipulation.png
results/price_rmse.png
results/allocation_efficiency.png
results/feedback_bias.png
results/retail_access.png
```

For an independent Colab verification, open:

https://colab.research.google.com/drive/1o-t9W3shjHubzSBcB8QK6KYFumrJmEbh

and upload:

```text
model.py
evaluator.py
auction.py
simulation.py
run_experiment.py
```

---

# Team

**Team FP3**

Authors:

- Feiyu Li — Duke Kunshan University
- Xuantong Fu — Duke Kunshan University

Course:

**COMSCI/ECON 206 — Computational Microeconomics**

Symposium:

**Session C**

Instructor:

**Professor Luyao Zhang**

---

# Final note

The central idea of the project is not simply that "AI can be manipulated."

The more specific problem is:

> **When an evaluator's own valuation decisions affect the outcomes it later learns from, how should evaluator memory and capital allocation be designed so that the evaluator does not mistake its own footprint for genuine firm information?**

The computational artifact provides a controlled environment for studying this feedback loop, while the Hugging Face artifact provides an exploratory behavioral interface for testing one of the model's behavioral assumptions.
