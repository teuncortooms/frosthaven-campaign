# Frosthaven campaign recap

Player-facing story recap for a **Frosthaven** board-game campaign. Export your save from [Gloomhaven Storyline](https://storyline.gloomhaven.com/), run a small Python script, and get a shareable summary: where each plot thread stands, what you can play next, and “Previously on Frosthaven…” reminders.

This repo tracks one group’s campaign (`stories.json`). The tooling is reusable for any Frosthaven group with the same workflow.

## Quick start

**Requirements:** Python 3.10+ (stdlib only — no pip install)

1. Export your campaign from **Gloomhaven Storyline** as `stories.json` (place it in the repo root).
2. Regenerate the recap:

   ```bash
   python scripts/generate-recap.py
   ```

3. Share **`campaign-recap.html`** with your group (open in a browser → Print → Save as PDF, or paste into Google Docs).

Outputs:

| File | Purpose |
|------|---------|
| `campaign-recap.md` | Markdown recap (version control, editing) |
| `campaign-recap.html` | Share-friendly HTML (WhatsApp, PDF, Docs) |

## What the recap includes

- **Outpost snapshot** — morale, prosperity, week, etc. (from the Storyline export)
- **Plot threads — where each arc stands** — high-level “where we are” per story arc (Algox, Lurkers, Unfettered, side quests, …)
- **Choices on the table** — open scenarios with narrative reminders and your table notes
- **Decisions we made** — inferred branch choices (e.g. Icespeaker vs Snowspeaker path)
- **Campaign progress** — blocked and hidden scenarios
- **What happened (by scenario)** — full recap text for completed scenarios

During play, **Gloomhaven Storyline** remains the live source of truth for scenario status and the calendar. This recap is a periodic snapshot for the group chat.

## Repository layout

```
stories.json                 # Campaign export from Gloomhaven Storyline
scripts/generate-recap.py    # Generator script
data/
  fh-recap-en.json           # Scenario recap labels (Secretariat)
  plot-arcs.json             # Arc titles, trails, and plain-language summaries
  campaign-notes.md          # Workflow notes (not read by the script)
campaign-recap.md            # Generated recap
campaign-recap.html          # Generated shareable HTML
```

### What the script reads

| Input | Role |
|-------|------|
| `stories.json` | Scenario states, notes, morale, prosperity, buildings |
| `data/fh-recap-en.json` | “Previously on Frosthaven…” text per scenario |
| `data/plot-arcs.json` | Arc narratives, status tags, scenario trails |

The script **does not** read `data/campaign-notes.md` or other free-form notes.

At generation time it also **fetches scenario names** from the Gloomhaven Secretariat GitHub repo (requires network).

### Customising the recap

- **Arc wording and story summaries** — edit `data/plot-arcs.json`
- **Branch detection and document structure** — edit `scripts/generate-recap.py`
- **Scenario state** — re-export `stories.json` from Storyline and regenerate

See [`data/campaign-notes.md`](data/campaign-notes.md) for the full workflow.

## Sources and attribution

This project combines a **private campaign export** with **community-maintained reference data**. It does **not** include official Cephalofair rulebooks, scenario maps, or section text.

### Game and official materials

| Source | Use in this repo |
|--------|------------------|
| [**Frosthaven**](https://cephalofair.com/products/frosthaven) (Cephalofair Games) | The board game; all story, scenarios, and characters are © Cephalofair Fair Games LLC. |
| **Frosthaven Scenario Book** & **Section Book** (physical) | Authoritative rules and § entries during play. Not reproduced here. |

### Campaign tracking

| Source | Use in this repo |
|--------|------------------|
| [**Gloomhaven Storyline**](https://storyline.gloomhaven.com/) | Live campaign tracker; `stories.json` is exported from the app. |

### Community reference data (Gloomhaven Secretariat)

| Source | Use in this repo |
|--------|------------------|
| [**Gloomhaven Secretariat**](https://gloomhaven-secretariat.de/) | Fan site and data project. |
| [`Lurkars/gloomhavensecretariat`](https://github.com/Lurkars/gloomhavensecretariat) on GitHub | |
| → [`data/fh/label/spoiler/en.json`](https://github.com/Lurkars/gloomhavensecretariat/blob/main/data/fh/label/spoiler/en.json) | Copied locally as `data/fh-recap-en.json` — scenario recap / “Previously on…” labels |
| → [`data/fh/scenarios/*.json`](https://github.com/Lurkars/gloomhavensecretariat/tree/main/data/fh/scenarios) | Fetched at generate time for scenario **names** only |

Thank you to the Gloomhaven Secretariat contributors for maintaining this data.

### Original content in this repo

| File | Author |
|------|--------|
| `data/plot-arcs.json` | Campaign-specific arc summaries and structure |
| `scripts/generate-recap.py` | Generator logic |
| `stories.json` | This group’s campaign state (from Storyline export) |
| `campaign-recap.md` / `.html` | Generated output |

## Disclaimer

**Frosthaven**, **Gloomhaven**, and related names and content are trademarks and © **Cephalofair Fair Games LLC**. This repository is an unofficial fan project for personal campaign tracking. It is not affiliated with or endorsed by Cephalofair Games.

Scenario recap text in `fh-recap-en.json` originates from the community Gloomhaven Secretariat project and may contain spoilers. Do not share generated recaps with players who have not reached those scenarios in your campaign.
