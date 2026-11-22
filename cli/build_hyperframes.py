"""Target: HyperFrames (heygen) / OpenMotion — HTML + timeline seekable GSAP.

Kontrak yang dipatuhi:
  * root: data-composition-id, data-width, data-height, data-fps, data-duration (detik)
  * tiap elemen bertiming: class="clip" + data-start + data-duration + data-track-index
  * animasi: satu timeline GSAP **paused**, didaftarkan di window.__timelines[id]
  * tidak ada wall-clock, tidak ada Math.random → render deterministik
"""
from __future__ import annotations

import html
import json
import os

from jsassets import GSAP_EASE_MAP


def _sec(frames, fps):
    return round(frames / fps, 4)


def _css_text_style(c):
    bits = [
        f"font-family:{c['fontFamily']}",
        f"font-size:{c['fontSize']}px",
        f"font-weight:{c['fontWeight']}",
        f"color:{c['color']}",
        f"line-height:{c['lineHeight']}",
        f"letter-spacing:{c['letterSpacing']}px",
        f"text-align:{c['align']}",
        f"width:{c['maxWidth']}px",
        "white-space:pre-wrap",
        "margin:0",
    ]
    if c.get("italic"):
        bits.append("font-style:italic")
    if c.get("uppercase"):
        bits.append("text-transform:uppercase")
    return ";".join(bits)


def _inner_html(layer, theme):
    c = layer["content"]
    t = layer["type"]
    if t == "text":
        text = html.escape(c["text"])
        if layer.get("wordTracks"):
            parts = []
            words = layer["wordTracks"]["words"]
            for i, w in enumerate(words):
                if w.get("br"):
                    parts.append("<br>")
                    continue
                nxt = words[i + 1] if i + 1 < len(words) else None
                sp = " " if (layer["wordTracks"]["mode"] == "word" and nxt and not nxt.get("br")) else ""
                parts.append(
                    f'<span class="word" id="w-{layer["id"]}-{i}" '
                    f'style="display:inline-block;white-space:pre">{html.escape(w["text"])}{sp}</span>')
            return "".join(parts)
        if c.get("highlight") and c["highlight"].get("word"):
            w = c["highlight"]["word"]
            if w in c["text"]:
                i = c["text"].index(w)
                col = c["highlight"].get("color") or theme.get("accent", "#7C5CFF")
                return (html.escape(c["text"][:i]) +
                        f'<span style="color:{col}">{html.escape(w)}</span>' +
                        html.escape(c["text"][i + len(w):]))
        return text
    if t == "shape":
        return ""
    if t == "counter":
        return html.escape((c.get("prefix") or "")) + html.escape((c.get("suffix") or ""))
    if t == "chart":
        vals = c.get("values") or []
        labels = c.get("labels") or []
        maxv = max(vals + [1])
        n = max(1, len(vals))
        slot = c["w"] / n
        barw = min(slot * 0.52, 96)
        parts = []
        for i, v in enumerate(vals):
            left = slot * i + slot / 2 - barw / 2
            parts.append(
                f'<div class="bar" id="bar-{layer["id"]}-{i}" style="left:{left:.2f}px;width:{barw:.2f}px;'
                f'height:{(v / maxv) * (c["h"] - 46):.2f}px;background:linear-gradient(180deg,{c["color"]},{c["color"]}88);'
                f'transform-origin:bottom center"></div>')
            if i < len(labels):
                parts.append(
                    f'<div style="position:absolute;bottom:6px;left:{slot * i + slot / 2:.2f}px;'
                    f'transform:translateX(-50%);font-size:{max(22, round(c["w"] / 30))}px;'
                    f'color:{c.get("labelColor", "#A1A1AA")}">'
                    f'{html.escape(labels[i])}</div>')
        return "".join(parts)
    if t == "image":
        return f'<img src="{html.escape(c["src"])}" style="width:{c["w"]}px;height:{c["h"]}px;object-fit:{c["fit"]};display:block">'
    return ""


def _anim_style(layer):
    c = layer.get("content") or {}
    if layer["type"] == "shape":
        s = c
        base = f"width:{s['w']}px;height:{s['h']}px;"
        if s["shape"] == "circle":
            base += f"border-radius:50%;background:{s['fill'] if s.get('fill') != 'transparent' else 'transparent'};"
            if s.get("stroke"):
                base += f"border:{s.get('strokeWidth') or 2}px solid {s['stroke']};"
        elif s["shape"] == "line":
            base += f"height:{s.get('strokeWidth') or 4}px;border-radius:99px;background:{s.get('stroke') or s['fill']};"
        elif s["shape"] == "triangle":
            base += f"background:{s['fill'] if s.get('fill') != 'transparent' else 'transparent'};clip-path:polygon(50% 0,100% 100%,0 100%);"
        else:
            base += f"background:{s['fill'] if s.get('fill') != 'transparent' else 'transparent'};border-radius:{s.get('radius', 0)}px;"
            if s.get("stroke"):
                base += f"border:{s.get('strokeWidth') or 2}px solid {s['stroke']};"
        if s.get("blur"):
            base += f"filter:blur({s['blur']}px);"
        if s.get("shadow"):
            base += f"box-shadow:{s['shadow']};"
        return base
    if layer["type"] == "chart":
        return f"position:relative;width:{c['w']}px;height:{c['h']}px;"
    if layer["type"] == "counter":
        return ("font-family:%s;font-size:%spx;font-weight:%s;color:%s;font-variant-numeric:tabular-nums;"
                "letter-spacing:-0.03em;white-space:nowrap;" %
                (c["fontFamily"], c["fontSize"], c["fontWeight"], c["color"]))
    return ""


