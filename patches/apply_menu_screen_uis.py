#!/usr/bin/env python3
"""Apply a shared Sonic.EXE visual system to Freeplay, Story Mode, Extras and Sound Test."""

from pathlib import Path
import sys


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"Menu UI patch stopped: expected one match for {label}, found {count}")
    return source.replace(old, new)


def patch_freeplay(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "\t\tbg.screenCenter();\n\n\t\tgrpSongs = new FlxTypedGroup<Alphabet>();",
        """\t\tbg.screenCenter();

\t\t// Shared Sonic.EXE screen frame. Sound Test uses its own original art/video,
\t\t// while regular Freeplay keeps the engine's selected-song color backdrop.
\t\tvar sonicUiPanel:FlxSprite = new FlxSprite(28, 72).makeGraphic(FlxG.width - 56, FlxG.height - 118, 0x6506000B);
\t\tsonicUiPanel.scrollFactor.set();
\t\tadd(sonicUiPanel);
\t\tvar sonicUiHeader:FlxSprite = new FlxSprite(0, 0).makeGraphic(FlxG.width, 58, 0xE8000000);
\t\tsonicUiHeader.scrollFactor.set();
\t\tadd(sonicUiHeader);
\t\tvar sonicUiHeaderLine:FlxSprite = new FlxSprite(0, 55).makeGraphic(FlxG.width, 4, 0xFFE00024);
\t\tsonicUiHeaderLine.scrollFactor.set();
\t\tadd(sonicUiHeaderLine);
\t\tvar sonicUiLeftLine:FlxSprite = new FlxSprite(28, 72).makeGraphic(4, FlxG.height - 118, 0xFF9D001B);
\t\tsonicUiLeftLine.scrollFactor.set();
\t\tadd(sonicUiLeftLine);
\t\tvar sonicUiRightLine:FlxSprite = new FlxSprite(FlxG.width - 32, 72).makeGraphic(4, FlxG.height - 118, 0xFF9D001B);
\t\tsonicUiRightLine.scrollFactor.set();
\t\tadd(sonicUiRightLine);
\t\tvar sonicUiTitle:String = sonicExeCustomSongMode ? "SOUND TEST" : "FREEPLAY";
\t\tvar sonicUiHeaderText:FlxText = new FlxText(24, 8, 600, sonicUiTitle, 30);
\t\tsonicUiHeaderText.setFormat(Paths.font("sonichud.ttf"), 30, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tsonicUiHeaderText.scrollFactor.set();
\t\tadd(sonicUiHeaderText);
\t\tvar sonicUiHeaderHint:FlxText = new FlxText(FlxG.width - 650, 17, 220, "SELECT A TRACK", 15);
\t\tsonicUiHeaderHint.setFormat(Paths.font("sonichud.ttf"), 15, 0xFFFFB8C2, RIGHT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tsonicUiHeaderHint.scrollFactor.set();
\t\tadd(sonicUiHeaderHint);

\t\tgrpSongs = new FlxTypedGroup<Alphabet>();""",
        "Freeplay and Sound Test frame",
    )

    source = replace_once(
        source,
        'var leText:String = "Press SPACE to listen to the Song / Press CTRL to open the Gameplay Changers Menu / Press RESET to Reset your Score and Accuracy.";',
        'var leText:String = sonicExeCustomSongMode ? "SPACE: PREVIEW TRACK  /  ENTER: PLAY  /  LEFT OR RIGHT: DIFFICULTY  /  ESC: BACK" : "SPACE: PREVIEW  /  ENTER: PLAY  /  CTRL: GAMEPLAY CHANGERS  /  RESET: CLEAR SCORE";',
        "Freeplay versus Sound Test control hints",
    )

    source = replace_once(
        source,
        'bottomBG.alpha = 0.6;',
        'bottomBG.alpha = 0.88;',
        "darken Freeplay and Sound Test footer",
    )
    source = replace_once(
        source,
        'bottomText.setFormat(Paths.font("vcr.ttf"), size, FlxColor.WHITE, CENTER);',
        'bottomText.setFormat(Paths.font("sonichud.ttf"), 14, FlxColor.WHITE, CENTER);',
        "use Sonic HUD font for Freeplay and Sound Test instructions",
    )
    source = replace_once(
        source,
        'var size:Int = 16;',
        'var size:Int = 14;',
        "right-size Freeplay footer text",
    )
    path.write_text(source, encoding="utf-8")
    print(f"Styled Freeplay and Sound Test in {path}")


