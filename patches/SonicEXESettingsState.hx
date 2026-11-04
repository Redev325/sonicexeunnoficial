package states;

import flixel.FlxG;
import flixel.FlxSprite;
import flixel.text.FlxText;
import flixel.util.FlxColor;
import options.ControlsSubState;
import options.VisualsUISubState;
import options.GameplaySettingsSubState;
import options.GraphicsSettingsSubState;

class SonicEXESettingsState extends MusicBeatState
{
	var categories:Array<String> = ["CONTROLS", "VISUALS", "GAMEPLAY", "GRAPHICS", "LANGUAGE", "GAMEJOLT"];
	var selected:Int = 3;
	var categoryShadows:Array<FlxSprite> = [];
	var categoryLabels:Array<FlxText> = [];
	var infoMode:Bool = false;
	var infoShade:FlxSprite;
	var infoText:FlxText;
	var pulseTime:Float = 0;
	var background:FlxSprite;
	var backgroundBaseScaleX:Float = 1;
	var backgroundBaseScaleY:Float = 1;
	var backgroundTint:FlxSprite;
	var watermark:FlxSprite;
	var watermarkBaseY:Float = 0;

	override public function create():Void
	{
		super.create();
		FlxG.mouse.visible = false;
		// Use the original Options track, replacing the main-menu theme while this state is open.
		FlxG.sound.playMusic(Paths.music("options"), 0.72, true);

		background = new FlxSprite();
		background.loadGraphic(Paths.image("sonicexe-options/bg"));
		background.setGraphicSize(Std.int(FlxG.width * 1.08), Std.int(FlxG.height * 1.08));
		background.updateHitbox();
		backgroundBaseScaleX = background.scale.x;
		backgroundBaseScaleY = background.scale.y;
		background.screenCenter();
		background.color = 0xFFB02C2C;
		background.scrollFactor.set(0, 0);
		add(background);

		// A restrained red overlay pulses over the original still artwork to animate the backdrop.
		backgroundTint = new FlxSprite().makeGraphic(1, 1, 0xFF9D0D1D);
		backgroundTint.setGraphicSize(FlxG.width, FlxG.height);
		backgroundTint.updateHitbox();
		backgroundTint.alpha = 0.09;
		backgroundTint.scrollFactor.set(0, 0);
		add(backgroundTint);

		watermark = new FlxSprite();
		watermark.loadGraphic(Paths.image("sonicexe-title/logo/ring"));
		watermark.setGraphicSize(Std.int(FlxG.width * 0.58));
		watermark.updateHitbox();
		watermark.screenCenter();
		watermark.y = FlxG.height * 0.18;
		watermarkBaseY = watermark.y;
		watermark.color = 0xFF641919;
		watermark.alpha = 0.19;
		watermark.scrollFactor.set(0, 0);
		add(watermark);

		var header:FlxSprite = new FlxSprite();
		header.loadGraphic(Paths.image("sonicexe-options/optionsTitle"));
		header.setGraphicSize(Std.int(FlxG.width * 0.40));
		header.updateHitbox();
		header.x = (FlxG.width - header.width) * 0.5;
		header.y = FlxG.height * 0.025;
		header.scrollFactor.set(0, 0);
		add(header);

		for (i in 0...categories.length)
		{
			var column:Int = i % 2;
			var row:Int = Std.int(i / 2);
			var panelWidth:Int = Std.int(FlxG.width * 0.245);
			var panelHeight:Int = Std.int(FlxG.height * 0.07);
			var x:Float = FlxG.width * (column == 0 ? 0.225 : 0.53);
			var y:Float = FlxG.height * (0.27 + row * 0.155);

			var shadow:FlxSprite = new FlxSprite(x + 4, y + 4);
			shadow.loadGraphic(Paths.image("sonicexe-options/sectionBGWhite"));
			shadow.setGraphicSize(panelWidth, panelHeight);
			shadow.updateHitbox();
			shadow.scrollFactor.set(0, 0);
			shadow.alpha = 0;
			categoryShadows.push(shadow);
			add(shadow);

			var plate:FlxSprite = new FlxSprite(x, y);
			plate.loadGraphic(Paths.image("sonicexe-options/sectionBGClone"));
			plate.setGraphicSize(panelWidth, panelHeight);
			plate.updateHitbox();
			plate.color = 0xFF070707;
			plate.scrollFactor.set(0, 0);
			add(plate);

			var label:FlxText = new FlxText(x + 4, y + 1, panelWidth - 8, categories[i], Std.int(FlxG.height * 0.033));
			label.setFormat(Paths.font("sonichud.ttf"), Std.int(FlxG.height * 0.033), FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
			label.scrollFactor.set(0, 0);
			label.y = y + (panelHeight - label.height) * 0.5 - 1;
			categoryLabels.push(label);
			add(label);
		}

		changeSelection(0);
		ClientPrefs.saveSettings();
	}

	function changeSelection(change:Int):Void
	{
		selected = (selected + change) % categories.length;
		if (selected < 0)
			selected += categories.length;

		for (i in 0...categories.length)
		{
			var active:Bool = (i == selected);
			categoryShadows[i].alpha = active ? 1 : 0;
			categoryLabels[i].color = active ? 0xFFFFE7A6 : FlxColor.WHITE;
			categoryLabels[i].alpha = active ? 1 : 0.86;
		}
		if (change != 0)
			FlxG.sound.play(Paths.sound("scrollMenu"));
	}

	function openInfo(title:String, message:String):Void
	{
		infoMode = true;
		infoShade = new FlxSprite(FlxG.width * 0.21, FlxG.height * 0.34);
		infoShade.makeGraphic(Std.int(FlxG.width * 0.58), Std.int(FlxG.height * 0.32), 0xEE080808);
		infoShade.scrollFactor.set(0, 0);
		add(infoShade);

		infoText = new FlxText(FlxG.width * 0.25, FlxG.height * 0.375, FlxG.width * 0.50, title + "\n\n" + message + "\n\nPRESS BACK TO RETURN", Std.int(FlxG.height * 0.03));
		infoText.setFormat(Paths.font("sonichud.ttf"), Std.int(FlxG.height * 0.03), FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
		infoText.scrollFactor.set(0, 0);
		add(infoText);
	}

	function closeInfo():Void
	{
		if (infoShade != null)
			remove(infoShade, true);
		if (infoText != null)
			remove(infoText, true);
		infoMode = false;
	}

	function openCategory():Void
	{
		FlxG.sound.play(Paths.sound("confirmMenu"));
		switch (selected)
		{
			case 0: openSubState(new ControlsSubState());
			case 1: openSubState(new VisualsUISubState());
			case 2: openSubState(new GameplaySettingsSubState());
			case 3: openSubState(new GraphicsSettingsSubState());
			case 4: openInfo("LANGUAGE", "ENGLISH IS THE LANGUAGE INCLUDED IN THIS BROWSER BUILD.");
			case 5: openInfo("GAMEJOLT", "GAMEJOLT CONNECTION IS NOT AVAILABLE IN THIS BROWSER BUILD.");
		}
	}

	override public function update(elapsed:Float):Void
	{
		super.update(elapsed);
		pulseTime += elapsed;
		// Animate the original red artwork with a gentle camera-like zoom, pan, and rotation.
		// The artwork has generous overscan, so the movement never exposes empty edges.
		var backgroundZoom:Float = 1.0 + Math.sin(pulseTime * 0.34) * 0.008;
		background.scale.set(backgroundBaseScaleX * backgroundZoom, backgroundBaseScaleY * backgroundZoom);
		background.updateHitbox();
		background.x = (FlxG.width - background.width) * 0.5 + Math.sin(pulseTime * 0.31) * FlxG.width * 0.022;
		background.y = (FlxG.height - background.height) * 0.5 + Math.cos(pulseTime * 0.23) * FlxG.height * 0.016;
		background.angle = Math.sin(pulseTime * 0.16) * 0.45;
		backgroundTint.alpha = 0.065 + (Math.sin(pulseTime * 0.78) + 1) * 0.035;
		watermark.y = watermarkBaseY + Math.sin(pulseTime * 0.42) * 7;
		watermark.alpha = 0.16 + (Math.sin(pulseTime * 0.72) + 1) * 0.025;

		if (infoMode)
		{
			if (controls.BACK || controls.ACCEPT)
				closeInfo();
			return;
		}

		categoryShadows[selected].alpha = 0.82 + Math.sin(pulseTime * 3.0) * 0.18;
		if (controls.BACK)
		{
			FlxG.sound.play(Paths.sound("cancelMenu"));
			FlxG.sound.playMusic(Paths.music("menu"), 0.7, true);
			MusicBeatState.switchStateWithSonicTransition(new MainMenuState());
			return;
		}
		if (controls.UI_UP_P) changeSelection(-2);
		if (controls.UI_DOWN_P) changeSelection(2);
		if (controls.UI_LEFT_P) changeSelection(-1);
		if (controls.UI_RIGHT_P) changeSelection(1);
		if (controls.ACCEPT) openCategory();
	}

	override public function closeSubState():Void
	{
		super.closeSubState();
		ClientPrefs.saveSettings();
	}
}
