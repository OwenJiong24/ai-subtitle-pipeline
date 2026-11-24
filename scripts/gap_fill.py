#!/usr/bin/env python3
"""Find and fill source-language leftovers in a generated subtitle file, by key.

Usage:
  python gap_fill.py --list source.ass output.ass gaps.txt
  python gap_fill.py --fill source.ass output.ass gaps_zh.txt output.ass
"""
import argparse, io, re

SPOKEN = ("Main", "Secondary", "Narrator", "Thoughts", "Flashbacks",
          "FlashbackThoughts", "FlashbacksSecondary")
CJK = re.compile(r"[\u4e00-\u9fff]")


def keyof(ts):
    m = re.match(r"(\d+):(\d+):(\d+)", ts)
    return "%d:%s:%s" % (int(m.group(1)), m.group(2), m.group(3)) if m else ts.strip()


def visible(t):
    return re.sub(r"\{[^{}]*\}", "", t).strip()


def dialogs(path):
    out = []
    for line in io.open(path, encoding="utf-8", errors="replace"):
        if line.startswith("Dialogue:"):
            f = line.rstrip("\n").split(",", 9)
            if len(f) == 10:
                out.append(f)
    return out


ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["--list", "--fill"])
ap.add_argument("src")
ap.add_argument("cur")
ap.add_argument("third")
ap.add_argument("out", nargs="?")
a = ap.parse_args()

src, cur = dialogs(a.src), dialogs(a.cur)
if a.mode == "--list":
    by = {}
    for f in cur:
        by.setdefault(keyof(f[1]), []).append(visible(f[9]))
    pos = {}
    gaps = []
    for f in src:
        if not f[3].startswith(SPOKEN) or re.search(r"\\p[01]", f[9]):
            continue
        k = keyof(f[1])
        i = pos.get(k, 0)
        txt = by.get(k, [])[i] if i < len(by.get(k, [])) else ""
        pos[k] = i + 1
        if not CJK.search(txt):
            gaps.append("%s|%s" % (k, re.sub(r"\s+", " ", visible(f[9]))))
    io.open(a.third, "w", encoding="utf-8").write("\n".join(gaps) + "\n")
    print("gaps:", len(gaps), "->", a.third)
else:
    new = {}
    for line in io.open(a.third, encoding="utf-8"):
        if "|" in line:
            k, v = line.rstrip("\n").split("|", 1)
            new.setdefault(k.strip(), []).append(v)
    by = {}
    for f in cur:
        by.setdefault(keyof(f[1]), []).append(visible(f[9]))
    pos, npos, out = {}, {}, []
    for f in src:
        k = keyof(f[1])
        i = pos.get(k, 0)
        curtxt = by.get(k, [])[i] if i < len(by.get(k, [])) else None
        pos[k] = i + 1
        if curtxt is not None and CJK.search(curtxt):
            val = curtxt
        else:
            j = npos.get(k, 0)
            lst = new.get(k, [])
            val = lst[j] if j < len(lst) else (curtxt or visible(f[9]))
            npos[k] = j + 1
        out.append(f"{k}|{val}")
    io.open(a.out, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("wrote", len(out), "translation entries")
