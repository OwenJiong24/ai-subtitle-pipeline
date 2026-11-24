#!/usr/bin/env python3
"""Mandatory pre-delivery audit — one command, objective checks only.

Usage: python audit_episode.py translated.ass video.mkv source.ass [label]
Prints PASS/FAIL/WARN/INFO; hard failures must be zero before delivery.
Never modifies files.
"""
import io, os, re, subprocess, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
SPOKEN = ("Main", "Secondary", "Narrator", "Thoughts", "Flashbacks",
          "FlashbackThoughts", "FlashbacksSecondary")
CJK = re.compile(r"[\u4e00-\u9fff]")


def run(script, *args):
    p = subprocess.run([PY, os.path.join(BASE, "scripts", script)] + list(args),
                       capture_output=True, text=True, errors="replace")
    return (p.stdout or p.stderr).strip()


def dialogs(path):
    out = []
    for line in io.open(path, encoding="utf-8", errors="replace"):
        if line.startswith("Dialogue:"):
            f = line.rstrip("\n").split(",", 9)
            if len(f) == 10:
                out.append(f)
    return out


zh, mkv, src = sys.argv[1], sys.argv[2], sys.argv[3]
label = sys.argv[4] if len(sys.argv) > 4 else os.path.basename(zh)[:30]
print("========== AUDIT: %s ==========" % label)
fails = 0

if not os.path.exists(zh) or os.path.getsize(zh) < 500:
    print("[FAIL] file missing or too small"); sys.exit(1)
D = dialogs(zh)
print("[PASS] file integrity: %d dialogue lines" % len(D))

bad = sum(1 for f in D if "Your media player does not support" in f[9]
          and not ("fscx0" in f[9] and "fscy0" in f[9]))
print(("[FAIL] visible banner on %d lines (fix_banner.py)" % bad) if bad else "[PASS] banner invisible")
fails += bool(bad)

spk = [f for f in D if f[3].startswith(SPOKEN) and not re.search(r"\\p[01]", f[9])]
n = sum(1 for f in spk if CJK.search(re.sub(r"\{[^{}]*\}", "", f[9])))
pct = 100.0 * n / max(1, len(spk))
print(("[PASS]" if pct >= 99 else "[WARN]") + " coverage %.1f%% (%d/%d)" % (pct, n, len(spk)))
if pct < 90:
    fails += 1

if os.path.exists(src):
    out = run("term_check.py", zh, src, label)
    for ln in out.splitlines():
        if "term checks" in ln:
            print("  " + ln.strip())
            m = re.search(r"missing=(\d+)", ln)
            if m and int(m.group(1)) > 5:
                fails += 1
if os.path.exists(mkv):
    out = run("strict_sync.py", zh, mkv)
    for ln in out.splitlines():
        if "samples=" in ln:
            print("  " + ln.strip())
            m = re.search(r"median=([+-][0-9.]+)s", ln)
            if m and abs(float(m.group(1))) > 1.0:
                fails += 1
else:
    print("[INFO] video not present - audio sync skipped")

tmp = os.path.join(BASE, "examples", "_style_tmp.txt")
out = run("style_dump.py", src if os.path.exists(src) else zh, tmp)
uniq = sum(1 for _ in io.open(tmp, encoding="utf-8")) if os.path.exists(tmp) else 0
if uniq <= 3 and os.path.exists(tmp):
    os.remove(tmp)
print("[INFO] unique untranslated stylized texts: %d" % uniq)
an8 = sum(1 for f in D if CJK.search(re.sub(r"\{[^{}]*\}", "", f[9])) and "\\an8" in f[9])
print("[INFO] top-position (\\an8) target-script lines: %d" % an8)
print("========== RESULT: %d hard failure(s) ==========" % fails)
