// HTML5 recreation of the original Final Escape stage composition.
function addFinalImage(name:String,x:Float,y:Float,scroll:Float=0.9,scaleX:Float=1,scaleY:Float=1.0):FlxSprite {
    var sprite = new FlxSprite(x,y);
    sprite.loadGraphic(Paths.image("final escape/"+name));
    sprite.scrollFactor.set(scroll,scroll);
    sprite.scale.set(scaleX,scaleY);
    sprite.updateHitbox();
    addBehindGF(sprite);
    return sprite;
}
function addFinalAtlas(name:String,x:Float,y:Float,prefix:String):FlxSprite {
    var sprite = new FlxSprite(x,y);
    sprite.frames = Paths.getSparrowAtlas("final escape/"+name);
    sprite.animation.addByPrefix("idle",prefix,24,true);
    sprite.animation.play("idle");
    addBehindGF(sprite);
    return sprite;
}
function onCreate():Void {
    addFinalImage("bg",-114,-200,0.9,1,1.2);
    addFinalImage("lines",-10,-125,0.9);
    addFinalImage("whiteglow",140,375,0.9);
    addFinalImage("sega",825,40,1,1.2,1.2);
    addFinalImage("egg box",1000,85,1);
    addFinalImage("cube",1035,-60,1);
    addFinalAtlas("banner",425,350,"banner0");
    addFinalAtlas("block2",765,-50,"gh 20");
    addFinalAtlas("block1",250,-95,"gh 10");
    addFinalAtlas("checkpoint",25,280,"checkpoint");
    addFinalImage("S",50,425,1);
    addFinalImage("O",250,385,1);
    addFinalImage("N",765,175,1);
    addFinalImage("I",1000,175,1);
    addFinalImage("C",1075,200,1);
    var ringSprite = addFinalAtlas("ring",1185,625,"ring0");
    ringSprite.cameras = [game.camHUD];
    ringSprite.scrollFactor.set();
    ringSprite.scale.set(1.5,1.5);
    if (ClientPrefs.data.downScroll) ringSprite.y = 10;
}
