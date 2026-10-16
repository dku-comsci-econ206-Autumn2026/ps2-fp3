"""Allocation mechanisms: M1 uniform-price auction, M2 stylised bookbuilding.

WHAT CHANGED AFTER THE 14 OCT 2026 INSTRUCTOR FEEDBACK
------------------------------------------------------
The PS2 implementation gave every investor `shares / n_investors` units, so
total demand equalled supply exactly and *no bid could ever exclude anybody*.
The allocation comparison was therefore a pricing comparison in disguise.

The final version makes the offering genuinely scarce.  Each investor submits a
price-quantity pair (b_i, q_i).  Demand is 160 units against a 100-unit
offering (coverage 1.6x).  Bids are ranked, filled until the offering is
exhausted, the marginal bidder is pro-rated, and every investor below the
clearing bid receives ZERO.  Raising a bid now buys priority; lowering it can
cost an investor the entire allocation.

The PS2 rule is preserved verbatim as `fixed_rationing` so the two
interpretations can be compared on identical seeds rather than one replacing
the other silently.

INSTRUMENT.  psi is an over-allotment ("greenshoe") shock to the *number of
shares sold*, not a free-floating multiplier on proceeds.  Q_sold = shares
(1 + psi).  Because psi shifts supply along a downward-sloping demand schedule
it moves the clearing price and the proceeds, while entering the outcome
equation y = theta + rho k + eps only through k.  That is the exclusion
restriction the capital-purged evaluator relies on, and it is now a property of
the mechanism rather than an assumption bolted on afterwards.

BOUNDARY.  Bidders are modelled as submitting their posterior mean for their
full quantity (flat demand curves).  Real multi-unit bidders shade -- "demand
reduction" -- and real bookbuilding carries certification and relationship
effects.  Neither is represented here; both are recorded as limitations.
"""
import numpy as np


def investor_signals(theta, rng, cfg):
    inst = theta + rng.normal(0, cfg.sigma_xi_institutional, cfg.n_institutional)
    retail = theta + rng.normal(0, cfg.sigma_xi_retail, cfg.n_retail)
    return np.r_[inst, retail]


def investor_quantities(cfg):
    """Maximum quantity each investor is willing to take."""
    return np.r_[np.full(cfg.n_institutional, cfg.q_institutional),
                 np.full(cfg.n_retail, cfg.q_retail)]


def posterior_bids(public_signal_value, x, cfg, expected_m):
    """Bayesian benchmark bid: strip the *expected* disclosure inflation out of
    the public signal, then precision-weight it against the private signal.

    This is the rational-investor benchmark the Hugging Face behavioural task
    is designed to challenge.
    """
    b = cfg.b_true
    public_d = ((public_signal_value - (1 - cfg.beta) * cfg.mu0)
                / (cfg.beta * b) - cfg.a)
    public_theta = public_d - expected_m
    public_sd = max(cfg.sigma_eta, 1e-6)
    w_public = 1.0 / (public_sd ** 2)
    bids = np.empty(cfg.n_investors)
    for i, xi in enumerate(x):
        sd = (cfg.sigma_xi_institutional if i < cfg.n_institutional
              else cfg.sigma_xi_retail)
        w_private = 1.0 / (sd ** 2)
        bids[i] = (w_public * public_theta + w_private * xi) / (w_public + w_private)
    return bids


def _fill(order, quantities, supply):
    """Fill demand in `order` until `supply` runs out. Pro-rate the marginal
    bidder; everyone after them gets zero. Returns (allocation, marginal index).
    """
    allocation = np.zeros(len(quantities))
    remaining = float(supply)
    marginal = None
    for i in order:
        if remaining <= 1e-12:
            break
        take = min(quantities[i], remaining)
        allocation[i] = take
        remaining -= take
        marginal = i
    return allocation, marginal


def uniform_price(bids, cfg, rng):
    """M1. Clearing price = lowest ACCEPTED bid; losers are excluded."""
    psi = float(rng.normal(0, cfg.psi_sd_uniform))
    q_sold = max(1e-6, cfg.shares * (1.0 + psi))
    order = np.argsort(-bids)

    if cfg.allocation_rule == "fixed_rationing":
        # Retained PS2 arm: equal shares for all, nobody excluded.
        q = np.full(len(bids), cfg.shares / len(bids))
        allocation, marginal = _fill(order, q, cfg.shares)
        P = float(bids[order[-1]])          # lowest bid clears: all are served
    else:
        q = investor_quantities(cfg)
        allocation, marginal = _fill(order, q, q_sold)
        P = float(bids[marginal]) if marginal is not None else 0.0

    P = max(0.0, P)
    k = P * (q_sold / cfg.shares)           # proceeds, normalised per offering
    return P, allocation, k, psi


def bookbuilding(bids, cfg, rng):
    """M2. Underwriter reserves 85% for institutions and prices at a discount
    to the precision-weighted institutional estimate. Within each tier the
    offering is still scarce, so weak bids are excluded there too.
    """
    psi = float(rng.normal(0, cfg.psi_sd_bookbuilding))
    q_sold = max(1e-6, cfg.shares * (1.0 + psi))
    inst_n = cfg.n_institutional
    inst_supply = q_sold * cfg.bookbuilding_institutional_share
    retail_supply = q_sold - inst_supply

    if cfg.allocation_rule == "fixed_rationing":
        q = np.r_[np.full(inst_n, inst_supply / inst_n),
                  np.full(cfg.n_retail, retail_supply / cfg.n_retail)]
    else:
        q = investor_quantities(cfg)

    inst_order = np.argsort(-bids[:inst_n])
    retail_order = np.argsort(-bids[inst_n:]) + inst_n
    alloc_i, _ = _fill(inst_order, q, inst_supply)
    alloc_r, _ = _fill(retail_order, q, retail_supply)
    allocation = alloc_i + alloc_r

    inst_precision = np.full(inst_n, 1.0 / cfg.sigma_xi_institutional ** 2)
    inst_est = float(np.average(bids[:inst_n], weights=inst_precision))
    P = max(0.0, inst_est * (1.0 - cfg.bookbuilding_discount))
    k = P * (q_sold / cfg.shares)
    return P, allocation, k, psi


def trace_one_bid(bids, cfg, rng_seed=0, investor=0, delta=1.0):
    """Audit helper requested by the instructor: trace ONE bid through quantity,
    price, proceeds and training label, to show the bid is consequential.
    """
    out = {}
    for label, shift in (("baseline", 0.0), ("raised", delta), ("lowered", -delta)):
        b = bids.copy()
        b[investor] += shift
        rng = np.random.default_rng(rng_seed)   # same psi draw in all three
        P, alloc, k, psi = uniform_price(b, cfg, rng)
        out[label] = {"bid": float(b[investor]), "quantity": float(alloc[investor]),
                      "clearing_price": P, "proceeds_k": k, "psi": psi,
                      "n_served": int((alloc > 1e-9).sum())}
    return out
