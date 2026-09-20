#!/usr/bin/env python3
"""Check authoring-conventions.md rule 12 — every figure and body table is labelled.

Three things go wrong, and this catches all three:

  1. an IMAGE with no `**Figure N** — …` caption line under it;
  2. a BODY TABLE with no `**Table N** — …` label line above it;
  3. a PROSE REFERENCE ("Figure 3", "fig 3", "table 2") pointing at a label the
     file does not contain — the dangling-pointer case rule 11 solved for §N.

Scope follows the rule: vocabulary/answers `<details>` blocks, the bilingual
key-terms tables and fenced code are lookup furniture and are skipped.

    python3 scripts/check-captions.py            # summary, non-zero exit on failure
    python3 scripts/check-captions.py -v         # list every hit
"""
import re
import sys
import glob

VERBOSE = "-v" in sys.argv

FIG_CAP = re.compile(r'^\*\*Figure (\d+)\*\* — ', re.M)
TBL_CAP = re.compile(r'^\*\*Table (\d+)\*\* — ', re.M)
IMG = re.compile(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$', re.M)
TBL_HEAD = re.compile(r'^\|[^\n]*\|\n\|[\s:|-]+\|$', re.M)
# a prose reference: "Figure 3", "fig 3", "fig3", "table 2" — but not a file path
REF = re.compile(r'(?<![-\w/])\b(figure|fig|table)\.? ?(\d+)\b', re.I)


def blank(m):
    """Blank a span but keep its LENGTH and its newlines, so offsets into the
    masked text and the raw text stay interchangeable (and line numbers hold)."""
    return "".join("\n" if c == "\n" else " " for c in m.group(0))


def masked(text):
    """Body only: drop <details> blocks, fenced code, and the key-terms section."""
    t = re.sub(r'<details>.*?</details>', blank, text, flags=re.S)
    t = re.sub(r'```.*?```', blank, t, flags=re.S)
    t = re.sub(r'^#{2,3} .{0,12}Key terms.*?(?=^#{1,3} |\Z)', blank, t, flags=re.S | re.M)
    return t


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def check(path):
    raw = open(path, encoding="utf-8").read()
    body = masked(raw)
    problems = []

    figs = {int(n) for n in FIG_CAP.findall(raw)}
    tbls = {int(n) for n in TBL_CAP.findall(raw)}

    # --- 1. images without a caption underneath -----------------------------
    for m in IMG.finditer(body):
        src = m.group(2)
        if "/diagrams/" not in src and not src.startswith(("diagrams/", "images/")):
            continue
        # Look for the caption in the RAW text: a figure wrapped in
        # <!-- DIAGRAM/PLOT:START --> carries its collapsed source block first,
        # and its caption must sit AFTER the END marker (render-diagrams.mjs
        # rewrites everything between the DIAGRAM markers and would eat it).
        tail = raw[m.end():][:3000]
        tail = re.split(r'\n#{1,6} |\n!\[', tail)[0]
        tail = re.sub(r'<details>.*?</details>', '', tail, flags=re.S)
        tail = re.sub(r'<!--\s*(DIAGRAM|PLOT):END\s*-->', '', tail)
        first = next((ln for ln in tail.split('\n') if ln.strip()), '')
        if re.match(r'\*\*Figure \d+\*\* — ', first):
            continue
        after = first + '\n'
        # an illustration already carrying an italic provenance caption (rule 7)
        # is not a numbered figure — it takes a number only if prose cites one
        if re.match(r'[*_][^*_]', first):
            continue
        # a Mermaid diagram is exempt unless the file numbers it with a marker
        if re.search(r'!\[Diagram \d+\]', m.group(0)):
            before = body[max(0, m.start() - 120):m.start()]
            if not re.search(r'<!--\s*fig(?:ure)?\s?\d+\s*-->', before, re.I):
                continue
        problems.append((line_of(body, m.start()), "UNCAPTIONED FIGURE",
                         src.split("/")[-1]))

    # --- 2. body tables without a label above -------------------------------
    for m in TBL_HEAD.finditer(body):
        before = body[max(0, m.start() - 300):m.start()]
        if not re.search(r'\*\*Table \d+\*\* — [^\n]*\n\s*\n\s*$', before):
            head = m.group(0).split("\n")[0]
            problems.append((line_of(body, m.start()), "UNLABELLED TABLE",
                             head[:60]))

    # --- 3. prose references pointing at a label that does not exist --------
    for m in REF.finditer(body):
        kind, num = m.group(1).lower(), int(m.group(2))
        have = figs if kind in ("figure", "fig") else tbls
        if num not in have:
            ctx = re.sub(r'\s+', " ", body[max(0, m.start() - 50):m.start() + 30]).strip()
            problems.append((line_of(body, m.start()), "DANGLING REF",
                             f"{m.group(0)!r} …{ctx}…"))
    return problems


def main():
    files = sorted(
        f for f in glob.glob("courses/**/*.md", recursive=True)
        + glob.glob("hobby/**/*.md", recursive=True)
        + glob.glob("upskill-readings/**/*.md", recursive=True)
        if not f.endswith(("plan.md", "README.md"))   # indexes are not material
    )
    counts = {"UNCAPTIONED FIGURE": 0, "UNLABELLED TABLE": 0, "DANGLING REF": 0}
    dirty = 0
    for f in files:
        problems = check(f)
        if not problems:
            continue
        dirty += 1
        if VERBOSE:
            print(f"\n{f}")
        for line, kind, detail in problems:
            counts[kind] += 1
            if VERBOSE:
                print(f"  L{line:<5} {kind:<20} {detail}")

    total = sum(counts.values())
    print(f"\nFiles with problems: {dirty} / {len(files)}")
    for k, v in counts.items():
        print(f"  {k:<20} {v}")
    print(f"  {'TOTAL':<20} {total}")
    if not VERBOSE and total:
        print("\nRun with -v to list them.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