def _tween(layer, prop, kf, fps, target, is_word=False):
    """Hasilkan satu baris GSAP tween."""
    ease = GSAP_EASE_MAP.get(kf["ease"], "power3.out")
    pos = _sec(layer["from"] + kf["start"], fps)
    dur = _sec(kf["dur"], fps)
    if prop in ("clipTop", "clipRight", "clipBottom", "clipLeft"):
        var = {"clipTop": "--ct", "clipRight": "--cr", "clipBottom": "--cb", "clipLeft": "--cl"}[prop]
        return (f'  tl.fromTo("{target}", {{"{var}": "{kf["from"]:.3f}%"}}, '
                f'{{"{var}": "{kf["to"]:.3f}%", duration: {dur}, ease: "{ease}"}}, {pos});')
    if prop == "blur":
        return (f'  tl.fromTo("{target}", {{filter: "blur({kf["from"]:.2f}px)"}}, '
                f'{{filter: "blur({kf["to"]:.2f}px)", duration: {dur}, ease: "{ease}"}}, {pos});')
    if prop == "letterSpacing":
        return (f'  tl.fromTo("{target}", {{letterSpacing: "{kf["from"]:.2f}px"}}, '
                f'{{letterSpacing: "{kf["to"]:.2f}px", duration: {dur}, ease: "{ease}"}}, {pos});')
    gsap_prop = {"x": "x", "y": "y", "scale": "scale", "scaleX": "scaleX", "scaleY": "scaleY",
                 "rotate": "rotation", "opacity": "opacity"}[prop]
    return (f'  tl.fromTo("{target}", {{"{gsap_prop}": {kf["from"]:.4f}}}, '
            f'{{"{gsap_prop}": {kf["to"]:.4f}, duration: {dur}, ease: "{ease}"}}, {pos});')


def build(scene, out_dir, score=100):
    comp = scene["composition"]
    theme = scene["theme"] or {}
    fps, dur = comp["fps"], comp["durationInFrames"]
    name = scene["meta"]["name"]
    accent = theme.get("accent", "#7C5CFF")
    bg = comp.get("background", "#0B0B10")
    font = theme.get("font", "Inter, system-ui, sans-serif")

    clips_html, js_lines, sets = [], [], []

    for L in scene["layers"]:
        c = L["content"]
        inner_css = _anim_style(L)
        if L["type"] == "text":
            inner_css = _css_text_style(c)
        var_defaults = "--ct:0%;--cr:0%;--cb:0%;--cl:0%"
        base_pos = f"left:50%;top:50%;transform:translate(-50%,-50%)"
        clip_style = (f"{base_pos};width:max-content;opacity:{L['opacity']};"
                      f"z-index:{10 + L['track']}")
        inner_css = inner_css.replace(";;", ";").rstrip(";")
        anim_style = f"{inner_css};clip-path:inset(var(--ct) var(--cr) var(--cb) var(--cl));{var_defaults}"
        if L.get("blendMode"):
            anim_style += f";mix-blend-mode:{L['blendMode']}"

        clips_html.append(
            f'    <div class="clip" id="c-{L["id"]}" data-start="{_sec(L["from"], fps)}" '
            f'data-duration="{_sec(L["dur"], fps)}" data-track-index="{L["track"]}" style="{clip_style}">\n'
            f'      <div class="anim" id="a-{L["id"]}" style="{anim_style}">{_inner_html(L, theme)}</div>\n'
            f'    </div>')

        target = f"#a-{L['id']}"
        if L["x"] or L["y"] or L["rotate"] or L["opacity"] != 1:
            sets.append(f'  gsap.set("{target}", {{x: {L["x"]:.3f}, y: {L["y"]:.3f}, '
                        f'rotation: {L["rotate"]:.3f}, opacity: {L["opacity"]:.3f}}});')

        # keyframe per properti
        for prop, keys in (L.get("tracks") or {}).items():
            for kf in keys:
                js_lines.append(_tween(L, prop, kf, fps, target))

        # stagger per kata
        if L.get("wordTracks"):
            for w in L["wordTracks"]["words"]:
                wt = f"#w-{L['id']}-{w['index']}"
                for prop, keys in w["tracks"].items():
                    for kf in keys:
                        js_lines.append(_tween(L, prop, kf, fps, wt))

        # counter
        if L["type"] == "counter":
            g = c.get("grow") or {"start": 0, "dur": max(12, min(L["dur"], 36))}
            pos = _sec(L["from"] + g["start"], fps)
            d = _sec(g["dur"], fps)
            decimals = c.get("decimals", 0)
            js_lines.append(
                f'  var c{L["id"].replace("-", "_")} = {{v: {c["from_value"]}}};\n'
                f'  tl.fromTo(c{L["id"].replace("-", "_")}, {{v: {c["from_value"]}}}, {{v: {c["to_value"]}, duration: {d}, '
                f'ease: "expo.out", onUpdate: function(){{ var n = c{L["id"].replace("-", "_")}.v; '
                f'document.getElementById("a-{L["id"]}").textContent = {json.dumps(c.get("prefix", ""))} + '
                f'n.toFixed({decimals}) + {json.dumps(c.get("suffix", ""))}; }}}}, {pos});')

        # chart
        if L["type"] == "chart":
            g = c.get("grow") or {"start": 4, "durationFrames": 26, "intervalFrames": 4}
            for i in range(len(c.get("values") or [])):
                start = (g.get("start") or 0) + i * (g.get("intervalFrames") or 4)
                pos = _sec(L["from"] + start, fps)
                d = _sec(g.get("durationFrames") or 26, fps)
                js_lines.append(
                    f'  tl.fromTo("#bar-{L["id"]}-{i}", {{scaleY: 0}}, '
                    f'{{scaleY: 1, duration: {d}, ease: "power4.out"}}, {pos});')

    doc = f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(name)} — HyperFrames composition (MOTION SKILL)</title>
