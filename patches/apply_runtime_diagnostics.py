#!/usr/bin/env python3
"""Add HTML5 runtime checkpoints without changing any menu visuals or behavior."""

from pathlib import Path
import sys


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"Runtime diagnostics patch stopped: expected one {label} anchor, found {count}"
        )
    return source.replace(old, new)


def patch_music_beat(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "class MusicBeatState extends FlxUIState\n{\n",
        """class MusicBeatState extends FlxUIState
{
\t// JS bridge used only by the browser diagnostics overlay. It has no visual
\t// effect and compiles to a no-op outside the HTML5 target.
\tpublic static function sonicEXEDebug(message:String):Void
\t{
\t\t#if html5
\t\tjs.Syntax.code("if (window.sonicEXEDiagnostics) window.sonicEXEDiagnostics.mark({0});", message);
\t\t#end
\t}

\tpublic static function sonicEXEPulse():Void
\t{
\t\t#if html5
\t\tjs.Syntax.code("if (window.sonicEXEDiagnostics) window.sonicEXEDiagnostics.pulse();");
\t\t#end
\t}
""",
        "diagnostics bridge",
    )
    source = replace_once(
        source,
        "\toverride function create() {\n\t\tvar skip:",
        "\toverride function create() {\n\t\tvar debugStateName = Type.getClassName(Type.getClass(this));\n\t\tsonicEXEDebug(\"STATE CREATE START: \" + (debugStateName == null ? \"unknown\" : debugStateName));\n\t\tvar skip:",
        "state-create start",
    )
    source = replace_once(
        source,
        "\t\ttimePassedOnState = 0;",
        "\t\ttimePassedOnState = 0;\n\t\tsonicEXEDebug(\"STATE CREATE COMPLETE: \" + (debugStateName == null ? \"unknown\" : debugStateName));",
        "state-create completion",
    )
    source = replace_once(
        source,
        "\tpublic static function switchState(nextState:FlxState = null) {\n\t\tif(nextState == null) nextState = FlxG.state;",
        "\tpublic static function switchState(nextState:FlxState = null) {\n\t\tif(nextState == null) nextState = FlxG.state;\n\t\tvar debugTargetName = nextState == null ? \"unknown\" : Type.getClassName(Type.getClass(nextState));\n\t\tsonicEXEDebug(\"STATE SWITCH REQUESTED: \" + (debugTargetName == null ? \"unknown\" : debugTargetName));",
        "state-switch request",
    )
    source = replace_once(
        source,
        "\toverride function update(elapsed:Float)\n\t{\n\t\t//everyStep();",
        "\toverride function update(elapsed:Float)\n\t{\n\t\tsonicEXEPulse();\n\t\t//everyStep();",
        "game update pulse",
    )
    path.write_text(source, encoding="utf-8")


