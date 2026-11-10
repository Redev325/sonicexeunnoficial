#!/usr/bin/env python3
"""Virtualize the Sonic.EXE Freeplay catalogue so rendering cost stays constant."""

from pathlib import Path
import re
import sys


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"Freeplay virtualization stopped: {label} expected once, found {count}")
    return source.replace(old, new)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: apply_freeplay_virtualization.py engine/source/states/FreeplayState.hx")

    path = Path(sys.argv[1])
    source = path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        "\tprivate var songSelectionShadows:FlxTypedGroup<FlxSprite>;",
        "\tprivate var songSelectionShadows:FlxTypedGroup<FlxSprite>;\n"
        "\tprivate static inline var MAX_VISIBLE_SONG_ROWS:Int = 7;",
        "fixed visible-row limit",
    )
    source = replace_once(
        source,
        "\t\tvar songPlateHeight:Int = Std.int(songPlateWidth * (322.0 / 1673.0));\n"
        "\t\tfor (i in 0...songs.length)",
        "\t\tvar songPlateHeight:Int = Std.int(songPlateWidth * (322.0 / 1673.0));\n"
        "\t\t// Allocate only the rows that can actually appear on screen.\n"
        "\t\tfor (i in 0...MAX_VISIBLE_SONG_ROWS)",
        "create a bounded number of song rows",
    )
    source = replace_once(
        source,
        "var songText:FlxText = new FlxText(0, 0, songPlateWidth - 120, songs[i].songName.toUpperCase(), songTextSize);",
        "var songText:FlxText = new FlxText(0, 0, songPlateWidth - 120, '', songTextSize);",
        "avoid allocating text layout for every song",
    )
    source = replace_once(
        source,
        "\t\t\tsongText.ID = i;",
        "\t\t\tsongText.ID = -1;",
        "initialize reusable row labels",
    )

    pattern = re.compile(
        r"\tpublic function updateTexts\(elapsed:Float = 0\.0\)\n"
        r"\t\{.*?\n"
        r"\t\}\n\n"
        r"\toverride function destroy",
        re.S,
    )
    replacement = """\tpublic function updateTexts(elapsed:Float = 0.0)
\t{
\t\tif (songs.length == 0)
\t\t\treturn;

\t\tlerpSelected = FlxMath.lerp(curSelected, lerpSelected, Math.exp(-elapsed * 9.6));
\t\tvar plateWidth:Float = FlxG.width * (sonicExeEncoreMode ? 0.40 : 0.55);
\t\tvar plateHeight:Float = plateWidth * (322.0 / 1673.0);
\t\tvar plateX:Float = (FlxG.width - plateWidth) * 0.5;
\t\tvar rowStep:Float = FlxG.height * (sonicExeEncoreMode ? 0.14 : 0.132);
\t\tvar radius:Int = Std.int(MAX_VISIBLE_SONG_ROWS * 0.5);
\t\tvar centerIndex:Int = Math.round(lerpSelected);

\t\t// Reuse seven row objects. Per-frame work is independent of catalogue size.
\t\tfor (slot in 0...MAX_VISIBLE_SONG_ROWS)
\t\t{
\t\t\tvar songIndex:Int = centerIndex + slot - radius;
\t\t\tvar rowVisible:Bool = songIndex >= 0 && songIndex < songs.length;
\t\t\tvar selected:Bool = songIndex == curSelected;
\t\t\tvar offset:Float = songIndex - lerpSelected;
\t\t\tvar rowY:Float = (FlxG.height - plateHeight) * 0.5 + offset * rowStep;

\t\t\tvar shadow:FlxSprite = songSelectionShadows.members[slot];
\t\t\tvar idlePlate:FlxSprite = songIdlePlates.members[slot];
\t\t\tvar selectedPlate:FlxSprite = songSelectedPlates.members[slot];
\t\t\tvar label:FlxText = grpSongs.members[slot];

\t\t\tshadow.visible = rowVisible && selected;
\t\t\tidlePlate.visible = rowVisible && !selected;
\t\t\tselectedPlate.visible = rowVisible && selected;
\t\t\tlabel.visible = rowVisible;
\t\t\tlabel.active = rowVisible;
\t\t\tif (!rowVisible)
\t\t\t\tcontinue;

\t\t\t// Relabel a recycled row only when it represents another song.
\t\t\tif (label.ID != songIndex)
\t\t\t{
\t\t\t\tlabel.text = songs[songIndex].songName.toUpperCase();
\t\t\t\tlabel.ID = songIndex;
\t\t\t}

\t\t\tshadow.x = plateX + plateWidth * 0.083;
\t\t\tshadow.y = rowY + plateHeight * 0.22;
\t\t\tidlePlate.x = plateX;
\t\t\tidlePlate.y = rowY;
\t\t\tselectedPlate.x = plateX;
\t\t\tselectedPlate.y = rowY;
\t\t\tlabel.x = plateX + 60;
\t\t\tlabel.y = rowY + (plateHeight - label.height) * 0.5 - 1;
\t\t\tlabel.alpha = selected ? 1 : 0.72;
\t\t\tlabel.color = selected ? FlxColor.WHITE : 0xFFFFC4CC;
\t\t}

\t\tupdateFreeplayCards();
\t\tif (!sonicExeCustomSongMode && !sonicExeEncoreMode)
\t\t\tpositionFreeplayScore();
\t}

\toverride function destroy"""
    source, count = pattern.subn(lambda _match: replacement, source, count=1)
    if count != 1:
        raise SystemExit(f"Freeplay virtualization stopped: expected one updateTexts(), found {count}")

    path.write_text(source, encoding="utf-8")
    print("Virtualized Freeplay rows: seven reusable rows instead of one set per song.")


if __name__ == "__main__":
    main()
