# Campaign tracking notes

## Data source

`stories.json` is exported from **Gloomhaven Storyline** (IndexedDB / campaign sync), not maintained by hand in this repo.

## What the generator does

Run:

```bash
python scripts/generate-recap.py
```

It reads **only** these inputs (it does **not** read this markdown file or any free-form instructions):

| File | Role |
|------|------|
| `stories.json` | Scenario states (complete / incomplete / blocked / hidden), notes, morale, prosperity, buildings, etc. |
| `data/fh-recap-en.json` | “Previously on Frosthaven…” text per scenario (Secretariat labels) |
| `data/plot-arcs.json` | **Story arc write-ups** — titles, status labels, scenario trails, plain-language summaries |

It writes:

| Output | Use |
|--------|-----|
| `campaign-recap.md` | Edit in repo, version control |
| `campaign-recap.html` | **Share with the group** (PDF / Google Docs) |

It also **fetches scenario names** from GitHub (Gloomhaven Secretariat) when you regenerate — needs network.

### What is automatic vs hand-written

**Automatic (from `stories.json`):**

- Which scenarios are open / blocked / hidden / complete
- Scenario trails show only **completed** steps as `A → B → C`
- Open scenarios on an arc get a **Next / retry** line
- Table notes (e.g. *Keihard gefaald*)
- Building levels (e.g. Crain’s workshop hint when Building 34 is high enough)
- Conditional intro lines (e.g. Algox Offensive vs Scouting) via rules in `plot-arcs.json`

**Hand-written (you edit `data/plot-arcs.json`):**

- Arc titles and status tags (*“active, mid-climax”*, *“largely resolved”*)
- Which scenario numbers belong to each arc
- **Story:** paragraphs in plain language
- Extra bullets and `trail_notes`

**Hand-written in Python (`scripts/generate-recap.py`):**

- **Decisions we made** — inferred branch logic (Icespeaker vs Snowspeaker, peace with Orphan, etc.)
- Document structure and HTML export

To change how an arc is **described**, edit `data/plot-arcs.json`.  
To change **branch detection** or add new sections, edit the script.

### `campaign-notes.md` vs `plot-arcs.json`

- **`campaign-notes.md`** (this file) — workflow docs for humans; **not** loaded by the script.
- **`plot-arcs.json`** — structured arc content the script **does** load.

## What the app tracks

**Gloomhaven Storyline** is the live source during play. The recap copies scenario state from the last export so the group can see progress — re-export and regenerate when that changes.

## What we sync manually

- Morale, prosperity, inspiration, town guard
- Scenario notes
- Full export when open/blocked lists change

## What the export does *not* track reliably

- Character levels or full roster
- Complete retired-character history

## Sharing with the team

See **Sharing with the team** section below — use `campaign-recap.html`, not raw `.md`.

### Option A — PDF (best for WhatsApp)

1. Open `campaign-recap.html` in Chrome or Edge.
2. Print → Save as PDF.
3. Send in WhatsApp.

### Option B — Google Docs

Open HTML in browser → Ctrl+A → Ctrl+C → paste into Google Docs, or upload the PDF.

## Reference data

- `fh-recap-en.json` — scenario recap text
- `plot-arcs.json` — arc “whereabouts” narratives
- Physical **Scenario Book** and **Section Book** — rules and § entries
