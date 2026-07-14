# Frosthaven reference data

## `fh-recap-en.json`

Narrative recap labels from [Gloomhaven Secretariat](https://gloomhaven-secretariat.de) ([source on GitHub](https://github.com/Lurkars/gloomhavensecretariat/blob/main/data/fh/label/spoiler/en.json)).

Use this for **“Previously on Frosthaven…”** text keyed by scenario number. It does **not** replace the physical Scenario Book or Section Book — those contain setup, rules, and § entries.

## Regenerating `campaign-recap.md`

After exporting a fresh `stories.json` from Secretariat:

```bash
python scripts/generate-recap.py
```

This merges your save state with scenario names and recap snippets into `campaign-recap.md`.
