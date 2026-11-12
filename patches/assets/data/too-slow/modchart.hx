// Browser-safe port of the original Too Slow strumline modchart.
var tooSlowBaseX:Array<Float> = []; var tooSlowBaseY:Array<Float> = [];
function onCreatePost():Void {
 tooSlowBaseX=[]; tooSlowBaseY=[];
 if (game.strumLineNotes==null) return;
 for (strum in game.strumLineNotes.members) if (strum!=null) { tooSlowBaseX.push(strum.x); tooSlowBaseY.push(strum.y); }
}
function onUpdate(elapsed:Float):Void {
 if (tooSlowBaseY.length==0 || game.strumLineNotes==null) return;
 var beat:Float=(Conductor.songPosition/1000)*(Conductor.bpm/84); var step:Int=game.curStep;
 for (i in 0...tooSlowBaseY.length) {
  if (i>=game.strumLineNotes.members.length) break;
  var strum=game.strumLineNotes.members[i]; if (strum==null) continue;
  var x:Float=tooSlowBaseX[i]; var y:Float=tooSlowBaseY[i];
  if (step>=789 && step<923) y += 5*Math.sin((beat+i*0.25)*Math.PI);
  if (step>=924 && step<1048) y -= 5*Math.sin((beat+i*0.25)*Math.PI);
  if (step>=1049 && step<1176) x += 2*Math.sin((beat+i*0.25)*Math.PI);
  if (step>=1177 && step<1959) x -= 6*Math.sin((beat+i*0.25)*Math.PI);
  strum.x=x; strum.y=y;
 }
 if ((step>=760 && step<786) || (step>=1392 && step<1428)) game.camGame.zoom=FlxMath.lerp(game.camGame.zoom,1.2,Math.min(1,elapsed*8));
 else if (game.camGame.zoom>game.defaultCamZoom) game.camGame.zoom=FlxMath.lerp(game.camGame.zoom,game.defaultCamZoom,Math.min(1,elapsed*8));
}
