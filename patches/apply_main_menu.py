#!/usr/bin/env python3
"""Use the original Sonic.EXE menu video, logo, and option sprites in Psych Engine."""

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
        "import lime.app.Application;\nimport flixel.util.FlxTimer;",
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
        "public static var curSelected:Int = 0;",
        "public static var curSelected:Int = 2;",
        "start on the reference's Story Mode selection",
    )

    source = replace_once(
        source,
        "var magenta:FlxSprite;\n\tvar camFollow:FlxObject;",
        "var magenta:FlxSprite;\n\tvar camFollow:FlxObject;\n\tvar menuHighlights:FlxTypedGroup<FlxSprite>;\n\tvar menuPlates:FlxTypedGroup<FlxSprite>;\n\tvar menuHitboxes:FlxTypedGroup<FlxSprite>;\n\tvar lastMouseX:Float = -99999;\n\tvar lastMouseY:Float = -99999;\n\tvar sonicMenuLogo:FlxSprite;\n\tvar sonicMenuLogoBaseY:Float = 0;\n\tvar sonicMenuFloatTime:Float = 0;",
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
        "\t\tFlxG.camera.bgColor = FlxColor.TRANSPARENT;",
        "reference-inspired red and black background",
    )

    source = replace_once(
        source,
        "\t\tadd(magenta);\n\n\t\tmenuItems = new FlxTypedGroup<FlxSprite>();",
        "\t\tadd(magenta);\n\n\t\tsonicMenuLogo = new FlxSprite(FlxG.width * 0.045, FlxG.height * 0.035);\n\t\tsonicMenuLogo.loadGraphic(Paths.image('sonicexe-logo'));\n\t\tsonicMenuLogo.setGraphicSize(Std.int(FlxG.width * 0.14));\n\t\tsonicMenuLogo.updateHitbox();\n\t\tsonicMenuLogo.antialiasing = ClientPrefs.data.antialiasing;\n\t\tsonicMenuLogo.scrollFactor.set(0, 0);\n\t\tsonicMenuLogoBaseY = sonicMenuLogo.y;\n\t\tadd(sonicMenuLogo);\n\n\t\tmenuHighlights = new FlxTypedGroup<FlxSprite>();\n\t\tadd(menuHighlights);\n\n\t\tmenuPlates = new FlxTypedGroup<FlxSprite>();\n\t\tadd(menuPlates);\n\n\t\tmenuItems = new FlxTypedGroup<FlxSprite>();\n\t\tadd(menuItems); // Keep the five English labels visible.\n\t\tmenuHitboxes = new FlxTypedGroup<FlxSprite>();\n\t\tadd(menuHitboxes);",
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
    new_loop = """\t\tvar buttonLeftFactors:Array<Float> = [0.63, 0.545, 0.43, 0.545, 0.63];
\t\tvar buttonWidthFactors:Array<Float> = [0.32, 0.39, 0.47, 0.39, 0.32];
\t\tvar buttonTopFactors:Array<Float> = [0.085, 0.255, 0.455, 0.655, 0.845];
\t\tvar labelSizeFactors:Array<Float> = [0.065, 0.072, 0.078, 0.072, 0.065];

\t\tfor (i in 0...optionShit.length)
\t\t{
\t\t\t// The reference uses a staggered hourglass arrangement instead of a straight column.
\t\t\tvar buttonX:Int = Std.int(FlxG.width * buttonLeftFactors[i]);
\t\t\tvar buttonWidth:Int = Std.int(FlxG.width * buttonWidthFactors[i]);
\t\t\tvar buttonY:Int = Std.int(FlxG.height * buttonTopFactors[i]);
\t\t\tvar buttonHeight:Int = Std.int(buttonWidth * (322.0 / 1673.0));
\t\t\tvar labelSize:Int = Std.int(FlxG.height * labelSizeFactors[i]);

\t\t\t// Match the reference's offset backplate: narrower and shorter than the
\t\t\t// purple frame, shifted right and down so it only shows along those edges.
\t\t\tvar shadowWidth:Int = Std.int(buttonWidth * 0.952);
\t\t\tvar shadowHeight:Int = Std.int(buttonHeight * 0.896);

\t\t\t// Layer 1: original yellow shadow, offset down-right behind the frame.
\t\t\tvar highlight:FlxSprite = new FlxSprite(
\t\t\t\tbuttonX + Std.int(buttonWidth * 0.083),
\t\t\t\tbuttonY + Std.int(buttonHeight * 0.22)
\t\t\t);
\t\t\thighlight.loadGraphic(Paths.image('sonicexe-menu/options/shadow'));
\t\t\thighlight.antialiasing = false;
\t\t\thighlight.setGraphicSize(shadowWidth, shadowHeight);
\t\t\thighlight.updateHitbox();
\t\t\thighlight.scrollFactor.set(0, 0);
\t\t\thighlight.alpha = (i == curSelected) ? 0.95 : 0;
\t\t\tmenuHighlights.add(highlight);

\t\t\t// Layer 2: original menu frame; idle rows are gray and the selected row is purple.
\t\t\tvar plate:FlxSprite = new FlxSprite(buttonX, buttonY);
\t\t\tplate.loadGraphic(Paths.image((i == curSelected) ? 'sonicexe-menu/options/box' : 'sonicexe-menu/options/box-idle'));
\t\t\tplate.antialiasing = false;
\t\t\tplate.setGraphicSize(buttonWidth, buttonHeight);
\t\t\tplate.updateHitbox();
\t\t\tplate.scrollFactor.set(0, 0);
\t\t\tplate.color = FlxColor.WHITE;
\t\t\tmenuPlates.add(plate);

\t\t\t// Layer 3: English pixel-font labels centered in each original frame.
\t\t\tvar label:FlxText = new FlxText(buttonX + 24, buttonY + 8, buttonWidth - 48, menuLabel(i), labelSize);
\t\t\tlabel.antialiasing = false;
\t\t\tlabel.scrollFactor.set(0, 0);
\t\t\tlabel.setFormat(Paths.font('sonichud.ttf'), labelSize, FlxColor.GRAY, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\t\tlabel.color = (i == curSelected) ? FlxColor.WHITE : 0xFF85838A;
\t\t\tlabel.y = buttonY + (buttonHeight - label.height) * 0.5 - 2;
\t\t\tmenuItems.add(label);

\t\t\t// Layer 4: original invisible hitbox sprite.
\t\t\tvar hitbox:FlxSprite = new FlxSprite();
\t\t\thitbox.loadGraphic(Paths.image('sonicexe-menu/options/hitbox'));
\t\t\thitbox.antialiasing = false;
\t\t\thitbox.setGraphicSize(
\t\t\t\tStd.int(buttonWidth * (1478.0 / 1673.0)),
\t\t\t\tStd.int(buttonHeight * (231.0 / 322.0))
\t\t\t);
\t\t\thitbox.updateHitbox();
\t\t\thitbox.x = buttonX + (buttonWidth - hitbox.width) * 0.5;
\t\t\thitbox.y = buttonY + (buttonHeight - hitbox.height) * 0.5;
\t\t\thitbox.alpha = 0;
\t\t\thitbox.scrollFactor.set(0, 0);
\t\t\tmenuHitboxes.add(hitbox);
\t\t}"""
    source = replace_once(source, old_loop, new_loop, "replace standard icon row with angled pixel menu")

    # The game version labels are moved to the upper-left to stay out of the menu list.
    source = replace_once(
        source,
        "var psychVer:FlxText = new FlxText(12, FlxG.height - 44, 0, \"Psych Engine v\" + psychEngineVersion, 12);",
        "var psychVer:FlxText = new FlxText(12, FlxG.height - 32, 0, \"Psych Engine v\" + psychEngineVersion, 10);",
        "upper-left engine version label",
    )
    source = replace_once(
        source,
        "psychVer.setFormat(\"VCR OSD Mono\", 16, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);",
        "psychVer.setFormat(Paths.font('sonichud.ttf'), 10, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);",
        "small engine version text",
    )
    source = replace_once(
        source,
        "var fnfVer:FlxText = new FlxText(12, FlxG.height - 24, 0, \"Friday Night Funkin' v\" + Application.current.meta.get('version'), 12);",
        "var fnfVer:FlxText = new FlxText(12, FlxG.height - 18, 0, \"Friday Night Funkin' v\" + Application.current.meta.get('version'), 10);",
        "upper-left game version label",
    )
    source = replace_once(
        source,
        "fnfVer.setFormat(\"VCR OSD Mono\", 16, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);",
        "fnfVer.setFormat(Paths.font('sonichud.ttf'), 10, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);",
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

    source = replace_once(
        source,
        "case 'options':\n\t\t\t\t\t\t\t\tMusicBeatState.switchState(new OptionsState());",
        "case 'options':\n\t\t\t\t\t\t\t\tMusicBeatState.switchState(new SonicEXESettingsState());",
        "open the original Sonic.EXE settings hub",
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
\t\t\t\t\t\t});
\t\t\t\t\t\tFlxTween.tween(menuHighlights.members[i], {alpha: 0}, 0.4, {
\t\t\t\t\t\t\tease: FlxEase.quadOut,
\t\t\t\t\t\t\tonComplete: function(twn:FlxTween)
\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\tmenuHighlights.members[i].kill();
\t\t\t\t\t\t\t}
\t\t\t\t\t\t});""",
        "fade original menu option sprites on transition",
    )

    helper_methods = """\tfunction flashSelectedButton():Void
