# Overleaf source — PS2

This source is the revised version of the team proposal on **strategic disclosure, AI valuation, capital allocation, and history-aware evaluator design**.

## Compile
1. Overleaf → New Project → Upload Project → upload this ZIP.
2. Set `main.tex` as the main document.
3. Compiler: **pdfLaTeX** (Menu → Compiler).

## Main-paper structure
`sections/proposal.tex` contains exactly five numbered sections and is designed to occupy the two-page main-paper portion:
1. Research question and verified gap
2. Strategic model and solution concept
3. Social choice and design objective
4. Mechanism design and auction comparison
5. Computational and behavioral test

## Files
- `main.tex` — metadata, authors, teaser, and document structure.
- `sections/proposal.tex` — the two-page Sections 1–5.
- `appendices/supporting.tex` — Author Notes, technical details, AI-use disclosure, cumulative development, formal response to feedback, structured abstract, auction record, artifact parity, and practical-impact record.
- `references.bib` — source bibliography retained for reference/Overleaf editing.
- `references_manual.tex` — compiled bibliography used by the current pdfLaTeX build.
- `figures/ps2_teaser.tex` — TikZ research-design figure.
- `acmart.cls`, `*.bst` — course template files.

## Current computational synchronization

The numerical results reported in the source are synchronized to the fresh Colab verification notebook:
https://colab.research.google.com/drive/1o-t9W3shjHubzSBcB8QK6KYFumrJmEbh

The five canonical Python files are not changed by this Overleaf revision. The current paper reports the fresh-run outputs for seeds 42--46, with two burn-in cohorts. The formal response map records Prof. Luyao Zhang's PS1 and collaborative-learning feedback, Han Zhang's accountability feedback, and the named peer reviews from Aaron Wang and Zhenning Wang.

## Final consistency checks
- `main.tex` records Symposium C (without a class time) and the current GitHub, Colab, and Hugging Face links.
- `sections/proposal.tex` contains the two-page main proposal, including the fixed-versus-revisable evaluator distinction, the accountability/correction extension, and the bounded interpretation of behavioral evidence.
- `appendices/supporting.tex` contains the named acknowledgements and the formal response map required by PS2.
- The five canonical Python files and the Colab outputs remain the source of the reported numerical results; this Overleaf revision does not silently change those computational files.
- Future work is explicitly labelled for endogenous allocation shocks, real-IPO replication, behavioral sample completion, and testing the accountability rule.
