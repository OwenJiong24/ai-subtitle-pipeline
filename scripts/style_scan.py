#!/usr/bin/env python3
r"""Scan an ASS file for lines the main dialogue translator does not handle.

Usage: python style_scan.py input.ass
Categories: STYLE (non-dialogue style), AN8 (top position), VECTOR (\p drawings),
BIG (large inline font), POS (explicit \pos override).
"""
import io, re, sys, collections

DLG = ("Main", "Secondary", "Narrator", "Thoughts", "Flashbacks", "FlashbackThoughts",
       "FlashbacksSecondary", "Note", "Notes", "Title", "Warning")
counts = collections.Counter()
for line in io.open(sys.argv[1], encoding="utf-8", errors="replace"):
    if not line.startswith("Dialogue:"):
        continue
    f = line.rstrip("\n").split(",", 9)
    if len(f) != 10:
        continue
    st, t = f[3].strip(), f[9]
    if re.search(r"\\p[01]", t):
        cat = "VECTOR"
    elif "\\an8" in t:
        cat = "AN8"
    elif not st.startswith(DLG):
        cat = "STYLE"
    elif re.search(r"\\pos\(", t):
        cat = "POS"
    elif re.search(r"\\fsc[xy]\s*(1[4-9]\d|[2-9]\d\d)|\\fs([5-9]\d|\d{3})", t):
        cat = "BIG"
    else:
        continue
    counts[cat] += 1
print(" ".join("%s=%d" % (k, v) for k, v in counts.most_common()))
