package backend;

import lime.app.Future;
import lime.utils.AssetLibrary;
import openfl.utils.Assets;

/**
 * Loads the separate song-audio library after the HTML5 boot preloader.
 * All callers share one Future so previews and gameplay never race the load.
 */
class SonicEXEAssetLoader
{
    private static var songsFuture:Future<AssetLibrary>;

    public static function beginSongLibraryLoad():Void
    {
        ensureSongLibraryLoaded(
            function():Void {},
            function(error:Dynamic):Void {
                trace("Sonic.EXE song-library background load failed: " + error);
            }
        );
    }

    public static function ensureSongLibraryLoaded(
        onReady:Void->Void,
        onError:Dynamic->Void
    ):Void
    {
        // A second request may arrive after the background request completed.
        if (Assets.getLibrary("songs") != null)
        {
            onReady();
            return;
        }

        if (songsFuture == null)
            songsFuture = Assets.loadLibrary("songs");

        var pending:Future<AssetLibrary> = songsFuture;
        pending.onComplete(function(_)
        {
            if (Assets.getLibrary("songs") == null)
            {
                if (songsFuture == pending)
                    songsFuture = null;
                onError("OpenFL completed the request without registering the songs library.");
                return;
            }

            if (songsFuture == pending)
                songsFuture = null;
            onReady();
        });
        pending.onError(function(error)
        {
            if (songsFuture == pending)
                songsFuture = null;
            onError(error);
        });
    }
}
