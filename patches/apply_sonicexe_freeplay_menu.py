#!/usr/bin/env python3
"""Install the original Sonic.EXE Freeplay art carousel without changing Extras/Sound Test."""
from pathlib import Path
import sys


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"Original Freeplay patch stopped: {label} expected once, found {count}")
    return source.replace(old, new)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: apply_sonicexe_freeplay_menu.py engine/source/states/FreeplayState.hx")

    path = Path(sys.argv[1])
    source = path.read_text(encoding="utf-8")

    if "import flixel.addons.display.FlxBackdrop;" not in source:
        source = replace_once(
            source,
            "import flixel.math.FlxMath;\n",
            "import flixel.math.FlxMath;\nimport flixel.addons.display.FlxBackdrop;\nimport flixel.util.FlxAxes;\n",
            "import FlxBackdrop for the original scrolling overlay",
        )

    source = replace_once(
        source,
        "\tvar bg:FlxSprite;\n\tvar intendedColor:Int;",
        """\tvar bg:FlxSprite;
\tvar intendedColor:Int;

\t// Original Sonic.EXE Freeplay carousel layers. The Extras and Sound Test
\t// lists keep the compact row UI installed by the existing patch.
\tvar freeplayBackdrop:FlxBackdrop;
\tvar freeplayCardArt:FlxSprite;
\tvar freeplayCardFrame:FlxSprite;\n\tvar freeplayNextCardArt:FlxSprite;\n\tvar freeplayNextCardFrame:FlxSprite;
\tvar freeplayTitle:FlxText;
\tvar freeplayCategory:FlxText;
\tvar freeplayScreenOverlay:FlxSprite;
\tvar freeplayTracksLabel:FlxSprite;
\tvar shownFreeplayIndex:Int = -1;
""",
        "add original Freeplay card state",
    )

    source = replace_once(
        source,
        "\t\tchangeSelection();\n\t\tupdateTexts();\n\t\tsuper.create();",
        """\t\tchangeSelection();
\t\tupdateTexts();

\t\t// Only the regular Freeplay screen uses the original picture-card carousel.
\t\t// Extras and Sound Test retain their separate existing list behavior.
\t\tif (!sonicExeCustomSongMode && !sonicExeEncoreMode)
\t\t{
\t\t\tgrpSongs.visible = false;
\t\t\tsongIdlePlates.visible = false;
\t\t\tsongSelectedPlates.visible = false;
\t\t\tsongSelectionShadows.visible = false;
\t\t\tif (scoreBG != null) scoreBG.visible = false;
\t\t\tif (bottomBG != null) bottomBG.visible = false;
\t\t\tif (bottomText != null) bottomText.visible = false;

\t\t\tbg.loadGraphic(Paths.image('backgroundlool'));
\t\t\tbg.setGraphicSize(FlxG.width, FlxG.height);
\t\t\tbg.updateHitbox();
\t\t\tbg.screenCenter();
\t\t\tbg.scrollFactor.set();

\t\t\tfreeplayBackdrop = new FlxBackdrop(Paths.image('sidebar'), FlxAxes.Y);
\t\t\tfreeplayBackdrop.scrollFactor.set();
\t\t\tfreeplayBackdrop.y = 0;
\t\t\tinsert(1, freeplayBackdrop);

\t\t\t// Original 1280x720 transparent card canvases, displayed at the
			// source game's ~64% scale and half-screen carousel spacing.
			var cardWidth:Float = FlxG.width * 0.64;
			var cardHeight:Float = FlxG.height * 0.64;
			var cardX:Float = (FlxG.width - cardWidth) * 0.5;
			var cardY:Float = (FlxG.height - cardHeight) * 0.5;

			freeplayCardArt = new FlxSprite(cardX, cardY);
			freeplayCardArt.loadGraphic(Paths.image('fpstuff/story'));
			freeplayCardArt.setGraphicSize(Std.int(cardWidth), Std.int(cardHeight));
			freeplayCardArt.updateHitbox();
			freeplayCardArt.antialiasing = false;
			freeplayCardArt.scrollFactor.set();
			add(freeplayCardArt);

			freeplayCardFrame = new FlxSprite(cardX, cardY);
			freeplayCardFrame.loadGraphic(Paths.image('FreeBox'));
			freeplayCardFrame.setGraphicSize(Std.int(cardWidth), Std.int(cardHeight));
			freeplayCardFrame.updateHitbox();
			freeplayCardFrame.antialiasing = false;
			freeplayCardFrame.scrollFactor.set();
			add(freeplayCardFrame);

			freeplayNextCardArt = new FlxSprite(cardX + FlxG.width * 0.5, cardY);
			freeplayNextCardArt.loadGraphic(Paths.image('fpstuff/story'));
			freeplayNextCardArt.setGraphicSize(Std.int(cardWidth), Std.int(cardHeight));
			freeplayNextCardArt.updateHitbox();
			freeplayNextCardArt.antialiasing = false;
			freeplayNextCardArt.scrollFactor.set();
			add(freeplayNextCardArt);

			freeplayNextCardFrame = new FlxSprite(cardX + FlxG.width * 0.5, cardY);
			freeplayNextCardFrame.loadGraphic(Paths.image('FreeBox'));
			freeplayNextCardFrame.setGraphicSize(Std.int(cardWidth), Std.int(cardHeight));
			freeplayNextCardFrame.updateHitbox();
			freeplayNextCardFrame.antialiasing = false;
			freeplayNextCardFrame.scrollFactor.set();
			add(freeplayNextCardFrame);

			freeplayTitle = new FlxText(240, FlxG.height - 104, 800, '', 38);
\t\t\tfreeplayTitle.setFormat(Paths.font('sonichud.ttf'), 38, FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\t\tfreeplayTitle.scrollFactor.set();
\t\t\tadd(freeplayTitle);

\t\t\tfreeplayCategory = new FlxText(28, FlxG.height - 96, 210, 'EXE', 36);
\t\t\tfreeplayCategory.setFormat(Paths.font('sonichud.ttf'), 36, 0xFFFF1717, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\t\tfreeplayCategory.scrollFactor.set();
\t\t\tadd(freeplayCategory);

\t\t\tif (scoreText != null)
\t\t\t{
\t\t\t\tscoreText.setFormat(Paths.font('sonichud.ttf'), 22, FlxColor.WHITE, RIGHT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\t\t\tscoreText.scrollFactor.set();
\t\t\t}
\t\t\tif (diffText != null)
\t\t\t{
\t\t\t\tdiffText.setFormat(Paths.font('sonichud.ttf'), 18, 0xFFFFC4CC, RIGHT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\t\t\tdiffText.scrollFactor.set();
\t\t\t}
\t\t\tupdateFreeplayCards();
\t\t}
\t\tsuper.create();""",
        "install original Freeplay card carousel after the base menu is initialized",
    )

    # Keep the existing song/week/difficulty/high-score behavior, but let the
    # original art carousel follow the selected song.
    source = replace_once(
        source,
        "\tpublic function updateTexts(elapsed:Float = 0.0)\n\t{\n\t\tif (songs.length == 0)\n\t\t\treturn;",
        "\tpublic function updateTexts(elapsed:Float = 0.0)\n\t{\n\t\tif (songs.length == 0)\n\t\t\treturn;",
        "preserve existing song row update routine",
    )
    source = replace_once(
        source,
        "\t\t\tlabel.color = selected ? FlxColor.WHITE : 0xFFFFC4CC;\n\t\t}\n\t}\n\n\toverride function destroy",
        "\t\t\tlabel.color = selected ? FlxColor.WHITE : 0xFFFFC4CC;\n\t\t}\n\t\tupdateFreeplayCards();\n\t\tif (!sonicExeCustomSongMode && !sonicExeEncoreMode)\n\t\t\tpositionFreeplayScore();\n\t}\n\n\toverride function destroy",
        "refresh original song art and lower score display",
    )

    source = replace_once(
        source,
        "\toverride function update(elapsed:Float)\n\t{",
        "\toverride function update(elapsed:Float)\n\t{\n\t\tif (freeplayBackdrop != null && !sonicExeCustomSongMode && !sonicExeEncoreMode) freeplayBackdrop.y += elapsed * 36;",
        "animate the original vertical Freeplay background layer",
    )

    helper = """\tfunction sonicEXEArtForSong(songName:String, songCharacter:String):String
\t{
\t\tvar key:String = Paths.formatToSongPath(songName);
\t\treturn switch (key)
\t\t{
\t\t\tcase 'cycles': 'lord x';
\t\t\tcase 'endless', 'endless-og': 'majin';
\t\t\tcase 'sunshine', 'soulless': 'tails doll';
\t\t\tcase 'chaos', 'black-sun': 'fleetway';
\t\t\tcase 'fatality': 'fatalerror';
\t\t\tcase 'prey', 'fight-or-flight': 'starved';
\t\t\tcase 'round-a-bout': 'needlemouse';
\t\t\tcase 'milk': 'sunky';
\t\t\tcase 'too-fest': 'sanic';
\t\t\tcase 'personel': 'coldsteel';
\t\t\tcase 'too-slow-encore': 'too-slow-encore';
\t\t\tcase 'you-cant-run-encore': 'you-cant-run-encore';
\t\t\tcase 'triple-trouble-encore': 'triple-trouble-encore';
\t\t\tcase 'faker': 'faker';
\t\t\tdefault:
\t\t\t\tvar charKey:String = (songCharacter == null ? '' : songCharacter.toLowerCase());
\t\t\t\tif (charKey == 'lordx') charKey = 'lord x';
\t\t\t\tif (charKey == 'tailsdoll') charKey = 'tails doll';
\t\t\t\tif (charKey.length == 0) 'story' else charKey;
\t\t};
\t}

\tfunction updateFreeplayCards():Void
\t{
\t\tif (sonicExeCustomSongMode || sonicExeEncoreMode || songs.length == 0 || freeplayCardArt == null)
\t\t\treturn;

\t\tvar selectedIndex:Int = curSelected;
\t\tif (selectedIndex < 0 || selectedIndex >= songs.length)
\t\t\tselectedIndex = 0;

\t\tif (shownFreeplayIndex != selectedIndex)
\t\t{
\t\t\tvar nextIndex:Int = (selectedIndex + 1) % songs.length;
			var selectedArt:String = sonicEXEArtForSong(songs[selectedIndex].songName, songs[selectedIndex].songCharacter);
			var nextArt:String = sonicEXEArtForSong(songs[nextIndex].songName, songs[nextIndex].songCharacter);
			var cardWidth:Int = Std.int(FlxG.width * 0.64);
			var cardHeight:Int = Std.int(FlxG.height * 0.64);
			var cardX:Float = (FlxG.width - cardWidth) * 0.5;
			var cardY:Float = (FlxG.height - cardHeight) * 0.5;

			freeplayCardArt.loadGraphic(Paths.image('fpstuff/' + selectedArt));
			freeplayCardArt.setGraphicSize(cardWidth, cardHeight);
			freeplayCardArt.updateHitbox();
			freeplayCardArt.setPosition(cardX, cardY);
			freeplayCardFrame.setGraphicSize(cardWidth, cardHeight);
			freeplayCardFrame.updateHitbox();
			freeplayCardFrame.setPosition(cardX, cardY);

			freeplayNextCardArt.loadGraphic(Paths.image('fpstuff/' + nextArt));
			freeplayNextCardArt.setGraphicSize(cardWidth, cardHeight);
			freeplayNextCardArt.updateHitbox();
			freeplayNextCardArt.setPosition(cardX + FlxG.width * 0.5, cardY);
			freeplayNextCardFrame.setGraphicSize(cardWidth, cardHeight);
			freeplayNextCardFrame.updateHitbox();
			freeplayNextCardFrame.setPosition(cardX + FlxG.width * 0.5, cardY);

			freeplayTitle.text = songs[selectedIndex].songName.toUpperCase();
			shownFreeplayIndex = selectedIndex;
\t\t}
\t}

\tfunction positionFreeplayScore():Void
\t{
\t\tif (scoreText != null)
\t\t{
\t\t\tscoreText.x = FlxG.width - 340;
\t\t\tscoreText.y = FlxG.height - 96;
\t\t\tscoreText.fieldWidth = 310;
\t\t\tscoreText.alignment = RIGHT;
\t\t}
\t\tif (diffText != null)
\t\t{
\t\t\tdiffText.x = FlxG.width - 340;
\t\t\tdiffText.y = FlxG.height - 60;
\t\t\tdiffText.fieldWidth = 310;
\t\t\tdiffText.alignment = RIGHT;
\t\t}
\t}
\n\n"""
    source = replace_once(
        source,
        "\toverride function destroy():Void",
        helper + "\toverride function destroy():Void",
        "add original Freeplay song-art mapping and display helpers",
    )

    path.write_text(source, encoding="utf-8")
    print(f"Installed original Sonic.EXE Freeplay card carousel in {path}")


if __name__ == "__main__":
    main()
