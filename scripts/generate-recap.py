"""Generate player-facing campaign recap (Markdown + HTML) from stories.json."""
import html
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RETIREMENT_SCENARIO_MIN = 200


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


def story_decisions(scenarios: dict[int, dict], names: dict[int, str]) -> list[str]:
    lines: list[str] = []

    def add(text: str) -> None:
        if text not in lines:
            lines.append(text)

    if scenarios.get(1, {}).get("state") == "complete":
        if scenarios.get(2, {}).get("state") == "blocked":
            add(
                "After the town attack, we went on the **Algox Offensive** "
                "rather than scouting the mountain pass first."
            )

    if scenarios.get(4, {}).get("state") == "complete":
        add(
            "At **Heart of Ice**, we split up to pursue three threads: "
            "the Algox war on **Snowscorn Peak**, the **Lurkers** at the Biting Sea, "
            "and the **Unfettered** constructs in the Crystal Fields."
        )

    if scenarios.get(6, {}).get("state") == "complete":
        add(
            "We sided with the **Icespeakers** against the Snowspeakers "
            "at Snowscorn Mountain."
        )

    if scenarios.get(19, {}).get("state") == "complete":
        s30 = scenarios.get(30, {})
        s28 = scenarios.get(28, {})
        if s30.get("state") in ("incomplete", "complete") or s28.get("state") == "blocked":
            add(
                "After **Skyhall**, we joined the push for **war** against the other "
                "Algox faction instead of backing the peace summit."
            )
        elif s28.get("state") == "complete":
            add(
                "After **Skyhall**, we backed **peace talks** between the Algox factions."
            )

    s30 = scenarios.get(30, {})
    if s30.get("state") == "incomplete":
        note = s30.get("notes", "").strip()
        if note:
            add(f"We **failed** **War of the Spire B** ({note}).")
        else:
            add("We **failed** **War of the Spire B** and still need to retry or move on.")

    s44 = scenarios.get(44, {})
    if s44.get("state") == "complete":
        choice = str(s44.get("choice", ""))
        if choice == "59" or scenarios.get(59, {}).get("state") == "complete":
            add(
                "Facing the Unfettered **Orphan**, we tried to **broker peace** "
                "rather than destroy them."
            )
        elif choice == "58" or scenarios.get(58, {}).get("state") == "complete":
            add(
                "Facing the Unfettered **Orphan**, we chose to **destroy** the threat."
            )

    if scenarios.get(36, {}).get("state") == "complete":
        add(
            "In the Unfettered complex, we reached the core through the **Buried Ducts** "
            "(not the deeper transit tunnels)."
        )

    for num, state in sorted(scenarios.items()):
        note = state.get("notes", "").strip()
        if not note or num == 30:
            continue
        name = names.get(num, f"scenario {num}")
        add(f"Table note — **{name} ({num})**: {note}")

    return lines


def format_scenario_entry(
    num: int,
    name: str,
    state: dict,
    recaps: dict,
    *,
    include_recap: bool = True,
) -> list[str]:
    lines: list[str] = []
    note = state.get("notes", "").strip()
    title = f"**{num} — {name}**"
    if note:
        title += f" — *{note}*"
    lines.append(f"- {title}")
    if include_recap:
        recap = clean(recap_text(recaps, num))
        if recap:
            lines.append(f"  - {recap}")
    return lines


