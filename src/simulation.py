"""Sequential simulation: 10 cohorts x 20 issuers per run."""
import numpy as np
import pandas as pd

from model import (Config, draw_issuer_types, disclosure, manipulation_cost,
                   best_response, performance)
from evaluator import Evaluator, MODES
from auction import (investor_signals, posterior_bids, uniform_price,
                     bookbuilding)

MECHANISMS = ("uniform_price", "bookbuilding")


def run(seed, mode, mechanism, cfg=None):
    """One sequential market. Returns a tidy per-issuer DataFrame."""
    cfg = cfg or Config()
    cfg.validate()
    rng = np.random.default_rng(seed)
    ev = Evaluator(mode, cfg)
    rows = []

    for cohort in range(cfg.n_cohorts):
        for j in range(cfg.issuers_per_cohort):
            theta, v, rho = draw_issuer_types(rng, cfg)

            # 1. issuer discloses, best-responding to the CURRENT published rule
            m = best_response(v, cfg, ev.b_hat)
            d = disclosure(theta, m)

            # 2. evaluator publishes the signal
            s = ev.score(d, rng)

            # 3. investors form posteriors and bid
            x = investor_signals(theta, rng, cfg)
            # Investors know the rule and strip the average inflation they have
            # recently observed. With no memory the rule is fixed, so the
            # expectation is exact.
            if mode == "no_memory" or not rows:
                expected_m = m
            else:
                expected_m = float(np.mean([r["m"] for r in rows[-20:]]))
            bids = posterior_bids(s, x, cfg, expected_m)

            # 4. the mechanism allocates and prices
            if mechanism == "uniform_price":
                P, alloc, k, psi = uniform_price(bids, cfg, rng)
            else:
                P, alloc, k, psi = bookbuilding(bids, cfg, rng)

            # 5. capital changes realised performance
            y, eps = performance(theta, rho, k, rng, cfg)

            # 6. the outcome enters the evaluator's history
            ev.update(d, y, k, psi)

            served = alloc > 1e-9
            sold = alloc.sum()
            rows.append({
                "seed": seed, "cohort": cohort,
                "firm_id": cohort * cfg.issuers_per_cohort + j,
                "memory": mode, "mechanism": mechanism,
                "allocation_rule": cfg.allocation_rule,
                "theta": theta, "v": v, "rho": rho,
                "m": m, "disclosure": d, "ai_signal": s,
                "price": P, "capital": k, "psi": psi,
                "performance": y, "epsilon": eps,
                "manipulation_cost": manipulation_cost(m, cfg.gamma),
                "price_error": P - theta,
                "b_hat": ev.b_hat,
                "feedback_bias": ev.feedback_bias(),
                "first_stage_F": ev.F_current,
                "frozen": bool(ev.frozen),
                "shares_sold": sold,
                "n_served": int(served.sum()),
                "n_excluded": int(cfg.n_investors - served.sum()),
                "retail_share": (alloc[cfg.n_institutional:].sum() / sold
                                 if sold > 1e-9 else np.nan),
                "retail_investors_served": int(served[cfg.n_institutional:].sum()),
            })
    return pd.DataFrame(rows)
