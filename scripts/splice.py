#!/usr/bin/env python3
"""Splice translations into an ASS file, preserving all override tags.

Usage: python splice.py input.ass translations.txt output.ass [--margin 40]
Translations file: key|text (key = H:MM:SS), duplicate keys consumed in order.
Only dialogue/title/warning styles consume translations; other styles untouched.
Invisible compatibility banners are left untouched.
"""
import argparse, io, re

DLG = ("Main", "Secondary", "Narrator", "Thoughts", "Flashbacks", "FlashbackThoughts",
       "FlashbacksSecondary", "Note", "Notes", "Title", "Warning")


def head_res(path):
    with io.open(path, encoding="utf-8") as f:
        head = "".join(f.readline() for _ in range(40))
    mx = re.search(r"PlayResX:\s*(\d+)", head)
    my = re.search(r"PlayResY:\s*(\d+)", head)
    return (int(mx.group(1)), int(my.group(1))) if mx and my else (1920, 1080)


def split_N(t):
    parts, buf, depth, i = [], "", 0, 0
    while i < len(t):
        c = t[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        if depth == 0 and t[i:i + 2] == "\\N":
            parts.append(buf); buf = ""; i += 2; continue
        buf += c; i += 1
    parts.append(buf)
    return parts


def set_margin(t, pw, ph, mv):
    parts = split_N(t)
    m = re.match(r"^\{([^}]*)\}", parts[0])
    if m:
        tags = re.sub(r"\\an\d", "", m.group(1))
        tags = re.sub(r"\\marginV[^\\}]*", "", tags)
        parts[0] = "{" + tags + "\\an2\\pos(" + str(pw // 2) + "," + str(ph - int(mv) - 27) + ")}" + parts[0][m.end():]
    else:
        parts[0] = "{\\an2\\pos(" + str(pw // 2) + "," + str(ph - int(mv) - 27) + ")}" + parts[0]
    return "\\N".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("trans")
    ap.add_argument("out")
    ap.add_argument("--margin", default="40")
    ap.add_argument("--font", default=None, help="optional font name override")
    a = ap.parse_args()
    pw, ph = head_res(a.src)
    trans = {}
    for line in io.open(a.trans, encoding="utf-8"):
        line = line.rstrip("\n")
        if "|" not in line:
            continue
        k, v = line.split("|", 1)
        trans.setdefault(k.strip(), []).append(v)
    out, used, consumed = [], 0, {}
    for line in io.open(a.src, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("Dialogue:"):
            f = line.split(",", 9)
            if len(f) == 10:
                m = re.match(r"(\d+):(\d+):(\d+)", f[1])
                key = ("%d:%s:%s" % (int(m.group(1)), m.group(2), m.group(3))) if m else f[1]
                vals = trans.get(key) or trans.get(f[1])
                zh = None
                if (vals and not re.search(r"\\p[01]", f[9]) and "\\an8" not in f[9]
                        and f[3].strip().startswith(DLG)
                        and "Your media player does not support" not in f[9]):
                    i = consumed.get(key, 0)
                    zh = vals[i] if i < len(vals) else vals[-1]
                    if i < len(vals):
                        consumed[key] = i + 1
                if zh:
                    seg = ("{\\fn" + a.font + "}" if a.font else "") + zh
                    f[9] = set_margin(seg, pw, ph, a.margin)
                    used += 1
                    line = ",".join(f)
        out.append(line)
    with io.open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")
    print("spliced", used, "lines ->", a.out)


main()
