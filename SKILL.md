---
name: ai-subtitle-pipeline
description: Local-first subtitle translation pipeline for AI-assisted workflows — build a term glossary, translate dialogue, calibrate timeline drift, preserve stylized signs, and audit before delivery. Use when translating subtitles for video, when subtitles are out of sync, when a translation has terminology drift, or when top-position / large centre text stays untranslated. English primary with optional Chinese.
version: 1.0.0
license: MIT
---

# AI Subtitle Pipeline

A local-first, auditable workflow for translating subtitles with AI assistance.
It is deliberately tool-agnostic: it works on any `.ass` subtitle file paired
with any video, and every step produces a file you can inspect.

The pipeline fixes three failure modes that ordinary "translate this SRT" flows
do not catch:

1. **Terminology drift** — the same name/technique translated differently per episode.
2. **Timeline drift** — the subtitle file and the video come from different edits
   of the same work, so lines are subtly (or wildly) out of sync.
3. **Stylized text loss** — top-position notices, signs, and large centre text are
   silently left in the source language.

## When to use

- Translating a video's subtitles into another language, especially episode series.
- Subtitles that "look mounted but don't match the picture".
- A translation whose names/terms drift between episodes.
- Signs/titles that stay untranslated because the main translator skips them.

## Core principles

- **Never claim done on trust.** Every episode ends with an objective audit.
- **Keep the source of truth explicit.** Record which subtitle track is authoritative.
- **Preserve formatting.** Translate text, not tags. `\an8`, `\pos`, `\move`,
  `\fscx`, fade, and karaoke timing survive untouched.
- **Local-first.** All scripts run offline on files you already have; no upload.

## Quick start

```bash
python scripts/dump_targets.py INPUT.ass targets.txt
# fill targets.txt -> translations.txt (key|text)
python scripts/splice.py INPUT.ass translations.txt OUTPUT.ass --margin 40
python scripts/audit_episode.py OUTPUT.ass VIDEO.mkv INPUT.ass
```

See [docs/pipeline.md](docs/pipeline.md) for the full workflow and
[docs/calibration.md](docs/calibration.md) for timeline drift.

## Files

| Path | Purpose |
|---|---|
| `docs/pipeline.md` | End-to-end workflow (dump → translate → splice → audit) |
| `docs/glossary.md` | Build and enforce a term glossary |
| `docs/calibration.md` | Detect and repair timeline drift |
| `docs/stylized-text.md` | Top-position, signs, large centre text |
| `docs/audit.md` | The mandatory pre-delivery audit |
| `scripts/` | Parameter-driven Python tools (no hardcoded paths) |
| `examples/` | A small synthetic example (no copyrighted material) |

## Case study

A short, anonymized case study is in [docs/case-study.md](docs/case-study.md):
how an episodic animated series exposed all three failure modes, and how the
audit caught them. No source material is included.

## 中文

本 skill 的中文概览见 [README.zh-CN.md](README.zh-CN.md)。
