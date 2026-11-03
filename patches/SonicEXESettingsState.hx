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

	override public function create():Void
	{
		super.create();
		FlxG.mouse.visible = false;

		var background:FlxSprite = new FlxSprite();
		background.loadGraphic(Paths.image("sonicexe-options/bg"));
		background.setGraphicSize(FlxG.width, FlxG.height);
		background.updateHitbox();
		background.color = 0xFFB02C2C;
		background.scrollFactor.set(0, 0);
		add(background);

		var watermark:FlxSprite = new FlxSprite();
		watermark.loadGraphic(Paths.image("sonicexe-title/logo/ring"));
		watermark.setGraphicSize(Std.int(FlxG.width * 0.58));
		watermark.updateHitbox();
		watermark.screenCenter();
		watermark.y = FlxG.height * 0.18;
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
			var panelWidth:Int = Std.int(FlxG.width * 0.255);
			var panelHeight:Int = Std.int(FlxG.height * 0.075);
			var x:Float = FlxG.width * (column == 0 ? 0.20 : 0.55);
			var y:Float = FlxG.height * (0.26 + row * 0.245);

			var shadow:FlxSprite = new FlxSprite(x + 6, y + 7);
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

			var label:FlxText = new FlxText(x + 4, y + 1, panelWidth - 8, categories[i], Std.int(FlxG.height * 0.043));
			label.setFormat(Paths.font("sonichud.ttf"), Std.int(FlxG.height * 0.043), FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
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
		infoShade = new FlxSprite(FlxG.width * 0.16, FlxG.height * 0.29);
		infoShade.makeGraphic(Std.int(FlxG.width * 0.68), Std.int(FlxG.height * 0.40), 0xEE080808);
		infoShade.scrollFactor.set(0, 0);
		add(infoShade);

		infoText = new FlxText(FlxG.width * 0.20, FlxG.height * 0.34, FlxG.width * 0.60, title + "\n\n" + message + "\n\nPRESS BACK TO RETURN", Std.int(FlxG.height * 0.035));
		infoText.setFormat(Paths.font("sonichud.ttf"), Std.int(FlxG.height * 0.035), FlxColor.WHITE, CENTER, FlxTextBorderStyle.OUTLINE, FlxColor.BLACK);
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
			MusicBeatState.switchState(new MainMenuState());
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
