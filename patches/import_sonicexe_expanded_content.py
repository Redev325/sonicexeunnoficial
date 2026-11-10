#!/usr/bin/env python3
"""Import the original EXE Freeplay/Story artwork and playable songs from content packs.

Source: Wolfie1985yt/EXEUNOFFICIAL, pinned by the build workflow.
This imports only original UI assets and tracks that have both a chart and Inst audio.
"""
from __future__ import annotations

from pathlib import Path
import json
import re
import shutil
import subprocess
import sys

from PIL import Image


DISPLAY_NAMES = {
    "universal-collapse": "Universal Collapse",
    "b4cksl4sh": "B4CKSL4SH",
    "manual-blast": "Manual Blast",
    "round-a-bout": "Round-a-Bout",
    "pre-design": "Pre-Design",
    "her-world": "Her World",
    "malediction": "Malediction",
    "longstrider": "Longstrider",
    "fight-or-flight": "Fight or Flight",
    "mania": "Mania",
    "miasma": "Miasma",
    "shocker": "Shocker",
    "hollow": "Hollow",
    "forestall-desire": "Forestall Desire",
    "hellbent": "Hellbent",
    "fate": "Fate",
    "prey": "Prey",
    "fatality": "Fatality",
    "substantial": "Substantial",
    "sharpy-showdown": "Sharpy Showdown",
    "found-you": "Found You",
    "endless-og": "Endless OG",
    "endless-us": "Endless",
    "endless-jp": "Endless JP",
}

COVER_ALIASES = {
    "endless": "endless-us",
    "endless-og": "endless-us",
    "milk": "chocolate-milk",
    "too-slow": "placeholder",
    "you-cant-run": "placeholder",
    "triple-trouble": "placeholder",
    "final-escape": "placeholder",
}


def fmt_song(value: str) -> str:
    value = str(value).replace(" ", "-")
    value = re.sub(r"[~&\\;:<>#]", "-", value)
    value = re.sub(r"[.,'\"%?!]", "", value)
    return value.lower()


def copy_webp_tree(source: Path, destination: Path) -> int:
    """Convert source WebP artwork to PNG while preserving original pixels/alpha."""
    if not source.is_dir():
        raise SystemExit(f"Required original art directory is missing: {source}")
    copied = 0
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(source)
        suffix = path.suffix.casefold()
        if suffix == ".webp":
            target = (destination / rel).with_suffix(".png")
            target.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(path) as image:
                image.convert("RGBA").save(target, format="PNG", optimize=True)
            copied += 1
        elif suffix in {".xml", ".json", ".txt"}:
            target = destination / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            copied += 1
    return copied


def find_chart(source_root: Path, slug: str) -> Path | None:
    candidates = []
    for branch in ("embedded_contents_file", "contents_file"):
        candidates.extend(source_root.glob(f"{branch}/*/data/{slug}/{slug}.json"))
    candidates = [p for p in candidates if p.is_file()]
    return sorted(candidates, key=lambda p: ("/embedded_contents_file/" not in p.as_posix(), p.as_posix()))[0] if candidates else None


def find_instrumental(source_root: Path, slug: str) -> Path | None:
    candidates = []
    for branch in ("contents_file", "embedded_contents_file"):
        for ext in (".ogg", ".mp3", ".wav"):
            candidates.extend(source_root.glob(f"{branch}/*/songs/{slug}/Inst{ext}"))
    candidates = [p for p in candidates if p.is_file()]
    # Prefer the ordinary mix over alternate VHS/variant mixes.
    return sorted(candidates, key=lambda p: (p.name.casefold() != "inst.ogg", p.name.casefold() != "inst.mp3", p.as_posix()))[0] if candidates else None


