#!/usr/bin/env python3
"""Fetch only image atlases referenced by playable EXE content-pack songs."""
from __future__ import annotations
from pathlib import Path
import json, re, subprocess, sys

def fmt_song(value: str) -> str:
    value = str(value).replace(" ", "-")
    value = re.sub(r"[~&\\;:<>#]", "-", value)
    value = re.sub(r"[.,'\"%?!]", "", value)
    return value.lower()

def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).casefold())

def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], check=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout

def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: prepare_sonicexe_asset_checkout.py source-root engine/assets")
    root, assets = Path(sys.argv[1]), Path(sys.argv[2])

    existing = set()
    weeks = assets / "shared/weeks"
    week_list = weeks / "weekList.txt"
    if week_list.is_file():
        for week_id in (x.strip() for x in week_list.read_text(encoding="utf-8-sig").splitlines()):
            if not week_id:
                continue
            file = weeks / f"{week_id}.json"
            if not file.is_file():
                continue
            try:
                data = json.loads(file.read_text(encoding="utf-8-sig"))
            except Exception:
                continue
            existing.update(fmt_song(row[0]) for row in data.get("songs", [])
                            if isinstance(row, list) and row)

    tree = git(root, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
    tree_set = set(tree)
    candidates: dict[tuple[str, str], str] = {}
    for path in tree:
        match = re.match(r"(?:embedded_contents_file|contents_file)/([^/]+)/data/([^/]+)/\2\.json$", path)
        if not match:
            continue
        pack, slug = match.group(1), match.group(2)
        if fmt_song(slug) in existing:
            continue
        audio = f"contents_file/{pack}/songs/{slug}/"
        if any(audio + f"Inst{ext}" in tree_set for ext in (".ogg", ".mp3", ".wav")):
            candidates[(pack, slug)] = path

    selected_packs = {pack for pack, _ in candidates}
    needed: set[str] = set()
    needed_sounds: set[str] = set()

    def add_sound(pack: str, key: str) -> None:
        key = str(key or "").replace("\\", "/").strip(" /")
        if not key or ".." in key:
            return
        key_path = Path(key)
        extensions = [key_path.suffix] if key_path.suffix else [".ogg", ".mp3", ".wav"]
        for branch in ("contents_file", "embedded_contents_file"):
            sound_root = root / branch / pack / "sounds"
            for ext in extensions:
                candidate = sound_root / (key if key_path.suffix else key + ext)
                if candidate.is_file():
                    needed_sounds.add(candidate.relative_to(root).as_posix())

    def add_image(pack: str, key: str, include_parent: bool = False) -> None:
        key = str(key or "").replace("\\", "/").strip(" /")
        if not key or ".." in key:
            return
        prefix = f"contents_file/{pack}/images/{key}"
        for path in tree:
            if path.startswith(prefix) and Path(path).suffix.casefold() in {".webp", ".png", ".xml", ".json", ".txt"}:
                needed.add(path)
        if include_parent:
            parent = prefix.rsplit("/", 1)[0] if "/" in prefix else prefix
            for path in tree:
                if path.startswith(parent + "/") and Path(path).suffix.casefold() in {".webp", ".png", ".xml", ".json", ".txt"}:
                    needed.add(path)

    def read_script_refs(pack: str, file: Path) -> None:
        try:
            source = file.read_text(encoding="utf-8-sig")
        except Exception:
            return
        # Any literal that names an image atlas or a sound file in this pack is
        # a dependency, even when it is embedded in a Lua/HScript callback.
        for value in re.findall(r"""['"]([^'"]{1,180})['"]""", source):
            value = value.replace("\\", "/").strip()
            if not value or ".." in value or ":" in value:
                continue
            if "/" in value:
                add_image(pack, value, include_parent=True)
            add_sound(pack, value)

    for pack, slug in sorted(candidates):
        for path in tree:
            if path.startswith(f"contents_file/{pack}/data/{slug}/"):
                needed.add(path)

        chart_file = root / candidates[(pack, slug)]
        try:
            chart = json.loads(chart_file.read_text(encoding="utf-8-sig"))
        except Exception:
            chart = {}
        if isinstance(chart.get("song"), dict):
            chart = chart["song"]

        for char_id in (chart.get("player1"), chart.get("player2"), chart.get("player3"), chart.get("gfVersion")):
            char_id = str(char_id or "").strip()
            if not char_id:
                continue
            char_file = root / f"embedded_contents_file/{pack}/characters/{char_id}.json"
            if not char_file.is_file():
                continue
            needed.add(char_file.relative_to(root).as_posix())
            try:
                character = json.loads(char_file.read_text(encoding="utf-8-sig"))
            except Exception:
                character = {}
            add_image(pack, character.get("image", ""))
            icon = str(character.get("healthicon", "")).strip()
            if icon:
                add_image(pack, f"icons/icon-{icon}")

        stage = str(chart.get("stage") or "").strip()
        if stage:
            for ext in (".json", ".lua", ".hx"):
                stage_file = root / f"embedded_contents_file/{pack}/stages/{stage}{ext}"
                if stage_file.is_file():
                    needed.add(stage_file.relative_to(root).as_posix())
                    if ext in {".lua", ".hx"}:
                        read_script_refs(pack, stage_file)

        for branch in ("embedded_contents_file", "contents_file"):
            folder = root / branch / pack / "data" / slug
            if folder.is_dir():
                for script in folder.rglob("*"):
                    if script.is_file() and script.suffix.casefold() in {".lua", ".hx"}:
                        needed.add(script.relative_to(root).as_posix())
                        read_script_refs(pack, script)

    # Song charts can rely on pack-defined note/event handlers, plus their
    # own note atlases, sounds and shaders. Add the script paths to sparse
    # checkout before scanning the source text for those asset references.
    custom_script_files = []
    for pack in sorted(selected_packs):
        for branch in ("embedded_contents_file", "contents_file"):
            for category in ("custom_notetypes", "custom_events"):
                folder = root / branch / pack / category
                if folder.is_dir():
                    for file in folder.rglob("*"):
                        if file.is_file():
                            relative = file.relative_to(root).as_posix()
                            needed.add(relative)
                            if file.suffix.casefold() in {".lua", ".hx"}:
                                custom_script_files.append((pack, file, relative))
            shader_folder = root / branch / pack / "shaders"
            if shader_folder.is_dir():
                for file in shader_folder.rglob("*"):
                    if file.is_file() and file.suffix.casefold() in {".frag", ".vert"}:
                        needed.add(file.relative_to(root).as_posix())

    script_patterns = ["/" + relative for _pack, _file, relative in custom_script_files]
    if script_patterns:
        git(root, "sparse-checkout", "add", *script_patterns)
    for pack, file, _relative in custom_script_files:
        read_script_refs(pack, file)

    for path in tree:
        if path.startswith("contents_file/images/exeSplashes/") and Path(path).suffix.casefold() in {".webp", ".png", ".xml", ".txt"}:
            needed.add(path)

    needed = {path for path in needed if path in tree_set}
    needed_sounds = {path for path in needed_sounds if path in tree_set}
    patterns = ["/" + path for path in sorted(needed | needed_sounds)]
    if patterns:
        git(root, "sparse-checkout", "add", *patterns)

    manifest: dict[str, list[str]] = {}
    for path in sorted(needed):
        match = re.match(r"contents_file/([^/]+)/images/(.+)$", path)
        if match:
            manifest.setdefault(match.group(1), []).append(match.group(2))
        elif path.startswith("contents_file/images/"):
            manifest.setdefault("__shared__", []).append(path.removeprefix("contents_file/images/"))

    sound_manifest: dict[str, list[str]] = {}
    for path in sorted(needed_sounds):
        match = re.match(r"(?:contents_file|embedded_contents_file)/([^/]+)/sounds/(.+)$", path)
        if match:
            sound_manifest.setdefault(match.group(1), []).append(match.group(2))

    output = assets.parent / "sonicexe-pack-assets.json"
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    sound_output = assets.parent / "sonicexe-pack-sounds.json"
    sound_output.write_text(json.dumps(sound_manifest, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(f"Selected {len(candidates)} additional playable chart/audio pairs across {len(selected_packs)} packs.")
    print(f"Fetched {len(patterns)} referenced metadata, image, atlas, script and sound files.")
    print(f"Wrote image manifest with {sum(map(len, manifest.values()))} entries and sound manifest with {sum(map(len, sound_manifest.values()))} entries.")

if __name__ == "__main__":
    main()
