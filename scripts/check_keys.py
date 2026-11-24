#!/usr/bin/env python3
"""Check translation keys against a source ASS file.

Usage: python check_keys.py source.ass translations.txt
Prints MISSING (source dialogue keys with no translation) and ORPHAN
(translation keys not used by the source).
"""
import io, re, sys

DLG = ("Main", "Secondary", "Narrator", "Thoughts", "Flashbacks", "FlashbackThoughts",
       "FlashbacksSecondary", "Note", "Notes", "Title", "Warning")


def keyof(ts):
    m = re.match(r"(\d+):(\d+):(\d+)", ts)
    return "%d:%s:%s" % (int(m.group(1)), m.group(2), m.group(3)) if m else ts.strip()


src, tr = sys.argv[1], sys.argv[2]
need = []
for line in io.open(src, encoding="utf-8", errors="replace"):
    if not line.startswith("Dialogue:"):
        continue
    f = line.rstrip("\n").split(",", 9)
    if len(f) != 10 or not f[3].strip().startswith(DLG):
        continue
    if re.search(r"\\p[01]", f[9]) or "\\an8" in f[9]:
        continue
    need.append(keyof(f[1]))

have = []
for line in io.open(tr, encoding="utf-8"):
    line = line.rstrip("\n")
    if "|" in line:
        have.append(line.split("|", 1)[0].strip())

from collections import Counter
cn, ch = Counter(need), Counter(have)
missing = {k: cn[k] - ch.get(k, 0) for k in cn if cn[k] > ch.get(k, 0)}
orphan = {k: ch[k] - cn.get(k, 0) for k in ch if ch[k] > cn.get(k, 0)}
print("MISSING (%d): %s" % (sum(missing.values()), missing))
print("ORPHAN  (%d): %s" % (sum(orphan.values()), orphan))
