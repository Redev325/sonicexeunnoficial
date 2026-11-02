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
        "import lime.app.Application;",
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
        "var magenta:FlxSprite;\n\tvar camFollow:FlxObject;\n\tvar menuHighlights:FlxTypedGroup<FlxSprite>;\n\tvar menuPlates:FlxTypedGroup<FlxSprite>;",
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
        "\t\tadd(magenta);\n\n\t\tvar menuLogo:FlxSprite = new FlxSprite(FlxG.width * 0.045, FlxG.height * 0.17);\n\t\tmenuLogo.loadGraphic(Paths.image('sonicexe-logo'));\n\t\tmenuLogo.setGraphicSize(Std.int(FlxG.width * 0.37));\n\t\tmenuLogo.updateHitbox();\n\t\tmenuLogo.antialiasing = ClientPrefs.data.antialiasing;\n\t\tmenuLogo.scrollFactor.set(0, 0);\n\t\tadd(menuLogo);\n\n\t\tmenuHighlights = new FlxTypedGroup<FlxSprite>();\n\t\tadd(menuHighlights);\n\n\t\tmenuPlates = new FlxTypedGroup<FlxSprite>();\n\t\tadd(menuPlates);\n\n\t\tmenuItems = new FlxTypedGroup<FlxSprite>();",
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
\t\tvar buttonWidth:Int = Std.int(FlxG.width * 0.47);
\t\tvar buttonHeight:Int = Std.int(buttonWidth * (322.0 / 1673.0));
\t\tvar labelSize:Int = Std.int(FlxG.height * 0.065);
\t\tfor (i in 0...optionShit.length)
\t\t{
\t\t\tvar buttonY:Int = Std.int(FlxG.height * (0.06 + i * 0.18));

\t\t\tvar highlight:FlxSprite = new FlxSprite(buttonX + 7, buttonY + 9);
\t\t\thighlight.loadGraphic(Paths.image('sonicexe-menu/options/shadow'));\n\t\t\thighlight.antialiasing = false;
\t\t\thighlight.setGraphicSize(buttonWidth - 18, Std.int((buttonWidth - 18) * (324.0 / 1833.0)));
\t\t\thighlight.updateHitbox();
\t\t\thighlight.scrollFactor.set(0, 0);
\t\t\thighlight.visible = (i == curSelected);
\t\t\tmenuHighlights.add(highlight);

\t\t\tvar plate:FlxSprite = new FlxSprite(buttonX, buttonY);
\t\t\tplate.loadGraphic(Paths.image('sonicexe-menu/options/box'));\n\t\t\tplate.antialiasing = false;
\t\t\tplate.setGraphicSize(buttonWidth, buttonHeight);
\t\t\tplate.updateHitbox();
\t\t\tplate.scrollFactor.set(0, 0);
\t\t\tmenuPlates.add(plate);

\t\t\tvar label:FlxText = new FlxText(buttonX + 24, buttonY + 8, buttonWidth - 48, menuLabel(i), labelSize);
\t\t\tlabel.antialiasing = false;
\t\t\tlabel.scrollFactor.set(0, 0);
\t\t\tlabel.setFormat(Paths.font('vcr.ttf'), labelSize, FlxColor.GRAY, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\t\tlabel.y = buttonY + (buttonHeight - label.height) * 0.5 - 2;
\t\t\tmenuItems.add(label);
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
        "psychVer.setFormat(\"VCR OSD Mono\", 10, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);",
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
        "fnfVer.setFormat(\"VCR OSD Mono\", 10, FlxColor.WHITE, LEFT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);",
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

    helper_methods = """\tfunction menuLabel(index:Int):String
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
\t\tif (FlxG.sound.music.volume < 0.8)""",
        "use original looping MP4 menu background",
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
\t\t\tmenuHighlights.members[i].visible = selected;
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
