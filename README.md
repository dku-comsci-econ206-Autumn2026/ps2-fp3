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
- `appendices/supporting.tex` — Author Notes, technical details, AI-use disclosure, cumulative development, review response, structured abstract, auction record, artifact parity, and practical-impact record.
- `references.bib` — source bibliography retained for reference/Overleaf editing.
- `references_manual.tex` — compiled bibliography used by the current pdfLaTeX build.
- `figures/ps2_teaser.tex` — TikZ research-design figure.
- `acmart.cls`, `*.bst` — course template files.

## Before final submission
Replace the remaining team/session/artifact placeholders: team/session metadata, GitHub URL and commit/release, notebook URL, Hugging Face URL/version, poster version, reviewer names, and the AI-use disclosure. Do not label future symposium reviews or behavioral results as completed before they occur. Regenerate every numerical result from the final code and seed record and make sure the paper, GitHub, Hugging Face artifact, and poster use the same model and parameters.
