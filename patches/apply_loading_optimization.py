#!/usr/bin/env python3
"""Defer the large songs library and load only the selected track on HTML5.

LoadingState initializes the songs manifest and requests the selected
instrumental/vocals. Freeplay previews use the same per-file loading path.
This avoids downloading and decoding the entire mod catalogue during boot.
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
    source, count = pattern.subn(r"\1false\2", source)
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
    print("Deferred the HTML5 songs library; selected tracks will load their MP3s on demand.")


if __name__ == "__main__":
    main()
