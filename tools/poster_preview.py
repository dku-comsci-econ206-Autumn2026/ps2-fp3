"""Regenerate the README poster preview from the exported poster PDF.

    python tools/poster_preview.py

Run this AFTER exporting poster/final-poster.pdf from PowerPoint. It renders
page 1 to poster/final-poster.png at a width readable on the GitHub landing
page. The assignment requires the actual poster PDF *and* a readable preview to
be committed, with the preview embedded in the ROOT README.md.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "poster" / "final-poster.pdf"
PNG = ROOT / "poster" / "final-poster.png"
TARGET_W = 2000          # px; readable on a GitHub landing page


def main():
    if not PDF.exists():
        print(f"ERROR: {PDF} not found.\n"
              "Export it first: open poster/final-poster.pptx in PowerPoint, "
              "File > Save as > PDF, save as poster/final-poster.pdf")
        return 1
    try:
        import fitz                      # PyMuPDF
    except ImportError:
        print("ERROR: PyMuPDF is required.  pip install pymupdf")
        return 1

    doc = fitz.open(PDF)
    page = doc[0]
    w_mm = page.rect.width / 72 * 25.4
    h_mm = page.rect.height / 72 * 25.4
    print(f"page 1: {w_mm:.0f} x {h_mm:.0f} mm")
    if not (abs(w_mm - 1189) < 3 and abs(h_mm - 841) < 3):
        print("  WARNING: not A0 landscape (1189 x 841 mm). Check the PowerPoint "
              "page setup before exporting.")

    zoom = TARGET_W / page.rect.width
    page.get_pixmap(matrix=fitz.Matrix(zoom, zoom)).save(PNG)
    print(f"wrote {PNG} ({TARGET_W}px wide, {PNG.stat().st_size/1e6:.1f} MB)")
    print("\nThe root README.md already contains:")
    print("  ![Final presentation poster](poster/final-poster.png)")
    print("  [Download the poster PDF](poster/final-poster.pdf)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
