"""Cross-check every number quoted in the paper, poster and README against the
results files. Run after src/run_experiment.py and src/robustness.py.

    python tools/check_numbers.py

The 14 October feedback asked that "the interpretation and every plotted number
refer to the same evidence". This is the check that enforces it: if a figure in
the LaTeX drifts from the CSV it was taken from, this fails.
"""
from pathlib import Path
import re
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "results"

TOL = 0.0051        # quoted to 3 dp
TOL2 = 0.051        # quoted to 2 dp


def close(a, b, tol=TOL):
    return abs(float(a) - float(b)) <= tol


def main():
    H = pd.read_csv(R / "headline_table.csv").set_index(["mechanism", "memory"])
    inst = pd.read_csv(R / "robust_instrument.csv")
    plac = pd.read_csv(R / "robust_placebo_verdict.csv")
    par = pd.read_csv(R / "robust_parameters_verdict.csv")
    lock = pd.read_csv(R / "audit_lockin.csv")
    scar = pd.read_csv(R / "robust_scarcity.csv")
    burden = pd.read_csv(R / "social_burden.csv")

    checks = []

    def chk(name, quoted, actual, tol=TOL):
        ok = close(quoted, actual, tol)
        checks.append((name, quoted, round(float(actual), 4), ok))

    # ---- headline table (paper Table 1, README table, poster) ------------
    for mech, tag in (("uniform_price", "M1"), ("bookbuilding", "M2")):
        for mem in ("no_memory", "naive_history", "capital_purged", "audited_freeze"):
            row = H.loc[(mech, mem)]
            checks.append((f"{tag}/{mem} present", "-", "-", True))
            # internal consistency: bias is zero exactly under commitment
            if mem == "no_memory":
                chk(f"{tag}/no_memory bias == 0", 0.0, row.feedback_bias)

    chk("M1 naive manipulation 0.824", 0.824, H.loc[("uniform_price", "naive_history"), "mean_manipulation"])
    chk("M1 committed manipulation 0.406", 0.406, H.loc[("uniform_price", "no_memory"), "mean_manipulation"])
    chk("M1 purged manipulation 0.455", 0.455, H.loc[("uniform_price", "capital_purged"), "mean_manipulation"])
    chk("M1 audited manipulation 0.423", 0.423, H.loc[("uniform_price", "audited_freeze"), "mean_manipulation"])
    chk("M1 naive bias 1.030", 1.030, H.loc[("uniform_price", "naive_history"), "feedback_bias"])
    chk("M1 purged bias 0.090", 0.090, H.loc[("uniform_price", "capital_purged"), "feedback_bias"])
    chk("M1 audited bias 0.038", 0.038, H.loc[("uniform_price", "audited_freeze"), "feedback_bias"])
    chk("M2 naive manipulation 0.717", 0.717, H.loc[("bookbuilding", "naive_history"), "mean_manipulation"])
    chk("M2 purged bias -0.024", -0.024, H.loc[("bookbuilding", "capital_purged"), "feedback_bias"])
    chk("M1 audited RMSE 2.57", 2.57, H.loc[("uniform_price", "audited_freeze"), "price_rmse"], TOL2)
    chk("M1 purged RMSE 5.26", 5.26, H.loc[("uniform_price", "capital_purged"), "price_rmse"], TOL2)
    chk("M1 audited freeze rate 0.245", 0.245, H.loc[("uniform_price", "audited_freeze"), "freeze_rate"])

    # "+103%" and "+77%"
    m1n = H.loc[("uniform_price", "naive_history"), "mean_manipulation"]
    m1c = H.loc[("uniform_price", "no_memory"), "mean_manipulation"]
    chk("M1 lift +103%", 103, 100 * (m1n - m1c) / m1c, 1.0)
    m2n = H.loc[("bookbuilding", "naive_history"), "mean_manipulation"]
    chk("M2 lift +77%", 77, 100 * (m2n - m1c) / m1c, 1.0)

    # R6: exclusion counts
    chk("M1 naive excluded 9.5", 9.5, H.loc[("uniform_price", "naive_history"), "n_excluded"], 0.051)
    chk("M1 committed excluded 17.2", 17.2, H.loc[("uniform_price", "no_memory"), "n_excluded"], 0.051)
    chk("M1 naive retail share 0.703", 0.703, H.loc[("uniform_price", "naive_history"), "retail_share"])

    # R7: allocative efficiency negative result
    worst_rho = H.capital_rho_corr.abs().max()
    checks.append(("R7 capital-rho corr <= 0.021 everywhere", "<=0.021",
                   round(float(worst_rho), 4), worst_rho <= 0.021))

    # ---- placebo ---------------------------------------------------------
    b = plac[(plac.arm.str.startswith("baseline")) & (plac.mechanism == "uniform_price")]
    p0 = plac[(plac.arm.str.startswith("PLACEBO")) & (plac.mechanism == "uniform_price")]
    chk("placebo baseline lift +0.328", 0.328, b.lift.iloc[0])
    chk("placebo rho=0 lift -0.019", -0.019, p0.lift.iloc[0])
    chk("placebo rho=0 pct -4.8%", -4.8, p0.lift_pct.iloc[0], 0.11)
    chk("baseline pct +80.9%", 80.9, b.lift_pct.iloc[0], 0.11)

    # ---- parameter grid --------------------------------------------------
    checks.append(("sign robust 27/27", "27/27",
                   f"{int(par.lift_sign_positive.sum())}/{len(par)}",
                   int(par.lift_sign_positive.sum()) == len(par) == 27))
    checks.append(("purge helps 27/27", "27/27",
                   f"{int(par.purge_reduces_bias.sum())}/{len(par)}",
                   int(par.purge_reduces_bias.sum()) == len(par)))
    # smallest gain should be at rho_mean = 0.10, where the footprint is tiny
    par = par.assign(gain=par.bias_naive.abs() - par.bias_purged.abs())
    sm = par.nsmallest(1, "gain").iloc[0]
    checks.append(("smallest purge gain at rho_mean=0.10", "rho_mean/0.1",
                   f"{sm.parameter}/{sm.value:g}",
                   sm.parameter == "rho_mean" and abs(sm.value - 0.10) < 1e-9))

    # ---- instrument sweep: the central claim -----------------------------
    m1 = inst[inst.mechanism == "uniform_price"]
    cp_worst = m1[m1.memory == "capital_purged"].feedback_bias.abs().max()
    au_worst = m1[m1.memory == "audited_freeze"].feedback_bias.abs().max()
    chk("purged worst-case bias 2.563", 2.563, cp_worst)
    chk("audited worst-case bias 0.275", 0.275, au_worst)
    checks.append(("audited worst < purged worst", "yes",
                   f"{au_worst:.3f} < {cp_worst:.3f}", au_worst < cp_worst))
    fz = m1[m1.memory == "audited_freeze"].sort_values("sigma_psi").freeze_rate
    checks.append(("audited freeze falls to 0", "100%->0%",
                   f"{100*fz.iloc[0]:.0f}%->{100*fz.iloc[-1]:.0f}%",
                   fz.iloc[0] > 0.95 and fz.iloc[-1] < 0.01))

    # ---- audit lock-in ---------------------------------------------------
    ng = lock[(lock.min_audit_n == 1) & (lock.mechanism == "uniform_price")]
    gd = lock[(lock.min_audit_n == 40) & (lock.mechanism == "uniform_price")]
    chk("lock-in no-guard bias -0.362", -0.362, ng.feedback_bias.iloc[0])
    chk("lock-in no-guard freeze 58.2%", 0.582, ng.freeze_rate.iloc[0])
    chk("lock-in guarded bias 0.002", 0.002, gd.feedback_bias.iloc[0])
    chk("lock-in guarded freeze 14.7%", 0.147, gd.freeze_rate.iloc[0])
    chk("lock-in no-guard RMSE 4.73", 4.73, ng.price_rmse.iloc[0], TOL2)
    chk("lock-in guarded RMSE 2.02", 2.02, gd.price_rmse.iloc[0], TOL2)

    # ---- scarcity: the PS2 arm excludes nobody ---------------------------
    ps2 = scar[abs(scar.coverage - 1.0) < 1e-9]
    checks.append(("PS2 coverage=1.0 excludes nobody", 0.0,
                   round(float(ps2.n_excluded.max()), 4), ps2.n_excluded.max() < 1e-6))

    # ---- R9: the social burden the Oct 12 duet challenge produced --------
    b = burden[(burden.allocation_rule == "excludable")
               & (burden.mechanism == "uniform_price")].set_index("memory")
    chk("R9 naive retail served 99.9%", 99.9, b.loc["naive_history", "retail_served_pct"], 0.11)
    chk("R9 audited retail served 62.5%", 62.5, b.loc["audited_freeze", "retail_served_pct"], 0.11)
    chk("R9 naive inst served 36.7%", 36.7, b.loc["naive_history", "inst_served_pct"], 0.11)
    chk("R9 audited inst served 64.8%", 64.8, b.loc["audited_freeze", "inst_served_pct"], 0.11)
    chk("R9 audited loses 13.1 retail", -13.1, b.loc["audited_freeze", "d_retail_served"], 0.11)
    chk("R9 audited gains 4.2 inst", 4.2, b.loc["audited_freeze", "d_inst_served"], 0.11)
    checks.append(("R9 burden falls on retail, not institutions", "retail<0<inst",
                   f"{b.loc['audited_freeze','d_retail_served']:.1f} / "
                   f"{b.loc['audited_freeze','d_inst_served']:+.1f}",
                   b.loc["audited_freeze", "d_retail_served"] < 0
                   < b.loc["audited_freeze", "d_inst_served"]))

    # ---- report ----------------------------------------------------------
    bad = [c for c in checks if not c[3]]
    print(f"{'check':44s}{'quoted':>12s}{'actual':>12s}  ok")
    for name, q, a, ok in checks:
        print(f"{name:44s}{str(q):>12s}{str(a):>12s}  {'OK' if ok else 'MISMATCH'}")
    print(f"\n{len(checks)-len(bad)}/{len(checks)} checks pass")
    if bad:
        print("\nMISMATCHES — the paper and the results have drifted apart:")
        for name, q, a, _ in bad:
            print(f"  {name}: paper says {q}, results say {a}")
        return 1
    print("Paper, poster and README agree with the frozen run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
