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
    # The Freeplay screen is installed by apply_sonicexe_freeplay_menu.py,
    # which uses the original animated background, gold photo frames and art.
    # Do not add generic panels, headers or substitute artwork here.
    if not path.is_file():
        raise SystemExit(f"Freeplay source file not found: {path}")
    print(f"Preserved original Freeplay layout for dedicated asset patch: {path}")

def patch_story(path: Path) -> None:
    # The Story Mode data-select visuals are installed by
    # apply_sonicexe_story_menu.py from the original static atlases and frames.
    if not path.is_file():
        raise SystemExit(f"Story Menu source file not found: {path}")
    print(f"Preserved original Story Mode layout for dedicated asset patch: {path}")

def patch_extras(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        '\t\tbg.screenCenter();\n\t\t\n\t\tgrpOptions = new FlxTypedGroup<Alphabet>();',
        """\t\tbg.screenCenter();
\t\t// Keep the original Extras background colors and artwork unchanged.
\t\tvar sonicExtrasPanel:FlxSprite = new FlxSprite(28, 72).makeGraphic(FlxG.width - 56, FlxG.height - 118, 0x6506000B);
\t\tsonicExtrasPanel.scrollFactor.set();
\t\tadd(sonicExtrasPanel);
\t\tvar sonicExtrasHeader:FlxSprite = new FlxSprite(0, 0).makeGraphic(FlxG.width, 58, 0xE8000000);
\t\tsonicExtrasHeader.scrollFactor.set();
\t\tadd(sonicExtrasHeader);
\t\tvar sonicExtrasLine:FlxSprite = new FlxSprite(0, 55).makeGraphic(FlxG.width, 4, 0xFFE00024);
\t\tsonicExtrasLine.scrollFactor.set();
\t\tadd(sonicExtrasLine);
\t\tvar sonicExtrasTitle:FlxText = new FlxText(24, 8, 520, "CREDITS", 30);
\t\tsonicExtrasTitle.setFormat(Paths.font("sonichud.ttf"), 30, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tsonicExtrasTitle.scrollFactor.set();
\t\tadd(sonicExtrasTitle);
\t\tvar sonicExtrasSubtitle:FlxText = new FlxText(FlxG.width - 370, 17, 340, "PSYCH ENGINE CONTRIBUTORS", 15);
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
