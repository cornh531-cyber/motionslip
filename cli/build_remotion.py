"""Target: Remotion (React/TSX).

Filosofi: scene di-compile jadi komponen React murni-fungsi-dari-frame.
Tidak memakai <Sequence> untuk transform supaya nilai tetap bisa di-audit baris per baris.
"""
from __future__ import annotations

import json
import os

EASINGS = (
    "linear", "easeInQuad", "easeOutQuad", "easeInOutQuad", "easeInCubic", "easeOutCubic",
    "easeInOutCubic", "easeInQuart", "easeOutQuart", "easeInOutQuart", "easeOutQuint",
    "easeInOutQuint", "easeOutExpo", "easeInOutExpo", "easeOutCirc", "easeOutBack",
    "easeInOutBack", "easeOutElastic", "easeOutBounce", "springSoft", "springSnappy",
)

LIB_EASING = """/**
 * Easing — MOTION SKILL (credit: rajxzdev, Apache-2.0)
 * Implementasi identik dengan cli/core.py & preview runtime.
 * Semua fungsi: f(t) -> t' dengan t dinormalisasi 0..1.
 */
export type EaseName =
%s;

const clamp01 = (t: number) => (t < 0 ? 0 : t > 1 ? 1 : t);

const easeOutBack = (t: number, s = 1.70158) => {
  const c3 = s + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2);
};
const easeInOutBack = (t: number, s = 1.70158) => {
  const c2 = s * 1.525;
  return t < 0.5
    ? (Math.pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2)) / 2
    : (Math.pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2;
};
const easeOutElastic = (t: number) => {
  if (t === 0 || t === 1) return t;
  const c4 = (2 * Math.PI) / 3;
  return Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
};
const easeOutBounce = (t: number) => {
  const n1 = 7.5625;
  const d1 = 2.75;
  if (t < 1 / d1) return n1 * t * t;
  if (t < 2 / d1) return n1 * (t -= 1.5 / d1) * t + 0.75;
  if (t < 2.5 / d1) return n1 * (t -= 2.25 / d1) * t + 0.9375;
  return n1 * (t -= 2.625 / d1) * t + 0.984375;
};
const springSoft = (t: number) => {
  if (t >= 1) return 1;
  const w = 12;
  return 1 - Math.exp(-0.85 * w * t) * (1 + 0.85 * w * t * (1 - t) * 0.35);
};
const springSnappy = (t: number) => {
  if (t >= 1) return 1;
  const w = 18;
  return 1 - Math.exp(-0.62 * w * t) * Math.cos(1.35 * w * t * 0.35);
};

export const EASINGS: Record<EaseName, (t: number) => number> = {
  linear: (t) => t,
  easeInQuad: (t) => t * t,
  easeOutQuad: (t) => 1 - (1 - t) * (1 - t),
  easeInOutQuad: (t) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2),
  easeInCubic: (t) => t * t * t,
  easeOutCubic: (t) => 1 - Math.pow(1 - t, 3),
  easeInOutCubic: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  easeInQuart: (t) => t * t * t * t,
  easeOutQuart: (t) => 1 - Math.pow(1 - t, 4),
  easeInOutQuart: (t) => (t < 0.5 ? 8 * Math.pow(t, 4) : 1 - Math.pow(-2 * t + 2, 4) / 2),
  easeOutQuint: (t) => 1 - Math.pow(1 - t, 5),
  easeInOutQuint: (t) => (t < 0.5 ? 16 * Math.pow(t, 5) : 1 - Math.pow(-2 * t + 2, 5) / 2),
  easeOutExpo: (t) => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t)),
  easeInOutExpo: (t) => {
    if (t === 0 || t === 1) return t;
    return t < 0.5 ? Math.pow(2, 20 * t - 10) / 2 : (2 - Math.pow(2, -20 * t + 10)) / 2;
  },
  easeOutCirc: (t) => (t < 1 ? Math.sqrt(1 - Math.pow(t - 1, 2)) : 1),
  easeOutBack: (t) => easeOutBack(t),
  easeInOutBack: (t) => easeInOutBack(t),
  easeOutElastic,
  easeOutBounce,
  springSoft,
  springSnappy,
};

/** Helper opsional: ease('easeOutBack', 0.4) */
export const ease = (name: EaseName, t: number): number =>
  (EASINGS[name] ?? EASINGS.easeOutCubic)(clamp01(t));
"""

