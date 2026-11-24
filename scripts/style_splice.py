#!/usr/bin/env python3
"""Translate styled text while preserving every ASS override tag byte-for-byte.

Usage: python style_splice.py input.ass translations.txt [--dry]
Translations file: style|source_text|target_text
Matching by (style, normalized text); all animated duplicates are updated.
"""
import argparse, io, re


def norm(t):
    t = re.sub(r"\{[^{}]*\}", "", re.sub(r"\{\{[^{}]*\}\}", "", t))
    return re.sub(r"\s+", " ", t.replace("\\N", " ").replace("\\n", " ").replace("\\h", " ")).strip()


def split_override(t):
    m = re.match(r"^((?:\{[^{}]*\})*)", t)
    return (m.group(1), t[m.end():]) if m else ("", t)


ap = argparse.ArgumentParser()
ap.add_argument("ass")
ap.add_argument("trans")
ap.add_argument("--dry", action="store_true")
a = ap.parse_args()

mapping = {}
for line in io.open(a.trans, encoding="utf-8"):
    line = line.rstrip("\n")
    if not line or line.startswith("#"):
        continue
    p = line.split("|", 2)
    if len(p) == 3:
        mapping[(p[0].strip(), norm(p[1]).lower())] = p[2].strip()
print("entries:", len(mapping))

lines = io.open(a.ass, encoding="utf-8").read().split("\n")
hits = 0
for i, ln in enumerate(lines):
    if not ln.startswith("Dialogue:"):
        continue
    f = ln.split(",", 9)
    if len(f) != 10:
        continue
    pre, vis = split_override(f[9])
    zh = mapping.get((f[3].strip(), norm(vis).lower()))
    if zh is None:
        continue
    lines[i] = ",".join(f[:9]) + "," + pre + zh
    hits += 1
print("rewritten lines:", hits)
if hits and not a.dry:
    with io.open(a.ass, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    print("written:", a.ass)
