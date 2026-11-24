# Full Pipeline

This is the end-to-end workflow. Run it per episode. Every step writes a file
you can inspect — no hidden state.

## 0. Establish the source of truth

Before translating anything, answer: **which subtitle track matches this video?**

```bash
ffprobe -v error -select_streams s -show_entries stream=index:stream_tags=language,title -of csv=p=0 video.mkv
```

Priority for the authoritative track:

1. An embedded subtitle track in the video that matches the language and dialogue style set.
2. A structured release script from the same release as the video.
3. Any loose subtitle file sitting next to the video — **only if verified** (see [calibration.md](calibration.md)).

Record the choice in an audit log. If you later change it, re-run everything.

## 1. Dump translatable lines

```bash
python scripts/dump_targets.py input.ass targets.txt
```

Output format: `key|style|text`, where `key = H:MM:SS` from the integer start time.
Styles that are dialogue-like (Main, Secondary, Narrator, Thoughts, etc.), plus
Title/Warning, are included. Vectors (`\p0/\p1`), `\an8` top text, and non-dialogue
styles are excluded by default — they are handled separately (see [stylized-text.md](stylized-text.md)).

## 2. Translate

Fill `translations.txt` with `key|中文/目标语言`, following the [glossary](glossary.md).
Rules:

- One line per source dialogue line. Same-second multiple lines must appear in
  **source-file order** (a dict would silently keep only the last value).
- Keep `\N` line breaks from the source.
- Empty-text dialogue lines still consume a value — provide a placeholder.

## 3. Pre-splice gates

```bash
python scripts/check_keys.py input.ass translations.txt
```

- `MISSING = 0` (every required line has a translation).
- Orphans limited to Title duplicate keys / intentional placeholders.
- Latin-residue gate: no leftover English words except proper nouns / codes.

## 4. Splice

```bash
python scripts/splice.py input.ass translations.txt output.ass --margin 40
```

The splicer reads `PlayResX/PlayResY` from the source header and places each
translated line at `(PW/2, PH - margin - 27)`, bottom-centre. Use a larger margin
(e.g. 66) when the picture has burned-in subtitles at the bottom.

Only dialogue/title/warning styles consume translations; signs, credits, karaoke,
and lyrics stay in the source language. Invisible player-compatibility banners
are left untouched.

## 5. Gap fill (if the generated file still has source-language lines)

```bash
python scripts/gap_fill.py --list input.ass output.ass gaps.txt
# translate gaps.txt -> gaps_zh.txt (key|中文)
python scripts/gap_fill.py --fill input.ass output.ass gaps_zh.txt output.ass
```

This matches by **key**, not line number, so it survives re-time ordering.

## 6. Mandatory audit

```bash
python scripts/audit_episode.py output.ass video.mkv input.ass
```

Hard failures must be zero before the episode is called done. See [audit.md](audit.md).

## 7. Visual spot-check

Render a single silent frame with a separate player process:

```bash
mpv --no-audio --vo=image --vo-image-format=png --vo-image-outdir=frames \
    --frames=1 --hr-seek=yes --start=00:05:00 video.mkv
```

Check that the translated line is visible, positioned correctly, and not
covered by burned-in text. Never disturb a player the user is actively watching.
