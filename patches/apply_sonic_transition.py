#!/usr/bin/env python3
"""Add the reverse Sonic-head reveal to the destination after a menu wipe."""

from pathlib import Path
import re
import sys


MUSIC_BEAT_IMPORTS = """import flixel.FlxState;
import backend.PsychCamera;"""
NEW_IMPORTS = """import flixel.FlxState;
import flixel.FlxG;
import flixel.FlxSprite;
import flixel.FlxSubState;
import backend.PsychCamera;"""

CREATE_OLD = """\t\tif(!skip) {
\t\t\topenSubState(new CustomFadeTransition(0.6, true));
\t\t}"""
CREATE_NEW = """\t\tif (sonicExeTransitionIn) {
\t\t\t// The source menu has already played the inward wipe. Reveal the new
\t\t\t// state by playing the very same alpha-mask frames in reverse.
\t\t\tsonicExeTransitionIn = false;
\t\t\topenSubState(new SonicEXETransitionSubState());
\t\t} else if(!skip) {
\t\t\topenSubState(new CustomFadeTransition(0.6, true));
\t\t}"""

TRANSITION_CLASS = """

// Transparent Sonic-head aperture used as the transition-in after the main-menu
// close animation. Frames 19 -> 0 expand the aperture back across the screen.
class SonicEXETransitionSubState extends FlxSubState
{
\tvar wipe:FlxSprite;

\toverride function create():Void
\t{
\t\tcameras = [FlxG.cameras.list[FlxG.cameras.list.length - 1]];
\t\tsuper.create();

\t\twipe = new FlxSprite();
\t\twipe.loadGraphic(Paths.image('sonicexe-transitions/head-wipe'), true, 640, 360);
\t\twipe.animation.add('open', [
\t\t\t19, 18, 17, 16, 15, 14, 13, 12, 11, 10,
\t\t\t9, 8, 7, 6, 5, 4, 3, 2, 1, 0
\t\t], 24, false);
\t\twipe.animation.play('open');
\t\twipe.setGraphicSize(FlxG.width, FlxG.height);
\t\twipe.updateHitbox();
\t\twipe.setPosition(0, 0);
\t\twipe.scrollFactor.set(0, 0);
\t\twipe.cameras = cameras;
\t\tadd(wipe);
\t}

\toverride function update(elapsed:Float):Void
\t{
\t\tsuper.update(elapsed);
\t\tif (wipe != null && wipe.animation.finished)
\t\t\tclose();
\t}
}
"""


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"Sonic transition patch stopped: expected one match for {label}, found {count}")
    return source.replace(old, new)


def patch_music_beat(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    source = replace_once(source, MUSIC_BEAT_IMPORTS, NEW_IMPORTS, "MusicBeatState imports")
    source = replace_once(
        source,
        "class MusicBeatState extends FlxUIState\n{",
        "class MusicBeatState extends FlxUIState\n{\n\tpublic static var sonicExeTransitionIn:Bool = false;",
        "incoming transition flag",
    )
    source = replace_once(source, CREATE_OLD, CREATE_NEW, "default transition-in hook")
    if "class SonicEXETransitionSubState extends FlxSubState" in source:
        raise SystemExit("Sonic transition patch stopped: transition substate is already installed.")
    source += TRANSITION_CLASS
    path.write_text(source, encoding="utf-8")
    print(f"Installed reverse Sonic-head reveal in {path}")


def patch_main_menu(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    pattern = re.compile(r"(?m)^(\s*)switch \(optionShit\[curSelected\]\)\s*$")
    # Match the menu's destination switch (called after the inward wipe has played).
    patched, count = pattern.subn(
        lambda match: match.group(1) + "MusicBeatState.sonicExeTransitionIn = true;\n" + match.group(0),
        source,
        count=1,
    )
    if count != 1:
        raise SystemExit(f"Sonic transition patch stopped: expected one menu destination switch, found {count}")
    path.write_text(patched, encoding="utf-8")
    print(f"Armed reverse Sonic-head reveal for menu destinations in {path}")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: apply_sonic_transition.py path/to/MusicBeatState.hx path/to/MainMenuState.hx")
    patch_music_beat(Path(sys.argv[1]))
    patch_main_menu(Path(sys.argv[2]))


if __name__ == "__main__":
    main()
