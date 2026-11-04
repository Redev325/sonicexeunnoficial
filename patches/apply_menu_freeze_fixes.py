#!/usr/bin/env python3
from pathlib import Path
import sys

def replace_once(source, old, new, label):
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"HTML5 menu optimization stopped: {label} expected once, found {count}")
    return source.replace(old, new)

def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: apply_menu_freeze_fixes.py FreeplayState.hx StoryMenuState.hx")
    freeplay = Path(sys.argv[1])
    source = freeplay.read_text(encoding="utf-8")
    source = replace_once(source,
        "\t\t\tMods.currentModDirectory = songs[i].folder;\n\t\t\tvar icon:HealthIcon = new HealthIcon(songs[i].songCharacter);\n\t\t\ticon.sprTracker = songText;\n\n\t\t\t\n\t\t\t// too laggy with a lot of songs, so i had to recode the logic for it\n\t\t\tsongText.visible = songText.active = songText.isMenuItem = false;\n\t\t\ticon.visible = icon.active = false;\n\n\t\t\t// using a FlxGroup is too much fuss!\n\t\t\ticonArray.push(icon);\n\t\t\tadd(icon);",
        "\t\t\t// Decode health icons only when their rows enter the visible window.\n\t\t\tsongText.visible = songText.active = songText.isMenuItem = false;\n\t\t\ticonArray.push(null);",
        "eager Freeplay health-icon construction")
    source = replace_once(source, "\t\t\ticonArray[i].alpha = 0.6;",
        "\t\t\tif (iconArray[i] != null) iconArray[i].alpha = 0.6;", "null-safe icon alpha")
    source = replace_once(source, "\t\ticonArray[curSelected].alpha = 1;",
        "\t\tif (iconArray[curSelected] != null) iconArray[curSelected].alpha = 1;", "null-safe selected icon")
    source = replace_once(source, "\t\t\ticonArray[i].visible = iconArray[i].active = false;",
        "\t\t\tif (iconArray[i] != null) iconArray[i].visible = iconArray[i].active = false;", "null-safe icon hiding")
    source = replace_once(source,
        "\t\t\tvar icon:HealthIcon = iconArray[i];\n\t\t\ticon.visible = icon.active = true;",
        "\t\t\tvar icon:HealthIcon = iconArray[i];\n\t\t\tif (icon == null)\n\t\t\t{\n\t\t\t\tMods.currentModDirectory = songs[i].folder;\n\t\t\t\ticon = new HealthIcon(songs[i].songCharacter);\n\t\t\t\ticon.sprTracker = item;\n\t\t\t\ticonArray[i] = icon;\n\t\t\t\tadd(icon);\n\t\t\t}\n\t\t\ticon.visible = icon.active = true;\n\t\t\ticon.alpha = (i == curSelected) ? 1 : 0.6;",
        "lazy creation for visible Freeplay icons")
    freeplay.write_text(source, encoding="utf-8")

    story = Path(sys.argv[2])
    source = story.read_text(encoding="utf-8")
    source = replace_once(source, "\t\tPaths.clearStoredMemory();\n\t\tPaths.clearUnusedMemory();",
        "\t\t#if !html5\n\t\tPaths.clearStoredMemory();\n\t\tPaths.clearUnusedMemory();\n\t\t#end",
        "Story Mode synchronous memory purge")
    story.write_text(source, encoding="utf-8")
    print("Applied lazy Freeplay icon decoding and skipped Story Mode cache purges on HTML5.")

if __name__ == "__main__":
    main()
