"""One-command final artifact.

    python src/run_experiment.py            # headline grid, 20 seeds
    python src/run_experiment.py --quick    # 5 seeds, for a fast check

Writes to results/:
    main_results.csv        every issuer, every treatment
    summary_results.csv     cell means with 95% CIs across seeds
    headline_table.csv      the numbers quoted in the paper and on the poster
    bid_trace.json          one bid traced through quantity/price/proceeds
    fresh_run_record.json   parameters, versions, hashes, timestamp
"""
from pathlib import Path
import sys, json, hashlib, platform, argparse, datetime

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import Config, draw_issuer_types                     # noqa: E402
from evaluator import MODES, _ols                               # noqa: E402
from simulation import MECHANISMS, run                          # noqa: E402
from auction import posterior_bids, investor_signals, trace_one_bid  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
SEEDS = list(range(42, 62))          # 42..61, twenty independent markets
QUICK_SEEDS = [42, 43, 44, 45, 46]   # the PS2 seeds, for continuity
ALLOCATION_RULES = ("excludable", "fixed_rationing")


# --------------------------------------------------------------------------
def pooled_first_stage_F(g):
    """F on psi in  k ~ 1 + d + psi, pooled over the post-burn-in sample."""
    n = len(g)
    if n < 10 or g.psi.var() < 1e-12:
        return np.nan
    X = np.c_[np.ones(n), g.disclosure.to_numpy(), g.psi.to_numpy()]
    beta, se, _ = _ols(X, g.capital.to_numpy())
    if beta is None or se is None or se[2] <= 0:
        return np.nan
    return float((beta[2] / se[2]) ** 2)


def ci95(series):
    """Mean and half-width of a 95% CI across seeds."""
    a = np.asarray(series, dtype=float)
    a = a[np.isfinite(a)]
    if len(a) < 2:
        return (float(a.mean()) if len(a) else np.nan), np.nan
    return float(a.mean()), float(1.96 * a.std(ddof=1) / np.sqrt(len(a)))


def summarize(df):
    """Per-cell summary. Uncertainty is computed ACROSS SEEDS, which is the
    unit of independent replication -- not across issuers within a seed, which
    are serially dependent through the evaluator's memory."""
    out = []
    keys = ["allocation_rule", "mechanism", "memory"]
    for cell, g in df.groupby(keys):
        per_seed = g.groupby("seed").agg(
            mean_manipulation=("m", "mean"),
            mean_manipulation_cost=("manipulation_cost", "mean"),
            price_rmse=("price_error", lambda s: float(np.sqrt(np.mean(s ** 2)))),
            final_b_hat=("b_hat", "last"),
            retail_share=("retail_share", "mean"),
            n_excluded=("n_excluded", "mean"),
            freeze_rate=("frozen", "mean"),
            mean_capital=("capital", "mean"),
        )
        # allocative efficiency: does capital go to high-rho firms?
        per_seed["capital_rho_corr"] = pd.Series(
            {s: sub.capital.corr(sub.rho) for s, sub in g.groupby("seed")})
        # Counterfactual: the slope a NAIVE learner would have read off this
        # path. Under no_memory the published rule never moves, so its
        # feedback bias is zero by construction; this column shows how much
        # bias commitment avoided rather than how much it incurred.
        per_seed["naive_slope_counterfactual"] = pd.Series(
            {s: (np.cov(sub.disclosure, sub.performance, ddof=1)[0, 1]
                 / np.var(sub.disclosure, ddof=1)) - Config().b_true
             for s, sub in g.groupby("seed")})
        per_seed["feedback_bias"] = per_seed.final_b_hat - Config().b_true

        row = dict(zip(keys, cell))
        for col in per_seed.columns:
            mean, half = ci95(per_seed[col])
            row[col] = mean
            row[col + "_ci95"] = half
        row["first_stage_F_pooled"] = pooled_first_stage_F(g)
        row["first_stage_F_legacy_mean"] = (
            row["first_stage_F_pooled"] / max(1, len(g) - 3))
        row["n_seeds"] = per_seed.shape[0]
        row["n_obs"] = len(g)
        out.append(row)
    return pd.DataFrame(out).sort_values(keys).reset_index(drop=True)


# --------------------------------------------------------------------------
def bid_trace(cfg):
    """Instructor request: trace ONE bid through quantity, price, proceeds and
    the resulting training label, to demonstrate the bid is consequential."""
    rng = np.random.default_rng(7)
    theta, v, rho = draw_issuer_types(rng, cfg)
    x = investor_signals(theta, rng, cfg)
    bids = posterior_bids((1 - cfg.beta) * cfg.mu0 + cfg.beta * cfg.b_true * theta,
                          x, cfg, 0.4)
    # pick an investor sitting near the clearing margin
    rank = np.argsort(-bids)
    marginal_investor = int(rank[min(len(rank) - 1, 24)])
    out = {}
    for rule in ALLOCATION_RULES:
        c = cfg.with_(allocation_rule=rule)
        t = trace_one_bid(bids, c, rng_seed=11, investor=marginal_investor, delta=1.0)
        for v_ in t.values():
            v_["training_label_y"] = float(theta + rho * v_["proceeds_k"])
        out[rule] = t
    out["_meta"] = {"investor_index": marginal_investor,
                    "is_retail": marginal_investor >= cfg.n_institutional,
                    "theta": float(theta), "rho": float(rho),
                    "note": "training_label_y = theta + rho*k, noise suppressed "
                            "so the mechanical effect of the bid is visible."}
    return out


