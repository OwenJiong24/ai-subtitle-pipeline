#!/usr/bin/env python3
"""Check that translated lines carry the proper nouns their source lines have.

Usage: python term_check.py translated.ass source.ass [--terms terms.txt]
Default: built-in generic term list; supply --terms for a project glossary
with lines "source_term|target_term".
"""
import io, re, sys

DEFAULT = [
    ("captain", "船长"), ("marine", "海军"), ("king", "王"), ("pirate", "海贼"),
    ("ship", "船"), ("sword", "剑"), ("devil fruit", "恶魔果实"),
]
DLG = ("Main", "Secondary", "Narrator", "Thoughts", "Flashbacks", "FlashbackThoughts",
       "FlashbacksSecondary", "Note", "Notes")


def lines(path):
    out = []
    for line in io.open(path, encoding="utf-8", errors="replace"):
        if not line.startswith("Dialogue:"):
            continue
        f = line.rstrip("\n").split(",", 9)
        if len(f) != 10 or not f[3].strip().startswith(DLG + ("Title", "Warning")):
            continue
        if re.search(r"\\p[01]", f[9]) or "\\an8" in f[9]:
            continue
        out.append(re.sub(r"\{[^{}]*\}", "", re.sub(r"\{\{[^{}]*\}\}", "", f[9])).strip())
    return out


terms = list(DEFAULT)
if "--terms" in sys.argv:
    i = sys.argv.index("--terms")
    for line in io.open(sys.argv[i + 1], encoding="utf-8"):
        if "|" in line:
            a, b = line.rstrip("\n").split("|", 1)
            terms.append((a.strip(), b.strip()))

paths = [p for p in sys.argv[1:] if p not in ("--terms",) and not p.endswith(".txt") or p == sys.argv[1]]
zh, en = lines(sys.argv[1]), lines(sys.argv[2])
checks = bad = 0
samples = []
for z, e in zip(zh, en):
    for a, b in terms:
        if a.lower() in e.lower():
            checks += 1
            if b.lower() not in z.lower():
                bad += 1
                if len(samples) < 5:
                    samples.append((e[:44], z[:30], b))
print("term checks=%d missing=%d (%.1f%%)" % (checks, bad, 100.0 * bad / max(1, checks)))
for e, z, b in samples:
    print("  SRC[%s] needs %s | TGT: %s" % (e, b, z))
