"""Sequential PS2 simulation: 10 cohorts x 20 issuers, seeds 42--46."""
import numpy as np
import pandas as pd
from model import Config, draw_issuer_types, disclosure, manipulation_cost, best_response, performance
from evaluator import Evaluator, MODES
from auction import investor_signals, posterior_bids, uniform_price, bookbuilding

MECHANISMS = ("uniform_price", "bookbuilding")


def run(seed, mode, mechanism, cfg=None):
    cfg = cfg or Config(); cfg.validate()
    rng = np.random.default_rng(seed)
    evaluator = Evaluator(mode, cfg)
    rows = []
    # The paper describes memory as cross-firm and includes a two-cohort burn-in.
    for cohort in range(cfg.n_cohorts):
        for j in range(cfg.issuers_per_cohort):
            firm_id = cohort * cfg.issuers_per_cohort + j
            theta, v, rho = draw_issuer_types(rng, cfg)
            m = best_response(v, cfg, evaluator.b_hat)
            d = disclosure(theta, m)
            s = evaluator.score(d, rng)
            x = investor_signals(theta, rng, cfg)
            expected_m = m if mode == "no_memory" else np.mean([r["m"] for r in rows[-20:]]) if rows else m
            bids = posterior_bids(s, x, cfg, expected_m)
            if mechanism == "uniform_price":
                P, alloc, k, psi = uniform_price(bids, cfg, rng)
            else:
                P, alloc, k, psi = bookbuilding(bids, cfg, rng)
            y, eps = performance(theta, rho, k, rng, cfg)
            evaluator.update(d, y, k, psi, theta, rho)
            retail_share = alloc[cfg.n_institutional:].sum() / cfg.shares
            rows.append({
                "seed": seed, "cohort": cohort, "firm_id": firm_id,
                "memory": mode, "mechanism": mechanism,
                "theta": theta, "v": v, "rho": rho,
                "m": m, "disclosure": d, "ai_signal": s,
                "price": P, "capital": k, "psi": psi,
                "performance": y, "epsilon": eps,
                "manipulation_cost": manipulation_cost(m, cfg.gamma),
                "price_error": P-theta, "retail_share": retail_share,
                "feedback_bias": evaluator.feedback_bias(),
                "first_stage_F": evaluator.first_stage_F(),
            })
    return pd.DataFrame(rows)
