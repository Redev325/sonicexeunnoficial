#!/usr/bin/env python3
"""Install the original Sonic.EXE warning, intro movie, and layered V3 title screen."""

from pathlib import Path
import sys


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"TitleState patch stopped: expected one match for {label}, found {count}")
    return source.replace(old, new)


def replace_function(source: str, signature: str, next_signature: str, replacement: str, label: str) -> str:
    start = source.find(signature)
    end = source.find(next_signature, start + len(signature))
    if start < 0 or end < 0:
        raise SystemExit(f"TitleState patch stopped: could not locate {label}")
    return source[:start] + replacement + source[end:]


def patch_title_state(source: str) -> str:
    source = replace_once(
        source,
        "var swagShader:ColorSwap = null;",
        "var swagShader:ColorSwap = null;\n"
        "\tvar postIntroGroup:FlxGroup;\n"
        "\tvar postIntroPlaying:Bool = false;\n"
        "\tvar warningGroup:FlxGroup;\n"
        "\tvar warningPrompt:FlxText;\n"
        "\tvar warningActive:Bool = false;\n"
        "\tvar warningPulseTime:Float = 0;\n"
        "\tvar sonicTitleLogo:FlxSprite;\n"
        "\tvar sonicLogoBaseY:Float = 0;\n"
        "\tvar sonicLogoFloatTime:Float = 0;",
        "title warning and layered emblem state fields",
    )

    start_intro = """\tfunction startIntro()
\t{
\t\t// The reference opens with a content warning before the original intro movie.
\t\tpersistentUpdate = true;
\t\tConductor.bpm = 102;
\t\tif (FlxG.sound.music != null)
\t\t\tFlxG.sound.music.stop();

\t\tvar black:FlxSprite = new FlxSprite().makeGraphic(FlxG.width, FlxG.height, FlxColor.BLACK);
\t\tblack.scrollFactor.set(0, 0);
\t\tadd(black);

\t\tlogoBl = null;
\t\tgfDance = null;
\t\tpostIntroGroup = new FlxGroup();

\t\t// Use the original release's complete VS SONIC.EXE emblem as one sprite.
		// The source artwork already contains the ring, eyes, wings, wordmark, and ribbon.
		sonicTitleLogo = new FlxSprite();
		sonicTitleLogo.loadGraphic(Paths.image('sonicexe-logo'));
		sonicTitleLogo.setGraphicSize(Std.int(FlxG.width * 0.56));
		sonicTitleLogo.updateHitbox();
		sonicTitleLogo.x = (FlxG.width - sonicTitleLogo.width) * 0.5;
		sonicTitleLogo.y = FlxG.height * 0.155;
		sonicTitleLogo.antialiasing = ClientPrefs.data.antialiasing;
		sonicTitleLogo.scrollFactor.set(0, 0);
		postIntroGroup.add(sonicTitleLogo);

		// This atlas supplies the pulsing white/yellow Enter prompt and its pressed animation.
\t\ttitleText = new FlxSprite(0, 0);
\t\ttitleText.frames = Paths.getSparrowAtlas('sonicexe-title/titleEnterNEW');
\t\ttitleText.animation.addByPrefix('idle', 'Press Enter to Begin instance', 24, true);
\t\ttitleText.animation.addByPrefix('press', 'ENTER PRESSED instance', 24, false);
\t\ttitleText.animation.play('idle');
\t\ttitleText.antialiasing = false;
\t\ttitleText.scrollFactor.set(0, 0);
\t\tvar titlePromptScale:Float = Math.min(FlxG.width / 1280, FlxG.height / 720);
\t\ttitleText.scale.set(titlePromptScale, titlePromptScale);
		titleText.updateHitbox();
		// Atlas frames are trimmed but retain a 1280x720 source canvas. Position
		// that full canvas, not the cropped text rectangle, so the prompt stays low.
		titleText.x = (FlxG.width - 1280 * titlePromptScale) * 0.5;
		titleText.y = (FlxG.height - 720 * titlePromptScale) * 0.5;
\t\tpostIntroGroup.add(titleText);

\t\tsonicLogoBaseY = sonicTitleLogo.y;
\t\tpostIntroGroup.visible = false;
\t\tadd(postIntroGroup);
\t\tnewTitle = true;

\t\t// English warning screen shown before the cutscene.
\t\twarningGroup = new FlxGroup();
\t\tvar warningHeading:FlxText = new FlxText(FlxG.width * 0.12, FlxG.height * 0.19, FlxG.width * 0.76, 'WELCOME.', Std.int(FlxG.height * 0.035));
\t\twarningHeading.setFormat(Paths.font('vcr.ttf'), Std.int(FlxG.height * 0.035), FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\twarningHeading.scrollFactor.set(0, 0);
\t\twarningGroup.add(warningHeading);

\t\tvar warningBodyText:String = 'BEFORE YOU CONTINUE, BE AWARE THAT THIS MOD CONTAINS FLASHING LIGHTS.\\n\\nIF YOU FEEL UNCOMFORTABLE OR TRIGGERED BY THESE EFFECTS, DO NOT PLAY THIS MOD.\\n\\nVIEWER DISCRETION IS ADVISED.';
\t\tvar warningBody:FlxText = new FlxText(FlxG.width * 0.12, FlxG.height * 0.30, FlxG.width * 0.76, warningBodyText, Std.int(FlxG.height * 0.029));
\t\twarningBody.setFormat(Paths.font('vcr.ttf'), Std.int(FlxG.height * 0.029), FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\twarningBody.scrollFactor.set(0, 0);
\t\twarningGroup.add(warningBody);

\t\twarningPrompt = new FlxText(0, FlxG.height * 0.84, FlxG.width, 'PRESS ENTER TO CONTINUE.', Std.int(FlxG.height * 0.032));
\t\twarningPrompt.setFormat(Paths.font('vcr.ttf'), Std.int(FlxG.height * 0.032), FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
\t\twarningPrompt.scrollFactor.set(0, 0);
\t\twarningGroup.add(warningPrompt);
\t\tadd(warningGroup);

\t\tcredGroup = new FlxGroup();
\t\ttextGroup = new FlxGroup();
\t\tinitialized = true;
\t\tskippedIntro = false;
\t\tclosedState = true;
\t\twarningActive = true;
\t\twarningPulseTime = 0;
\t\tpostIntroPlaying = false;

\t\tsetMenuBackdropVisible(false);
\t\tsetTitleBackdropVisible(false);
\t\tsetPostIntroVideoVisible(false);
\t\tPaths.clearUnusedMemory();
\t}

\tfunction beginPostIntro():Void
\t{
\t\twarningActive = false;
\t\tif (warningGroup != null)
\t\t\twarningGroup.visible = false;
\t\tpostIntroPlaying = true;
\t\tsetTitleBackdropVisible(false);
\t\tsetPostIntroVideoVisible(true);
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

\tfunction setTitleBackdropVisible(visible:Bool):Void
\t{
\t\t#if js
\t\tvar browserWindow:Dynamic = js.Browser.window;
\t\tvar callback:Dynamic = Reflect.field(browserWindow, "setSonicEXETitleVideo");
\t\tif (callback != null)
\t\t\tReflect.callMethod(browserWindow, callback, [visible]);
\t\t#end
\t}

\tfunction setPostIntroVideoVisible(visible:Bool):Void
\t{
\t\t#if js
\t\tvar browserWindow:Dynamic = js.Browser.window;
\t\tvar callback:Dynamic = Reflect.field(browserWindow, "setSonicEXEPostIntro");
\t\tif (callback != null)
\t\t\tReflect.callMethod(browserWindow, callback, [visible]);
\t\t#end
\t}

\tfunction postIntroVideoFinished():Bool
\t{
\t\t#if js
\t\tvar browserWindow:Dynamic = js.Browser.window;
\t\treturn Reflect.field(browserWindow, "sonicEXEPostIntroFinished") == true;
\t\t#else
\t\treturn true;
\t\t#end
\t}

\tfunction postIntro():Void
\t{
\t\tif (!postIntroPlaying)
\t\t\treturn;

\t\tpostIntroPlaying = false;
\t\tsetPostIntroVideoVisible(false);
\t\tsetTitleBackdropVisible(true);
\t\tif (postIntroGroup != null)
\t\t\tpostIntroGroup.visible = true;

\t\tskippedIntro = true;
\t\tclosedState = true;
\t\tFlxG.sound.playMusic(Paths.music('menu'), 0);
\t\tif (FlxG.sound.music != null)
\t\t\tFlxG.sound.music.fadeIn(1.2, 0, 0.7);
\t}
"""
    source = replace_function(
        source,
        "\tfunction startIntro()",
        "\n\tfunction getIntroTextShit()",
        start_intro,
        "startIntro",
    )

    title_update = """\t\tif (warningActive)
\t\t{
\t\t\twarningPulseTime += elapsed;
\t\t\tif (warningPrompt != null)
\t\t\t\twarningPrompt.alpha = 0.58 + Math.sin(warningPulseTime * 3.2) * 0.42;
\t\t\tif (pressedEnter)
\t\t\t{
\t\t\t\tFlxG.sound.play(Paths.sound('sonic'));
\t\t\t\tbeginPostIntro();
\t\t\t}
\t\t\tsuper.update(elapsed);
\t\t\treturn;
\t\t}

\t\tif (postIntroPlaying)
\t\t{
\t\t\tif (postIntroVideoFinished() || pressedEnter)
\t\t\t\tpostIntro();
\t\t\tsuper.update(elapsed);
\t\t\treturn;
\t\t}

\t\tif (sonicTitleLogo != null && postIntroGroup != null && postIntroGroup.visible)
		{
			sonicLogoFloatTime += elapsed;
			sonicTitleLogo.y = sonicLogoBaseY + Math.sin(sonicLogoFloatTime * 1.6) * 10;
		}

"""
    source = replace_once(
        source,
        "\t\tif (newTitle) {",
        title_update + "\t\tif (newTitle) {",
        "warning, intro, and layered logo update sequence",
    )

    # The intro movie supplies the opening scene. The title background video
    # is enabled only when the movie ends and the real title card appears.
    beat_start = source.find("\toverride function beatHit()")
    beat_end = source.find("\n\tvar skippedIntro:Bool", beat_start)
    if beat_start < 0 or beat_end < 0:
        raise SystemExit("TitleState patch stopped: could not locate beatHit")
    source = source[:beat_start] + "\toverride function beatHit()\n\t{\n\t\tsuper.beatHit();\n\t}\n" + source[beat_end:]
    source = replace_once(
        source,
        "FlxG.sound.play(Paths.sound('confirmMenu'), 0.7);",
        "FlxG.sound.play(Paths.sound('menulaugh'), 1.0);",
        "play the original Sonic.EXE menu laugh on Enter",
    )
    return source


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: apply_title_screen.py path/to/TitleState.hx")
    target = Path(sys.argv[1])
    if not target.is_file():
        raise SystemExit(f"TitleState source file not found: {target}")
    original = target.read_text(encoding="utf-8")
    patched = patch_title_state(original)
    if patched == original:
        raise SystemExit("TitleState was not changed.")
    target.write_text(patched, encoding="utf-8")
    print("Installed the original Sonic.EXE warning, intro movie, layered title emblem, and animated Enter prompt.")


if __name__ == "__main__":
    main()
