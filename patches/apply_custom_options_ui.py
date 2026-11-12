#!/usr/bin/env python3
"""Apply the original Sonic.EXE panel treatment to settings submenus."""

from pathlib import Path
import sys


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"Custom options UI patch stopped: expected one match for {label}, found {count}")
    return source.replace(old, new)


def patch_base_options(path: Path) -> None:
    source = path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        "\t\tsuper();\n\n\t\tif(title == null) title = 'Options';",
        "\t\tsuper();\n\t\t// The Options theme must remain active on every settings page.\n\t\tFlxG.sound.playMusic(Paths.music('options'), 0.72, true);\n\n\t\tif(title == null) title = 'Options';",
        "keep Options music active on shared settings pages",
    )

    source = replace_once(
        source,
        "private var descBox:FlxSprite;\n\tprivate var descText:FlxText;",
        """private var descBox:FlxSprite;
\tprivate var descText:FlxText;
\tprivate var customRows:FlxTypedGroup<FlxSprite>;
\tprivate var customHighlights:FlxTypedGroup<FlxSprite>;
\tprivate var customArrows:FlxTypedGroup<FlxSprite>;
\tprivate var customLabels:FlxTypedGroup<FlxText>;
\tprivate var customValues:FlxTypedGroup<FlxText>;
\tprivate var customTitlePanel:FlxSprite;
\tprivate var customTitle:FlxText;
\tprivate var customBackgroundTint:FlxSprite;
\tprivate var customBackgroundTime:Float = 0;
\tprivate var customBackgroundScaleX:Float = 1;
\tprivate var customBackgroundScaleY:Float = 1;""",
        "custom options UI fields",
    )

    source = replace_once(
        source,
        """\t\tbg = new FlxSprite().loadGraphic(Paths.image('menuDesat'));
\t\tbg.color = 0xFFea71fd;
\t\tbg.screenCenter();
\t\tbg.antialiasing = ClientPrefs.data.antialiasing;
\t\tadd(bg);""",
        """\t\t// Reuse the original Sonic.EXE red Options artwork for every settings page.
\t\tbg = new FlxSprite().loadGraphic(Paths.image('sonicexe-options/bg'));
\t\tbg.setGraphicSize(Std.int(FlxG.width * 1.08), Std.int(FlxG.height * 1.08));
\t\tbg.updateHitbox();
\t\tbg.screenCenter();
\t\tcustomBackgroundScaleX = bg.scale.x;
\t\tcustomBackgroundScaleY = bg.scale.y;
\t\tbg.color = 0xFFB02C2C;
\t\tbg.antialiasing = ClientPrefs.data.antialiasing;
\t\tbg.scrollFactor.set(0, 0);
\t\tadd(bg);

\t\tcustomBackgroundTint = new FlxSprite().makeGraphic(1, 1, 0xFF9D0D1D);
\t\tcustomBackgroundTint.setGraphicSize(FlxG.width, FlxG.height);
\t\tcustomBackgroundTint.updateHitbox();
\t\tcustomBackgroundTint.alpha = 0.08;
\t\tcustomBackgroundTint.scrollFactor.set(0, 0);
\t\tadd(customBackgroundTint);""",
        "original red options background",
    )

    source = replace_once(
        source,
        """\t\tcheckboxGroup = new FlxTypedGroup<CheckboxThingie>();
\t\tadd(checkboxGroup);

\t\tdescBox = new FlxSprite().makeGraphic(1, 1, FlxColor.BLACK);
\t\tdescBox.alpha = 0.6;
\t\tadd(descBox);

\t\tvar titleText:Alphabet = new Alphabet(75, 45, title, true);
\t\ttitleText.setScale(0.6);
\t\ttitleText.alpha = 0.4;
\t\tadd(titleText);

\t\tdescText = new FlxText(50, 600, 1180, "", 32);
\t\tdescText.setFormat(Paths.font("vcr.ttf"), 32, FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tdescText.scrollFactor.set();
\t\tdescText.borderSize = 2.4;
\t\tadd(descText);""",
        """\t\tcheckboxGroup = new FlxTypedGroup<CheckboxThingie>();
\t\tadd(checkboxGroup);

\t\t// The engine's original text/checkbox controls remain active for input and
\t\t// preference logic, but the visible presentation is replaced below.
\t\tgrpOptions.visible = false;
\t\tgrpTexts.visible = false;
\t\tcheckboxGroup.visible = false;

\t\tcustomRows = new FlxTypedGroup<FlxSprite>();
\t\tcustomHighlights = new FlxTypedGroup<FlxSprite>();
\t\tcustomArrows = new FlxTypedGroup<FlxSprite>();
\t\tcustomLabels = new FlxTypedGroup<FlxText>();
\t\tcustomValues = new FlxTypedGroup<FlxText>();
\t\tadd(customRows);
\t\tadd(customHighlights);
\t\tadd(customArrows);
\t\tadd(customLabels);
\t\tadd(customValues);

\t\tcustomTitlePanel = new FlxSprite();
\t\tcustomTitlePanel.loadGraphic(Paths.image('sonicexe-options/titleBG'));
\t\tcustomTitlePanel.setGraphicSize(Std.int(FlxG.width * 0.64), Std.int(FlxG.height * 0.10));
\t\tcustomTitlePanel.updateHitbox();
\t\tcustomTitlePanel.x = (FlxG.width - customTitlePanel.width) * 0.5;
\t\tcustomTitlePanel.y = FlxG.height * 0.015;
\t\tcustomTitlePanel.scrollFactor.set(0, 0);
\t\tadd(customTitlePanel);

\t\tcustomTitle = new FlxText(0, FlxG.height * 0.035, FlxG.width, title.toUpperCase(), Std.int(FlxG.height * 0.040));
\t\tcustomTitle.setFormat(Paths.font('sonichud.ttf'), Std.int(FlxG.height * 0.040), FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tcustomTitle.scrollFactor.set(0, 0);
\t\tadd(customTitle);

\t\tdescBox = new FlxSprite();
\t\tdescBox.loadGraphic(Paths.image('sonicexe-options/propertyBG'));
\t\tdescBox.alpha = 0.82;
\t\tadd(descBox);

\t\tdescText = new FlxText(120, 600, FlxG.width - 240, "", Std.int(FlxG.height * 0.023));
\t\tdescText.setFormat(Paths.font("sonichud.ttf"), Std.int(FlxG.height * 0.026), FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tdescText.scrollFactor.set();
\t\tdescText.borderSize = 1.5;
\t\tadd(descText);""",
        "replace stock option page header and description",
    )

    source = replace_once(
        source,
        """\t\t\t//optionText.snapToPosition(); //Don't ignore me when i ask for not making a fucking pull request to uncomment this line ok
\t\t\tupdateTextFrom(optionsArray[i]);
\t\t}

\t\tchangeSelection();""",
        """\t\t\t//optionText.snapToPosition(); //Don't ignore me when i ask for not making a fucking pull request to uncomment this line ok
\t\t\tupdateTextFrom(optionsArray[i]);

\t\t\tvar rowWidth:Int = Std.int(FlxG.width * 0.58);
\t\t\tvar rowHeight:Int = Std.int(rowWidth * (164.0 / 972.0));
\t\t\tvar row:FlxSprite = new FlxSprite();
\t\t\trow.loadGraphic(Paths.image('sonicexe-options/sectionBGClone'));
\t\t\trow.setGraphicSize(rowWidth, rowHeight);
\t\t\trow.updateHitbox();
\t\t\trow.scrollFactor.set(0, 0);
\t\t\tcustomRows.add(row);

\t\t\tvar selectedFrame:FlxSprite = new FlxSprite();
\t\t\tselectedFrame.loadGraphic(Paths.image('sonicexe-options/sectionBGWhite'));
\t\t\tselectedFrame.setGraphicSize(rowWidth, rowHeight);
\t\t\tselectedFrame.updateHitbox();
\t\t\tselectedFrame.alpha = 0;
\t\t\tselectedFrame.scrollFactor.set(0, 0);
\t\t\tcustomHighlights.add(selectedFrame);

\t\t\tvar labelSize:Int = Std.int(FlxG.height * 0.029);
\t\t\tvar label:FlxText = new FlxText(0, 0, rowWidth * 0.62, optionsArray[i].name, labelSize);
\t\t\tlabel.setFormat(Paths.font('sonichud.ttf'), labelSize, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\t\tlabel.scrollFactor.set(0, 0);
\t\t\tcustomLabels.add(label);

\t\t\tvar value:FlxText = new FlxText(0, 0, rowWidth * 0.30, '', labelSize);
\t\t\tvalue.setFormat(Paths.font('sonichud.ttf'), labelSize, 0xFFFFE7A6, RIGHT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\t\tvalue.scrollFactor.set(0, 0);
\t\t\tcustomValues.add(value);

\t\t\tvar arrow:FlxSprite = new FlxSprite();
\t\t\tarrow.loadGraphic(Paths.image('sonicexe-options/optionArrow'));
\t\t\tarrow.setGraphicSize(Std.int(FlxG.width * 0.047), Std.int(FlxG.height * 0.015));
\t\t\tarrow.updateHitbox();
\t\t\tarrow.alpha = 0.72;
\t\t\tarrow.scrollFactor.set(0, 0);
\t\t\tcustomArrows.add(arrow);
\t\t}

\t\tchangeSelection();""",
        "create custom Sonic row panels and labels",
    )

    source = replace_once(
        source,
        """\t\t\tif(curOption.type == 'bool')
\t\t\t{""",
        """\t\t\tif(curOption.type == 'bool')
\t\t\t{""",
        "validate boolean settings input path",
    )

    source = replace_once(
        source,
        """\t\tsuper.update(elapsed);

\t\tif(bindingKey)""",
        """\t\tsuper.update(elapsed);
\t\tupdateCustomOptionsUI(elapsed);

\t\tif(bindingKey)""",
        "update custom option visuals",
    )

    source = replace_once(
        source,
        """\t\tcurOption = optionsArray[curSelected]; //shorter lol
\t\tFlxG.sound.play(Paths.sound('scrollMenu'));
\t}""",
        """\t\tcurOption = optionsArray[curSelected]; //shorter lol
\t\tupdateCustomOptionsUI(0);
\t\tFlxG.sound.play(Paths.sound('scrollMenu'));
\t}""",
        "synchronize selected custom row",
    )

    custom_methods = """\tfunction customOptionValue(option:Option):String
\t{
\t\tif (option.type == 'bool')
\t\t\treturn option.getValue() == true ? 'ON' : 'OFF';
\t\tif (option.type == 'keybind')
\t\t\treturn option.text == null ? Std.string(option.getValue()) : option.text;

\t\tvar display:String = option.displayFormat;
\t\tvar value:Dynamic = option.getValue();
\t\tvar defaultValue:Dynamic = option.defaultValue;
\t\tif (option.type == 'percent') value *= 100;
\t\treturn display.replace('%v', Std.string(value)).replace('%d', Std.string(defaultValue));
\t}

\tfunction updateCustomOptionsUI(elapsed:Float):Void
\t{
\t\tcustomBackgroundTime += elapsed;
\t\tvar zoom:Float = 1.0 + Math.sin(customBackgroundTime * 0.32) * 0.007;
\t\tbg.scale.set(customBackgroundScaleX * zoom, customBackgroundScaleY * zoom);
\t\tbg.updateHitbox();
\t\tbg.x = (FlxG.width - bg.width) * 0.5 + Math.sin(customBackgroundTime * 0.28) * FlxG.width * 0.014;
\t\tbg.y = (FlxG.height - bg.height) * 0.5 + Math.cos(customBackgroundTime * 0.22) * FlxG.height * 0.010;
\t\tbg.angle = Math.sin(customBackgroundTime * 0.14) * 0.30;
\t\tcustomBackgroundTint.alpha = 0.055 + (Math.sin(customBackgroundTime * 0.72) + 1) * 0.028;

\t\tif (grpOptions == null || customRows == null) return;
\t\tvar rowWidth:Float = FlxG.width * 0.58;
\t\tfor (i in 0...customRows.length)
\t\t{
\t\t\tvar anchor:Alphabet = grpOptions.members[i];
\t\t\tvar row:FlxSprite = customRows.members[i];
\t\t\tvar frame:FlxSprite = customHighlights.members[i];
\t\t\tvar label:FlxText = customLabels.members[i];
\t\t\tvar value:FlxText = customValues.members[i];
\t\t\tvar arrow:FlxSprite = customArrows.members[i];
\t\t\tif (anchor == null || row == null) continue;

\t\t\trow.x = (FlxG.width - row.width) * 0.5;
\t\t\trow.y = anchor.y + (anchor.height - row.height) * 0.5;
\t\t\tframe.setPosition(row.x, row.y);
\t\t\tframe.alpha = (i == curSelected) ? 0.16 + (Math.sin(customBackgroundTime * 3.0) + 1) * 0.10 : 0;
\t\t\tlabel.x = row.x + rowWidth * 0.055;
\t\t\tlabel.y = row.y + (row.height - label.height) * 0.5;
\t\t\tlabel.alpha = (i == curSelected) ? 1 : 0.72;
\t\t\tvalue.x = row.x + rowWidth * 0.64;
\t\t\tvalue.y = row.y + (row.height - value.height) * 0.5;
\t\t\tvalue.text = customOptionValue(optionsArray[i]);
\t\t\tvalue.color = (i == curSelected) ? 0xFFFFE7A6 : FlxColor.WHITE;
\t\t\tvalue.alpha = (i == curSelected) ? 1 : 0.72;
\t\t\tarrow.x = row.x + rowWidth * 0.615;
\t\t\tarrow.y = row.y + (row.height - arrow.height) * 0.5;
\t\t\tarrow.visible = optionsArray[i].type != 'bool';
\t\t\tarrow.alpha = (i == curSelected) ? 0.85 : 0.48;
\t\t}
\t}

"""
    source = replace_once(
        source,
        "\tfunction changeSelection(change:Int = 0)",
        custom_methods + "\tfunction changeSelection(change:Int = 0)",
        "insert custom options UI helpers",
    )

    path.write_text(source, encoding="utf-8")
    print(f"Applied custom Sonic.EXE option panels to {path}")


