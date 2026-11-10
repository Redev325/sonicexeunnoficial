#!/usr/bin/env python3
"""Import the curated Sonic.EXE mod weeks, charts, audio and required character/stage assets."""

from pathlib import Path
import json
import re
import shutil
import sys


VANILLA_SONGS = {
    "tutorial", "bopeebo", "fresh", "dadbattle", "spookeez", "south", "monster",
    "pico", "phillynice", "blammed", "satinpanties", "high", "milf", "cocoa",
    "eggnog", "winterhorrorland", "senpai", "roses", "thorns", "ugh", "guns",
    "stress", "darnell", "litup", "2hot", "blazin",
}


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).casefold())


def format_song_path(value: str) -> str:
    # Match Psych Engine Paths.formatToSongPath().
    value = str(value).replace(" ", "-")
    value = re.sub(r"[~&\\;:<>#]", "-", value)
    value = re.sub(r"[.,'\"%?!]", "", value)
    return value.lower()


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
    for file in source.rglob("*"):
        if file.is_file():
            relative = file.relative_to(source)
            if copy_file(file, destination / relative):
                copied += 1
    return copied


def find_song_folder(data_root: Path, songs_root: Path, title: str):
    target = format_song_path(title)
    candidates = []
    if data_root.is_dir():
        for folder in data_root.iterdir():
            if not folder.is_dir():
                continue
            if norm(folder.name) == norm(target):
                candidates.append(folder)
    for data_folder in candidates:
        slug = data_folder.name
        hard_chart = data_folder / f"{slug}-hard.json"
        audio_folder = songs_root / slug
        instrumental = next(
            (audio_folder / f"Inst{ext}" for ext in (".mp3", ".ogg", ".wav")
             if (audio_folder / f"Inst{ext}").is_file()),
            None,
        )
        if hard_chart.is_file() and instrumental is not None:
            return slug, data_folder, audio_folder, hard_chart
    return None


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: import_sonicexe_song_data.py sonic-source/assets engine/assets"
        )

    source_assets = Path(sys.argv[1])
    output_assets = Path(sys.argv[2])
    source_weeks = source_assets / "weeks"
    data_root = source_assets / "data"
    songs_root = source_assets / "songs"

    week_list_file = source_weeks / "weekList.txt"
    if not week_list_file.is_file():
        raise SystemExit(f"Sonic.EXE source repository has no {week_list_file}.")

    week_ids = [
        line.strip() for line in week_list_file.read_text(encoding="utf-8-sig").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]

    selected_weeks = []
    selected_song_slugs = set()
    selected_song_names = []
    selected_characters = set()
    selected_stages = set()
    selected_stage_directories = set()
    skipped = []

    for week_id in week_ids:
        week_path = source_weeks / f"{week_id}.json"
        if not week_path.is_file():
            print(f"Skipping week {week_id}: missing {week_path.name}")
            continue

        try:
            week_data = json.loads(week_path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            print(f"Skipping malformed week {week_id}: {exc}")
            continue

        source_rows = week_data.get("songs")
        if not isinstance(source_rows, list):
            print(f"Skipping week {week_id}: songs is not an array")
            continue

        playable_rows = []
        for row in source_rows:
            if not isinstance(row, list) or len(row) < 2:
                skipped.append(f"{week_id}: malformed song row")
                continue

            title = str(row[0])
            key = norm(title)
            if not key or key in VANILLA_SONGS:
                skipped.append(f"{week_id}: stock FNF entry {title}")
                continue

            match = find_song_folder(data_root, songs_root, title)
            if match is None:
                skipped.append(f"{week_id}: {title} (no matching Hard chart + Inst audio)")
                continue

            slug, data_folder, audio_folder, hard_chart = match
            chart_folder = data_folder
            try:
                chart_json = json.loads(hard_chart.read_text(encoding="utf-8-sig"))
            except Exception as exc:
                skipped.append(f"{week_id}: {title} (invalid chart JSON: {exc})")
                continue
            chart_song = chart_json.get("song", chart_json)
            if not isinstance(chart_song, dict):
                skipped.append(f"{week_id}: {title} (unexpected chart format)")
                continue

            selected_song_slugs.add(slug)
            selected_song_names.append(title)

            for character in (row[1], chart_song.get("player1"), chart_song.get("player2"), chart_song.get("gfVersion")):
                if character:
                    selected_characters.add(str(character))

            stage = chart_song.get("stage")
            if stage:
                selected_stages.add(str(stage))

            # The week file's original display name, character and color are kept.
            playable_rows.append(row)

        if playable_rows:
            week_data["songs"] = playable_rows
            week_data["startUnlocked"] = True
            week_data["hideFreeplay"] = False
            week_data["hideStoryMode"] = True
            if not isinstance(week_data.get("weekCharacters"), list) or len(week_data["weekCharacters"]) < 3:
                week_data["weekCharacters"] = ["", "bf", "gf"]
            if not week_data.get("difficulties"):
                week_data["difficulties"] = "Hard"
            selected_weeks.append((week_id, week_data))

    # Import every other song that actually has both a Hard chart and Inst audio.
    # The older importer only walked the three songs listed in weekList.txt, which
    # left most original Sonic.EXE/bonus packs invisible in Freeplay.
    extra_rows = []
    display_names = {
        "b4cksl4sh": "B4CKSL4SH",
        "black-sun": "Black Sun",
        "cycles-encore": "Cycles Encore",
        "endless-og": "Endless OG",
        "fight-or-flight": "Fight or Flight",
        "final-escape": "Final Escape",
        "forestall-desire": "Forestall Desire",
        "manual-blast": "Manual Blast",
        "pre-design": "Pre-Design",
        "round-a-bout": "Round-a-Bout",
        "sharpy-showdown": "Sharpy Showdown",
        "sunshine-encore": "Sunshine Encore",
        "too-fest": "Too-Fest",
        "too-slow-encore": "Too Slow Encore",
        "you-cant-run-encore": "You Can't Run Encore",
        "personel-serious": "Personel Serious",
        "iron-forest": "Iron Forest",
    }

    for data_folder in sorted((p for p in data_root.iterdir() if p.is_dir()), key=lambda p: p.name.casefold()):
        slug = data_folder.name
        if slug in selected_song_slugs:
            continue
        hard_chart = data_folder / f"{slug}-hard.json"
        audio_folder = songs_root / slug
        instrumental = next(
            (audio_folder / f"Inst{ext}" for ext in (".mp3", ".ogg", ".wav")
             if (audio_folder / f"Inst{ext}").is_file()),
            None,
        )
        if not hard_chart.is_file() or instrumental is None:
            continue
        try:
            chart_json = json.loads(hard_chart.read_text(encoding="utf-8-sig"))
            chart_song = chart_json.get("song", chart_json)
        except Exception as exc:
            skipped.append(f"{slug}: invalid Hard chart ({exc})")
            continue
        if not isinstance(chart_song, dict):
            skipped.append(f"{slug}: unexpected Hard chart format")
            continue

        title = display_names.get(slug, slug.replace("-", " ").title())
        song_character = chart_song.get("player2") or chart_song.get("player1") or "sonicexe"
        extra_rows.append([title, str(song_character), [146, 0, 0]])
        selected_song_slugs.add(slug)
        selected_song_names.append(title)

        for character in (chart_song.get("player1"), chart_song.get("player2"), chart_song.get("gfVersion")):
            if character:
                selected_characters.add(str(character))
        stage = chart_song.get("stage")
        if stage:
            selected_stages.add(str(stage))

    if extra_rows:
        selected_weeks.append(("more-songs", {
            "storyName": "More Songs",
            "difficulties": "Hard",
            "hideFreeplay": False,
            "weekBackground": "",
            "weekBefore": "",
            "freeplayColor": [146, 0, 0],
            "startUnlocked": True,
            "hideStoryMode": True,
            "songs": extra_rows,
            "weekCharacters": ["", "bf", "gf"],
            "weekName": "More Songs",
        }))

    # A dedicated hidden-from-Freeplay week keeps the original four-song Story
    # Mode data-select menu using the same shared charts/audio as the browser build.
    story_rows = []
    story_titles = {
        "too-slow": "Too Slow",
        "you-cant-run": "You Can't Run",
        "triple-trouble": "Triple Trouble",
        "final-escape": "Final Escape",
    }
    for slug, title in story_titles.items():
        hard_chart = data_root / slug / f"{slug}-hard.json"
        audio_folder = songs_root / slug
        instrumental = next(
            (audio_folder / f"Inst{ext}" for ext in (".mp3", ".ogg", ".wav")
             if (audio_folder / f"Inst{ext}").is_file()),
            None,
        )
        if not hard_chart.is_file() or instrumental is None:
            raise SystemExit(
                f"Sonic.EXE Story Mode import stopped: {slug} is missing its Hard chart or instrumental."
            )
        chart_json = json.loads(hard_chart.read_text(encoding="utf-8-sig"))
        chart_song = chart_json.get("song", chart_json)
        if not isinstance(chart_song, dict):
            raise SystemExit(f"Sonic.EXE Story Mode import stopped: {slug} has an invalid chart.")
        song_character = chart_song.get("player2") or chart_song.get("player1") or "sonicexe"
        story_rows.append([title, str(song_character), [146, 0, 0]])
        selected_song_slugs.add(slug)

        for character in (chart_song.get("player1"), chart_song.get("player2"), chart_song.get("gfVersion")):
            if character:
                selected_characters.add(str(character))
        stage = chart_song.get("stage")
        if stage:
            selected_stages.add(str(stage))

    selected_weeks.insert(0, ("sonicexe-story", {
        "storyName": "Sonic.EXE",
        "difficulties": "Hard",
        "hideFreeplay": True,
        "weekBackground": "",
        "weekBefore": "",
        "freeplayColor": [146, 0, 0],
        "startUnlocked": True,
        "hideStoryMode": False,
        "songs": story_rows,
        "weekCharacters": ["", "bf", "gf"],
        "weekName": "Sonic.EXE Story",
    }))

    if not selected_weeks:
        raise SystemExit(
            "Sonic.EXE import stopped: no source week contains a song with both a Hard chart and instrumental audio."
        )

    normal_count = sum(
        1
        for week_id, week_data in selected_weeks
        if not week_data.get("hideFreeplay", False)
        for row in week_data["songs"]
        if "encore" not in norm(row[0])
        and "bonus" not in norm(row[0])
        and "extra" not in norm(row[0])
        and "encore" not in norm(week_id)
        and "bonus" not in norm(week_id)
        and "extra" not in norm(week_id)
    )
    if normal_count == 0:
        raise SystemExit("Sonic.EXE import stopped: no regular (non-Encore/non-Bonus) tracks were found.")

    # Replace the default FNF week catalogue completely.
    weeks_output = output_assets / "shared" / "weeks"
    weeks_output.mkdir(parents=True, exist_ok=True)
    for old_file in weeks_output.glob("*.json"):
        old_file.unlink()
    (weeks_output / "weekList.txt").write_text(
        "\n".join(week_id for week_id, _data in selected_weeks) + "\n",
        encoding="utf-8",
    )
    for week_id, week_data in selected_weeks:
        (weeks_output / f"{week_id}.json").write_text(
            json.dumps(week_data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    copied_charts = 0
    copied_audio = 0
    for slug in sorted(selected_song_slugs):
        copied_charts += copy_folder(data_root / slug, output_assets / "shared" / "data" / slug)
        copied_audio += copy_folder(songs_root / slug, output_assets / "songs" / slug)

    # Import only character definitions and sprites actually referenced by the
    # selected weeks or their chart metadata. Existing built-in characters stay intact.
    copied_character_defs = 0
    copied_character_images = 0
    copied_icons = 0
    char_root = source_assets / "characters"
    image_root = source_assets / "images"
    for character in sorted(selected_characters):
        char_json = char_root / f"{character}.json"
        if not char_json.is_file():
            continue
        if copy_file(char_json, output_assets / "shared" / "characters" / char_json.name):
            copied_character_defs += 1

        try:
            char_data = json.loads(char_json.read_text(encoding="utf-8-sig"))
        except Exception:
            char_data = {}

        image_key = char_data.get("image")
        if isinstance(image_key, str) and image_key:
            for ext in (".png", ".xml"):
                relative_image = Path(f"{image_key}{ext}")
                candidates = (
                    image_root / relative_image,
                    source_assets / "shared" / "images" / relative_image,
                )
                for src in candidates:
                    if copy_file(src, output_assets / "shared" / "images" / relative_image):
                        copied_character_images += 1
                        break

        health_icon = char_data.get("healthicon")
        if isinstance(health_icon, str) and health_icon:
            icons_root = image_root / "icons"
            for icon_file in icons_root.glob("*"):
                if icon_file.is_file() and norm(icon_file.stem) in {
                    norm(health_icon), norm("icon-" + health_icon)
                }:
                    if copy_file(icon_file, output_assets / "shared" / "images" / "icons" / icon_file.name):
                        copied_icons += 1

        # Character-specific Lua files are optional, but copy them when present.
        copy_file(char_root / f"{character}.lua",
                  output_assets / "shared" / "characters" / f"{character}.lua")

    # Stage metadata is required for character placement and the correct asset library.
    copied_stages = 0
    for stage in sorted(selected_stages):
        stage_file = source_assets / "stages" / f"{stage}.json"
        if not copy_file(stage_file, output_assets / "shared" / "stages" / f"{stage}.json"):
            print(f"Warning: no stage metadata found for {stage}")
            continue
        copied_stages += 1
        try:
            stage_data = json.loads(stage_file.read_text(encoding="utf-8-sig"))
        except Exception:
            stage_data = {}
        directory = stage_data.get("directory")
        if isinstance(directory, str) and directory:
            selected_stage_directories.add(directory)

    copied_stage_assets = 0
    for directory in sorted(selected_stage_directories):
        copied_stage_assets += copy_folder(
            source_assets / directory,
            output_assets / "week_assets" / directory,
        )

    # Original EXE-stage and cutscene images are requested at runtime from
    # assets/exe/images. Copy the complete directory, not only Final Escape:
    # stages such as Sunky load atlases from sibling folders (for example
    # sunky/sunker.png + sunky/sunker.xml).
    exe_images_source = source_assets / "exe" / "images"
    exe_images_output = output_assets / "exe" / "images"
    required_exe_images = (
        "sunky/sunker.png",
        "sunky/sunker.xml",
        "final escape/broke.xml",
        "final escape/exe line.xml",
        "final escape/block2.xml",
        "final escape/banner.xml",
        "final escape/bf dead.xml",
        "final escape/attack arm.xml",
        "final escape/checkpoint.xml",
    )
    if not exe_images_source.is_dir():
        raise SystemExit(
            "Sonic.EXE import stopped: original EXE image directory is missing "
            f"from the source checkout: {exe_images_source}"
        )

    copied_exe_image_assets = copy_folder(exe_images_source, exe_images_output)
    missing_exe_images = [
        name for name in required_exe_images
        if not (exe_images_output / name).is_file()
    ]
    if missing_exe_images:
        raise SystemExit(
            "Sonic.EXE import stopped: required original EXE image assets were "
            "not copied: " + ", ".join(missing_exe_images)
        )
    print(
        f"Copied original EXE image assets: {copied_exe_image_assets} files; "
        f"validated {len(required_exe_images)} required Sunky/Final Escape files."
    )

    # Original Freeplay and Story Mode visuals. These are source-game files,
    # not generated replacements. Keep them in the shared image library so
    # Paths.image()/Paths.getSparrowAtlas() resolve them on HTML5.
    menu_image_files = (
        "FreeBox.png",
        "BackGROUND.png",
        "Main_Menu_Spritesheet_Animation.png",
        "Main_Menu_Spritesheet_Animation.xml",
        "SPIKES.png",
        "FreePlayShit.png",
        "Menu_Tracks.png",
        "backgroundlool.png",
        "sidebar.png",
        "redbox.png",
        "yellowbox.png",
        "greybox.png",
        "SMMStatic.png",
        "SMMStatic.xml",
        "screenstatic.png",
        "screenstatic.xml",
        "campaign_menu_UI_assets.png",
        "campaign_menu_UI_assets.xml",
        "campaign_menu_UI_assets_alt.png",
        "campaign_menu_UI_assets_alt.xml",
    )
    menu_image_root = source_assets / "images"
    menu_output_root = output_assets / "shared" / "images"
    copied_menu_images = 0
    for name in menu_image_files:
        if not copy_file(menu_image_root / name, menu_output_root / name):
            raise SystemExit(
                f"Sonic.EXE menu import stopped: required original asset is missing: "
                f"{menu_image_root / name}"
            )
        copied_menu_images += 1

    copied_freeplay_art = copy_folder(
        menu_image_root / "fpstuff",
        menu_output_root / "fpstuff",
    )
    expected_freeplay_art = sorted(
        file.name for file in (menu_image_root / "fpstuff").glob("*.png")
        if file.is_file()
    )
    missing_freeplay_art = [
        name for name in expected_freeplay_art
        if not (menu_output_root / "fpstuff" / name).is_file()
    ]
    if not expected_freeplay_art or missing_freeplay_art:
        raise SystemExit(
            "Sonic.EXE menu import stopped: original Freeplay song-card art is "
            "incomplete. Missing: " + (", ".join(missing_freeplay_art) or "all fpstuff PNG files")
        )

    # Preserve the source game's Freeplay song catalogue beside the imported
    # charts. The custom menu uses WeekData for selection, but keeping this
    # original list available avoids silently dropping a source menu resource.
    source_song_list = source_assets / "data" / "freeplaySonglist.txt"
    if not copy_file(source_song_list, output_assets / "shared" / "data" / "freeplaySonglist.txt"):
        raise SystemExit(
            "Sonic.EXE menu import stopped: original Freeplay song list is missing: "
            f"{source_song_list}"
        )

    print(
        f"Copied original Freeplay/Story menu assets: {copied_menu_images} "
        f"root images and atlases plus {copied_freeplay_art} song-card art files; "
        f"validated all {len(expected_freeplay_art)} original card images and "
        "the Freeplay song-list metadata."
    )

    print(f"Imported Sonic.EXE weeks: {', '.join(week_id for week_id, _ in selected_weeks)}")
    print(f"Playable tracks imported: {len(selected_song_names)} ({normal_count} regular; Encore/Bonus/Extra kept for Extras)")
    print("Songs: " + ", ".join(selected_song_names))
    print(f"Skipped entries without a matching Hard chart and instrumental: {len(skipped)}")
    for entry in skipped:
        print("  " + entry)
    print(
        f"Copied charts/data: {copied_charts}; audio: {copied_audio}; "
        f"character JSONs: {copied_character_defs}; character images: {copied_character_images}; "
        f"icons: {copied_icons}; stage JSONs: {copied_stages}; stage asset files: {copied_stage_assets}."
    )


if __name__ == "__main__":
    main()
