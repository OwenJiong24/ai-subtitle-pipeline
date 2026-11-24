# Building a Term Glossary

The glossary is the single source of truth for names, techniques, places, and
fixed expressions. It is the main defence against "translation inaccurate in
later episodes" — AI translators otherwise invent a new rendering each time.

## Format

A Markdown table per category:

| Source term | Locked translation | Note |
|---|---|---|
| Captain | 船长 | rank, not "captain" |
| ... | ... | ... |

Keep categories: general rules, characters, places, techniques/abilities,
organizations/events, pitfalls.

## Rules

1. **Look up before translating.** Order: glossary → project notes → previously
   released episodes. Only invent when all three are empty.
2. **Write back immediately.** A newly coined term goes into the glossary the
   same session, with the episode/source noted.
3. **Resolve conflicts explicitly.** If an old episode used a different
   rendering, either fix the old episode or record both with a disambiguation
   note. Never leave two silent variants.
4. **No guessing placeholders as facts.** If unsure, write "not yet encountered;
   verify against released material before coining" rather than inventing.

## Pitfalls that actually happened

- Two characters with near-identical source names were both rendered with the
  same target name; the running joke that depends on the difference broke.
  Fixed by locking distinct renderings per character with a warning note.
- Latin residue (`Gatling`, `All Blue`) left in "translated" lines — caught by
  the Latin-residue gate.
- Honorifics (`-chan`, `-kun`, `-san`) rendered inconsistently across episodes.
  Lock a table of honorific → target wording.

## Automated check

```bash
python scripts/term_check.py translated.ass source.ass
```

Reports `term checks=N missing=M`. Keep missing ≤5%; a spike means translations
were mapped onto the wrong source lines (go back to alignment/key order).
