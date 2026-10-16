"""Evaluator memory modes and the audit rule.

FOUR modes, in increasing order of accountability:

  no_memory       Fixed announced rule. b_hat = b_true forever. The commitment
                  benchmark.
  naive_history   Revisable rule. OLS of realised performance on disclosure.
                  Absorbs the evaluator's own capital footprint.
  capital_purged  Revisable rule with 2SLS: the greenshoe shock psi instruments
                  for capital k, with disclosure d as an included control.
  audited_freeze  capital_purged PLUS the accountability rule. The first-stage
                  F is the audit statistic. If F falls below the Staiger-Stock
                  threshold the correction is not identified, the update is
                  FROZEN, and the last audited parameter is restored. Repeated
                  freezes are logged for human review.

TWO BUGS FIXED RELATIVE TO PS2 (both verified in tests/test_verification.py):

  1. first_stage_F divided by the residual SUM OF SQUARES instead of the
     residual VARIANCE, understating every reported F by a factor of (n-2).
     The PS2 paper's "F = 0.136" is 5.47 once normalised correctly. The
     weak-instrument reading was partly a software defect -- but only partly:
     see mode-dependence in the results.

  2. The purge used b_true when constructing its target, so the estimator
     silently used the answer it was meant to recover. Replaced with textbook
     two-stage least squares, which uses no knowledge of b_true.

NOTE ON THE STRUCTURAL VALUE OF b. In y = theta + rho k + eps with
d = theta + m, the coefficient of y on d holding k fixed is exactly 1.00. The
paper's stated calibration is b_true = 1.02, so a perfectly identified
estimator reports a residual "bias" of about -0.02. That offset is a property
of the stated calibration, not of the estimator, and is reported as such.
"""
import numpy as np
from model import public_signal

MODES = ("no_memory", "naive_history", "capital_purged", "audited_freeze")
LEARNING_MODES = ("naive_history", "capital_purged", "audited_freeze")


def _ols(X, y):
    """Return (coefficients, standard errors, dof). X includes its intercept."""
    n, p = X.shape
    if n <= p:
        return None, None, 0
    XtX = X.T @ X
    if np.linalg.cond(XtX) > 1e12:
        return None, None, 0
    beta = np.linalg.solve(XtX, X.T @ y)
    resid = y - X @ beta
    dof = n - p
    s2 = float(resid @ resid) / dof
    if s2 <= 0:
        return beta, np.zeros(p), dof
    se = np.sqrt(np.maximum(s2 * np.diag(np.linalg.inv(XtX)), 0.0))
    return beta, se, dof


class Evaluator:
    def __init__(self, mode, cfg):
        if mode not in MODES:
            raise ValueError(f"unknown mode {mode!r}; expected one of {MODES}")
        self.mode, self.cfg = mode, cfg
        self.d, self.y, self.k, self.psi = [], [], [], []
        self.b_hat = cfg.b_true
        self.b_audited = cfg.b_true      # last parameter that passed the audit
        self.F_current = np.nan
        self.frozen = False
        self.freeze_events = 0
        self.n_updates = 0

    # ---------------------------------------------------------------- stats
    def first_stage_F(self):
        """F on the excluded instrument psi in  k ~ 1 + d + psi.

        This is the textbook t^2 form. The PS2 implementation is kept below as
        `first_stage_F_legacy` so the correction is auditable rather than
        silently applied.
        """
        n = len(self.psi)
        if n < 10:
            return np.nan
        z, d, k = map(np.asarray, (self.psi, self.d, self.k))
        if np.var(z) < 1e-12:
            return 0.0
        X = np.c_[np.ones(n), d, z]
        beta, se, dof = _ols(X, k)
        if beta is None or se is None or se[2] <= 0:
            return np.nan
        return float((beta[2] / se[2]) ** 2)

    def first_stage_F_legacy(self):
        """The PS2 formula, retained to document the (n-2) normalisation bug."""
        n = len(self.psi)
        if n < 5:
            return np.nan
        z, k = np.asarray(self.psi), np.asarray(self.k)
        if np.var(z) < 1e-12:
            return 0.0
        slope = float(np.cov(z, k, ddof=1)[0, 1] / np.var(z, ddof=1))
        resid = k - (k.mean() + slope * (z - z.mean()))
        ssr = float(resid @ resid)
        if ssr < 1e-12:
            return np.inf
        return float(slope ** 2 * np.sum((z - z.mean()) ** 2) / ssr)

    # ------------------------------------------------------------ estimators
    def _naive(self):
        n = len(self.d)
        X = np.c_[np.ones(n), np.asarray(self.d)]
        beta, _, _ = _ols(X, np.asarray(self.y))
        return None if beta is None else float(beta[1])

    def _two_stage(self):
        """2SLS of y on (d, k), instrumenting k with psi. Returns (b_hat, rho_hat)."""
        n = len(self.d)
        d, y, k, z = map(np.asarray, (self.d, self.y, self.k, self.psi))
        first, se1, _ = _ols(np.c_[np.ones(n), d, z], k)
        if first is None:
            return None, None
        k_hat = np.c_[np.ones(n), d, z] @ first
        second, _, _ = _ols(np.c_[np.ones(n), d, k_hat], y)
        if second is None:
            return None, None
        return float(second[1]), float(second[2])

    # ---------------------------------------------------------------- update
    def update(self, d, y, k, psi, theta=None, rho=None):
        self.d.append(float(d)); self.y.append(float(y))
        self.k.append(float(k)); self.psi.append(float(psi))
        self.n_updates += 1
        self.frozen = False

        if self.mode == "no_memory":
            self.b_hat = self.cfg.b_true
            self.F_current = self.first_stage_F()
            return

        if len(self.d) < 10:        # not enough history to estimate anything
            self.F_current = self.first_stage_F()
            return

        self.F_current = self.first_stage_F()

        if self.mode == "naive_history":
            est = self._naive()
        else:
            est, _ = self._two_stage()

        if est is None or not np.isfinite(est):
            self.frozen = True
            self.freeze_events += 1
            return

        if self.mode == "audited_freeze":
            # ---- the accountability rule -------------------------------
            # An evaluator must EARN the right to revise its own rule. The
            # correction is certified only if (a) the sample is thick enough
            # to audit and (b) the first stage is strong enough for the
            # correction to be identified. Otherwise the update is FROZEN and
            # the last audited parameter is restored -- which, until any audit
            # has ever passed, is the originally committed rule b_true.
            #
            # Without the min_audit_n guard the rule certifies on a thin,
            # noisy sample and then locks in permanently; that failure is
            # demonstrated in results/audit_lockin.csv.
            identified = (np.isfinite(self.F_current)
                          and self.F_current >= self.cfg.first_stage_F_threshold)
            thick = len(self.d) >= self.cfg.min_audit_n
            if not (identified and thick):
                self.frozen = True
                self.freeze_events += 1
                self.b_hat = self.b_audited      # restoration criterion
                return
            self.b_audited = float(np.clip(est, -self.cfg.b_hat_clip,
                                           self.cfg.b_hat_clip))

        self.b_hat = float(np.clip(est, -self.cfg.b_hat_clip, self.cfg.b_hat_clip))

    # ----------------------------------------------------------------- misc
    def score(self, d, rng):
        return public_signal(d, self.b_hat, rng, self.cfg)[0]

    def feedback_bias(self):
        return self.b_hat - self.cfg.b_true

    @property
    def freeze_rate(self):
        return self.freeze_events / max(1, self.n_updates)
