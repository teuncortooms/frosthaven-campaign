# Storyline exports

Save each Gloomhaven Storyline export here, named by date:

```
YYYY-MM-DD-storyline.json
```

The generator picks the **newest file by name** (so `2026-07-21-storyline.json` beats `2026-07-14-storyline.json`):

```bash
python scripts/generate-recap.py
```

Output recap files use the same date: `output/2026-07-21-recap.md`.

To use a specific export:

```bash
python scripts/generate-recap.py --export exports/2026-07-14-storyline.json
```

Older exports are kept for comparison.
