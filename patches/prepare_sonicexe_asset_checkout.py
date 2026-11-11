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
        for value in re.findall(r"""['"]([^'"]{1,180})['"]""", source):
            value = value.replace("\\", "/").strip()
            if not value or ".." in value or ":" in value or "/" not in value:
                continue
            add_image(pack, value, include_parent=True)

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

    # Song charts can rely on pack-defined note and event handlers.
    # PlayState loads these from shared/custom_notetypes and shared/custom_events.
    for pack in sorted(selected_packs):
        for branch in ("embedded_contents_file", "contents_file"):
            for category in ("custom_notetypes", "custom_events"):
                folder = root / branch / pack / category
                if folder.is_dir():
                    for file in folder.rglob("*"):
                        if file.is_file():
                            needed.add(file.relative_to(root).as_posix())

    for path in tree:
        if path.startswith("contents_file/images/exeSplashes/") and Path(path).suffix.casefold() in {".webp", ".png", ".xml", ".txt"}:
            needed.add(path)

    needed = {path for path in needed if path in tree_set}
    patterns = ["/" + path for path in sorted(needed)]
    if patterns:
        git(root, "sparse-checkout", "add", *patterns)

    manifest: dict[str, list[str]] = {}
    for path in sorted(needed):
        match = re.match(r"contents_file/([^/]+)/images/(.+)$", path)
        if match:
            manifest.setdefault(match.group(1), []).append(match.group(2))
        elif path.startswith("contents_file/images/"):
            manifest.setdefault("__shared__", []).append(path.removeprefix("contents_file/images/"))

    output = assets.parent / "sonicexe-pack-assets.json"
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Selected {len(candidates)} additional playable chart/audio pairs across {len(selected_packs)} packs.")
    print(f"Fetched {len(patterns)} referenced metadata, image, atlas and support files.")
    print(f"Wrote image manifest with {sum(map(len, manifest.values()))} entries to {output}.")

if __name__ == "__main__":
    main()
