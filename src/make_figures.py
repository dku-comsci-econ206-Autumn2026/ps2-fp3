"""Figures for the paper and the A0 poster.

    python src/make_figures.py        # after run_experiment.py and robustness.py

Palette: course Strategic-Thinking blue #315EFB and Interdisciplinary violet
#9254F5 are retained from the course materials; orange and aqua are snapped to
validated steps. The four-slot categorical set passes the lightness band,
chroma floor, adjacent CVD separation (worst dE 9.2, deutan) and the
normal-vision floor (worst dE 27.6) on a light surface. Aqua sits below 3:1
contrast, so every bar carries a visible direct label -- the relief rule.

Mechanism is encoded as a FACET, never as a second colour axis, so colour
always means "which evaluator rule" and nothing else.
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
FIGS = ROOT / "figures"
FIGS.mkdir(exist_ok=True)

MODE_COLOR = {
    "no_memory":      "#315EFB",   # committed rule
    "naive_history":  "#EB6834",   # the failure mode
    "capital_purged": "#1BAF7A",   # the correction
    "audited_freeze": "#9254F5",   # the accountability rule
}
MODE_LABEL = {
    "no_memory": "No memory\n(committed)",
    "naive_history": "Naive history",
    "capital_purged": "Capital-purged",
    "audited_freeze": "Audited freeze",
}
MODE_SHORT = {"no_memory": "No memory", "naive_history": "Naive",
              "capital_purged": "Purged", "audited_freeze": "Audited"}
MODE_ORDER = list(MODE_COLOR)
MECH_LABEL = {"uniform_price": "M1 uniform-price auction",
              "bookbuilding": "M2 bookbuilding"}

INK, MUTED, GRID = "#18324A", "#5A6B7D", "#DFE4EA"

mpl.rcParams.update({
    "figure.dpi": 200, "savefig.dpi": 200, "savefig.bbox": "tight",
    "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "axes.edgecolor": GRID, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": GRID, "grid.linewidth": 0.6, "legend.frameon": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
})


def _style(ax, ylabel=None, title=None):
    ax.yaxis.grid(True, linewidth=0.6)
    ax.set_axisbelow(True)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, color=INK, pad=8)
    return ax


# ------------------------------------------------------------------ figure 1
def fig_manipulation(summary):
    """Headline: naive history roughly doubles strategic disclosure; the
    correction and the audit rule return it to the committed baseline."""
    d = summary[summary.allocation_rule == "excludable"]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.1), sharey=True)
    for ax, mech in zip(axes, ("uniform_price", "bookbuilding")):
        g = d[d.mechanism == mech].set_index("memory")
        base = g.loc["no_memory", "mean_manipulation"]
        ax.axhline(base, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=1)
        if mech == "bookbuilding":
            ax.text(3.45, base - 0.06, "committed baseline", fontsize=7,
                    color=MUTED, va="top", ha="right")
        for i, m in enumerate(MODE_ORDER):
            v, e = g.loc[m, "mean_manipulation"], g.loc[m, "mean_manipulation_ci95"]
            ax.bar(i, v, 0.62, color=MODE_COLOR[m], zorder=2,
                   label=MODE_LABEL[m].replace("\n", " ")
                   if mech == "uniform_price" else None)
            ax.errorbar(i, v, yerr=e, fmt="none", ecolor=INK, elinewidth=1.1,
                        capsize=3, zorder=3)
            ax.text(i, v + e + 0.035, f"{v:.3f}", ha="center", fontsize=7.5,
                    color=INK, fontweight="bold")
        ax.set_xticks(range(4))
        ax.set_xticklabels([MODE_SHORT[m] for m in MODE_ORDER], fontsize=7.5)
        ax.set_xlim(-0.6, 3.6)
        _style(ax, title=MECH_LABEL[mech])
    axes[0].set_ylabel("Mean manipulation  $\\bar m$")
    axes[0].set_ylim(0, 1.05)
    fig.legend(loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.17), fontsize=7.5)
    fig.suptitle("Evaluator memory and strategic disclosure "
                 "(20 seeds, bars show 95% CI across seeds)",
                 fontsize=10, color=INK, y=1.04)
    fig.savefig(FIGS / "fig1_manipulation.png")
    plt.close(fig)


# ------------------------------------------------------------------ figure 2
def fig_instrument(inst):
    """The discriminating test, and the paper's central result.

    Below the Staiger-Stock threshold the capital-purged estimator is not
    merely biased, it is unstable (bias swings to -2.56). The audited rule
    refuses to certify there, holds the committed parameter, and resumes
    automatically as identification arrives -- so its worst case is an order
    of magnitude smaller at no cost once the instrument is strong.
    """
    d = inst[inst.mechanism == "uniform_price"]
    SUB = "#FDF0E8"          # sub-threshold region
    # where does the purged first stage cross F = 10?
    cp = d[d.memory == "capital_purged"].sort_values("sigma_psi")
    below = cp[cp.first_stage_F < 10].sigma_psi
    above = cp[cp.first_stage_F >= 10].sigma_psi
    xcross = ((float(below.max()) + float(above.min())) / 2
              if len(below) and len(above) else 0.0)

    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.9))
    series = ("naive_history", "capital_purged", "audited_freeze")

    def shade(ax):
        ax.axvspan(0, xcross, color=SUB, zorder=0)

    ax = axes[0]
    shade(ax)
    for m in series:
        g = d[d.memory == m].sort_values("sigma_psi")
        ax.plot(g.sigma_psi, g.first_stage_F, "-o", color=MODE_COLOR[m], lw=2,
                ms=4.5, label=MODE_LABEL[m].replace("\n", " "), zorder=3)
    ax.axhline(10, color="#C2410C", lw=1.3, ls=(0, (4, 3)), zorder=2)
    ax.text(0.40, 13, "F = 10", fontsize=7, color="#C2410C", ha="right")
    ax.set_yscale("log")
    ax.set_xlabel("Greenshoe s.d.  $\\sigma_\\psi$")
    _style(ax, "First-stage $F$ (log)", "a. Identification strength")

    ax = axes[1]
    shade(ax)
    ax.axhline(0, color=INK, lw=0.9, zorder=2)
    for m in series:
        g = d[d.memory == m].sort_values("sigma_psi")
        ax.plot(g.sigma_psi, g.feedback_bias, "-o", color=MODE_COLOR[m], lw=2,
                ms=4.5, zorder=3)
    worst = cp.loc[cp.feedback_bias.abs().idxmax()]
    ax.annotate(f"{worst.feedback_bias:.2f}\nweak-instrument\nblow-up",
                (worst.sigma_psi, worst.feedback_bias),
                textcoords="offset points", xytext=(16, 6), fontsize=6.8,
                color="#1BAF7A", fontweight="bold",
                arrowprops=dict(arrowstyle="-", color="#1BAF7A", lw=0.9))
    ax.set_xlabel("Greenshoe s.d.  $\\sigma_\\psi$")
    _style(ax, "$\\hat b - b_{\\rm true}$", "b. Residual feedback bias")

    ax = axes[2]
    shade(ax)
    g = d[d.memory == "audited_freeze"].sort_values("sigma_psi")
    ax.plot(g.sigma_psi, 100 * g.freeze_rate, "-o", color=MODE_COLOR["audited_freeze"],
            lw=2, ms=4.5, zorder=3)
    for r in g.itertuples():
        if r.freeze_rate > 0.02:
            ax.annotate(f"{100*r.freeze_rate:.0f}%", (r.sigma_psi, 100*r.freeze_rate),
                        textcoords="offset points", xytext=(4, 4), fontsize=6.8,
                        color=INK)
    ax.set_xlabel("Greenshoe s.d.  $\\sigma_\\psi$")
    _style(ax, "Updates frozen (%)", "c. The rule restores itself")
    ax.text(0.40, 72, "resumes learning\nonce identified", fontsize=6.8,
            color=MUTED, ha="right", va="top")

    fig.legend(loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.14), fontsize=8)
    fig.suptitle("Shaded band: the capital-purged correction is not identified. "
                 "The audit rule declines to certify there.",
                 fontsize=9, color=INK, y=1.03)
    fig.savefig(FIGS / "fig2_instrument.png")
    plt.close(fig)


# ------------------------------------------------------------------ figure 3
def fig_placebo(verdict):
    """Falsification test: switch the capital channel off and the effect must
    disappear. It does."""
    fig, ax = plt.subplots(figsize=(4.6, 3.0))
    arms = ["baseline rho>0", "PLACEBO rho=0"]
    arm_lbl = {"baseline rho>0": "Baseline\n$\\rho>0$",
               "PLACEBO rho=0": "Placebo\n$\\rho=0$"}
    w, x = 0.34, np.arange(2)
    for j, mech in enumerate(("uniform_price", "bookbuilding")):
        vals, cols = [], []
        for arm in arms:
            r = verdict[(verdict.arm == arm) & (verdict.mechanism == mech)]
            vals.append(float(r.lift.iloc[0]))
        col = "#EB6834" if mech == "uniform_price" else "#9254F5"
        bars = ax.bar(x + (j - 0.5) * w, vals, w * 0.92, color=col,
                      label=MECH_LABEL[mech], zorder=2)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2,
                    v + (0.008 if v >= 0 else -0.008), f"{v:+.3f}",
                    va="bottom" if v >= 0 else "top",
                    ha="center", fontsize=7.5, color=INK, fontweight="bold")
    ax.axhline(0, color=INK, lw=1)
    ax.set_xticks(x); ax.set_xticklabels([arm_lbl[a] for a in arms], fontsize=8)
    ax.set_ylim(-0.10, 0.375)
    ax.tick_params(axis="x", pad=18)
    _style(ax, "Manipulation lift of naive history\nover the committed rule")
    ax.set_title("The effect is the capital channel, not the synthetic setup",
                 fontsize=9.5, color=INK, pad=8)
    ax.legend(fontsize=7.5, loc="upper right")
    fig.savefig(FIGS / "fig3_placebo.png")
    plt.close(fig)


# ------------------------------------------------------------------ figure 4
def fig_rationing(scarcity):
    """Only visible once the offering is genuinely scarce: feedback destroys
    the auction's ability to ration."""
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0), sharex=True)
    for j, (ax, (col, lbl, ttl)) in enumerate(zip(axes, [
            ("n_excluded", "Investors excluded (of 50)", "Who is rationed out"),
            ("retail_share", "Retail share of allocated stock",
             "Who ends up holding the stock")])):
        for m in ("no_memory", "naive_history", "capital_purged"):
            g = scarcity[scarcity.memory == m].sort_values("coverage")
            ax.plot(g.coverage, g[col], "-o", color=MODE_COLOR[m], lw=2, ms=5,
                    label=MODE_LABEL[m].replace("\n", " ") if j == 0 else None,
                    zorder=3)
        ax.axvline(1.0, color=MUTED, lw=1, ls=(0, (3, 3)))
        ax.annotate("PS2 code:\nno exclusion", (1.0, 0.985), xycoords=("data", "axes fraction"),
                    fontsize=6.8, color=MUTED, ha="left", va="top",
                    xytext=(4, 0), textcoords="offset points")
        ax.set_xlabel("Coverage ratio (demand / offering)")
        _style(ax, lbl, ttl)
    fig.legend(loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.16), fontsize=8)
    fig.suptitle("Feedback degrades rationing: the inflated signal compresses "
                 "bids so the auction stops sorting", fontsize=9.5, color=INK, y=1.03)
    fig.savefig(FIGS / "fig4_rationing.png")
    plt.close(fig)


