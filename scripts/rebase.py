#!/usr/bin/env python3
"""Rebase an existing translation onto an authoritative timeline.

Usage: python rebase.py --old base.ass --truth truth.ass --trans trans_dir \
            --video video.mkv --margin 40 [--arc "Enies Lobby"]
DP-aligns base English to truth English, carries target values across in order,
splices a new subtitle next to the video, and overwrites the sidecar with truth.
"""
import argparse, io, os, re, subprocess, sys
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
    return pairs


ap = argparse.ArgumentParser()
ap.add_argument("--old", required=True)
ap.add_argument("--truth", required=True)
ap.add_argument("--trans", required=True)
ap.add_argument("--video", required=True)
ap.add_argument("--margin", default="40")
ap.add_argument("--arc", default="Default")
a = ap.parse_args()

old, tru = targets(a.old), targets(a.truth)
trans = {}
for fn in sorted(os.listdir(a.trans)):
    if fn.endswith(".txt"):
        for line in io.open(os.path.join(a.trans, fn), encoding="utf-8"):
            if "|" in line:
                k, v = line.rstrip("\n").split("|", 1)
                trans.setdefault(k.strip(), []).append(v)
vals, idx = [], {}
for k, _ in old:
    lst = trans.get(k)
    if not lst:
        vals.append(None); continue
    i = idx.get(k, 0)
    vals.append(lst[i] if i < len(lst) else lst[-1])
    idx[k] = i + 1
pairs = align(old, tru)
out = ["%s|%s" % (tru[j][0], vals[i]) for i, j in pairs if vals[i]]
tmp = os.path.join(os.path.dirname(a.video), "_rebase_tmp")
os.makedirs(tmp, exist_ok=True)
for f in os.listdir(tmp):
    os.remove(os.path.join(tmp, f))
io.open(os.path.join(tmp, "all.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("base=%d translated=%d aligned=%d -> %d truth=%d"
      % (len(old), len([v for v in vals if v]), len(pairs), len(out), len(tru)))
stem = os.path.splitext(os.path.basename(a.video))[0]
r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "splice.py"),
                    a.truth, os.path.join(tmp, "all.txt"), a.video[:-4] + ".zh.ass",
                    "--margin", a.margin], capture_output=True, text=True)
print((r.stdout or r.stderr).strip()[:180])
sidecar = a.video[:-4] + ".en.ass"
if os.path.abspath(sidecar) != os.path.abspath(a.truth):
    with io.open(sidecar, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(io.open(a.truth, encoding="utf-8").read())
    print("sidecar <-", os.path.basename(a.truth))
else:
    print("sidecar already is truth")
