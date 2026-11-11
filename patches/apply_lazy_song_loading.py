#!/usr/bin/env python3
"""Load only the selected HTML5 song instead of preloading the entire songs library."""

from pathlib import Path
import re
import sys


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"Lazy song loading stopped: {label} expected once, found {count}")
    return source.replace(old, new)


def replace_regex_once(source: str, pattern: str, replacement: str, label: str) -> str:
    source, count = re.subn(pattern, lambda _match: replacement, source, count=1)
    if count != 1:
        raise SystemExit(f"Lazy song loading stopped: {label} expected once, found {count}")
    return source


def patch_loading_state(path: Path) -> None:
    source = path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        "import haxe.io.Path;",
        "import haxe.io.Path;\nimport haxe.Json;",
        "import JSON support for the per-song vocal index",
    )

    source = replace_once(
        source,
        """\tstatic function getSongPath()
\t{
\t\treturn Paths.inst(PlayState.SONG.song);
\t}""",
        """\tstatic function getSongPath():String
\t{
\t\treturn Paths.getLibraryPath(Paths.formatToSongPath(PlayState.SONG.song) + '/Inst.mp3', 'songs');
\t}""",
        "use a manifest key for the instrumental asset",
    )
    source = replace_regex_once(
        source,
        r"if \(PlayState\.SONG\.needsVoices\)\r?\n\s*checkLoadSong\(getVocalPath\(\)\);",
        """if (PlayState.SONG.needsVoices)
\t\t\t\t\t\tfor (voicePath in getVocalPaths(PlayState.SONG.song))
\t\t\t\t\t\t\tcheckLoadSong(voicePath);""",
        "load every vocal stem in the selected song",
    )
    source = replace_once(
        source,
        """\tstatic function getVocalPath()
\t{
\t\treturn Paths.voices(PlayState.SONG.song);
\t}""",
        """\tstatic function getVocalPaths(song:String):Array<String>
\t{
\t\tvar slug:String = Paths.formatToSongPath(song);
\t\tvar result:Array<String> = [];
\t\ttry
\t\t{
\t\t\tvar index:Dynamic = Json.parse(Assets.getText(Paths.getSharedPath('data/sonicexe-audio-index.json')));
\t\t\tvar names:Array<String> = cast Reflect.field(index, slug);
\t\t\tif (names != null)
\t\t\t\tfor (name in names)
\t\t\t\t\tresult.push(Paths.getLibraryPath(slug + '/' + name, 'songs'));
\t\t}
\t\tcatch (e:Dynamic) {}
\t\tif (result.length == 0)
\t\t\tresult.push(Paths.getLibraryPath(slug + '/Voices.mp3', 'songs'));
\t\treturn result;
\t}""",
        "use the per-song audio index for all vocal files",
    )
    source = replace_once(
        source,
        """\t\t\tvar callback = callbacks.add("song:" + path);
\t\t\tAssets.loadSound(path).onComplete(function (_) { callback(); });""",
        """\t\t\tvar callback = callbacks.add("song:" + path);
\t\t\tAssets.loadSound(path).onComplete(function (_) {
\t\t\t\tcallback();
\t\t\t}).onError(function (error) {
\t\t\t\ttrace("Failed to load selected song asset " + path + ": " + error);
\t\t\t\tcallback();
\t\t\t});""",
        "report individual audio-load failures",
    )
    source = replace_regex_once(
        source,
        r"\t\tif \(stopMusic && FlxG\.sound\.music != null\)\r?\n"
        r"\t\t\tFlxG\.sound\.music\.stop\(\);\r?\n[ \t]*\r?\n"
        r"\t\treturn target;",
        """\t\t#if html5
\t\tif (PlayState.SONG != null)
\t\t{
\t\t\tvar selectedAudioLoaded:Bool = Assets.cache.hasSound(getSongPath());
\t\t\tif (PlayState.SONG.needsVoices)
\t\t\t\tfor (voicePath in getVocalPaths(PlayState.SONG.song))
\t\t\t\t\tselectedAudioLoaded = selectedAudioLoaded && Assets.cache.hasSound(voicePath);

\t\t\t// Stage sprites are large too; register their library only when a
\t\t\t// selected song needs a non-shared stage directory.
\t\t\tvar selectedStageLoaded:Bool = directory == 'shared' || Assets.getLibrary("week_assets") != null;
\t\t\tif (!selectedAudioLoaded || !selectedStageLoaded)
\t\t\t\treturn new LoadingState(target, stopMusic, directory);
\t\t}
\t\t#end

\t\tif (stopMusic && FlxG.sound.music != null)
\t\t\tFlxG.sound.music.stop();

\t\treturn target;""",
        "show a loading screen only when the selected song is not cached",
    )

    helper = """\tpublic static function loadSongAudio(
\t\tsong:String,
\t\tneedsVoices:Bool,
\t\tonReady:Void->Void,
\t\tonError:Dynamic->Void
\t):Void
\t{
\t\tvar slug:String = Paths.formatToSongPath(song);
\t\tvar requested:Array<String> = [
\t\t\tPaths.getLibraryPath(slug + '/Inst.mp3', 'songs')
\t\t];
\t\tif (needsVoices)
\t\t\tfor (voicePath in getVocalPaths(song))
\t\t\t\trequested.push(voicePath);

\t\tinitSongsManifest().onComplete(function (_)
\t\t{
\t\t\tvar pending:Array<String> = [];
\t\t\tfor (assetPath in requested)
\t\t\t\tif (!Assets.cache.hasSound(assetPath))
\t\t\t\t\tpending.push(assetPath);

\t\t\tif (pending.length == 0)
\t\t\t{
\t\t\t\tonReady();
\t\t\t\treturn;
\t\t\t}

\t\t\tvar completed:Int = 0;
\t\t\tvar failed:Bool = false;
\t\t\tfunction finishOne():Void
\t\t\t{
\t\t\t\tcompleted++;
\t\t\t\tif (!failed && completed >= pending.length)
\t\t\t\t\tonReady();
\t\t\t}
\t\t\tfunction fail(error:Dynamic):Void
\t\t\t{
\t\t\t\tif (!failed)
\t\t\t\t{
\t\t\t\t\tfailed = true;
\t\t\t\t\tonError(error);
\t\t\t\t}
\t\t\t}
\t\t\tfor (assetPath in pending)
\t\t\t{
\t\t\t\tAssets.loadSound(assetPath).onComplete(function (_) {
\t\t\t\t\tfinishOne();
\t\t\t\t}).onError(fail);
\t\t\t}
\t\t}).onError(onError);
\t}

"""
    source = replace_once(
        source,
        "\tstatic function initSongsManifest()",
        helper + "\tstatic function initSongsManifest()",
        "add the per-track Freeplay preview loader",
    )

    path.write_text(source, encoding="utf-8")
    print(f"Installed per-track HTML5 song loading in {path}")


