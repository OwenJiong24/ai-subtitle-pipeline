# Mandatory Pre-Delivery Audit

Run this before calling any episode done. This gate was added after an incident
where an episode had correct-looking translation files but was unusable in
playback. **Do not skip it, and do not edit code before reading its numbers.**

```bash
python scripts/audit_episode.py translated.ass video.mkv source.ass label
```

## Checks

1. **File integrity** — file exists, non-trivial size, has dialogue lines.
2. **Warning banner** — any player-compatibility banner must keep its invisible
   tags (`\fscx0\fscy0\clip`). A visible full-screen banner makes an episode
   look "completely broken". Repair with `fix_banner.py`.
3. **Language coverage** — % of speaking-style lines containing target-script
   characters. Full coverage or explicit recorded exceptions (lyrics/credits).
4. **Term consistency** — `term_check` missing count ≤5%. A spike means target
   text was mapped to the wrong source lines.
5. **Audio sync** — `strict_sync` median of `onset − subtitle_start` must be
   within ±1 s.
6. **Stylized gaps** — count of unique untranslated sign/title texts.
7. **Top-position sanity** — target-script lines with `\an8` should be
   intentional signs, not flattened dialogue.

Hard failures must be zero.

## When to re-run

- After generating or regenerating the subtitle file.
- After changing the baseline source.
- After a gap-fill pass.
- Whenever a viewer says "this looks wrong" — measure first, then change code.

## Red-line triage

| Symptom | First action |
|---|---|
| Low coverage | `gap_fill.py --list` → translate → `--fill` |
| Term mismatch high | re-check alignment / same-key order; worst case retranslate |
| Sync median >1 s | `audit_align.py`, then `rebase.py` / `retime.py` |
| Visible banner | `fix_banner.py` |
| Stylized untranslated | follow [stylized-text.md](stylized-text.md) |

## Keep a record

Save each run to `audit_<episode>.txt` with the baseline source, coverage, sync
median, term mismatches, stylized gap count, and hard failure count. This makes
cross-episode comparison and post-mortem possible.