def convert_audio(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix.casefold() == ".mp3":
        shutil.copy2(source, target)
        return
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", str(source), "-vn", "-c:a", "libmp3lame", "-q:a", "2", str(target)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0 or not target.is_file() or target.stat().st_size == 0:
        raise SystemExit(f"Failed to convert {source} to HTML5 MP3:\n{result.stdout[-5000:]}")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: import_sonicexe_expanded_content.py exe-source-root engine/assets")
    source_root = Path(sys.argv[1])
    output_assets = Path(sys.argv[2])

    # Original Freeplay background, frame, spike strip, and every supplied song cover.
    freeplay_source = source_root / "assets/exe/freeplayassets"
    freeplay_output = output_assets / "shared/images/sonicexe-freeplay"
    freeplay_count = copy_webp_tree(freeplay_source, freeplay_output)
    for required in ("bgsonic.png", "spikesup.png", "FreeBox.png", "covers/placeholder.png"):
        if not (freeplay_output / required).is_file():
            raise SystemExit(f"Original Freeplay asset was not imported: {required}")

    # Original Sonic.EXE data-select assets: six cloud layers, animated static,
    # the DATA SELECT heading, character animation, boxes, arrows, and lock.
    story_source = source_root / "assets/exe/story"
    story_output = output_assets / "shared/images/sonicexe-story"
    story_count = copy_webp_tree(story_source, story_output)
    cover_source = source_root / "assets/exe/cover"
    story_covers = story_output / "covers"
    story_cover_count = copy_webp_tree(cover_source, story_covers)
    required_story = (
        "SMMStatic.png", "SMMStatic.xml", "screenstatic.png", "screenstatic.xml",
        "dataselect.png", "dataselect.xml", "greybox.png", "yellowbox.png",
        "bf_menu.png", "bf_menu.xml", "cuadro.png", "cuadro.xml",
        "arrow.png", "gf.png", "padLock.png", "padLock.xml",
        "covers/too-slow.png", "covers/you-cant-run.png",
        "covers/triple-trouble.png", "covers/final-escape.png",
    )
    missing_story = [name for name in required_story if not (story_output / name).is_file()]
    if missing_story:
        raise SystemExit("Original Story Mode artwork is incomplete: " + ", ".join(missing_story))

    # Import the four source Story Mode charts' soundtrack if supplied.
    story_music = source_root / "assets/exe/music/story.ogg"
    if story_music.is_file():
        convert_audio(story_music, output_assets / "shared/music/sonicexe-story.mp3")

    # Existing root-source weeks may already include some tracks. Preserve those rows,
    # and add the wider screenshot catalogue in a distinct, unlocked "Others" week.
    weeks_dir = output_assets / "shared/weeks"
    week_list_path = weeks_dir / "weekList.txt"
    if not week_list_path.is_file():
        raise SystemExit(f"Existing Sonic.EXE week list is missing: {week_list_path}")
    week_ids = [line.strip() for line in week_list_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    existing_rows = set()
    for week_id in week_ids:
        week_path = weeks_dir / f"{week_id}.json"
        if not week_path.is_file():
            continue
        try:
            week_data = json.loads(week_path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        for row in week_data.get("songs", []):
            if isinstance(row, list) and row:
                existing_rows.add(fmt_song(str(row[0])))

    cover_files = sorted((freeplay_source / "covers").glob("*.webp"), key=lambda p: p.stem.casefold())
    others_rows = []
    copied_charts = 0
    copied_audio = 0
    skipped = []
    added_slugs = set()

    for cover in cover_files:
        slug = cover.stem.casefold()
        chart_path = find_chart(source_root, slug)
        instrumental = find_instrumental(source_root, slug)
        if chart_path is None or instrumental is None:
            skipped.append(slug)
            continue
        if slug in existing_rows:
            continue

        try:
            chart = json.loads(chart_path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            skipped.append(f"{slug} (invalid chart: {exc})")
            continue
        if isinstance(chart.get("song"), dict):
            chart = chart["song"]
        if not isinstance(chart, dict) or not isinstance(chart.get("notes"), list):
            skipped.append(f"{slug} (unsupported chart structure)")
            continue

        display_name = DISPLAY_NAMES.get(slug, slug.replace("-", " ").title())
        chart["song"] = display_name
        # Use engine-native characters/stage so these charts never request an
        # unavailable content-pack character or stage atlas in this browser build.
        chart["player1"] = "bf"
        chart["player2"] = "dad"
        chart["gfVersion"] = "gf"
        chart["stage"] = "stage"
        chart.pop("player3", None)
        chart["needsVoices"] = False
        chart.setdefault("bpm", 100)
        chart.setdefault("speed", 1)
        chart.setdefault("events", [])

        chart_output = output_assets / "shared/data" / slug / f"{slug}-hard.json"
        chart_output.parent.mkdir(parents=True, exist_ok=True)
        chart_output.write_text(json.dumps({"song": chart}, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        copied_charts += 1

        convert_audio(instrumental, output_assets / "songs" / slug / "Inst.mp3")
        copied_audio += 1

        others_rows.append([display_name, "dad", [146, 0, 0]])
        existing_rows.add(slug)
        added_slugs.add(slug)

    # Add an explicit Others category to Freeplay + Other songs. The ordinary
    # Freeplay songs remain in their existing weeks; this category contains the
    # newly imported bonus/content-pack catalogue.
    if others_rows:
        others_path = weeks_dir / "others.json"
        others_data = {
            "storyName": "Others",
            "weekName": "Others",
            "difficulties": "Hard",
            "weekBackground": "",
            "weekBefore": "",
            "freeplayColor": [146, 0, 0],
            "startUnlocked": True,
            "hideStoryMode": True,
            "hideFreeplay": False,
            "weekCharacters": ["", "bf", "gf"],
            "songs": others_rows,
        }
        others_path.write_text(json.dumps(others_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if "others" not in week_ids:
            week_ids.append("others")
            week_list_path.write_text("\n".join(week_ids) + "\n", encoding="utf-8")

    # Ensure every track known to the existing weeks has a real cover path. The
    # original placeholder is used only when the source does not provide a cover.
    placeholder = freeplay_output / "covers/placeholder.png"
    for week_id in week_ids:
        week_path = weeks_dir / f"{week_id}.json"
        if not week_path.is_file():
            continue
        try:
            week_data = json.loads(week_path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        for row in week_data.get("songs", []):
            if not isinstance(row, list) or not row:
                continue
            slug = fmt_song(row[0])
            target = freeplay_output / "covers" / f"{slug}.png"
            if not target.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(placeholder, target)

    print(f"Imported original EXE Freeplay art: {freeplay_count} files ({len(cover_files)} cover files scanned).")
    print(f"Imported original EXE Story Mode art: {story_count + story_cover_count} files.")
    print(f"Imported new playable Others tracks: {len(others_rows)} (charts: {copied_charts}, MP3 instrumentals: {copied_audio}).")
    if added_slugs:
        print("Others songs: " + ", ".join(DISPLAY_NAMES.get(s, s.replace("-", " ").title()) for s in sorted(added_slugs)))
    if skipped:
        print(f"Skipped cover entries without a matching chart + instrumental or compatible chart: {len(skipped)}")
    if not others_rows:
        print("No new Others rows were added; source weeks already contain all available chart/audio pairs.")


if __name__ == "__main__":
    main()
