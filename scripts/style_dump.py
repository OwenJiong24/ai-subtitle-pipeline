#!/usr/bin/env python3
"""Dedup untranslated stylized text into one row per unique phrase.

Usage: python style_dump.py input.ass out.txt
Output: reason|first_ts|style|text
"""
import io, re, sys

DLG = ("Main", "Secondary", "Narrator", "Thoughts", "Flashbacks", "FlashbackThoughts",
       "FlashbacksSecondary", "Note", "Notes", "Title", "Warning")


def norm(t):
    t = re.sub(r"\{[^{}]*\}", "", re.sub(r"\{\{[^{}]*\}\}", "", t))
    return re.sub(r"\s+", " ", t.replace("\\N", " ").replace("\\n", " ")).strip()


seen = {}
for line in io.open(sys.argv[1], encoding="utf-8", errors="replace"):
    if not line.startswith("Dialogue:"):
        continue
    f = line.rstrip("\n").split(",", 9)
    if len(f) != 10:
        continue
    st, t, txt = f[3].strip(), f[9], norm(f[9])
    if not txt or "Your media player does not support" in txt:
        continue
    reason = None
    if re.search(r"\\p[01]", t):
        reason = "VECTOR"
    elif not st.startswith(DLG):
        reason = "STYLE"
    elif "\\an8" in t:
        reason = "AN8"
    if not reason:
        continue
    seen.setdefault((st, txt.lower()), (f[1], st, txt, reason))
rows = ["%s|%s|%s|%s" % v for v in sorted(seen.values(), key=lambda x: (x[3], x[1], x[0]))]
io.open(sys.argv[2], "w", encoding="utf-8").write("\n".join(rows) + "\n")
print("unique:", len(rows), "->", sys.argv[2])
