# AI Subtitle Pipeline

[中文版](README.zh-CN.md) · [License](LICENSE)

A local-first, auditable pipeline for AI-assisted subtitle translation. It turns
a source subtitle file (`*.ass`) and a video into a translated subtitle file,
with objective checks that catch the three things naive translation misses:
**terminology drift**, **timeline drift**, and **untranslated stylized text**.

## Why this exists

Translating a subtitle line is easy. Translating a *series* correctly is not:

- The same character name gets three different renderings across episodes.
- The subtitle file and the video turn out to be different edits of the same
  work; the first line is close but the middle drifts by tens of seconds.
- Top-position notices, location signs, and large centre text stay in the
  original language because the main dialogue translator skips non-dialogue
  styles.

This pipeline adds a glossary, a timeline baseline, a style-preserving splice,
and a mandatory pre-delivery audit to fix those.

## Features

- **Glossary-first** — a locked term table that every translation must obey,
  plus an automated consistency check.
- **Timeline calibration** — measure drift by aligning dialogue text and by
  comparing subtitle starts to audio onsets; rebase onto the authoritative track.
- **Style-preserving splice** — translate only the visible text; keep every
  ASS override tag (`\an8`, `\pos`, `\move`, `\fscx`, fades) intact.
- **Mandatory audit** — one command checks file integrity, warning banners,
  language coverage, term consistency, audio sync, and stylized gaps.
- **Local-first & offline** — plain Python scripts on local files; nothing is
  uploaded.

## Install

No dependencies beyond Python 3 and (for the audio sync check) `ffmpeg` /
`ffprobe` on `PATH`.

```bash
git clone https://github.com/OwenJiong24/ai-subtitle-pipeline.git
cd ai-subtitle-pipeline
python scripts/dump_targets.py --help
```

## Usage

```bash
# 1. Dump the lines that need translation
python scripts/dump_targets.py input.ass targets.txt

# 2. Translate: edit targets.txt into translations.txt (key|text)

# 3. Splice translations back into a new subtitle file
python scripts/splice.py input.ass translations.txt output.ass --margin 40

# 4. Mandatory audit before delivery
python scripts/audit_episode.py output.ass video.mkv input.ass
```

Detailed guides:

- [Full pipeline](docs/pipeline.md)
- [Building a term glossary](docs/glossary.md)
- [Timeline calibration](docs/calibration.md)
- [Stylized / top-position text](docs/stylized-text.md)
- [Audit reference](docs/audit.md)
- [Anonymized case study](docs/case-study.md)

## Layout

```
ai-subtitle-pipeline/
├── SKILL.md                 # agent skill definition
├── README.md                # this file (English)
├── README.zh-CN.md          # optional Chinese overview
├── LICENSE                  # MIT
├── docs/
│   ├── pipeline.md
│   ├── glossary.md
│   ├── calibration.md
│   ├── stylized-text.md
│   ├── audit.md
│   └── case-study.md
├── scripts/
│   ├── dump_targets.py
│   ├── splice.py
│   ├── check_keys.py
│   ├── gap_fill.py
│   ├── audit_align.py
│   ├── strict_sync.py
│   ├── term_check.py
│   ├── style_scan.py
│   ├── style_splice.py
│   ├── fix_banner.py
│   ├── coverage.py
│   └── audit_episode.py
└── examples/
    └── demo.ass             # synthetic, no copyrighted content
```

## Contributing

Issues and PRs welcome. Please keep examples synthetic — do not commit
copyrighted subtitle content or media.

## License

MIT — see [LICENSE](LICENSE).
