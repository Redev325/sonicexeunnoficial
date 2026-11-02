#!/usr/bin/env python3
"""Install the original Sonic.EXE post-intro video and title card in Psych Engine."""

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
        "\tvar postIntroPlaying:Bool = false;",
        "postIntro state fields",
    )

    start_intro = """\tfunction startIntro()
\t{
\t\t// The game's own postIntro movie plays first; the original title card is revealed afterward.
\t\tpersistentUpdate = true;
\t\tConductor.bpm = 102;
\t\tif (FlxG.sound.music != null)
\t\t\tFlxG.sound.music.stop();

\t\tvar bg:FlxSprite = new FlxSprite().makeGraphic(FlxG.width, FlxG.height, FlxColor.BLACK);
\t\tbg.scrollFactor.set(0, 0);
\t\tadd(bg);

\t\tlogoBl = null;
\t\tgfDance = null;
\t\tpostIntroGroup = new FlxGroup();

\t\tvar ring:FlxSprite = new FlxSprite().loadGraphic(Paths.image('sonicexe-title/logo/ring'));
\t\tring.setGraphicSize(Std.int(FlxG.width * 0.62));
\t\tring.updateHitbox();
\t\tring.x = (FlxG.width - ring.width) * 0.5;
\t\tring.y = FlxG.height * 0.055;
\t\tring.antialiasing = ClientPrefs.data.antialiasing;
\t\tring.scrollFactor.set(0, 0);
\t\tpostIntroGroup.add(ring);

\t\tvar eyes:FlxSprite = new FlxSprite().loadGraphic(Paths.image('sonicexe-title/logo/eyes'));
\t\teyes.setGraphicSize(Std.int(FlxG.width * 0.19));
\t\teyes.updateHitbox();
\t\teyes.x = (FlxG.width - eyes.width) * 0.5;
\t\teyes.y = FlxG.height * 0.255;
\t\teyes.antialiasing = ClientPrefs.data.antialiasing;
\t\teyes.scrollFactor.set(0, 0);
\t\tpostIntroGroup.add(eyes);

\t\tvar bandana:FlxSprite = new FlxSprite().loadGraphic(Paths.image('sonicexe-title/logo/bandana'));
\t\tbandana.setGraphicSize(Std.int(FlxG.width * 0.56));
\t\tbandana.updateHitbox();
\t\tbandana.x = (FlxG.width - bandana.width) * 0.5;
\t\tbandana.y = FlxG.height * 0.49;
\t\tbandana.antialiasing = ClientPrefs.data.antialiasing;
\t\tbandana.scrollFactor.set(0, 0);
\t\tpostIntroGroup.add(bandana);

\t\tvar sonicLogo:FlxSprite = new FlxSprite().loadGraphic(Paths.image('sonicexe-title/logo/sonic'));
\t\tsonicLogo.setGraphicSize(Std.int(FlxG.width * 0.51));
\t\tsonicLogo.updateHitbox();
\t\tsonicLogo.x = (FlxG.width - sonicLogo.width) * 0.5;
\t\tsonicLogo.y = FlxG.height * 0.36;
\t\tsonicLogo.antialiasing = ClientPrefs.data.antialiasing;
\t\tsonicLogo.scrollFactor.set(0, 0);
\t\tpostIntroGroup.add(sonicLogo);

\t\tvar spikes:FlxSprite = new FlxSprite().loadGraphic(Paths.image('sonicexe-title/spikesdown'));
\t\tspikes.setGraphicSize(FlxG.width);
\t\tspikes.updateHitbox();
\t\tspikes.x = 0;
\t\tspikes.y = 0;
\t\tspikes.scrollFactor.set(0, 0);
\t\tpostIntroGroup.add(spikes);

\t\t// The original 1280x720 atlas already includes the prompt's placement.
\t\ttitleText = new FlxSprite(0, 0);
\t\ttitleText.frames = Paths.getSparrowAtlas('sonicexe-title/titleEnterNEW');
\t\ttitleText.animation.addByPrefix('idle', 'Press Enter to Begin instance', 24, true);
\t\ttitleText.animation.addByPrefix('press', 'ENTER PRESSED instance', 24, false);
\t\ttitleText.animation.play('idle');
\t\ttitleText.antialiasing = false;
\t\ttitleText.scrollFactor.set(0, 0);
\t\ttitleText.setGraphicSize(FlxG.width, FlxG.height);
\t\ttitleText.updateHitbox();
\t\tpostIntroGroup.add(titleText);

\t\tpostIntroGroup.visible = false;
\t\tadd(postIntroGroup);
\t\tnewTitle = true;

\t\tcredGroup = new FlxGroup();
\t\ttextGroup = new FlxGroup();
\t\tinitialized = true;
\t\tskippedIntro = false;
\t\tclosedState = true;
\t\tpostIntroPlaying = true;

\t\tsetMenuBackdropVisible(false);
\t\tsetPostIntroVideoVisible(true);
\t\tPaths.clearUnusedMemory();
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

    post_intro_update = """\t\tif (postIntroPlaying)
\t\t{
\t\t\tif (postIntroVideoFinished() || pressedEnter)
\t\t\t\tpostIntro();

\t\t\tsuper.update(elapsed);
\t\t\treturn;
\t\t}

"""
    source = replace_once(
        source,
        "\t\tif (newTitle) {",
        post_intro_update + "\t\tif (newTitle) {",
        "postIntro video completion and skip handling",
    )

    # The original video's soundtrack is used during the postIntro clip. The
    # normal menu theme begins only after the clip hands off to the title card.
    beat_start = source.find("\toverride function beatHit()")
    beat_end = source.find("\n\tvar skippedIntro:Bool", beat_start)
    if beat_start < 0 or beat_end < 0:
        raise SystemExit("TitleState patch stopped: could not locate beatHit")
    source = (
        source[:beat_start]
        + "\toverride function beatHit()\n\t{\n\t\tsuper.beatHit();\n\t}\n"
        + source[beat_end:]
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
    print("Installed the postIntro video and original Sonic.EXE post-intro title card.")


if __name__ == "__main__":
    main()