def patch_controls(path: Path) -> None:
    source = path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        "\t\tsuper();\n\n\t\t#if DISCORD_ALLOWED",
        "\t\tsuper();\n\t\t// Controls is part of Options, so keep its dedicated theme playing too.\n\t\tFlxG.sound.playMusic(Paths.music('options'), 0.72, true);\n\n\t\t#if DISCORD_ALLOWED",
        "keep Options music active on the Controls page",
    )

    source = replace_once(
        source,
        "\tvar bg:FlxSprite;",
        """\tvar bg:FlxSprite;
\tvar customRowPanels:FlxTypedGroup<AttachedSprite>;
\tvar customTitlePanel:FlxSprite;
\tvar customTitle:FlxText;
\tvar customBackgroundTime:Float = 0;
\tvar customBackgroundScaleX:Float = 1;
\tvar customBackgroundScaleY:Float = 1;""",
        "controls custom UI fields",
    )

    source = replace_once(
        source,
        """\t\tbg = new FlxSprite().loadGraphic(Paths.image('menuDesat'));
\t\tbg.color = keyboardColor;
\t\tbg.antialiasing = ClientPrefs.data.antialiasing;
\t\tbg.screenCenter();
\t\tadd(bg);

\t\tvar grid:FlxBackdrop = new FlxBackdrop(FlxGridOverlay.createGrid(80, 80, 160, 160, true, 0x33FFFFFF, 0x0));
\t\tgrid.velocity.set(40, 40);
\t\tgrid.alpha = 0;
\t\tFlxTween.tween(grid, {alpha: 1}, 0.5, {ease: FlxEase.quadOut});
\t\tadd(grid);

\t\tgrpDisplay = new FlxTypedGroup<Alphabet>();
\t\tadd(grpDisplay);
\t\tgrpOptions = new FlxTypedGroup<Alphabet>();""",
        """\t\tbg = new FlxSprite().loadGraphic(Paths.image('sonicexe-options/bg'));
\t\tbg.setGraphicSize(Std.int(FlxG.width * 1.08), Std.int(FlxG.height * 1.08));
\t\tbg.updateHitbox();
\t\tbg.screenCenter();
\t\tcustomBackgroundScaleX = bg.scale.x;
\t\tcustomBackgroundScaleY = bg.scale.y;
\t\tbg.color = 0xFFB02C2C;
\t\tbg.antialiasing = ClientPrefs.data.antialiasing;
\t\tbg.scrollFactor.set(0, 0);
\t\tadd(bg);

\t\tvar grid:FlxBackdrop = new FlxBackdrop(FlxGridOverlay.createGrid(80, 80, 160, 160, true, 0x33FFFFFF, 0x0));
\t\tgrid.velocity.set(16, 16);
\t\tgrid.alpha = 0.10;
\t\tadd(grid);

\t\tcustomTitlePanel = new FlxSprite();
\t\tcustomTitlePanel.loadGraphic(Paths.image('sonicexe-options/titleBG'));
\t\tcustomTitlePanel.setGraphicSize(Std.int(FlxG.width * 0.52), Std.int(FlxG.height * 0.082));
\t\tcustomTitlePanel.updateHitbox();
\t\tcustomTitlePanel.x = (FlxG.width - customTitlePanel.width) * 0.5;
\t\tcustomTitlePanel.y = FlxG.height * 0.02;
\t\tcustomTitlePanel.scrollFactor.set(0, 0);
\t\tadd(customTitlePanel);
\t\tcustomTitle = new FlxText(0, FlxG.height * 0.035, FlxG.width, 'CONTROLS', Std.int(FlxG.height * 0.037));
\t\tcustomTitle.setFormat(Paths.font('sonichud.ttf'), Std.int(FlxG.height * 0.037), FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tcustomTitle.scrollFactor.set(0, 0);
\t\tadd(customTitle);

\t\tgrpDisplay = new FlxTypedGroup<Alphabet>();
\t\tadd(grpDisplay);
\t\tcustomRowPanels = new FlxTypedGroup<AttachedSprite>();
\t\tadd(customRowPanels);
\t\tgrpOptions = new FlxTypedGroup<Alphabet>();""",
        "original red background and controls header",
    )

    source = replace_once(
        source,
        """\t\tselectSpr = new AttachedSprite();
\t\tselectSpr.makeGraphic(250, 78, FlxColor.WHITE);
\t\tselectSpr.copyAlpha = false;
\t\tselectSpr.alpha = 0.75;
\t\tadd(selectSpr);""",
        """\t\tselectSpr = new AttachedSprite();
\t\tselectSpr.loadGraphic(Paths.image('sonicexe-options/sectionBGWhite'));
\t\tselectSpr.setGraphicSize(Std.int(FlxG.width * 0.76), Std.int(FlxG.height * 0.09));
\t\tselectSpr.updateHitbox();
\t\tselectSpr.xAdd = -395;
\t\tselectSpr.yAdd = -10;
\t\tselectSpr.copyAlpha = false;
\t\tselectSpr.alpha = 0.82;
\t\tadd(selectSpr);""",
        "custom Controls selected-row highlight",
    )

    source = replace_once(
        source,
        """\t\tgrpDisplay.forEachAlive(function(text:Alphabet) text.destroy());
\t\tgrpBlacks.forEachAlive(function(black:AttachedSprite) black.destroy());""",
        """\t\tgrpDisplay.forEachAlive(function(text:Alphabet) text.destroy());
\t\tcustomRowPanels.forEachAlive(function(panel:AttachedSprite) panel.destroy());
\t\tgrpBlacks.forEachAlive(function(black:AttachedSprite) black.destroy());""",
        "clear old controls row panels",
    )
    source = replace_once(
        source,
        """\t\tgrpDisplay.clear();
\t\tgrpBlacks.clear();""",
        """\t\tgrpDisplay.clear();
\t\tcustomRowPanels.clear();
\t\tgrpBlacks.clear();""",
        "clear custom controls panels",
    )

    source = replace_once(
        source,
        """\t\t\t\t\telse {
\t\t\t\t\t\tgrpOptions.add(text);
\t\t\t\t\t\tcurOptions.push(i);
\t\t\t\t\t\tcurOptionsValid.push(myID);
\t\t\t\t\t}""",
        """\t\t\t\t\telse {
\t\t\t\t\t\tvar rowPanel:AttachedSprite = new AttachedSprite();
\t\t\t\t\t\trowPanel.loadGraphic(Paths.image('sonicexe-options/sectionBGClone'));
\t\t\t\t\t\trowPanel.setGraphicSize(Std.int(FlxG.width * 0.62), Std.int(FlxG.height * 0.08));
\t\t\t\t\t\trowPanel.updateHitbox();
\t\t\t\t\t\trowPanel.sprTracker = text;
\t\t\t\t\t\trowPanel.xAdd = -41;
\t\t\t\t\t\trowPanel.yAdd = -12;
\t\t\t\t\t\trowPanel.alphaMult = 0.78;
\t\t\t\t\t\tcustomRowPanels.add(rowPanel);
\t\t\t\t\t\tgrpOptions.add(text);
\t\t\t\t\t\tcurOptions.push(i);
\t\t\t\t\t\tcurOptionsValid.push(myID);
\t\t\t\t\t}""",
        "draw original panel behind each key option",
    )

    source = replace_once(
        source,
        """\t\t\tvar black:AttachedSprite = new AttachedSprite();
\t\t\tblack.makeGraphic(250, 78, FlxColor.BLACK);
\t\t\tblack.alphaMult = 0.4;""",
        """\t\t\tvar black:AttachedSprite = new AttachedSprite();
\t\t\tblack.loadGraphic(Paths.image('sonicexe-options/propertyBG'));
\t\t\tblack.setGraphicSize(215, 68);
\t\t\tblack.updateHitbox();
\t\t\tblack.alphaMult = 0.84;""",
        "original key binding value panels",
    )

    source = replace_once(
        source,
        """\toverride function update(elapsed:Float)
\t{
\t\tif(timeForMoving > 0)""",
        """\toverride function update(elapsed:Float)
\t{
\t\tcustomBackgroundTime += elapsed;
\t\tvar zoom:Float = 1.0 + Math.sin(customBackgroundTime * 0.30) * 0.007;
\t\tbg.scale.set(customBackgroundScaleX * zoom, customBackgroundScaleY * zoom);
\t\tbg.updateHitbox();
\t\tbg.x = (FlxG.width - bg.width) * 0.5 + Math.sin(customBackgroundTime * 0.25) * FlxG.width * 0.012;
\t\tbg.y = (FlxG.height - bg.height) * 0.5 + Math.cos(customBackgroundTime * 0.20) * FlxG.height * 0.009;
\t\tbg.angle = Math.sin(customBackgroundTime * 0.14) * 0.28;

\t\tif(timeForMoving > 0)""",
        "animate controls red backdrop",
    )

    path.write_text(source, encoding="utf-8")
    print(f"Applied custom Sonic.EXE key-binding panels to {path}")



