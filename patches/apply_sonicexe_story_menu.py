#!/usr/bin/env python3
"""Use original Sonic.EXE Story Mode art while retaining the playable Story week."""

from pathlib import Path
import sys


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"Sonic.EXE Story Mode patch stopped: {label} expected once, found {count}")
    return source.replace(old, new)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: apply_sonicexe_story_menu.py engine/source/states/StoryMenuState.hx")

    path = Path(sys.argv[1])
    source = path.read_text(encoding="utf-8")

    replacement = """\t\tchangeWeek();
\t\tchangeDifficulty();

\t\t// Hide the default Psych Engine Story selector and show the original EXE data-select.
\t\tbgYellow.visible = false;
\t\tbgSprite.visible = false;
\t\tblackBarThingie.visible = false;
\t\tgrpWeekText.visible = false;
\t\tgrpWeekCharacters.visible = false;
\t\tgrpLocks.visible = false;
\t\tdifficultySelectors.visible = false;
\t\ttracksSprite.visible = false;
\t\ttxtTracklist.visible = false;
\t\tscoreText.visible = false;
\t\ttxtWeekTitle.visible = false;

\t\tvar sonicStoryBackground:FlxSprite = new FlxSprite(0, 0);
\t\tsonicStoryBackground.frames = Paths.getSparrowAtlas('sonicexe-story/SMMStatic');
\t\tsonicStoryBackground.animation.addByPrefix('staticLoop', 'static', 24, true);
\t\tsonicStoryBackground.animation.play('staticLoop');
\t\tsonicStoryBackground.setGraphicSize(FlxG.width, FlxG.height);
\t\tsonicStoryBackground.updateHitbox();
\t\tsonicStoryBackground.scrollFactor.set();
\t\tinsert(0, sonicStoryBackground);

\t\tvar sonicStoryNoise:FlxSprite = new FlxSprite(0, 0);
\t\tsonicStoryNoise.frames = Paths.getSparrowAtlas('sonicexe-story/screenstatic');
\t\tsonicStoryNoise.animation.addByPrefix('staticLoop', 'screenSTATIC', 24, true);
\t\tsonicStoryNoise.animation.play('staticLoop');
\t\tsonicStoryNoise.setGraphicSize(FlxG.width, FlxG.height);
\t\tsonicStoryNoise.updateHitbox();
\t\tsonicStoryNoise.scrollFactor.set();
\t\tsonicStoryNoise.alpha = 0.12;
\t\tadd(sonicStoryNoise);

\t\tvar sonicStoryBanner:FlxSprite = new FlxSprite(0, 8);
\t\tsonicStoryBanner.frames = Paths.getSparrowAtlas('sonicexe-story/dataselect');
\t\tsonicStoryBanner.animation.addByPrefix('idle', 'dataselect dataselect', 6, true);
\t\tsonicStoryBanner.animation.play('idle');
\t\tsonicStoryBanner.setGraphicSize(Std.int(FlxG.width * 0.76));
\t\tsonicStoryBanner.updateHitbox();
\t\tsonicStoryBanner.screenCenter(X);
\t\tsonicStoryBanner.scrollFactor.set();
\t\tadd(sonicStoryBanner);

\t\tvar sonicStoryTitle:FlxText = new FlxText(0, 26, FlxG.width, 'SONIC.EXE STORY MODE', 28);
\t\tsonicStoryTitle.setFormat(Paths.font('sonichud.ttf'), 28, FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tsonicStoryTitle.scrollFactor.set();
\t\tadd(sonicStoryTitle);

\t\t// Four original chapter covers, each shown inside a source-game grey/yellow frame.
\t\tvar storyCoverNames:Array<String> = ['too-slow', 'you-cant-run', 'triple-trouble', 'final-escape'];
\t\tvar storyCoverTitles:Array<String> = ['TOO SLOW', "YOU CAN'T RUN", 'TRIPLE TROUBLE', 'FINAL ESCAPE'];
\t\tvar storyCoverWidth:Int = Std.int(FlxG.width * 0.17);
\t\tvar storyCoverY:Float = FlxG.height * 0.38;
\t\tvar storyGap:Float = FlxG.width * 0.035;
\t\tvar storyTotalWidth:Float = storyCoverWidth * 4 + storyGap * 3;
\t\tvar storyStartX:Float = (FlxG.width - storyTotalWidth) * 0.5;
\t\tfor (i in 0...storyCoverNames.length)
\t\t{
\t\t\tvar coverX:Float = storyStartX + i * (storyCoverWidth + storyGap);
\t\t\tvar coverFrame:FlxSprite = new FlxSprite(coverX - 9, storyCoverY - 9);
\t\t\tcoverFrame.loadGraphic(Paths.image(i == 0 ? 'sonicexe-story/yellowbox' : 'sonicexe-story/greybox'));
\t\t\tcoverFrame.setGraphicSize(storyCoverWidth + 18, Std.int(storyCoverWidth * 0.82));
\t\t\tcoverFrame.updateHitbox();
\t\t\tcoverFrame.scrollFactor.set();
\t\t\tadd(coverFrame);

\t\t\tvar cover:FlxSprite = new FlxSprite(coverX, storyCoverY);
\t\t\tcover.loadGraphic(Paths.image('sonicexe-story/covers/' + storyCoverNames[i]));
\t\t\tcover.setGraphicSize(storyCoverWidth);
\t\t\tcover.updateHitbox();
\t\t\tcover.scrollFactor.set();
\t\t\tadd(cover);

\t\t\tvar coverTitle:FlxText = new FlxText(coverX - 8, storyCoverY + cover.height + 10, storyCoverWidth + 16, storyCoverTitles[i], 17);
\t\t\tcoverTitle.setFormat(Paths.font('sonichud.ttf'), 17, FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\t\tcoverTitle.scrollFactor.set();
\t\t\tadd(coverTitle);
\t\t}

\t\tvar storySelectionFrame:FlxSprite = new FlxSprite(storyStartX - 12, storyCoverY - 12);
\t\tstorySelectionFrame.frames = Paths.getSparrowAtlas('sonicexe-story/cuadro');
\t\tstorySelectionFrame.animation.addByPrefix('idle', 'cuandrado', 1, true);
\t\tstorySelectionFrame.animation.play('idle');
\t\tstorySelectionFrame.setGraphicSize(storyCoverWidth + 24);
\t\tstorySelectionFrame.updateHitbox();
\t\tstorySelectionFrame.scrollFactor.set();
\t\tadd(storySelectionFrame);

\t\tvar storyControls:FlxText = new FlxText(0, FlxG.height - 36, FlxG.width, 'ENTER: START STORY     LEFT / RIGHT: DIFFICULTY     ESC: BACK', 16);
\t\tstoryControls.setFormat(Paths.font('sonichud.ttf'), 16, 0xFFFFC4CC, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tstoryControls.scrollFactor.set();
\t\tadd(storyControls);

\t\tsuper.create();"""

    source = replace_once(
        source,
        "\t\tchangeWeek();\n\t\tchangeDifficulty();\n\n\t\tsuper.create();",
        replacement,
        "replace Psych Story layout with original Sonic.EXE Story assets",
    )

    path.write_text(source, encoding="utf-8")
    print(f"Installed original Sonic.EXE Story Mode artwork in {path}")


if __name__ == "__main__":
    main()
