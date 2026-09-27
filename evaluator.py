"""Three evaluator memory modes in the PS2 proposal.

No memory: uses b_true.
Naive history: updates b by regressing realized outcome on disclosure.
Capital-purged: estimates the capital footprint using the allocation shock psi
as an instrument for k, subject to a first-stage F diagnostic.
"""
import numpy as np
from model import public_signal

MODES = ("no_memory", "naive_history", "capital_purged")

class Evaluator:
    def __init__(self, mode, cfg):
        if mode not in MODES:
            raise ValueError(mode)
        self.mode = mode
        self.cfg = cfg
        self.d = []
        self.y = []
        self.k = []
        self.psi = []
        self.theta = []
        self.rho = []
        self.b_hat = cfg.b_true

    def _ols_slope(self, x, y):
        x, y = np.asarray(x), np.asarray(y)
        if len(x) < 5 or np.var(x) < 1e-12:
            return self.cfg.b_true
        return float(np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1))

    def update(self, d, y, k, psi, theta, rho):
        self.d.append(float(d)); self.y.append(float(y)); self.k.append(float(k))
        self.psi.append(float(psi)); self.theta.append(float(theta)); self.rho.append(float(rho))
        if self.mode == "no_memory":
            self.b_hat = self.cfg.b_true
            return
        d_arr = np.asarray(self.d); y_arr = np.asarray(self.y); k_arr = np.asarray(self.k)
        if self.mode == "naive_history":
            # Naive learning follows the decomposition stated in the paper.
            self.b_hat = self._ols_slope(d_arr, y_arr)
        else:
            # Capital-purged benchmark: first-stage k <- psi, then use the
            # instrument to isolate the capital footprint before learning b.
            psi_arr = np.asarray(self.psi)
            if len(psi_arr) >= 5 and np.var(psi_arr) > 1e-12:
                first = self._ols_slope(psi_arr, k_arr)
                fitted_k = np.mean(k_arr) + first * (psi_arr - np.mean(psi_arr))
                beta_k = self._ols_slope(fitted_k, y_arr - self.cfg.b_true * d_arr)
                # Remove the estimated capital footprint and re-estimate b.
                purged_y = y_arr - beta_k * fitted_k
                self.b_hat = self._ols_slope(d_arr, purged_y)
            else:
                self.b_hat = self.cfg.b_true

    def score(self, d, rng):
        return public_signal(d, self.b_hat, rng, self.cfg)[0]

    def first_stage_F(self):
        if len(self.psi) < 5:
            return np.nan
        z = np.asarray(self.psi); k = np.asarray(self.k)
        if np.var(z) < 1e-12:
            return 0.0
        slope = self._ols_slope(z, k)
        resid = k - (np.mean(k) + slope * (z - np.mean(z)))
        if np.var(resid) < 1e-12:
            return np.inf
        return float((slope ** 2 * np.sum((z-z.mean())**2)) / np.sum(resid**2))

    def feedback_bias(self):
        return self.b_hat - self.cfg.b_true
