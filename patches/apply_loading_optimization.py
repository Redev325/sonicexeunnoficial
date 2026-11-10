#!/usr/bin/env python3
"""Defer large HTML5 asset libraries and apply browser-friendly defaults once."""

from pathlib import Path
import re
import sys


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"HTML5 performance patch stopped: {label} expected once, found {count}")
    return source.replace(old, new)


def patch_project(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    for library in ("songs", "week_assets"):
        pattern = re.compile(
            rf'(?m)^([ \t]*)<library name="{library}" preload="(?:true|false)"\s*/>$'
        )
        source, count = pattern.subn(
            rf'\1<library name="{library}" preload="false" if="html5" />' + "\n"
            + rf'\1<library name="{library}" preload="true" unless="html5" />',
            source,
        )
        if count != 1:
            raise SystemExit(
                f"HTML5 performance patch stopped: expected one {library} library entry, found {count}"
            )
    path.write_text(source, encoding="utf-8")
    print("HTML5 only: song audio and stage assets will load on demand.")


def patch_title_state(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    addition = """\t\tClientPrefs.loadPrefs();

\t\t#if html5
\t\t// Start with a lighter browser profile once. These settings remain
\t\t// editable in Options and are not forced again on later launches.
\t\tif (FlxG.save.data.sonicEXEPerformanceConfigured != true)
\t\t{
\t\t\tClientPrefs.data.lowQuality = true;
\t\t\tClientPrefs.data.shaders = false;
\t\t\tClientPrefs.data.antialiasing = false;
\t\t\tClientPrefs.data.framerate = 60;
\t\t\tFlxG.updateFramerate = 60;
\t\t\tFlxG.drawFramerate = 60;
\t\t\tFlxG.save.data.sonicEXEPerformanceConfigured = true;
\t\t\tClientPrefs.saveSettings();
\t\t}
\t\tFlxG.game.focusLostFramerate = 15;
\t\t#end"""
    source = replace_once(
        source,
        "\t\tClientPrefs.loadPrefs();",
        addition,
        "one-time HTML5 performance profile",
    )
    path.write_text(source, encoding="utf-8")
    print("Installed one-time 60 FPS / reduced-effects HTML5 profile; Options can override it.")


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage: apply_loading_optimization.py Project.xml TitleState.hx MainMenuState.hx"
        )
    patch_project(Path(sys.argv[1]))
    patch_title_state(Path(sys.argv[2]))


if __name__ == "__main__":
    main()
