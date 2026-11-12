// HTML5 background layers for You Can't Run's Phase 3 stage.
function addYCRLayer(path:String,x:Float,y:Float,sx:Float,sy:Float):FlxSprite {
    var layer = new FlxSprite(x,y);
    layer.loadGraphic(Paths.image(path));
    layer.scrollFactor.set(sx,sy);
    addBehindGF(layer);
    return layer;
}
function onCreate():Void {
    addYCRLayer("Phase3/bgNormal",-900,-650,0.55,0.55);
    addYCRLayer("Phase3/normal/BackBush",-900,-420,0.62,0.62);
    addYCRLayer("Phase3/normal/TTTrees",-900,-380,0.72,0.72);
    addYCRLayer("Phase3/normal/TopBushes",-900,-360,0.80,0.80);
    addYCRLayer("Phase3/normal/FGTree1",-900,-250,0.90,0.90);
    addYCRLayer("Phase3/normal/FGTree2",-900,-240,0.95,0.95);
}