def patch_visuals(path: Path) -> None:
    source = path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        """			if(!noteSkins.contains(ClientPrefs.data.noteSkin))
				ClientPrefs.data.noteSkin = ClientPrefs.defaultData.noteSkin; //Reset to default if saved noteskin couldnt be found

			noteSkins.insert(0, ClientPrefs.defaultData.noteSkin); //Default skin always comes first""",
        """			if(!noteSkins.contains(ClientPrefs.data.noteSkin))
				ClientPrefs.data.noteSkin = 'Sonic.EXE';

			// Make the original Sonic.EXE arrows the first option and the option reset value.
			if (noteSkins.contains('Sonic.EXE'))
				noteSkins.remove('Sonic.EXE');
			noteSkins.insert(0, 'Sonic.EXE');
			if (!noteSkins.contains(ClientPrefs.defaultData.noteSkin))
				noteSkins.insert(1, ClientPrefs.defaultData.noteSkin);""",
        "make Sonic.EXE the first and reset-default note skin",
    )

    source = replace_once(
        source,
        """\t\tvar noteSplashes:Array<String> = Mods.mergeAllTextsNamed('images/noteSplashes/list.txt');
\t\tif(noteSplashes.length > 0)
\t\t{
\t\t\tif(!noteSplashes.contains(ClientPrefs.data.splashSkin))
\t\t\t\tClientPrefs.data.splashSkin = ClientPrefs.defaultData.splashSkin; //Reset to default if saved splashskin couldnt be found

\t\t\tnoteSplashes.insert(0, ClientPrefs.defaultData.splashSkin); //Default skin always comes first""",
        """\t\tvar noteSplashes:Array<String> = Mods.mergeAllTextsNamed('images/noteSplashes/list.txt');
\t\tif(noteSplashes.length > 0)
\t\t{
\t\t\tif(!noteSplashes.contains(ClientPrefs.data.splashSkin))
\t\t\t\tClientPrefs.data.splashSkin = ClientPrefs.defaultData.splashSkin; //Reset to default if saved splashskin couldnt be found

\t\t\t// Keep Sonic.EXE primary and restore the original Psych splash as the next option.
\t\t\tif (!noteSplashes.contains('Psych'))
\t\t\t\tnoteSplashes.push('Psych');
\t\t\tif (noteSplashes.contains(ClientPrefs.defaultData.splashSkin))
\t\t\t\tnoteSplashes.remove(ClientPrefs.defaultData.splashSkin);
\t\t\tif (noteSplashes.contains('Psych'))
\t\t\t\tnoteSplashes.remove('Psych');
\t\t\tnoteSplashes.insert(0, ClientPrefs.defaultData.splashSkin);
\t\t\tnoteSplashes.insert(1, 'Psych');""",
        "make Sonic.EXE the first and reset-default note splash",
    )

    source = replace_once(
        source,
        """\tfunction onChangePauseMusic()
\t{
\t\tif(ClientPrefs.data.pauseMusic == 'None')
\t\t\tFlxG.sound.music.volume = 0;
\t\telse
\t\t\tFlxG.sound.playMusic(Paths.music(Paths.formatToSongPath(ClientPrefs.data.pauseMusic)));

\t\tchangedMusic = true;
\t}""",
        """\tfunction onChangePauseMusic()
\t{
\t\t// Save the selected pause-screen track without interrupting the Options theme.
\t\tchangedMusic = true;
\t}""",
        "keep Options music while changing pause-screen song preference",
    )

    source = replace_once(
        source,
        """\t\tif(changedMusic && !OptionsState.onPlayState) FlxG.sound.playMusic(Paths.music('freakyMenu'), 1, true);""",
        """\t\tif(changedMusic && !OptionsState.onPlayState)
\t\t\tFlxG.sound.playMusic(Paths.music('options'), 0.72, true);""",
        "restore Options music after closing Visuals settings",
    )

    path.write_text(source, encoding="utf-8")
    print(f"Kept the Options soundtrack active in {path}")




