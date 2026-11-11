#!/usr/bin/env python3
"""Resolve song-pack event and note-type handlers from the active week_assets directory."""

from pathlib import Path
import sys


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"Pack script resolution stopped: {label} expected once, found {count}"
        )
    return source.replace(old, new)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: apply_pack_song_script_resolution.py engine/source/states/PlayState.hx"
        )

    path = Path(sys.argv[1])
    source = path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        """\t\t#if MODS_ALLOWED
\t\tvar luaToLoad:String = Paths.modFolders(luaFile);
\t\tif(!FileSystem.exists(luaToLoad))
\t\t\tluaToLoad = Paths.getSharedPath(luaFile);

\t\tif(FileSystem.exists(luaToLoad))
\t\t#elseif sys
\t\tvar luaToLoad:String = Paths.getSharedPath(luaFile);
\t\tif(OpenFlAssets.exists(luaToLoad))
\t\t#end""",
        """\t\t#if MODS_ALLOWED
\t\tvar luaToLoad:String = Paths.modFolders(luaFile);
\t\tif(!FileSystem.exists(luaToLoad))
\t\t\tluaToLoad = Paths.getPath(luaFile, TEXT);

\t\tif(FileSystem.exists(luaToLoad) || OpenFlAssets.exists(luaToLoad, TEXT))
\t\t#elseif sys
\t\tvar luaToLoad:String = Paths.getPath(luaFile, TEXT);
\t\tif(OpenFlAssets.exists(luaToLoad, TEXT))
\t\t#end""",
        "resolve Lua handlers from the active pack before shared scripts",
    )

    source = replace_once(
        source,
        """\t\t#if MODS_ALLOWED
\t\tvar scriptToLoad:String = Paths.modFolders(scriptFile);
\t\tif(!FileSystem.exists(scriptToLoad))
\t\t\tscriptToLoad = Paths.getSharedPath(scriptFile);
\t\t#else
\t\tvar scriptToLoad:String = Paths.getSharedPath(scriptFile);
\t\t#end

\t\tif(FileSystem.exists(scriptToLoad))""",
        """\t\t#if MODS_ALLOWED
\t\tvar scriptToLoad:String = Paths.modFolders(scriptFile);
\t\tif(!FileSystem.exists(scriptToLoad))
\t\t\tscriptToLoad = Paths.getPath(scriptFile, TEXT);
\t\t#else
\t\tvar scriptToLoad:String = Paths.getPath(scriptFile, TEXT);
\t\t#end

\t\tif(FileSystem.exists(scriptToLoad) || OpenFlAssets.exists(scriptToLoad, TEXT))""",
        "resolve HScript handlers from the active pack before shared scripts",
    )

    path.write_text(source, encoding="utf-8")
    print("PlayState now resolves pack-scoped custom note/event scripts.")


if __name__ == "__main__":
    main()