def patch_freeplay(path: Path) -> None:
    source = path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        "\tprivate var curPlaying:Bool = false;",
        "\tprivate var curPlaying:Bool = false;\n"
        "\tprivate var previewLoading:Bool = false;\n"
        "\tprivate var previewLoadToken:Int = 0;",
        "add cancellable asynchronous preview state",
    )
    source = replace_once(
        source,
        """\t\tif (songs.length == 0 || player.playingMusic)
\t\t\treturn;

\t\t_updateSongLastDifficulty();""",
        """\t\tif (songs.length == 0 || player.playingMusic)
\t\t\treturn;

\t\tif (previewLoading)
\t\t{
\t\t\tpreviewLoadToken++;
\t\t\tpreviewLoading = false;
\t\t}

\t\t_updateSongLastDifficulty();""",
        "cancel stale previews on selection change",
    )
    source = replace_once(
        source,
        "else if (controls.ACCEPT && !player.playingMusic && songs.length > 0)",
        "else if (controls.ACCEPT && !player.playingMusic && songs.length > 0 && !previewLoading)",
        "prevent gameplay launch while a preview is pending",
    )
    source = replace_once(
        source,
        """\t\tif (controls.BACK || FlxG.keys.justPressed.BACKSPACE)
\t\t{
\t\t\tif (player.playingMusic)""",
        """\t\tif (controls.BACK || FlxG.keys.justPressed.BACKSPACE)
\t\t{
\t\t\tpreviewLoadToken++;
\t\t\tpreviewLoading = false;
\t\t\tif (player.playingMusic)""",
        "cancel pending preview on menu exit",
    )

    preview_pattern = re.compile(
        r"if\(instPlaying != curSelected && !player\.playingMusic\)\n"
        r"\s*\{.*?\n"
        r"\s*\}\n"
        r"\s*else if \(instPlaying == curSelected && player\.playingMusic\)",
        re.S,
    )
    preview_replacement = """if (instPlaying != curSelected && !player.playingMusic && !previewLoading)
\t\t\t{
\t\t\t\tvar requestedIndex:Int = curSelected;
\t\t\t\tMods.currentModDirectory = songs[requestedIndex].folder;
\t\t\t\tvar requestedLowercase:String = Paths.formatToSongPath(songs[requestedIndex].songName);
\t\t\t\tvar chartName:String = Highscore.formatSong(requestedLowercase, curDifficulty);
\t\t\t\tPlayState.SONG = Song.loadFromJson(chartName, requestedLowercase);

\t\t\t\tvar requestedSong:String = PlayState.SONG.song;
\t\t\t\tvar requestedNeedsVoices:Bool = PlayState.SONG.needsVoices;
\t\t\t\tvar loadToken:Int = ++previewLoadToken;
\t\t\t\tpreviewLoading = true;

\t\t\t\tLoadingState.loadSongAudio(requestedSong, requestedNeedsVoices, function()
\t\t\t\t{
\t\t\t\t\tif (loadToken != previewLoadToken)
\t\t\t\t\t\treturn;
\t\t\t\t\tpreviewLoading = false;
\t\t\t\t\tif (requestedIndex != curSelected || player.playingMusic)
\t\t\t\t\t\treturn;

\t\t\t\t\tdestroyFreeplayVocals();
\t\t\t\t\tFlxG.sound.music.volume = 0;
\t\t\t\t\tif (requestedNeedsVoices)
\t\t\t\t\t{
\t\t\t\t\t\tvar previewVoice = Paths.voices(requestedSong, 'Player');
\t\t\t\t\t\tif (previewVoice == null) previewVoice = Paths.voices(requestedSong, 'Opponent');
\t\t\t\t\t\tif (previewVoice == null) previewVoice = Paths.voices(requestedSong);
\t\t\t\t\t\tif (previewVoice != null)
\t\t\t\t\t\t{
\t\t\t\t\t\t\tvocals = new FlxSound().loadEmbedded(previewVoice);
\t\t\t\t\t\t\tFlxG.sound.list.add(vocals);
\t\t\t\t\t\t\tvocals.persist = true;
\t\t\t\t\t\t\tvocals.looped = true;
\t\t\t\t\t\t}
\t\t\t\t\t}

\t\t\t\t\tFlxG.sound.playMusic(Paths.inst(requestedSong), 0.8);
\t\t\t\t\tif (vocals != null)
\t\t\t\t\t{
\t\t\t\t\t\tvocals.play();
\t\t\t\t\t\tvocals.volume = 0.8;
\t\t\t\t\t}
\t\t\t\t\tinstPlaying = requestedIndex;
\t\t\t\t\tplayer.playingMusic = true;
\t\t\t\t\tplayer.curTime = 0;
\t\t\t\t\tplayer.switchPlayMusic();
\t\t\t\t}, function(error:Dynamic)
\t\t\t\t{
\t\t\t\t\tif (loadToken != previewLoadToken)
\t\t\t\t\t\treturn;
\t\t\t\t\tpreviewLoading = false;
\t\t\t\t\ttrace("Sonic.EXE Freeplay preview failed to load: " + error);
\t\t\t\t});
\t\t\t}
\t\t\telse if (instPlaying == curSelected && player.playingMusic)"""
    source, count = preview_pattern.subn(lambda _match: preview_replacement, source, count=1)
    if count != 1:
        raise SystemExit(f"Lazy song loading stopped: expected one Freeplay preview branch, found {count}")

    source = replace_regex_once(
        source,
        r"\toverride function destroy\(\):Void\r?\n\t\{",
        """\toverride function destroy():Void
\t{
\t\tpreviewLoadToken++;
\t\tpreviewLoading = false;""",
        "cancel callbacks immediately when Freeplay is destroyed",
    )
    path.write_text(source, encoding="utf-8")
    print(f"Installed asynchronous Freeplay previews in {path}")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: apply_lazy_song_loading.py engine/source/states/LoadingState.hx "
            "engine/source/states/FreeplayState.hx"
        )
    patch_loading_state(Path(sys.argv[1]))
    patch_freeplay(Path(sys.argv[2]))


if __name__ == "__main__":
    main()
