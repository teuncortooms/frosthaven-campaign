"""Generate campaign-recap.md from stories.json and Secretariat recap labels."""
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def clean(text: str | None) -> str | None:
    if not text:
        return text
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = re.sub(r"</?strong>", "", text, flags=re.I)
    text = re.sub(
        r"%ui\.tooltip:data\.scenario\.recap\.fh\.character\.([^%]+)%",
        lambda m: m.group(1).replace("-", " ").title(),
        text,
    )
    text = re.sub(r"%ui\.tooltip:[^%]+%", "", text)
    text = re.sub(r"%game\.[^%]+%", "", text)
    text = re.sub(r"%data\.[^%]+%", "", text)
    text = re.sub(r"%+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_scenario_name(num: int) -> str:
    base = (
        "https://raw.githubusercontent.com/Lurkars/gloomhavensecretariat/"
        "main/data/fh/scenarios/"
    )
    candidates = [f"{num:03d}.json"]
    if num == 4:
        candidates = ["004A.json", "004B.json"] + candidates
    for filename in candidates:
        try:
            with urllib.request.urlopen(base + filename, timeout=8) as resp:
                data = json.loads(resp.read())
                name = data.get("name", "?")
                if num == 4 and filename.startswith("004"):
                    return name.replace(" A", "").replace(" B", "")
                return name
        except Exception:
            continue
    return "?"


def recap_text(recaps: dict, num: int) -> str | None:
    entry = recaps.get(str(num))
    if not entry or not isinstance(entry, dict):
        return None
    if entry.get(""):
        return entry[""]
    for key in sorted(entry.keys(), key=lambda x: (x != "", x)):
        if key and entry[key]:
            return entry[key]
    return None


def main() -> None:
    with open(ROOT / "stories.json", encoding="utf-8") as f:
        save = json.load(f)[0]
    data = save["data"]
    campaign = data["campaign-fh"]

    with open(ROOT / "data" / "fh-recap-en.json", encoding="utf-8") as f:
        labels = json.load(f)
    recaps = labels.get("scenario", {}).get("recap", {}).get("fh", {})

    scenarios: dict[int, dict] = {}
    for key, val in data.items():
        if key.startswith("scenario-fh-"):
            num = key.replace("scenario-fh-", "")
            if num.isdigit():
                scenarios[int(num)] = val

    all_nums = sorted(set(scenarios) | set(range(max(scenarios) + 1 if scenarios else 0)))
    names = {n: fetch_scenario_name(n) for n in all_nums if n in scenarios or n <= 140}

    complete = sorted(n for n, s in scenarios.items() if s.get("state") == "complete")
    incomplete = sorted(n for n, s in scenarios.items() if s.get("state") == "incomplete")
    blocked = sorted(n for n, s in scenarios.items() if s.get("state") == "blocked")
    hidden = sorted(n for n, s in scenarios.items() if s.get("state") == "hidden")

    choices = []
    for num, state in sorted(scenarios.items()):
        bits = []
        if "choice" in state:
            bits.append(f"choice={state['choice']}")
        if "promptChoice" in state:
            bits.append(f"promptChoice={state['promptChoice']}")
        if "notes" in state:
            bits.append(f'notes="{state["notes"]}"')
        if bits:
            choices.append((num, names.get(num, "?"), ", ".join(bits), state.get("state")))

    archived = campaign.get("archivedCharacters", {})
    archived_uuids = set(archived.keys())
    characters = [
        val
        for key, val in data.items()
        if key.startswith("character-")
        and isinstance(val, dict)
        and val.get("id")
        and val.get("uuid") not in archived_uuids
    ]
    calendar = campaign["calendar"]
    week = calendar["week"]
    sections = calendar["sections"]

    lines: list[str] = []
    lines.append("# Frosthaven Campaign Recap — teuncortooms")
    lines.append("")
    updated = save.get("updated_at", "?")[:10]
    lines.append(f"*Generated from `stories.json` (updated {updated}).*")
    lines.append("")
    lines.append("## Campaign status")
    lines.append("")
    lines.append(f"- **Calendar week:** {week}")
    lines.append(f"- **Morale:** {campaign.get('morale', '?')} / 20")
    lines.append(f"- **Prosperity index:** {campaign.get('prosperityIndex', '?')}")
    lines.append(f"- **Inspiration:** {campaign.get('inspiration', '?')}")
    lines.append(
        f"- **Town Guard soldiers:** {campaign.get('soldiers', '?')} "
        f"(total defense {campaign.get('totalDefense', '?')})"
    )
    lines.append(f"- **Scenarios completed:** {len(complete)}")
    lines.append("")
    lines.append("### Next calendar reads")
    lines.append("")
    week_key = str(week)
    if week_key in sections:
        for sec in sections[week_key]:
            lines.append(f"- Week **{week}**: read **§{sec}** in the Section Book")
    else:
        lines.append(f"- Week **{week}**: no sections listed for this week in the save.")
    lines.append("")
    lines.append("Upcoming scheduled sections (this week and later):")
    for w in sorted(sections.keys(), key=int):
        if int(w) >= week:
            secs = ", ".join(f"§{s}" for s in sections[w])
            lines.append(f"- Week {w}: {secs}")
    lines.append("")
    lines.append("## Party")
    lines.append("")
    for char in sorted(characters, key=lambda x: x.get("sortOrder", 0)):
        cid = char.get("id", "?")
        name = char.get("name", cid)
        level = char.get("level", "?")
        retirements = char.get("retirements")
        extra = f", retired {retirements}x" if retirements else ""
        lines.append(f"- **{name}** ({cid}) — level {level}{extra}")
    if archived:
        lines.append("")
        lines.append("**Retired:**")
        for uuid, cid in archived.items():
            retired = next(
                (
                    val
                    for key, val in data.items()
                    if key == f"character-{uuid}" and isinstance(val, dict)
                ),
                None,
            )
            name = retired.get("name", cid) if retired else cid
            level = retired.get("level", "?") if retired else "?"
            lines.append(f"- **{name}** ({cid}) — retired at level {level}")
    lines.append("")
    lines.append("## Branch choices (from save)")
    lines.append("")
    for num, name, info, state in choices:
        lines.append(f"- **{num} {name}** [{state}]: {info}")
    lines.append("")
    lines.append("## Story so far (inferred)")
    lines.append("")
    lines.append(
        "You are mercenaries hired to reach **Frosthaven** after the Imperial Pass thawed. "
        "After the opening attack, you took **Algox Offensive (3)** rather than scouting. "
        "At **Heart of Ice (4)** you opened the three main forks (**6 / 7 / 8**): "
        "Algox mountains, Lurkers, and Unfettered."
    )
    lines.append("")
    lines.append(
        "You progressed the **Icespeaker** Algox arc through **Skyhall (19)** and chose the "
        "**war path** over **Summit Meeting (28)** peace talks. **War of the Spire B (30)** "
        "is **failed** (*Keihard gefaald*) — the Algox main plot is mid-climax. The Oracle / "
        "Unyielding Shard chain (28→38→45–57) is largely **not done**."
    )
    lines.append("")
    lines.append(
        "In parallel you **brokered peace with the Unfettered Orphan (59)** after "
        "**Nerve Center (44)** via **Buried Ducts (36)**; **Collapsing Vent (98)** remains. "
        "The **Lurker Coral Crown** arc is **mid-way** (bathysphere thread through 34/42, "
        "not crown reunion). **Aesther** array is at **The Face of Torment (68)**. "
        "**Pinter's road** needs **Caravan Guards (116)**. Several **treasure-chest side "
        "scenarios** are open (107–111, 121, 126, 136)."
    )
    lines.append("")
    lines.append("## Completed scenarios")
    lines.append("")
    for num in complete:
        name = names.get(num, "?")
        lines.append(f"### {num} — {name}")
        recap = clean(recap_text(recaps, num))
        if recap:
            lines.append("")
            lines.append(recap)
        state = scenarios[num]
        if state.get("treasures"):
            lines.append("")
            lines.append(f"*Treasures looted: {state['treasures']}*")
        lines.append("")

    lines.append("## Open scenarios")
    lines.append("")
    lines.append("### Available (incomplete)")
    lines.append("")
    for num in incomplete:
        name = names.get(num, "?")
        state = scenarios[num]
        note = state.get("notes", "")
        extra = f" — *{note}*" if note else ""
        recap = clean(recap_text(recaps, num))
        lines.append(f"- **{num} — {name}**{extra}")
        if recap:
            snippet = recap if len(recap) <= 300 else recap[:300] + "..."
            lines.append(f"  - Setup: {snippet}")
    lines.append("")
    lines.append("### Blocked (other path taken)")
    lines.append("")
    for num in blocked:
        lines.append(f"- **{num} — {names.get(num, '?')}**")
    lines.append("")
    lines.append("### Hidden (not yet revealed)")
    lines.append("")
    for num in hidden:
        lines.append(f"- **{num} — {names.get(num, '?')}**")
    lines.append("")
    lines.append("## Plot threads at a glance")
    lines.append("")
    threads = [
        (
            "Algox civil war",
            "19 done; 30 failed; 28 still listed open; Oracle chain mostly untouched",
            "30 (retry?), 28 (peace — may be locked by section choices)",
        ),
        (
            "Unfettered / Crain",
            "Peace with Orphan (59); second facility through 97",
            "98 Collapsing Vent; Harbinger seals 61–64 not in save",
        ),
        (
            "Lurkers / Coral Crown",
            "13–22, 32–34, 42, 78",
            "Crown reunion 49–57, 60 not started",
        ),
        (
            "Aesther elementals",
            "65–67 done",
            "68 The Face of Torment",
        ),
        ("True Oak", "69–70 done", "—"),
        ("Pinter mountain road", "114–115 done", "116 Caravan Guards"),
        ("Mindthief", "120 done", "121 Black Memories"),
        (
            "Side / chest quests",
            "108, 113, 127 done",
            "107, 109–111, 126, 136",
        ),
    ]
    for title, progress, open_items in threads:
        lines.append(f"### {title}")
        lines.append(f"- **Progress:** {progress}")
        lines.append(f"- **Open:** {open_items}")
        lines.append("")

    lines.append("## Local reference files")
    lines.append("")
    lines.append(
        "- `data/fh-recap-en.json` — Gloomhaven Secretariat recap text "
        "(from [Lurkars/gloomhavensecretariat](https://github.com/Lurkars/gloomhavensecretariat))"
    )
    lines.append("- `stories.json` — your campaign export")
    lines.append(
        "- Physical **Scenario Book** and **Section Book** remain the source of truth for § entries"
    )
    lines.append("")
    lines.append(
        "Re-run `python scripts/generate-recap.py` after updating `stories.json`."
    )
    lines.append("")

    out = ROOT / "campaign-recap.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
