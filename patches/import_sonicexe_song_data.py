#!/usr/bin/env python3
"""Import playable, non-vanilla Sonic.EXE songs from the original release archive."""

from pathlib import Path, PurePosixPath
from zipfile import ZipFile
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
BONUS_TERMS = ("encore", "bonus", "extra")


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).casefold())


def is_bonus(value: str) -> bool:
    key = norm(value)
    return any(term in key for term in BONUS_TERMS)


def path_contains_song(path: str, song_key: str, root_name: str) -> bool:
    parts = [norm(part) for part in PurePosixPath(path).parts]
    try:
        root_index = next(i for i, part in enumerate(parts) if part == root_name)
    except StopIteration:
        return False
    return song_key in parts[root_index + 1:]


def copy_entries(z: ZipFile, names: list[str], predicate, destination: Path) -> int:
    copied = 0
    for name in names:
        if not predicate(name) or name.endswith("/"):
            continue
        suffix = PurePosixPath(name).parts
        if not suffix or suffix[0].casefold() != "assets":
            continue
        target = destination.joinpath(*suffix[1:])
        target.parent.mkdir(parents=True, exist_ok=True)
        with z.open(name) as source, target.open("wb") as output:
            shutil.copyfileobj(source, output)
        copied += 1
    return copied


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: import_sonicexe_song_data.py package/release.zip engine/assets")

    archive = Path(sys.argv[1])
    output_assets = Path(sys.argv[2])
    if not archive.is_file():
        raise SystemExit(f"Original Sonic.EXE release archive not found: {archive}")

    with ZipFile(archive) as z:
        names = z.namelist()
        week_lists = [
            name for name in names
            if PurePosixPath(name).name.casefold() == "weeklist.txt"
            and any(part.casefold() == "weeks" for part in PurePosixPath(name).parts)
        ]
        if not week_lists:
            print("Sonic.EXE archive week/data inventory (no weeks/weekList.txt found):")
            week_related = [
                name for name in names
                if "week" in name.casefold()
                and (PurePosixPath(name).suffix.casefold() in {".txt", ".json", ".xml"})
            ]
            chart_related = [
                name for name in names
                if PurePosixPath(name).suffix.casefold() == ".json"
                and any(part.casefold() in {"data", "songs", "charts"} for part in PurePosixPath(name).parts)
            ]
            audio_related = [
                name for name in names
                if PurePosixPath(name).suffix.casefold() in {".ogg", ".mp3", ".wav"}
                and any(part.casefold() in {"songs", "music", "audio"} for part in PurePosixPath(name).parts)
            ]
            print("Week-related files (" + str(len(week_related)) + "):")
            for name in week_related[:160]:
                print("  " + name)
            print("Chart/data JSON files (" + str(len(chart_related)) + "):")
            for name in chart_related[:160]:
                print("  " + name)
            print("Song/audio files (" + str(len(audio_related)) + "):")
            for name in audio_related[:160]:
                print("  " + name)

            contents_files = [name for name in names if name.casefold().startswith("contents/") and not name.endswith("/")]
            by_suffix = {}
            for name in contents_files:
                suffix = PurePosixPath(name).suffix.casefold() or "<no extension>"
                by_suffix.setdefault(suffix, []).append(name)
            print("Contents file types:")
            for suffix, entries in sorted(by_suffix.items()):
                print(f"  {suffix}: {len(entries)}")
            for suffix in (".json", ".jsonc", ".txt", ".hx", ".xml", ".fnfc", ".chart", ".bin", ".csv", ".yaml", ".yml"):
                entries = by_suffix.get(suffix, [])
                if entries:
                    print(f"Contents {suffix} files ({len(entries)}):")
                    for name in entries[:240]:
                        print("  " + name)
            raise SystemExit("Sonic.EXE import stopped: archive has no week list; file-type inventory above identifies alternate chart formats.")

        data_json = [
            name for name in names
            if name.casefold().endswith(".json") and "/data/" in name.casefold()
        ]
        song_audio = [
            name for name in names
            if name.casefold().startswith("assets/songs/")
            and PurePosixPath(name).suffix.casefold() in {".ogg", ".mp3", ".wav"}
        ]

        candidates = []
        for list_path in week_lists:
            folder = PurePosixPath(list_path).parent
            try:
                week_ids = [
                    line.strip() for line in z.read(list_path).decode("utf-8-sig").splitlines()
                    if line.strip() and not line.lstrip().startswith("#")
                ]
            except Exception as exc:
                print(f"Skipping unreadable week list {list_path}: {exc}")
                continue

            accepted_weeks = []
            accepted_songs = []
            chart_paths = set()
            audio_paths = set()
            for week_id in week_ids:
                week_path = str(folder / f"{week_id}.json")
                if week_path not in names:
                    continue
                try:
                    week_data = json.loads(z.read(week_path).decode("utf-8-sig"))
                except Exception as exc:
                    print(f"Skipping malformed week metadata {week_path}: {exc}")
                    continue

                week_songs = week_data.get("songs")
                if not isinstance(week_songs, list):
                    continue

                playable_rows = []
                for row in week_songs:
                    if not isinstance(row, list) or not row:
                        continue
                    title = str(row[0])
                    key = norm(title)
                    if not key or key in VANILLA_SONGS:
                        continue

                    charts = {
                        name for name in data_json
                        if path_contains_song(name, key, "data")
                    }
                    audio = {
                        name for name in song_audio
                        if path_contains_song(name, key, "songs")
                    }
                    if not charts or not audio:
                        continue
                    playable_rows.append(row)
                    chart_paths.update(charts)
                    audio_paths.update(audio)

                if playable_rows:
                    week_data["songs"] = playable_rows
                    accepted_weeks.append((week_id, week_path, week_data))
                    accepted_songs.extend(str(row[0]) for row in playable_rows)

            score = len(accepted_songs)
            candidates.append((score, list_path, accepted_weeks, accepted_songs, chart_paths, audio_paths))

        if not candidates:
            raise SystemExit("Sonic.EXE import stopped: no readable week-list candidates were found.")
        candidates.sort(key=lambda item: item[0], reverse=True)
        score, chosen_list, selected_weeks, selected_songs, chart_paths, audio_paths = candidates[0]

        print("Sonic.EXE release week-list candidates:")
        for candidate in candidates:
            print(f"  {candidate[1]}: {len(candidate[3])} playable non-vanilla/non-bonus songs")
        if score == 0:
            raise SystemExit(
                "Sonic.EXE import stopped: no non-vanilla, non-Encore/bonus tracks had both chart JSON and instrumental audio. "
                "No stock FNF weeks will be silently left in Freeplay."
            )

        # Replace only the base game's week metadata with the discovered Sonic.EXE
        # weeks. Entries containing Encore/Bonus/Extra are deliberately omitted.
        weeks_output = output_assets / "shared" / "weeks"
        weeks_output.mkdir(parents=True, exist_ok=True)
        for old_file in weeks_output.glob("*.json"):
            old_file.unlink()
        (weeks_output / "weekList.txt").write_text(
            "\n".join(week_id for week_id, _path, _data in selected_weeks) + "\n",
            encoding="utf-8",
        )
        for week_id, _week_path, week_data in selected_weeks:
            (weeks_output / f"{week_id}.json").write_text(
                json.dumps(week_data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

        copied_charts = copy_entries(
            z, names,
            lambda name: name in chart_paths,
            output_assets,
        )
        copied_audio = copy_entries(
            z, names,
            lambda name: name in audio_paths,
            output_assets,
        )

        # Bring over common custom character, icon, menu-character and stage art
        # directories used by the imported weeks. These are game assets, not
        # generated substitutes.
        copied_support = copy_entries(
            z, names,
            lambda name: any(
                token in name.casefold()
                for token in (
                    "assets/shared/characters/",
                    "assets/shared/images/characters/",
                    "assets/shared/images/icons/",
                    "assets/shared/images/menucharacters/",
                    "assets/shared/images/menubackgrounds/",
                    "assets/week_assets/",
                )
            ),
            output_assets,
        )

        print(f"Imported {len(selected_weeks)} Sonic.EXE weeks from {chosen_list}.")
        print("Imported playable Sonic.EXE tracks (Encore/Bonus/Extra retained for the separate Extras list): " + ", ".join(selected_songs))
        print(f"Copied chart files: {copied_charts}; instrumental/voice files: {copied_audio}; support assets: {copied_support}.")


if __name__ == "__main__":
    main()
