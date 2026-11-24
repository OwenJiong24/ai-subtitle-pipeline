#!/usr/bin/env python3
r"""Restore invisible tags on player-compatibility banners that a translator exposed.

Usage: python fix_banner.py file.ass [--dry] [more.ass ...]
The banner text starting with 'Your media player does not support' must be
invisible: {\org(0,0)\fscx0\fscy0\clip(0,0,0,0)}.
"""
import io, sys

INVIS = r"{\org(0,0)\fscx0\fscy0\clip(0,0,0,0)}Your media player does not support the subtitle format used in this episode.\NSubtitles will likely not function properly.\NPlease use one of the recommended video players, preferably mpv:\Nhttps://mpv.io"
dry = "--dry" in sys.argv
paths = [p for p in sys.argv[1:] if p != "--dry"]
total = 0
for p in paths:
    lines = io.open(p, encoding="utf-8").read().split("\n")
    n = 0
    for i, ln in enumerate(lines):
        if not ln.startswith("Dialogue:"):
            continue
        f = ln.split(",", 9)
        if len(f) != 10 or "Your media player does not support" not in f[9]:
            continue
        if "fscx0" in f[9] and "fscy0" in f[9]:
            continue
        lines[i] = ",".join(f[:9]) + "," + INVIS
        n += 1
    total += n
    if n:
        print(p, "repaired", n)
        if not dry:
            with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(lines))
print("total repaired:", total, "(dry=%s)" % dry)