def patch_client_prefs(path: Path) -> None:
    source = path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        "\tpublic var noteSkin:String = 'Default';",
        "\tpublic var noteSkin:String = 'Sonic.EXE';",
        "make Sonic.EXE the fresh-profile note skin",
    )

    source = replace_once(
        source,
        "\tpublic var splashSkin:String = 'Psych';",
        "\tpublic var splashSkin:String = 'Sonic.EXE';",
        "make Sonic.EXE the fresh-profile note splash",
    )

    source = replace_once(
        source,
        "\tpublic var splashSkin:String = 'Sonic.EXE';",
        "\tpublic var splashSkin:String = 'Sonic.EXE';\n\tpublic var splashSkinDefaultMigrated:Bool = false;",
        "add a one-time migration marker for the previous default splash",
    )

    source = replace_once(
        source,
        "\tpublic static var defaultData:SaveVariables = {};",
        "\tpublic static var defaultData:SaveVariables = {noteSkin: 'Default', splashSkin: 'Sonic.EXE', splashSkinDefaultMigrated: true};",
        "keep the base note skin as the no-suffix fallback",
    )

    source = replace_once(
        source,
        """\t\tfor (key in Reflect.fields(data))
\t\t\tif (key != 'gameplaySettings' && Reflect.hasField(FlxG.save.data, key))
\t\t\t\tReflect.setField(data, key, Reflect.field(FlxG.save.data, key));""",
        """\t\tfor (key in Reflect.fields(data))
\t\t\tif (key != 'gameplaySettings' && Reflect.hasField(FlxG.save.data, key))
\t\t\t\tReflect.setField(data, key, Reflect.field(FlxG.save.data, key));

\t\t// Move existing browser saves from the engine default to the game skin.
\t\tif (data.noteSkin == null || data.noteSkin == 'Default')
\t\t\tdata.noteSkin = 'Sonic.EXE';
\t\tif (!data.splashSkinDefaultMigrated)
\t\t{
\t\t\tif (data.splashSkin == null || data.splashSkin == 'Psych')
\t\t\t\tdata.splashSkin = 'Sonic.EXE';
\t\t\tdata.splashSkinDefaultMigrated = true;
\t\t}""",
        "migrate existing browser saves to Sonic.EXE once while preserving future Psych selections",
    )

    path.write_text(source, encoding="utf-8")
    print(f"Set Sonic.EXE as the fresh and migrated note skin in {path}")