LIB_MOTION = """/**
 * Runtime motion — MOTION SKILL (credit: rajxzdev, Apache-2.0)
 * Semua nilai adalah fungsi murni dari frame → render deterministik & seekable.
 */
import {EASINGS, EaseName} from './easing';

export type K = {s: number; d: number; f: number; v: number; e: EaseName};

/** Nilai properti pada frame lokal layer. Keyframe belakangan menang. */
export const track = (frame: number, keys: K[] | undefined, base = 1): number => {
  if (!keys || keys.length === 0) return base;
  let value = base;
  let applied = false;
  for (const k of keys) {
    const t = (frame - k.s) / k.d;
    if (t < 0) continue;
    applied = true;
    const fn = EASINGS[k.e] ?? EASINGS.easeOutCubic;
    value = k.f + (k.v - k.f) * fn(t > 1 ? 1 : t);
  }
  return applied ? value : keys[0].f;
};

export const inset = (top: number, right: number, bottom: number, left: number) =>
  top || right || bottom || left ? `inset(${top}% ${right}% ${bottom}% ${left}%)` : undefined;

/** Counter: angka yang naik dengan easing. */
export const counter = (
  frame: number,
  start: number,
  dur: number,
  from: number,
  to: number,
  easing: EaseName = 'easeOutExpo',
  decimals = 0,
): string => {
  const t = Math.max(0, Math.min(1, (frame - start) / dur));
  const v = from + (to - from) * (EASINGS[easing] ?? EASINGS.easeOutExpo)(t);
  return v.toFixed(decimals);
};

/** Progress 0..1 untuk bar chart bertahap. */
export const grow = (frame: number, start: number, dur: number): number => {
  const t = Math.max(0, Math.min(1, (frame - start) / dur));
  return EASINGS.easeOutQuint(t);
};
"""


def _fmt(v):
    if isinstance(v, float):
        s = f"{v:.4f}".rstrip("0").rstrip(".")
        return s if s not in ("", "-") else "0"
    return str(v)


def _keys_ts(keys):
    parts = []
    for k in keys:
        parts.append("{s:%d,d:%d,f:%s,v:%s,e:'%s'}" % (
            k["start"], k["dur"], _fmt(k["from"]), _fmt(k["to"]), k["ease"]))
    return "[" + ",".join(parts) + "]"


def _style(items):
    return "{{" + ", ".join(f'"{k}": {v}' for k, v in items) + "}}"


def _text_jsx(L, var_prefix, local_var, words_jsx=None):
    c = L["content"]
    base_style = _style([
        ("fontFamily", json.dumps(c["fontFamily"])),
        ("fontSize", c["fontSize"]),
        ("fontWeight", json.dumps(str(c["fontWeight"]))),
        ("color", json.dumps(c["color"])),
        ("lineHeight", c["lineHeight"]),
        ("letterSpacing", f'`${{{var_prefix}ls}}px`'),
        ("textAlign", json.dumps(c["align"])),
        ("width", c["maxWidth"]),
        ("whiteSpace", '"pre-wrap"'),
        ("fontStyle", '"italic"' if c.get("italic") else '"normal"'),
        ("textTransform", '"uppercase"' if c.get("uppercase") else '"none"'),
    ])
    if words_jsx is not None:
        body = words_jsx
    elif c.get("highlight") and c["highlight"].get("word") and c["highlight"]["word"] in c["text"]:
        w = c["highlight"]["word"]
        i = c["text"].index(w)
        col = c["highlight"].get("color") or "#7C5CFF"
        body = (json.dumps(c["text"][:i])
                + f'<span style={{{{ color: {json.dumps(col)} }}}}>{json.dumps(w)}</span>'
                + json.dumps(c["text"][i + len(w):]))
    else:
        body = "{" + json.dumps(c["text"]) + "}"
    return f'<div style={base_style}>{body}</div>'


