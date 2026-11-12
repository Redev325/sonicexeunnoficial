// HTML5 background layers for the original Too Slow Encore stage.
function addEncoreLayer(path:String,x:Float,y:Float,sx:Float,sy:Float):FlxSprite {
    var layer = new FlxSprite(x,y);
    layer.loadGraphic(Paths.image(path));
    layer.scrollFactor.set(sx,sy);
    game.add(layer);
    return layer;
}
function onCreate():Void {
    addEncoreLayer("PolishedP1/BGSky",-900,-520,0.45,0.45);
    addEncoreLayer("PolishedP1/bgEncore",-900,-420,0.65,0.65);
    addEncoreLayer("PolishedP1/OuterBush",-900,-300,0.75,0.75);
    addEncoreLayer("PolishedP1/TreesMidBack",-900,-280,0.82,0.82);
    addEncoreLayer("PolishedP1/TreesMid",-900,-220,0.90,0.90);
    addEncoreLayer("PolishedP1/Grass",-900,430,1,1);
    addEncoreLayer("PolishedP1/TreesFG",-900,300,1.05,1.05);
}
