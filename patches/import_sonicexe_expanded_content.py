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
    "endless-us": "Endless US",
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





def copy_file(source: Path, destination: Path) -> bool:
    if not source.is_file():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return True


def copy_folder(source: Path, destination: Path) -> int:
    if not source.is_dir():
        return 0
    copied = 0
    for path in source.rglob("*"):
        if path.is_file() and copy_file(path, destination / path.relative_to(source)):
            copied += 1
    return copied


def pack_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def copy_pack_assets(source_root: Path, output_assets: Path) -> dict[str, int]:
    manifest_file = output_assets.parent / "sonicexe-pack-assets.json"
    if not manifest_file.is_file():
        raise SystemExit(f"Song asset manifest is missing: {manifest_file}")
    manifest = json.loads(manifest_file.read_text(encoding="utf-8-sig"))
    result = {}
    for pack, files in manifest.items():
        if pack == "__shared__":
            src_root = source_root / "contents_file/images"
            out_root = output_assets / "shared/images"
        else:
            src_root = source_root / "contents_file" / pack / "images"
            out_root = output_assets / "week_assets" / pack_key(pack) / "images"
        copied = 0
        for relative in files:
            relative = Path(relative)
            src = src_root / relative
            if not src.is_file():
                continue
            suffix = src.suffix.casefold()
            if suffix == ".webp":
                target = (out_root / relative).with_suffix(".png")
                target.parent.mkdir(parents=True, exist_ok=True)
                with Image.open(src) as image:
                    image.convert("RGBA").save(target, format="PNG", optimize=True)
                copied += 1
            elif suffix in {".png", ".xml", ".json", ".txt"}:
                target = out_root / relative
                if copy_file(src, target):
                    if suffix == ".xml":
                        # WebP inputs were converted to PNG, so keep Sparrow's
                        # imagePath in sync with the generated sibling image.
                        xml = target.read_text(encoding="utf-8-sig")
                        sibling_png = target.with_suffix(".png")
                        if sibling_png.is_file():
                            xml = re.sub(r"""imagePath\s*=\s*["'][^"']+["']""",
                                         f'imagePath="{sibling_png.name}"', xml, count=1)
                            target.write_text(xml, encoding="utf-8")
                    copied += 1
        result[pack] = copied
    return result


def install_blood_splash(source_root: Path, output_assets: Path, source_stem: str, target_stem: str) -> None:
    source_dir = source_root / "contents_file/images/exeSplashes"
    image_source = source_dir / f"{source_stem}.webp"
    xml_source = source_dir / f"{source_stem}.xml"
    if not image_source.is_file() or not xml_source.is_file():
        raise SystemExit(f"Required Sonic.EXE BloodSplash source is missing: {source_stem}")
    out_dir = output_assets / "shared/images/noteSplashes"
    out_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(image_source) as image:
        image.convert("RGBA").save(out_dir / f"{target_stem}.png", format="PNG", optimize=True)
    xml = xml_source.read_text(encoding="utf-8-sig")
    xml, changed = re.subn(r"""imagePath\s*=\s*["'][^"']+["']""",
                           f'imagePath="{target_stem}.png"', xml, count=1)
    if changed != 1:
        raise SystemExit(f"Could not update BloodSplash atlas XML: {xml_source}")
    (out_dir / f"{target_stem}.xml").write_text(xml, encoding="utf-8")


def copy_pack_sounds(source_root: Path, output_assets: Path) -> int:
    manifest_file = output_assets.parent / "sonicexe-pack-sounds.json"
    if not manifest_file.is_file():
        return 0
    manifest = json.loads(manifest_file.read_text(encoding="utf-8-sig"))
    copied = 0
    for pack, files in manifest.items():
        pack_id = pack_key(pack)
        for relative_name in files:
            relative = Path(relative_name)
            source = source_root / "contents_file" / pack / "sounds" / relative
            if not source.is_file():
                source = source_root / "embedded_contents_file" / pack / "sounds" / relative
            if not source.is_file():
                continue

            # Paths.sound() uses mp3 on HTML5. Convert OGG/WAV dependencies
            # and write both the extensionless-key path and a compatibility
            # path for scripts that included the original extension in a key.
            browser_relative = relative.with_suffix(".mp3")
            browser_target = output_assets / "week_assets" / pack_id / "sounds" / browser_relative
            if not browser_target.is_file():
                convert_audio(source, browser_target)
                copied += 1

            explicit_extension_target = (
                output_assets / "week_assets" / pack_id / "sounds" / Path(str(relative) + ".mp3")
            )
            if explicit_extension_target != browser_target and not explicit_extension_target.is_file():
                convert_audio(source, explicit_extension_target)
    return copied


