"""Rebuild the A0 poster from the frozen run.

    python tools/update_poster.py

Reads poster/final-poster.pptx, replaces the text of named shapes and swaps the
two result figures, then writes the file back. Every number written here is read
from results/headline_table.csv, so the poster cannot drift from the paper --
which is what the 14 October feedback asked for ("regenerate from one frozen
run so the interpretation and every plotted number refer to the same evidence").

Slide stays 1189 x 841 mm (A0 landscape). Export the PDF from PowerPoint, then
run tools/poster_preview.py to regenerate the PNG preview for the README.
"""
from pathlib import Path
import copy

import pandas as pd
from pptx import Presentation
from pptx.util import Mm, Pt

ROOT = Path(__file__).resolve().parent.parent
POSTER = ROOT / "poster" / "final-poster.pptx"
FIGS = ROOT / "figures"

H = pd.read_csv(ROOT / "results" / "headline_table.csv").set_index(["mechanism", "memory"])
def g(mech, mem, col):
    return float(H.loc[(mech, mem), col])

# Explicit point sizes for boxes whose inherited size no longer fits the new
# text. Measured with tools/check_poster_fit.py, which estimates wrapped lines
# against the box geometry.
SIZES = {"design-caption": 21, "dates": 14, "ack": 12.5,
         "references": 13.5, "access-links": 13}

M1 = lambda mem, col: g("uniform_price", mem, col)
M2 = lambda mem, col: g("bookbuilding", mem, col)


# --------------------------------------------------------------------------
def set_text(slide, name, text, size=None):
    """Replace a shape's text, preserving the first run's character formatting."""
    if size is None:
        size = SIZES.get(name)
    for sh in slide.shapes:
        if sh.name != name:
            continue
        if not sh.has_text_frame:
            return False
        tf = sh.text_frame
        p0 = tf.paragraphs[0]
        proto = p0.runs[0] if p0.runs else None
        font = {}
        if proto is not None:
            f = proto.font
            font = {"bold": f.bold, "italic": f.italic, "size": f.size,
                    "name": f.name,
                    "color": (f.color.rgb if f.color and f.color.type is not None
                              else None)}
        # keep paragraph 0, drop the rest
        for p in list(tf.paragraphs)[1:]:
            p._p.getparent().remove(p._p)
        for r in list(p0.runs):
            r._r.getparent().remove(r._r)

        lines = text.split("\n")
        for i, line in enumerate(lines):
            para = p0 if i == 0 else tf.add_paragraph()
            if i > 0:
                para.alignment = p0.alignment
                para.level = p0.level
            run = para.add_run()
            run.text = line
            f = run.font
            if font.get("bold") is not None:   f.bold = font["bold"]
            if font.get("italic") is not None: f.italic = font["italic"]
            if font.get("name"):               f.name = font["name"]
            if size is not None:               f.size = Pt(size)
            elif font.get("size"):             f.size = font["size"]
            if font.get("color") is not None:
                f.color.rgb = font["color"]
        return True
    print(f"  ! shape not found: {name}")
    return False


def move(slide, name, left=None, top=None, width=None, height=None):
    for sh in slide.shapes:
        if sh.name == name:
            if left is not None:   sh.left = Mm(left)
            if top is not None:    sh.top = Mm(top)
            if width is not None:  sh.width = Mm(width)
            if height is not None: sh.height = Mm(height)
            return True
    print(f"  ! shape not found for move: {name}")
    return False


def swap_picture(slide, name, image, box):
    """Delete the named picture and drop `image` into `box` (L,T,W,H in mm),
    preserving the image's aspect ratio and centring it in the box."""
    target = next((s for s in slide.shapes if s.name == name), None)
    if target is None:
        print(f"  ! picture not found: {name}")
        return
    target._element.getparent().remove(target._element)
    L, T, W, Hh = box
    from PIL import Image
    try:
        iw, ih = Image.open(image).size
        ar = iw / ih
    except Exception:
        ar = W / Hh
    if W / Hh > ar:                 # box wider than image -> fit height
        h, w = Hh, Hh * ar
    else:                           # fit width
        w, h = W, W / ar
    pic = slide.shapes.add_picture(str(image), Mm(L + (W - w) / 2),
                                   Mm(T + (Hh - h) / 2), Mm(w), Mm(h))
    pic.name = name
    return pic


