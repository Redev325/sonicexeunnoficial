#!/usr/bin/env python3
"""Replace the generic Psych title card with the game's original Sonic.EXE title artwork."""

from pathlib import Path
import sys


def replace_visuals(source: str) -> str:
    start_marker = "\t\tvar bg:FlxSprite = new FlxSprite();"
    end_marker = "\t\tcredGroup = new FlxGroup();"
    start = source.find(start_marker, source.find("function startIntro()"))
    end = source.find(end_marker, start)
    if start < 0 or end < 0:
        raise SystemExit("TitleState patch stopped: could not locate the original title artwork block.")

    replacement = """\t\t// The original Sonic.EXE title screen is assembled from the supplied game layers.
\t\tvar bg:FlxSprite = new FlxSprite().makeGraphic(FlxG.width, FlxG.height, FlxColor.BLACK);
\t\tbg.scrollFactor.set(0, 0);
\t\tadd(bg);

\t\tlogoBl = null;
\t\tgfDance = null;

\t\tvar ring:FlxSprite = new FlxSprite().loadGraphic(Paths.image('sonicexe-title/logo/ring'));
\t\tring.setGraphicSize(Std.int(FlxG.width * 0.62));
\t\tring.updateHitbox();
\t\tring.x = (FlxG.width - ring.width) * 0.5;
\t\tring.y = FlxG.height * 0.055;
\t\tring.antialiasing = ClientPrefs.data.antialiasing;
\t\tring.scrollFactor.set(0, 0);
\t\tadd(ring);

\t\tvar eyes:FlxSprite = new FlxSprite().loadGraphic(Paths.image('sonicexe-title/logo/eyes'));
\t\teyes.setGraphicSize(Std.int(FlxG.width * 0.19));
\t\teyes.updateHitbox();
\t\teyes.x = (FlxG.width - eyes.width) * 0.5;
\t\teyes.y = FlxG.height * 0.255;
\t\teyes.antialiasing = ClientPrefs.data.antialiasing;
\t\teyes.scrollFactor.set(0, 0);
\t\tadd(eyes);

\t\tvar bandana:FlxSprite = new FlxSprite().loadGraphic(Paths.image('sonicexe-title/logo/bandana'));
\t\tbandana.setGraphicSize(Std.int(FlxG.width * 0.56));
\t\tbandana.updateHitbox();
\t\tbandana.x = (FlxG.width - bandana.width) * 0.5;
\t\tbandana.y = FlxG.height * 0.49;
\t\tbandana.antialiasing = ClientPrefs.data.antialiasing;
\t\tbandana.scrollFactor.set(0, 0);
\t\tadd(bandana);

\t\tvar sonicLogo:FlxSprite = new FlxSprite().loadGraphic(Paths.image('sonicexe-title/logo/sonic'));
\t\tsonicLogo.setGraphicSize(Std.int(FlxG.width * 0.51));
\t\tsonicLogo.updateHitbox();
\t\tsonicLogo.x = (FlxG.width - sonicLogo.width) * 0.5;
\t\tsonicLogo.y = FlxG.height * 0.36;
\t\tsonicLogo.antialiasing = ClientPrefs.data.antialiasing;
\t\tsonicLogo.scrollFactor.set(0, 0);
\t\tadd(sonicLogo);

\t\tvar spikes:FlxSprite = new FlxSprite().loadGraphic(Paths.image('sonicexe-title/spikesdown'));
\t\tspikes.setGraphicSize(FlxG.width);
\t\tspikes.updateHitbox();
\t\tspikes.x = 0;
\t\tspikes.y = 0;
\t\tspikes.scrollFactor.set(0, 0);
\t\tadd(spikes);

\t\t// This is the original 11-frame "Press Enter to Begin" animation atlas.
\t\ttitleText = new FlxSprite(0, 0);
\t\ttitleText.frames = Paths.getSparrowAtlas('sonicexe-title/titleEnterNEW');
\t\ttitleText.animation.addByPrefix('idle', 'Press Enter to Begin instance', 24, true);
\t\ttitleText.animation.addByPrefix('press', 'ENTER PRESSED instance', 24, false);
\t\ttitleText.animation.play('idle');
\t\ttitleText.antialiasing = false;
\t\ttitleText.scrollFactor.set(0, 0);
\t\ttitleText.setGraphicSize(FlxG.width, FlxG.height);
\t\ttitleText.updateHitbox();
\t\tadd(titleText);
\t\tnewTitle = true;
\t\t
"""
    return source[:start] + replacement + source[end:]


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: apply_title_screen.py path/to/TitleState.hx")
    target = Path(sys.argv[1])
    if not target.is_file():
        raise SystemExit(f"TitleState source file not found: {target}")
    original = target.read_text(encoding="utf-8")
    patched = replace_visuals(original)
    if patched == original:
        raise SystemExit("TitleState was not changed.")
    target.write_text(patched, encoding="utf-8")
    print(f"Applied original Sonic.EXE title artwork to {target}")


if __name__ == "__main__":
    main()
