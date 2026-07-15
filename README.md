# Frosthaven campaign recap

Player-facing story recap for a **Frosthaven** board-game campaign. Export your save from [Gloomhaven Storyline](https://storyline.gloomhaven.com/), run a small Python script, and get a shareable summary: where each plot thread stands, what you can play next, and “Previously on Frosthaven…” reminders.

This repo tracks one group’s campaign. The tooling is reusable for any Frosthaven group with the same workflow.

## Quick start

**Requirements:** Python 3.10+ (stdlib only — no pip install, no network needed for normal recap generation)

1. Export your campaign from **Gloomhaven Storyline** and save it as:

   ```
   exports/YYYY-MM-DD-storyline.json
   ```

   The generator uses the **newest file by name** (no `latest.json` copy step).

2. Set your planned next session in `data/campaign-config.json` (Storyline’s “linked scenario” is not in the export):

   ```json
   {
     "next_scenario": 68,
     "next_scenario_note": "Linked in Storyline as our next session."
   }
   ```

3. Regenerate the recap:

   ```bash
   python scripts/generate-recap.py
   ```

4. Share **`output/latest-recap.html`** with your group (open in a browser → Print → Save as PDF, or paste into Google Docs).

Outputs:

| File | Purpose |
|------|---------|
| `output/YYYY-MM-DD-recap.md` | Dated recap (kept when you add newer exports) |
| `output/YYYY-MM-DD-recap.html` | Dated shareable HTML |
| `output/latest-recap.md` / `.html` | Always the most recent run (convenient for sharing) |

## What the recap includes

- **Outpost snapshot** — morale, prosperity, week, etc. (from the Storyline export)
- **Plot threads — where each arc stands** — high-level “where we are” per story arc
- **Choices on the table** — **Next session** (from config) plus other open scenarios with recap text
- **Decisions we made** — inferred branch choices (e.g. Icespeaker vs Snowspeaker path)
- **Campaign progress** — blocked and hidden scenarios
- **What happened (by scenario)** — full recap text for completed scenarios

During play, **Gloomhaven Storyline** remains the live source of truth. This recap is a periodic snapshot for the group chat.

## Is “export + run script” enough every session?

**Mostly yes for facts; no for narrative polish.**

| Updates automatically each run | Usually needs a manual touch |
|-------------------------------|------------------------------|
| Open / complete / blocked / hidden scenarios | Arc **status tags** and **Story** paragraphs in `plot-arcs.json` when the *meaning* of where you are shifts (e.g. “mid-climax” → “failed, need retry”) |
| Progress trails (`A → B → C`) on each arc | Which scenario numbers belong on an arc’s `trail` / `future` lists when you enter a new branch |
| Choices list with recap snippets | **`next_scenario`** in `campaign-config.json` when you pick a new linked scenario |
| Table notes from the export | New **branch rules** in the script’s `story_decisions()` when you hit a major fork the script doesn’t know yet |
| Building-level hints (e.g. Crain’s workshop) | Wording tweaks any time you want the recap to read better |

**Practical workflow:** after most sessions, export + run the script and share the HTML. Every few sessions (or when a major arc turns), skim `plot-arcs.json` and update status/story lines. That file changes far less often than `stories.json`.

See [`data/campaign-notes.md`](data/campaign-notes.md) for the full breakdown.

## Repository layout

```
exports/
  2026-07-14-storyline.json    # Dated Storyline export
  2026-07-15-storyline.json    # Newest by filename is used automatically
output/
  2026-07-15-recap.md          # Same date as the export filename
  2026-07-15-recap.html
  latest-recap.md              # Copy of most recent run (convenient GitHub link)
  latest-recap.html
scripts/
  generate-recap.py            # Main generator (offline)
  fetch-scenario-names.py      # Optional: refresh name list from Secretariat
data/
  scenario-names.en.json       # Scenario display names (offline)
  fh-recap-en.json             # “Previously on…” labels (Secretariat)
  plot-arcs.json               # Arc titles, trails, plain-language summaries
  campaign-config.json         # Next linked scenario, etc.
  campaign-notes.md            # Human workflow docs (not read by script)
```

### What the script reads

| Input | Role |
|-------|------|
| `exports/*-storyline.json` (newest by filename, or `--export`) | Scenario states, notes, morale, prosperity, buildings |
| `data/scenario-names.en.json` | Scenario **names** (local — no network) |
| `data/fh-recap-en.json` | “Previously on Frosthaven…” text per scenario |
| `data/plot-arcs.json` | Arc narratives, status tags, scenario trails |
| `data/campaign-config.json` | Next session scenario (linked choice) |

The script **does not** read `data/campaign-notes.md`.

### Customising the recap

- **Next session highlight** — `data/campaign-config.json`
- **Arc wording and story summaries** — `data/plot-arcs.json`
- **Branch detection** — `scripts/generate-recap.py` (`story_decisions()`)
- **Scenario state** — new export in `exports/`, then regenerate
- **Scenario names** — `python scripts/fetch-scenario-names.py` (optional, needs network)

## Sources and attribution

This project combines a **campaign export** with **community-maintained reference data**. It does **not** include official Cephalofair rulebooks, scenario maps, or section text.

### Game and official materials

| Source | Use in this repo |
|--------|------------------|
| [**Frosthaven**](https://cephalofair.com/products/frosthaven) (Cephalofair Games) | The board game; all story, scenarios, and characters are © Cephalofair Fair Games LLC. |
| **Frosthaven Scenario Book** & **Section Book** (physical) | Authoritative rules and § entries during play. Not reproduced here. |

### Campaign tracking

| Source | Use in this repo |
|--------|------------------|
| [**Gloomhaven Storyline**](https://storyline.gloomhaven.com/) | Live campaign tracker; exports saved under `exports/` |

### Community reference data (Gloomhaven Secretariat)

| Source | Use in this repo |
|--------|------------------|
| [**Gloomhaven Secretariat**](https://gloomhaven-secretariat.de/) | Fan site and data project. |
| [`Lurkars/gloomhavensecretariat`](https://github.com/Lurkars/gloomhavensecretariat) on GitHub | |
| → [`data/fh/label/spoiler/en.json`](https://github.com/Lurkars/gloomhavensecretariat/blob/main/data/fh/label/spoiler/en.json) | Copied locally as `data/fh-recap-en.json` |
| → [`data/fh/scenarios/*.json`](https://github.com/Lurkars/gloomhavensecretariat/tree/main/data/fh/scenarios) | Copied locally as `data/scenario-names.en.json` (refresh via `fetch-scenario-names.py`) |

Thank you to the Gloomhaven Secretariat contributors for maintaining this data.

### Original content in this repo

| File | Author |
|------|--------|
| `data/plot-arcs.json` | Campaign-specific arc summaries and structure |
| `data/campaign-config.json` | Table preferences (next scenario, etc.) |
| `scripts/generate-recap.py` | Generator logic |
| `exports/*.json` | Campaign state (from Storyline export) |
| `output/*-recap.*` | Generated output |

## Disclaimer

**Frosthaven**, **Gloomhaven**, and related names and content are trademarks and © **Cephalofair Fair Games LLC**. This repository is an unofficial fan project for personal campaign tracking. It is not affiliated with or endorsed by Cephalofair Games.

Scenario recap text in `fh-recap-en.json` originates from the community Gloomhaven Secretariat project and may contain spoilers. Do not share generated recaps with players who have not reached those scenarios in your campaign.
