// Browser HScript port of Final Escape's scripted intro sequence.
var feBlack:FlxSprite;
var feCircle:FlxSprite;
var feLogo:FlxSprite;
var feBanner:FlxSprite;
var feInstruction:FlxSprite;
var feBreathing:FlxSprite;
var feScream:FlxSprite;
var feHand:FlxSprite;
var feRing:FlxSprite;
var feLine:FlxSprite;
var feIntroSkipped:Bool = false;
var feInstructionVisible:Bool = false;

function feAddImage(path:String,x:Float,y:Float,camera:Dynamic):FlxSprite {
    var sprite = new FlxSprite(x,y);
    sprite.loadGraphic(Paths.image("final escape/" + path));
    sprite.cameras = [camera];
    game.add(sprite);
    return sprite;
}
function feAddAtlas(path:String,x:Float,y:Float,prefix:String,camera:Dynamic,loop:Bool):FlxSprite {
    var sprite = new FlxSprite(x,y);
    sprite.frames = Paths.getSparrowAtlas("final escape/" + path);
    sprite.animation.addByPrefix("idle",prefix,24,loop);
    sprite.animation.play("idle");
    sprite.cameras = [camera];
    game.add(sprite);
    return sprite;
}
function feHideIntro():Void {
    if (feCircle != null) feCircle.visible = false;
    if (feLogo != null) feLogo.visible = false;
    if (feBanner != null) feBanner.visible = false;
    if (feBreathing != null) feBreathing.visible = false;
    if (feScream != null) feScream.visible = false;
    if (feHand != null) feHand.visible = false;
}
function onCreate():Void {
    feBlack = feAddImage("black",-400,-200,game.camGame);
    feBlack.scale.set(1.5,1.5);
    feBlack.updateHitbox();
    feCircle = feAddImage("sonic circle front",100,0,game.camGame);
    feLogo = feAddImage("sonic logo",375,385,game.camGame);
    feBanner = feAddImage("banner normal",220,370,game.camGame);
    feBreathing = feAddAtlas("exe breathing",435,75,"exe breating0",game.camGame,true);
    feScream = feAddAtlas("exe reaching out",435,75,"exe reaching out",game.camGame,true);
    feHand = feAddAtlas("hand",600,175,"reaching out hand",game.camGame,true);
    feRing = feAddAtlas("ring flew",80,-175,"ring flew",game.camGame,false);
    feLine = feAddAtlas("exe line",380,-50,"EXE FRONT line",game.camGame,false);
    feScream.visible = false;
    feHand.visible = false;
    feRing.visible = false;
    feLine.visible = false;
    feInstruction = feAddImage("instruction",0,0,game.camOther);
    feInstruction.alpha = 0;
    game.dad.visible = false;
    game.camHUD.visible = false;
}
function onUpdatePost(elapsed:Float):Void {
    if (FlxG.keys.justPressed.TAB && feInstruction != null) {
        feInstructionVisible = !feInstructionVisible;
        FlxTween.cancelTweensOf(feInstruction);
        FlxTween.tween(feInstruction,{alpha:feInstructionVisible ? 1 : 0},0.25);
    }
    if (FlxG.keys.justPressed.SPACE && !feIntroSkipped && game.curStep < 464) {
        feIntroSkipped = true;
        Conductor.songPosition = 13600;
        if (FlxG.sound.music != null) FlxG.sound.music.time = 13600;
        if (game.vocals != null) game.vocals.time = 13600;
        feHideIntro();
        if (feBlack != null) FlxTween.tween(feBlack,{alpha:0},0.35);
        game.dad.visible = true;
        game.camHUD.visible = true;
    }
}
function onStepHit():Void {
    switch (game.curStep) {
        case 87:
            feBreathing.visible = false;
            feScream.visible = true;
            feHand.visible = true;
            FlxTween.tween(feHand.scale,{x:1.3,y:1.3},6,{ease:FlxEase.quadOut});
            game.camGame.zoom = 1.2;
            feLogo.angle = 35;
        case 91:
            FlxTween.tween(feLogo,{y:745},1,{ease:FlxEase.backOut});
            FlxTween.tween(feLogo,{x:635},2,{ease:FlxEase.linear});
            FlxTween.tween(feBanner,{y:730},2,{ease:FlxEase.linear});
        case 176:
            feRing.visible = true;
            feCircle.visible = false;
            feScream.visible = false;
            feHand.visible = false;
            game.camGame.zoom = 1;
            feIntroSkipped = true;
        case 192:
            game.dad.visible = true;
            game.dad.playAnim("pulls up",true);
            game.camHUD.visible = true;
        case 448:
            feLine.visible = true;
            game.dad.visible = false;
            game.camGame.zoom = 1.1;
        case 452: game.camGame.zoom = 1.2;
        case 456: game.camGame.zoom = 1.4;
        case 460: game.camGame.zoom = 1.6;
        case 464:
            feIntroSkipped = true;
            feHideIntro();
            feBlack.alpha = 0;
            feRing.visible = false;
            feLine.visible = false;
            game.dad.visible = true;
            game.camHUD.visible = true;
            game.camGame.zoom = 1;
    }
}
function onGameOver():Dynamic {
    feIntroSkipped = true;
    return Function_Continue;
}
