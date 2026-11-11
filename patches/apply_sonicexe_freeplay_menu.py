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

    source = replace_once(
        source,
        "\tvar bg:FlxSprite;\n\tvar intendedColor:Int;",
        """\tvar bg:FlxSprite;
\tvar intendedColor:Int;

\t// Original Sonic.EXE Freeplay carousel layers. The Extras and Sound Test
\t// lists keep the compact row UI installed by the existing patch.
\tvar freeplaySpikes:FlxSprite;\n\tvar freeplayTopSpikes:FlxSprite;
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

\t\t\t// Use the original bgsonic.webp with the original red Freeplay tint.
\t\t\tbg.loadGraphic(Paths.image('sonicexe-freeplay/bgsonic'));
\t\t\tbg.setGraphicSize(FlxG.width, FlxG.height);
\t\t\tbg.updateHitbox();
\t\t\tbg.screenCenter();
\t\t\tbg.scrollFactor.set();
\t\t\tbg.color = 0xFFFF0000;
\t\t\tbg.alpha = 1.0;

\t\t\t// The original image has its dark band at the top and teeth pointing down.
\t\t\t// Use it normally at the top edge, then flip a second copy for the bottom.
\t\t\tvar spikeHeight:Int = Std.int(FlxG.width * (157.0 / 2048.0));

\t\t\tfreeplayTopSpikes = new FlxSprite(0, 0);
\t\t\tfreeplayTopSpikes.loadGraphic(Paths.image('sonicexe-freeplay/spikesup'));
\t\t\tfreeplayTopSpikes.setGraphicSize(FlxG.width, spikeHeight);
\t\t\tfreeplayTopSpikes.updateHitbox();
\t\t\tfreeplayTopSpikes.flipY = false;
\t\t\tfreeplayTopSpikes.setPosition(0, 0);
\t\t\tfreeplayTopSpikes.scrollFactor.set();
\t\t\tfreeplayTopSpikes.antialiasing = false;
\t\t\tadd(freeplayTopSpikes);

\t\t\tfreeplaySpikes = new FlxSprite(0, FlxG.height - spikeHeight);
\t\t\tfreeplaySpikes.loadGraphic(Paths.image('sonicexe-freeplay/spikesup'));
\t\t\tfreeplaySpikes.setGraphicSize(FlxG.width, spikeHeight);
\t\t\tfreeplaySpikes.updateHitbox();
\t\t\tfreeplaySpikes.flipY = true;
\t\t\tfreeplaySpikes.setPosition(0, FlxG.height - freeplaySpikes.height);
\t\t\tfreeplaySpikes.scrollFactor.set();
\t\t\tfreeplaySpikes.antialiasing = false;
\t\t\tadd(freeplaySpikes);

\t\t\t// Original 1280x720 transparent card canvases, displayed at 60% scale
			// with a small preview of the next song to the right.
			var cardWidth:Float = FlxG.width * 0.60;
			var cardHeight:Float = FlxG.height * 0.60;
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

			freeplayNextCardArt = new FlxSprite(cardX + cardWidth + FlxG.width * 0.02, cardY);
			freeplayNextCardArt.loadGraphic(Paths.image('fpstuff/story'));
			freeplayNextCardArt.setGraphicSize(Std.int(cardWidth), Std.int(cardHeight));
			freeplayNextCardArt.updateHitbox();
			freeplayNextCardArt.antialiasing = false;
\t\t\tfreeplayNextCardArt.alpha = 0.78;
			freeplayNextCardArt.scrollFactor.set();
			add(freeplayNextCardArt);

			freeplayNextCardFrame = new FlxSprite(cardX + cardWidth + FlxG.width * 0.02, cardY);
			freeplayNextCardFrame.loadGraphic(Paths.image('FreeBox'));
			freeplayNextCardFrame.setGraphicSize(Std.int(cardWidth), Std.int(cardHeight));
			freeplayNextCardFrame.updateHitbox();
			freeplayNextCardFrame.antialiasing = false;
\t\t\tfreeplayNextCardFrame.alpha = 0.78;
			freeplayNextCardFrame.scrollFactor.set();
			add(freeplayNextCardFrame);

			freeplayTitle = new FlxText(FlxG.width * 0.20, FlxG.height * 0.82, FlxG.width * 0.60, '', 36);
\t\t\tfreeplayTitle.setFormat(Paths.font('sonichud.ttf'), 36, FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\t\tfreeplayTitle.scrollFactor.set();
\t\t\tadd(freeplayTitle);

\t\t\tfreeplayCategory = new FlxText(FlxG.width * 0.025, FlxG.height - 72, FlxG.width * 0.20, 'EXE', 34);
\t\t\tfreeplayCategory.setFormat(Paths.font('sonichud.ttf'), 34, 0xFFFF1717, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
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

    helper = """\tfunction sonicEXEArtForSong(songName:String, songCharacter:String):String
\t{
\t\tvar key:String = Paths.formatToSongPath(songName);
\t\tvar originalCoverNames:Array<String> = [
\t\t\t'b4cksl4sh', 'black-sun', 'chaos', 'chocolate-milk', 'cycles', 'deception', 'digitalized',
\t\t\t'endless-jp', 'endless-us', 'fakebaby', 'faker', 'fatality', 'fate', 'fight-or-flight',
\t\t\t'flash', 'forestall-desire', 'found-you', 'godspeed', 'gotta-go', 'haze', 'hedge', 'hellbent',
\t\t\t'her-world', 'hijacked-transmission', 'hollow', 'life-and-death', 'longstrider', 'malediction',
\t\t\t'mania', 'manual-blast', 'miasma', 'monochromatic', 'personel', 'placeholder', 'pre-design',
\t\t\t'prey', 'round-a-bout', 'sharpy-showdown', 'shocker', 'soulless', 'starline', 'substantial',
\t\t\t'sunshine', 'too-fest', 'uh-oh', 'universal-collapse', 'vanilla-milk'
\t\t];
\t\tif (originalCoverNames.indexOf(key) >= 0)
\t\t\treturn 'sonicexe-freeplay/covers/' + key;
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
			var cardWidth:Int = Std.int(FlxG.width * 0.60);
			var cardHeight:Int = Std.int(FlxG.height * 0.60);
			var cardX:Float = (FlxG.width - cardWidth) * 0.5;
			var cardY:Float = (FlxG.height - cardHeight) * 0.5;

			freeplayCardArt.loadGraphic(Paths.image(selectedArt.indexOf('sonicexe-freeplay/') == 0 ? selectedArt : 'fpstuff/' + selectedArt));
			freeplayCardArt.setGraphicSize(cardWidth, cardHeight);
			freeplayCardArt.updateHitbox();
			freeplayCardArt.setPosition(cardX, cardY);
			freeplayCardFrame.setGraphicSize(cardWidth, cardHeight);
			freeplayCardFrame.updateHitbox();
			freeplayCardFrame.setPosition(cardX, cardY);

			freeplayNextCardArt.loadGraphic(Paths.image(nextArt.indexOf('sonicexe-freeplay/') == 0 ? nextArt : 'fpstuff/' + nextArt));
			freeplayNextCardArt.setGraphicSize(cardWidth, cardHeight);
			freeplayNextCardArt.updateHitbox();
			freeplayNextCardArt.setPosition(cardX + cardWidth + FlxG.width * 0.02, cardY);
\t\t\tfreeplayNextCardArt.alpha = 0.78;
			freeplayNextCardFrame.setGraphicSize(cardWidth, cardHeight);
			freeplayNextCardFrame.updateHitbox();
			freeplayNextCardFrame.setPosition(cardX + cardWidth + FlxG.width * 0.02, cardY);
\t\t\tfreeplayNextCardFrame.alpha = 0.78;

			freeplayTitle.text = songs[selectedIndex].songName.toUpperCase();
			shownFreeplayIndex = selectedIndex;
\t\t}
\t}

\tfunction positionFreeplayScore():Void
\t{
\t\tif (scoreText != null)
\t\t{
\t\t\tscoreText.x = FlxG.width - 340;
\t\t\tscoreText.y = FlxG.height - 82;
\t\t\tscoreText.fieldWidth = 310;
\t\t\tscoreText.alignment = RIGHT;
\t\t}
\t\tif (diffText != null)
\t\t{
\t\t\tdiffText.x = FlxG.width - 340;
\t\t\tdiffText.y = FlxG.height - 48;
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
