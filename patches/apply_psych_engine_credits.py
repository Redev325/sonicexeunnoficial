#!/usr/bin/env python3
from pathlib import Path
import sys

def once(s,o,n,label):
    if s.count(o)!=1:
        raise SystemExit(f"Psych credits patch stopped: expected one {label}, found {s.count(o)}")
    return s.replace(o,n)

def patch_menu(path):
    s=path.read_text(encoding="utf-8")
    s=once(s,"var sonicMenuFloatTime:Float = 0;",
        "var sonicMenuFloatTime:Float = 0;\n\tvar psychCreditsButton:FlxText;",
        "Psych credits button field")
    s=once(s,
        "var psychVer:FlxText = new FlxText(12, FlxG.height - 32, 0, \"Psych Engine v\" + psychEngineVersion, 10);",
        "psychCreditsButton = new FlxText(FlxG.width - 285, FlxG.height - 42, 270, \"PSYCH ENGINE CREDITS\", 14);\n\t\tpsychCreditsButton.setFormat(Paths.font('sonichud.ttf'), 14, FlxColor.WHITE, RIGHT, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);\n\t\tpsychCreditsButton.scrollFactor.set();\n\t\tadd(psychCreditsButton);\n\t\tvar psychVer:FlxText = new FlxText(12, FlxG.height - 32, 0, \"Psych Engine v\" + psychEngineVersion, 10);",
        "Psych credits button creation")
    s=once(s,
        "var mouseAccept:Bool = false;",
        "if (psychCreditsButton != null && FlxG.mouse.justPressed && FlxG.mouse.overlaps(psychCreditsButton, FlxG.camera))\n\t\t\t{\n\t\t\t\tselectedSomethin = true;\n\t\t\t\tCreditsState.psychEngineCreditsOnly = true;\n\t\t\t\tMusicBeatState.switchState(new CreditsState());\n\t\t\t\treturn;\n\t\t\t}\n\t\t\tvar mouseAccept:Bool = false;",
        "Psych credits button click action")
    path.write_text(s,encoding="utf-8")

def patch_credits(path):
    s=path.read_text(encoding="utf-8")
    s=once(s,"class CreditsState extends MusicBeatState\n{",
        "class CreditsState extends MusicBeatState\n{\n\tpublic static var psychEngineCreditsOnly:Bool = false;",
        "CreditsState mode flag")
    old="""\t\tvar defaultList:Array<Array<String>> = [
\t\t\t["Funkin' Crew"],
\t\t\t['ninjamuffin99', 'ninjamuffin99', "Programmer of Friday Night Funkin'", 'https://twitter.com/ninja_muffin99', 'CF2D2D'],
\t\t\t['PhantomArcade', 'phantomarcade', "Animator of Friday Night Funkin'", 'https://twitter.com/PhantomArcade3K', 'FADC45'],
\t\t\t['evilsk8r', 'evilsk8r', "Artist of Friday Night Funkin'", 'https://twitter.com/evilsk8r', '5ABD4B'],
\t\t\t['kawaisprite', 'kawaisprite', "Composer of Friday Night Funkin'", 'https://twitter.com/kawaisprite', '378FC7']
\t\t];"""
    new="""\t\tvar defaultList:Array<Array<String>> = psychEngineCreditsOnly ? [
\t\t\t['Psych Engine Team'],
\t\t\t['Shadow Mario', 'shadowmario', 'Main Programmer and Head of Psych Engine', 'https://ko-fi.com/shadowmario', '444444'],
\t\t\t['Riveren', 'riveren', 'Main Artist/Animator of Psych Engine', 'https://twitter.com/riverennn', '14967B'],
\t\t\t[''],
\t\t\t['Former Engine Members'],
\t\t\t['bb-panzu', 'bb', 'Ex-Programmer of Psych Engine', 'https://twitter.com/bbsub3', '3E813A'],
\t\t\t['shubs', '', 'Ex-Programmer of Psych Engine', '', 'A1A1A1'],
\t\t\t[''],
\t\t\t['Engine Contributors'],
\t\t\t['CrowPlexus', 'crowplexus', 'Input System v3 and Other PRs', 'https://twitter.com/crowplexus', 'A1A1A1'],
\t\t\t['Keoiki', 'keoiki', 'Note Splash Animations and Latin Alphabet', 'https://twitter.com/Keoiki_', 'D2D2D2'],
\t\t\t['SqirraRNG', 'sqirra', 'Crash Handler and Chart Editor Waveform', 'https://twitter.com/gedehari', 'E1843A'],
\t\t\t['EliteMasterEric', 'mastereric', 'Runtime Shaders support', 'https://twitter.com/EliteMasterEric', 'FFBD40'],
\t\t\t['PolybiusProxy', 'proxy', 'MP4 Video Loader Library', 'https://twitter.com/polybiusproxy', 'DCD294'],
\t\t\t['Tahir', 'tahir', 'SScript and Other PRs', 'https://twitter.com/tahirk618', 'A04397'],
\t\t\t['iFlicky', 'flicky', 'Composer and Dialogue Sounds', 'https://twitter.com/flicky', '9E29CF'],
\t\t\t['KadeDev', 'kade', 'Chart Editor fixes and Other PRs', 'https://twitter.com/kade0912', '64A250'],
\t\t\t['superpowers04', 'superpowers04', 'LUA JIT Fork', 'https://twitter.com/superpowers04', 'B957ED'],
\t\t\t['CheemsAndFriends', 'face', 'Creator of FlxAnimate', 'https://twitter.com/CheemsnFriendos', 'A1A1A1']
\t\t] : [
\t\t\t["Funkin' Crew"],
\t\t\t['ninjamuffin99', 'ninjamuffin99', "Programmer of Friday Night Funkin'", 'https://twitter.com/ninja_muffin99', 'CF2D2D'],
\t\t\t['PhantomArcade', 'phantomarcade', "Animator of Friday Night Funkin'", 'https://twitter.com/PhantomArcade3K', 'FADC45'],
\t\t\t['evilsk8r', 'evilsk8r', "Artist of Friday Night Funkin'", 'https://twitter.com/evilsk8r', '5ABD4B'],
\t\t\t['kawaisprite', 'kawaisprite', "Composer of Friday Night Funkin'", 'https://twitter.com/kawaisprite', '378FC7']
\t\t];"""
    s=once(s,old,new,"split Psych Engine credits from Extras")
    path.write_text(s,encoding="utf-8")

if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("Usage: apply_psych_engine_credits.py MainMenuState.hx CreditsState.hx")
    patch_menu(Path(sys.argv[1]))
    patch_credits(Path(sys.argv[2]))
