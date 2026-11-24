#!/usr/bin/env python3
"""Measure subtitle-vs-audio sync using clean speech onsets.

Usage: python strict_sync.py translated.ass video.mkv
Needs ffmpeg + ffprobe on PATH. Reports median of (onset - subtitle_start)
using only lines preceded by >=0.4s of silence.
"""
import io, math, re, struct, subprocess, sys

SPOKEN = ("Main", "Secondary", "Narrator", "Thoughts", "Flashbacks",
          "FlashbackThoughts", "FlashbacksSecondary")
SR, HOP = 8000, 0.04


def sec(t):
    m = re.match(r"(\d+):(\d+):(\d+(?:\.\d+)?)", t)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0


def envelope(mkv):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", mkv, "-vn", "-ac", "1",
                        "-ar", str(SR), "-f", "s16le", "-"], capture_output=True)
    d, step = p.stdout, int(SR * HOP)
    out = []
    for i in range(0, len(d) - step, step):
        s = struct.unpack("<%dh" % (len(d[i * 2:(i + step) * 2]) // 2), d[i * 2:(i + step) * 2])
        out.append((sum(v * v for v in s) / max(1, len(s))) ** 0.5)
    return out


def starts(path):
    out = []
    for line in io.open(path, encoding="utf-8", errors="replace"):
        if not line.startswith("Dialogue:"):
            continue
        f = line.rstrip("\n").split(",", 9)
        if len(f) != 10 or not f[3].startswith(SPOKEN) or re.search(r"\\p[01]", f[9]):
            continue
        out.append(sec(f[1]))
    return out


zh, mkv = sys.argv[1], sys.argv[2]
env = envelope(mkv)
db = [20 * math.log10(max(1.0, v)) for v in env]
quiet = 20 * math.log10(300.0)
deltas = []
for t in starts(zh):
    i = int(t / HOP)
    if i < 12 or i >= len(db) or max(db[max(0, i - 10):i - 1]) > quiet:
        continue
    for j in range(i, min(len(db), i + 25)):
        if db[j] >= quiet + 6:
            deltas.append(j * HOP - t)
            break
if not deltas:
    print("no clean-onset samples")
else:
    d = sorted(deltas)
    n = len(d)
    print("samples=%d median=%+.2fs p10=%+.2fs p90=%+.2fs within0.35s=%.0f%%"
          % (n, d[n // 2], d[int(n * .1)], d[int(n * .9)],
             100.0 * len([x for x in d if abs(x) <= .35]) / n))
