#!/usr/bin/env python3
"""check-xrefs.py — validate every section cross-reference in the course/hobby/reading material.

Run from the repo root:   python3 scripts/check-xrefs.py

Two passes (see authoring-conventions.md rule 11 for the convention itself):
  1. BARE  "§N"  must name a heading in the file it appears in.
  2. QUALIFIED "Ch2 §1" / "E05 §2" / "M01 Ch4 §3" must resolve to a real section FILE;
     a heading inside another file needs the section level too ("Ch1 §1 §5").

Exit status is non-zero if anything is broken, so it can gate a commit.
"""

# ---------- pass 1: bare references ----------

import re, sys, glob

QUAL = re.compile(r"(?:[EM]\d{1,2}|Ch\d+|§\d+[a-z]?(?:'s)?)\s*$")   # a qualifier immediately before
EXTERNAL = re.compile(r'(?:RFC|PEP|ISO|IEEE)\s*\d+\s*$', re.I)        # external standards, not repo refs

def check(path, verbose=True):
    raw = open(path).read()
    t = re.sub(r'```.*?```', lambda m: ' ' * len(m.group()), raw, flags=re.S)
    heads = set()
    for m in re.finditer(r'^## (\d+)([a-z]?)\.', t, re.M):
        heads.add(m.group(1))
    if not heads:
        return []
    bad = []
    for m in re.finditer(r'§(\d+)([a-z]?)', t):
        pre = t[max(0, m.start()-14):m.start()]
        if QUAL.search(pre):
            continue                      # qualified: Ch2 §1, E05 §2, §2 §10, §2's §10a -> other file
        if EXTERNAL.search(pre):
            continue                      # "RFC 9110 §13" cites a standard, not this repo
        if re.search(r'Applied\*\* (?:gets|will be) added', t[m.start():m.start()+60]):
            continue                      # forward ref in a PREPARED file; exists once finalized
        if m.group(1) not in heads:
            line = t.count('\n', 0, m.start()) + 1
            ctx = re.sub(r'\s+', ' ', t[max(0,m.start()-60):m.start()+45]).strip()
            bad.append((line, m.group(0), ctx))
    if verbose and bad:
        print(f"\n{path}  (headings: {' '.join(sorted(heads, key=int))})")
        for line, ref, ctx in bad:
            print(f"  L{line:<5} {ref:<6} …{ctx}…")
    return bad

files = sorted(f for f in glob.glob('courses/**/*.md', recursive=True)+glob.glob('hobby/**/*.md', recursive=True)+glob.glob('upskill-readings/**/*.md', recursive=True) if not f.endswith('plan.md'))
total = sum(len(check(f)) for f in files)
print(f"\nDangling bare references: {total}")


# ---------- pass 2: qualified references ----------

import re, glob, os, collections

def chapters(module_dir):
    return {int(d[:2]): d for d in os.listdir(module_dir) if re.match(r'\d\d-', d) and os.path.isdir(os.path.join(module_dir, d))}
def sections(chap_dir):
    return {int(f[:2]): f for f in os.listdir(chap_dir) if re.match(r'\d\d-.*\.md$', f)}

ECON = 'hobby/economy-and-finance'
econ_mods = chapters(ECON)
bad = collections.Counter(); details = []

for path in sorted(glob.glob('courses/**/*.md', recursive=True)+glob.glob(ECON+'/**/*.md', recursive=True)+glob.glob('upskill-readings/**/*.md', recursive=True)):
    if path.endswith('plan.md'): continue
    t = re.sub(r'```.*?```', ' ', open(path).read(), flags=re.S)
    parts = path.split('/')
    # ---- Ch<N> §<M>  (within the same course module)
    if parts[0] == 'courses':
        mod_dir = '/'.join(parts[:2]); ch = chapters(mod_dir)
        for m in re.finditer(r'(?<![Mm]\d)(?<![Mm]\d\d\s)Ch(\d+)\s+§(\d+)', t):
            c, s = int(m.group(1)), int(m.group(2))
            if c not in ch: details.append((path, m.group(0), f"chapter {c} does not exist in {mod_dir}")); bad['ch']+=1; continue
            if s not in sections(os.path.join(mod_dir, ch[c])): details.append((path, m.group(0), f"no section {s} in {ch[c]}")); bad['ch']+=1
    # ---- M<NN> Ch<N> §<M>
    for m in re.finditer(r'M(\d{2})\s+Ch(\d+)\s+§(\d+)', t):
        mm, c, s = m.group(1), int(m.group(2)), int(m.group(3))
        mods = {d[:2]: d for d in os.listdir('courses') if re.match(r'\d\d-', d)}
        if mm not in mods: details.append((path, m.group(0), f"module {mm} not found")); bad['m']+=1; continue
        ch = chapters('courses/'+mods[mm])
        if c not in ch: details.append((path, m.group(0), f"no chapter {c} in M{mm}")); bad['m']+=1; continue
        if s not in sections(f"courses/{mods[mm]}/{ch[c]}"): details.append((path, m.group(0), f"no section {s} in M{mm} Ch{c}")); bad['m']+=1
    # ---- E<NN> §<M>
    for m in re.finditer(r'E(\d{2})\s+§(\d+)', t):
        mm, s = int(m.group(1)), int(m.group(2))
        if mm not in econ_mods: details.append((path, m.group(0), f"econ module {mm} not found")); bad['e']+=1; continue
        if s not in sections(os.path.join(ECON, econ_mods[mm])): details.append((path, m.group(0), f"no section {s} in E{mm:02d}")); bad['e']+=1

FORWARD = ('E08', 'E09', 'E06 \u00a74', 'M04 Ch1 \u00a72', 'Ch1 \u00a73', 'Ch3 \u00a74', 'Ch4 \u00a74')
broken = [d for d in details if not any(d[1].startswith(f) for f in FORWARD)]
fwd    = [d for d in details if     any(d[1].startswith(f) for f in FORWARD)]
for p, ref, why in broken:
    print(f"  BROKEN  {p.split('/')[-1][:42]:44} {ref:16} {why}")
print(f"\nFORWARD refs to planned-but-unwritten material (OK): {len(fwd)}")
for ref, why in sorted({(d[1], d[2]) for d in fwd}):
    print(f"  forward  {ref:16} {why}")
print(f"\nBROKEN qualified refs: {len(broken)}")

import sys
sys.exit(1 if (total or len(broken)) else 0)
