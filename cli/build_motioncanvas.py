"""Target: Motion Canvas (generator-based, TypeScript).

Catatan jujur: Motion Canvas memakai model sekuensial (generator `yield*`), bukan model
"nilai = f(frame)". Compiler ini menerjemahkan timeline absolut jadi generator dengan
`waitFor` di depan setiap tween, sehingga hasilnya setara. Preset mask/blur tidak punya
padanan 1:1 di API inti → di-fallback ke opacity + diberi komentar TODO.
"""
from __future__ import annotations

import json
import os

from jsassets import MC_EASE_MAP


def _s(frames, fps):
    return round(frames / fps, 4)


def build(scene, out_dir, score=100):
    comp = scene["composition"]
    theme = scene["theme"] or {}
    fps, dur = comp["fps"], comp["durationInFrames"]
    name = scene["meta"]["name"]
    camel = name[0].lower() + name[1:]
    accent = theme.get("accent", "#7C5CFF")

    lines_create, lines_init, anims = [], [], []
    used_eases = set()
    needs = {"Txt": False, "Rect": False, "Circle": False, "Line": False, "Img": False, "signal": False}

    for i, L in enumerate(scene["layers"]):
        c = L["content"]
        ref = f"ref{i}"
        t = L["type"]
        base_pos = (L["x"], L["y"])

        if t == "text":
            needs["Txt"] = True
            txt = c["text"]
            lines_create.append(
                f'  const {ref} = createRef<Txt>();\n'
                f'  view.add(<Txt ref={{{ref}}} text={json.dumps(txt)} y={{{base_pos[1]}}} x={{{base_pos[0]}}} '
                f'fontSize={{{c["fontSize"]}}} fontWeight={{{c["fontWeight"]}}} fill={json.dumps(c["color"])} '
                f'width={{{c["maxWidth"]}}} textAlign={json.dumps("center" if c["align"] == "center" else c["align"])} '
                f'lineHeight={{{c["lineHeight"]}}} fontFamily={json.dumps("Inter")} />);')
        elif t == "shape":
            shape = c["shape"]
            if shape == "circle":
                needs["Circle"] = True
                lines_create.append(
                    f'  const {ref} = createRef<Circle>();\n'
                    f'  view.add(<Circle ref={{{ref}}} size={{{c["w"]}}} x={{{base_pos[0]}}} y={{{base_pos[1]}}} '
                    f'fill={json.dumps(c["fill"])} />);')
            elif shape == "line":
                needs["Line"] = True
                lines_create.append(
                    f'  const {ref} = createRef<Line>();\n'
                    f'  view.add(<Line ref={{{ref}}} points={{[[{-c["w"] / 2}, 0], [{c["w"] / 2}, 0]]}} '
                    f'lineWidth={{{c.get("strokeWidth") or 4}}} stroke={json.dumps(c.get("stroke") or c["fill"])} '
                    f'x={{{base_pos[0]}}} y={{{base_pos[1]}}} />);')
            else:
                needs["Rect"] = True
                lines_create.append(
                    f'  const {ref} = createRef<Rect>();\n'
                    f'  view.add(<Rect ref={{{ref}}} width={{{c["w"]}}} height={{{c["h"]}}} '
                    f'x={{{base_pos[0]}}} y={{{base_pos[1]}}} fill={json.dumps(c["fill"])} '
                    f'radius={{{c.get("radius", 0)}}} '
                    + (f'stroke={json.dumps(c["stroke"])} lineWidth={{{c.get("strokeWidth") or 2}}} ' if c.get("stroke") else "")
                    + '/>);')
        elif t == "counter":
            needs["Txt"] = True
            needs["signal"] = True
            g = c.get("grow") or {"start": 0, "dur": max(12, min(L["dur"], 36))}
            lines_create.append(
                f'  const {ref}Value = createSignal({c["from_value"]});\n'
                f'  const {ref} = createRef<Txt>();\n'
                f'  view.add(<Txt ref={{{ref}}} text={{() => {json.dumps(c.get("prefix", ""))} + '
                f'Math.round({ref}Value()).toString() + {json.dumps(c.get("suffix", ""))}}} '
                f'x={{{base_pos[0]}}} y={{{base_pos[1]}}} fontSize={{{c["fontSize"]}}} '
                f'fontWeight={{{c["fontWeight"]}}} fill={json.dumps(c["color"])} />);')
            anims.append((L["from"] + g.get("start", 0),
                          f'  yield* {ref}Value({c["to_value"]}, {_s(g.get("dur", 24), fps)}, easeOutExpo);'))
        elif t == "chart":
            needs["Rect"] = True
            needs["Txt"] = True
            vals = c.get("values") or []
            labels = c.get("labels") or []
            maxv = max(vals + [1])
            n = max(1, len(vals))
            slot = c["w"] / n
            barw = min(slot * 0.52, 96)
            g = c.get("grow") or {"start": 4, "durationFrames": 26, "intervalFrames": 4}
            for j, v in enumerate(vals):
                needs["Rect"] = True
                lines_create.append(
                    f'  const {ref}bar{j} = createRef<Rect>();\n'
                    f'  view.add(<Rect ref={{{ref}bar{j}}} width={{{barw:.1f}}} '
                    f'height={{{(v / maxv) * (c["h"] - 46):.1f}}} fill={json.dumps(c["color"])} '
                    f'radius={{{6}}} x={{{base_pos[0] - c["w"] / 2 + slot * j + slot / 2 - barw / 2:.1f}}} '
                    f'y={{{base_pos[1] + c["h"] / 2 - 34 - ((v / maxv) * (c["h"] - 46)) / 2:.1f}}} '
                    f'offset={{[0, 1]}} scale={{new Vector2(1, 0)}} />);')
                start = (g.get("start") or 0) + j * (g.get("intervalFrames") or 4)
                anims.append((L["from"] + start,
                              f'  yield* {ref}bar{j}.scale(new Vector2(1, 1), '
                              f'{_s(g.get("durationFrames") or 26, fps)}, easeOutQuint);'))
                if j < len(labels):
                    needs["Txt"] = True
                    lines_create.append(
                        f'  view.add(<Txt text={json.dumps(labels[j])} fontSize={{{max(22, round(c["w"] / 30))}}} fill={json.dumps(c.get("labelColor", "#A1A1AA"))} '
                        f'x={{{base_pos[0] - c["w"] / 2 + slot * j + slot / 2:.1f}}} y={{{base_pos[1] + c["h"] / 2 - 6:.1f}}} />);')
        elif t == "image":
            needs["Img"] = True
            lines_create.append(
                f'  const {ref} = createRef<Img>();\n'
                f'  view.add(<Img ref={{{ref}}} src={json.dumps(c["src"].replace("assets/", "../assets/"))} '
                f'width={{{c["w"]}}} height={{{c["h"]}}} x={{{base_pos[0]}}} y={{{base_pos[1]}}} />);')

        # ---- inisialisasi nilai awal
        tr = L.get("tracks") or {}
        if "opacity" in tr:
            lines_init.append(f'  {ref}().opacity({tr["opacity"][0]["from"]});')
        if "scale" in tr:
            lines_init.append(f'  {ref}().scale({tr["scale"][0]["from"]});')
        if "rotate" in tr:
            lines_init.append(f'  {ref}().rotation({tr["rotate"][0]["from"] + L["rotate"]});')
        for prop in ("x", "y"):
            if prop in tr:
                k = tr[prop][0]
                lines_init.append(f'  {ref}().{prop}({base_pos[0] if prop == "x" else base_pos[1]} + {k["from"]});')

        # ---- tween
        for prop, keys in tr.items():
            for k in keys:
                start_abs = L["from"] + k["start"]
                d = _s(k["dur"], fps)
                mc_ease = MC_EASE_MAP.get(k["ease"], "easeOutCubic")
                used_eases.add(mc_ease)
                if prop == "opacity":
                    anims.append((start_abs, f'  yield* {ref}().opacity({k["to"]}, {d}, {mc_ease});'))
                elif prop == "scale":
                    anims.append((start_abs, f'  yield* {ref}().scale({k["to"]}, {d}, {mc_ease});'))
                elif prop == "rotate":
                    anims.append((start_abs, f'  yield* {ref}().rotation({k["to"] + L["rotate"]}, {d}, {mc_ease});'))
                elif prop in ("x", "y"):
                    basev = base_pos[0] if prop == "x" else base_pos[1]
                    anims.append((start_abs,
                                  f'  yield* {ref}().{prop}({basev} + {k["to"]}, {d}, {mc_ease});'))
                else:
                    anims.append((start_abs,
                                  f'  // TODO: properti "{prop}" belum punya padanan 1:1 di Motion Canvas core '
                                  f'({k["from"]} → {k["to"]} selama {k["dur"]}f)'))

    anims.sort(key=lambda a: a[0])

    # generator: semua animasi paralel, masing-masing menunggu start-nya
    gen_lines, todo_lines = [], []
    for start, code in anims:
        text = code.strip()
        if text.startswith("//"):
            todo_lines.append(f'  // TODO @ {_s(start, fps)}s — {text.split("//", 1)[1].strip()}')
            continue
        if text.startswith("yield*"):
            text = text[len("yield*"):].strip()
        gen_lines.append(f'    (function* () {{ yield* waitFor({_s(start, fps)}); yield* {text} }})(),')

    imports_2d = sorted(k for k in ("Txt", "Rect", "Circle", "Line", "Img") if needs[k])
    imports_core = ["all", "createRef", "createSignal", "waitFor", "Vector2"] + sorted(used_eases - {"linear"})
    if "linear" in used_eases:
        imports_core.append("linear")

    ts = f"""import {{makeScene2D{(', ' + ', '.join(imports_2d)) if imports_2d else ''}}} from '@motion-canvas/2d';
import {{{', '.join(sorted(set(imports_core)))}}} from '@motion-canvas/core';

/**
 * {name} — scene Motion Canvas
 * Digenerate MOTION SKILL (credit: rajxzdev · Apache-2.0) · {comp['width']}×{comp['height']} @ {fps}fps
 * Durasi: {_s(dur, fps)} s. Smoothness score: {score}/100
 *
 * Semua tween dijalankan paralel dengan `waitFor()` di depan, jadi timing absolut
 * dari scene.json tetap terjaga.
 */
export default makeScene2D(function* (view) {{
  view.fill({json.dumps(comp.get('background', '#0B0B10'))});

{chr(10).join(lines_create)}

{chr(10).join(todo_lines) if todo_lines else ''}

  // nilai awal (state sebelum animasi masuk)
{chr(10).join(lines_init) if lines_init else '  // (tidak ada nilai awal khusus)'}

  yield* all(
{chr(10).join(gen_lines) if gen_lines else '    (function* () { yield; })(),'}
  );

  // tahan sampai akhir komposisi
  yield* waitFor({_s(max(1, dur - max([a[0] for a in anims], default=0)), fps)});
}});
"""
    out = os.path.join(out_dir, "src", "scenes")
    os.makedirs(out, exist_ok=True)
    scene_file = os.path.join(out, f"{camel}.tsx")
    with open(scene_file, "w", encoding="utf-8") as fh:
        fh.write(ts)

    readme = f"""# {name} — Motion Canvas target

Digenerate **MOTION SKILL** (credit: rajxzdev · Apache-2.0).

```bash
npm init @motion-canvas@latest   # buat project Motion Canvas
# lalu salin src/scenes/{camel}.tsx ke project kamu
npm start                        # editor + preview
```

## Status konversi

| Fitur | Dukungan |
| --- | --- |
| opacity / x / y / scale / rotation | ✅ tween akurat (`waitFor` + easing) |
| counter | ✅ via `createSignal` + `text={{() => ...}}` |
| chart | ✅ bar `scale.y` bertahap |
| clip / mask (`maskUp`, `wipeRight`) | ⚠️ tidak ada padanan core → komentar TODO |
| blur | ⚠️ butuh `@motion-canvas/ffmpeg` / filter, TODO |

Motion Canvas memakai model generator (sekuensial) — kalau kamu butuh animasi
yang nilainya fungsi murni dari frame, target **Remotion** atau **HyperFrames** lebih pas.
"""
    with open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(readme)
    return scene_file
