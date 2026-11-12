// Browser-safe Triple Trouble stage behavior; Middle Scroll stays user-controlled.
var ttX:Array<Float>=[]; var ttY:Array<Float>=[]; var ttSaved:Bool=false; var ttDad:String=""; var ttBf:String="";
function onCountdownStarted():Void { ttX=[]; ttY=[]; for (i in 0...4) { ttX.push(game.playerStrums.members[i].x); ttY.push(game.playerStrums.members[i].y); } ttSaved=true; }
function onUpdate(elapsed:Float):Void {
 if (ClientPrefs.data.middleScroll && ttSaved) for (i in 0...4) {
  game.playerStrums.members[i].x=ttX[i]; game.playerStrums.members[i].y=ttY[i]; game.playerStrums.members[i].visible=true; game.opponentStrums.members[i].visible=false;
 }
 var d=game.dad.curCharacter;
 if (d!=ttDad) { ttDad=d; if (game.iconP2!=null) { if (d=="TailsSoul") game.iconP2.changeIcon("mechbf"); else game.iconP2.changeIcon(game.dad.healthIcon); } }
 var b=game.boyfriend.curCharacter;
 if (b!=ttBf) { ttBf=b; if (game.iconP1!=null) { if (b=="TailsSoul") game.iconP1.changeIcon("mechbf"); else game.iconP1.changeIcon(game.boyfriend.healthIcon); } }
}