<style>
  :root {{ --accent: {accent}; }}
  html, body {{ margin: 0; height: 100%; background: #05050A; }}
  *, *::before, *::after {{ box-sizing: border-box; }}
  body {{ display: flex; align-items: center; justify-content: center; }}
  #stage {{
    position: relative; overflow: hidden; background: {bg};
    width: {comp['width']}px; height: {comp['height']}px;
    font-family: {font};
    -webkit-font-smoothing: antialiased;
  }}
  .clip {{ position: absolute; }}
  .anim {{ will-change: transform, opacity, filter, clip-path; }}
  .bar {{ position: absolute; bottom: 34px; border-radius: 6px 6px 2px 2px; }}
</style>
</head>
<body>
  <div id="stage"
       data-composition-id="{html.escape(name)}"
       data-width="{comp['width']}"
       data-height="{comp['height']}"
       data-fps="{fps}"
       data-duration="{_sec(dur, fps)}">
{chr(10).join(clips_html)}
  </div>

  <!-- GSAP: untuk produksi, pasang lokal (`npm i gsap`) dan ganti src di bawah.
       HyperFrames butuh timeline PAUSED yang di-seek per frame. -->
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
  <script>
  (function () {{
    var tl = gsap.timeline({{ paused: true }});
{chr(10).join(sets)}
{chr(10).join(js_lines)}
    tl.to({{}}, {{ duration: {_sec(dur, fps)} }}); // padding durasi komposisi
    window.__timelines = window.__timelines || {{}};
    window.__timelines[{json.dumps(name)}] = tl;
  }})();
  </script>
</body>
</html>
"""
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "index.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(doc)

    readme = f"""# {name} — HyperFrames composition

Dihasilkan oleh **MOTION SKILL** (credit: rajxzdev, Apache-2.0) dari scene `{name}`.

- Canvas: `{comp['width']}×{comp['height']}` @ `{fps} fps` — `{_sec(dur, fps)} s`
- Smoothness score: **{score}/100**

## Jalankan

```bash
# di dalam folder proyek HyperFrames-mu
npx hyperframes check .          # validasi komposisi
npx hyperframes preview          # studio + live reload
npx hyperframes render --quality high -o {name}.mp4

# atau lewat HeyGen cloud (tanpa Chrome/FFmpeg lokal)
npx hyperframes cloud render
```

Tidak ada dependency build step: `index.html` bisa dibuka langsung di browser
(butuh internet untuk CDN GSAP — untuk render offline, `npm i gsap` dan ganti
`<script src>` ke `./node_modules/gsap/dist/gsap.min.js`).

## Penting

| Aturan | Status |
| --- | --- |
| Timeline **paused** | ✅ `gsap.timeline({{paused:true}})` |
| Didaftarkan di `window.__timelines["{name}"]` | ✅ |
| Timing tiap clip pakai `data-start` / `data-duration` / `data-track-index` (detik) | ✅ |
| Tanpa wall-clock / `Math.random` | ✅ semua nilai turunan dari seek timeline |

## Ubah isi

Semua teks/angka ada di HTML. Warna di `:root` + inline style.
Kalau perlu ubah timing, ubah juga di scene JSON lalu build ulang supaya layout
preview (`preview.html`) tetap sinkron.
"""
    with open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(readme)
    return out
