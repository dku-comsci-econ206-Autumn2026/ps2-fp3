"""Pre-submission readiness check.

    python tools/preflight.py

Prints one status board covering everything the Review and Evaluation Guide's
submission audit asks for. Re-run it after each step; it is cheap. Exit code is
0 only when nothing is BLOCKING.

Three levels:
  BLOCKING  the submission is incomplete or inconsistent without this
  TODO      required by the rubric, needs a human action
  OK        verified here
"""
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
rows = []


def add(level, item, detail=""):
    rows.append((level, item, detail))


def run(cmd):
    try:
        r = subprocess.run([sys.executable] + cmd, cwd=ROOT,
                           capture_output=True, text=True, timeout=1200)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return 1, str(e)


def main():
    # ---------- 1. code and numbers ---------------------------------------
    rc, out = run(["tests/test_verification.py"])
    m = re.search(r"(\d+)/(\d+) passed", out)
    add("OK" if rc == 0 else "BLOCKING", "Verification assertions",
        m.group(0) if m else "could not parse")

    rc, out = run(["tools/check_numbers.py"])
    m = re.search(r"(\d+)/(\d+) checks pass", out)
    add("OK" if rc == 0 else "BLOCKING",
        "Paper/poster/README agree with frozen run",
        m.group(0) if m else "could not parse")

    rec = ROOT / "results" / "fresh_run_record.json"
    if rec.exists():
        d = json.loads(rec.read_text())
        add("OK", "Fresh-run record",
            f"{len(d['seeds'])} seeds, {d['rows']} rows, {d['generated_utc'][:16]}Z")
    else:
        add("BLOCKING", "Fresh-run record", "run src/run_experiment.py")

    figs = sorted((ROOT / "figures").glob("fig*.png"))
    add("OK" if len(figs) >= 7 else "BLOCKING", "Figures generated",
        f"{len(figs)} present")

    # ---------- 2. LaTeX source -------------------------------------------
    tex = ["main.tex", "sections/proposal.tex", "appendices/supporting.tex"] + \
          [f"figures/{p.name}" for p in (ROOT / "figures").glob("*.tex")]
    fills, cites, labels, refs = 0, set(), set(), set()
    for f in tex:
        t = (ROOT / f).read_text()
        fills += t.count("\\FILL{")
        labels |= set(re.findall(r"\\label\{([^}]+)\}", t))
        refs |= set(re.findall(r"\\(?:page)?ref\{([^}]+)\}", t))
        for c in re.findall(r"\\cite\{([^}]+)\}", t):
            cites |= {x.strip() for x in c.split(",")}
    bib = set(re.findall(r"@\w+\{([^,]+),",
                         (ROOT / "references.bib").read_text()))
    add("OK" if not (refs - labels) else "BLOCKING", "All \\ref resolve",
        f"{len(refs)} refs" if not (refs - labels) else str(refs - labels))
    add("OK" if not (cites - bib) else "BLOCKING", "All \\cite in references.bib",
        f"{len(cites)} citations" if not (cites - bib) else str(cites - bib))
    add("TODO" if fills else "OK", "Red [FILL] markers in the PDF",
        f"{fills} remaining — grep -rn 'FILL{{' sections/ appendices/"
        if fills else "none")

    # ---------- 3. poster --------------------------------------------------
    pptx = ROOT / "poster" / "final-poster.pptx"
    pdf = ROOT / "poster" / "final-poster.pdf"
    png = ROOT / "poster" / "final-poster.png"
    if pptx.exists():
        try:
            from pptx import Presentation
            prs = Presentation(str(pptx))
            w = prs.slide_width / 914400 * 25.4
            h = prs.slide_height / 914400 * 25.4
            ok = abs(w - 1189) < 2 and abs(h - 841) < 2
            add("OK" if ok else "BLOCKING", "Poster PPTX is A0 landscape",
                f"{w:.0f} x {h:.0f} mm")
        except ImportError:
            add("TODO", "Poster PPTX size", "python-pptx not installed")
    else:
        add("BLOCKING", "Poster PPTX", "missing")
    add("OK" if pdf.exists() else "BLOCKING", "Poster PDF exported",
        "present" if pdf.exists() else "PowerPoint > Save as PDF > poster/final-poster.pdf")
    add("OK" if png.exists() else "BLOCKING", "Poster PNG preview",
        "present" if png.exists() else "then run tools/poster_preview.py")

    # ---------- 4. README embed -------------------------------------------
    rd = (ROOT / "README.md").read_text()
    embed = "![Final presentation poster](poster/final-poster.png)" in rd
    link = "(poster/final-poster.pdf)" in rd
    add("OK" if embed and link else "BLOCKING",
        "ROOT README embeds preview + links PDF",
        "both present" if embed and link else "missing one")

    # ---------- 5. SDG icons ----------------------------------------------
    sdg = sorted((ROOT / "figures" / "sdg").glob("sdg*.png"))
    add("OK" if len(sdg) >= 2 else "TODO", "Official UN SDG icons",
        f"{len(sdg)} present" if sdg else
        "download from un.org into figures/sdg/ (compiles without them)")

    # ---------- 6. git ------------------------------------------------------
    try:
        r = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            dirty = [l for l in r.stdout.splitlines() if l.strip()]
            add("TODO" if dirty else "OK", "Working tree committed",
                f"{len(dirty)} uncommitted file(s)" if dirty else "clean")
            h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                               capture_output=True, text=True, timeout=30)
            if h.returncode == 0:
                add("TODO", "Record this commit in Appendix A.6 + G",
                    h.stdout.strip())
        else:
            add("TODO", "Git repository", "not a git repo here yet")
    except Exception:
        add("TODO", "Git repository", "git unavailable")

    # ---------- 7. human-only steps ---------------------------------------
    add("TODO", "Overleaf compiles, main text is exactly 2 A4 pages", "check by eye")
    add("TODO", "Hugging Face Space updated from hf_space/", "README + banner")
    add("TODO", "Canvas: 4 files uploaded, BOTH members verified", "by 21 Oct 23:00")

    # ---------- print -------------------------------------------------------
    order = {"BLOCKING": 0, "TODO": 1, "OK": 2}
    rows.sort(key=lambda r: order[r[0]])
    mark = {"OK": "  OK  ", "TODO": " TODO ", "BLOCKING": "BLOCK!"}
    print("\n" + "=" * 78)
    print("  PRE-SUBMISSION CHECK — FP3 final project")
    print("=" * 78)
    for lvl, item, detail in rows:
        print(f"[{mark[lvl]}] {item:<46s} {detail}")
    nb = sum(1 for r in rows if r[0] == "BLOCKING")
    nt = sum(1 for r in rows if r[0] == "TODO")
    print("=" * 78)
    print(f"  {nb} blocking, {nt} to do, "
          f"{sum(1 for r in rows if r[0]=='OK')} verified")
    if nb:
        print("\n  Blocking items must be resolved before submitting.")
    print()
    return 1 if nb else 0


if __name__ == "__main__":
    sys.exit(main())
