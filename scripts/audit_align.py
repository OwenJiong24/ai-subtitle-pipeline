#!/usr/bin/env python3
"""Align two subtitle files by dialogue text and report timing drift.

Usage: python audit_align.py old.ass truth.ass
Uses Needleman-Wunsch on normalized text; prints delta min/median/max and
how many matched lines are more than 1.5 s off.
"""
import io, re, sys
from difflib import SequenceMatcher

DLG = ("Main", "Secondary", "Narrator", "Thoughts", "Flashbacks", "FlashbackThoughts",
       "FlashbacksSecondary", "Note", "Notes")


def sec(k):
    p = k.split(":")
    return int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2])


def targets(path):
    out = []
    for line in io.open(path, encoding="utf-8", errors="replace"):
        if not line.startswith("Dialogue:"):
            continue
        f = line.rstrip("\n").split(",", 9)
        if len(f) != 10 or not f[3].startswith(DLG):
            continue
        if re.search(r"\\p[01]", f[9]) or "\\an8" in f[9]:
            continue
        m = re.match(r"(\d+):(\d+):(\d+)", f[1])
        if not m:
            continue
        txt = re.sub(r"\{[^{}]*\}", "", re.sub(r"\{\{[^{}]*\}\}", "", f[9])).strip()
        out.append(("%d:%s:%s" % (int(m.group(1)), m.group(2), m.group(3)), txt))
    return out


def sim(a, b):
    na = re.sub(r"[^a-z0-9 ]", "", a.lower()).strip()
    nb = re.sub(r"[^a-z0-9 ]", "", b.lower()).strip()
    if not na or not nb:
        return 0.0
    return 1.0 if na == nb else SequenceMatcher(None, na[:90], nb[:90]).ratio()


def align(old, tru):
    n, m = len(old), len(tru)
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    bt = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            s = sim(old[i - 1][1], tru[j - 1][1])
            sm = s * 3 - 0.35 if s >= 0.55 else -1e9
            best, b = dp[i - 1][j - 1] + sm, 1
            if dp[i - 1][j] + 0.25 > best:
                best, b = dp[i - 1][j] + 0.25, 2
            if dp[i][j - 1] + 0.25 > best:
                best, b = dp[i][j - 1] + 0.25, 3
            dp[i][j], bt[i][j] = best, b
    i, j, pairs = n, m, []
    while i > 0 and j > 0:
        b = bt[i][j]
        if b == 1:
            pairs.append((i - 1, j - 1)); i -= 1; j -= 1
        elif b == 2:
            i -= 1
        else:
            j -= 1
    pairs.reverse()
    return pairs, lambda p: sec(tru[p[1]][0]) - sec(old[p[0]][0])


old, tru = targets(sys.argv[1]), targets(sys.argv[2])
pairs, d = align(old, tru)
ds = sorted(d(p) for p in pairs)
if not ds:
    print("no aligned pairs"); sys.exit(0)
med = ds[len(ds) // 2]
print("old=%d truth=%d matched=%d (%.1f%%)  delta[min/med/max]=%+d/%+d/%+d s  >1.5s=%d"
      % (len(old), len(tru), len(ds), 100.0 * len(ds) / max(1, len(old)),
         ds[0], med, ds[-1], len([x for x in ds if abs(x) > 1.5])))
