---
name: frosthaven-recap
description: >-
  Regenerate the Frosthaven player recap after a Gloomhaven Storyline export.
  Diffs exports, updates plot-arcs.json and campaign-config.json, runs
  generate-recap.py, and verifies narrative text. Use when the user drops a
  new export, asks to generate/update the recap, or mentions Storyline sync.
---

# Frosthaven recap workflow

Run end-to-end when the user adds a Storyline export or asks for a new recap.

## Inputs

| Path | Role |
|------|------|
| `exports/YYYY-MM-DD-storyline.json` | Newest `*-storyline.json` by filename is used |
| `data/plot-arcs.json` | Arc trails, status, story paragraphs — **sync from export diff** |
| `data/campaign-config.json` | `next_scenario`, `next_scenario_note` |
| `data/fh-recap-en.json`, `data/scenario-names.en.json` | Read-only unless user asks |

Do **not** use `data/campaign-notes.md` for generation logic.

## Checklist

```
- [ ] 1. Find newest valid export in exports/
- [ ] 2. Diff vs previous export (scenario state changes)
- [ ] 3. Update data/plot-arcs.json from diff
- [ ] 4. Update data/campaign-config.json if user gave next scenario
- [ ] 5. Run: python scripts/generate-recap.py
- [ ] 6. Verify recap — no stale plain_terms or open lists
- [ ] 7. Summarize changes for the user
- [ ] 8. Commit/push only if user asked
```

## Step 1 — Export

- Use newest `exports/*-storyline.json` sorted by filename.
- If newest is empty/invalid, warn and fall back (script handles this).
- Output stamp = date in export **filename**, not Storyline `updated_at`.

## Step 2 — Diff exports

Compare previous dated export vs newest. For each `scenario-fh-N` note:

- `incomplete` → `complete` (newly finished)
- `hidden`/`blocked` → `incomplete` (newly unlocked)
- New or changed `notes`, `choice`, `promptChoice`

Skip retirement scenarios (200+) unless user cares.

## Step 3 — Sync plot-arcs.json

For each arc:

- **trail:** add newly completed scenarios that belong on this arc
- **open:** remove completed; add newly unlocked arc scenarios
- **status:** update when arc meaning shifts (e.g. cleanup done → wrapped)
- **plain_terms:** rewrite if it contradicts export (e.g. "one scenario left" but complete)
- **plain_terms_extra:** add/remove conditionals when forks change

Do not rewrite unchanged arcs.

### Arc → scenarios

| Arc id | Key scenarios |
|--------|----------------|
| algox | 3,4,6,11,19,28,30,38,45–57 |
| unfettered | 15,16,26,36,44,59,96,97,98,61–64 |
| lurkers | 7,13,14,21,22,32–34,42,78,49–57,60 |
| aesther | 65,66,67,68 |
| true_oak | 69,70 |
| pinter | 114,115,116 |
| mindthief | 120,121 |
| side_chests | 107,108,109,110,111,113,126,127,136 |

## Step 4 — campaign-config.json

Update when user states linked/next scenario:

```json
{
  "next_scenario": 68,
  "next_scenario_note": "Linked in Storyline as our next session."
}
```

## Step 5 — Generate

```bash
python scripts/generate-recap.py
```

Outputs: `output/YYYY-MM-DD-recap.md`, `output/latest-recap.md` (and `.html`).

## Step 6 — Verify

In `output/latest-recap.md` Plot threads:

- No **Next / retry** for completed scenarios
- No **Story** claiming open work that's complete
- **Progress** includes new completions on `trail`
- **Next session** matches `campaign-config.json`

## Step 7 — User summary

Report: export used, newly complete/open scenarios, plot-arcs edits, share link:

`https://github.com/teuncortooms/frosthaven-campaign/blob/main/output/latest-recap.md`

## Constraints

- Minimal diffs; don't refactor generator unless broken
- Player-facing — no `promptChoice` jargon
- Don't commit unless user asks

## User prompt (reference)

```
@frosthaven-recap New export in exports/. Full recap workflow.
```

Optional: `Next scenario is N.` / `Commit and push when done.`
