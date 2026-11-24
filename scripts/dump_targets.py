#!/usr/bin/env python3
"""Dump translatable dialogue lines from an ASS file.

Usage: python dump_targets.py input.ass targets.txt [--styles Main,Secondary,...]
Output: key|style|text  (key = H:MM:SS from integer start)
"""
import argparse, io, re

DEFAULT = ("Main", "Secondary", "Narrator", "Thoughts", "Flashbacks",
           "FlashbackThoughts", "FlashbacksSecondary", "Note", "Notes",
           "Title", "Warning")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--styles", default=",".join(DEFAULT))
    a = ap.parse_args()
    styles = tuple(s.strip() for s in a.styles.split(",") if s.strip())
    rows = []
    for line in io.open(a.src, encoding="utf-8", errors="replace"):
        if not line.startswith("Dialogue:"):
            continue
        f = line.rstrip("\n").split(",", 9)
        if len(f) != 10:
            continue
        if not f[3].strip().startswith(styles):
            continue
        t = f[9]
        if re.search(r"\\p[01]", t) or "\\an8" in t:
            continue
        m = re.match(r"(\d+):(\d+):(\d+)", f[1])
        if not m:
            continue
        key = "%d:%s:%s" % (int(m.group(1)), m.group(2), m.group(3))
        txt = re.sub(r"\{[^{}]*\}", "", re.sub(r"\{\{[^{}]*\}\}", "", t)).strip()
        rows.append("%s|%s|%s" % (key, f[3].strip(), txt))
    with io.open(a.out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(rows) + "\n")
    print("dumped", len(rows), "lines ->", a.out)


main()
