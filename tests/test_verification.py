"""Verification tests. Run:  python -m pytest tests -q   (or: python tests/test_verification.py)

These are the checks the team ran when responding to the 14 October instructor
feedback and to its own two self-challenges. Each test corresponds to a claim
made in the paper, so a failure here means a claim in the paper is wrong.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from model import Config                                        # noqa: E402
from evaluator import Evaluator, _ols                           # noqa: E402
from auction import (uniform_price, bookbuilding, posterior_bids,   # noqa: E402
                     investor_signals, investor_quantities)
from simulation import run                                      # noqa: E402


# ----------------------------------------------------------- the auction fix
def test_offering_is_scarce():
    """Instructor, 14 Oct: 'the current code gives every investor shares'."""
    cfg = Config()
    assert cfg.total_demand > cfg.shares
    assert cfg.coverage_ratio > 1.0
    print(f"  demand {cfg.total_demand:.0f} vs offering {cfg.shares:.0f} "
          f"(coverage {cfg.coverage_ratio:.2f}x)")


def test_bids_exclude_investors():
    """A low bidder must receive ZERO, and the count of served investors must
    be strictly below the number of bidders."""
    cfg = Config()
    rng = np.random.default_rng(0)
    bids = rng.normal(8.5, 1.0, cfg.n_investors)
    P, alloc, k, psi = uniform_price(bids, cfg, rng)
    served = alloc > 1e-9
    assert served.sum() < cfg.n_investors, "nobody was excluded"
    assert alloc[np.argmin(bids)] == 0.0, "the lowest bidder still got shares"
    assert P >= np.min(bids[served]) - 1e-9
    print(f"  served {served.sum()}/{cfg.n_investors}, "
          f"excluded {cfg.n_investors - served.sum()}, clearing price {P:.3f}")


def test_bid_is_consequential():
    """Raising one bid must weakly increase that investor's quantity; lowering
    it far enough must drive the quantity to zero. This is the property the
    PS2 implementation lacked."""
    cfg = Config()
    rng = np.random.default_rng(1)
    bids = rng.normal(8.5, 1.0, cfg.n_investors)
    i = int(np.argsort(-bids)[24])          # an investor near the margin
    qs = {}
    for shift in (-3.0, 0.0, +3.0):
        b = bids.copy(); b[i] += shift
        _, alloc, _, _ = uniform_price(b, cfg, np.random.default_rng(11))
        qs[shift] = alloc[i]
    assert qs[-3.0] == 0.0, "a far-below-market bid still won shares"
    assert qs[+3.0] >= qs[0.0] >= qs[-3.0]
    print(f"  quantity at bid-3 / bid / bid+3 = "
          f"{qs[-3.0]:.2f} / {qs[0.0]:.2f} / {qs[3.0]:.2f}")


def test_fixed_rationing_arm_excludes_nobody():
    """The retained PS2 arm must reproduce the old behaviour exactly, so the
    comparison is like-for-like."""
    cfg = Config().with_(allocation_rule="fixed_rationing")
    rng = np.random.default_rng(0)
    bids = rng.normal(8.5, 1.0, cfg.n_investors)
    _, alloc, _, _ = uniform_price(bids, cfg, rng)
    assert (alloc > 1e-9).all(), "the PS2 arm should serve everybody"
    assert np.allclose(alloc, cfg.shares / cfg.n_investors)
    print(f"  PS2 arm: all {cfg.n_investors} served {alloc[0]:.1f} shares each")


# ------------------------------------------------------- the F-statistic fix
def test_first_stage_F_normalisation():
    """PS2 divided by the residual SUM OF SQUARES rather than the residual
    VARIANCE, understating every F by a factor of (n - dof)."""
    cfg = Config()
    df = run(42, "capital_purged", "uniform_price", cfg)
    df = df[df.cohort >= cfg.burn_in_cohorts]
    n = len(df)
    z, d, k = df.psi.to_numpy(), df.disclosure.to_numpy(), df.capital.to_numpy()
    beta, se, _ = _ols(np.c_[np.ones(n), d, z], k)
    F_proper = (beta[2] / se[2]) ** 2

    ev = Evaluator("capital_purged", cfg)
    for r in df.itertuples():
        ev.update(r.disclosure, r.performance, r.capital, r.psi)
    ratio = ev.first_stage_F() / max(ev.first_stage_F_legacy(), 1e-12)
    assert ratio > 50, "the legacy formula should be far smaller"
    assert F_proper > 0
    print(f"  proper F = {F_proper:.2f}; legacy/proper ratio = 1:{ratio:.0f}")


def test_purge_does_not_use_b_true():
    """The 2SLS estimator must not read the answer it is meant to recover.
    Shifting b_true in the config must not shift the estimate."""
    df = run(42, "capital_purged", "uniform_price", Config())
    ev_a, ev_b = (Evaluator("capital_purged", Config().with_(b_true=1.02)),
                  Evaluator("capital_purged", Config().with_(b_true=5.00)))
    for r in df.itertuples():
        ev_a.update(r.disclosure, r.performance, r.capital, r.psi)
        ev_b.update(r.disclosure, r.performance, r.capital, r.psi)
    assert abs(ev_a.b_hat - ev_b.b_hat) < 1e-9, "the estimator leaked b_true"
    print(f"  b_hat identical under b_true=1.02 and 5.00: {ev_a.b_hat:.6f}")


def test_structural_coefficient_is_one():
    """In y = theta + rho k + eps with d = theta + m, the coefficient of y on d
    holding k fixed is exactly 1.00. The stated calibration b_true = 1.02
    therefore leaves a residual offset of about -0.02 for a perfect estimator.
    This test documents that the offset is a property of the calibration."""
    cfg = Config()
    df = run(42, "capital_purged", "uniform_price", cfg)
    df = df[df.cohort >= cfg.burn_in_cohorts]
    assert abs(df.b_hat.iloc[-1] - 1.0) < 0.5
    print(f"  final b_hat = {df.b_hat.iloc[-1]:.3f} against structural 1.00 "
          f"and stated b_true = {cfg.b_true}")


# --------------------------------------------------------------- audit rule
def test_audit_freezes_when_unidentified():
    """With an impossibly high threshold the evaluator must never learn and
    must fall back to the committed rule."""
    cfg = Config().with_(first_stage_F_threshold=1e12)
    df = run(42, "audited_freeze", "uniform_price", cfg)
    assert np.allclose(df.b_hat, cfg.b_true), "it revised without certification"
    assert df.frozen.iloc[-1]
    print(f"  threshold 1e12: b_hat pinned at {df.b_hat.iloc[-1]:.3f}, "
          f"freeze rate {df.frozen.mean():.2f}")


def test_audit_matches_purge_when_strongly_identified():
    """With a zero threshold the audit rule must behave like plain purging."""
    cfg = Config().with_(first_stage_F_threshold=0.0, min_audit_n=10)
    a = run(42, "audited_freeze", "uniform_price", cfg).b_hat.iloc[-1]
    b = run(42, "capital_purged", "uniform_price", cfg).b_hat.iloc[-1]
    assert abs(a - b) < 1e-9
    print(f"  threshold 0: audited {a:.4f} == purged {b:.4f}")


# ------------------------------------------------------------- reproducibility
def test_run_is_deterministic():
    a = run(42, "naive_history", "uniform_price", Config())
    b = run(42, "naive_history", "uniform_price", Config())
    assert a.equals(b)
    print("  same seed reproduces bit-for-bit")


def test_feedback_decomposition_holds():
    """bias ~ rho * Cov(k,d)/Var(d) + R, the decomposition quoted in Appendix A."""
    cfg = Config()
    df = run(42, "naive_history", "uniform_price", cfg)
    df = df[df.cohort >= cfg.burn_in_cohorts]
    d, y, k = df.disclosure, df.performance, df.capital
    naive_slope = np.cov(d, y, ddof=1)[0, 1] / np.var(d, ddof=1)
    footprint = np.cov(k, d, ddof=1)[0, 1] / np.var(d, ddof=1)
    predicted = 1.0 + cfg.rho_mean * footprint      # structural b is 1.0
    rel = abs(naive_slope - predicted) / abs(naive_slope)
    assert rel < 0.25, f"decomposition off by {rel:.1%}"
    print(f"  naive slope {naive_slope:.3f} vs predicted {predicted:.3f} "
          f"(footprint {footprint:.3f}); gap {rel:.1%}")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for f in fns:
        try:
            print(f"\n{f.__name__}")
            f()
            print("  PASS")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
