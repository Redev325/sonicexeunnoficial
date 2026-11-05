#!/usr/bin/env python3
"""Keep the songs library preloaded on HTML5.

The deferred OpenFL AssetLibrary load could remain unresolved in the browser,
leaving every song-backed destination on a black transition screen. Options
does not depend on the songs library, which is why it remained accessible.
Use the engine's normal preload path for reliable menu entry.
"""
from pathlib import Path
import re
import sys


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage: apply_loading_optimization.py Project.xml TitleState.hx MainMenuState.hx"
        )

    project = Path(sys.argv[1])
    source = project.read_text(encoding="utf-8")
    pattern = re.compile(
        r'(?m)^(\s*<library\s+name="songs"\s+preload=")(?:true|false)("\s*/>)$'
    )
    source, count = pattern.subn(r"\1true\2", source)
    if count != 1:
        raise SystemExit(
            "HTML5 song loading fix stopped: expected exactly one songs library entry, "
            f"found {count}."
        )
    if not re.search(
        r'(?m)^\s*<library\s+name="week_assets"\s+preload="true"\s*/>\s*$',
        source,
    ):
        raise SystemExit("HTML5 song loading fix stopped: week_assets must remain preloaded.")
    project.write_text(source, encoding="utf-8")
    print("Restored normal HTML5 preload for songs; menu destinations no longer wait on a deferred library request.")


if __name__ == "__main__":
    main()
