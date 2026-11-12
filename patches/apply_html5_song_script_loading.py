#!/usr/bin/env python3
"""Load embedded per-song HScript assets in HTML5 without filesystem directory scans."""
from pathlib import Path
import sys
def main():
 if len(sys.argv)!=2: raise SystemExit("Usage: apply_html5_song_script_loading.py engine/source/states/PlayState.hx")
 p=Path(sys.argv[1]); src=p.read_text(encoding="utf-8")
 start="\t\t#if (LUA_ALLOWED || HSCRIPT_ALLOWED)\n\t\tfor (folder in Mods.directoriesWithFile(Paths.getSharedPath(), 'data/$songName/'))"
 end="\t\t#end\n\n\t\tstartCallback();"
 if src.count(start)!=1 or src.count(end)!=1: raise SystemExit("Could not find the exact song-script loading block in PlayState.hx.")
 a=src.index(start); b=src.index(end,a)+len("\t\t#end")
 replacement="""\t\t#if sys && (LUA_ALLOWED || HSCRIPT_ALLOWED)
\t\tfor (folder in Mods.directoriesWithFile(Paths.getSharedPath(), 'data/$songName/'))
\t\t\tfor (file in FileSystem.readDirectory(folder))
\t\t\t{
\t\t\t\t#if LUA_ALLOWED
\t\t\t\tif(file.toLowerCase().endsWith('.lua'))
\t\t\t\t\tnew FunkinLua(folder + file);
\t\t\t\t#end
\t\t\t\t#if HSCRIPT_ALLOWED
\t\t\t\tif(file.toLowerCase().endsWith('.hx'))
\t\t\t\t\tinitHScript(folder + file);
\t\t\t\t#end
\t\t\t}
\t\t#end
\t\t#if (HSCRIPT_ALLOWED && !sys)
\t\t// HTML5 cannot enumerate embedded asset folders with FileSystem.
\t\tfor (scriptName in ["modchart.hx", "intro.hx", "run.hx", songName + ".hx"])
\t\t\tstartHScriptsNamed('data/' + songName + '/' + scriptName);
\t\tstartHScriptsNamed('custom_events/SonicEXEEvents.hx');
\t\t#end"""
 src=src[:a]+replacement+src[b:]; p.write_text(src,encoding="utf-8")
 print("PlayState now loads embedded per-song HScript files on HTML5.")
if __name__=="__main__": main()
