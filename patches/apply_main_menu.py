#!/usr/bin/env python3
"""Apply the reference-inspired Sonic EXE menu layout to Psych Engine."""

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
        "import lime.app.Application;",
        "import lime.app.Application;\nimport openfl.display.BitmapData;\nimport openfl.display.Shape;",
        "OpenFL drawing imports",
    )

    source = replace_once(
        source,
        """\tvar optionShit:Array<String> = [
\t\t'story_mode',
\t\t'freeplay',
\t\t#if MODS_ALLOWED 'mods', #end
\t\t#if ACHIEVEMENTS_ALLOWED 'awards', #end
\t\t'credits',
\t\t#if !switch 'donate', #end
\t\t'options'
\t];""",
        """\tvar optionShit:Array<String> = [
\t\t'sound_test',
\t\t'freeplay',
\t\t'story_mode',
\t\t'extras',
\t\t'options'
\t];""",
        "five reference menu destinations",
    )

    source = replace_once(
        source,
        "var magenta:FlxSprite;\n\tvar camFollow:FlxObject;",
        "var magenta:FlxSprite;\n\tvar camFollow:FlxObject;\n\tvar menuPlates:FlxTypedGroup<FlxSprite>;\n\tvar movingRedBackdrop:FlxSprite;\n\tvar backdropTileWidth:Int = 0;\n\tvar backdropTravel:Float = 0;",
        "menu button plate group",
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
        "\t\tbuildReferenceBackdrop();",
        "reference-inspired red and black background",
    )

    source = replace_once(
        source,
        "\t\tadd(magenta);\n\n\t\tmenuItems = new FlxTypedGroup<FlxSprite>();",
        "\t\tadd(magenta);\n\n\t\tmenuPlates = new FlxTypedGroup<FlxSprite>();\n\t\tadd(menuPlates);\n\n\t\tmenuItems = new FlxTypedGroup<FlxSprite>();",
        "menu plates behind menu labels",
    )

    old_loop = """\t\tfor (i in 0...optionShit.length)
\t\t{
\t\t\tvar offset:Float = 108 - (Math.max(optionShit.length, 4) - 4) * 80;
\t\t\tvar menuItem:FlxSprite = new FlxSprite(0, (i * 140) + offset);
\t\t\tmenuItem.antialiasing = ClientPrefs.data.antialiasing;
\t\t\tmenuItem.frames = Paths.getSparrowAtlas('mainmenu/menu_' + optionShit[i]);
\t\t\tmenuItem.animation.addByPrefix('idle', optionShit[i] + " basic", 24);
\t\t\tmenuItem.animation.addByPrefix('selected', optionShit[i] + " white", 24);
\t\t\tmenuItem.animation.play('idle');
\t\t\tmenuItems.add(menuItem);
\t\t\tvar scr:Float = (optionShit.length - 4) * 0.135;
\t\t\tif (optionShit.length < 6)
\t\t\t\tscr = 0;
\t\t\tmenuItem.scrollFactor.set(0, scr);
\t\t\tmenuItem.updateHitbox();
\t\t\tmenuItem.screenCenter(X);
\t\t}"""
    new_loop = """\t\tvar buttonX:Int = Std.int(FlxG.width * 0.505);
\t\tvar buttonWidth:Int = Std.int(FlxG.width * 0.485);
\t\tvar buttonHeight:Int = Std.int(FlxG.height * 0.135);
\t\tvar labelSize:Int = Std.int(FlxG.height * 0.075);
\t\tfor (i in 0...optionShit.length)
\t\t{
\t\t\tvar buttonY:Int = Std.int(FlxG.height * (0.075 + i * 0.19));
\t\t\tvar plate:FlxSprite = new FlxSprite(buttonX, buttonY);
\t\t\tplate.loadGraphic(makeMenuPlate(buttonWidth, buttonHeight, i == curSelected));
\t\t\tplate.scrollFactor.set(0, 0);
\t\t\tmenuPlates.add(plate);

\t\t\tvar label:FlxText = new FlxText(buttonX + 18, buttonY + 8, buttonWidth - 36, menuLabel(i), labelSize);
\t\t\tlabel.antialiasing = false;
\t\t\tlabel.scrollFactor.set(0, 0);
\t\t\tlabel.setFormat("VCR OSD Mono", labelSize, FlxColor.GRAY, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\t\tlabel.y = buttonY + (buttonHeight - label.height) * 0.5 - 2;
\t\t\tmenuItems.add(label);
\t\t}"""
    source = replace_once(source, old_loop, new_loop, "replace standard icon row with angled pixel menu")

    # The game version labels are moved to the upper-left to stay out of the menu list.
    source = replace_once(
        source,
        "var psychVer:FlxText = new FlxText(12, FlxG.height - 44, 0, \"Psych Engine v\" + psychEngineVersion, 12);",
        "var psychVer:FlxText = new FlxText(8, 6, 0, \"Psych Engine v\" + psychEngineVersion, 8);",
        "upper-left engine version label",
    )
    source = replace_once(
        source,
        "psychVer.setFormat(\"VCR OSD Mono\", 16, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);",
        "psychVer.setFormat(\"VCR OSD Mono\", 8, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);",
        "small engine version text",
    )
    source = replace_once(
        source,
        "var fnfVer:FlxText = new FlxText(12, FlxG.height - 24, 0, \"Friday Night Funkin' v\" + Application.current.meta.get('version'), 12);",
        "var fnfVer:FlxText = new FlxText(8, 17, 0, \"Friday Night Funkin' v\" + Application.current.meta.get('version'), 8);",
        "upper-left game version label",
    )
    source = replace_once(
        source,
        "fnfVer.setFormat(\"VCR OSD Mono\", 16, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);",
        "fnfVer.setFormat(\"VCR OSD Mono\", 8, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);",
        "small game version text",
    )

    # Sound Test is a lightweight action for now; the other four choices enter real engine screens.
    source = replace_once(
        source,
        "\t\t\t\t\t\tswitch (optionShit[curSelected])\n\t\t\t\t\t\t{\n",
        "\t\t\t\t\t\tswitch (optionShit[curSelected])\n\t\t\t\t\t\t{\n"
        "\t\t\t\t\t\t\tcase 'sound_test':\n"
        "\t\t\t\t\t\t\t\tFlxG.sound.play(Paths.sound('confirmMenu'));\n"
        "\t\t\t\t\t\t\t\tMusicBeatState.switchState(new FreeplayState());\n"
        "\t\t\t\t\t\t\tcase 'extras':\n"
        "\t\t\t\t\t\t\t\tMusicBeatState.switchState(new CreditsState());\n",
        "sound test and extras menu actions",
    )

    # Fade the button outlines along with the selected labels when changing screens.
    source = replace_once(
        source,
        """\t\t\t\t\t\tFlxTween.tween(menuItems.members[i], {alpha: 0}, 0.4, {
\t\t\t\t\t\t\tease: FlxEase.quadOut,
\t\t\t\t\t\t\tonComplete: function(twn:FlxTween)
\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\tmenuItems.members[i].kill();
\t\t\t\t\t\t\t}
\t\t\t\t\t\t});""",
        """\t\t\t\t\t\tFlxTween.tween(menuItems.members[i], {alpha: 0}, 0.4, {
\t\t\t\t\t\t\tease: FlxEase.quadOut,
\t\t\t\t\t\t\tonComplete: function(twn:FlxTween)
\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\tmenuItems.members[i].kill();
\t\t\t\t\t\t\t}
\t\t\t\t\t\t});
\t\t\t\t\t\tFlxTween.tween(menuPlates.members[i], {alpha: 0}, 0.4, {
\t\t\t\t\t\t\tease: FlxEase.quadOut,
\t\t\t\t\t\t\tonComplete: function(twn:FlxTween)
\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\tmenuPlates.members[i].kill();
\t\t\t\t\t\t\t}
\t\t\t\t\t\t});""",
        "fade menu plates on transition",
    )

    helper_methods = """\tfunction menuLabel(index:Int):String
\t{
\t\treturn switch (index)
\t\t{
\t\t\tcase 0: "SOUND TEST";
\t\t\tcase 1: "JUEGO LIBRE";
\t\t\tcase 2: "MODO HISTORIA";
\t\t\tcase 3: "EXTRAS";
\t\t\tcase 4: "OPCIONES";
\t\t\tdefault: "MENU";
\t\t};
\t}

\tfunction makeMenuPlate(width:Int, height:Int, selected:Bool):BitmapData
\t{
\t\tvar bitmap = new BitmapData(width, height, true, 0x00000000);
\t\tvar shape = new Shape();
\t\tvar borderColor:Int = selected ? 0xFF7600A8 : 0xFF68666D;
\t\tshape.graphics.lineStyle(selected ? 5 : 3, borderColor, 1);
\t\tshape.graphics.beginFill(0xF008080B, 1);
\t\tshape.graphics.moveTo(15, 2);
\t\tshape.graphics.lineTo(width - 3, 2);
\t\tshape.graphics.lineTo(width - 3, height - 4);
\t\tshape.graphics.lineTo(32, height - 4);
\t\tshape.graphics.lineTo(3, 14);
\t\tshape.graphics.lineTo(15, 2);
\t\tshape.graphics.endFill();
\t\tbitmap.draw(shape);

\t\tif (selected)
\t\t{
\t\t\tvar underline = new Shape();
\t\t\tunderline.graphics.beginFill(0xFFFFE52B, 1);
\t\t\tunderline.graphics.drawRect(34, height - 7, width - 34, 9);
\t\t\tunderline.graphics.endFill();
\t\t\tbitmap.draw(underline);
\t\t}
\t\treturn bitmap;
\t}

\tfunction buildReferenceBackdrop():Void
\t{
\t\tvar black = new FlxSprite().makeGraphic(FlxG.width, FlxG.height, 0xFF020204);
\t\tblack.scrollFactor.set(0, 0);
\t\tadd(black);

\t\tvar leftWidth:Int = Std.int(FlxG.width * 0.68);
\t\tvar tiledWidth:Int = leftWidth * 2;
\t\tbackdropTileWidth = leftWidth;
\t\tvar redPixels = new BitmapData(tiledWidth, FlxG.height, false, 0xFF26000A);
\t\tfor (y in 0...FlxG.height)
\t\t{
\t\t\tvar rowWave:Float = Math.sin(y * 0.075) * 21 + Math.sin(y * 0.021) * 13;
\t\t\tfor (x in 0...tiledWidth)
\t\t\t{
\t\t\t\t// Repeat the cloud field twice for a seamless horizontal scroll.
\t\t\t\tvar patternX:Int = x % leftWidth;
\t\t\t\tvar flow:Float = Math.sin((y * 0.061) + Math.sin(patternX * 0.014) * 3.8 + Math.sin(patternX * 0.038) * 1.5);
\t\t\t\tvar ripple:Float = Math.sin((patternX * 0.019) + (y * 0.014)) * 11;
\t\t\t\tvar grain:Float = ((patternX * 17 + y * 29 + ((patternX * y) % 37)) % 23) - 11;
\t\t\t\tvar value:Float = 42 + rowWave + flow * 39 + ripple + grain;
\t\t\t\tvar red:Int = Std.int(Math.max(8, Math.min(176, value * 1.55)));
\t\t\t\tvar green:Int = Std.int(Math.max(0, Math.min(20, value * 0.055)));
\t\t\t\tvar blue:Int = Std.int(Math.max(1, Math.min(30, value * 0.08)));
\t\t\t\tredPixels.setPixel32(x, y, 0xFF000000 | (red << 16) | (green << 8) | blue);
\t\t\t}
\t\t}

\t\tmovingRedBackdrop = new FlxSprite(-leftWidth, 0).loadGraphic(redPixels);
\t\tmovingRedBackdrop.scrollFactor.set(0, 0);
\t\tadd(movingRedBackdrop);

\t\t// Thick red lightning seam creates the sharp zig-zag split in the reference layout.
\t\tvar redSeam = new Shape();
\t\tredSeam.graphics.lineStyle(Math.max(18, FlxG.height * 0.052), 0xFFFF151D, 1);
\t\tredSeam.graphics.moveTo(FlxG.width * 0.395, -12);
\t\tredSeam.graphics.lineTo(FlxG.width * 0.545, FlxG.height * 0.325);
\t\tredSeam.graphics.lineTo(FlxG.width * 0.335, FlxG.height * 0.645);
\t\tredSeam.graphics.lineTo(FlxG.width * 0.585, FlxG.height * 0.895);
\t\tredSeam.graphics.lineTo(FlxG.width * 0.415, FlxG.height + 18);
\t\tvar redSeamBitmap = new BitmapData(FlxG.width, FlxG.height, true, 0x00000000);
\t\tredSeamBitmap.draw(redSeam);
\t\tvar redSeamSprite = new FlxSprite().loadGraphic(redSeamBitmap);
\t\tredSeamSprite.scrollFactor.set(0, 0);
\t\tadd(redSeamSprite);

\t\t// Inner yellow highlight, slightly offset toward the red field.
\t\tvar yellowSeam = new Shape();
\t\tyellowSeam.graphics.lineStyle(Math.max(7, FlxG.height * 0.018), 0xFFFFE51E, 1);
\t\tyellowSeam.graphics.moveTo(FlxG.width * 0.382, -10);
\t\tyellowSeam.graphics.lineTo(FlxG.width * 0.522, FlxG.height * 0.325);
\t\tyellowSeam.graphics.lineTo(FlxG.width * 0.323, FlxG.height * 0.645);
\t\tyellowSeam.graphics.lineTo(FlxG.width * 0.563, FlxG.height * 0.895);
\t\tyellowSeam.graphics.lineTo(FlxG.width * 0.402, FlxG.height + 15);
\t\tvar yellowSeamBitmap = new BitmapData(FlxG.width, FlxG.height, true, 0x00000000);
\t\tyellowSeamBitmap.draw(yellowSeam);
\t\tvar yellowSeamSprite = new FlxSprite().loadGraphic(yellowSeamBitmap);
\t\tyellowSeamSprite.scrollFactor.set(0, 0);
\t\tadd(yellowSeamSprite);

\t\t// Small original emblem treatment; the source game's logo art is not reused.
\t\tvar emblem = new Shape();
\t\temblem.graphics.lineStyle(5, 0xFF251721, 1);
\t\temblem.graphics.beginFill(0xB814111A, 1);
\t\temblem.graphics.drawCircle(FlxG.width * 0.135, FlxG.height * 0.145, FlxG.height * 0.082);
\t\temblem.graphics.endFill();
\t\tvar emblemBitmap = new BitmapData(Std.int(FlxG.width * 0.28), Std.int(FlxG.height * 0.30), true, 0x00000000);
\t\temblemBitmap.draw(emblem);
\t\tvar emblemSprite = new FlxSprite().loadGraphic(emblemBitmap);
\t\temblemSprite.scrollFactor.set(0, 0);
\t\tadd(emblemSprite);

\t\tvar versus = new FlxText(FlxG.width * 0.075, FlxG.height * 0.085, FlxG.width * 0.12, "VS", Std.int(FlxG.height * 0.045));
\t\tversus.scrollFactor.set(0, 0);
\t\tversus.alignment = CENTER;
\t\tversus.setFormat("VCR OSD Mono", Std.int(FlxG.height * 0.045), 0xFFFFD8E2, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\tadd(versus);

\t\tvar emblemTitle = new FlxText(FlxG.width * 0.035, FlxG.height * 0.17, FlxG.width * 0.20, "SONIC.EXE", Std.int(FlxG.height * 0.043));
\t\temblemTitle.scrollFactor.set(0, 0);
\t\temblemTitle.alignment = CENTER;
\t\temblemTitle.setFormat("VCR OSD Mono", Std.int(FlxG.height * 0.043), FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, 0xFF24111A);
\t\tadd(emblemTitle);
\t}

"""

    source = replace_once(
        source,
        "\tvar selectedSomethin:Bool = false;",
        helper_methods + "\tvar selectedSomethin:Bool = false;",
        "reference backdrop and angled menu helpers",
    )

    source = replace_once(
        source,
        """\toverride function update(elapsed:Float)
\t{
\t\tif (FlxG.sound.music.volume < 0.8)""",
        """\toverride function update(elapsed:Float)
\t{
\t\t// Scroll the repeating red cloud field behind the fixed zig-zag divider.
\t\tif (movingRedBackdrop != null && backdropTileWidth > 0)
\t\t{
\t\t\tbackdropTravel += elapsed * 22;
\t\t\twhile (backdropTravel >= backdropTileWidth)
\t\t\t\tbackdropTravel -= backdropTileWidth;
\t\t\tmovingRedBackdrop.x = -backdropTileWidth + backdropTravel;
\t\t}

\t\tif (FlxG.sound.music.volume < 0.8)""",
        "animate menu background during update",
    )

    # Rebuild menu selection colors and plate treatment whenever the selected row changes.
    source = replace_once(
        source,
        """\tfunction changeItem(huh:Int = 0)
\t{
\t\tFlxG.sound.play(Paths.sound('scrollMenu'));
\t\tmenuItems.members[curSelected].animation.play('idle');
\t\tmenuItems.members[curSelected].updateHitbox();
\t\tmenuItems.members[curSelected].screenCenter(X);

\t\tcurSelected += huh;

\t\tif (curSelected >= menuItems.length)
\t\t\tcurSelected = 0;
\t\tif (curSelected < 0)
\t\t\tcurSelected = menuItems.length - 1;

\t\tmenuItems.members[curSelected].animation.play('selected');
\t\tmenuItems.members[curSelected].centerOffsets();
\t\tmenuItems.members[curSelected].screenCenter(X);

\t\tcamFollow.setPosition(menuItems.members[curSelected].getGraphicMidpoint().x,
\t\t\tmenuItems.members[curSelected].getGraphicMidpoint().y - (menuItems.length > 4 ? menuItems.length * 8 : 0));
\t}""",
        """\tfunction changeItem(huh:Int = 0)
\t{
\t\tFlxG.sound.play(Paths.sound('scrollMenu'));

\t\tcurSelected += huh;
\t\tif (curSelected >= menuItems.length)
\t\t\tcurSelected = 0;
\t\tif (curSelected < 0)
\t\t\tcurSelected = menuItems.length - 1;

\t\tfor (i in 0...menuItems.length)
\t\t{
\t\t\tvar selected:Bool = (i == curSelected);
\t\t\tvar label:FlxText = cast menuItems.members[i];
\t\t\tlabel.color = selected ? FlxColor.WHITE : 0xFF85838A;
\t\t\tlabel.alpha = selected ? 1 : 0.82;
\t\t\tvar plate:FlxSprite = menuPlates.members[i];
\t\t\tplate.loadGraphic(makeMenuPlate(Std.int(plate.width), Std.int(plate.height), selected));
\t\t}

\t\tcamFollow.setPosition(FlxG.width * 0.75, FlxG.height * 0.5);
\t}""",
        "reference menu selection rendering",
    )

    target.write_text(source, encoding="utf-8")
    print(f"Applied screenshot-referenced menu layout to {target}")


if __name__ == "__main__":
    main()
