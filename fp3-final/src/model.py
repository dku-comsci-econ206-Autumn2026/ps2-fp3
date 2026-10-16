"""FP3 final model: strategic disclosure, AI valuation, capital allocation, feedback.

Primitives follow the paper exactly:

    disclosure      d_t = theta_t + m_t,          c(m) = m^2 / (2 gamma)
    public signal   s_t = (1-beta) mu_0 + beta [a + b_hat (d_t + eta_t)]
    performance     y_t = theta_t + rho_t k_t + eps_t

Every quantity the paper reports is a field of `Config` so that the paper,
the notebook and the Space read the same numbers from one place.

Change from the PS2 version (instructor feedback, 14 Oct 2026): the offering is
genuinely scarce.  Investors now submit (bid, quantity) pairs whose total demand
exceeds the offering, so a bid determines *whether* an investor is served, not
only what they pay.  The PS2 fixed-rationing rule is retained verbatim as an
explicitly labelled robustness arm (`allocation_rule="fixed_rationing"`).
"""
from dataclasses import dataclass, replace
import numpy as np


@dataclass(frozen=True)
class Config:
    # --- written in the PS2 appendix; unchanged ---------------------------
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
    b_true: float = 1.02
    a: float = 0.0
    lambda_P: float = 1.0
    kappa0: float = 0.0
    bookbuilding_institutional_share: float = 0.85
    bookbuilding_discount: float = 0.08
    v_mean: float = 2.2
    v_sd: float = 0.4
    rho_mean: float = 0.50
    rho_sd: float = 0.12
    psi_sd_uniform: float = 0.08
    psi_sd_bookbuilding: float = 0.20

    # --- new in the final version ----------------------------------------
    # Per-investor maximum demand.  15*6 + 35*2 = 160 shares of demand chase a
    # 100-share offering, a 1.6x coverage ratio, so the marginal bidder is
    # excluded.  Under "fixed_rationing" these are ignored and every investor
    # receives shares/n, which is the PS2 behaviour.
    q_institutional: float = 6.0
    q_retail: float = 2.0
    allocation_rule: str = "excludable"   # "excludable" | "fixed_rationing"

    # Diagnostic / audit thresholds.
    first_stage_F_threshold: float = 10.0   # Staiger-Stock convention
    min_audit_n: int = 40                   # no certification on a thin sample
    b_hat_clip: float = 25.0                # numerical guard, never binds on-path

    @property
    def n_investors(self) -> int:
        return self.n_institutional + self.n_retail

    @property
    def total_demand(self) -> float:
        return (self.n_institutional * self.q_institutional
                + self.n_retail * self.q_retail)

    @property
    def coverage_ratio(self) -> float:
        return self.total_demand / self.shares

    def validate(self) -> None:
        assert self.n_issuers == self.n_cohorts * self.issuers_per_cohort
        assert self.n_investors == 50
        assert self.shares == 100
        assert self.burn_in_cohorts == 2
        assert self.lambda_ == 1.0
        assert self.allocation_rule in ("excludable", "fixed_rationing")
        if self.allocation_rule == "excludable":
            # The offering must actually be scarce, otherwise a bid cannot
            # exclude anybody and the auction comparison is vacuous.
            assert self.total_demand > self.shares, (
                "excludable demand requires total demand > offering")

    def with_(self, **kw) -> "Config":
        """Return a copy with fields replaced (frozen dataclass helper)."""
        return replace(self, **kw)


def draw_issuer_types(rng, cfg):
    theta = rng.normal(cfg.mu0, cfg.sigma_theta)
    v = max(0.05, rng.normal(cfg.v_mean, cfg.v_sd))
    rho = max(0.0, rng.normal(cfg.rho_mean, cfg.rho_sd))
    return theta, v, rho


def disclosure(theta, m):
    return theta + m


def manipulation_cost(m, gamma):
    return m * m / (2.0 * gamma)


def best_response(v, cfg, perceived_b):
    """m* = gamma v n lambda_P [lambda beta b + (1-lambda) kappa_0].

    Derived in Appendix A.  Increasing in the evaluator's perceived sensitivity
    `perceived_b`: this is the channel through which evaluator learning feeds
    back into issuer behaviour.
    """
    return max(0.0, cfg.gamma * v * cfg.n_investors * cfg.lambda_P * (
        cfg.lambda_ * cfg.beta * perceived_b
        + (1.0 - cfg.lambda_) * cfg.kappa0))


def public_signal(d, b, rng, cfg):
    eta = rng.normal(0.0, cfg.sigma_eta)
    s = (1.0 - cfg.beta) * cfg.mu0 + cfg.beta * (cfg.a + b * (d + eta))
    return s, eta


def performance(theta, rho, k, rng, cfg):
    eps = rng.normal(0.0, cfg.sigma_epsilon)
    return theta + rho * k + eps, eps
