#!/usr/bin/env python3
"""Load HScript from filesystem on sys targets and embedded OpenFL assets on HTML5."""
from pathlib import Path
import sys

def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"HTML5 HScript loader stopped: expected one {label} anchor, found {count}")
    return source.replace(old, new)

def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: apply_html5_song_script_loading.py engine/source/states/PlayState.hx")
    path = Path(sys.argv[1])
    source = path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        "\t\t#if (LUA_ALLOWED || HSCRIPT_ALLOWED)\n\t\tfor (folder in Mods.directoriesWithFile(Paths.getSharedPath(), 'scripts/'))",
        "\t\t#if sys && (LUA_ALLOWED || HSCRIPT_ALLOWED)\n\t\tfor (folder in Mods.directoriesWithFile(Paths.getSharedPath(), 'scripts/'))",
        "global script scan",
    )

    start = "\tpublic function startHScriptsNamed(scriptFile:String)\n"
    end = "\n\tpublic function initHScript(file:String)\n"
    if source.count(start) != 1 or source.count(end) != 1:
        raise SystemExit("HTML5 HScript loader stopped: missing startHScriptsNamed/initHScript methods.")
    begin = source.index(start)
    finish = source.index(end, begin)
    method = """\tpublic function startHScriptsNamed(scriptFile:String)
\t{
\t\t#if sys
\t\t\t#if MODS_ALLOWED
\t\t\tvar scriptToLoad:String = Paths.modFolders(scriptFile);
\t\t\tif(!FileSystem.exists(scriptToLoad))
\t\t\t\tscriptToLoad = Paths.getSharedPath(scriptFile);
\t\t\t#else
\t\t\tvar scriptToLoad:String = Paths.getSharedPath(scriptFile);
\t\t\t#end
\t\t\tif(FileSystem.exists(scriptToLoad))
\t\t\t{
\t\t\t\tif (SScript.global.exists(scriptToLoad)) return false;
\t\t\t\tinitHScript(scriptToLoad);
\t\t\t\treturn true;
\t\t\t}
\t\t#else
\t\t\tvar assetPath:String = Paths.getSharedPath(scriptFile);
\t\t\tif(OpenFlAssets.exists(assetPath, openfl.utils.AssetType.TEXT))
\t\t\t{
\t\t\t\tfor (loadedScript in hscriptArray)
\t\t\t\t\tif (loadedScript != null && loadedScript.origin == assetPath)
\t\t\t\t\t\treturn false;
\t\t\t\tinitHScript(scriptFile);
\t\t\t\treturn true;
\t\t\t}
\t\t#end
\t\treturn false;
\t}
"""
    source = source[:begin] + method + source[finish:]

    source = replace_once(
        source,
        "\t\t\tvar newScript:HScript = new HScript(null, file);",
        """#if sys
\t\t\tvar scriptContents:String = file;
#else
\t\t\tvar scriptPath:String = Paths.getSharedPath(file);
\t\t\tif(!OpenFlAssets.exists(scriptPath, openfl.utils.AssetType.TEXT)) return;
\t\t\tvar scriptContents:String = OpenFlAssets.getText(scriptPath);
#end
\t\t\tvar newScript:HScript = new HScript(null, scriptContents);
#if !sys
\t\t\tnewScript.origin = scriptPath;
#end""",
        "HScript source constructor",
    )

    source = replace_once(
        source,
        "\t\t#if (LUA_ALLOWED || HSCRIPT_ALLOWED)\n\t\tfor (folder in Mods.directoriesWithFile(Paths.getSharedPath(), 'data/$songName/'))",
        "\t\t#if sys && (LUA_ALLOWED || HSCRIPT_ALLOWED)\n\t\tfor (folder in Mods.directoriesWithFile(Paths.getSharedPath(), 'data/$songName/'))",
        "song script scan",
    )
    source = replace_once(
        source,
        "\t\t#end\n\n\t\tstartCallback();",
        """\t\t#end

\t\t#if (HSCRIPT_ALLOWED && !sys)
\t\tfor (scriptName in ["modchart.hx", "intro.hx", "run.hx", songName + ".hx"])
\t\t\tstartHScriptsNamed('data/' + songName + '/' + scriptName);
\t\tstartHScriptsNamed('custom_events/SonicEXEEvents.hx');
\t\t#end

\t\tstartCallback();""",
        "HTML5 embedded song scripts",
    )
    path.write_text(source, encoding="utf-8")
    print("HTML5 embedded stage/event/note-type/song HScript loading enabled.")

if __name__ == "__main__":
    main()
