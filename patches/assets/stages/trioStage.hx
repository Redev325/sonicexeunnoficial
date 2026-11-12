// HTML5 Triple Trouble Phase 3 scene, with the original normal/Xeno backdrops.
var trioNormal:Array<FlxSprite> = [];
var trioXeno:Array<FlxSprite> = [];
function addTrioLayer(path:String,x:Float,y:Float,sx:Float,sy:Float,visible:Bool):FlxSprite {
    var layer = new FlxSprite(x,y);
    layer.loadGraphic(Paths.image(path));
    layer.scrollFactor.set(sx,sy);
    layer.visible = visible;
    addBehindGF(layer);
    return layer;
}
function onCreate():Void {
    trioNormal.push(addTrioLayer("Phase3/bgNormal",-900,-650,0.55,0.55,true));
    trioNormal.push(addTrioLayer("Phase3/normal/BackBush",-900,-420,0.62,0.62,true));
    trioNormal.push(addTrioLayer("Phase3/normal/TTTrees",-900,-380,0.72,0.72,true));
    trioNormal.push(addTrioLayer("Phase3/normal/TopBushes",-900,-360,0.80,0.80,true));
    trioNormal.push(addTrioLayer("Phase3/normal/FGTree1",-900,-250,0.90,0.90,true));
    trioNormal.push(addTrioLayer("Phase3/normal/FGTree2",-900,-240,0.95,0.95,true));
    trioXeno.push(addTrioLayer("Phase3/bgXeno",-900,-650,0.55,0.55,false));
    trioXeno.push(addTrioLayer("Phase3/xeno/BackTrees",-900,-420,0.62,0.62,false));
    trioXeno.push(addTrioLayer("Phase3/xeno/Grass",-900,360,0.92,0.92,false));
    trioXeno.push(addTrioLayer("Phase3/xeno/FGTree1",-900,-250,0.90,0.90,false));
    trioXeno.push(addTrioLayer("Phase3/xeno/FGTree2",-900,-240,0.95,0.95,false));
}
function onEvent(name:Dynamic,value1:Dynamic,value2:Dynamic,strumTime:Dynamic):Void {
    if (name=="bgSpec") {
        var useXeno = (Std.string(value1)=="1" || Std.string(value1)=="flip");
        for (layer in trioNormal) layer.visible = !useXeno;
        for (layer in trioXeno) layer.visible = useXeno;
    }
}
