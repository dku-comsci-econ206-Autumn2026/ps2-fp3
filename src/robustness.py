"""Robustness and falsification suite.

Each block answers a specific challenge that was put to the team in writing.

  A. PLACEBO (rho = 0). Team self-challenge #1: "the 0.408 -> 1.367 jump comes
     from 200 synthetic issuers; if it is a model artifact our story collapses."
     If the jump is a genuine capital-feedback effect it MUST disappear when
     capital has no effect on performance. If it survives rho = 0, the effect is
     an artifact and we abandon the claim.

  B. INSTRUMENT STRENGTH SWEEP (sigma_psi). Team self-challenge #2: "if a
     stronger allocation shock still gives a low F, our correction does not
     work." Sweeps the greenshoe shock and reports first-stage F against bias
     reduction. This is the test that would make us abandon the purged design.

  C. PARAMETER GRID. Zhengjun He / Yichen Shen: "test alternative model
     assumptions and parameter settings." Varies gamma, beta, rho_mean,
     sigma_theta, sigma_eta one at a time and reports whether the SIGN of the
     naive-history effect survives.

  D. SCARCITY SWEEP. Instructor: the offering must actually be scarce. Varies
     the coverage ratio from 1.0 (no exclusion, the PS2 case) upward.

  E. AUDIT LOCK-IN. Demonstrates the failure mode that motivated min_audit_n:
     without the thick-sample guard the audit certifies on noise and freezes
     permanently at a wrong parameter.

Run:  python src/robustness.py            (uses 10 seeds)
      python src/robustness.py --quick    (3 seeds)
"""
from pathlib import Path
import sys, json, argparse

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import Config                       # noqa: E402
from simulation import run                     # noqa: E402
from run_experiment import pooled_first_stage_F, ci95   # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"


def cell(cfg, seeds, mode, mech):
    """Run one (mode, mechanism) cell and return post-burn-in per-seed stats."""
    rows = []
    for s in seeds:
        df = run(s, mode, mech, cfg)
        df = df[df.cohort >= cfg.burn_in_cohorts]
        rows.append({
            "seed": s,
            "mean_manipulation": df.m.mean(),
            "price_rmse": float(np.sqrt(np.mean(df.price_error ** 2))),
            "final_b_hat": df.b_hat.iloc[-1],
            "feedback_bias": df.b_hat.iloc[-1] - cfg.b_true,
            "first_stage_F": pooled_first_stage_F(df),
            "freeze_rate": df.frozen.mean(),
            "retail_share": df.retail_share.mean(),
            "n_excluded": df.n_excluded.mean(),
        })
    return pd.DataFrame(rows)


def agg(cfg, seeds, mode, mech, **label):
    d = cell(cfg, seeds, mode, mech)
    out = dict(label, memory=mode, mechanism=mech, n_seeds=len(d))
    for c in ("mean_manipulation", "price_rmse", "feedback_bias",
              "first_stage_F", "freeze_rate", "retail_share", "n_excluded"):
        m, h = ci95(d[c])
        out[c], out[c + "_ci95"] = m, h
    return out


# ---------------------------------------------------------------- A. placebo
def placebo(base, seeds):
    """rho = 0: capital cannot affect performance, so the feedback channel is
    switched off at the source. The naive-history effect must vanish."""
    out = []
    for rho_mean, rho_sd, tag in ((base.rho_mean, base.rho_sd, "baseline rho>0"),
                                  (0.0, 0.0, "PLACEBO rho=0")):
        cfg = base.with_(rho_mean=rho_mean, rho_sd=rho_sd)
        for mech in ("uniform_price", "bookbuilding"):
            for mode in ("no_memory", "naive_history", "capital_purged"):
                out.append(agg(cfg, seeds, mode, mech, arm=tag, rho_mean=rho_mean))
    df = pd.DataFrame(out)
    # verdict: manipulation lift of naive_history over no_memory, per arm
    v = []
    for (arm, mech), g in df.groupby(["arm", "mechanism"]):
        nm = g[g.memory == "no_memory"].mean_manipulation.iloc[0]
        nh = g[g.memory == "naive_history"].mean_manipulation.iloc[0]
        v.append({"arm": arm, "mechanism": mech, "no_memory": nm,
                  "naive_history": nh, "lift": nh - nm,
                  "lift_pct": 100 * (nh - nm) / nm if nm else np.nan})
    return df, pd.DataFrame(v)


