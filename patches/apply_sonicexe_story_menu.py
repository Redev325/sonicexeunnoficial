#!/usr/bin/env python3
"""Keep the original playable Sonic.EXE Story Mode selector and restore its animated background."""
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

    # Keep Psych Engine's native week, character, lock, difficulty, score and
    # track-list objects. They remain connected to StoryMenuState's real logic.
    replacement = """\t\tchangeWeek();
\t\tchangeDifficulty();

\t\t// Keep the native selectable Story Mode UI visible. The previous mock
\t\t// screen hid these controls and replaced them with unrelated artwork.
\t\tbgYellow.visible = false;
\t\tbgSprite.visible = false;
\t\tblackBarThingie.visible = true;
\t\tgrpWeekText.visible = true;
\t\tgrpWeekCharacters.visible = true;
\t\tgrpLocks.visible = true;
\t\tdifficultySelectors.visible = true;
\t\ttracksSprite.visible = true;
\t\ttxtTracklist.visible = true;
\t\tscoreText.visible = true;
\t\ttxtWeekTitle.visible = true;

\t\t// The source game's full-screen 24-frame Story Mode static background.
\t\tvar sonicStoryBackground:FlxSprite = new FlxSprite(0, 0);
\t\tsonicStoryBackground.frames = Paths.getSparrowAtlas('SMMStatic');
\t\tsonicStoryBackground.animation.addByPrefix('staticLoop', 'damfstatic', 24, true);
\t\tsonicStoryBackground.animation.play('staticLoop');
\t\tsonicStoryBackground.setGraphicSize(FlxG.width, FlxG.height);
\t\tsonicStoryBackground.updateHitbox();
\t\tsonicStoryBackground.scrollFactor.set();
\t\tinsert(0, sonicStoryBackground);

\t\t// Subtle original screen-static animation, placed behind the selectable UI.
\t\tvar sonicStoryNoise:FlxSprite = new FlxSprite(0, 0);
\t\tsonicStoryNoise.frames = Paths.getSparrowAtlas('screenstatic');
\t\tsonicStoryNoise.animation.addByPrefix('staticLoop', 'screenSTATIC', 24, true);
\t\tsonicStoryNoise.animation.play('staticLoop');
\t\tsonicStoryNoise.setGraphicSize(FlxG.width, FlxG.height);
\t\tsonicStoryNoise.updateHitbox();
\t\tsonicStoryNoise.scrollFactor.set();
\t\tsonicStoryNoise.alpha = 0.08;
\t\tinsert(1, sonicStoryNoise);

\t\tvar sonicStoryDataTitle:FlxText = new FlxText(FlxG.width * 0.32, 8, FlxG.width * 0.36, 'DATA SELECT', 28);
\t\tsonicStoryDataTitle.setFormat(Paths.font('Plaza Regular.ttf'), 28, FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tsonicStoryDataTitle.scrollFactor.set();
\t\tadd(sonicStoryDataTitle);

\t\tsuper.create();"""

    source = replace_once(
        source,
        "\t\tchangeWeek();\n\t\tchangeDifficulty();\n\n\t\tsuper.create();",
        replacement,
        "restore native Story Mode selection and add original animated background",
    )

    path.write_text(source, encoding="utf-8")
    print(f"Restored the playable Sonic.EXE Story Mode selector in {path}")


if __name__ == "__main__":
    main()