def find_playable_pairs(source_root: Path):
    """Return charts with their same-pack instrumental and every available vocal stem."""
    seen = set()
    for branch in ("embedded_contents_file", "contents_file"):
        root = source_root / branch
        if not root.is_dir():
            continue
        for pack_dir in sorted((p for p in root.iterdir() if p.is_dir()), key=lambda p: p.name.casefold()):
            data_root = pack_dir / "data"
            if not data_root.is_dir():
                continue
            for song_dir in sorted((p for p in data_root.iterdir() if p.is_dir()), key=lambda p: p.name.casefold()):
                slug = song_dir.name.casefold()
                chart = song_dir / f"{song_dir.name}.json"
                if not chart.is_file() or (pack_dir.name, slug) in seen:
                    continue
                audio_dir = source_root / "contents_file" / pack_dir.name / "songs" / song_dir.name
                if not audio_dir.is_dir():
                    continue
                instrumental = next((audio_dir / f"Inst{ext}" for ext in (".ogg", ".mp3", ".wav")
                                     if (audio_dir / f"Inst{ext}").is_file()), None)
                if instrumental is None:
                    continue
                voices = sorted((p for p in audio_dir.glob("Voices*.*")
                                 if p.suffix.casefold() in {".ogg", ".mp3", ".wav"}),
                                key=lambda p: p.name.casefold())
                seen.add((pack_dir.name, slug))
                yield pack_dir.name, slug, chart, instrumental, voices


