#!/usr/bin/env python3
"""Report target-script coverage per speaking-style line.

Usage: python coverage.py file.ass [--script CJK|latin]
Default CJK: [\u4e00-\u9fff].
"""
import io, re, sys

SPOKEN = ("Main", "Secondary", "Narrator", "Thoughts", "Flashbacks",
          "FlashbackThoughts", "FlashbacksSecondary")
CJK = re.compile(r"[\u4e00-\u9fff]")
LATIN = re.compile(r"[A-Za-z]{3,}")
path = sys.argv[1]
mode = "latin" if "--script latin" in " ".join(sys.argv) else "cjk"
pat = LATIN if mode == "latin" else CJK
tot = hit = 0
for line in io.open(path, encoding="utf-8", errors="replace"):
    if not line.startswith("Dialogue:"):
        continue
    f = line.rstrip("\n").split(",", 9)
    if len(f) != 10 or not f[3].startswith(SPOKEN) or re.search(r"\\p[01]", f[9]):
        continue
    txt = re.sub(r"\{[^{}]*\}", "", f[9])
    if not txt.strip():
        continue
    tot += 1
    if pat.search(txt):
        hit += 1
print("lines=%d matched=%d (%.1f%%) mode=%s" % (tot, hit, 100.0 * hit / max(1, tot), mode))
