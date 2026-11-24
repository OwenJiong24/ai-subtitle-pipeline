# Stylized / Top-Position Text

Dialogue translators typically handle only "Main"-style lines. This leaves
another layer untranslated: location signs, notices, big centre titles, and
other styled text.

## The problem

- A location sign may be `{\an8\pos(...)\fscx125}` — top-position, large font.
- It is often **animated**: the same words repeated across hundreds of frames
  with slightly different `\pos` values.
- A naive "translate every line" approach would (a) produce hundreds of
  duplicate translations and (b) flatten the position to the bottom.

## Workflow

### 1. Scan

```bash
python scripts/style_scan.py input.ass
```

Reports categories: `STYLE` (non-dialogue style), `AN8` (top-position),
`VECTOR` (drawn paths), `BIG` (large inline font overrides), `POS`.

### 2. Deduplicate

```bash
python scripts/style_dump.py input.ass style_targets.txt
```

Outputs one row per **unique text**: `reason|first_timestamp|style|text`.
A sign repeated 1564 times usually collapses to ~7 unique phrases.

### 3. Translate by unique text

Create `style_zh.txt`:

```
Captions|Gates of Justice|正义之门
Captions|Courthouse|法院
```

Use the glossary for sign terminology.

### 4. Splice preserving tags

```bash
python scripts/style_splice.py output.ass style_zh.txt --dry   # preview hit count
python scripts/style_splice.py output.ass style_zh.txt         # apply
```

`style_splice` replaces **only the visible text after the last override block**,
keeping every tag byte-for-byte: `\an8`, `\pos`, `\move`, `\fscx`, `\fn`, fades.
Matching is by `(style, normalized text)`, so all animated duplicates update.

### 5. What not to translate

- Karaoke / song lyrics / romaji — usually leave in source language.
- Credits / staff lists — usually leave in source language.
- Vector drawings — require separate typesetting work, not text translation.

Record deliberate exclusions in the audit log so they are not mistaken for gaps.

### Verification

- `audit_episode.py` reports the number of Chinese lines with `\an8` — confirm
  these are intentional signs, not accidentally flattened dialogue.
- Render a frame at the sign's first timestamp and check placement and size.