# ------------------------------------------------- B. instrument strength
def instrument_sweep(base, seeds):
    grid = [0.01, 0.02, 0.05, 0.08, 0.15, 0.25, 0.40]
    out = []
    for sd in grid:
        cfg = base.with_(psi_sd_uniform=sd, psi_sd_bookbuilding=sd)
        for mech in ("uniform_price", "bookbuilding"):
            for mode in ("naive_history", "capital_purged", "audited_freeze"):
                out.append(agg(cfg, seeds, mode, mech, sigma_psi=sd))
    return pd.DataFrame(out)


# ------------------------------------------------------- C. parameter grid
def parameter_grid(base, seeds):
    sweeps = {
        "gamma":        [0.002, 0.004, 0.006, 0.010, 0.015],
        "beta":         [0.30, 0.45, 0.60, 0.75, 0.90],
        "rho_mean":     [0.10, 0.25, 0.50, 0.75, 1.00],
        "sigma_theta":  [0.50, 1.00, 1.50, 2.00],
        "sigma_eta":    [0.25, 0.50, 1.00, 1.50],
        "sigma_epsilon":[0.40, 0.80, 1.60, 3.20],
    }
    out = []
    for name, values in sweeps.items():
        for val in values:
            cfg = base.with_(**{name: val})
            for mode in ("no_memory", "naive_history", "capital_purged"):
                out.append(agg(cfg, seeds, mode, "uniform_price",
                               parameter=name, value=val))
    df = pd.DataFrame(out)
    v = []
    for (p, val), g in df.groupby(["parameter", "value"]):
        nm = g[g.memory == "no_memory"].mean_manipulation.iloc[0]
        nh = g[g.memory == "naive_history"].mean_manipulation.iloc[0]
        cp = g[g.memory == "capital_purged"].mean_manipulation.iloc[0]
        bn = g[g.memory == "naive_history"].feedback_bias.iloc[0]
        bc = g[g.memory == "capital_purged"].feedback_bias.iloc[0]
        v.append({"parameter": p, "value": val,
                  "manip_lift": nh - nm, "lift_sign_positive": bool(nh > nm),
                  "bias_naive": bn, "bias_purged": bc,
                  "purge_reduces_bias": bool(abs(bc) < abs(bn)),
                  "manip_purged": cp})
    return df, pd.DataFrame(v)


# ----------------------------------------------------------- D. scarcity
def scarcity_sweep(base, seeds):
    # (q_inst, q_retail) -> coverage ratio against the 100-share offering.
    # Coverage must exceed 1.0 for exclusion to be possible at all; the
    # coverage = 1.0 case is the PS2 fixed-rationing arm, appended below.
    grid = [(2.2, 2.0), (3.0, 2.0), (4.0, 2.0), (6.0, 2.0), (8.0, 3.0), (12.0, 4.0)]
    out = []
    for qi, qr in grid:
        cfg = base.with_(q_institutional=qi, q_retail=qr)
        for mode in ("no_memory", "naive_history", "capital_purged"):
            out.append(agg(cfg, seeds, mode, "uniform_price",
                           q_institutional=qi, q_retail=qr,
                           coverage=cfg.coverage_ratio))
    # the PS2 arm: nobody is ever excluded
    cfg0 = base.with_(allocation_rule="fixed_rationing")
    for mode in ("no_memory", "naive_history", "capital_purged"):
        out.append(agg(cfg0, seeds, mode, "uniform_price",
                       q_institutional=np.nan, q_retail=np.nan, coverage=1.0))
    return pd.DataFrame(out)


