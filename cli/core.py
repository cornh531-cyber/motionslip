"""
MOTION SKILL — core
===================
Loader, preset expander, validator, dan smoothness linter untuk file *.scene.json.

Credit: rajxzdev — Apache-2.0
Hanya memakai standard library Python 3.9+.
"""
from __future__ import annotations

import json
import math
import os
import re

SCHEMA_VERSION = "1.0.0"
SUPPORTED_FPS = (24, 25, 30, 50, 60)
RENDERERS = ("preview", "hyperframes", "remotion", "motion-canvas")

# --------------------------------------------------------------------------------------
# Easing — implementasi referensi. Versi TS/JS di renderers/remotion/src/lib/easing.ts
# harus identik supaya preview & hasil render tidak berbeda.
# --------------------------------------------------------------------------------------

def _clamp01(t):
    return 0.0 if t < 0 else 1.0 if t > 1 else t


def linear(t):
    return t


def easeInQuad(t):
    return t * t


def easeOutQuad(t):
    return 1 - (1 - t) ** 2


def easeInOutQuad(t):
    return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2


def easeInCubic(t):
    return t ** 3


def easeOutCubic(t):
    return 1 - (1 - t) ** 3


def easeInOutCubic(t):
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def easeInQuart(t):
    return t ** 4


def easeOutQuart(t):
    return 1 - (1 - t) ** 4


def easeInOutQuart(t):
    return 8 * t ** 4 if t < 0.5 else 1 - (-2 * t + 2) ** 4 / 2


def easeOutQuint(t):
    return 1 - (1 - t) ** 5


def easeInOutQuint(t):
    return 16 * t ** 5 if t < 0.5 else 1 - (-2 * t + 2) ** 5 / 2


def easeOutExpo(t):
    return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)


def easeInOutExpo(t):
    if t == 0 or t == 1:
        return t
    return 2 ** (20 * t - 10) / 2 if t < 0.5 else (2 - 2 ** (-20 * t + 10)) / 2


def easeOutCirc(t):
    return math.sqrt(1 - (t - 1) ** 2) if t < 1 else 1.0


def easeOutBack(t, s=1.70158):
    c3 = s + 1
    return 1 + c3 * (t - 1) ** 3 + s * (t - 1) ** 2