def patch_story(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        'var bgYellow:FlxSprite = new FlxSprite(0, 56).makeGraphic(FlxG.width, 386, 0xFFF9CF51);',
        'var bgYellow:FlxSprite = new FlxSprite(0, 56).makeGraphic(FlxG.width, 386, 0xC908060B);',
        "replace bright Story Mode slab with a translucent dark panel",
    )
    source = replace_once(
        source,
        'var blackBarThingie:FlxSprite = new FlxSprite().makeGraphic(FlxG.width, 56, FlxColor.BLACK);\n\t\tadd(blackBarThingie);',
        """var blackBarThingie:FlxSprite = new FlxSprite().makeGraphic(FlxG.width, 58, 0xE8000000);
\t\tadd(blackBarThingie);
\t\tvar sonicStoryAccent:FlxSprite = new FlxSprite(0, 55).makeGraphic(FlxG.width, 4, 0xFFE00024);
\t\tsonicStoryAccent.scrollFactor.set();
\t\tadd(sonicStoryAccent);
\t\tvar sonicStoryTitle:FlxText = new FlxText(FlxG.width * 0.34, 10, 360, "STORY MODE", 28);
\t\tsonicStoryTitle.setFormat(Paths.font("sonichud.ttf"), 28, FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tsonicStoryTitle.scrollFactor.set();
\t\tadd(sonicStoryTitle);""",
        "Story Mode title and red header",
    )
    source = replace_once(
        source,
        'txtWeekTitle.setFormat("VCR OSD Mono", 32, FlxColor.WHITE, RIGHT);',
        'txtWeekTitle.setFormat(Paths.font("sonichud.ttf"), 27, FlxColor.WHITE, RIGHT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);',
        "use Sonic HUD font for Story Mode week title",
    )
    source = replace_once(
        source,
        'txtTracklist.color = 0xFFe55777;',
        'txtTracklist.color = 0xFFFFC4CC;\n\t\ttxtTracklist.setFormat(Paths.font("sonichud.ttf"), 23, 0xFFFFC4CC, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);',
        "style Story Mode track list",
    )
    source = replace_once(
        source,
        '\t\tchangeWeek();\n\t\tchangeDifficulty();\n\n\t\tsuper.create();',
        """\t\tchangeWeek();
\t\tchangeDifficulty();

\t\tvar sonicStoryFooter:FlxSprite = new FlxSprite(0, FlxG.height - 34).makeGraphic(FlxG.width, 34, 0xE8000000);
\t\tsonicStoryFooter.scrollFactor.set();
\t\tadd(sonicStoryFooter);
\t\tvar sonicStoryFooterLine:FlxSprite = new FlxSprite(0, FlxG.height - 36).makeGraphic(FlxG.width, 3, 0xFF9D001B);
\t\tsonicStoryFooterLine.scrollFactor.set();
\t\tadd(sonicStoryFooterLine);
\t\tvar sonicStoryHints:FlxText = new FlxText(0, FlxG.height - 28, FlxG.width, "UP / DOWN: SELECT WEEK    LEFT / RIGHT: DIFFICULTY    ENTER: PLAY    ESC: BACK", 14);
\t\tsonicStoryHints.setFormat(Paths.font("sonichud.ttf"), 14, FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tsonicStoryHints.scrollFactor.set();
\t\tadd(sonicStoryHints);

\t\tsuper.create();""",
        "Story Mode footer and controls",
    )
    path.write_text(source, encoding="utf-8")
    print(f"Styled Story Mode in {path}")


