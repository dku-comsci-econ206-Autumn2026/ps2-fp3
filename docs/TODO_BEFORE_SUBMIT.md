# Final submission checklist — Team FP3

## Updated from the author-supplied final files

- Main text is stated by the authors to be two A4 pages; verify the latest Overleaf PDF visually after recompilation.
- Upstream GitHub base commit supplied by the authors: `0f735e72d9b7e0144914c8664b45850cddac3616`.
- Related pull-request commit supplied by the authors: `71d0586dd6a0f9d4fae1d243c07eba8ce0c19cf3`.
- The local finalization edits still need to be committed and pushed; the SHA above is the upstream base commit, not a hash of these edits.
- The Overleaf source contains official SDG image files `figures/sdg/sdg8.png`, `sdg9.png`, and `sdg16.png`.
- The GitHub source bundle contains `poster/final-poster.pptx`, `poster/final-poster.pdf`, and `poster/final-poster.png`; README embeds the PNG preview and links the PDF.
- The 12 October Ed post content supplied by the authors is archived in this repository's `docs/ED_REPLIES.md` and summarized in Appendix G.
- The experiment record in `results/fresh_run_record.json` is timestamped `2026-10-15T16:06:56.494786+00:00` (UTC). This is the recorded experiment run, not a separate Colab execution timestamp.

## Remaining external confirmations (not inferable from source ZIP)

1. Confirm the live Hugging Face Space revision hash and record it if required.
2. If the course requires a Colab execution timestamp, obtain it from the actual Colab run history; do not substitute the experiment JSON timestamp.
3. Verify both personal forks and whether the pull request was merged in the live GitHub organization.
4. Confirm the live defence responses, takeaway sheet, and handwritten exit evidence if these are required.
5. Compile the final source on Overleaf; check page 3 starts with Author Notes, there are no unresolved citations, and all icons/diagrams render correctly.
6. Open the final poster PDF after the last PPTX edit and verify visual parity. The supplied bundle contains PPTX, PDF and PNG, but a ZIP listing alone cannot verify visual parity.
7. Upload the final paper PDF, Overleaf source ZIP, A0 PPTX, and A0 PDF to Canvas. Both members must independently verify the group submission before the deadline.

## Reproduction commands

```bash
pip install -r requirements.txt
python src/run_experiment.py
python src/robustness.py
python src/make_figures.py
python tests/test_verification.py
python tools/check_numbers.py
```

Do not mark external-service checks as complete until they have been verified in the live service.