def _layer_tsx(idx, L, theme):
    """Hasilkan blok kode + JSX untuk satu layer."""
    c = L["content"]
    pid = f"L{idx}"
    lines = []
    lines.append(f"  // ── {L['id']} ({L['type']}) frames {L['from']}–{L['from'] + L['dur']}")
    lines.append(f"  const t_{pid} = frame - {L['from']};")
    lines.append(f"  const vis_{pid} = t_{pid} >= 0 && t_{pid} < {L['dur']};")

    props = {}
    for prop in ("opacity", "x", "y", "scale", "scaleX", "scaleY", "rotate", "blur",
                 "letterSpacing", "clipTop", "clipRight", "clipBottom", "clipLeft"):
        keys = (L.get("tracks") or {}).get(prop)
        if not keys:
            continue
        base = {"opacity": 1, "scale": 1, "scaleX": 1, "scaleY": 1, "rotate": L["rotate"]}.get(prop, 0)
        lines.append(f"  const {pid}_{prop} = track(t_{pid}, {_keys_ts(keys)}, {_fmt(base)});")
        props[prop] = f"{pid}_{prop}"

    o = props.get("opacity", "1")
    x = props.get("x", _fmt(L["x"]))
    y = props.get("y", _fmt(L["y"]))
    sc = props.get("scale", "1")
    scx = props.get("scaleX", "1")
    scy = props.get("scaleY", "1")
    rot = props.get("rotate", _fmt(L["rotate"]))
    blur = props.get("blur")
    ct, cr, cb, cl = (props.get("clipTop", "0"), props.get("clipRight", "0"),
                      props.get("clipBottom", "0"), props.get("clipLeft", "0"))

    # ---- transform: literal kalau statis, template literal kalau dianimasikan
    def is_var(v):
        return isinstance(v, str) and v.startswith(pid + "_")

    tf = ["translate(-50%,-50%)"]
    if is_var(x) or is_var(y):
        tf.append(f"translate(${{{x}}}px, ${{{y}}}px)")
    elif float(L["x"]) or float(L["y"]):
        tf.append(f'translate({_fmt(L["x"])}px, {_fmt(L["y"])}px)')
    if is_var(rot):
        tf.append(f"rotate(${{{rot}}}deg)")
    elif float(L["rotate"]):
        tf.append(f'rotate({_fmt(L["rotate"])}deg)')
    scale_parts = [v for v in (scx, scy, sc) if v != "1"]
    if any(is_var(v) for v in scale_parts):
        sx_expr = f"calc(${{{scx}}} * ${{{sc}}})"
        sy_expr = f"calc(${{{scy}}} * ${{{sc}}})"
        tf.append(f"scale({sx_expr}, {sy_expr})")
    elif scale_parts:
        prod = 1.0
        for v in scale_parts:
            prod *= float(v)
        if abs(prod - 1) > 1e-6:
            tf.append(f"scale({_fmt(prod)})")

    clip_any = any(is_var(v) or float(v) for v in (ct, cr, cb, cl))
    if any(is_var(v) for v in (ct, cr, cb, cl)):
        clip_expr = f"`inset(${{{ct}}}% ${{{cr}}}% ${{{cb}}}% ${{{cl}}}%)`"
    elif clip_any:
        clip_expr = f'"inset({float(ct):g}% {float(cr):g}% {float(cb):g}% {float(cl):g}%)"'
    else:
        clip_expr = "undefined"

    wrap_style = _style([
        ("position", '"absolute"'),
        ("left", '"50%"'),
        ("top", '"50%"'),
        ("opacity", o),
        ("transform", "`" + " ".join(tf) + "`"),
        ("filter", f"`blur(${{{blur}}}px)`" if is_var(blur) else (f'"blur({float(blur):g}px)"' if blur and float(blur) else "undefined")),
        ("clipPath", clip_expr),
        ("zIndex", 10 + L["track"]),
        ("mixBlendMode", json.dumps(L["blendMode"]) if L.get("blendMode") else "undefined"),
    ])

    content_jsx = ""
    if L["type"] == "text":
        words_jsx = None
        if L.get("wordTracks"):
            wl = []
            for w in L["wordTracks"]["words"]:
                if w.get("br"):
                    wl.append(f'<br key={{{w["index"]}}} />')
                    continue
                wp = f"{pid}w{w['index']}"
                wprops = {}
                for prop, keys in w["tracks"].items():
                    lines.append(f"  const {wp}_{prop} = track(t_{pid}, {_keys_ts(keys)}, "
                                 f"{_fmt(1 if prop in ('opacity', 'scale') else 0)});")
                wo = wp + "_opacity"
                wy = wp + "_y"
                ws = wp + "_scale"
                nxt = L["wordTracks"]["words"][w["index"] + 1] if w["index"] + 1 < len(L["wordTracks"]["words"]) else None
                txt = json.dumps(w["text"] + (" " if nxt and not nxt.get("br") else ""))
                wl.append(
                    f'<span key={{{w["index"]}}} style={{{{ display: "inline-block", whiteSpace: "pre", '
                    f'opacity: {wo}, transform: `translateY(${{{wy}}}px) scale(${{{ws}}})` }}}}>{{{txt}}}</span>')
            words_jsx = "\n          ".join(wl)
        content_jsx = _text_jsx(L, pid, f"t_{pid}", words_jsx)

    elif L["type"] == "shape":
        s = c
        style_items = [("width", s["w"]), ("height", s["h"])]
        if s["shape"] == "circle":
            style_items += [("borderRadius", '"50%"'),
                            ("background", json.dumps(s["fill"] if s.get("fill") != "transparent" else "transparent"))]
            if s.get("stroke"):
                style_items.append(("border", json.dumps(str(s.get("strokeWidth") or 2) + "px solid " + s["stroke"])))
        elif s["shape"] == "line":
            style_items += [("height", s.get("strokeWidth") or 4),
                            ("background", json.dumps(s.get("stroke") or s["fill"])),
                            ("borderRadius", '"99px"')]
        elif s["shape"] == "triangle":
            style_items += [("background", json.dumps(s["fill"])),
                            ("clipPath", '"polygon(50% 0, 100% 100%, 0 100%)"')]
        else:
            style_items += [("background", json.dumps(s["fill"] if s.get("fill") != "transparent" else "transparent")),
                            ("borderRadius", s.get("radius", 0))]
            if s.get("stroke"):
                style_items.append(("border", f'{json.dumps(str(s.get("strokeWidth") or 2) + "px solid " + s["stroke"])}'))
        if s.get("blur"):
            style_items.append(("filter", f'"blur({s["blur"]}px)"'))
        if s.get("shadow"):
            style_items.append(("boxShadow", json.dumps(s["shadow"])))
        content_jsx = f'<div style={_style(style_items)} />'

    elif L["type"] == "counter":
        g = c.get("grow") or {"start": 0, "dur": max(12, min(L["dur"], 36))}
        lines.append(f"  const {pid}_num = counter(t_{pid}, {g.get('start', 0)}, {g.get('dur', 24)}, "
                     f"{c['from_value']}, {c['to_value']}, 'easeOutExpo', {c.get('decimals', 0)});")
        content_jsx = ("<div style={{ fontFamily: %s, fontSize: %s, fontWeight: %s, color: %s, "
                       "fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.03em', whiteSpace: 'nowrap' }}>"
                       "{%s}{%s_num}{%s}</div>") % (
            json.dumps(c["fontFamily"]), c["fontSize"], json.dumps(str(c["fontWeight"])),
            json.dumps(c["color"]), json.dumps(c["prefix"]), pid, json.dumps(c["suffix"]))

    elif L["type"] == "chart":
        g = c.get("grow") or {"start": 4, "durationFrames": 26, "intervalFrames": 4}
        vals = c.get("values") or []
        labels = c.get("labels") or []
        maxv = max(vals + [1])
        n = max(1, len(vals))
        slot = c["w"] / n
        barw = min(slot * 0.52, 96)
        lines.append(f"  const {pid}_grow = (i: number) => grow(t_{pid}, "
                     f"{g.get('start', 0)} + i * {g.get('intervalFrames', 4)}, {g.get('durationFrames', 26)});")
        bar_jsx = []
        for i, v in enumerate(vals):
            left = slot * i + slot / 2 - barw / 2
            label = json.dumps(labels[i]) if i < len(labels) else '""'
            bar_jsx.append(
                f'<div key={{{i}}} style={{{{ position: "absolute", left: {left:.2f}, bottom: 34, '
                f'width: {barw:.2f}, height: {(v / maxv) * (c["h"] - 46):.2f}, '
                f'background: "linear-gradient(180deg, {c["color"]}, {c["color"]}88)", '
                f'borderRadius: "6px 6px 2px 2px", transformOrigin: "bottom center", '
                f'transform: `scaleY(${{{pid}_grow({i})}})` }}}}>'
                f'<div style={{{{ position: "absolute", top: "100%", left: "50%", transform: "translateX(-50%)", '
                f'marginTop: 8, fontSize: {max(22, round(c["w"] / 30))}, color: {json.dumps(c.get("labelColor", "#A1A1AA"))}, whiteSpace: "nowrap" }}}}>'
                f'{{{label}}}</div></div>')
        content_jsx = ('<div style={{ position: "relative", width: %s, height: %s }}>\n        %s\n      </div>'
                       % (c["w"], c["h"], "\n        ".join(bar_jsx)))

    elif L["type"] == "image":
        content_jsx = ('<Img src={staticFile(%s)} style={{ width: %s, height: %s, objectFit: %s }} />'
                       % (json.dumps(c["src"].replace("assets/", "")), c["w"], c["h"],
                          json.dumps(c["fit"])))

    jsx = f"""      {{vis_{pid} && (
    <div style={wrap_style}>
      {content_jsx}
    </div>
  )}}"""
    return "\n".join(lines), jsx