\t{
\t\tvar label:FlxText = cast menuItems.members[curSelected];
\t\tvar plate:FlxSprite = menuPlates.members[curSelected];
\t\tvar shadow:FlxSprite = menuHighlights.members[curSelected];
\t\tvar flashes:Int = 0;
\t\tnew FlxTimer().start(0.075, function(timer:FlxTimer)
\t\t{
\t\t\tvar redFlash:Bool = (flashes % 2 == 0);
\t\t\tlabel.color = redFlash ? 0xFFFF2929 : FlxColor.WHITE;
\t\t\tplate.alpha = redFlash ? 0.28 : 1;
\t\t\tshadow.alpha = redFlash ? 0.18 : 0.95;
\t\t\tflashes++;
\t\t\tif (flashes >= 12)
\t\t\t{
\t\t\t\tlabel.color = FlxColor.WHITE;
\t\t\t\tplate.alpha = 1;
\t\t\t\tshadow.alpha = 0.95;
\t\t\t}
\t\t}, 12);
\t}

\tfunction beginSonicConfirmWipe():Void
\t{
\t\tvar darken:FlxSprite = new FlxSprite().makeGraphic(FlxG.width, FlxG.height, FlxColor.BLACK);
\t\tdarken.scrollFactor.set(0, 0);
\t\tdarken.alpha = 0;
\t\tadd(darken);

\t\tvar sonicWipe:FlxSprite = new FlxSprite();
\t\tsonicWipe.loadGraphic(Paths.image('sonicexe-transitions/sanic-red'));
\t\tsonicWipe.setGraphicSize(Std.int(FlxG.width * 0.18), Std.int(FlxG.height * 0.18));
\t\tsonicWipe.updateHitbox();
\t\tsonicWipe.screenCenter();
\t\tsonicWipe.scrollFactor.set(0, 0);
\t\tsonicWipe.alpha = 0;
\t\tadd(sonicWipe);

\t\tvar targetScaleX:Float = sonicWipe.scale.x * 6.4;
\t\tvar targetScaleY:Float = sonicWipe.scale.y * 6.4;
\t\tFlxTween.tween(sonicWipe, {alpha: 1}, 0.12, {ease: FlxEase.quadOut});
\t\tFlxTween.tween(sonicWipe.scale, {x: targetScaleX, y: targetScaleY}, 0.78, {ease: FlxEase.quadIn});
\t\tFlxTween.tween(darken, {alpha: 1}, 0.34, {startDelay: 0.48, ease: FlxEase.quadIn});
\t}

