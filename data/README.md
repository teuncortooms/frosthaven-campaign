# Frosthaven reference data

## Workflow

See **`campaign-notes.md`** for the full session workflow and what is automatic vs manual.

## Files

| File | Source | Used by script? |
|------|--------|-----------------|
| `scenario-names.en.json` | [Gloomhaven Secretariat scenarios](https://github.com/Lurkars/gloomhavensecretariat/tree/main/data/fh/scenarios) | Yes — display names (offline) |
| `fh-recap-en.json` | [Secretariat labels](https://github.com/Lurkars/gloomhavensecretariat/blob/main/data/fh/label/spoiler/en.json) | Yes — “Previously on…” text |
| `plot-arcs.json` | Hand-written for this campaign | Yes — arc narratives |
| `campaign-config.json` | Hand-written (next scenario, etc.) | Yes |
| `campaign-notes.md` | Human docs | No |

Refresh scenario names (optional, needs network):

```bash
python scripts/fetch-scenario-names.py
```

## Regenerating recaps

After a new export in `exports/`:

```bash
python scripts/generate-recap.py
```

Outputs go to `output/` — share **`output/latest-recap.html`**.