def build(scene, out_dir, score=100):
    comp = scene["composition"]
    theme = scene["theme"] or {}
    name = scene["meta"]["name"]
    os.makedirs(os.path.join(out_dir, "src", "scenes"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "src", "lib"), exist_ok=True)

    # ---- lib
    eases_union = "\n".join(f"  | '{e}'" for e in EASINGS)
    with open(os.path.join(out_dir, "src", "lib", "easing.ts"), "w", encoding="utf-8") as fh:
        fh.write(LIB_EASING % eases_union)
    with open(os.path.join(out_dir, "src", "lib", "motion.ts"), "w", encoding="utf-8") as fh:
        fh.write(LIB_MOTION)

    # ---- scene
    blocks, jsx_blocks, needs_img = [], [], False
    for i, L in enumerate(scene["layers"]):
        code, jsx = _layer_tsx(i, L, theme)
        blocks.append(code)
        jsx_blocks.append(jsx)
        if L["type"] == "image":
            needs_img = True

    imports = ["import React from 'react';",
               "import {AbsoluteFill, useCurrentFrame" + (", staticFile, Img" if needs_img else "") + "} from 'remotion';",
               "import {track, counter, grow} from '../lib/motion';"]

    scene_tsx = "\n".join(imports) + f"""

/**
 * {name}
 * preset: {scene['meta'].get('preset')} · {comp['width']}×{comp['height']} @ {comp['fps']}fps · {comp['durationInFrames']} frames
 * {scene['meta'].get('notes', '')}
 *
 * Digenerate oleh MOTION SKILL — credit: rajxzdev · Apache-2.0
 * Semua animasi adalah fungsi murni dari `frame` (tidak ada Math.random / wall clock).
 */
export const {name}: React.FC = () => {{
  const frame = useCurrentFrame();

{chr(10).join(blocks)}

  return (
    <AbsoluteFill style={{{{ backgroundColor: {json.dumps(comp.get('background', '#0B0B10'))}, overflow: 'hidden' }}}}>
{chr(10).join(jsx_blocks)}
    </AbsoluteFill>
  );
}};
"""
    scene_file = os.path.join(out_dir, "src", "scenes", f"{name}.tsx")
    with open(scene_file, "w", encoding="utf-8") as fh:
        fh.write(scene_tsx)

    # ---- manifest + root
    manifest_path = os.path.join(out_dir, "src", "scenes", "manifest.json")
    manifest = []
    if os.path.exists(manifest_path):
        try:
            manifest = json.load(open(manifest_path))
        except Exception:
            manifest = []
    manifest = [m for m in manifest if m["id"] != name]
    manifest.append({"id": name, "file": name, "fps": comp["fps"], "width": comp["width"],
                     "height": comp["height"], "durationInFrames": comp["durationInFrames"]})
    manifest.sort(key=lambda m: m["id"])
    json.dump(manifest, open(manifest_path, "w"), indent=2)

    root = ["import React from 'react';",
            "import {Composition} from 'remotion';"]
    for m in manifest:
        root.append(f"import {{{m['id']}}} from './scenes/{m['file']}';")
    root.append("")
    root.append("export const RemotionRoot: React.FC = () => {")
    root.append("  return (")
    root.append("    <>")
    for m in manifest:
        root.append(f'      <Composition id="{m["id"]}" component={{{m["id"]}}} '
                    f'durationInFrames={{{m["durationInFrames"]}}} fps={{{m["fps"]}}} '
                    f'width={{{m["width"]}}} height={{{m["height"]}}} />')
    root.append("    </>")
    root.append("  );")
    root.append("};")
    root.append("")
    with open(os.path.join(out_dir, "src", "Root.tsx"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(root))

    with open(os.path.join(out_dir, "src", "index.ts"), "w", encoding="utf-8") as fh:
        fh.write("import {registerRoot} from 'remotion';\n"
                 "import {RemotionRoot} from './Root';\n\n"
                 "registerRoot(RemotionRoot);\n")

    # ---- project files (tidak menimpa kalau sudah ada)
    pkg = {
        "name": "motion-skill-remotion",
        "version": "1.0.0",
        "private": True,
        "description": "Scene Remotion hasil MOTION SKILL (credit: rajxzdev)",
        "license": "Apache-2.0",
        "scripts": {
            "dev": "remotion studio",
            "studio": "remotion studio",
            "render": "remotion render src/index.ts " + name + " out/" + name + ".mp4",
            "render:gif": "remotion render src/index.ts " + name + " out/" + name + ".gif --codec=gif",
            "still": "remotion still src/index.ts " + name + " out/still.png --frame=30",
            "typecheck": "tsc --noEmit",
        },
        "dependencies": {
            "@remotion/cli": "4.0.200",
            "react": "18.3.1",
            "react-dom": "18.3.1",
            "remotion": "4.0.200",
        },
        "devDependencies": {
            "@types/react": "18.3.12",
            "@types/react-dom": "18.3.1",
            "typescript": "5.6.3",
        },
    }
    pkg_path = os.path.join(out_dir, "package.json")
    if not os.path.exists(pkg_path):
        json.dump(pkg, open(pkg_path, "w"), indent=2)

    tsconfig = {
        "compilerOptions": {
            "target": "ES2020", "module": "ESNext", "moduleResolution": "Bundler",
            "jsx": "react-jsx", "strict": True, "noEmit": True, "esModuleInterop": True,
            "skipLibCheck": True, "forceConsistentCasingInFileNames": True,
            "lib": ["DOM", "ES2020"],
        },
        "include": ["src"],
    }
    tsc_path = os.path.join(out_dir, "tsconfig.json")
    if not os.path.exists(tsc_path):
        json.dump(tsconfig, open(tsc_path, "w"), indent=2)

    cfg_path = os.path.join(out_dir, "remotion.config.ts")
    if not os.path.exists(cfg_path):
        open(cfg_path, "w").write(
            "import {Config} from '@remotion/cli/config';\n\n"
            "Config.setVideoImageFormat('jpeg');\n"
            "Config.setOverwriteOutput(true);\n"
            "// Render paralel; turunkan kalau RAM lokal terbatas.\n"
            "Config.setConcurrency(4);\n")

    readme = f"""# {name} — Remotion project

Digenerate **MOTION SKILL** (credit: rajxzdev · Apache-2.0) · smoothness **{score}/100**

```bash
npm install
npm run dev        # Remotion Studio (scrub timeline)
npm run render     # → out/{name}.mp4
npm run typecheck
```

## Struktur

```
src/
├── index.ts        # registerRoot
├── Root.tsx        # <Composition id="{name}" .../>
├── scenes/{name}.tsx
└── lib/
    ├── easing.ts   # 21 easing, identik dengan validator Python
    └── motion.ts   # track(), counter(), grow(), inset()
```

## Aturan yang sudah dipatuhi

- `useCurrentFrame()` murni — tidak ada `Date.now()`, `Math.random()`, atau animasi CSS berbasis wall-clock.
- Semua transform dihitung dari satu `track()` sehingga mudah diaudit.
- `durationInFrames` = {comp['durationInFrames']} @ {comp['fps']}fps = {comp['durationInFrames'] / comp['fps']:.2f}s.

> Catatan lisensi: Remotion punya lisensi komersial sendiri untuk perusahaan > 3 orang.
> Skill ini Apache-2.0, tapi **runtime Remotion** tetap tunduk pada lisensi Remotion.
"""
    with open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(readme)
    return scene_file
