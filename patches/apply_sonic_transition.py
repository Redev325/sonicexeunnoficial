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

SWITCH_OLD = """\t\tif(FlxTransitionableState.skipNextTransIn) FlxG.switchState(nextState);
\t\telse startTransition(nextState);"""
SWITCH_NEW = """\t\t// Keep the Sonic close and reverse reveal adjacent; don't insert the
\t\t// engine's default fade between the two halves of the same transition.
\t\tif(sonicExeTransitionIn || FlxTransitionableState.skipNextTransIn)
\t\t\tFlxG.switchState(nextState);
\t\telse
\t\t\tstartTransition(nextState);"""

SONIC_SWITCH_TO_WITH_SONIC = """\t// Play the Sonic close on the current screen, then open the destination in reverse.
\tpublic static function switchStateWithSonicTransition(nextState:FlxState):Void
\t{
\t\tif (nextState == null) return;
\t\tvar currentState:FlxState = FlxG.state;
\t\tif (currentState == null)
\t\t{
\t\t\tFlxG.switchState(nextState);
\t\t\treturn;
\t\t}
\t\tcurrentState.openSubState(new SonicEXETransitionSubState(true, function():Void
\t\t{
\t\t\tsonicExeTransitionIn = true;
\t\t\tswitchState(nextState);
\t\t}));
\t}
"""

TRANSITION_CLASS = """

// Shared Sonic-head wipe. closeAfter=true plays the inward close on the current
// state; otherwise the frames run in reverse to reveal the destination state.
class SonicEXETransitionSubState extends FlxSubState
{
\tvar wipe:FlxSprite;
\tvar closeAfter:Bool = false;
\tvar finishCallback:Void->Void;
\tvar finished:Bool = false;

\tpublic function new(closeAfter:Bool = false, finishCallback:Void->Void = null)
\t{
\t\tsuper();
\t\tthis.closeAfter = closeAfter;
\t\tthis.finishCallback = finishCallback;
\t}

\toverride function create():Void
\t{
\t\tcameras = [FlxG.cameras.list[FlxG.cameras.list.length - 1]];
\t\tsuper.create();

\t\twipe = new FlxSprite();
\t\twipe.loadGraphic(Paths.image('sonicexe-transitions/head-wipe'), true, 640, 360);
\t\twipe.antialiasing = true;
\t\tvar frames:Array<Int> = [];
\t\tif (closeAfter)
\t\t{
\t\t\tfor (i in 0...36) frames.push(i);
\t\t}
\t\telse
\t\t{
\t\t\tfor (i in 0...36) frames.push(35 - i);
\t\t}
\t\twipe.animation.add(closeAfter ? 'close' : 'open', frames, 30, false);
\t\twipe.animation.play(closeAfter ? 'close' : 'open');
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
\t\tif (!finished && wipe != null && wipe.animation.finished)
\t\t{
\t\t\tfinished = true;
\t\t\tif (finishCallback != null)
\t\t\t\tfinishCallback();
\t\t\telse
\t\t\t\tclose();
\t\t}
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
    source = replace_once(source, SWITCH_OLD, SWITCH_NEW, "chain Sonic close directly to reverse reveal")
    source = replace_once(
        source,
        "\tpublic static function resetState() {",
        SONIC_SWITCH_TO_WITH_SONIC + "\tpublic static function resetState() {",
        "two-part Sonic transition switch helper",
    )
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
