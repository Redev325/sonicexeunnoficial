#!/usr/bin/env python3
"""Apply the original browser main-menu layout to the open-source Psych Engine source."""

from pathlib import Path
import sys


def replace_once(source: str, old: str, new: str, label: str, count: int = 1) -> str:
    found = source.count(old)
    if found != count:
        raise SystemExit(
            f"MainMenuState patch stopped: expected {count} match(es) for {label}, found {found}"
        )
    return source.replace(old, new)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: apply_main_menu.py path/to/MainMenuState.hx")

    target = Path(sys.argv[1])
    if not target.is_file():
        raise SystemExit(f"Psych Engine source file not found: {target}")

    source = target.read_text(encoding="utf-8")

    source = replace_once(
        source,
        "var magenta:FlxSprite;\n\tvar camFollow:FlxObject;",
        "var magenta:FlxSprite;\n"
        "\tvar camFollow:FlxObject;\n"
        "\tvar selectedModeText:FlxText;\n"
        "\tvar selectedModeDescription:FlxText;",
        "menu information fields",
    )

    source = replace_once(
        source,
        """\t\tvar bg:FlxSprite = new FlxSprite(-80).loadGraphic(Paths.image('menuBG'));
\t\tbg.antialiasing = ClientPrefs.data.antialiasing;
\t\tbg.scrollFactor.set(0, yScroll);
\t\tbg.setGraphicSize(Std.int(bg.width * 1.175));
\t\tbg.updateHitbox();
\t\tbg.screenCenter();
\t\tadd(bg);""",
        """\t\t// Original dark, high-contrast browser menu background.
\t\tvar bg:FlxSprite = new FlxSprite().makeGraphic(FlxG.width, FlxG.height, 0xFF08080D);
\t\tbg.scrollFactor.set(0, 0);
\t\tadd(bg);

\t\tvar upperBand:FlxSprite = new FlxSprite(0, 0).makeGraphic(FlxG.width, 5, 0xFFFF405B);
\t\tupperBand.scrollFactor.set(0, 0);
\t\tadd(upperBand);

\t\tvar lowerBand:FlxSprite = new FlxSprite(0, FlxG.height - 5).makeGraphic(FlxG.width, 5, 0xFF6B2638);
\t\tlowerBand.scrollFactor.set(0, 0);
\t\tadd(lowerBand);

\t\tvar leftRail:FlxSprite = new FlxSprite(30, 0).makeGraphic(2, FlxG.height, 0xFF401D2A);
\t\tleftRail.scrollFactor.set(0, 0);
\t\tadd(leftRail);""",
        "custom browser background",
    )

    source = replace_once(
        source,
        "\t\tadd(magenta);\n\n\t\tmenuItems = new FlxTypedGroup<FlxSprite>();",
        "\t\tadd(magenta);\n\n\t\tbuildSidePanel();\n\n\t\tmenuItems = new FlxTypedGroup<FlxSprite>();",
        "side panel creation call",
    )

    source = replace_once(
        source,
        "var menuItem:FlxSprite = new FlxSprite(0, (i * 140) + offset);",
        "var menuItem:FlxSprite = new FlxSprite(60, (i * 140) + offset);",
        "left aligned menu item construction",
    )
    source = replace_once(
        source,
        "\t\t\tmenuItem.screenCenter(X);",
        "\t\t\tmenuItem.x = 60;",
        "left aligned menu item placement",
    )

    source = replace_once(
        source,
        "\t\tmenuItems.members[curSelected].screenCenter(X);",
        "\t\tmenuItems.members[curSelected].x = 60;",
        "left aligned current item placement",
        count=2,
    )

    source = replace_once(
        source,
        "camFollow.setPosition(menuItems.members[curSelected].getGraphicMidpoint().x,",
        "camFollow.setPosition(FlxG.width * 0.5,",
        "fixed horizontal camera position",
    )

    insertion = """\tfunction buildSidePanel():Void
\t{
\t\tvar sidePanel = new FlxSprite(870, 0).makeGraphic(FlxG.width - 870, FlxG.height, 0xF20D0D14);
\t\tsidePanel.scrollFactor.set(0, 0);
\t\tadd(sidePanel);

\t\tvar panelEdge = new FlxSprite(866, 0).makeGraphic(3, FlxG.height, 0xFFFF405B);
\t\tpanelEdge.scrollFactor.set(0, 0);
\t\tadd(panelEdge);

\t\tvar topLabel = new FlxText(915, 125, FlxG.width - 940, "SONIC.EXE", 42);
\t\ttopLabel.scrollFactor.set(0, 0);
\t\ttopLabel.setFormat("VCR OSD Mono", 42, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tadd(topLabel);

\t\tvar editionLabel = new FlxText(918, 183, FlxG.width - 940, "UNOFFICIAL  /  BROWSER EDITION", 12);
\t\teditionLabel.scrollFactor.set(0, 0);
\t\teditionLabel.setFormat("VCR OSD Mono", 12, 0xFFFF7184, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tadd(editionLabel);

\t\tvar separator = new FlxSprite(915, 235).makeGraphic(FlxG.width - 955, 2, 0xFF763344);
\t\tseparator.scrollFactor.set(0, 0);
\t\tadd(separator);

\t\tvar selectedLabel = new FlxText(918, 275, FlxG.width - 940, "SELECTED MODE", 11);
\t\tselectedLabel.scrollFactor.set(0, 0);
\t\tselectedLabel.setFormat("VCR OSD Mono", 11, 0xFFB2A6B2, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tadd(selectedLabel);

\t\tselectedModeText = new FlxText(915, 310, FlxG.width - 940, "STORY MODE", 27);
\t\tselectedModeText.scrollFactor.set(0, 0);
\t\tselectedModeText.setFormat("VCR OSD Mono", 27, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tadd(selectedModeText);

\t\tselectedModeDescription = new FlxText(918, 360, FlxG.width - 945, "", 13);
\t\tselectedModeDescription.scrollFactor.set(0, 0);
\t\tselectedModeDescription.setFormat("VCR OSD Mono", 13, 0xFFD0CBD4, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tadd(selectedModeDescription);

\t\tvar controlRule = new FlxSprite(915, 510).makeGraphic(FlxG.width - 955, 2, 0xFF763344);
\t\tcontrolRule.scrollFactor.set(0, 0);
\t\tadd(controlRule);

\t\tvar controls = new FlxText(918, 535, FlxG.width - 940,
\t\t\t"UP / DOWN   SELECT\\nENTER       CONFIRM\\nESC         BACK", 12);
\t\tcontrols.scrollFactor.set(0, 0);
\t\tcontrols.setFormat("VCR OSD Mono", 12, 0xFFFF7184, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tadd(controls);
\t}

\tfunction updateMenuInformation():Void
\t{
\t\tif (selectedModeText == null || selectedModeDescription == null) return;

\t\tselectedModeText.text = switch (optionShit[curSelected])
\t\t{
\t\t\tcase 'story_mode': 'STORY MODE';
\t\t\tcase 'freeplay': 'FREEPLAY';
\t\t\tcase 'mods': 'MODS';
\t\t\tcase 'awards': 'AWARDS';
\t\t\tcase 'credits': 'CREDITS';
\t\t\tcase 'donate': 'SUPPORT';
\t\t\tcase 'options': 'OPTIONS';
\t\t\tdefault: 'MENU';
\t\t};

\t\tselectedModeDescription.text = switch (optionShit[curSelected])
\t\t{
\t\t\tcase 'story_mode': 'Play the available story weeks and follow the song order.';
\t\t\tcase 'freeplay': 'Choose an individual song and play it on your own terms.';
\t\t\tcase 'mods': 'Browse and select installed content packs.';
\t\t\tcase 'awards': 'Review achievements earned while playing.';
\t\t\tcase 'credits': 'See the people behind the engine and this project.';
\t\t\tcase 'donate': 'Visit the engine creators’ support page.';
\t\t\tcase 'options': 'Adjust controls, visuals, audio, and gameplay settings.';
\t\t\tdefault: 'Choose a menu option to continue.';
\t\t};
\t}

"""

    source = replace_once(
        source,
        "\tvar selectedSomethin:Bool = false;",
        insertion + "\tvar selectedSomethin:Bool = false;",
        "side panel helper methods",
    )

    source = replace_once(
        source,
        "\t\tcamFollow.setPosition(FlxG.width * 0.5,\n\t\t\tmenuItems.members[curSelected].getGraphicMidpoint().y - (menuItems.length > 4 ? menuItems.length * 8 : 0));",
        "\t\tcamFollow.setPosition(FlxG.width * 0.5,\n\t\t\tmenuItems.members[curSelected].getGraphicMidpoint().y - (menuItems.length > 4 ? menuItems.length * 8 : 0));\n"
        "\t\tupdateMenuInformation();",
        "update selected mode detail text",
    )

    target.write_text(source, encoding="utf-8")
    print(f"Applied original browser main menu layout to {target}")


if __name__ == "__main__":
    main()
