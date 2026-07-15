# Storyline exports

Save each Gloomhaven Storyline export here:

```
YYYY-MM-DD-storyline.json
```

After adding a new export, copy it to **`latest.json`** (or pass `--export` to the generator):

```bash
copy exports\2026-07-21-storyline.json exports\latest.json
python scripts/generate-recap.py
```

Older exports are kept for comparison; recaps are written to `output/` with the same date stamp.