def patch_note_splash(path: Path) -> None:
    source = path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        """\tpublic static function getSplashSkinPostfix()
\t{
\t\tvar skin:String = '';
\t\tif(ClientPrefs.data.splashSkin != ClientPrefs.defaultData.splashSkin)
\t\t\tskin = '-' + ClientPrefs.data.splashSkin.trim().toLowerCase().replace(' ', '_');
\t\treturn skin;
\t}""",
        """\tpublic static function getSplashSkinPostfix()
\t{
\t\tvar skin:String = '';
\t\tif(ClientPrefs.data.splashSkin != ClientPrefs.defaultData.splashSkin && ClientPrefs.data.splashSkin != 'Psych')
\t\t\tskin = '-' + ClientPrefs.data.splashSkin.trim().toLowerCase().replace(' ', '_');
\t\treturn skin;
\t}

\tpublic static function getSplashSkinPath():String
\t{
\t\tif (ClientPrefs.data.splashSkin == 'Sonic.EXE')
\t\t\treturn PlayState.isPixelStage ? 'noteSplashes/sonicexe-blood-pixel' : 'noteSplashes/sonicexe-blood';
\t\treturn defaultNoteSplash + getSplashSkinPostfix();
\t}""",
        "resolve Sonic.EXE selection to the animated BloodSplash atlas",
    )

    source = replace_once(
        source,
        """\t\tif (ClientPrefs.data.splashSkin == 'Sonic.EXE') skin = getSplashSkinPath();
\t\telse if(PlayState.SONG.splashSkin != null && PlayState.SONG.splashSkin.length > 0) skin = PlayState.SONG.splashSkin;
\t\telse skin = getSplashSkinPath();""",
        """\t\tif (ClientPrefs.data.splashSkin == 'Sonic.EXE') skin = getSplashSkinPath();
\t\telse if(PlayState.SONG.splashSkin != null && PlayState.SONG.splashSkin.length > 0) skin = PlayState.SONG.splashSkin;
\t\telse skin = getSplashSkinPath();""",
        "make the selected Sonic.EXE blood atlas override song-level splash defaults",
    )

    source = replace_once(
        source,
        """\t\tif(note != null && note.noteSplashData.texture != null) texture = note.noteSplashData.texture;
\t\telse if(PlayState.SONG.splashSkin != null && PlayState.SONG.splashSkin.length > 0) texture = PlayState.SONG.splashSkin;
\t\telse texture = defaultNoteSplash + getSplashSkinPostfix();""",
        """\t\t// Sonic.EXE uses the red BloodSplash atlas for every note hit.
\t\tif (ClientPrefs.data.splashSkin == 'Sonic.EXE') texture = getSplashSkinPath();
\t\telse if(note != null && note.noteSplashData.texture != null) texture = note.noteSplashData.texture;
\t\telse if(PlayState.SONG.splashSkin != null && PlayState.SONG.splashSkin.length > 0) texture = PlayState.SONG.splashSkin;
\t\telse texture = getSplashSkinPath();""",
        "prioritize the selected Sonic.EXE BloodSplash while preserving explicit note-type textures",
    )

    source = replace_once(
        source,
        """\t\tif(animName == null)
\t\t\tanimName = config != null ? config.anim : 'note splash';""",
        """\t\tif (StringTools.startsWith(skin, 'noteSplashes/sonicexe-blood'))
\t\t{
\t\t\tmaxAnims = 1;
\t\t\tanimation.addByPrefix('blood', 'Squirt', 24, false);
\t\t\treturn config;
\t\t}

\t\tif(animName == null)
\t\t\tanimName = config != null ? config.anim : 'note splash';""",
        "register the EXE Squirt animation frames",
    )

    source = replace_once(
        source,
        "\t\tanimation.play('note' + direction + '-' + animNum, true);",
        """\t\tif (StringTools.startsWith(texture, 'noteSplashes/sonicexe-blood'))
\t\t\tanimation.play('blood', true);
\t\telse
\t\t\tanimation.play('note' + direction + '-' + animNum, true);""",
        "play the BloodSplash animation for the Sonic.EXE skin",
    )

    path.write_text(source, encoding="utf-8")
    print(f"Set the default Sonic.EXE splash atlas in {path}")


def main() -> None:
    if len(sys.argv) != 6:
        raise SystemExit("Usage: apply_custom_options_ui.py path/to/BaseOptionsMenu.hx path/to/ControlsSubState.hx path/to/VisualsUISubState.hx path/to/ClientPrefs.hx path/to/NoteSplash.hx")
    patch_base_options(Path(sys.argv[1]))
    patch_controls(Path(sys.argv[2]))
    patch_visuals(Path(sys.argv[3]))
    patch_client_prefs(Path(sys.argv[4]))
    patch_note_splash(Path(sys.argv[5]))


if __name__ == "__main__":
    main()
