# Case Study (Anonymized)

> A short, generalized case showing how the three failure modes appeared in a
> real series workflow. Names, titles, release groups, and source details are
> deliberately withheld. No source material is included.

## Context

A viewer was watching a long-running episodic animated series in a re-edited
release, with a translated subtitle file mounted alongside an embedded English
track. Early episodes looked fine; by one mid-series episode the subtitles became
"completely unusable".

## What the viewer reported

- Earlier episodes "mostly acceptable"; one episode "completely unusable".
- Subtitles appeared mounted in the player's track list but lines did not match
  the picture.
- Some top-of-frame signs and large centre text stayed untranslated.
- Names and technique terms varied between episodes.

## What the audit found

### 1. Timeline drift (the "completely unusable" cause)

The loose English subtitle file was a **different edit** of the same work from
the video. Measured by text alignment against the video's embedded track:

- First line offset: ~3 seconds (looked close — misleading).
- Median offset across the episode: **−27 seconds**.
- Outliers: up to −50 seconds.
- Essentially every dialogue line was misplaced.

Two later episodes had only ~1–2 s median drift with about 150 lines beyond
1.5 s — matching the viewer's "barely acceptable" description. Drift was
**piecewise constant**, jumping at edit points, not a simple linear offset.

### 2. Invisible banner made visible

The release includes a player-compatibility notice styled with invisible tags
(`\fscx0\fscy0\clip`). The translation step replaced its text but dropped the
invisible tags, so a 90-point white banner covered the screen for ten seconds
at the start. Combined with the drift, this made the episode look broken.

### 3. Terminology drift

A glossary did not exist. Character names and technique terms were coined
fresh per episode; two similarly named characters ended up with the same
rendered name, breaking a joke that depends on the distinction.

### 4. Stylized text loss

An animated location sign was repeated over a thousand times with tiny position
changes. The main translator skipped it because it was not a dialogue style,
so it stayed untranslated.

## Fixes applied

1. Selected the embedded track as the authoritative baseline; re-produced the
   translated file line-by-line against it (migrating old values was judged
   untrustworthy because the edit structure differed).
2. Fixed the banner handling so invisible tags are never dropped, and wrote a
   repair script for already-generated files.
3. Created a locked glossary with automated consistency checks.
4. Built a dedup + style-preserving splice for the animated sign.

## Verification numbers

- Audio-onset sync median: +0.25 s (healthy reference from a known-good episode: +0.32 s).
- Term consistency: 0 mismatches after re-translation (was ~5%).
- Target-script coverage: 100% for dialogue lines.
- Stylized sign: ~7 unique texts translated; all animated duplicates preserved.

## Lessons

- "Mounted and visible" does not mean "correctly timed".
- Checking only the first line is not sync verification.
- An audit that runs before delivery catches failures that manual review misses.
- Keep case studies generic — the pipeline is about the method, not any work.
