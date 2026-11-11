#!/usr/bin/env python3
"""Use the Sonic.EXE menu theme whenever gameplay returns to a menu."""

from pathlib import Path
import sys


OLD_TRACK = "FlxG.sound.playMusic(Paths.music('freakyMenu'));"
SONIC_EXE_TRACK = "FlxG.sound.playMusic(Paths.music('menu'));"


def patch_play_state(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    start = source.find("\tpublic function endSong()")
    end = source.find("\n\tpublic function KillNotes()", start)
    if start < 0 or end < 0:
        raise SystemExit("Menu music patch stopped: could not find PlayState.endSong()")

    block = source[start:end]
    found = block.count(OLD_TRACK)
    if found != 2:
        raise SystemExit(
            "Menu music patch stopped: expected the story-complete and Freeplay "
            f"return tracks in PlayState.endSong(), found {found}"
        )

    source = source[:start] + block.replace(OLD_TRACK, SONIC_EXE_TRACK) + source[end:]
    path.write_text(source, encoding="utf-8")
    print("PlayState now starts the Sonic.EXE menu theme after a song ends.")


def patch_pause_substate(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    found = source.count(OLD_TRACK)
    if found != 1:
        raise SystemExit(
            "Menu music patch stopped: expected one Exit to menu track in "
            f"PauseSubState.hx, found {found}"
        )

    source = source.replace(OLD_TRACK, SONIC_EXE_TRACK, 1)
    path.write_text(source, encoding="utf-8")
    print("Pause-menu Exit to menu now starts the Sonic.EXE menu theme.")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: apply_sonicexe_menu_music.py "
            "engine/source/states/PlayState.hx "
            "engine/source/substates/PauseSubState.hx"
        )

    play_state = Path(sys.argv[1])
    pause_substate = Path(sys.argv[2])
    for target in (play_state, pause_substate):
        if not target.is_file():
            raise SystemExit(f"Psych Engine source file not found: {target}")

    patch_play_state(play_state)
    patch_pause_substate(pause_substate)


if __name__ == "__main__":
    main()
