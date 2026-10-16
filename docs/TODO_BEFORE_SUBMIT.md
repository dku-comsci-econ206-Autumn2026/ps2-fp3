# Before you submit — what only you can do

Everything in this repository runs and is self-consistent. The items below need a human,
either because they are facts I don't have or because they need your account.

**Deadline: Wednesday 21 October 2026, 23:00 Asia/Shanghai.**

---

## 1. Facts I could not know — search the paper for `\FILL{`

```bash
grep -rn 'FILL{' sections/ appendices/
```

Each one renders in **red bold** in the compiled PDF, so you cannot miss one. They are:

| Where | What's needed |
|---|---|
| `main.tex` ~line 33, `\TestedRelease` | Replace `\FILL{SHA}` with the commit SHA. This one macro feeds Open Science (page 2) and every other place that cites the release. |
| Appendix A.6 (`appendices/supporting.tex`, "A.6 Fresh-run record") | Commit SHA, Hugging Face Space revision hash, Colab run timestamp |
| Appendix F | Confirm both personal forks + merged PRs are visible in the org repo (Aaron marked this FIX) |
| Appendix G | The Category I / II / III synthesis posts you published on Oct 12 |
| Appendix G, final audit | SDG icons present, Overleaf compiled, poster PDF re-exported after any final edit, both members checked Canvas |

Also paste the same SHA into the **Canvas text entry**.

Done: Ed reply dates (Feiyu 15 Oct, Xuantong 16 Oct) and both Rogerson email dates (16 Oct).

**Everything else is now written in.** The two review sheets, the FP4 duet papers, the
three-lens roundtable challenges, both individual self-challenges, the Ed thread URL and
Rogerson's actual question are all recorded with names, dates and verification locations.

**I did not invent any of these.** Where I had a real source — the instructor's feedback
PDF, your message naming Zhengjun He and Yichen Shen, the PS2 acknowledgments — the names
and points are already written in.

## 2. Post two Ed replies, send two Rogerson emails

**Ed replies** — `docs/ED_REPLIES.md`. Two separate replies to Zhengjun He's three points,
one from each account. They deliberately split the points so they are not interchangeable:
Feiyu takes the interaction question and the distributional finding; Xuantong takes
robustness and the evidence-for-policy question. Each ends with a genuine open question
back to FP4.

**Rogerson emails** — `docs/ROGERSON_EMAIL.md`, both addressed to **rogerson@duke.edu**.
Separate email from each account, different contribution and different question. Both are
built on the question he actually asked you — *what makes your AI better than the AI that
came before it* — and give the corrected answer the project produced.

## 3. The three official SDG icons

I could not download them — the network here blocks `un.org`. Get them from
<https://www.un.org/sustainabledevelopment/news/communications-material/> and save as:

```
figures/sdg/sdg9.png      figures/sdg/sdg16.png      (and sdg8.png if you use target 8.10)
```

The paper compiles **either way**: without the PNGs the diagram draws a labelled tile in
the official goal colour. But the rubric says *official icons*, so get the real ones.
Target wording (16.6, 16.10, 9.3) is already quoted verbatim and verified.

## 4. Compile on Overleaf

Upload `FP3-Final-Overleaf-Source.zip`. It compiles locally with XeTeX (tectonic): 17 pages, the main
text is exactly 2 A4 pages and Author Notes starts page 3, with about two lines of slack in the
right column of page 2. Overleaf uses pdfLaTeX, so line breaks can shift slightly.

**Check on the first compile:**
- [ ] Page 3 starts with **Author Notes**. If page 2 runs over, cut a clause from
      Results R1–R9 or Practical Impacts first.
- [ ] The three diagrams (Figure 2, top of page 2) render side by side.
- [ ] No `??` references (Overleaf runs BibTeX and two passes automatically).

To fit 2 pages, the full results grid (with RMSE and F) moved to Appendix A
(Table "Full headline grid"). The expanded diagrams were already in Appendix G.

## 5. Poster → PDF → PNG

Done on 16 Oct: the poster was rebuilt and exported (PDF + PNG), and the placeholder text was
removed. Only redo this if you edit the poster again:

```bash
python tools/update_poster.py && python tools/check_poster_fit.py
# PowerPoint > Save as PDF -> poster/final-poster.pdf
python tools/poster_preview.py
```

This also fixes the instructor's point that the poster plotted ~1.4 while the headline
said ~6.36: those were two different objects (mean manipulation vs terminal `b̂`) that
were never labelled as different. Every poster number now comes from one frozen run.

## 6. Push, then record the commit

```bash
git add -A && git commit -m "Final project: excludable allocation, audited-freeze rule, robustness suite"
git push
git tag -a v1.0-final -m "Final submission" && git push --tags
git rev-parse HEAD        # <- paste into main.tex \TestedRelease, Appendix A.6, Canvas text
```

Then **check the GitHub landing page renders the poster** — that embed is explicitly
scored. Update the Hugging Face Space: upload `hf_space/README.md` and `hf_space/index.html` (these two
changed since PS2; `script.js` / `style.css` did not), then record the Space revision in A.6.

## 7. Canvas — four files, one submitter

| File | Source |
|---|---|
| `Final-FP3-TeamName.pdf` | Overleaf compile |
| `Final-FP3-TeamName-Overleaf-Source.zip` | `FP3-Final-Overleaf-Source.zip` |
| `Final-FP3-TeamName-A0-Poster.pptx` | `poster/final-poster.pptx` |
| `Final-FP3-TeamName-A0-Poster.pdf` | your PowerPoint export |

**Both members must verify the group submission appears.**

---

## Three things to be ready to defend

**1. Your PS2 adverse result is now reversed.** The instructor's feedback PDF explicitly
*appreciated* that result ("it prevents accountability from being equated automatically
with improvement"). The paper does not quietly drop it — it explains that the adverse
finding was a symptom of weak identification, backed by the sweep showing purging fails
below `F = 10` and works above it. Appendix D records this as a revised claim, not a
silent correction. Be ready to say that out loud.

**2. Two of the defects were in your own PS2 code**, and the paper says so plainly: the
first-stage `F` was mis-normalised (reported 0.136, actually 5.47), and the purge read
`b_true` when forming its own target. Owning these is worth more than hiding them —
"Shared contribution and verification" and "Feedback and accountability" both reward it.
Run `python tests/test_verification.py` once yourself so you have seen all 11 pass.

**3. You narrowed a claim because FP4 challenged you.** Milli et al. (2019) predicts that
strategy-robustness buys institutional utility at a social burden on the classified. You
had recommended the audited evaluator without measuring who pays. R9 measures it: the
safeguard costs retail 13.1 of 35 places and gains institutions 4.2 of 15. This is the
strongest "feedback and accountability" evidence in the submission — an external challenge
that changed a conclusion rather than being absorbed. Say so plainly, and credit FP4 by
name when you do.

## What I'd check first if you only have an hour

1. `grep -rn 'FILL{' sections/ appendices/` — fill them in.
2. Compile on Overleaf, confirm 2 pages.
3. Open the poster, look at it, export the PDF.
4. Push and confirm the README poster embed renders.
