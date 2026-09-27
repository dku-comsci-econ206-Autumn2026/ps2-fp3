"""One-command PS2 computational artifact.

Runs the 3 evaluator modes x 2 allocation mechanisms over seeds 42--46 and
writes a fresh-run record plus the metrics named in the Overleaf proposal.
"""
from pathlib import Path
import sys, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import Config
from evaluator import MODES
from simulation import MECHANISMS, run

SEEDS = [42,43,44,45,46]


def summarize(df):
    out=[]
    for (mode, mech), g in df.groupby(["memory","mechanism"]):
        # footprint decomposition: naive slope minus true b.
        d=g.disclosure.to_numpy(); y=g.performance.to_numpy(); k=g.capital.to_numpy()
        slope=np.cov(d,y,ddof=1)[0,1]/np.var(d,ddof=1)
        footprint=np.cov(k,d,ddof=1)[0,1]/np.var(d,ddof=1)
        out.append({
            "memory":mode,"mechanism":mech,
            "mean_manipulation":g.m.mean(),
            "mean_manipulation_cost":g.manipulation_cost.mean(),
            "price_rmse":np.sqrt(np.mean(g.price_error**2)),
            "capital_rho_corr":g.capital.corr(g.rho),
            "feedback_bias":slope-Config().b_true,
            "footprint_cov_k_d_over_var_d":footprint,
            "retail_allocation_share":g.retail_share.mean(),
            "mean_first_stage_F":g.first_stage_F.replace([np.inf],np.nan).mean(),
            "mean_capital":g.capital.mean(),
        })
    return pd.DataFrame(out)


def plot_metric(summary, metric, filename):
    p=summary.pivot(index="memory",columns="mechanism",values=metric)
    ax=p.plot(kind="bar",figsize=(8,5))
    ax.set_ylabel(metric); ax.set_xlabel("Evaluator memory")
    plt.tight_layout(); plt.savefig(Path("results")/filename,dpi=180); plt.close()


def main():
    cfg=Config(); cfg.validate(); frames=[]
    for seed in SEEDS:
        for mode in MODES:
            for mech in MECHANISMS:
                print(f"seed={seed} mode={mode} mechanism={mech}")
                frames.append(run(seed,mode,mech,cfg))
    df=pd.concat(frames,ignore_index=True)
    # Two-cohort burn-in is part of the written computational design. Keep all
    # rows in main_results.csv, but compute headline summaries after burn-in.
    analysis_df=df[df["cohort"] >= cfg.burn_in_cohorts].copy()
    summary=summarize(analysis_df)
    Path("results").mkdir(exist_ok=True)
    df.to_csv("results/main_results.csv",index=False)
    summary.to_csv("results/summary_results.csv",index=False)
    for metric,fn in [("mean_manipulation","manipulation.png"),("price_rmse","price_rmse.png"),("capital_rho_corr","allocation_efficiency.png"),("feedback_bias","feedback_bias.png"),("retail_allocation_share","retail_access.png")]:
        plot_metric(summary,metric,fn)
    record={"seeds":SEEDS,"n_issuers":cfg.n_issuers,"cohorts":cfg.n_cohorts,"issuers_per_cohort":cfg.issuers_per_cohort,"burn_in_cohorts":cfg.burn_in_cohorts,"shares":cfg.shares,"gamma":cfg.gamma,"sigma_theta":cfg.sigma_theta,"sigma_eta":cfg.sigma_eta,"mu0":cfg.mu0,"beta":cfg.beta,"lambda":cfg.lambda_,"sigma_epsilon":cfg.sigma_epsilon,"institutional":cfg.n_institutional,"retail":cfg.n_retail,"sigma_xi_institutional":cfg.sigma_xi_institutional,"sigma_xi_retail":cfg.sigma_xi_retail,"b_true":cfg.b_true,"lambda_P":cfg.lambda_P,"kappa0":cfg.kappa0,"note":"v/rho distributions and lambda_P are not numerically specified in the supplied Overleaf; explicit implementation values are recorded in model.py."}
    Path("results/fresh_run_record.json").write_text(json.dumps(record,indent=2))
    print("\nSUMMARY\n",summary.to_string(index=False))

if __name__=="__main__": main()
