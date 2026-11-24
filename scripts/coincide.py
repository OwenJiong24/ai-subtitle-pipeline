#!/usr/bin/env python3
"""Coincidence test: do source-language line starts align with a reference track?

Usage: python coincide.py base.ass reference.ass
Useful when the video has no embedded track: an official subtitle in another
language from the same release shares the timeline. In-sync pairs show a
coincidence rate clearly above chance.
"""
import bisect, io, re, sys

SPOKEN = ("Main", "Secondary", "Narrator", "Thoughts", "Flashbacks", "FlashbackThoughts", "FlashbacksSecondary")


def sec(t):
    m = re.match(r"(\d+):(\d+):(\d+(?:\.\d+)?)", t)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0


def starts(path):
    out = []
    for line in io.open(path, encoding="utf-8", errors="replace"):
        if not line.startswith("Dialogue:"):
            continue
        f = line.rstrip("\n").split(",", 9)
        if len(f) != 10 or not f[3].startswith(SPOKEN) or re.search(r"\\p[01]", f[9]):
            continue
        out.append(sec(f[1]))
    return sorted(out)


a, b = starts(sys.argv[1]), starts(sys.argv[2])
if not a or not b:
    print("no starts"); sys.exit(0)
hit = 0
for t in a:
    i = bisect.bisect_left(b, t)
    cand = [abs(b[j] - t) for j in (i - 1, i) if 0 <= j < len(b)]
    if cand and min(cand) <= 1.5:
        hit += 1
chance = min(100.0, 100.0 * len(b) * 3.0 / max(1.0, b[-1] - b[0]))
print("base=%d ref=%d coincidence=%.1f%% chance~%.1f%%" % (len(a), len(b), 100.0 * hit / len(a), chance))