def markdown_to_html(md: str) -> str:
    """Minimal Markdown to HTML for sharing (headings, bold, lists, italics)."""
    out: list[str] = []
    in_ul = False

    def close_ul() -> None:
        nonlocal in_ul
        if in_ul:
            out.append("</ul>")
            in_ul = False

    def inline(text: str) -> str:
        text = html.escape(text)
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
        return text

    for line in md.splitlines():
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if stripped.startswith("### "):
            close_ul()
            out.append(f"<h3>{inline(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            close_ul()
            out.append(f"<h2>{inline(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            close_ul()
            out.append(f"<h1>{inline(stripped[2:])}</h1>")
        elif stripped.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            content = stripped[2:]
            if indent >= 2:
                out.append(f"<li class='nested'>{inline(content)}</li>")
            else:
                out.append(f"<li>{inline(content)}</li>")
        elif line.strip() == "---":
            close_ul()
            out.append("<hr>")
        elif line.strip() == "":
            close_ul()
        else:
            close_ul()
            out.append(f"<p>{inline(line)}</p>")

    close_ul()
    body = "\n".join(out)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Frosthaven — where we left off</title>
  <style>
    body {{ font-family: Georgia, "Times New Roman", serif; line-height: 1.5; max-width: 42rem; margin: 2rem auto; padding: 0 1rem; color: #222; }}
    h1 {{ font-size: 1.6rem; border-bottom: 1px solid #ccc; padding-bottom: 0.3rem; }}
    h2 {{ font-size: 1.25rem; margin-top: 1.5rem; color: #333; }}
    h3 {{ font-size: 1.05rem; margin-top: 1rem; color: #444; }}
    ul {{ padding-left: 1.2rem; }}
    li {{ margin-bottom: 0.5rem; }}
    li.nested {{ list-style: circle; margin-left: 1rem; font-size: 0.95rem; color: #444; }}
    p em {{ color: #555; }}
    hr {{ border: none; border-top: 1px solid #ddd; margin: 2rem 0; }}
    @media print {{ body {{ margin: 1cm; max-width: none; }} }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


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

    names = {n: fetch_scenario_name(n) for n in sorted(scenarios) if n <= 220}

    complete = sorted(n for n, s in scenarios.items() if s.get("state") == "complete")
    incomplete = sorted(n for n, s in scenarios.items() if s.get("state") == "incomplete")
    blocked = sorted(n for n, s in scenarios.items() if s.get("state") == "blocked")
    hidden = sorted(n for n, s in scenarios.items() if s.get("state") == "hidden")

    incomplete_main = [n for n in incomplete if n < RETIREMENT_SCENARIO_MIN]
    incomplete_retirement = [n for n in incomplete if n >= RETIREMENT_SCENARIO_MIN]

    lines: list[str] = []
    updated = save.get("updated_at", "?")[:10]
    lines.append("# Frosthaven — where we left off")
    lines.append("")
    lines.append(
        f"*Updated {updated}. Scenario list synced from Storyline export — "
        f"double-check the app before choosing what to play.*"
    )
    lines.append("")
    lines.append("## Outpost snapshot")
    lines.append("")
    lines.append("(From the last manual sync — check your notes for current values.)")
    lines.append("")
    lines.append(f"- **Morale:** {campaign.get('morale', '?')} / 20")
    lines.append(f"- **Prosperity index:** {campaign.get('prosperityIndex', '?')}")
    lines.append(f"- **Inspiration:** {campaign.get('inspiration', '?')}")
    soldiers = campaign.get("soldiers")
    defense = campaign.get("totalDefense")
    if soldiers is not None:
        guard = f"- **Town Guard:** {soldiers} soldiers"
        if defense is not None:
            guard += f" (outpost defense {defense})"
        lines.append(guard)
    lines.append(f"- **Scenarios completed:** {len(complete)}")
    lines.append("")
    lines.append("## The story so far")
    lines.append("")
    lines.append(
        "We are mercenaries who reached **Frosthaven** after the Imperial Pass thawed. "
        "After the opening attack, we took the **Algox Offensive** rather than scouting first. "
        "That led us into the Algox civil war, the Lurker Coral Shards, and the Unfettered "
        "beneath the Crystal Fields — often all at once."
    )
    lines.append("")
    lines.append(
        "On the **Algox** front, we backed the **Icespeakers**, survived **Skyhall**, "
        "and chose the **war path** over a peace summit. **War of the Spire B** went badly "
        "(*Keihard gefaald*) — that thread is stuck mid-climax. The Oracle / Unyielding Shard "
        "storyline (peace summit, Marogh, the combined ice-and-snow ritual) is mostly still ahead."
    )
    lines.append("")
    lines.append(
        "We **made peace with the Unfettered Orphan** (Crain's arc) and cleared a second "
        "facility up to **Program Control Nexus**; **Collapsing Vent** is still open. "
        "The **Lurker crown** plot is mid-way — bathysphere and shards, but no reunion yet. "
        "The **Aesther** elemental array failed at the attunement step (**The Face of Torment**). "
        "**Pinter's mountain road** is almost done — **Caravan Guards** is next. "
        "Various **side jobs from treasure chests** are still floating around."
    )
    lines.append("")
    lines.append("## Choices on the table")
    lines.append("")
    lines.append(
        "Scenarios we **can play next** (or retry), with a story reminder for each. "
        "Pick one when we meet — or cross-check Storyline if something unlocked since the last export."
    )
    lines.append("")
    if incomplete_main:
        for num in incomplete_main:
            lines.extend(
                format_scenario_entry(
                    num, names.get(num, "?"), scenarios[num], recaps
                )
            )
    else:
        lines.append("- *(none listed in export)*")
    lines.append("")
    if incomplete_retirement:
        lines.append("### Retirement / personal-quest scenarios")
        lines.append("")
        for num in incomplete_retirement:
            lines.extend(
                format_scenario_entry(
                    num, names.get(num, "?"), scenarios[num], recaps
                )
            )
        lines.append("")
    lines.append("## Decisions we made")
    lines.append("")
    for decision in story_decisions(scenarios, names):
        lines.append(f"- {decision}")
    lines.append("")
    lines.append("## Campaign progress")
    lines.append("")
    lines.append("### Blocked — other path taken")
    lines.append("")
    lines.append("We can't do these in this campaign branch:")
    lines.append("")
    if blocked:
        for num in blocked:
            lines.append(f"- **{num} — {names.get(num, '?')}**")
    else:
        lines.append("- *(none)*")
    lines.append("")
    lines.append("### Hidden — not yet revealed")
    lines.append("")
    lines.append("Still secret on the map / in the story:")
    lines.append("")
    if hidden:
        for num in hidden:
            lines.append(f"- **{num} — {names.get(num, '?')}**")
    else:
        lines.append("- *(none)*")
    lines.append("")
    lines.append("## Plot threads")
    lines.append("")
    threads = [
        (
            "Algox civil war",
            "Icespeaker allies; Skyhall done; war assault failed at War of the Spire B.",
            "Retry the assault, or see whether peace talks (Summit Meeting) are still an option at your table.",
        ),
        (
            "Unfettered & Crain",
            "Peace with the Orphan; second factory cleared through Program Control Nexus.",
            "Collapsing Vent; the Harbinger / seal storyline may unlock later via Crain's workshop.",
        ),
        (
            "Lurkers & Coral Crown",
            "Shards collected; bathysphere built; Sun-in-Shallows arc started.",
            "Crown reunion scenarios — not started.",
        ),
        (
            "Aesther elementals",
            "Cores retrieved from four planes; attunement went wrong.",
            "The Face of Torment — new rift opened.",
        ),
        (
            "True Oak",
            "Listerius triangulated the tree; Radiant Order confrontation resolved.",
            None,
        ),
        (
            "Pinter's Copperneck road",
            "Explosives and pylon defense done.",
            "Caravan Guards — first merchant run on the shortcut.",
        ),
        (
            "Mindthief in the woods",
            "Cleared the influenced guards at the cabin.",
            "Black Memories — trail leads toward the Black Barrow near Gloomhaven.",
        ),
        (
            "Treasure-map side jobs",
            "Lustrous Pit, Lush Grotto, Derelict Freighter done.",
            "Emperor's invitation, factory, temple keystone, ice cave, Joseph's shop, pirate hoard, etc.",
        ),
    ]
    for title, progress, next_up in threads:
        lines.append(f"### {title}")
        lines.append(f"- {progress}")
        if next_up:
            lines.append(f"- **Still open:** {next_up}")
        lines.append("")
    lines.append("## What happened (by scenario)")
    lines.append("")
    lines.append("Narrative reminders for scenarios we've **finished**.")
    lines.append("")
    for num in complete:
        name = names.get(num, "?")
        recap = clean(recap_text(recaps, num))
        lines.append(f"### {num} — {name}")
        if recap:
            lines.append("")
            lines.append(recap)
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "Regenerate: `python scripts/generate-recap.py` → `campaign-recap.html` for sharing. "
        "See `data/campaign-notes.md`."
    )
    lines.append("")

    md_text = "\n".join(lines)
    (ROOT / "campaign-recap.md").write_text(md_text, encoding="utf-8")
    (ROOT / "campaign-recap.html").write_text(markdown_to_html(md_text), encoding="utf-8")
    print(f"Wrote {ROOT / 'campaign-recap.md'} ({len(lines)} lines)")
    print(f"Wrote {ROOT / 'campaign-recap.html'}")


if __name__ == "__main__":
    main()
