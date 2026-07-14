# Frosthaven reference data

## Workflow

See **`campaign-notes.md`** for what Gloomhaven Storyline tracks vs what we sync manually, and how the player recap is meant to be used.

## `fh-recap-en.json`

Narrative recap labels from [Gloomhaven Secretariat](https://gloomhaven-secretariat.de) ([source on GitHub](https://github.com/Lurkars/gloomhavensecretariat/blob/main/data/fh/label/spoiler/en.json)).

Use this for **“Previously on Frosthaven…”** text keyed by scenario number. It does **not** replace the physical Scenario Book or Section Book.

## Regenerating `campaign-recap.md`

After exporting a fresh `stories.json` from Gloomhaven Storyline:

```bash
python scripts/generate-recap.py
```

The recap is **player-facing**: story, decisions, open/blocked/hidden scenarios, and narrative reminders.

Outputs: `campaign-recap.md` and **`campaign-recap.html`** (for sharing — see `campaign-notes.md`).
