# Campaign tracking notes

## Data source

`stories.json` is exported from **Gloomhaven Storyline** (IndexedDB / campaign sync), not maintained by hand in this repo.

## What the app tracks

**Gloomhaven Storyline** is the live source for scenario and calendar state during play.

The recap also lists **open / blocked / hidden** scenarios from the last export so the group can see progress and choices — re-export and regenerate when that changes.

## What we sync manually (every now and then)

Export a fresh `stories.json` when you want the recap to reflect:

- Morale, prosperity, inspiration
- Town Guard / outpost defense
- Scenario **notes** (e.g. failed attempts)
- Open / blocked / hidden scenario lists

## What the export does *not* track reliably

- Character levels or full roster
- Complete retired-character history

Keep that on paper or elsewhere.

## Regenerating the recap

```bash
python scripts/generate-recap.py
```

Outputs:

- `campaign-recap.md` — for editing in the repo
- `campaign-recap.html` — **share this with the group** (see below)

## Sharing with the team (WhatsApp / Google Docs)

Most people don't read `.md` well on a phone. Use **`campaign-recap.html`** instead.

### Option A — PDF (best for WhatsApp)

1. Open `campaign-recap.html` in Chrome or Edge (double-click the file).
2. **Print** → **Save as PDF** (or “Microsoft Print to PDF”).
3. Send the PDF in your WhatsApp group.

Everyone gets readable headings and no `**asterisk**` formatting.

### Option B — Google Docs (easy to comment)

1. Open `campaign-recap.html` in a browser.
2. **Ctrl+A** → **Ctrl+C**.
3. In Google Docs: new document → **Ctrl+V**.

Headings and lists usually paste cleanly. Upload the PDF instead if paste looks wrong.

Alternatively: **File → Open** in Google Docs and upload the **PDF** from option A.

### Option C — Google Drive link

Upload `campaign-recap.pdf` or `.html` to Drive → share link in WhatsApp. HTML opens in the browser; PDF opens everywhere.

### Don't

- Paste raw `campaign-recap.md` into WhatsApp — `**bold**` and `# headings` stay literal.
- Expect the recap to stay in sync without re-exporting `stories.json` and re-running the script.

## Reference data

- `fh-recap-en.json` — “Previously on Frosthaven…” text (Gloomhaven Secretariat labels)
- Physical **Scenario Book** and **Section Book** — setup, rules, and section entries