# --------------------------------------------------------- E. audit lock-in
def audit_lockin(base, seeds):
    """Without the thick-sample guard the audit certifies on noise and locks."""
    out = []
    for n_min, tag in ((1, "no guard (min_audit_n=1)"),
                       (base.min_audit_n, f"guarded (min_audit_n={base.min_audit_n})")):
        cfg = base.with_(min_audit_n=n_min)
        for mech in ("uniform_price", "bookbuilding"):
            d = cell(cfg, seeds, "audited_freeze", mech)
            m, h = ci95(d.feedback_bias)
            fm, fh = ci95(d.freeze_rate)
            rm, rh = ci95(d.price_rmse)
            out.append({"arm": tag, "min_audit_n": n_min, "mechanism": mech,
                        "feedback_bias": m, "feedback_bias_ci95": h,
                        "freeze_rate": fm, "freeze_rate_ci95": fh,
                        "price_rmse": rm, "price_rmse_ci95": rh,
                        "final_b_hat_spread": float(d.final_b_hat.std(ddof=1))})
    return pd.DataFrame(out)


# ------------------------------------------------------------------- driver
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    seeds = [42, 43, 44] if args.quick else list(range(42, 52))

    base = Config(); base.validate()
    RESULTS.mkdir(exist_ok=True)
    fmt = lambda x: f"{x:8.3f}"

    print("\n### A. PLACEBO: rho = 0 switches the feedback channel off")
    pl, pl_v = placebo(base, seeds)
    pl.to_csv(RESULTS / "robust_placebo.csv", index=False)
    pl_v.to_csv(RESULTS / "robust_placebo_verdict.csv", index=False)
    print(pl_v.to_string(index=False, float_format=fmt))

    print("\n### B. INSTRUMENT STRENGTH SWEEP")
    isw = instrument_sweep(base, seeds)
    isw.to_csv(RESULTS / "robust_instrument.csv", index=False)
    print(isw[isw.mechanism == "uniform_price"][
        ["sigma_psi", "memory", "first_stage_F", "feedback_bias",
         "mean_manipulation", "freeze_rate"]].to_string(index=False, float_format=fmt))

    print("\n### C. PARAMETER GRID (sign robustness, M1)")
    pg, pg_v = parameter_grid(base, seeds)
    pg.to_csv(RESULTS / "robust_parameters.csv", index=False)
    pg_v.to_csv(RESULTS / "robust_parameters_verdict.csv", index=False)
    print(pg_v.to_string(index=False, float_format=fmt))
    print(f"\n  sign of manipulation lift positive in "
          f"{pg_v.lift_sign_positive.sum()}/{len(pg_v)} settings")
    print(f"  purging reduces |bias| in "
          f"{pg_v.purge_reduces_bias.sum()}/{len(pg_v)} settings")

    print("\n### D. SCARCITY SWEEP")
    sc = scarcity_sweep(base, seeds)
    sc.to_csv(RESULTS / "robust_scarcity.csv", index=False)
    print(sc[["coverage", "memory", "n_excluded", "retail_share",
              "mean_manipulation", "feedback_bias"]].to_string(
        index=False, float_format=fmt))

    print("\n### E. AUDIT LOCK-IN")
    lk = audit_lockin(base, seeds)
    lk.to_csv(RESULTS / "audit_lockin.csv", index=False)
    print(lk.to_string(index=False, float_format=fmt))

    summary = {
        "seeds": seeds,
        "placebo_lift_baseline_M1": float(
            pl_v[(pl_v.arm.str.startswith("baseline")) &
                 (pl_v.mechanism == "uniform_price")].lift.iloc[0]),
        "placebo_lift_rho0_M1": float(
            pl_v[(pl_v.arm.str.startswith("PLACEBO")) &
                 (pl_v.mechanism == "uniform_price")].lift.iloc[0]),
        "sign_robust_settings": int(pg_v.lift_sign_positive.sum()),
        "total_settings": int(len(pg_v)),
        "purge_helps_settings": int(pg_v.purge_reduces_bias.sum()),
    }
    (RESULTS / "robustness_summary.json").write_text(json.dumps(summary, indent=2))
    print("\nWrote", RESULTS)


if __name__ == "__main__":
    main()
