# Campaign tracking notes

## Data source

Storyline exports live in **`exports/`**, one dated file per export:

```
exports/2026-07-14-storyline.json
exports/2026-07-21-storyline.json   ← newest by name is used automatically
```

Output recap files use the **same date as the export filename** (`2026-07-21-recap.md`).

## What the generator does

Run:

```bash
python scripts/generate-recap.py
```

Optional: `python scripts/generate-recap.py --export exports/2026-07-14-storyline.json`

It reads **only** these inputs (it does **not** read this markdown file):

| File | Role |
|------|------|
| `exports/*-storyline.json` | Scenario states, notes, morale, prosperity, buildings |
| `data/scenario-names.en.json` | Scenario display names (**offline**) |
| `data/fh-recap-en.json` | “Previously on Frosthaven…” text per scenario |
| `data/plot-arcs.json` | Arc write-ups — titles, status, trails, story paragraphs |
| `data/campaign-config.json` | **Next session** scenario (Storyline “linked” choice is not in the export) |

It writes:

| Output | Use |
|--------|-----|
| `output/YYYY-MM-DD-recap.md` | Dated recap (kept for history) |
| `output/YYYY-MM-DD-recap.html` | Dated HTML |
| `output/latest-recap.md` / `.html` | Most recent run — **share the HTML** |

No network is required for normal regeneration. Scenario names are stored locally. To refresh names from Secretariat: `python scripts/fetch-scenario-names.py`.

## After each session — what is automatic vs manual?

Your instinct is right: **the script alone is not a full “write the recap for me” pipeline**, but it *is* enough for most session-to-session updates if you accept that arc *interpretation* is curated separately.

### Automatic (just export + run)

- Which scenarios are open, complete, blocked, hidden
- **Progress** trails on each arc (`A → B → C` for completed steps)
- **Next / retry** lines for open scenarios listed on each arc
- **Choices on the table** — recap snippets for every open scenario
- **Next session** block — from `campaign-config.json`
- Table notes (e.g. *Keihard gefaald*)
- Building hints (e.g. Crain’s workshop level)
- Conditional intro lines (Algox Offensive vs Scouting) via rules in `plot-arcs.json`
- Full “what happened” text for newly completed scenarios

### Manual (occasionally)

| File | When to edit |
|------|--------------|
| `exports/` | Every session — new Storyline export |
| `data/campaign-config.json` | When you change the linked / planned next scenario |
| `data/plot-arcs.json` | When narrative **status** or **story meaning** shifts — e.g. war assault failed, arc largely wrapped, new fork opened. Trails often still auto-update from the export; you mainly edit `status`, `plain_terms`, `trail_notes`, and `future` lists when structure changes |
| `scripts/generate-recap.py` | Rarely — new branch-detection rules in `story_decisions()` |
| `data/scenario-names.en.json` | Almost never — optional refresh script |

**Rule of thumb:** export + run after every session; touch `plot-arcs.json` when something *story-significant* changed, not every week.

### `campaign-notes.md` vs `plot-arcs.json` vs `campaign-config.json`

- **`campaign-notes.md`** — this file; humans only.
- **`plot-arcs.json`** — structured arc content the script loads.
- **`campaign-config.json`** — table preferences the export does not capture (next scenario).

## What the app tracks

**Gloomhaven Storyline** is the live source during play. Re-export and regenerate when scenario status changes.

## What we sync manually

- Morale, prosperity, inspiration, town guard (if not in export)
- Scenario notes
- Full export when open/blocked lists change
- Next linked scenario in `campaign-config.json`

## What the export does *not* track reliably

- Character levels or full roster
- Complete retired-character history
- Storyline “linked” / pinned next scenario

## Sharing with the team

Use **`output/latest-recap.html`**, not raw `.md`.

### Option A — PDF (best for WhatsApp)

1. Open `output/latest-recap.html` in Chrome or Edge.
2. Print → Save as PDF.
3. Send in WhatsApp.

### Option B — Google Docs

Open HTML in browser → Ctrl+A → Ctrl+C → paste into Google Docs, or upload the PDF.

## Reference data

- `scenario-names.en.json` — scenario titles
- `fh-recap-en.json` — scenario recap text
- `plot-arcs.json` — arc “whereabouts” narratives
- Physical **Scenario Book** and **Section Book** — rules and § entries