def patch_freeplay(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "\t\treturn (!leWeek.startUnlocked && leWeek.weekBefore.length > 0 && (!StoryMenuState.weekCompleted.exists(leWeek.weekBefore) || !StoryMenuState.weekCompleted.get(leWeek.weekBefore)));",
        "\t\tvar previousWeek:String = leWeek.weekBefore;\n\t\treturn (!leWeek.startUnlocked && previousWeek != null && previousWeek.length > 0 && (!StoryMenuState.weekCompleted.exists(previousWeek) || !StoryMenuState.weekCompleted.get(previousWeek)));",
        "Freeplay nullable week prerequisite",
    )
    source = replace_once(
        source,
        "\toverride function create()\n\t{\n\t\t//Paths.clearStoredMemory();",
        "\toverride function create()\n\t{\n\t\tMusicBeatState.sonicEXEDebug(\"FREEPLAY CREATE: start\");\n\t\t//Paths.clearStoredMemory();",
        "Freeplay create start",
    )
    source = replace_once(
        source,
        "\t\tWeekData.reloadWeekFiles(false);",
        "\t\tWeekData.reloadWeekFiles(false);\n\t\tMusicBeatState.sonicEXEDebug(\"FREEPLAY DATA: week files reloaded; weeks=\" + WeekData.weeksList.length);",
        "Freeplay week reload",
    )
    source = replace_once(
        source,
        "\t\tWeekData.setDirectoryFromWeek();\n\n\t\tscoreText =",
        "\t\tWeekData.setDirectoryFromWeek();\n\t\tMusicBeatState.sonicEXEDebug(\"FREEPLAY DATA: song metadata built; songs=\" + songs.length);\n\t\tif (songs.length == 0) MusicBeatState.sonicEXEDebug(\"ERROR: Freeplay has zero available songs\");\n\n\t\tscoreText =",
        "Freeplay song list checkpoint",
    )
    source = replace_once(
        source,
        "\t\tchangeSelection();\n\t\tupdateTexts();\n\t\tsuper.create();",
        "\t\tchangeSelection();\n\t\tupdateTexts();\n\t\tsuper.create();\n\t\tMusicBeatState.sonicEXEDebug(\"FREEPLAY CREATE: finished\");",
        "Freeplay create completion",
    )
    source = replace_once(
        source,
        "\t\t\ttry\n\t\t\t{\n\t\t\t\tPlayState.SONG = Song.loadFromJson(poop, songLowercase);",
        "\t\t\tMusicBeatState.sonicEXEDebug(\"FREEPLAY SONG: loading chart \" + poop + \" for \" + songLowercase);\n\t\t\ttry\n\t\t\t{\n\t\t\t\tPlayState.SONG = Song.loadFromJson(poop, songLowercase);\n\t\t\t\tMusicBeatState.sonicEXEDebug(\"FREEPLAY SONG: chart parsed successfully\");",
        "Freeplay chart load",
    )
    source = replace_once(
        source,
        "\t\t\tcatch(e:Dynamic)\n\t\t\t{\n\t\t\t\ttrace('ERROR! $e');",
        "\t\t\tcatch(e:Dynamic)\n\t\t\t{\n\t\t\t\tMusicBeatState.sonicEXEDebug(\"ERROR: Freeplay chart load failed: \" + Std.string(e));\n\t\t\t\ttrace('ERROR! $e');",
        "Freeplay chart error",
    )
    source = replace_once(
        source,
        "\t\t\tLoadingState.loadAndSwitchState(new PlayState());",
        "\t\t\tMusicBeatState.sonicEXEDebug(\"FREEPLAY SONG: requesting PlayState load\");\n\t\t\tLoadingState.loadAndSwitchState(new PlayState());",
        "Freeplay PlayState request",
    )
    path.write_text(source, encoding="utf-8")


def patch_story(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "\t\treturn (!leWeek.startUnlocked && leWeek.weekBefore.length > 0 && (!weekCompleted.exists(leWeek.weekBefore) || !weekCompleted.get(leWeek.weekBefore)));",
        "\t\tvar previousWeek:String = leWeek.weekBefore;\n\t\treturn (!leWeek.startUnlocked && previousWeek != null && previousWeek.length > 0 && (!weekCompleted.exists(previousWeek) || !weekCompleted.get(previousWeek)));",
        "Story nullable week prerequisite",
    )
    source = replace_once(
        source,
        "\toverride function create()\n\t{\n",
        "\toverride function create()\n\t{\n\t\tMusicBeatState.sonicEXEDebug(\"STORY CREATE: start\");\n",
        "Story create start",
    )
    source = replace_once(
        source,
        "\t\tWeekData.reloadWeekFiles(true);",
        "\t\tWeekData.reloadWeekFiles(true);\n\t\tMusicBeatState.sonicEXEDebug(\"STORY DATA: week files reloaded; weeks=\" + WeekData.weeksList.length);",
        "Story week reload",
    )
    source = replace_once(
        source,
        "\t\tsuper.create();\n\t}\n\n\toverride function closeSubState()",
        "\t\tsuper.create();\n\t\tMusicBeatState.sonicEXEDebug(\"STORY CREATE: finished; visible weeks=\" + loadedWeeks.length);\n\t}\n\n\toverride function closeSubState()",
        "Story create completion",
    )
    source = replace_once(
        source,
        "\tfunction selectWeek()\n\t{\n\t\tif (!weekIsLocked(loadedWeeks[curWeek].fileName))",
        "\tfunction selectWeek()\n\t{\n\t\tMusicBeatState.sonicEXEDebug(\"STORY SONG: select week index=\" + curWeek);\n\t\tif (!weekIsLocked(loadedWeeks[curWeek].fileName))",
        "Story week selection",
    )
    source = replace_once(
        source,
        "\t\t\t\tPlayState.SONG = Song.loadFromJson(PlayState.storyPlaylist[0].toLowerCase() + diffic, PlayState.storyPlaylist[0].toLowerCase());",
        "\t\t\t\tMusicBeatState.sonicEXEDebug(\"STORY SONG: loading chart \" + PlayState.storyPlaylist[0] + diffic);\n\t\t\t\tPlayState.SONG = Song.loadFromJson(PlayState.storyPlaylist[0].toLowerCase() + diffic, PlayState.storyPlaylist[0].toLowerCase());\n\t\t\t\tMusicBeatState.sonicEXEDebug(\"STORY SONG: chart parsed successfully\");",
        "Story chart load",
    )
    source = replace_once(
        source,
        "\t\t\tcatch(e:Dynamic)\n\t\t\t{\n\t\t\t\ttrace('ERROR! $e');",
        "\t\t\tcatch(e:Dynamic)\n\t\t\t{\n\t\t\t\tMusicBeatState.sonicEXEDebug(\"ERROR: Story chart load failed: \" + Std.string(e));\n\t\t\t\ttrace('ERROR! $e');",
        "Story chart error",
    )
    source = replace_once(
        source,
        "\t\t\tnew FlxTimer().start(1, function(tmr:FlxTimer)\n\t\t\t{\n\t\t\t\tLoadingState.loadAndSwitchState(new PlayState(), true);",
        "\t\t\tMusicBeatState.sonicEXEDebug(\"STORY SONG: requesting PlayState load after confirmation delay\");\n\t\t\tnew FlxTimer().start(1, function(tmr:FlxTimer)\n\t\t\t{\n\t\t\t\tLoadingState.loadAndSwitchState(new PlayState(), true);",
        "Story PlayState request",
    )
    path.write_text(source, encoding="utf-8")