# ------------------------------------------------------------------ figure 5
def fig_audit(lockin):
    """The accountability rule needs a thick-sample guard or it certifies on
    noise and locks in permanently."""
    fig, axes = plt.subplots(1, 3, figsize=(7.8, 2.8))
    cols = [("feedback_bias", "Feedback bias $\\hat b - b_{\\rm true}$"),
            ("freeze_rate", "Share of updates frozen"),
            ("price_rmse", "Price RMSE")]
    arms = list(dict.fromkeys(lockin.arm))
    colr = {arms[0]: "#EB6834", arms[1]: "#9254F5"}
    for ax, (c, lbl) in zip(axes, cols):
        bars = []
        for j, arm in enumerate(arms):
            g = lockin[lockin.arm == arm].set_index("mechanism")
            vals = [g.loc[m, c] for m in ("uniform_price", "bookbuilding")]
            errs = [g.loc[m, c + "_ci95"] if c + "_ci95" in g.columns else 0
                    for m in ("uniform_price", "bookbuilding")]
            xs = np.arange(2) + (j - 0.5) * 0.34
            ax.bar(xs, vals, 0.31, color=colr[arm], zorder=2,
                   label=arm if c == "feedback_bias" else None)
            ax.errorbar(xs, vals, yerr=errs, fmt="none", ecolor=INK,
                        elinewidth=1, capsize=2.5, zorder=3)
            bars += list(zip(xs, vals, errs))
        ax.axhline(0, color=INK, lw=0.9)
        # label ABOVE the whisker, using a pad scaled to the finished axis
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo, hi + 0.16 * (hi - lo))
        lo, hi = ax.get_ylim()
        pad = 0.035 * (hi - lo)
        for xx, v, e in bars:
            if v >= 0:
                ax.text(xx, v + (e or 0) + pad, f"{v:.2f}", ha="center",
                        va="bottom", fontsize=6.8, color=INK, fontweight="bold")
            else:
                ax.text(xx, v - (e or 0) - pad, f"{v:.2f}", ha="center",
                        va="top", fontsize=6.8, color=INK, fontweight="bold")
        ax.set_xticks(range(2)); ax.set_xticklabels(["M1", "M2"], fontsize=8)
        _style(ax, lbl)
    fig.legend(loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.14), fontsize=8)
    fig.subplots_adjust(wspace=0.42)
    fig.suptitle("An audit rule must earn the right to certify: "
                 "without a thick-sample guard it locks in on noise",
                 fontsize=9.5, color=INK, y=1.04)
    fig.savefig(FIGS / "fig5_audit.png")
    plt.close(fig)


