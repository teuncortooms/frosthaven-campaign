"""Generate player-facing campaign recap (Markdown + HTML) from a Storyline export."""
from __future__ import annotations

import argparse
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORTS_DIR = ROOT / "exports"
OUTPUT_DIR = ROOT / "output"
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


def load_scenario_names() -> dict[int, str]:
    path = ROOT / "data" / "scenario-names.en.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Run: python scripts/fetch-scenario-names.py"
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    return {int(k): v for k, v in data.get("names", {}).items()}


def load_campaign_config() -> dict:
    path = ROOT / "data" / "campaign-config.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


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


def load_save(export_path: Path) -> dict:
    text = export_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"{export_path.name} is empty")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{export_path.name} is not valid JSON") from exc
    if not isinstance(data, list) or not data:
        raise ValueError(f"Unexpected export format in {export_path.name}")
    return data[0]


def list_storyline_exports() -> list[Path]:
    return sorted(EXPORTS_DIR.glob("*-storyline.json"))


def resolve_export_path(arg: str | None) -> Path:
    if arg:
        path = Path(arg)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            raise FileNotFoundError(f"Export not found: {path}")
        return path

    exports = list_storyline_exports()
    if not exports:
        raise FileNotFoundError(
            f"No exports in {EXPORTS_DIR}. "
            "Save a Storyline export as exports/YYYY-MM-DD-storyline.json"
        )

    skipped: list[str] = []
    for path in reversed(exports):
        try:
            load_save(path)
        except ValueError as exc:
            skipped.append(str(exc))
            continue
        if skipped:
            print(f"Warning: skipped invalid export(s): {'; '.join(skipped)}")
        return path

    raise ValueError(
        f"No valid exports in {EXPORTS_DIR}. "
        f"Problems: {'; '.join(skipped)}"
    )


def export_stamp(export_path: Path, save: dict) -> str:
    match = re.search(r"(\d{4}-\d{2}-\d{2})", export_path.name)
    if match:
        return match.group(1)
    updated = save.get("updated_at", "")[:10]
    if updated:
        return updated
    return date.today().isoformat()


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
    highlight: bool = False,
) -> list[str]:
    lines: list[str] = []
    note = state.get("notes", "").strip()
    title = f"**{num} — {name}**"
    if note:
        title += f" — *{note}*"
    if highlight:
        lines.append(f"- **→ {num} — {name}**" + (f" — *{note}*" if note else ""))
    else:
        lines.append(f"- {title}")
    if include_recap:
        recap = clean(recap_text(recaps, num))
        if recap:
            lines.append(f"  - {recap}")
    return lines


def scenario_status(scenarios: dict[int, dict], num: int) -> str:
    return scenarios.get(num, {}).get("state", "missing")


def matches_when(when: dict, scenarios: dict[int, dict], data: dict) -> bool:
    if "complete" in when:
        if scenario_status(scenarios, when["complete"]) != "complete":
            return False
    if "blocked" in when:
        if scenario_status(scenarios, when["blocked"]) != "blocked":
            return False
    if "any_incomplete" in when:
        if not any(
            scenario_status(scenarios, n) == "incomplete" for n in when["any_incomplete"]
        ):
            return False
    if "building_min_level" in when:
        building = data.get(when["building_min_level"]["key"], {})
        if building.get("level", 0) < when["building_min_level"]["min_level"]:
            return False
    return True


def format_trail_step(num: int, name: str, scenarios: dict[int, dict]) -> str:
    label = f"**{num} {name}**"
    state = scenario_status(scenarios, num)
    note = scenarios.get(num, {}).get("notes", "").strip()
    if state == "complete":
        return label
    if state == "incomplete":
        if note:
            return f"{label} *(open — {note})*"
        return f"{label} *(open)*"
    if state == "blocked":
        return f"{label} *(blocked)*"
    return label


def render_intro(intro: dict, scenarios: dict[int, dict], data: dict) -> list[str]:
    lines: list[str] = []
    lines.append(f"### {intro['title']}")
    lines.append("")
    for line in intro.get("lines", []):
        lines.append(line)
        lines.append("")
    for rule in intro.get("conditional", []):
        if matches_when(rule["when"], scenarios, data):
            lines.append(rule["line"])
            lines.append("")
    return lines


