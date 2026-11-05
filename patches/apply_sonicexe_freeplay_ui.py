#!/usr/bin/env python3
"""Replace Psych Engine's default Freeplay row widgets with the original Sonic.EXE menu plates."""

from pathlib import Path
import re
import sys


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"Sonic.EXE Freeplay UI patch stopped: {label} expected once, found {count}")
    return source.replace(old, new)


def replace_pattern(source: str, pattern: str, replacement: str, label: str) -> str:
    source, count = re.subn(pattern, lambda _match: replacement, source, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"Sonic.EXE Freeplay UI patch stopped: {label} expected once, found {count}")
    return source


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: apply_sonicexe_freeplay_ui.py engine/source/states/FreeplayState.hx")

    path = Path(sys.argv[1])
    source = path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        "private var grpSongs:FlxTypedGroup<Alphabet>;",
        """private var grpSongs:FlxTypedGroup<FlxText>;
	private var songIdlePlates:FlxTypedGroup<FlxSprite>;
	private var songSelectedPlates:FlxTypedGroup<FlxSprite>;
	private var songSelectionShadows:FlxTypedGroup<FlxSprite>;""",
        "replace Psych Alphabet list with Sonic.EXE song rows",
    )
    source = replace_once(
        source,
        "\tprivate var iconArray:Array<HealthIcon> = [];",
        "",
        "remove Psych Engine health-icon row array",
    )

    # This replacement expects the lazy-icon version installed by the preceding
    # HTML5 menu-freeze patch, so no stock HealthIcon is constructed or rendered.
    source = replace_pattern(
        source,
        r"\t\tgrpSongs = new FlxTypedGroup<Alphabet>\(\);\n\t\tadd\(grpSongs\);\n\n\t\tfor \(i in 0\.\.\.songs\.length\)\n\t\t\{.*?\n\t\t\}\n\t\tWeekData\.setDirectoryFromWeek\(\);",
        """\t\t// Regular Freeplay excludes Encore/Bonus/Extra tracks. These remain
\t\t// available through the dedicated Extras mode, and Sound Test keeps them all.
\t\tif (!sonicExeCustomSongMode)
\t\t{
\t\t\tvar regularSonicSongs:Array<SongMetadata> = [];
\t\t\tfor (song in songs)
\t\t\t{
\t\t\t\tvar songTags:String = song.songName.toLowerCase();
\t\t\t\tif (song.week >= 0 && song.week < WeekData.weeksList.length)
\t\t\t\t{
\t\t\t\t\tvar weekId:String = WeekData.weeksList[song.week];
\t\t\t\t\tsongTags += " " + weekId.toLowerCase();
\t\t\t\t\tvar weekInfo:WeekData = WeekData.weeksLoaded.get(weekId);
\t\t\t\t\tif (weekInfo != null)
\t\t\t\t\t\tsongTags += " " + (weekInfo.weekName == null ? "" : weekInfo.weekName.toLowerCase()) + " " + (weekInfo.storyName == null ? "" : weekInfo.storyName.toLowerCase());
\t\t\t\t}
\t\t\t\tvar isEncoreOrBonus:Bool = songTags.indexOf("encore") >= 0 || songTags.indexOf("bonus") >= 0 || songTags.indexOf("extra") >= 0;
\t\t\t\tif (!isEncoreOrBonus) regularSonicSongs.push(song);
\t\t\t}
\t\t\tsongs = regularSonicSongs;
\t\t}
\t\tsongSelectionShadows = new FlxTypedGroup<FlxSprite>();
\t\tadd(songSelectionShadows);
\t\tsongIdlePlates = new FlxTypedGroup<FlxSprite>();
\t\tadd(songIdlePlates);
\t\tsongSelectedPlates = new FlxTypedGroup<FlxSprite>();
\t\tadd(songSelectedPlates);
\t\tgrpSongs = new FlxTypedGroup<FlxText>();
\t\tadd(grpSongs);

\t\tvar songPlateWidth:Int = Std.int(FlxG.width * 0.55);
\t\tvar songPlateHeight:Int = Std.int(songPlateWidth * (322.0 / 1673.0));
\t\tfor (i in 0...songs.length)
\t\t{
\t\t\tvar shadow:FlxSprite = new FlxSprite().loadGraphic(Paths.image('sonicexe-menu/options/shadow'));
\t\t\tshadow.setGraphicSize(Std.int(songPlateWidth * 0.952), Std.int(songPlateHeight * 0.896));
\t\t\tshadow.updateHitbox();
\t\t\tshadow.scrollFactor.set();
\t\t\tshadow.visible = false;
\t\t\tsongSelectionShadows.add(shadow);

\t\t\tvar idlePlate:FlxSprite = new FlxSprite().loadGraphic(Paths.image('sonicexe-menu/options/box-idle'));
\t\t\tidlePlate.setGraphicSize(songPlateWidth, songPlateHeight);
\t\t\tidlePlate.updateHitbox();
\t\t\tidlePlate.scrollFactor.set();
\t\t\tidlePlate.visible = false;
\t\t\tsongIdlePlates.add(idlePlate);

\t\t\tvar selectedPlate:FlxSprite = new FlxSprite().loadGraphic(Paths.image('sonicexe-menu/options/box'));
\t\t\tselectedPlate.setGraphicSize(songPlateWidth, songPlateHeight);
\t\t\tselectedPlate.updateHitbox();
\t\t\tselectedPlate.scrollFactor.set();
\t\t\tselectedPlate.visible = false;
\t\t\tsongSelectedPlates.add(selectedPlate);

\t\t\tvar songText:FlxText = new FlxText(0, 0, songPlateWidth - 120, songs[i].songName.toUpperCase(), 24);
\t\t\tsongText.setFormat(Paths.font("sonichud.ttf"), 24, FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\t\tsongText.scrollFactor.set();
\t\t\tsongText.antialiasing = false;
\t\t\tsongText.ID = i;
\t\t\tsongText.visible = false;
\t\t\tgrpSongs.add(songText);
\t\t}
\t\tWeekData.setDirectoryFromWeek();""",
        "replace Psych song text/icons with original Sonic.EXE plate, shadow and font layers",
    )

    # Replace stock icon alpha updates and Alphabet targetY updates.
    source = replace_pattern(
        source,
        r"\t\tfor \(i in 0\.\.\.iconArray\.length\)\n\t\t\{\n\t\t\tif \(iconArray\[i\] != null\) iconArray\[i\]\.alpha = 0\.6;\n\t\t\}\n\n\t\tif \(iconArray\[curSelected\] != null\) iconArray\[curSelected\]\.alpha = 1;\n",
        "",
        "remove Psych icon selection logic",
    )
    source = replace_pattern(
        source,
        r"\t\tfor \(item in grpSongs\.members\)\n\t\t\{\n\t\t\tbullShit\+\+;\n\t\t\titem\.alpha = 0\.6;\n\t\t\tif \(item\.targetY == curSelected\)\n\t\t\t\titem\.alpha = 1;\n\t\t\}\n",
        "",
        "remove Psych Alphabet row selection logic",
    )

    source = replace_pattern(
        source,
        r"\tpublic function updateTexts\(elapsed:Float = 0\.0\)\n\t\{.*?\n\t\}\n\n\toverride function destroy",
        """\tpublic function updateTexts(elapsed:Float = 0.0)
\t{
\t\tif (songs.length == 0)
\t\t\treturn;

\t\tlerpSelected = FlxMath.lerp(curSelected, lerpSelected, Math.exp(-elapsed * 9.6));
\t\tvar plateWidth:Float = FlxG.width * 0.55;
\t\tvar plateHeight:Float = plateWidth * (322.0 / 1673.0);
\t\tvar plateX:Float = (FlxG.width - plateWidth) * 0.5;
\t\tvar rowStep:Float = FlxG.height * 0.132;

\t\tfor (i in 0...songs.length)
\t\t{
\t\t\tvar offset:Float = i - lerpSelected;
\t\t\tvar rowVisible:Bool = Math.abs(offset) <= 2.25;
\t\t\tvar selected:Bool = (i == curSelected);
\t\t\tvar rowY:Float = (FlxG.height - plateHeight) * 0.5 + offset * rowStep;

\t\t\tvar shadow:FlxSprite = songSelectionShadows.members[i];
\t\t\tvar idlePlate:FlxSprite = songIdlePlates.members[i];
\t\t\tvar selectedPlate:FlxSprite = songSelectedPlates.members[i];
\t\t\tvar label:FlxText = grpSongs.members[i];

\t\t\tshadow.visible = rowVisible && selected;
\t\t\tidlePlate.visible = rowVisible && !selected;
\t\t\tselectedPlate.visible = rowVisible && selected;
\t\t\tlabel.visible = rowVisible;
\t\t\tlabel.active = rowVisible;

\t\t\tif (!rowVisible)
\t\t\t\tcontinue;

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
\t}

\toverride function destroy""",
        "replace Psych scrolling list with Sonic.EXE row layout",
    )

    source = replace_once(
        source,
        "\t\tif(curSelected >= songs.length) curSelected = 0;\n\t\tbg.color = songs[curSelected].color;\n\t\tintendedColor = bg.color;",
        "\t\tif(curSelected >= songs.length) curSelected = 0;\n\t\tbg.color = 0xFF1A0509;\n\t\tintendedColor = bg.color;",
        "replace stock song-color backdrop with dark Sonic.EXE background",
    )
    source = replace_once(
        source,
        "\tfunction changeSelection(change:Int = 0, playSound:Bool = true)\n\t{\n\t\tif (player.playingMusic)",
        "\tfunction changeSelection(change:Int = 0, playSound:Bool = true)\n\t{\n\t\tif (songs.length == 0 || player.playingMusic)",
        "guard empty selection and keep the player state valid",
    )
    source = replace_once(
        source,
        "\t\tvar newColor:Int = songs[curSelected].color;",
        "\t\tvar newColor:Int = 0xFF1A0509;",
        "keep the Sonic.EXE background color stable",
    )
    source = replace_once(
        source,
        "\tfunction changeDiff(change:Int = 0)\n\t{\n\t\tif (player.playingMusic)",
        "\tfunction changeDiff(change:Int = 0)\n\t{\n\t\tif (songs.length == 0 || player.playingMusic)",
        "guard difficulty changes when no songs are available",
    )
    source = replace_once(
        source,
        "\t\telse if(FlxG.keys.justPressed.SPACE)\n\t\t{",
        "\t\telse if(FlxG.keys.justPressed.SPACE && songs.length > 0)\n\t\t{",
        "guard preview input when no songs are available",
    )
    source = replace_once(
        source,
        "\t\telse if (controls.ACCEPT && !player.playingMusic)",
        "\t\telse if (controls.ACCEPT && !player.playingMusic && songs.length > 0)",
        "guard play input when no songs are available",
    )
    source = replace_once(
        source,
        "\t\telse if(controls.RESET && !player.playingMusic)",
        "\t\telse if(controls.RESET && !player.playingMusic && songs.length > 0)",
        "guard score reset input when no songs are available",
    )

    # Replace remaining Psych Engine font treatments in the song-info area.
    source = replace_once(
        source,
        'scoreText.setFormat(Paths.font("vcr.ttf"), 32, FlxColor.WHITE, RIGHT);',
        'scoreText.setFormat(Paths.font("sonichud.ttf"), 18, FlxColor.WHITE, RIGHT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);',
        "Sonic HUD score font",
    )
    source = replace_once(
        source,
        'diffText.font = scoreText.font;',
        'diffText.setFormat(Paths.font("sonichud.ttf"), 17, 0xFFFFC4CC, RIGHT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);',
        "Sonic HUD difficulty font",
    )
    source = replace_once(
        source,
        'missingText.setFormat(Paths.font("vcr.ttf"), 24, FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);',
        'missingText.setFormat(Paths.font("sonichud.ttf"), 22, FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);',
        "Sonic HUD chart error font",
    )
    source = replace_once(
        source,
        "\t\tplayer = new MusicPlayer(this);\n\t\tadd(player);",
        "\t\tplayer = new MusicPlayer(this);\n\t\tadd(player);\n\t\tplayer.visible = false;",
        "hide the stock Psych preview-player widget while retaining preview playback",
    )

    path.write_text(source, encoding="utf-8")
    print(f"Installed original Sonic.EXE Freeplay UI in {path}")


if __name__ == "__main__":
    main()