def patch_extras(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        '\t\tbg.screenCenter();\n\t\t\n\t\tgrpOptions = new FlxTypedGroup<Alphabet>();',
        """\t\tbg.screenCenter();
\t\tbg.color = 0xFF4A101A;
\t\tvar sonicExtrasPanel:FlxSprite = new FlxSprite(28, 72).makeGraphic(FlxG.width - 56, FlxG.height - 118, 0x6506000B);
\t\tsonicExtrasPanel.scrollFactor.set();
\t\tadd(sonicExtrasPanel);
\t\tvar sonicExtrasHeader:FlxSprite = new FlxSprite(0, 0).makeGraphic(FlxG.width, 58, 0xE8000000);
\t\tsonicExtrasHeader.scrollFactor.set();
\t\tadd(sonicExtrasHeader);
\t\tvar sonicExtrasLine:FlxSprite = new FlxSprite(0, 55).makeGraphic(FlxG.width, 4, 0xFFE00024);
\t\tsonicExtrasLine.scrollFactor.set();
\t\tadd(sonicExtrasLine);
\t\tvar sonicExtrasTitle:FlxText = new FlxText(24, 8, 520, "EXTRAS", 30);
\t\tsonicExtrasTitle.setFormat(Paths.font("sonichud.ttf"), 30, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tsonicExtrasTitle.scrollFactor.set();
\t\tadd(sonicExtrasTitle);
\t\tvar sonicExtrasSubtitle:FlxText = new FlxText(FlxG.width - 370, 17, 340, "CREDITS  /  CONTRIBUTIONS", 15);
\t\tsonicExtrasSubtitle.setFormat(Paths.font("sonichud.ttf"), 15, 0xFFFFB8C2, RIGHT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tsonicExtrasSubtitle.scrollFactor.set();
\t\tadd(sonicExtrasSubtitle);

\t\tgrpOptions = new FlxTypedGroup<Alphabet>();""",
        "Extras header and content frame",
    )
    source = replace_once(
        source,
        'descText.setFormat(Paths.font("vcr.ttf"), 32, FlxColor.WHITE, CENTER/*, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK*/);',
        'descText.setFormat(Paths.font("sonichud.ttf"), 25, FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);',
        "use Sonic HUD font for Extras descriptions",
    )
    source = replace_once(
        source,
        '\t\tchangeSelection();\n\t\tsuper.create();',
        """\t\tchangeSelection();
\t\tvar sonicExtrasFooter:FlxSprite = new FlxSprite(0, FlxG.height - 32).makeGraphic(FlxG.width, 32, 0xE8000000);
\t\tsonicExtrasFooter.scrollFactor.set();
\t\tadd(sonicExtrasFooter);
\t\tvar sonicExtrasFooterLine:FlxSprite = new FlxSprite(0, FlxG.height - 34).makeGraphic(FlxG.width, 3, 0xFF9D001B);
\t\tsonicExtrasFooterLine.scrollFactor.set();
\t\tadd(sonicExtrasFooterLine);
\t\tvar sonicExtrasHints:FlxText = new FlxText(0, FlxG.height - 26, FlxG.width, "UP / DOWN: SELECT    ENTER: OPEN LINK    ESC: BACK", 14);
\t\tsonicExtrasHints.setFormat(Paths.font("sonichud.ttf"), 14, FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tsonicExtrasHints.scrollFactor.set();
\t\tadd(sonicExtrasHints);
\t\tsuper.create();""",
        "Extras footer and controls",
    )
    path.write_text(source, encoding="utf-8")
    print(f"Styled Extras/Credits in {path}")


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage: apply_menu_screen_uis.py path/to/FreeplayState.hx path/to/StoryMenuState.hx path/to/CreditsState.hx"
        )
    patch_freeplay(Path(sys.argv[1]))
    patch_story(Path(sys.argv[2]))
    patch_extras(Path(sys.argv[3]))


if __name__ == "__main__":
    main()
