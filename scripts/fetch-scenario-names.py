"""Download Frosthaven scenario names from Gloomhaven Secretariat (one-time / refresh)."""
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "scenario-names.en.json"
BASE = (
    "https://raw.githubusercontent.com/Lurkars/gloomhavensecretariat/"
    "main/data/fh/scenarios/"
)


def fetch_name(num: int) -> str | None:
    candidates = [f"{num:03d}.json"]
    if num == 4:
        candidates = ["004A.json", "004B.json"] + candidates
    for filename in candidates:
        try:
            with urllib.request.urlopen(BASE + filename, timeout=10) as resp:
                data = json.loads(resp.read())
                name = data.get("name")
                if not name:
                    continue
                if num == 4 and filename.startswith("004"):
                    return name.replace(" A", "").replace(" B", "")
                return name
        except Exception:
            continue
    return None


def main() -> None:
    existing: dict[str, str] = {}
    if OUT.exists():
        existing = json.loads(OUT.read_text(encoding="utf-8")).get("names", {})

    names = dict(existing)
    added = 0
    for num in range(0, 221):
        key = str(num)
        if key in names:
            continue
        name = fetch_name(num)
        if name:
            names[key] = name
            added += 1

    payload = {
        "_meta": {
            "source": "https://github.com/Lurkars/gloomhavensecretariat/tree/main/data/fh/scenarios",
            "note": "Scenario display names. Refresh with: python scripts/fetch-scenario-names.py",
        },
        "names": dict(sorted(names.items(), key=lambda kv: int(kv[0]))),
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(names)} names, {added} newly fetched)")


if __name__ == "__main__":
    main()