def easeInOutBack(t, s=1.70158):
    c2 = s * 1.525
    if t < 0.5:
        return ((2 * t) ** 2 * ((c2 + 1) * 2 * t - c2)) / 2
    return ((2 * t - 2) ** 2 * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2


def easeOutElastic(t):
    if t in (0, 1):
        return t
    c4 = (2 * math.pi) / 3
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def easeOutBounce(t):
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1:
        return n1 * t * t
    if t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    if t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    t -= 2.625 / d1
    return n1 * t * t + 0.984375


def springSoft(t):
    # kritikal-damped mendekati overshoot kecil (zeta ≈ 0.85)
    if t >= 1:
        return 1.0
    w = 12.0
    return 1 - math.exp(-0.85 * w * t) * (1 + 0.85 * w * t * (1 - t) * 0.35)


def springSnappy(t):
    if t >= 1:
        return 1.0
    w = 18.0
    return 1 - math.exp(-0.62 * w * t) * math.cos(1.35 * w * t * 0.35)


EASINGS = {
    "linear": linear,
    "easeInQuad": easeInQuad, "easeOutQuad": easeOutQuad, "easeInOutQuad": easeInOutQuad,
    "easeInCubic": easeInCubic, "easeOutCubic": easeOutCubic, "easeInOutCubic": easeInOutCubic,
    "easeInQuart": easeInQuart, "easeOutQuart": easeOutQuart, "easeInOutQuart": easeInOutQuart,
    "easeOutQuint": easeOutQuint, "easeInOutQuint": easeInOutQuint,
    "easeOutExpo": easeOutExpo, "easeInOutExpo": easeInOutExpo,
    "easeOutCirc": easeOutCirc,
    "easeOutBack": easeOutBack, "easeInOutBack": easeInOutBack,
    "easeOutElastic": easeOutElastic, "easeOutBounce": easeOutBounce,
    "springSoft": springSoft, "springSnappy": springSnappy,
}

# Property yang boleh dianimasikan
PROPS = (
    "opacity", "x", "y", "scale", "scaleX", "scaleY", "rotate", "blur",
    "letterSpacing", "clipTop", "clipRight", "clipBottom", "clipLeft",
)

BASE_VALUE = {
    "opacity": 1.0, "x": 0.0, "y": 0.0, "scale": 1.0, "scaleX": 1.0, "scaleY": 1.0,
    "rotate": 0.0, "blur": 0.0, "letterSpacing": 0.0,
    "clipTop": 0.0, "clipRight": 0.0, "clipBottom": 0.0, "clipLeft": 0.0,
}

MIN_ANIM_FRAMES = 4          # di bawah ini = patah
GOOD_ANIM_FRAMES = 6         # rekomendasi minimum @30fps


# --------------------------------------------------------------------------------------
# Preset
# --------------------------------------------------------------------------------------

def _kf(prop, frm, to, start, dur, ease):
    return {"property": prop, "from": float(frm), "to": float(to),
            "start": int(start), "dur": max(1, int(dur)), "ease": ease}


def expand_in(preset, dur, delay, distance, ease):
    """Preset masuk -> daftar keyframe (start relatif ke layer)."""
    dur = max(2, int(dur))
    d = distance if distance is not None else 48
    out = []
    if preset == "fade":
        out.append(_kf("opacity", 0, 1, delay, dur, "easeOutCubic"))
    elif preset == "slideUp":
        out.append(_kf("opacity", 0, 1, delay, max(4, int(dur * 0.7)), "easeOutCubic"))
        out.append(_kf("y", d, 0, delay, dur, ease or "easeOutQuint"))
    elif preset == "slideDown":
        out.append(_kf("opacity", 0, 1, delay, max(4, int(dur * 0.7)), "easeOutCubic"))
        out.append(_kf("y", -d, 0, delay, dur, ease or "easeOutQuint"))
    elif preset == "slideLeft":
        out.append(_kf("opacity", 0, 1, delay, max(4, int(dur * 0.7)), "easeOutCubic"))
        out.append(_kf("x", d, 0, delay, dur, ease or "easeOutQuint"))
    elif preset == "slideRight":
        out.append(_kf("opacity", 0, 1, delay, max(4, int(dur * 0.7)), "easeOutCubic"))
        out.append(_kf("x", -d, 0, delay, dur, ease or "easeOutQuint"))
    elif preset == "scaleIn":
        out.append(_kf("opacity", 0, 1, delay, dur, "easeOutCubic"))
        out.append(_kf("scale", 0.88, 1, delay, dur, ease or "easeOutQuint"))
    elif preset == "popIn":
        out.append(_kf("opacity", 0, 1, delay, max(4, int(dur * 0.55)), "easeOutCubic"))
        out.append(_kf("scale", 0.62, 1, delay, dur, ease or "easeOutBack"))
    elif preset == "blurIn":
        out.append(_kf("opacity", 0, 1, delay, dur, "easeOutCubic"))
        out.append(_kf("blur", 18, 0, delay, dur, ease or "easeOutQuint"))
    elif preset == "maskUp":
        out.append(_kf("clipTop", 100, 0, delay, dur, ease or "easeOutQuint"))
    elif preset == "wipeRight":
        out.append(_kf("clipLeft", 100, 0, delay, dur, ease or "easeOutQuint"))
    elif preset == "typeOn":
        out.append(_kf("clipRight", 100, 0, delay, dur, "linear"))
    elif preset == "popStagger":
        out.append(_kf("opacity", 0, 1, delay, max(4, int(dur * 0.6)), "easeOutCubic"))
        out.append(_kf("scale", 0.7, 1, delay, dur, ease or "easeOutBack"))
    else:
        raise ValueError(f"preset masuk tidak dikenal: {preset}")
    return out


def expand_out(preset, dur, delay, distance, ease, layer_dur):
    """Preset keluar -> keyframe, di-anchor dari ujung layer."""
    dur = max(2, int(dur))
    d = distance if distance is not None else 40
    start = max(0, layer_dur - dur - delay)
    out = []
    if preset == "fade":
        out.append(_kf("opacity", 1, 0, start, dur, "easeInCubic"))
    elif preset == "slideDown":
        out.append(_kf("opacity", 1, 0, start, dur, "easeInCubic"))
        out.append(_kf("y", 0, d, start, dur, ease or "easeInCubic"))
    elif preset == "slideUpOut":
        out.append(_kf("opacity", 1, 0, start, dur, "easeInCubic"))
        out.append(_kf("y", 0, -d, start, dur, ease or "easeInCubic"))
    elif preset == "scaleOut":
        out.append(_kf("opacity", 1, 0, start, dur, "easeInCubic"))
        out.append(_kf("scale", 1, 0.9, start, dur, ease or "easeInOutCubic"))
    elif preset == "blurOut":
        out.append(_kf("opacity", 1, 0, start, dur, "easeInCubic"))
        out.append(_kf("blur", 0, 16, start, dur, ease or "easeInOutCubic"))
    elif preset == "maskDown":
        out.append(_kf("clipTop", 0, 100, start, dur, ease or "easeInCubic"))
    else:
        raise ValueError(f"preset keluar tidak dikenal: {preset}")
    return out


# --------------------------------------------------------------------------------------
# Load + compile
# --------------------------------------------------------------------------------------

class SceneError(Exception):
    pass


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError as exc:
            raise SceneError(f"JSON tidak valid di {path}: {exc}") from exc


def compile_scene(scene):
    """Normalisasi scene -> struktur siap-render. Tidak melakukan validasi berat."""
    comp = dict(scene.get("composition") or {})
    comp.setdefault("fps", 30)
    comp.setdefault("background", "#0B0B10")
    theme = scene.get("theme") or {}
    meta = scene.get("meta") or {}

    layers_out = []
    for src in scene.get("layers", []):
        layer = {
            "id": src["id"],
            "type": src["type"],
            "from": int(src.get("from", 0)),
            "dur": int(src.get("durationInFrames", 1)),
            "track": int(src.get("track", 0)),
            "x": float(src.get("x", 0)),
            "y": float(src.get("y", 0)),
            "w": src.get("w"),
            "h": src.get("h"),
            "rotate": float(src.get("rotate", 0)),
            "opacity": float(src.get("opacity", 1)),
            "blendMode": src.get("blendMode"),
            "content": {},
            "tracks": {},
            "wordTracks": None,
        }
        # ---- konten per tipe
        t = src["type"]
        if t == "text":
            layer["content"] = {
                "text": src.get("text", ""),
                "fontSize": src.get("fontSize", 72),
                "fontWeight": src.get("fontWeight", 700),
                "fontFamily": src.get("fontFamily", theme.get("font", "Inter, system-ui, sans-serif")),
                "color": src.get("color", theme.get("text", "#FFFFFF")),
                "lineHeight": src.get("lineHeight", 1.1),
                "letterSpacing": src.get("letterSpacing", 0),
                "align": src.get("align", "center"),
                "maxWidth": src.get("maxWidth", comp.get("width", 1080) * 0.86),
                "uppercase": bool(src.get("uppercase", False)),
                "italic": bool(src.get("italic", False)),
                "highlight": src.get("highlight"),
            }
        elif t == "shape":
            layer["content"] = {
                "shape": src.get("shape", "rect"),
                "fill": src.get("fill", theme.get("accent", "#7C5CFF")),
                "stroke": src.get("stroke"),
                "strokeWidth": src.get("strokeWidth", 0),
                "radius": src.get("radius", 0),
                "w": src.get("w", 200),
                "h": src.get("h", 200),
                "blur": src.get("blur", 0),
                "shadow": src.get("shadow"),
            }
            layer["w"] = layer["w"] if layer["w"] is not None else layer["content"]["w"]
            layer["h"] = layer["h"] if layer["h"] is not None else layer["content"]["h"]
        elif t == "counter":
            layer["content"] = {
                "from_value": src.get("from_value", 0),
                "to_value": src.get("to_value", 100),
                "prefix": src.get("prefix", ""),
                "suffix": src.get("suffix", ""),
                "decimals": int(src.get("decimals", 0)),
                "fontSize": src.get("fontSize", 200),
                "fontWeight": src.get("fontWeight", 900),
                "fontFamily": src.get("fontFamily", theme.get("font", "Inter, system-ui, sans-serif")),
                "color": src.get("color", theme.get("text", "#FFFFFF")),
                "grow": src.get("grow") or {"start": 0, "dur": max(12, min(int(src.get("durationInFrames", 30)), 36))},
            }
        elif t == "chart":
            layer["content"] = {
                "values": src.get("values", []),
                "labels": src.get("labels", []),
                "color": src.get("color", theme.get("accent", "#7C5CFF")),
                "w": src.get("w", 820),
                "h": src.get("h", 460),
                "grow": src.get("grow") or {"start": 4, "durationFrames": 26, "intervalFrames": 4},
                "labelColor": src.get("labelColor", theme.get("muted", "#A1A1AA")),
            }
            layer["w"] = layer["w"] if layer["w"] is not None else layer["content"]["w"]
            layer["h"] = layer["h"] if layer["h"] is not None else layer["content"]["h"]
        elif t == "image":
            layer["content"] = {
                "src": src.get("src", ""),
                "fit": src.get("fit", "contain"),
                "w": src.get("w", 400),
                "h": src.get("h", 400),
            }
            layer["w"] = layer["w"] if layer["w"] is not None else layer["content"]["w"]
            layer["h"] = layer["h"] if layer["h"] is not None else layer["content"]["h"]

        # ---- keyframe eksplisit
        tracks = {}
        for kf in src.get("animate", []) or []:
            prop = kf["property"]
            tracks.setdefault(prop, []).append({
                "property": prop,
                "from": float(kf["from"]),
                "to": float(kf["to"]),
                "start": int(kf.get("start", 0)),
                "dur": max(1, int(kf["duration"])),
                "ease": kf.get("easing", "easeOutCubic"),
            })

        # ---- preset masuk/keluar
        # CATATAN SEMANTIK: keyframe preset untuk x/y/rotate adalah OFFSET dari posisi
        # dasar layer (layer.x / layer.y / layer.rotate). Kita lipat (fold) base ke dalam
        # nilai keyframe di sini, supaya semua renderer cukup menggambar track apa adanya.
        base_fold = {"x": layer["x"], "y": layer["y"], "rotate": layer["rotate"]}

        def _fold(kf):
            base = base_fold.get(kf["property"], 0.0)
            if base:
                kf = dict(kf)
                kf["from"] += base
                kf["to"] += base
            kf["preset"] = True
            return kf

        if src.get("in"):
            p = src["in"]
            for kf in expand_in(p["preset"], p.get("duration", 14), p.get("delay", 0),
                                p.get("distance", 48), p.get("easing")):
                tracks.setdefault(kf["property"], []).append(_fold(kf))
        if src.get("out"):
            p = src["out"]
            for kf in expand_out(p["preset"], p.get("duration", 10), p.get("delay", 0),
                                 p.get("distance", 40), p.get("easing"), layer["dur"]):
                tracks.setdefault(kf["property"], []).append(_fold(kf))

        for prop in tracks:
            tracks[prop].sort(key=lambda k: k["start"])
        layer["tracks"] = tracks

        # ---- stagger per kata
        st = src.get("stagger")
        if st and t == "text":
            mode = st.get("mode", "word")
            interval = int(st.get("intervalFrames", 3))
            ip = st.get("preset") or {"preset": "slideUp", "duration": 14}
            ip = dict(ip) if isinstance(ip, dict) else {"preset": str(ip), "duration": 14}
            base_tracks = expand_in(ip.get("preset", "slideUp"), ip.get("duration", 14),
                                    ip.get("delay", 0), ip.get("distance", 34), ip.get("easing"))
            text = layer["content"]["text"]
            words = []
            if mode == "char":
                units = [{"text": ch} for ch in text if ch != "\n"]
            else:
                units = []
                for li, line in enumerate(text.split("\n")):
                    if li:
                        units.append({"text": "", "br": True})
                    for w in line.split(" "):
                        if w:
                            units.append({"text": w})
            for i, unit in enumerate(units):
                wt = {}
                if not unit.get("br"):
                    for kf in base_tracks:
                        k = dict(kf)
                        k["start"] = kf["start"] + i * interval
                        wt.setdefault(k["property"], []).append(k)
                words.append({**unit, "index": i, "tracks": wt})
            layer["wordTracks"] = {"mode": mode, "interval": interval,
                                   "words": words}

        layers_out.append(layer)

    layers_out.sort(key=lambda l: (l["track"], l["from"]))
    return {
        "meta": {"name": meta.get("name", "Untitled"), "preset": meta.get("preset", "ads"),
                 "credit": meta.get("credit", "rajxzdev"), "license": meta.get("license", "Apache-2.0"),
                 "notes": meta.get("notes", "")},
        "composition": comp,
        "theme": theme,
        "layers": layers_out,
        "raw": scene,
    }


# --------------------------------------------------------------------------------------
# Sampling helpers (dipakai validator + report)
# --------------------------------------------------------------------------------------

def track_value(tracks, prop, local_frame):
    """Nilai properti pada frame lokal layer. Keyframe belakangan menang."""
    keys = tracks.get(prop)
    base = BASE_VALUE.get(prop, 0.0)
    if not keys:
        return base
    value = base
    applied = False
    for k in keys:
        t = (local_frame - k["start"]) / k["dur"]
        if t < 0:
            continue
        applied = True
        value = k["from"] + (k["to"] - k["from"]) * EASINGS[k["ease"]](_clamp01(t))
    if not applied:
        return keys[0]["from"]
    return value


# --------------------------------------------------------------------------------------
# Validator + smoothness lint
# --------------------------------------------------------------------------------------

def _is_background(layer, cw, ch):
    """Shape polos yang menutupi seluruh canvas dianggap background (boleh jadi dead-air penutup)."""
    if layer.get("type") != "shape":
        return False
    w = layer.get("w") or (layer.get("content") or {}).get("w") or 0
    h = layer.get("h") or (layer.get("content") or {}).get("h") or 0
    return w >= cw * 0.98 and h >= ch * 0.98 and not layer.get("stroke")


def _count_animations(layer):
    """Jumlah animasi sebenarnya (keyframe eksplisit + preset yang di-expand)."""
    n = len(layer.get("animate") or [])
    d = int(layer.get("durationInFrames", 1))
    if layer.get("in"):
        p = layer["in"]
        n += len(expand_in(p["preset"], p.get("duration", 14), p.get("delay", 0),
                           p.get("distance", 48), p.get("easing")))
    if layer.get("out"):
        p = layer["out"]
        n += len(expand_out(p["preset"], p.get("duration", 10), p.get("delay", 0),
                            p.get("distance", 40), p.get("easing"), d))
    st = layer.get("stagger")
    if st and layer.get("type") == "text":
        txt = layer.get("text", "")
        units = (len([w for w in txt.replace("\n", " ").split(" ") if w])
                 if st.get("mode", "word") == "word" else len(txt.replace("\n", "")))
        ip = st.get("preset") or {}
        if isinstance(ip, dict):
            n += units * len(expand_in(ip.get("preset", "slideUp"), ip.get("duration", 14),
                                       0, ip.get("distance", 34), ip.get("easing")))
    return n


def validate(scene, strict=False):
    """Kembalikan dict: errors, warnings, score, stats."""
    errors, warnings, notes = [], [], []
    fps = int((scene.get("composition") or {}).get("fps", 30))
    dur = int((scene.get("composition") or {}).get("durationInFrames", 0))
    comp = scene.get("composition") or {}
    meta = scene.get("meta") or {}

    # ---------- struktural
    if not meta.get("name"):
        errors.append("meta.name wajib ada")
    elif not re.match(r"^[A-Za-z][A-Za-z0-9_]*$", meta["name"]):
        errors.append("meta.name harus PascalCase/identifier (tanpa spasi/strip)")
    if fps not in SUPPORTED_FPS:
        errors.append(f"composition.fps={fps} tidak didukung (pakai {SUPPORTED_FPS})")
    if dur <= 0:
        errors.append("composition.durationInFrames harus > 0")
    if not scene.get("layers"):
        errors.append("layers kosong")
    if meta.get("license") and meta["license"] != "Apache-2.0":
        warnings.append("lisensi proyek disarankan Apache-2.0 (default skill ini)")
    if meta.get("credit") and meta["credit"] != "rajxzdev":
        notes.append(f"credit: {meta['credit']} (default skill: rajxzdev)")

    ids = set()
    frame_min = 6 if fps <= 30 else 8
    warn_short = round(GOOD_ANIM_FRAMES * 30 / fps)

    for i, layer in enumerate(scene.get("layers", [])):
        lid = layer.get("id", f"layer[{i}]")
        if lid in ids:
            errors.append(f"[{lid}] id duplikat")
        ids.add(lid)
        if layer.get("type") not in ("text", "shape", "counter", "image", "chart"):
            errors.append(f"[{lid}] type tidak dikenal: {layer.get('type')}")
        frm = int(layer.get("from", 0))
        ln = int(layer.get("durationInFrames", 0))
        if ln <= 0:
            errors.append(f"[{lid}] durationInFrames harus > 0")
        if frm + ln > dur:
            errors.append(f"[{lid}] keluar canvas: {frm}+{ln} > {dur} frame. "
                          f"Perpanjang composition.durationInFrames atau pendekkan layer.")
        if frm + ln <= 0:
            warnings.append(f"[{lid}] tidak pernah tampil")

        if layer.get("type") == "text":
            txt = layer.get("text", "")
            if not txt.strip():
                errors.append(f"[{lid}] text kosong")
            fs = layer.get("fontSize", 72)
            maxw = layer.get("maxWidth", comp.get("width", 1080) * 0.86)
            widest = max([len(w) for w in txt.split("\n")] + [0])
            est = widest * fs * 0.55
            if est > maxw * 1.02:
                warnings.append(
                    f"[{lid}] teks kemungkinan overflow ({int(est)}px > maxWidth {int(maxw)}px). "
                    f"Turunkan fontSize ke ~{int(fs * maxw / est)} atau pecah baris.")
            if len(txt) > 90:
                warnings.append(f"[{lid}] teks panjang ({len(txt)} char) — pertimbangkan 2 layer/animasi bertahap")

        # ---------- animasi
        props_seen = {}
        for prop, keys in (layer.get("tracks") or {}).items():
            if prop not in PROPS:
                errors.append(f"[{lid}] properti animasi tidak dikenal: {prop}")
                continue
            props_seen.setdefault(prop, 0)
            props_seen[prop] += len(keys)
            for k in keys:
                props_seen["_dur_min"] = min(props_seen.get("_dur_min", 10 ** 6), k["dur"])
                if k["ease"] not in EASINGS:
                    errors.append(f"[{lid}.{prop}] easing tidak dikenal: {k['ease']}")
                if k["dur"] < MIN_ANIM_FRAMES:
                    warnings.append(
                        f"[{lid}.{prop}] durasi {k['dur']}f terlalu pendek (< {MIN_ANIM_FRAMES}f) — "
                        f"animasi akan terasa patah")
                if k["dur"] < warn_short and k["dur"] >= MIN_ANIM_FRAMES:
                    notes.append(f"[{lid}.{prop}] {k['dur']}f < rekomendasi {warn_short}f @{fps}fps")
                if k["start"] + k["dur"] > ln:
                    warnings.append(f"[{lid}.{prop}] animasi melewati akhir layer "
                                    f"({k['start'] + k['dur']}f > {ln}f) dan akan terpotong")
                # linear hanya untuk gerak kontinu
                if k["ease"] == "linear" and prop in ("y", "x", "scale", "opacity"):
                    warnings.append(f"[{lid}.{prop}] easing 'linear' bikin gerak terasa mekanis; "
                                    f"pakai easeOut* / spring")
                if prop == "blur" and max(k["from"], k["to"]) > 32:
                    warnings.append(f"[{lid}.{prop}] blur > 32px mahal & cenderung 'smear'")
                if prop == "clipTop" and k["from"] < k["to"] and k["start"] == 0 and ln < 8:
                    notes.append(f"[{lid}] layer pendek untuk animasi mask")

        # keyframe tumpang tindih pada properti yang sama
        for prop, keys in (layer.get("tracks") or {}).items():
            for a, b in zip(keys, keys[1:]):
                if b["start"] < a["start"] + a["dur"]:
                    warnings.append(
                        f"[{lid}.{prop}] keyframe tumpang tindih di frame {b['start']} — "
                        f"nilai keyframe terakhir menang (bisa menyebabkan 'pop')")

        # in/out overlap
        if layer.get("in") and layer.get("out"):
            in_end = layer["in"].get("delay", 0) + layer["in"].get("duration", 14)
            out_start = ln - layer["out"].get("duration", 10) - layer["out"].get("delay", 0)
            if out_start < in_end:
                warnings.append(f"[{lid}] animasi masuk & keluar tumpang tindih "
                                f"(in selesai {in_end}f, out mulai {out_start}f)")
        if ln < 10 and (layer.get("in") or layer.get("out")):
            warnings.append(f"[{lid}] layer hanya {ln}f tapi punya animasi masuk/keluar — "
                            f"penonton tidak sempat membaca")

        # konflik nyata: keyframe eksplisit menabrak rentang preset 'in'
        if layer.get("in"):
            p_in = layer["in"]
            in_end = p_in.get("delay", 0) + p_in.get("duration", 14)
            in_props = {k["property"] for k in expand_in(
                p_in["preset"], p_in.get("duration", 14), p_in.get("delay", 0),
                p_in.get("distance", 48), p_in.get("easing"))}
            for kf in (layer.get("animate") or []):
                if kf.get("start", 0) < in_end and kf["property"] in in_props:
                    warnings.append(
                        f"[{lid}.{kf['property']}] keyframe eksplisit mulai di frame "
                        f"{kf.get('start', 0)} menabrak preset 'in' (0–{in_end}f) — "
                        f"nilai keyframe terakhir menang, hasil bisa 'pop'")

    # ---------- pacing keseluruhan
    if dur:
        seconds = dur / fps
        if seconds < 2:
            warnings.append(f"durasi total {seconds:.1f}s sangat pendek untuk sebuah scene")
        if seconds > 60:
            warnings.append(f"durasi total {seconds:.0f}s — pertimbangkan dipecah jadi beberapa scene")

    # dead air: abaikan layer background full-bleed, pakai running-max
    cw = comp.get("width", 1080)
    ch = comp.get("height", 1080)
    foreground = [l for l in scene.get("layers", []) if not _is_background(l, cw, ch)]
    spans = sorted([(l.get("from", 0), l.get("from", 0) + l.get("durationInFrames", 0))
                    for l in foreground])
    gap = 0
    reach = 0
    for start, end in spans:
        if start > reach:
            gap = max(gap, start - reach)
        reach = max(reach, end)
    if gap >= fps:
        warnings.append(f"ada {gap}f ({gap / fps:.2f}s) tanpa layer apa pun — layar kosong. "
                        f"Disengaja atau lupa?")

    # ---------- smoothness score
    score = 100
    score -= 12 * len([e for e in errors])
    score -= 4 * len(warnings)
    if gap >= fps:
        score -= 6
    score = max(0, min(100, score))

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "notes": notes,
        "score": score,
        "stats": {
            "fps": fps,
            "durationInFrames": dur,
            "durationSeconds": round(dur / fps, 2),
            "layers": len(scene.get("layers", [])),
            "animations": sum(_count_animations(l) for l in scene.get("layers", [])),
        },
    }
