#!/usr/bin/env python3
"""Defer the HTML5 songs library until the title sequence, then gate song menus on it."""

from pathlib import Path
import re
import sys


def patch_project(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r'(?m)^(\s*<library\s+name="songs"\s+preload=")true("\s*/>)$'
    )
    source, count = pattern.subn(r"\1false\2", source)
    if count != 1:
        raise SystemExit(
            "Loading optimization stopped: expected exactly one preloaded songs library, "
            f"found {count}."
        )

    # Keep week art and metadata available to Story Mode and Freeplay.
    if not re.search(
        r'(?m)^\s*<library\s+name="week_assets"\s+preload="true"\s*/>\s*$',
        source,
    ):
        raise SystemExit(
            "Loading optimization stopped: the week_assets library is not still preloaded."
        )

    path.write_text(source, encoding="utf-8")
    print("Deferred only the separate songs library; shared and week assets remain preloaded.")


def patch_title(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    old = (
        "\t\tsuper.create();\n"
        "\n"
        "\t\tFlxG.save.bind('funkin', CoolUtil.getSavePath());"
    )
    new = (
        "\t\tsuper.create();\n"
        "\n"
        "\t\t#if html5\n"
        "\t\t// Fetch song audio while the Sonic.EXE warning and intro sequence play.\n"
        "\t\tbackend.SonicEXEAssetLoader.beginSongLibraryLoad();\n"
        "\t\t#end\n"
        "\n"
        "\t\tFlxG.save.bind('funkin', CoolUtil.getSavePath());"
    )
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"Loading optimization stopped: expected one TitleState startup anchor, found {count}."
        )
    if "SonicEXEAssetLoader.beginSongLibraryLoad()" in source:
        raise SystemExit("Loading optimization stopped: TitleState was already patched.")
    path.write_text(source.replace(old, new), encoding="utf-8")
    print("Started the songs download during the title sequence.")


def patch_menu(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    if "SonicEXEAssetLoader.ensureSongLibraryLoaded" in source:
        raise SystemExit("Loading optimization stopped: MainMenuState was already patched.")

    pattern = re.compile(
        r"(?m)^(\t*)MusicBeatState\.switchState\(new (StoryMenuState|FreeplayState)\(\)\);$"
    )
    matches = pattern.findall(source)
    story_count = sum(1 for _, target in matches if target == "StoryMenuState")
    freeplay_count = sum(1 for _, target in matches if target == "FreeplayState")
    if story_count != 1 or freeplay_count != 3:
        raise SystemExit(
            "Loading optimization stopped: expected one Story Mode route and three Freeplay "
            f"routes (regular + Sound Test + Extras/Encore), found Story={story_count}, Freeplay={freeplay_count}."
        )

    def guarded_route(match: re.Match) -> str:
        indent, target = match.groups()
        return (
            f"{indent}backend.SonicEXEAssetLoader.ensureSongLibraryLoaded(function():Void {{\n"
            f"{indent}\tMusicBeatState.switchState(new {target}());\n"
            f"{indent}}}, function(error:Dynamic):Void {{\n"
            f"{indent}\ttrace('Sonic.EXE could not load the songs library: ' + error);\n"
            f"{indent}\tMusicBeatState.sonicExeTransitionIn = false;\n"
            f"{indent}\tMusicBeatState.switchState(new MainMenuState());\n"
            f"{indent}}});"
        )

    source, count = pattern.subn(guarded_route, source)
    if count != 4:
        raise SystemExit(
            f"Loading optimization stopped: expected to guard 4 menu routes, patched {count}."
        )
    path.write_text(source, encoding="utf-8")
    print("Guarded Story Mode, regular Freeplay, Sound Test and Extras/Encore until song audio is ready.")


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage: apply_loading_optimization.py Project.xml TitleState.hx MainMenuState.hx"
        )

    patch_project(Path(sys.argv[1]))
    patch_title(Path(sys.argv[2]))
    patch_menu(Path(sys.argv[3]))


if __name__ == "__main__":
    main()
