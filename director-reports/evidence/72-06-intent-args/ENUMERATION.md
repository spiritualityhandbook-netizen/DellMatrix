# 72-06 — producer/consumer enumeration (reproducible)

Generated at the #308 supplement head from the commands below.
Outputs are verbatim (paths trimmed to repo-relative).

## Producers — every Intent construction + args site in translate.py

    grep -c "return Intent" form/mandell/translate.py
77

    grep -n "args=" form/mandell/translate.py  (args-bearing sites)
342:        return Intent("nurture", 37, "Nurture", {"label": label_orig},
348:        return Intent("nurture", 37, "Nurture", {"pid": pid, "op": "confirm"},
354:        return Intent("nurture", 37, "Nurture", {"pid": pid, "op": "reject"},
376:            args = {"id": uid, "label": label.replace("_", " "), "words": label}
387:            args = {"cycles": max(1, int(_lbl)) if _lbl.isdigit() else 1}
389:            args = {"direction": "left" if "left" in hint else "right"}
396:            args = {"expression": expr}
404:            args = {"steps": int(_lbl) if _lbl.isdigit() else 1}
406:            args = {"direction": "left" if "left" in lower else "right"}
408:            args = {"ref": hit.get("label") or ""}
411:            args = {"condition": m.group(1) if m else "clear"}
416:            args = {"cycles": n}
426:            args = {"form": form_name}
437:            args=args,
467:                         {"source": src, "destination": dst},
477:                         {"source": src},
487:                         {"key": key},
496:                         {"old": old, "new": new},
505:                         {"key": key, "value": val},
539:                         {"key": key},
554:                             {"key": key},
569:                         {"predicate": safe_pred},
578:                         {"pattern": safe_pat},
582:        return Intent("walk", 19, "Drive", {"steps": 1}, "19[Drive] :: walk", text)
584:        return Intent("backstep", 19, "Drive", {"steps": 1}, "19[Drive] :: backstep", text)
587:        return Intent("strafe", 19, "Drive", {"direction": d, "steps": 1}, f"19[Drive] :: strafe_{d}", text)
596:        return Intent("turn", 4, "Transform", {"direction": d}, f"04[Transform] :: turn_{d}", text)
605:        return Intent("express", 5, "Tone", {"expression": "joy"}, "05[Tone] :: joy", text)
607:        return Intent("express", 5, "Tone", {"expression": "calm"}, "05[Tone] :: calm", text)
609:        return Intent("express", 5, "Tone", {"expression": "focus"}, "05[Tone] :: focus", text)
635:        return Intent("grow", 13, "Loop", {"cycles": 1}, "13[Loop] > 04[Transform] :: grow", text)
642:        return Intent("stamp", 34, "Stamp", {"mark": mark}, f"34[Stamp] :: {mark}", text)
657:        return Intent("cycle", 6, "Cycle", {"count": n}, f"06[Cycle] :: {n}", text)
661:        return Intent("form", 15, "Map", {"form": form_name}, f"15[Map] :: {form_name}", text)
699:            return Intent(name.lower(), n, name, {"label": label}, mandel, text)

## Consumers — every intent.args read in the router

    grep -n "intent.args" form/mandell/semantic_router.py
110:        cycles = int((intent.args or {}).get("cycles", 1))
143:    mark = str((intent.args or {}).get("mark", "")).strip()[:48] or "mark"
151:        n = int((intent.args or {}).get("count", 1))
159:    form_name = str((intent.args or {}).get("form", "")).strip().lower()
201:            "the direct handler. Cycles carried from intent.args (default 1). "

## Consumers — REPL direct-handler arg reads

    grep -n "args.get" form/repl.py
2940:            uid = args.get("id", "idea")
2941:            label = args.get("label", uid)
2942:            p.place(uid, label, words=args.get("words", ""), skin=Skin.CUBE)
3022:        steps = int(args.get("steps", 1))
3059:        pos = p.avatar.backstep(int(args.get("steps", 1)))
3070:        direction = str(args.get("direction", "right")).lower()
3072:        pos = p.avatar.strafe(side, int(args.get("steps", 1)))
3089:        direction = args.get("direction", "right")
3096:        d = str(args.get("direction", "n")).lower()
3123:        name = args.get("expression", "neutral")
3215:        q = (args.get("query") or intent.english or raw_line or "").strip()

## Consumers — dead-arg sweep (must be empty)

    grep -rn "args.get(\"ref\"|args.get(\"condition\"" form/ gui/
(no matches — zoom.ref and weather.condition have no consumer)

## Reporting-only consumer

    grep -n "intent.args" form/mandell/bridge.py
75:        out["args"] = intent.args