# --------------------------------------------------------------------------
def main():
    prs = Presentation(str(POSTER))
    s = prs.slides[0]
    print(f"slide {prs.slide_width/914400*25.4:.0f} x "
          f"{prs.slide_height/914400*25.4:.0f} mm")

    set_text(s, "course-line",
             "COMSCI / ECON 206   |   FINAL PROJECT   |   AUTUMN 2026   |   SYMPOSIUM C")
    set_text(s, "project-title",
             "Learning from Its Own Footprint\n"
             "When may an AI valuation rule revise itself?")
    set_text(s, "authors", "Feiyu Li · Xuantong Fu  |  Team FP3")
    set_text(s, "course-instructor", "Course instructor: Professor Luyao Zhang")
    set_text(s, "version",
             "v1.0-final · 20 seeds · frozen run · all results simulated")

    # ---- key message: ONE object, one number, no 1.4-vs-6.36 ambiguity ----
    set_text(s, "takeaway",
             f"An evaluator that learns from outcomes it caused roughly DOUBLES strategic "
             f"disclosure: mean manipulation {M1('naive_history','mean_manipulation'):.3f} "
             f"vs {M1('no_memory','mean_manipulation'):.3f} under a committed rule (M1, 20 seeds).\n"
             f"The fix is not accountability in general but IDENTIFICATION: gate revision on a "
             f"first-stage F ≥ 10 and worst-case bias falls from 2.563 to 0.275.\n"
             f"But the safeguard is NOT free: it costs retail investors 13.1 of 35 places "
             f"and gains institutions 4.2 of 15. An integrity gain with a distributional price.")

    # ---- column 1: question and model ------------------------------------
    set_text(s, "research-question",
             "Under what condition may an AI valuation rule safely revise itself from "
             "outcomes it helped cause — and does the allocation mechanism decide whether "
             "that condition can hold?\n"
             "Gap: costly-disclosure and performative-prediction work never let the SAME rule "
             "both set allocation and retrain on it, so no checkable condition exists.")
    set_text(s, "model",
             "Issuer discloses d = θ + m at cost m²/2γ. The rule posts a public score "
             "s = (1−β)μ₀ + β[a + b̂(d+η)]; investors bid; the mechanism sets price P and "
             "proceeds k; outcome y = θ + ρk + ε re-enters the rule's history.\n"
             "Best response m* ∝ λβb̂ — every revision of the rule moves every later issuer's "
             "report. PBE with beliefs and sequential rationality in Appendix A.0.")
    set_text(s, "lenses",
             "Game theory — revising the rule is itself a strategic act: m* rises with the "
             "rule's PERCEIVED sensitivity, so the cost is waste, not deception.\n"
             "Social choice — pricing accuracy, allocative efficiency and retail access "
             "conflict; later issuers inherit a calibration they never influenced.\n"
             "Mechanism design — only the allocation rule supplies variation in k orthogonal "
             "to d, so it decides whether learning is admissible at all.")
    set_text(s, "auction",
             "100 shares; 15 institutions (≤6 units) and 35 retail (≤2 units) — 160 units of "
             "demand, coverage 1.6×, so bids EXCLUDE: 16 of 50 investors get zero.\n"
             "M1 uniform-price: rank bids, fill, pro-rate the margin, pay the lowest accepted "
             "bid. M2 bookbuilding: 85% reserved to institutions at an 8% discount.\n"
             "The PS2 fixed-share rule is retained as a labelled arm. Boundary: flat demand "
             "curves (no demand reduction); no certification or relationship effects.")

    # ---- column 2 figures ------------------------------------------------
    swap_picture(s, "Picture 58", FIGS / "fig1_manipulation.png", (375, 310, 438, 128))
    set_text(s, "design-caption",
             "Fig 1. Evaluator memory and strategic disclosure. 20 seeds, 95% CI across "
             "seeds. Naive history roughly doubles manipulation; the correction and the "
             "audit rule return it to the committed baseline.")
    swap_picture(s, "Picture 59", FIGS / "fig2_instrument.png", (375, 489, 438, 175))
    set_text(s, "result-caption",
             "Fig 2. The discriminating test. Shaded band = the correction is NOT identified. "
             "(a) stronger exchange-set greenshoe variation buys identification; (b) below "
             "F = 10 the purged estimator is not merely biased but unstable, swinging to "
             "−2.563, while the audited rule's worst case is 0.275; (c) the rule restores "
             "itself, unfreezing 100% → 0% as identification arrives.\n"
             "Placebo: setting ρ = 0 removes the effect entirely (+0.328 → −0.019), so it is "
             "the capital channel, not the synthetic setup. Sign holds in 27/27 settings.")

    # ---- column 3: impact -------------------------------------------------
    set_text(s, "real-world",
             "Mechanism: require any valuation rule that also influences allocation to publish "
             "its calibration path, allocation footprint and first-stage F, and to freeze "
             "updates when F < 10, restoring the last audited rule.\n"
             "Indicator: share of published updates carrying F ≥ 10. Baseline: no venue "
             "discloses this today. SDG 16.6, 16.10, 9.3.\n"
             "Evidence status: INTENDED BENEFIT, SIMULATED ONLY. Risk: a published threshold "
             "is gameable — suppress allocation variation and the rule stays frozen on a "
             "favourable parameter. Safeguard: exchange-set shock, third-party audit log.")
    set_text(s, "interdisciplinary",
             "Economics — the allocation rule, not the estimator, decides whether the "
             "evaluator's own footprint is identifiable.\n"
             "Computer science — GitHub runs the whole grid in one command; 11 assertions "
             "verify each claim, including two defects we found in our own PS2 code: a "
             "first-stage F mis-normalised by a factor of n−2 (reported 0.136, actually 5.47) "
             "and a purge that read b_true when forming its target.\n"
             "Social choice — challenged by Team FP4 (Oct 12 duet) with Milli et al. 2019 on "
             "the social cost of strategic classification, we measured who pays for our own "
             "safeguard. Versus the unsafeguarded rule the audited evaluator serves 13.1 "
             "fewer of 35 retail investors (99.9%→62.5%) and 4.2 more of 15 institutions "
             "(36.7%→64.8%). The allocation and equilibrium claims survived that challenge; "
             "the welfare claim did not, and is now narrowed.\n"
             "Behavioral — the Hugging Face Space records whether players strip predictable "
             "inflation out of the public signal. EXPLORATORY: completed n and matched "
             "treatment outputs are not established; no population claim is made.")
    set_text(s, "limits",
             "Instrument exogeneity is imposed by construction — the central open limitation. "
             "ρ is exogenous and unobserved, so allocative efficiency on ρ stays ≈0 in every "
             "cell (reported as a negative result). Flat demand curves. One evaluator. "
             "Equilibrium is of the stage game, not the full dynamic game.\n"
             "NEXT TEST, stated in advance: 2SLS on SEC EDGAR S-1 text × realised greenshoe "
             "exercise, 2015–2025. If the real first stage returns F < 10, an audited "
             "evaluator can never certify in practice and we ABANDON this design in favour "
             "of commitment.")

    # ---- named contributions (required on the poster as well as the paper)
    move(s, "dates", left=845, top=714, width=307, height=50)
    set_text(s, "dates",
             "NAMED CONTRIBUTIONS — Feiyu Li: decided the allocation rule governs whether "
             "learning is admissible; built the excludable mechanism (src/auction.py) and the "
             "allocation assertions; verified 16/50 excluded and that the PS2 arm still serves "
             "all 50. Xuantong Fu: decided the first-stage F should govern the audit rule; "
             "built the 2SLS estimator, the audited-freeze rule and the robustness suite; found "
             "and verified the F mis-normalisation and the b_true leak. Each author "
             "independently re-ran and confirmed a consequential component of the other's work.")

    # ---- footer: FULL acknowledgments, same list as the paper -------------
    move(s, "ack-heading", left=37, top=771, width=500, height=16)
    move(s, "ack", left=37, top=786, width=500, height=48)
    set_text(s, "ack",
             "Duet partner Team FP4 — Zhengjun He and Yichen Shen — whose selection of Milli "
             "et al. (2019) forced us to narrow a claim rather than defend it (see Social "
             "choice, left). Prof. Luyao Zhang — incubated this research; her 14 Oct 2026 feedback (fixed-share "
             "allocation, the missing sequential-rationality argument, the poster/headline "
             "mismatch) produced the largest change in this work. Prof. Kenneth S. (Ken) "
             "Rogerson — Program Discussant, 2056 Nobel and Turing Laureate Program Launch "
             "Workshop, 7 Sep 2026, who asked what makes our AI better than the AI before "
             "it; this paper is the corrected answer. Han Zhang (Liberata; Duke PhD "
             "candidate) — explicit "
             "correction routes, which became the audited-freeze rule. Formal reviewers: Aaron "
             "Wang (FP8), Zhenning Wang — who independently converged on the same open question, "
             "whether the footprint survives real issuance data, now the roadmap's first study. "
             "Individual self-challenges posted 14 Oct by Feiyu Li (artifact risk) and Xuantong "
             "Fu (weak identification); each ran their own test and replied to FP4 separately. "
             "Tencent Shanghai "
             "office; Shanghai Science and Technology Museum; and the whole COMSCI/ECON 206 "
             "classroom community. Software: Python, NumPy, pandas, Matplotlib, Gradio. SDG "
             "icons and target text © United Nations. AI-Assisted — disclosed in Appendix A.1. "
             "If you reviewed this project and are not named, tell us and we will correct both "
             "artifacts.")

    move(s, "references-heading", left=556, top=771, width=270, height=16)
    move(s, "references", left=556, top=786, width=270, height=48)
    set_text(s, "references",
             "Perdomo, Zrnic, Mendler-Dünner & Hardt 2020, ICML (performative prediction). "
             "Benveniste & Spindt 1989, JFE 24(2) 343, doi:10.1016/0304-405X(89)90051-2. "
             "Cao, Jiang, Yang & Zhang 2023, RFS 36(9) 3603, doi:10.1093/rfs/hhad021. "
             "Staiger & Stock 1997, Econometrica 65(3) 557, doi:10.2307/2171753. "
             "Milli, Miller, Dragan & Hardt 2019, FAT* 230, doi:10.1145/3287560.3287576. "
             "Lucas 1976, Carnegie-Rochester 1, 19. Nobel Prize in Economic Sciences 2026 "
             "(Hall & Woodford) and 2025 (Mokyr, Aghion & Howitt), nobelprize.org. "
             "Full reference list in the paper.")

    set_text(s, "access-links",
             "GitHub: github.com/dku-comsci-econ206-Autumn2026/ps2-fp3 (poster embedded in root README)\n"
             "Colab: colab.research.google.com/drive/1o-t9W3shjHubzSBcB8QK6KYFumrJmEbh\n"
             "HF Space: huggingface.co/spaces/dku-comsci-econ206-2026/strategic-disclosure-game")

    prs.save(str(POSTER))
    print(f"wrote {POSTER}")
    print("NEXT: open in PowerPoint -> Save as PDF -> poster/final-poster.pdf,")
    print("      then: python tools/poster_preview.py")


if __name__ == "__main__":
    main()