def patch_loading(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "\toverride function create()\n\t{\n\t\tvar bg:FlxSprite",
        "\toverride function create()\n\t{\n\t\tMusicBeatState.sonicEXEDebug(\"LOADING STATE CREATE: start\");\n\t\tvar bg:FlxSprite",
        "LoadingState create start",
    )
    source = replace_once(
        source,
        "\t\tinitSongsManifest().onComplete\n\t\t(\n\t\t\tfunction (lib)\n\t\t\t{\n\t\t\t\tcallbacks = new MultiCallback(onLoad);",
        "\t\tMusicBeatState.sonicEXEDebug(\"LOADING STATE: requesting songs manifest\");\n\t\tinitSongsManifest().onComplete\n\t\t(\n\t\t\tfunction (lib)\n\t\t\t{\n\t\t\t\tMusicBeatState.sonicEXEDebug(\"LOADING STATE: songs manifest ready\");\n\t\t\t\tcallbacks = new MultiCallback(onLoad);",
        "songs manifest completion",
    )
    source = replace_once(
        source,
        "\tfunction onLoad()\n\t{\n\t\tif (stopMusic",
        "\tfunction onLoad()\n\t{\n\t\tMusicBeatState.sonicEXEDebug(\"LOADING STATE: all registered assets completed\");\n\t\tif (stopMusic",
        "LoadingState completion",
    )
    source = replace_once(
        source,
        "\tinline static public function loadAndSwitchState(target:FlxState, stopMusic = false)\n\t{\n\t\tMusicBeatState.switchState(getNextState(target, stopMusic));",
        "\tinline static public function loadAndSwitchState(target:FlxState, stopMusic = false)\n\t{\n\t\tvar debugTargetName = Type.getClassName(Type.getClass(target));\n\t\tMusicBeatState.sonicEXEDebug(\"LOADING STATE REQUESTED: \" + (debugTargetName == null ? \"unknown\" : debugTargetName));\n\t\tMusicBeatState.switchState(getNextState(target, stopMusic));",
        "LoadingState load request",
    )
    source = replace_once(
        source,
        "\tstatic function getNextState(target:FlxState, stopMusic = false):FlxState\n\t{\n\t\tvar directory:String = 'shared';",
        "\tstatic function getNextState(target:FlxState, stopMusic = false):FlxState\n\t{\n\t\tMusicBeatState.sonicEXEDebug(\"LOADING STATE: resolving next state and asset directory\");\n\t\tvar directory:String = 'shared';",
        "LoadingState target resolution",
    )
    path.write_text(source, encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit(
            "Usage: apply_runtime_diagnostics.py MusicBeatState.hx FreeplayState.hx StoryMenuState.hx LoadingState.hx"
        )
    patch_music_beat(Path(sys.argv[1]))
    patch_freeplay(Path(sys.argv[2]))
    patch_story(Path(sys.argv[3]))
    patch_loading(Path(sys.argv[4]))
    print("Installed HTML5 runtime checkpoints for state changes, Freeplay, Story Mode, and song loading.")


if __name__ == "__main__":
    main()