def render_arc(
    arc: dict,
    scenarios: dict[int, dict],
    names: dict[int, str],
    data: dict,
    next_scenario: int | None,
) -> list[str]:
    lines: list[str] = []
    status = arc.get("status", "")
    header = f"### {arc['title']}"
    if status:
        header += f" — *{status}*"
    lines.append(header)
    lines.append("")

    trail = arc.get("trail", [])
    if trail:
        done = [n for n in trail if scenario_status(scenarios, n) == "complete"]
        if done:
            chain = " → ".join(format_trail_step(n, names.get(n, "?"), scenarios) for n in done)
            lines.append(f"- **Progress:** {chain}")
        for note in arc.get("trail_notes", []):
            lines.append(f"- {note}")

    for num in arc.get("open", []):
        if scenario_status(scenarios, num) == "incomplete":
            step = format_trail_step(num, names.get(num, "?"), scenarios)
            prefix = "**Next session:** " if num == next_scenario else "**Next / retry:** "
            lines.append(f"- {prefix}{step}")

    future = arc.get("future", [])
    if future:
        not_done = [
            n
            for n in future
            if scenario_status(scenarios, n) not in ("complete", "blocked")
        ]
        if not_done:
            note = arc.get("not_started_note")
            if note:
                lines.append(f"- **Not yet:** {note}")
            else:
                labels = ", ".join(f"**{n}**" for n in not_done)
                lines.append(f"- **Not yet:** {labels}")

    side_list = arc.get("scenarios", [])
    if side_list:
        lines.append("- **Scenario status:**")
        for num in side_list:
            name = names.get(num, "?")
            state = scenario_status(scenarios, num)
            note = scenarios.get(num, {}).get("notes", "").strip()
            detail = state
            if note:
                detail += f" — {note}"
            lines.append(f"  - **{num} {name}:** {detail}")

    hint = arc.get("building_hint")
    if hint:
        building = data.get(hint["key"], {})
        if building.get("level", 0) >= hint.get("min_level", 1):
            lines.append(f"- {hint['line']}")

    if arc.get("plain_terms"):
        lines.append("")
        lines.append(f"**Story:** {arc['plain_terms']}")
    for rule in arc.get("plain_terms_extra", []):
        if matches_when(rule["when"], scenarios, data):
            lines.append("")
            lines.append(rule["line"])

    lines.append("")
    return lines


def render_plot_arcs(
    plot_arcs: dict,
    scenarios: dict[int, dict],
    names: dict[int, str],
    data: dict,
    next_scenario: int | None,
) -> list[str]:
    lines: list[str] = []
    lines.append("## Plot threads — where each arc stands")
    lines.append("")
    lines.append(
        "High-level map of the campaign. Scenario numbers come from the last Storyline export."
    )
    lines.append("")
    if "intro" in plot_arcs:
        lines.extend(render_intro(plot_arcs["intro"], scenarios, data))
    for arc in plot_arcs.get("arcs", []):
        lines.extend(render_arc(arc, scenarios, names, data, next_scenario))
    return lines


