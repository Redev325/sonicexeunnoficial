#!/usr/bin/env python3
"""Install the original animated Sonic.EXE Story Mode data-select screen."""
from pathlib import Path
import sys


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"Original Story Mode patch stopped: {label} expected once, found {count}")
    return source.replace(old, new)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: apply_sonicexe_story_menu.py engine/source/states/StoryMenuState.hx")

    path = Path(sys.argv[1])
    source = path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        "\tvar loadedWeeks:Array<WeekData> = [];",
        """\tvar loadedWeeks:Array<WeekData> = [];
\tvar sonicStoryWeekLabel:FlxText;
\tvar sonicStoryDifficultyLabel:FlxText;""",
        "add selected week and difficulty labels",
    )

    # The old menu objects remain allocated because the original week-selection
    # and score logic uses them. They are simply hidden beneath the original
    # data-select artwork; no week/song loading code is replaced.
    code = """\t\t// The original Story Mode screen is built from the mod's real atlases.
\t\t// Keep the stock groups alive for the existing week/score selection logic,
\t\t// but do not draw their generic menu layout over the source-game screen.
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
\t\trankText.visible = false;

\t\tvar sonicStoryBackground:FlxSprite = new FlxSprite(0, 0);
\t\tsonicStoryBackground.frames = Paths.getSparrowAtlas('SMMStatic');
\t\tsonicStoryBackground.animation.addByPrefix('staticLoop', 'damfstatic', 24, true);
\t\tsonicStoryBackground.animation.play('staticLoop');
\t\tsonicStoryBackground.setGraphicSize(FlxG.width, FlxG.height);
\t\tsonicStoryBackground.updateHitbox();
\t\tinsert(0, sonicStoryBackground);

\t\t// The upper picture is the original hand-drawn Story image. Its static
\t\t// layer is a separate animated atlas, as in the source-game data select.
\t\tvar sonicStoryPortrait:FlxSprite = new FlxSprite(46, 10);
\t\tsonicStoryPortrait.loadGraphic(Paths.image('fpstuff/story'));
\t\tsonicStoryPortrait.setGraphicSize(620);
\t\tsonicStoryPortrait.updateHitbox();
\t\tsonicStoryPortrait.antialiasing = true;
\t\tadd(sonicStoryPortrait);

\t\tvar sonicStoryPortraitStatic:FlxSprite = new FlxSprite(46, 10);
\t\tsonicStoryPortraitStatic.frames = Paths.getSparrowAtlas('screenstatic');
\t\tsonicStoryPortraitStatic.animation.addByPrefix('staticLoop', 'screenSTATIC', 24, true);
\t\tsonicStoryPortraitStatic.animation.play('staticLoop');
\t\tsonicStoryPortraitStatic.setGraphicSize(620);
\t\tsonicStoryPortraitStatic.updateHitbox();
\t\tsonicStoryPortraitStatic.alpha = 0.30;
\t\tsonicStoryPortraitStatic.antialiasing = true;
\t\tadd(sonicStoryPortraitStatic);

\t\t// Boyfriend uses the existing animated character atlas, not a drawn stand-in.
\t\tvar sonicStoryBoyfriend:FlxSprite = new FlxSprite(275, 300);
\t\tsonicStoryBoyfriend.frames = Paths.getSparrowAtlas('characters/BOYFRIEND', 'shared');
\t\tsonicStoryBoyfriend.animation.addByPrefix('idle', 'BF idle dance', 24, true);
\t\tsonicStoryBoyfriend.animation.play('idle');
\t\tsonicStoryBoyfriend.setGraphicSize(170);
\t\tsonicStoryBoyfriend.updateHitbox();
\t\tsonicStoryBoyfriend.antialiasing = true;
\t\tadd(sonicStoryBoyfriend);

\t\t// The two original T-shaped card frames share the same crop and scale
\t\t// used in the reference screen. The second frame is the locked data slot.
\t\tvar sonicStoryLockedShade:FlxSprite = new FlxSprite(850, 85).makeGraphic(340, 410, 0xD9000000);
\t\tsonicStoryLockedShade.scrollFactor.set();
\t\tadd(sonicStoryLockedShade);

\t\tvar sonicStoryRightGreyFrame:FlxSprite = new FlxSprite(442, 0);
\t\tsonicStoryRightGreyFrame.loadGraphic(Paths.image('greybox'));
\t\tsonicStoryRightGreyFrame.setGraphicSize(Std.int(FlxG.width * 0.72));
\t\tsonicStoryRightGreyFrame.updateHitbox();
\t\tsonicStoryRightGreyFrame.alpha = 0.34;
\t\tadd(sonicStoryRightGreyFrame);

\t\tvar sonicStoryGoldFrame:FlxSprite = new FlxSprite(-224, 0);
\t\tsonicStoryGoldFrame.loadGraphic(Paths.image('yellowbox'));
\t\tsonicStoryGoldFrame.setGraphicSize(Std.int(FlxG.width * 0.72));
\t\tsonicStoryGoldFrame.updateHitbox();
\t\tadd(sonicStoryGoldFrame);

\t\tvar sonicStoryLockedGoldFrame:FlxSprite = new FlxSprite(442, 0);
\t\tsonicStoryLockedGoldFrame.loadGraphic(Paths.image('yellowbox'));
\t\tsonicStoryLockedGoldFrame.setGraphicSize(Std.int(FlxG.width * 0.72));
\t\tsonicStoryLockedGoldFrame.updateHitbox();
\t\tsonicStoryLockedGoldFrame.alpha = 0.72;
\t\tadd(sonicStoryLockedGoldFrame);

\t\tvar sonicStoryOuterSelection:FlxSprite = new FlxSprite(0, 0);
\t\tsonicStoryOuterSelection.loadGraphic(Paths.image('redbox'));
\t\tsonicStoryOuterSelection.setGraphicSize(FlxG.width, FlxG.height);
\t\tsonicStoryOuterSelection.updateHitbox();
\t\tadd(sonicStoryOuterSelection);

\t\tvar sonicStoryLock:FlxSprite = new FlxSprite(1000, 275);
\t\tsonicStoryLock.frames = Paths.getSparrowAtlas('campaign_menu_UI_assets');
\t\tsonicStoryLock.animation.addByPrefix('lock', 'lock', 24, true);
\t\tsonicStoryLock.animation.play('lock');
\t\tsonicStoryLock.setGraphicSize(66);
\t\tsonicStoryLock.updateHitbox();
\t\tadd(sonicStoryLock);

\t\tvar sonicStoryDataTitle:FlxText = new FlxText(0, FlxG.height - 170, FlxG.width, 'DATA SELECT', 82);
\t\tsonicStoryDataTitle.setFormat(Paths.font('Plaza Regular.ttf'), 82, FlxColor.WHITE, CENTER);
\t\tsonicStoryDataTitle.antialiasing = true;
\t\tsonicStoryDataTitle.scrollFactor.set();
\t\tadd(sonicStoryDataTitle);

\t\tsonicStoryWeekLabel = new FlxText(FlxG.width * 0.56, FlxG.height - 64, FlxG.width * 0.40, '', 24);
\t\tsonicStoryWeekLabel.setFormat(Paths.font('sonichud.ttf'), 24, FlxColor.WHITE, RIGHT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tsonicStoryWeekLabel.scrollFactor.set();
\t\tadd(sonicStoryWeekLabel);

\t\tsonicStoryDifficultyLabel = new FlxText(FlxG.width * 0.56, FlxG.height - 34, FlxG.width * 0.40, '', 18);
\t\tsonicStoryDifficultyLabel.setFormat(Paths.font('sonichud.ttf'), 18, 0xFFFFC4CC, RIGHT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tsonicStoryDifficultyLabel.scrollFactor.set();
\t\tadd(sonicStoryDifficultyLabel);

\t\tif (loadedWeeks.length > 0)
\t\t\tsonicStoryWeekLabel.text = loadedWeeks[curWeek].storyName.toUpperCase();
\t\tsonicStoryDifficultyLabel.text = Difficulty.getString(curDifficulty).toUpperCase();

\t\tsuper.create();"""

    source = replace_once(
        source,
        "\t\tchangeWeek();\n\t\tchangeDifficulty();\n\n\t\tsuper.create();",
        code,
        "replace generic Story Mode presentation with original animated data select",
    )

    source = replace_once(
        source,
        "\t\tvar leName:String = leWeek.storyName;\n\t\ttxtWeekTitle.text = leName.toUpperCase();",
        "\t\tvar leName:String = leWeek.storyName;\n\t\ttxtWeekTitle.text = leName.toUpperCase();\n\t\tif (sonicStoryWeekLabel != null) sonicStoryWeekLabel.text = leName.toUpperCase();",
        "keep the visible data-select label synced to the current week",
    )

    source = replace_once(
        source,
        "\t\tlastDifficultyName = diff;",
        "\t\tlastDifficultyName = diff;\n\t\tif (sonicStoryDifficultyLabel != null) sonicStoryDifficultyLabel.text = diff.toUpperCase();",
        "keep the visible difficulty label synced",
    )

    path.write_text(source, encoding="utf-8")
    print(f"Installed original animated Sonic.EXE Story Mode data select in {path}")


if __name__ == "__main__":
    main()
