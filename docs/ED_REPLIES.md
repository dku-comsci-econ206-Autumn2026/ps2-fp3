# Ed replies to post — one from each author

**Thread:** https://edstem.org/us/courses/102917/discussion/8381683?comment=19460396
**Replying to:** Zhengjun He (Team FP4, with Yichen Shen)

Post these as **two separate replies**, one from each account. The assignment requires each
author to post their own response to classmates, and the two replies deliberately cover
different points so they are not interchangeable.

Posting record: the two replies are recorded in Appendix G as posted on 15 October 2026 (Feiyu Li) and 16 October 2026 (Xuantong Fu), according to the project record.

---

## Reply 1 — from Feiyu Li

> Thanks Zhengjun — these were the three most useful comments we got, and all three changed
> something. I'll take your first point and the distributional half of your third; Xuantong
> is replying separately on robustness and on what evidence a policy claim would need.
>
> **On the interaction being unclear.** You were right that we had described the three
> pieces separately and left the reader to assemble them. The problem was partly ours and
> partly the code's: our PS2 auction gave every investor an equal share, so "capital
> allocation" wasn't actually allocating anything, and the link you couldn't see wasn't
> really there. We've rewritten it so 160 units of demand chase 100 shares and bidders
> below the clearing price receive zero. The chain is now stated as one loop with each
> dependency named — manipulation responds to the rule's *perceived* sensitivity b̂, b̂ is
> estimated from realised performance y, y depends on capital k, and k is set by the
> mechanism. There's a traced example in `results/bid_trace.json` showing a single bid
> moving through quantity → clearing price → proceeds → the training label the evaluator
> later learns from.
>
> **On your third point, the part about who this affects.** Your team's duet paper (Milli
> et al. 2019) turned out to be a prediction about us, and we hadn't tested it. We'd been
> recommending our audit rule without measuring who pays for it. We have now: compared with
> the unsafeguarded evaluator, the audited one serves **13.1 fewer of 35 retail investors**
> (99.9% → 62.5%) and **4.2 more of 15 institutions** (36.7% → 64.8%). The entire cost of
> restoring the evaluator's integrity lands on the least-informed participants. We've
> stopped claiming the rule is an improvement full stop — it's an integrity gain with a
> distributional price, and the paper now says so.
>
> One thing we're genuinely unsure about and would value your view on: is that a cost at
> all? Under the naive rule retail gets allocated almost everything, but only because the
> inflated signal compresses bids until the auction stops sorting. Being allocated stock at
> a distorted price may not be better than being rationed at an accurate one. We report the
> number and decline to call it welfare — but we're not confident that's the right call.

---

## Reply 2 — from Xuantong Fu

> Thanks Zhengjun. Taking your second point and the "what evidence is needed" half of your
> third, since those are the parts I worked on.
>
> **On alternative assumptions and parameter settings.** Fair hit — we had five seeds and
> no uncertainty reported. We now run 20 seeds with confidence intervals computed *across
> seeds* rather than across issuers, since issuers within a run are serially dependent
> through the evaluator's memory. On top of that: a 27-setting one-at-a-time parameter grid
> over γ, β, ρ̄, σ_θ, σ_η and σ_ε; a 7-point sweep of the allocation-shock variance; a
> 7-point sweep of the coverage ratio; and a ρ = 0 placebo. The direction of the effect
> survives in **27/27** settings and the correction helps in **27/27**. The magnitude does
> not survive — naive bias ranges from 0.095 to 23.98 across the grid — which I think
> supports your scepticism rather than defeating it, so we claim the sign and not the size.
>
> The sweep also caught a mistake of ours. I had publicly challenged our own team that our
> first-stage F of 0.136 was too weak for the correction to mean anything. Re-deriving it,
> the statistic had been divided by the residual *sum of squares* instead of the residual
> *variance* — understating it by a factor of n−2. Correctly computed it's 5.47. But my
> original worry was still half right: below F = 10 the corrected estimator isn't just
> biased, it's erratic, swinging to −2.563, while the audited version's worst case over the
> same sweep is 0.275.
>
> **On how the mechanism would be evaluated in practice.** This is the one we were weakest
> on. The indicator is now explicit: the share of published rule updates carrying F ≥ 10.
> The baseline is that no venue discloses this at all today. The evidence status is labelled
> *simulated only* — we've shown the mechanism works inside our model, not that it has
> impact in any market. And the test that would make us abandon the design is stated in
> advance: run 2SLS on SEC EDGAR S-1 text crossed with realised greenshoe exercise,
> 2015–2025, and if the real first stage comes back under 10, an audited evaluator can never
> certify in practice and commitment beats correction.
>
> We also added a second risk because of your point: a published threshold is a target.
> Anyone who benefits from the evaluator staying frozen can suppress the variation it needs.
> Our current answer is that the shock should be exchange-set rather than underwriter-set,
> but I don't think that fully closes it.

---

## After posting

1. Note the posting date.
2. In `appendices/supporting.tex`, search for `assigned responses` and replace the
   `Recorded in Appendix G: Feiyu Li replied on 15 October 2026 on the interaction and distributional-burden points; Xuantong Fu replied on 16 October 2026 on robustness and the evidence required for policy claims.` marker with the date and a one-line summary of each reply.


---

## 12 October Ed post — author-supplied record

The authors supplied the following post content for the final project record. A direct URL for this particular post was not supplied, so this archive records the date and content without inventing a permalink.

### Intellectual merits
Closest paper: Juan C. Perdomo, Tijana Zrnic, Celestine Mendler-Dünner, and Moritz Hardt (2020), “Performative Prediction,” *Proceedings of the 37th International Conference on Machine Learning*, PMLR 119, 7599–7609. Official publication page: https://proceedings.mlr.press/v119/perdomo20a.html (no DOI is listed on that page).

The project builds on the insight that predictions can change the outcomes they are intended to predict and jointly models strategic firm disclosure, an AI valuation rule that influences capital allocation, and an evaluator that learns from outcomes partly caused by its previous decisions. It compares evaluator memory modes and allocation mechanisms using mean manipulation, price RMSE, allocation efficiency, and feedback-bias diagnostics. The numerical evidence is synthetic; real IPO validation remains future work.

### Practical impacts
Potential stakeholders include issuing firms, institutional and retail investors, exchanges, and financial regulators. The post connects auditable AI valuation rules, documented calibration histories, and correction procedures to SDG 16, Target 16.6. Proposed indicators include strategic manipulation, price RMSE, allocation efficiency, feedback-bias diagnostics, and public audit/correction records. These are proposed evaluation measures, not demonstrated real-world impacts; current quantitative results are simulation-based.

### Future research directions
Proposed extensions include testing real IPO data and credible allocation shocks; repeated issuance, heterogeneous firms, and cross-market settings; competition between AI evaluators; and audit-triggered freezes, restoration of audited parameters, and human review.

**Nobel frontier prediction:** growing recognition for the intersection of mechanism design, strategic information disclosure, and accountable AI decision-making, because consequential AI systems should learn from outcomes without reinforcing the effects of their own decisions.