def social_burden(df):
    """Who bears the cost of making the evaluator strategy-robust?

    Added after the October 12 duet challenge from Team FP4, which raised
    Milli et al. (2019). That paper proves that any gain in institutional
    utility from strategy-robustness comes with a matching "social burden" on
    the classified population, falling hardest on the disadvantaged. We had not
    measured it. These columns are the test: the share of each investor class
    that receives any allocation at all, by evaluator rule.
    """
    out = []
    for (rule, mech, mem), g in df.groupby(["allocation_rule", "mechanism", "memory"]):
        per_seed = g.groupby("seed").agg(
            retail_served=("retail_investors_served", "mean"),
            n_served=("n_served", "mean"),
            retail_share=("retail_share", "mean"))
        per_seed["inst_served"] = per_seed.n_served - per_seed.retail_served
        n_ret = Config().n_retail
        n_ins = Config().n_institutional
        row = {"allocation_rule": rule, "mechanism": mech, "memory": mem}
        for col, denom in (("retail_served", n_ret), ("inst_served", n_ins)):
            m, h = ci95(per_seed[col])
            row[col] = m
            row[col + "_pct"] = 100 * m / denom
            row[col + "_ci95"] = h
        row["retail_share"], row["retail_share_ci95"] = ci95(per_seed.retail_share)
        out.append(row)
    res = pd.DataFrame(out)
    # burden relative to the unsafeguarded rule, within each (rule, mechanism)
    deltas = []
    for (rule, mech), g in res.groupby(["allocation_rule", "mechanism"]):
        base = g[g.memory == "naive_history"].iloc[0]
        for _, r in g.iterrows():
            deltas.append({
                "allocation_rule": rule, "mechanism": mech, "memory": r.memory,
                "d_retail_served": r.retail_served - base.retail_served,
                "d_inst_served": r.inst_served - base.inst_served,
                "d_retail_served_pct": r.retail_served_pct - base.retail_served_pct,
                "d_inst_served_pct": r.inst_served_pct - base.inst_served_pct})
    return res.merge(pd.DataFrame(deltas),
                     on=["allocation_rule", "mechanism", "memory"])


def file_hashes():
    h = {}
    for p in sorted((ROOT / "src").glob("*.py")):
        h[f"src/{p.name}"] = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    return h


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="5 seeds instead of 20")
    args = ap.parse_args()
    seeds = QUICK_SEEDS if args.quick else SEEDS

    base = Config(); base.validate()
    RESULTS.mkdir(exist_ok=True)

    frames = []
    total = len(ALLOCATION_RULES) * len(seeds) * len(MODES) * len(MECHANISMS)
    i = 0
    for rule in ALLOCATION_RULES:
        cfg = base.with_(allocation_rule=rule)
        for seed in seeds:
            for mode in MODES:
                for mech in MECHANISMS:
                    i += 1
                    print(f"[{i:4d}/{total}] rule={rule:16s} seed={seed} "
                          f"mode={mode:15s} mech={mech}", flush=True)
                    frames.append(run(seed, mode, mech, cfg))

    df = pd.concat(frames, ignore_index=True)
    analysis = df[df.cohort >= base.burn_in_cohorts].copy()
    summary = summarize(analysis)

    df.to_csv(RESULTS / "main_results.csv", index=False)
    summary.to_csv(RESULTS / "summary_results.csv", index=False)

    headline = summary[summary.allocation_rule == "excludable"][
        ["mechanism", "memory", "mean_manipulation", "mean_manipulation_ci95",
         "price_rmse", "price_rmse_ci95", "feedback_bias", "feedback_bias_ci95",
         "first_stage_F_pooled", "retail_share", "n_excluded", "freeze_rate",
         "naive_slope_counterfactual",
         "capital_rho_corr"]]
    headline.to_csv(RESULTS / "headline_table.csv", index=False)

    (RESULTS / "bid_trace.json").write_text(json.dumps(bid_trace(base), indent=2))
    social_burden(analysis).to_csv(RESULTS / "social_burden.csv", index=False)

    record = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "seeds": seeds,
        "allocation_rules": list(ALLOCATION_RULES),
        "memory_modes": list(MODES),
        "mechanisms": list(MECHANISMS),
        "config": {k: (v if not isinstance(v, (np.floating, np.integer)) else v.item())
                   for k, v in base.__dict__.items()},
        "derived": {"total_demand": base.total_demand,
                    "coverage_ratio": base.coverage_ratio,
                    "n_investors": base.n_investors},
        "python": platform.python_version(),
        "numpy": np.__version__, "pandas": pd.__version__,
        "platform": platform.platform(),
        "source_sha256_16": file_hashes(),
        "rows": len(df),
        "notes": [
            "Uncertainty is computed across seeds, the unit of independent replication.",
            "first_stage_F_pooled is the textbook t^2 on psi in k ~ 1 + d + psi.",
            "first_stage_F_legacy_mean reproduces the PS2 normalisation bug for audit.",
            "All data are synthetic. No claim is made about any real issuer.",
        ],
    }
    (RESULTS / "fresh_run_record.json").write_text(json.dumps(record, indent=2))

    pd.set_option("display.width", 200, "display.max_columns", 50)
    print("\n================ HEADLINE (excludable demand) ================")
    print(headline.to_string(index=False, float_format=lambda x: f"{x:9.3f}"))
    print("\nWrote", RESULTS)


if __name__ == "__main__":
    main()
