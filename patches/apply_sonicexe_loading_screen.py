#!/usr/bin/env python3
"""Replace Psych Engine's default loading art with the original Sonic.EXE loading screen."""

from pathlib import Path
import re
import shutil
import sys


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"Sonic.EXE loading-screen patch stopped: {label} expected once, found {count}"
        )
    return source.replace(old, new)


def patch_loading_state(path: Path) -> None:
    source = path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        "\tvar loadBar:FlxSprite;",
        "\tvar loadBar:FlxSprite;\n\tvar loadBarBackground:FlxSprite;",
        "add a background track behind the progress bar",
    )

    pattern = re.compile(
        r"\t\tvar bg:FlxSprite = new FlxSprite\(0, 0\)\.makeGraphic\(FlxG\.width, FlxG\.height, 0xffcaff4d\);"
        r".*?\t\tadd\(loadBar\);",
        re.S,
    )
    replacement = """\t\t// Keep a black fallback behind the supplied full-screen artwork.
\t\tvar bg:FlxSprite = new FlxSprite(0, 0).makeGraphic(FlxG.width, FlxG.height, 0xFF000000);
\t\tbg.scrollFactor.set();
\t\tadd(bg);

\t\t// Original Sonic.EXE loading artwork replaces Psych Engine's "funkay" screen.
\t\tfunkay = new FlxSprite(0, 0).loadGraphic(Paths.getPath('images/Sonic.exeloadingscreen.png', IMAGE));
\t\tfunkay.setGraphicSize(FlxG.width, 0);
\t\tfunkay.updateHitbox();
\t\tfunkay.screenCenter();
\t\tfunkay.antialiasing = ClientPrefs.data.antialiasing;
\t\tfunkay.scrollFactor.set();
\t\tadd(funkay);

\t\t// The artwork's LOADING word is near the lower center. Keep the progress
\t\t// indicator short and centered in the empty area directly underneath it.
\t\tvar barWidth:Int = Std.int(FlxG.width * 0.24);
\t\tvar barHeight:Int = Std.int(Math.max(10, FlxG.height * 0.016));
\t\tvar barX:Int = Std.int((FlxG.width - barWidth) * 0.5);
\t\tvar barY:Int = Std.int(FlxG.height * 0.94);

\t\tloadBarBackground = new FlxSprite(barX, barY).makeGraphic(barWidth, barHeight, 0xFF280000);
\t\tloadBarBackground.scrollFactor.set();
\t\tadd(loadBarBackground);

\t\tloadBar = new FlxSprite(barX, barY).makeGraphic(barWidth, barHeight, 0xFFFF2020);
\t\tloadBar.origin.set(0, 0);
\t\tloadBar.scale.x = 0;
\t\tloadBar.scrollFactor.set();
\t\tadd(loadBar);"""
    source, count = pattern.subn(lambda _match: replacement, source, count=1)
    if count != 1:
        raise SystemExit(
            "Sonic.EXE loading-screen patch stopped: could not replace the default "
            "Psych Engine splash and full-width progress bar"
        )

    old_zoom = """\t\tfunkay.setGraphicSize(Std.int(0.88 * FlxG.width + 0.9 * (funkay.width - 0.88 * FlxG.width)));
\t\tfunkay.updateHitbox();
\t\tif(controls.ACCEPT)
\t\t{
\t\t\tfunkay.setGraphicSize(Std.int(funkay.width + 60));
\t\t\tfunkay.updateHitbox();
\t\t}
"""
    source = replace_once(
        source,
        old_zoom,
        "\t\t// Keep the Sonic.EXE loading artwork at a stable size while assets load.\n",
        "remove the stock splash zoom and accept-to-enlarge behavior",
    )

    if "images/Sonic.exeloadingscreen.png" not in source:
        raise SystemExit("Sonic.EXE loading-screen image reference was not installed.")
    if "0xFFFF2020" not in source or "FlxG.height * 0.94" not in source:
        raise SystemExit("Red loading bar placement was not installed.")
    if "Paths.getPath('images/funkay.png', IMAGE)" in source:
        raise SystemExit("Psych Engine's default loading image is still referenced.")

    path.write_text(source, encoding="utf-8")
    print("Installed Sonic.EXE loading art and a compact red progress bar under LOADING.")


def install_asset(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise SystemExit(f"Original Sonic.EXE loading artwork is missing: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if not destination.is_file() or destination.stat().st_size != source.stat().st_size:
        raise SystemExit("Sonic.EXE loading artwork was not copied correctly.")
    print(f"Installed loading artwork: {destination} ({destination.stat().st_size:,} bytes)")


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage: apply_sonicexe_loading_screen.py LoadingState.hx "
            "Sonic.exeloadingscreen.png engine/assets/shared/images/Sonic.exeloadingscreen.png"
        )
    patch_loading_state(Path(sys.argv[1]))
    install_asset(Path(sys.argv[2]), Path(sys.argv[3]))


if __name__ == "__main__":
    main()