def copy_pack_runtime_data(source_root: Path, output_assets: Path, pack: str,
                           slug: str, output_slug: str, chart: dict) -> str:
    pack_id = pack_key(pack)
    original_stage = str(chart.get("stage") or "stage").strip()
    mapped_stage = f"{fmt_song(original_stage)}-{pack_id}"
    stage_source = source_root / "embedded_contents_file" / pack / "stages" / f"{original_stage}.json"
    if stage_source.is_file():
        stage_data = json.loads(stage_source.read_text(encoding="utf-8-sig"))
    else:
        stage_data = {
            "defaultZoom": 0.9, "stageUI": "normal",
            "boyfriend": [770, 100], "opponent": [100, 100], "girlfriend": [400, 130]
        }
    stage_data["directory"] = pack_id
    stage_out = output_assets / "shared/stages" / f"{mapped_stage}.json"
    stage_out.parent.mkdir(parents=True, exist_ok=True)
    stage_out.write_text(json.dumps(stage_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for ext in (".lua", ".hx"):
        script = source_root / "embedded_contents_file" / pack / "stages" / f"{original_stage}{ext}"
        if script.is_file():
            copy_file(script, output_assets / "shared/stages" / f"{mapped_stage}{ext}")

    characters = {
        str(chart.get(key, "")).strip()
        for key in ("player1", "player2", "player3", "gfVersion")
        if str(chart.get(key, "")).strip()
    }
    char_out = output_assets / "week_assets" / pack_id / "characters"
    for character in characters:
        char_file = source_root / "embedded_contents_file" / pack / "characters" / f"{character}.json"
        copy_file(char_file, char_out / char_file.name)
        for branch in ("embedded_contents_file", "contents_file"):
            for ext in (".lua", ".hx"):
                char_script = source_root / branch / pack / "characters" / f"{character}{ext}"
                copy_file(char_script, char_out / char_script.name)

    # Song-specific events/scripts are loaded from shared/data/<song>.
    for branch in ("embedded_contents_file", "contents_file"):
        support = source_root / branch / pack / "data" / slug
        if support.is_dir():
            copy_folder(support, output_assets / "shared" / "data" / output_slug)

    # Keep event/note handlers isolated per EXE pack. PlayState resolves the
    # active week's directory before falling back to shared scripts, preventing
    # same-named handlers from unrelated packs from overwriting one another.
    for branch in ("embedded_contents_file", "contents_file"):
        for category in ("custom_notetypes", "custom_events"):
            source_folder = source_root / branch / pack / category
            if not source_folder.is_dir():
                continue
            # PlayState resolves the active week's directory before shared
            # scripts, so same-named handlers stay isolated between packs.
            target_folder = output_assets / "week_assets" / pack_id / category
            for file in source_folder.rglob("*"):
                if not file.is_file():
                    continue
                target = target_folder / file.relative_to(source_folder)
                if target.is_file():
                    if target.read_bytes() != file.read_bytes():
                        raise SystemExit(
                            f"Conflicting {category} script '{file.name}' within pack '{pack}'."
                        )
                    continue
                copy_file(file, target)
    # The content-pack shader names resolve under the active stage library.
    for branch in ("embedded_contents_file", "contents_file"):
        shader_folder = source_root / branch / pack / "shaders"
        if shader_folder.is_dir():
            copy_folder(shader_folder, output_assets / "week_assets" / pack_id / "shaders")
    return mapped_stage


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
    cover_slugs = {p.stem.casefold() for p in cover_files}
    pack_asset_counts = copy_pack_assets(source_root, output_assets)
    copied_pack_sounds = copy_pack_sounds(source_root, output_assets)
    if not (output_assets / "shared/images/noteSplashes/sonicexe-blood.png").is_file():
        install_blood_splash(source_root, output_assets, "BloodSplash", "sonicexe-blood")
    install_blood_splash(source_root, output_assets, "BloodSplashPixel", "sonicexe-blood-pixel")

    others_rows = []
    copied_charts = 0
    copied_audio = 0
    copied_vocals = 0
    skipped = []
    added_slugs = set()
    audio_index = {}

    for pack, slug, chart_path, instrumental, voices in find_playable_pairs(source_root):
        if slug in existing_rows or slug in added_slugs:
            continue
        try:
            chart = json.loads(chart_path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            skipped.append(f"{pack}/{slug} (invalid chart: {exc})")
            continue
        if isinstance(chart.get("song"), dict):
            chart = chart["song"]
        if not isinstance(chart, dict) or not isinstance(chart.get("notes"), list) or not chart["notes"]:
            skipped.append(f"{pack}/{slug} (chart has no playable note sections)")
            continue

        display_name = DISPLAY_NAMES.get(slug, str(chart.get("song") or slug.replace("-", " ").title()))
        output_slug = fmt_song(display_name)
        if output_slug in existing_rows or output_slug in added_slugs:
            continue
        chart["song"] = display_name
        # Preserve the actual EXE pack characters, stage, note events, BPM, speed,
        # and chart note lanes. Do not replace them with generic BF/Dad/stage data.
        chart.setdefault("player1", "bf")
        chart.setdefault("player2", "dad")
        chart.setdefault("gfVersion", "gf")
        chart.setdefault("bpm", 100)
        chart.setdefault("speed", 1)
        chart.setdefault("events", [])
        chart["needsVoices"] = bool(voices)

        mapped_stage = copy_pack_runtime_data(source_root, output_assets, pack, slug, output_slug, chart)
        chart["stage"] = mapped_stage

        chart_output = output_assets / "shared/data" / output_slug / f"{output_slug}-hard.json"
        chart_output.parent.mkdir(parents=True, exist_ok=True)
        chart_output.write_text(
            json.dumps({"song": chart}, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        copied_charts += 1

        song_output = output_assets / "songs" / output_slug
        convert_audio(instrumental, song_output / "Inst.mp3")
        copied_audio += 1
        voice_names = []
        for voice in voices:
            name = voice.stem + ".mp3"
            convert_audio(voice, song_output / name)
            voice_names.append(name)
            copied_vocals += 1
        if voice_names:
            audio_index[output_slug] = sorted(voice_names)

        row_character = str(chart.get("player2") or chart.get("player1") or "dad")
        song_color = chart.get("freeplayColor", [146, 0, 0])
        if not isinstance(song_color, list) or len(song_color) < 3:
            song_color = [146, 0, 0]
        others_rows.append([display_name, row_character, song_color])
        added_slugs.add(output_slug)

    # Keep an index for both expanded-pack vocals and the restored root game's
    # ordinary Voices.mp3 tracks so the HTML5 loader can fetch the correct stems.
    for song_dir in sorted((p for p in (output_assets / "songs").iterdir() if p.is_dir()), key=lambda p: p.name):
        names = sorted(p.name for p in song_dir.glob("Voices*.mp3") if p.is_file())
        if names:
            audio_index[song_dir.name] = names
    index_file = output_assets / "shared/data/sonicexe-audio-index.json"
    index_file.parent.mkdir(parents=True, exist_ok=True)
    index_file.write_text(json.dumps(audio_index, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")

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

    # Supply a genuine alias cover when one exists; only use the placeholder as a last resort.
    placeholder = freeplay_output / "covers/placeholder.png"
    for week_id in week_ids + (["others"] if others_rows else []):
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
            song_slug = fmt_song(row[0])
            target = freeplay_output / "covers" / f"{song_slug}.png"
            if target.is_file():
                continue
            alias = COVER_ALIASES.get(song_slug)
            alias_target = freeplay_output / "covers" / f"{alias}.png" if alias else None
            if alias_target and alias_target.is_file():
                shutil.copy2(alias_target, target)
            else:
                shutil.copy2(placeholder, target)

    print(f"Imported original EXE Freeplay art: {freeplay_count} files ({len(cover_files)} cover files scanned).")
    print(f"Imported original EXE Story Mode art: {story_count + story_cover_count} files.")
    print(f"Imported all playable expanded-pack tracks: {len(others_rows)} (charts: {copied_charts}, MP3 instrumentals: {copied_audio}).")
    print(f"Imported vocal stems: {copied_vocals}; referenced pack images/atlases: {sum(pack_asset_counts.values())}; pack sound effects: {copied_pack_sounds}.")
    if added_slugs:
        print("Others songs: " + ", ".join(DISPLAY_NAMES.get(s, s.replace("-", " ").title()) for s in sorted(added_slugs)))
    if skipped:
        print(f"Skipped cover entries without a matching chart + instrumental or compatible chart: {len(skipped)}")
    if not others_rows:
        print("No new Others rows were added; source weeks already contain all available chart/audio pairs.")


if __name__ == "__main__":
    main()