def render_choices(
    incomplete_main: list[int],
    incomplete_retirement: list[int],
    scenarios: dict[int, dict],
    names: dict[int, str],
    recaps: dict,
    config: dict,
) -> list[str]:
    lines: list[str] = []
    lines.append("## Choices on the table")
    lines.append("")
    lines.append(
        "Scenarios we **can play next** (or retry), with a story reminder for each. "
        "Pick one when we meet — or cross-check Storyline if something unlocked since the last export."
    )
    lines.append("")

    next_num = config.get("next_scenario")
    next_note = config.get("next_scenario_note", "").strip()
    if isinstance(next_num, int):
        if scenario_status(scenarios, next_num) == "incomplete":
            name = names.get(next_num, "?")
            lines.append("### Next session")
            lines.append("")
            if next_note:
                lines.append(f"*{next_note}*")
                lines.append("")
            lines.extend(
                format_scenario_entry(
                    next_num,
                    name,
                    scenarios[next_num],
                    recaps,
                    highlight=True,
                )
            )
            lines.append("")
            other = [n for n in incomplete_main if n != next_num]
            if other:
                lines.append("### Also available")
                lines.append("")
                for num in other:
                    lines.extend(
                        format_scenario_entry(
                            num, names.get(num, "?"), scenarios[num], recaps
                        )
                    )
        else:
            lines.append(
                f"*Configured next scenario **{next_num}** is not open in this export "
                f"(state: {scenario_status(scenarios, next_num)}). Showing all open scenarios.*"
            )
            lines.append("")
            for num in incomplete_main:
                lines.extend(
                    format_scenario_entry(
                        num, names.get(num, "?"), scenarios[num], recaps
                    )
                )
    elif incomplete_main:
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
    parser = argparse.ArgumentParser(description="Generate campaign recap from Storyline export.")
    parser.add_argument(
        "--export",
        help="Path to export JSON (default: newest exports/*-storyline.json by filename)",
    )
    parser.add_argument(
        "--stamp",
        help="Output date stamp YYYY-MM-DD (default: date from export filename)",
    )
    args = parser.parse_args()

    export_path = resolve_export_path(args.export)
    save = load_save(export_path)
    data = save["data"]
    campaign = data["campaign-fh"]

    stamp = args.stamp or export_stamp(export_path, save)

    with open(ROOT / "data" / "fh-recap-en.json", encoding="utf-8") as f:
        labels = json.load(f)
    recaps = labels.get("scenario", {}).get("recap", {}).get("fh", {})

    with open(ROOT / "data" / "plot-arcs.json", encoding="utf-8") as f:
        plot_arcs = json.load(f)

    config = load_campaign_config()
    next_scenario = config.get("next_scenario")
    if next_scenario is not None:
        next_scenario = int(next_scenario)

    names = load_scenario_names()

    scenarios: dict[int, dict] = {}
    for key, val in data.items():
        if key.startswith("scenario-fh-"):
            num = key.replace("scenario-fh-", "")
            if num.isdigit():
                scenarios[int(num)] = val

    complete = sorted(n for n, s in scenarios.items() if s.get("state") == "complete")
    incomplete = sorted(n for n, s in scenarios.items() if s.get("state") == "incomplete")
    blocked = sorted(n for n, s in scenarios.items() if s.get("state") == "blocked")
    hidden = sorted(n for n, s in scenarios.items() if s.get("state") == "hidden")

    incomplete_main = [n for n in incomplete if n < RETIREMENT_SCENARIO_MIN]
    incomplete_retirement = [n for n in incomplete if n >= RETIREMENT_SCENARIO_MIN]

    lines: list[str] = []
    updated = save.get("updated_at", "?")[:10]
    campaign_name = save.get("name", "campaign")
    lines.append("# Frosthaven — where we left off")
    lines.append("")
    lines.append(
        f"*Campaign **{campaign_name}** — export {updated}. "
        f"Scenario list synced from Storyline — double-check the app before choosing what to play.*"
    )
    lines.append("")
    lines.append("## Outpost snapshot")
    lines.append("")
    lines.append("(From the last manual sync — check your notes for current values.)")
    lines.append("")
    lines.append(f"- **Morale:** {campaign.get('morale', '?')} / 20")
    lines.append(f"- **Prosperity index:** {campaign.get('prosperityIndex', '?')}")
    lines.append(f"- **Inspiration:** {campaign.get('inspiration', '?')}")
    week = campaign.get("calendar", {}).get("week")
    if week is not None:
        lines.append(f"- **Calendar week:** {week}")
    soldiers = campaign.get("soldiers")
    defense = campaign.get("totalDefense")
    if soldiers is not None:
        guard = f"- **Town Guard:** {soldiers} soldiers"
        if defense is not None:
            guard += f" (outpost defense {defense})"
        lines.append(guard)
    lines.append(f"- **Scenarios completed:** {len(complete)}")
    lines.append("")
    lines.extend(
        render_plot_arcs(plot_arcs, scenarios, names, data, next_scenario)
    )
    lines.extend(
        render_choices(
            incomplete_main,
            incomplete_retirement,
            scenarios,
            names,
            recaps,
            config,
        )
    )
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
        f"Regenerate: `python scripts/generate-recap.py` "
        f"(from `{export_path.relative_to(ROOT)}`) → "
        f"`output/{stamp}-recap.html` for sharing. See `data/campaign-notes.md`."
    )
    lines.append("")

    md_text = "\n".join(lines)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dated_md = OUTPUT_DIR / f"{stamp}-recap.md"
    dated_html = OUTPUT_DIR / f"{stamp}-recap.html"
    latest_md = OUTPUT_DIR / "latest-recap.md"
    latest_html = OUTPUT_DIR / "latest-recap.html"

    dated_md.write_text(md_text, encoding="utf-8")
    dated_html.write_text(markdown_to_html(md_text), encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")
    latest_html.write_text(markdown_to_html(md_text), encoding="utf-8")

    print(f"Export: {export_path.relative_to(ROOT)}")
    print(f"Wrote {dated_md.relative_to(ROOT)} ({len(lines)} lines)")
    print(f"Wrote {dated_html.relative_to(ROOT)}")
    print(f"Wrote {latest_md.relative_to(ROOT)} (share this or the .html)")


if __name__ == "__main__":
    main()