\tfunction menuLabel(index:Int):String
\t{
\t\treturn switch (index)
\t\t{
\t\t\tcase 0: "SOUND TEST";
\t\t\tcase 1: "FREEPLAY";
\t\t\tcase 2: "STORY MODE";
\t\t\tcase 3: "EXTRAS";
\t\t\tcase 4: "OPTIONS";
\t\t\tdefault: "MENU";
\t\t};
\t}

\tfunction setMenuBackdropVisible(visible:Bool):Void
\t{
\t\t#if js
\t\tvar browserWindow:Dynamic = js.Browser.window;
\t\tvar callback:Dynamic = Reflect.field(browserWindow, "setSonicEXEMenuVideo");
\t\tif (callback != null)
\t\t\tReflect.callMethod(browserWindow, callback, [visible]);
\t\t#end
\t}
"""

    source = replace_once(
        source,
        "\tvar selectedSomethin:Bool = false;",
        helper_methods + "\tvar selectedSomethin:Bool = false;",
        "insert original menu label and video helpers",
    )

    source = replace_once(
        source,
        """\toverride function update(elapsed:Float)
\t{
\t\tif (FlxG.sound.music.volume < 0.8)""",
        """\toverride function update(elapsed:Float)
\t{
\t\tif (sonicMenuLogo != null)
\t\t{
\t\t\tsonicMenuFloatTime += elapsed;
\t\t\tsonicMenuLogo.y = sonicMenuLogoBaseY + Math.sin(sonicMenuFloatTime * 1.6) * 9;
\t\t}
\t\tif (FlxG.sound.music.volume < 0.8)""",
        "use original looping MP4 menu background",
    )

    source = replace_once(
        source,
        """\t\tif (!selectedSomethin)
\t\t{
\t\t\tif (controls.UI_UP_P)""",
        """\t\tif (!selectedSomethin)
\t\t{
\t\t\tvar mouseAccept:Bool = false;
\t\t\tvar mouseMoved:Bool = (FlxG.mouse.x != lastMouseX || FlxG.mouse.y != lastMouseY);

\t\t\t// Only let hover change selection when the pointer actually moves.
\t\t\t// A stationary cursor must not fight keyboard navigation.
\t\t\tif (mouseMoved)
\t\t\t{
\t\t\t\tlastMouseX = FlxG.mouse.x;
\t\t\t\tlastMouseY = FlxG.mouse.y;
\t\t\t\tfor (i in 0...menuHitboxes.length)
\t\t\t\t{
\t\t\t\t\tif (FlxG.mouse.overlaps(menuHitboxes.members[i], FlxG.camera))
\t\t\t\t\t{
\t\t\t\t\t\tif (i != curSelected)
\t\t\t\t\t\t\tchangeItem(i - curSelected);
\t\t\t\t\t\tbreak;
\t\t\t\t\t}
\t\t\t\t}
\t\t\t}

\t\t\t// A click is checked independently so it works without pointer movement.
\t\t\tif (FlxG.mouse.justPressed)
\t\t\t{
\t\t\t\tfor (i in 0...menuHitboxes.length)
\t\t\t\t{
\t\t\t\t\tif (FlxG.mouse.overlaps(menuHitboxes.members[i], FlxG.camera))
\t\t\t\t\t{
\t\t\t\t\t\tif (i != curSelected)
\t\t\t\t\t\t\tchangeItem(i - curSelected);
\t\t\t\t\t\tmouseAccept = true;
\t\t\t\t\t\tbreak;
\t\t\t\t\t}
\t\t\t\t}
\t\t\t}

\t\t\tif (controls.UI_UP_P)""",
        "wire original hitboxes to hover and click input",
    )

    source = replace_once(
        source,
        "if (controls.ACCEPT)",
        "if (controls.ACCEPT || mouseAccept)",
        "allow mouse clicks on original menu hitboxes",
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

\t\tcurSelected = (curSelected + huh) % menuItems.length;
\t\tif (curSelected < 0)
\t\t\tcurSelected += menuItems.length;

\t\tfor (i in 0...menuItems.length)
\t\t{
\t\t\tvar selected:Bool = (i == curSelected);
\t\t\tvar label:FlxText = cast menuItems.members[i];
\t\t\tlabel.color = selected ? FlxColor.WHITE : 0xFF85838A;
\t\t\tlabel.alpha = selected ? 1 : 0.82;
\t\t\tvar plate:FlxSprite = menuPlates.members[i];
\t\t\tplate.loadGraphic(Paths.image(selected ? 'sonicexe-menu/options/box' : 'sonicexe-menu/options/box-idle'));
\t\t\tplate.color = FlxColor.WHITE;
\t\t\tmenuPlates.members[i].color = selected ? 0xFF7D00B5 : 0xFF85838A;
\t\t\tvar shadow:FlxSprite = menuHighlights.members[i];\n\t\t\tFlxTween.cancelTweensOf(shadow);\n\t\t\tFlxTween.tween(shadow, {alpha: selected ? 0.95 : 0}, 0.14, {ease: FlxEase.quadOut});
\t\t}

\t\tcamFollow.setPosition(FlxG.width * 0.75, FlxG.height * 0.5);
\t}""",
        "update selection using original yellow sprite",
    )



    source = replace_once(
        source,
        """\t\t\tif (controls.BACK)
\t\t\t{
\t\t\t\tselectedSomethin = true;
\t\t\t\tFlxG.sound.play(Paths.sound('cancelMenu'));""",
        """\t\t\tif (controls.BACK)
\t\t\t{
\t\t\t\tselectedSomethin = true;
\t\t\t\tsetMenuBackdropVisible(false);
\t\t\t\tFlxG.sound.play(Paths.sound('cancelMenu'));""",
        "hide menu video when returning to title screen",
    )

    source = replace_once(
        source,
        """\t\t\t\telse
\t\t\t\t{
\t\t\t\t\tselectedSomethin = true;
\t\t\t\t\tsetMenuBackdropVisible(false);
\t\t\t\t\tflashSelectedButton();
\t\t\t\t\tbeginSonicConfirmWipe();

\t\t\t\t\tif (ClientPrefs.data.flashing)""",
        """\t\t\t\telse
\t\t\t\t{
\t\t\t\t\tselectedSomethin = true;
\t\t\t\t\tsetMenuBackdropVisible(false);

\t\t\t\t\tif (ClientPrefs.data.flashing)""",
        "hide menu video when opening another menu",
    )

    source = replace_once(
        source,
        """\t\tsuper.create();

\t\tFlxG.camera.follow(camFollow, null, 9);""",
        """\t\tsuper.create();
\t\tFlxG.camera.bgColor = FlxColor.TRANSPARENT;
\t\tsetMenuBackdropVisible(true);

\t\tFlxG.camera.follow(camFollow, null, 9);""",
        "show original menu video behind transparent canvas",
    )

    target.write_text(source, encoding="utf-8")
    print(f"Applied screenshot-referenced menu layout to {target}")


if __name__ == "__main__":
    main()
