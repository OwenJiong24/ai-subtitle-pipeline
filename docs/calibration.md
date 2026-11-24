# Timeline Calibration

Timeline drift is the most damaging and least obvious failure: the subtitle file
is real, the translation is correct, but the lines land at the wrong picture.

## Symptom

- "Subtitles are mounted but don't match the picture."
- "It worked for earlier episodes, now it doesn't."
- The first line is close, but later lines drift progressively or jump in steps.

## Root cause

The subtitle file and the video are **different edits of the same work** —
e.g. a TV broadcast script used against a re-edited release, with extra
eyecatches/previews removed. Drift is often *piecewise constant*, not linear:
0 → −1 → −11 → −12 → −17 seconds across the episode. Checking only the first
line is not enough.

## Step 1 — Enumerate tracks

```bash
ffprobe -v error -select_streams s -show_entries stream=index:stream_tags=language,title -of csv=p=0 video.mkv
```

Pick the track whose language and style set match the dialogue. If there is an
embedded track, extract it:

```bash
ffmpeg -y -v error -i video.mkv -map 0:s:0 -c:s copy truth.ass
```

**Gotcha:** `ffmpeg -ss` before `-i` resets timestamps and produces phantom
"no subtitles" frames. Put `-ss` after `-i` for burn-in checks.

## Step 2 — Measure drift objectively

```bash
python scripts/audit_align.py old_base.ass truth.ass
```

Prints `old / truth / matched / delta(min,median,max) / lines beyond 1.5s`.
A healthy pair has median ≈0 and few outliers. A drifted pair has a large
median or a wide min–max span.

Alternative when no embedded track exists: compare your English base against
an official subtitle in another language from the same release:

```bash
python scripts/coincide.py base.ass other_language.ass
```

In-sync pairs show a coincidence rate clearly above chance; drifted pairs fall
to roughly the random rate.

## Step 3 — Rebase

If the translation is trustworthy but the timeline is not:

```bash
python scripts/rebase.py --old old_base.ass --truth truth.ass \
    --trans trans_dir --video video.mkv --margin 40
```

It DP-aligns old English → truth English, carries the Chinese/target values
across in order, splices a new file, and overwrites the sidecar with the truth
so future runs use the corrected baseline.

If the mapping itself is untrustworthy (large structural edits), **retranslate
against the truth script line by line** instead of migrating values.

## Step 4 — Verify

```bash
python scripts/strict_sync.py translated.ass video.mkv
```

Uses only clean onsets (≥0.4 s of preceding silence) and reports the median
of `onset − subtitle_start`. A healthy baseline is roughly +0.2 to +0.5 s
(subtitles start slightly before the voice, which is normal). Values beyond
±1 s indicate a problem.

## Baseline discipline

- Record the chosen baseline per episode in the audit log.
- Changing the baseline requires overwriting the sidecar too.
- Never use "first line matches" as proof of sync.
