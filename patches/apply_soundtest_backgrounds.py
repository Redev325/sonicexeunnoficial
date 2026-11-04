#!/usr/bin/env python3
"""Install original Sonic.EXE custom-song background and preview-video hooks."""

from pathlib import Path
import sys


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"Freeplay background patch stopped: expected 1 match for {label}, found {count}")
    return source.replace(old, new)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: apply_soundtest_backgrounds.py path/to/FreeplayState.hx")

    target = Path(sys.argv[1])
    if not target.is_file():
        raise SystemExit(f"FreeplayState source file not found: {target}")
    source = target.read_text(encoding="utf-8")

    source = replace_once(
        source,
        "class FreeplayState extends MusicBeatState\n{",
        "class FreeplayState extends MusicBeatState\n{\n\tpublic static var sonicExeCustomSongMode:Bool = false;",
        "add the custom-song screen flag",
    )

    source = replace_once(
        source,
        "\t\tbg = new FlxSprite().loadGraphic(Paths.image('menuDesat'));\n\t\tbg.antialiasing = ClientPrefs.data.antialiasing;\n\t\tadd(bg);\n\t\tbg.screenCenter();",
        "\t\tbg = new FlxSprite().loadGraphic(Paths.image(sonicExeCustomSongMode ? 'sonicexe-soundtest/bgtest' : 'menuDesat'));\n\t\tbg.antialiasing = ClientPrefs.data.antialiasing;\n\t\tif (sonicExeCustomSongMode)\n\t\t{\n\t\t\tbg.setGraphicSize(FlxG.width, FlxG.height);\n\t\t\tbg.updateHitbox();\n\t\t}\n\t\tadd(bg);\n\t\tbg.screenCenter();",
        "use the original Sound Test background texture",
    )

    source = replace_once(
        source,
        "\tfunction changeDiff(change:Int = 0)",
        """\tfunction soundTestVideoKey(songName:String):String
\t{
\t\tvar key:String = new EReg("[^a-z0-9]", "g").replace(songName.toLowerCase(), "");
\t\treturn switch (key)
\t\t{
\t\t\tcase "tooslowencore": "tooslowencore";
\t\t\tcase "tripletrouble": "tripletrouble";
\t\t\tcase "sanic", "sanicvid": "sanicvid";
\t\t\tcase "starvedarg1", "starvedarg1final": "starvedarg1final";
\t\t\tcase "predesign": "predesign";
\t\t\tcase "elpan": "elpan";
\t\t\tcase "mattpro": "mattpro";
\t\t\tcase "nebros": "nebros";
\t\t\tcase "darwinunofficial": "darwinunofficial";
\t\t\tcase "ttripl": "ttripl";
\t\t\tdefault: "";
\t\t};
\t}

\tfunction updateSonicEXESoundTestBackdrop():Void
\t{
\t\tif (!sonicExeCustomSongMode || songs.length == 0 || curSelected < 0 || curSelected >= songs.length)
\t\t\treturn;
\t\tvar videoKey:String = soundTestVideoKey(songs[curSelected].songName);
\t\t// Keep the Sound Test artwork fully opaque; don't blend preview video through the game canvas.
		bg.alpha = videoKey.length > 0 ? 0.18 : 1;
\t\t#if js
\t\tvar browserWindow:Dynamic = js.Browser.window;
\t\tvar callback:Dynamic = Reflect.field(browserWindow, "setSonicEXESoundTestVideo");
\t\tif (callback != null)
\t\t\tReflect.callMethod(browserWindow, callback, [songs[curSelected].songName]);
\t\t#end
\t}

\tfunction changeDiff(change:Int = 0)""",
        "add original song-preview video selection",
    )

    source = replace_once(
        source,
        "\t\tif (curSelected >= songs.length)\n\t\t\tcurSelected = 0;",
        "\t\tif (curSelected >= songs.length)\n\t\t\tcurSelected = 0;\n\t\tupdateSonicEXESoundTestBackdrop();",
        "refresh video when the selected song changes",
    )

    source = replace_once(
        source,
        "\toverride function destroy():Void\n\t{\n\t\tsuper.destroy();",
        """\toverride function destroy():Void
\t{
\t\t#if js
\t\tif (sonicExeCustomSongMode)
\t\t{
\t\t\tvar browserWindow:Dynamic = js.Browser.window;
\t\t\tvar callback:Dynamic = Reflect.field(browserWindow, "setSonicEXESoundTestVideo");
\t\t\tif (callback != null) Reflect.callMethod(browserWindow, callback, [""]);
\t\t}
\t\t#end
\t\tsonicExeCustomSongMode = false;
\t\tsuper.destroy();""",
        "stop preview video when leaving custom songs",
    )

    target.write_text(source, encoding="utf-8")
    print(f"Installed animated Sonic.EXE custom-song backgrounds in {target}")


if __name__ == "__main__":
    main()
