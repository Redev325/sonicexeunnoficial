#!/usr/bin/env python3
"""Create small per-stage OpenFL libraries and index actual song audio filenames."""
from pathlib import Path
import json
import re
import shutil
import sys


def library_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9_]+", "_", value.strip().lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    if not slug:
        raise SystemExit(f"Invalid stage directory: {value!r}")
    return slug


def song_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")


def insert_project_entries(project: str, libraries: list[str]) -> str:
    asset_pattern = re.compile(
        r'(?m)^\s*<assets path="assets/week_assets"[^>]*/>\s*\n'
        r'\s*<assets path="assets/week_assets"[^>]*/>'
    )
    match = asset_pattern.search(project)
    if not match:
        raise SystemExit("Stage library setup stopped: the two week_assets asset entries were not found.")
    asset_lines = []
    for library in libraries:
        asset_lines.extend([
            f'\\t<assets path="assets/{library}" library="{library}" rename="assets" exclude="*.ogg" if="web"/>',
            f'\\t<assets path="assets/{library}" library="{library}" rename="assets" exclude="*.mp3" unless="web"/>',
        ])
    project = project[:match.end()] + "\n" + "\n".join(asset_lines) + project[match.end():]

    library_pattern = re.compile(r'(?m)^\s*<library name="week_assets"[^>]*/>')
    matches = list(library_pattern.finditer(project))
    if not matches:
        raise SystemExit("Stage library setup stopped: week_assets library declarations were not found.")
    insert_at = matches[-1].end()
    declarations = "\n".join(
        f'\\t<library name="{library}" preload="false" if="web"/>'
        for library in libraries
    )
    project = project[:insert_at] + "\n" + declarations + project[insert_at:]
    return project


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("Usage: prepare_stage_asset_libraries.py engine/assets engine/Project.xml engine/source/backend/Paths.hx")
    assets_root = Path(sys.argv[1])
    project_path = Path(sys.argv[2])
    paths_path = Path(sys.argv[3])

    stages_root = assets_root / "shared" / "stages"
    week_root = assets_root / "week_assets"
    directories = set()
    for stage_file in sorted(stages_root.glob("*.json")):
        try:
            stage = json.loads(stage_file.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            raise SystemExit(f"Invalid stage JSON {stage_file}: {exc}")
        directory = stage.get("directory")
        if isinstance(directory, str) and directory.strip() and directory.strip().lower() != "shared":
            directories.add(directory.strip())

    slug_map = {}
    for directory in sorted(directories, key=str.casefold):
        slug = library_slug(directory)
        if slug in slug_map and slug_map[slug] != directory:
            raise SystemExit(f"Stage library name collision: {slug_map[slug]!r} and {directory!r}")
        slug_map[slug] = directory

    libraries = []
    for slug, directory in sorted(slug_map.items()):
        source = week_root / directory
        if not source.is_dir():
            raise SystemExit(f"Missing imported stage directory: {source}")
        library = "stage_assets_" + slug
        target_root = assets_root / library
        if target_root.exists():
            shutil.rmtree(target_root)
        # getLibraryPathForce(file, library, currentLevel) resolves to
        # <library>:assets/<lowercase currentLevel>/<file>.
        target_level = target_root / directory.lower()
        shutil.copytree(source, target_level)
        count = sum(1 for path in target_level.rglob("*") if path.is_file())
        if count == 0:
            raise SystemExit(f"Stage asset directory is empty: {source}")
        libraries.append(library)
        print(f"Prepared {library}: {count} files from directory {directory!r}")

    # Use actual filenames, supporting Inst.ogg/wav and multiple Voices-* stems.
    extension_priority = {".mp3": 0, ".ogg": 1, ".wav": 2}
    audio_index = {}
    songs_root = assets_root / "songs"
    for folder in sorted((p for p in songs_root.iterdir() if p.is_dir()), key=lambda p: p.name.casefold()):
        files = [p for p in folder.iterdir() if p.is_file()]
        instruments = [
            p for p in files
            if p.stem.casefold() == "inst" and p.suffix.casefold() in extension_priority
        ]
        if not instruments:
            continue
        instruments.sort(key=lambda p: (extension_priority[p.suffix.casefold()], p.name.casefold()))
        vocals = [
            p.name for p in files
            if p.stem.casefold().startswith("voices") and p.suffix.casefold() in extension_priority
        ]
        vocals.sort(key=str.casefold)
        audio_index[song_slug(folder.name)] = {
            "instrumental": instruments[0].name,
            "vocals": vocals,
        }

    index_file = assets_root / "shared" / "data" / "sonicexe-audio-index.json"
    index_file.parent.mkdir(parents=True, exist_ok=True)
    index_file.write_text(json.dumps(audio_index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Indexed actual audio filenames for {len(audio_index)} songs.")

    project = project_path.read_text(encoding="utf-8")
    project_path.write_text(insert_project_entries(project, libraries), encoding="utf-8")

    paths = paths_path.read_text(encoding="utf-8")
    old = (
        "\t\tif (currentLevel != null)\n"
        "\t\t{\n"
        "\t\t\tvar levelPath:String = '';\n"
        "\t\t\tif(currentLevel != 'shared') {\n"
        "\t\t\t\tlevelPath = getLibraryPathForce(file, 'week_assets', currentLevel);\n"
        "\t\t\t\tif (OpenFlAssets.exists(levelPath, type))\n"
        "\t\t\t\t\treturn levelPath;\n"
        "\t\t\t}\n"
        "\t\t}"
    )
    new = (
        "\t\tif (currentLevel != null)\n"
        "\t\t{\n"
        "\t\t\tvar levelPath:String = '';\n"
        "\t\t\tif(currentLevel != 'shared') {\n"
        "#if html5\n"
        "\t\t\t\tvar invalidCharacters:EReg = ~/[^a-z0-9_]/g;\n"
        "\t\t\t\tvar stageLibrary:String = 'stage_assets_' + invalidCharacters.replace(currentLevel.toLowerCase(), '_');\n"
        "\t\t\t\tlevelPath = getLibraryPathForce(file, stageLibrary, currentLevel);\n"
        "\t\t\t\tif (OpenFlAssets.exists(levelPath, type))\n"
        "\t\t\t\t\treturn levelPath;\n"
        "#end\n"
        "\t\t\t\tlevelPath = getLibraryPathForce(file, 'week_assets', currentLevel);\n"
        "\t\t\t\tif (OpenFlAssets.exists(levelPath, type))\n"
        "\t\t\t\t\treturn levelPath;\n"
        "\t\t\t}\n"
        "\t\t}"
    )
    if paths.count(old) != 1:
        raise SystemExit(f"Stage library setup stopped: Paths.hx block expected once, found {paths.count(old)}.")
    paths_path.write_text(paths.replace(old, new), encoding="utf-8")
    print(f"Registered {len(libraries)} per-stage libraries and patched Paths.hx.")


if __name__ == "__main__":
    main()