# ------------------------------------------------------------------ figure 6
def fig_sign(verdict):
    """Sign robustness across the one-at-a-time parameter grid."""
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    v = verdict.copy().reset_index(drop=True)
    labels = [f"{r.parameter}={r.value:g}" for r in v.itertuples()]
    y = np.arange(len(v))
    ax.barh(y, v.manip_lift, 0.66,
            color=["#1BAF7A" if s else "#EB6834" for s in v.lift_sign_positive],
            zorder=2)
    for i, val in enumerate(v.manip_lift):
        ax.text(val + 0.12, i, f"{val:+.2f}", va="center", fontsize=6.5, color=INK)
    ax.axvline(0, color=INK, lw=1)
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=6.5)
    ax.invert_yaxis()
    ax.set_xlabel("Manipulation lift of naive history over the committed rule")
    _style(ax)
    n_pos = int(v.lift_sign_positive.sum())
    ax.set_title(f"Sign of the feedback effect holds in {n_pos}/{len(v)} "
                 f"parameter settings", fontsize=9.5, color=INK, pad=8)
    fig.savefig(FIGS / "fig6_sign_robustness.png")
    plt.close(fig)


# ------------------------------------------------------------------ figure 7
def fig_burden(burden):
    """Who pays for the safeguard. Added after Team FP4's Oct 12 duet challenge
    raised Milli et al. (2019): strategy-robustness buys institutional utility
    at a matching social burden on those classified."""
    d = burden[(burden.allocation_rule == "excludable")
               & (burden.mechanism == "uniform_price")].set_index("memory")
    fig, ax = plt.subplots(figsize=(5.4, 3.1))
    x = np.arange(len(MODE_ORDER))
    w = 0.36
    # Colour means INVESTOR CLASS here, not evaluator rule -- the x-axis
    # already carries the rule, and one axis should not be encoded twice.
    for j, (col, lbl, colour, hatch) in enumerate([
            ("retail_served_pct", "Retail investors served (% of 35)", "#315EFB", None),
            ("inst_served_pct", "Institutions served (% of 15)", "#9AA7B4", "///")]):
        vals = [d.loc[m, col] for m in MODE_ORDER]
        bars = ax.bar(x + (j - 0.5) * w, vals, w * 0.92, color=colour,
                      hatch=hatch, edgecolor="white", linewidth=0.8, zorder=2,
                      label=lbl)
        for b_, v in zip(bars, vals):
            ax.text(b_.get_x() + b_.get_width() / 2, v + 1.6, f"{v:.0f}",
                    ha="center", fontsize=7, color=INK, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([MODE_SHORT[m] for m in MODE_ORDER], fontsize=8)
    ax.set_ylim(0, 118)
    _style(ax, "Share of each class receiving any allocation")
    ax.legend(fontsize=7.5, loc="upper right", ncol=1)
    d_ret = d.loc["audited_freeze", "d_retail_served"]
    d_ins = d.loc["audited_freeze", "d_inst_served"]
    ax.set_title("The safeguard is not distribution-neutral:\n"
                 f"auditing costs retail {abs(d_ret):.1f} of 35 places "
                 f"and gains institutions {d_ins:.1f} of 15",
                 fontsize=9, color=INK, pad=8)
    fig.savefig(FIGS / "fig7_social_burden.png")
    plt.close(fig)


# ---------------------------------------------------------------------------
def main():
    s = pd.read_csv(RESULTS / "summary_results.csv")
    fig_manipulation(s)
    made = ["fig1_manipulation.png"]
    for name, fn, args in [
            ("fig2_instrument.png", fig_instrument, ("robust_instrument.csv",)),
            ("fig3_placebo.png", fig_placebo, ("robust_placebo_verdict.csv",)),
            ("fig4_rationing.png", fig_rationing, ("robust_scarcity.csv",)),
            ("fig5_audit.png", fig_audit, ("audit_lockin.csv",)),
            ("fig6_sign_robustness.png", fig_sign, ("robust_parameters_verdict.csv",)),
            ("fig7_social_burden.png", fig_burden, ("social_burden.csv",))]:
        p = RESULTS / args[0]
        if p.exists():
            fn(pd.read_csv(p))
            made.append(name)
        else:
            print(f"  skipped {name}: run src/robustness.py first")
    print("wrote:", ", ".join(made), "->", FIGS)


if __name__ == "__main__":
    main()
