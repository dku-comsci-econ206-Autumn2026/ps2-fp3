"""PS2 model: strategic disclosure, AI valuation, allocation, and feedback.

This file mirrors the equations and parameter values written in the supplied
PS2 Overleaf project. Where the paper does not yet give a numerical
calibration (notably the distributions of v and rho and lambda_P), those are
kept as explicit configuration fields rather than hidden inside functions.
"""
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class Config:
    # Written in the PS2 appendix
    n_issuers: int = 200
    n_cohorts: int = 10
    issuers_per_cohort: int = 20
    burn_in_cohorts: int = 2
    shares: float = 100.0
    gamma: float = 0.006
    sigma_theta: float = 1.0
    sigma_eta: float = 0.5
    mu0: float = 8.5
    beta: float = 0.60
    lambda_: float = 1.0
    sigma_epsilon: float = 0.8
    n_institutional: int = 15
    n_retail: int = 35
    sigma_xi_institutional: float = 1.0
    sigma_xi_retail: float = 2.5
    b_true: float = 1.02  # reported in the current Overleaf output
    a: float = 0.0
    lambda_P: float = 1.0  # normalization; not numerically specified in paper
    kappa0: float = 0.0    # drops out because lambda_=1
    bookbuilding_institutional_share: float = 0.85
    bookbuilding_discount: float = 0.08
    # Explicit completion of quantities not numerically specified in Overleaf.
    # These must be copied into the paper before claiming exact numerical parity.
    v_mean: float = 2.2
    v_sd: float = 0.4
    rho_mean: float = 0.50
    rho_sd: float = 0.12
    psi_sd_uniform: float = 0.08
    psi_sd_bookbuilding: float = 0.20

    @property
    def n_investors(self):
        return self.n_institutional + self.n_retail

    def validate(self):
        assert self.n_issuers == self.n_cohorts * self.issuers_per_cohort
        assert self.n_investors == 50
        assert self.shares == 100
        assert self.burn_in_cohorts == 2
        assert self.lambda_ == 1.0


def draw_issuer_types(rng, cfg):
    # theta is centered on the evaluator prior mu0; the paper specifies sigma_theta.
    theta = rng.normal(cfg.mu0, cfg.sigma_theta)
    v = max(0.05, rng.normal(cfg.v_mean, cfg.v_sd))
    rho = max(0.01, rng.normal(cfg.rho_mean, cfg.rho_sd))
    return theta, v, rho


def disclosure(theta, m):
    return theta + m


def manipulation_cost(m, gamma):
    return m * m / (2.0 * gamma)


def best_response(v, cfg, perceived_b):
    # Exact expression stated in Appendix A:
    # m*=gamma*v*n*lambda_P*[lambda*beta*b+(1-lambda)*kappa0]
    return max(0.0, cfg.gamma * v * cfg.n_investors * cfg.lambda_P * (
        cfg.lambda_ * cfg.beta * perceived_b
        + (1.0 - cfg.lambda_) * cfg.kappa0
    ))


def public_signal(d, b, rng, cfg):
    eta = rng.normal(0.0, cfg.sigma_eta)
    s = (1.0 - cfg.beta) * cfg.mu0 + cfg.beta * (
        cfg.a + b * (d + eta)
    )
    return s, eta


def performance(theta, rho, k, rng, cfg):
    eps = rng.normal(0.0, cfg.sigma_epsilon)
    y = theta + rho * k + eps
    return y, eps
