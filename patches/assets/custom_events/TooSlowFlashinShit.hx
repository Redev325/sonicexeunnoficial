// Browser event handler for Too Slow's timed red flash cue.
function onEvent(name:Dynamic,v1:Dynamic,v2:Dynamic,strumTime:Dynamic):Void {
 if (name=="TooSlowFlashinShit") { game.camGame.flash(0xFFFF0000,0.22); game.camHUD.flash(0xFFFF0000,0.16); game.camGame.shake(0.004,0.12); }
}
