#!/usr/bin/env python3
"""Fail the browser build if core Sonic.EXE songs have incomplete runtime dependencies."""
from pathlib import Path
import json, sys
ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path("engine/assets")
SONGS={
 "too-slow":{"chart":"too-slow-hard.json","stage":"too-slow","scripts":("modchart.lua","modchart.hx"),"event":"TooSlowFlashinShit"},
 "you-cant-run":{"chart":"you-cant-run-hard.json","stage":"cant-run-xd","types":("Static Note","Phantom Note")},
 "triple-trouble":{"chart":"triple-trouble-hard.json","stage":"trioStage","scripts":("triple-trouble.hx",),"types":("Static Note","Phantom Note")},
 "final-escape":{"chart":"final-escape-hard.json","stage":"final","scripts":("intro.lua","run.lua","run.hx"),"event":"runStage"},
}
def fail(msg): raise SystemExit("Sonic.EXE song asset validation failed: "+msg)
def req(p,what):
 if not p.is_file() or p.stat().st_size==0: fail(f"missing {what}: {p}")
def read_song(slug,spec):
 p=ROOT/"shared"/"data"/slug/spec["chart"]; req(p,slug+" Hard chart")
 try: d=json.loads(p.read_text(encoding="utf-8-sig"))
 except Exception as e: fail(f"invalid chart {p}: {e}")
 s=d.get("song",d)
 if not isinstance(s,dict) or not isinstance(s.get("notes"),list) or not s["notes"]: fail(slug+" has no playable note sections")
 req(ROOT/"songs"/slug/"Inst.mp3",slug+" instrumental")
 if s.get("needsVoices",False): req(ROOT/"songs"/slug/"Voices.mp3",slug+" vocals")
 return s
def names(s):
 out=[]
 for rec in s.get("events",[]) or []:
  if isinstance(rec,list) and len(rec)>1 and isinstance(rec[1],list):
   out += [str(x[0]) for x in rec[1] if isinstance(x,list) and x]
 return out
def types(s):
 out=set()
 for sec in s.get("notes",[]) or []:
  for note in sec.get("sectionNotes",[]) or []:
   if isinstance(note,list) and len(note)>3 and note[3]: out.add(str(note[3]))
 return out
loaded={}
for slug,spec in SONGS.items():
 s=read_song(slug,spec); loaded[slug]=s
 stage_path=ROOT/"shared"/"stages"/(spec["stage"]+".json"); req(stage_path,slug+" stage JSON")
 stage=json.loads(stage_path.read_text(encoding="utf-8-sig")); directory=str(stage.get("directory") or "")
 if directory=="encore":
  img=ROOT/"week_assets"/"encore"/"images"
  if not img.is_dir() or len([p for p in img.rglob("*") if p.is_file()])<20: fail(slug+" Encore backgrounds/asset folder is incomplete")
 elif directory=="exe":
  img=ROOT/"exe"/"images"/"final escape"
  for name in ("bg.png","exe line.png","checkpoint.png","ring.png"): req(img/name,slug+" background/object")
 else: fail(f"{slug} references missing/unexpected stage library '{directory}'")
 for script in spec.get("scripts",()): req(ROOT/"shared"/"data"/slug/script,slug+" script "+script)
 if spec.get("event") and spec["event"] not in names(s): fail(slug+" missing timed event "+spec["event"])
 for nt in spec.get("types",()):
  if nt not in types(s): fail(slug+" missing special note type "+nt)
for atlas in ("STATICNOTE_assets","PHANTOMNOTE_assets"):
 req(ROOT/"shared"/"images"/(atlas+".png"),atlas+" PNG")
 req(ROOT/"shared"/"images"/(atlas+".xml"),atlas+" XML")
for char in ("ycr","TailsSoul","bf-run"):
 p=ROOT/"shared"/"characters"/(char+".json"); req(p,char+" character definition")
 c=json.loads(p.read_text(encoding="utf-8-sig"))
 if c.get("image"): req(ROOT/"shared"/"images"/(c["image"]+".png"),char+" sprite")
req(ROOT/"shared"/"stages"/"trioStage.lua","Triple Trouble stage script")
req(ROOT/"shared"/"stages"/"final.lua","Final Escape stage script")
if len(names(loaded["final-escape"]))<5: fail("Final Escape events.json was not merged into its loaded chart")
print("Sonic.EXE story song assets validated:")
for slug,s in loaded.items(): print(f"  {slug}: sections={len(s['notes'])} events={len(s.get('events',[]) or [])}")
print("  Backgrounds, note atlases, character sprites, vocals and scripts are present.")
