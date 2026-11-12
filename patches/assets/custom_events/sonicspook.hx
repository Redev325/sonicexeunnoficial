// Browser event handler for the chart's Sonic scare cue.
function onEvent(name:Dynamic,v1:Dynamic,v2:Dynamic,strumTime:Dynamic):Void {
 if (name=="sonicspook") { game.camGame.shake(0.009,0.24); FlxG.sound.play(Paths.sound("too-slow"),0.8); }
}
