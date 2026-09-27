"""M1 uniform-price auction and M2 stylized bookbuilding from PS2."""
import numpy as np


def investor_signals(theta, rng, cfg):
    inst = theta + rng.normal(0, cfg.sigma_xi_institutional, cfg.n_institutional)
    retail = theta + rng.normal(0, cfg.sigma_xi_retail, cfg.n_retail)
    return np.r_[inst, retail]


def posterior_bids(public_signal_value, x, cfg, expected_m):
    """Bayesian benchmark: remove expected disclosure inflation from public signal,
    then precision-weight public and private signals. The public-signal precision
    is implied by beta*b*sigma_eta in the stated signal equation.
    """
    b = cfg.b_true
    # Invert the public rule to recover expected disclosure, then remove expected m.
    public_d = ((public_signal_value - (1-cfg.beta)*cfg.mu0) /
                (cfg.beta * b) - cfg.a)
    public_theta = public_d - expected_m
    public_sd = max(cfg.sigma_eta, 1e-6)
    w_public = 1.0 / (public_sd**2)
    bids = np.empty(cfg.n_investors)
    for i, xi in enumerate(x):
        sd = cfg.sigma_xi_institutional if i < cfg.n_institutional else cfg.sigma_xi_retail
        w_private = 1.0 / (sd**2)
        bids[i] = (w_public * public_theta + w_private * xi) / (w_public + w_private)
    return bids


def uniform_price(bids, cfg, rng):
    n = len(bids)
    q = np.full(n, cfg.shares / n)
    order = np.argsort(-bids)
    allocation = np.zeros(n)
    remaining = cfg.shares
    accepted = []
    for i in order:
        take = min(q[i], remaining)
        allocation[i] = take
        accepted.append(bids[i])
        remaining -= take
        if remaining <= 1e-12:
            break
    P = float(min(accepted)) if accepted else 0.0
    psi = rng.normal(0, cfg.psi_sd_uniform)
    k = max(0.0, P * (1.0 + psi))
    return P, allocation, k, psi


def bookbuilding(bids, cfg, rng):
    n = len(bids)
    inst_n, retail_n = cfg.n_institutional, cfg.n_retail
    allocation = np.zeros(n)
    # 85% of the offering is reserved for institutions; 15% for retail.
    inst_shares = cfg.shares * cfg.bookbuilding_institutional_share
    retail_shares = cfg.shares - inst_shares
    inst_order = np.argsort(-bids[:inst_n])
    retail_order = np.argsort(-bids[inst_n:]) + inst_n
    for order, supply in ((inst_order, inst_shares), (retail_order, retail_shares)):
        remaining = supply
        q = supply / len(order)
        for i in order:
            allocation[i] = min(q, remaining)
            remaining -= allocation[i]
    # Precision-weighted institutional estimate (all institutions have the same sigma).
    inst_precision = np.full(inst_n, 1.0 / cfg.sigma_xi_institutional**2)
    inst_est = float(np.average(bids[:inst_n], weights=inst_precision))
    P = max(0.0, inst_est * (1.0 - cfg.bookbuilding_discount))
    psi = rng.normal(0, cfg.psi_sd_bookbuilding)
    k = max(0.0, P * (1.0 + psi))
    return P, allocation, k, psi
