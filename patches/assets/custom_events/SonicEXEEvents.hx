// Shared browser-side event handlers for legacy EXE charts whose timed cues
// are encoded as negative-lane note records or in events.json.
function swapStrumSides():Void {
    for (i in 0...4) {
        var playerX:Float = game.playerStrums.members[i].x;
        game.playerStrums.members[i].x = game.opponentStrums.members[i].x;
        game.opponentStrums.members[i].x = playerX;
    }
}

function onEvent(name:Dynamic, value1:Dynamic, value2:Dynamic, strumTime:Dynamic):Void {
    switch (Std.string(name)) {
        case "RedVG":
            game.camGame.flash(0xFFFF0000, 0.18);
            game.camGame.shake(0.006, 0.16);
        case "static":
            game.camGame.flash(0xFFFFFFFF, 0.10);
            game.camHUD.flash(0xFFFFFFFF, 0.07);
        case "Genesis":
            game.camGame.flash(0xFFFFFFFF, 0.20);
            game.camGame.shake(0.008, 0.20);
        case "Majin spin":
            FlxTween.tween(game.camGame, {angle: game.camGame.angle + 180}, 0.55, {ease: FlxEase.quadInOut});
        case "startstatic":
            game.camGame.flash(0xFFFFFFFF, 0.16);
            game.camGame.shake(0.004, 0.12);
        case "tailsjump", "knuxjump", "eggjump":
            game.dad.playAnim("singUP", true);
            FlxG.sound.play(Paths.sound("jump"), 0.75);
        case "bgSpec":
            if (Std.string(value1) == "0") game.camGame.flash(0xFFFFFFFF, 0.12);
            else game.camGame.flash(0xFFFF0000, 0.12);
            game.camGame.shake(0.003, 0.12);
        case "strum swap1", "strum swap2":
            swapStrumSides();
        case "Zaa":
            game.camGame.flash(0xFFFFFFFF, 0.15);
            game.camGame.shake(0.005, 0.16);
        case "window_shake":
            var amount:Float = Std.parseFloat(Std.string(value1));
            var duration:Float = Std.parseFloat(Std.string(value2));
            if (Math.isNaN(amount)) amount = 5;
            if (Math.isNaN(duration)) duration = 10;
            var strength:Float = Math.min(0.025, amount / 1000);
            var time:Float = Math.min(0.6, duration / 100);
            game.camGame.shake(strength, time);
            game.camHUD.shake(strength, time);
        case "runStage":
            game.camGame.zoom = 1.0;
            game.boyfriend.playAnim("singUP", true);
            game.camGame.shake(0.004, 0.12);
        case "exe attack":
            game.camGame.flash(0xFFFF0000, 0.12);
            game.camGame.shake(0.012, 0.24);
            FlxG.sound.play(Paths.sound("beam"), 0.65);
    }
}
