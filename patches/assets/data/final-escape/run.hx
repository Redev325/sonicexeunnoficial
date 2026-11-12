// Browser-safe Final Escape running jump mechanic, ported from run.lua.
var escapeCanJump:Bool=false; var escapeEnded:Bool=false; var escapeBaseY:Float=0;
function onStepHit():Void if (game.curStep>=464 && !escapeEnded) escapeCanJump=true;
function onUpdatePost(elapsed:Float):Void {
 if (game.curStep>=464 && !escapeEnded) escapeCanJump=true;
 if (!escapeCanJump || escapeEnded || game.cpuControlled || !FlxG.keys.justPressed.SPACE) return;
 escapeCanJump=false; escapeBaseY=game.boyfriend.y; FlxG.sound.play(Paths.sound("jump"),1);
 FlxTween.tween(game.boyfriend,{y:escapeBaseY-200},Conductor.crochet/1000,{ease:FlxEase.quadOut,onComplete:function(_) {
  FlxTween.tween(game.boyfriend,{y:escapeBaseY},Conductor.crochet/1000,{ease:FlxEase.quadIn,onComplete:function(_) if (!escapeEnded) escapeCanJump=true});
 }});
}
function onGameOver():Dynamic { escapeEnded=true; escapeCanJump=false; return Function_Continue; }
