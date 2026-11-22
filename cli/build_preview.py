"""Target: preview.html — runtime dependency-free (tanpa CDN, tanpa npm).

Bisa dibuka langsung di browser / iframe sandbox, dan dipakai untuk frame review.
"""
from __future__ import annotations

import html
import json
import os

from jsassets import EASING_JS


def _payload(scene):
    """Ambil hanya field yang dibutuhkan runtime."""
    layers = []
    for l in scene["layers"]:
        item = {
            "id": l["id"], "type": l["type"], "from": l["from"], "dur": l["dur"],
            "track": l["track"], "x": l["x"], "y": l["y"], "rotate": l["rotate"],
            "opacity": l["opacity"], "blendMode": l["blendMode"],
            "w": l["w"], "h": l["h"], "tracks": l["tracks"], "content": l["content"],
        }
        if l.get("wordTracks"):
            item["wordTracks"] = l["wordTracks"]
        layers.append(item)
    return {
        "meta": scene["meta"],
        "composition": scene["composition"],
        "theme": scene["theme"],
        "layers": layers,
    }


TEMPLATE = r"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__NAME__ — MOTION SKILL preview</title>
<style>
  :root{
    --accent:__ACCENT__;
    --bg:#07070B;
    --panel:#0E0E15;
    --line:#1E1E2A;
    --text:#EDEDF2;
    --muted:#8A8A9A;
    --font:__FONT__;
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden}
  body{
    background:
      radial-gradient(900px 600px at 15% -10%, color-mix(in srgb, var(--accent) 22%, transparent), transparent 60%),
      radial-gradient(700px 500px at 100% 110%, #1b1140 0%, transparent 60%),
      var(--bg);
    color:var(--text); font-family:var(--font); display:flex; flex-direction:column;
    align-items:center; justify-content:center; gap:14px; padding:18px; min-height:100%;
  }
  header{display:flex;align-items:center;gap:10px;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
  header b{color:var(--text);letter-spacing:.18em}
  .dot{width:6px;height:6px;border-radius:50%;background:var(--accent);box-shadow:0 0 12px var(--accent)}
  .wrap{position:relative;flex:1;width:100%;min-height:0;overflow:hidden}
  .stage{
    position:absolute; left:50%; top:50%; overflow:hidden; background:__BG__;
    box-shadow:0 40px 90px rgba(0,0,0,.6), 0 0 0 1px rgba(255,255,255,.06);
    transform-origin:center center; border-radius:6px;
  }
  .layer{position:absolute;left:50%;top:50%;will-change:transform,opacity,filter}
  .layer .txt{white-space:pre-wrap}
  .word{display:inline-block;white-space:pre}
  .bar{position:absolute;bottom:34px;border-radius:6px 6px 2px 2px;transform-origin:bottom center}
  .barlabel{position:absolute;bottom:6px;font-size:13px;letter-spacing:.06em;text-align:center;color:var(--muted);transform:translateX(-50%)}
  .hud{
    width:min(720px,100%);background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.01));
    border:1px solid var(--line);border-radius:14px;padding:10px 12px;display:flex;flex-direction:column;gap:9px;
    backdrop-filter:blur(8px);
  }
  .row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
  button{
    background:#15151F;color:var(--text);border:1px solid var(--line);border-radius:9px;
    padding:7px 11px;font:inherit;font-size:12px;cursor:pointer;transition:.16s;
  }
  button:hover{border-color:var(--accent);color:#fff}
  button.primary{background:var(--accent);border-color:transparent;color:#0B0714;font-weight:700}
  .mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px;color:var(--muted)}
  input[type=range]{-webkit-appearance:none;appearance:none;height:4px;border-radius:99px;background:#22222F;flex:1;outline:none}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:13px;height:13px;border-radius:50%;background:var(--accent);cursor:pointer;box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 20%,transparent)}
  input[type=range]::-moz-range-thumb{width:13px;height:13px;border:0;border-radius:50%;background:var(--accent);cursor:pointer}
  .ruler{position:relative;height:26px;border-radius:8px;background:#101018;border:1px solid var(--line);overflow:hidden;cursor:pointer}
  .clip{position:absolute;top:4px;height:5px;border-radius:99px;background:var(--accent);opacity:.55}
  .clip:hover{opacity:1}
  .playhead{position:absolute;top:0;bottom:0;width:1px;background:#fff;opacity:.85}
  .meta{display:flex;gap:14px;flex-wrap:wrap;font-size:11px;color:var(--muted)}
  .meta span b{color:var(--text);font-weight:600}
  .badge{border:1px solid var(--line);border-radius:99px;padding:2px 8px;font-size:10px;letter-spacing:.1em;text-transform:uppercase}
  footer{font-size:10.5px;color:#5A5A6C;letter-spacing:.08em}
  footer a{color:#7E7E92}
</style>
</head>
<body>
  <header><span class="dot"></span><b>MOTION SKILL</b><span>/ preview</span><span class="badge" id="preset">__PRESET__</span></header>

  <div class="wrap"><div class="stage" id="stage"></div></div>

  <div class="hud">
    <div class="row">
      <button class="primary" id="play">▶ Play</button>
      <button id="restart">↺</button>
      <button id="loop" aria-pressed="true">Loop: on</button>
      <span class="mono" id="tc">00:00.00 / 00:00.00 · f 0/0</span>
    </div>
    <div class="row">
      <input type="range" id="scrub" min="0" max="1" value="0" step="1">
    </div>
    <div class="ruler" id="ruler"><div class="playhead" id="ph"></div></div>
    <div class="meta">
      <span><b id="m-name">—</b></span>
      <span id="m-size">—</span>
      <span id="m-fps">—</span>
      <span id="m-layers">—</span>
      <span>Smoothness <b id="m-score">—</b>/100</span>
    </div>
  </div>
  <footer>generated by MOTION SKILL · credit <a href="https://github.com/rajxzdev" target="_blank" rel="noopener">rajxzdev</a> · Apache-2.0</footer>

<script>
const SCENE = __SCENE__;
const SCORE = __SCORE__;
__EASINGS__

const comp = SCENE.composition;
const W = comp.width, H = comp.height, FPS = comp.fps, TOTAL = comp.durationInFrames;
const stage = document.getElementById('stage');
stage.style.width = W + 'px';
stage.style.height = H + 'px';

/* ---------- util ---------- */
const el = (tag, cls, css) => { const n = document.createElement(tag); if (cls) n.className = cls; if (css) Object.assign(n.style, css); return n; };
const clamp01 = v => v < 0 ? 0 : v > 1 ? 1 : v;
function fmt(n){ return Number(n).toFixed(2).replace('.', ':'); }
function tc(f){ const s = f / FPS; const m = Math.floor(s / 60); const r = (s % 60).toFixed(2).padStart(5, '0'); return `${String(m).padStart(2,'0')}:${r}`; }

/* ---------- easing & track ---------- */
__TRACK__

/* ---------- build DOM ---------- */
const nodes = {};
const bars = {};   // chart bars cache
function buildLayer(L){
  const c = L.content;
  const node = el('div', 'layer');
  node.dataset.id = L.id;

  if (L.type === 'text'){
    const t = el('div', 'txt');
    const base = {
      fontSize: c.fontSize + 'px', fontWeight: c.fontWeight, color: c.color,
      lineHeight: c.lineHeight, letterSpacing: c.letterSpacing + 'px',
      textAlign: c.align, width: c.maxWidth + 'px',
      fontStyle: c.italic ? 'italic' : 'normal',
      textTransform: c.uppercase ? 'uppercase' : 'none',
      fontFamily: c.fontFamily,
    };
    Object.assign(t.style, base);
    let text = c.text;
    if (L.wordTracks){
      const words = L.wordTracks.words;
      node.__words = [];
      words.forEach((w, i) => {
        if (w.br){ t.appendChild(document.createElement('br')); return; }
        const s = el('span', 'word');
        const next = words[i + 1];
        s.textContent = w.text + (L.wordTracks.mode === 'word' && next && !next.br ? ' ' : '');
        s.style.transformOrigin = 'center center';
        t.appendChild(s);
        node.__words.push({ el: s, tracks: w.tracks });
      });
    } else if (c.highlight && c.highlight.word){
      const w = c.highlight.word;
      const i = text.indexOf(w);
      if (i >= 0){
        const before = text.slice(0, i), after = text.slice(i + w.length);
        const span = el('span');
        span.textContent = w;
        span.style.color = c.highlight.color || SCENE.theme.accent || '#7C5CFF';
        t.appendChild(document.createTextNode(before));
        t.appendChild(span);
        t.appendChild(document.createTextNode(after));
      } else t.textContent = text;
    } else t.textContent = text;
    node.appendChild(t);
  }

  if (L.type === 'shape'){
    const s = el('div');
    const fill = c.fill || SCENE.theme.accent || '#7C5CFF';
    const w = c.w, h = c.h;
    const css = { width: w + 'px', height: h + 'px' };
    if (c.shape === 'circle'){
      css.borderRadius = '50%';
      css.background = (c.fill && c.fill !== 'transparent') ? fill : 'transparent';
      if (c.stroke){ css.border = `${c.strokeWidth || 2}px solid ${c.stroke}`; }
    }
    else if (c.shape === 'line'){ css.height = (c.strokeWidth || 4) + 'px'; css.background = c.stroke || fill; css.borderRadius = '99px'; }
    else if (c.shape === 'triangle'){ css.background = fill; css.clipPath = 'polygon(50% 0, 100% 100%, 0 100%)'; }
    else { css.background = fill; css.borderRadius = (c.radius || 0) + 'px'; }
    if (c.shape === 'rect' && c.stroke){
      css.border = `${c.strokeWidth || 2}px solid ${c.stroke}`;
      css.background = c.fill && c.fill !== 'transparent' ? fill : 'transparent';
    }
    if (c.blur) css.filter = `blur(${c.blur}px)`;
    if (c.shadow) css.boxShadow = c.shadow;
    Object.assign(s.style, css);
    node.appendChild(s);
  }

  if (L.type === 'counter'){
    const t = el('div');
    Object.assign(t.style, {
      fontSize: c.fontSize + 'px', fontWeight: c.fontWeight, color: c.color,
      fontFamily: c.fontFamily, fontVariantNumeric: 'tabular-nums',
      letterSpacing: '-0.03em', whiteSpace: 'nowrap',
    });
    node.appendChild(t);
    node.__counter = t;
  }

  if (L.type === 'chart'){
    const wrap = el('div', '', { position: 'relative', width: c.w + 'px', height: c.h + 'px' });
    const vals = c.values || [];
    const max = Math.max.apply(null, vals.concat([1]));
    const n = vals.length || 1;
    const slot = c.w / n;
    const barW = Math.min(slot * 0.52, 96);
    node.__bars = [];
    vals.forEach((v, i) => {
      const b = el('div', 'bar', {
        width: barW + 'px', height: '0px', left: (slot * i + slot / 2 - barW / 2) + 'px',
        background: `linear-gradient(180deg, ${c.color}, ${c.color}88)`,
      });
      const lab = el('div', 'barlabel', { left: (slot * i + slot / 2) + 'px', color: c.labelColor,
        fontSize: Math.max(22, Math.round(c.w / 30)) + 'px' });
      lab.textContent = (c.labels || [])[i] || '';
      wrap.appendChild(b);
      if ((c.labels || [])[i]) wrap.appendChild(lab);
      node.__bars.push(b);
    });
    node.appendChild(wrap);
    node.__chart = c;
  }

  if (L.type === 'image'){
    const img = el('img', '', { width: (c.w) + 'px', height: (c.h) + 'px', objectFit: c.fit, display: 'block' });
    img.src = c.src;
    node.appendChild(img);
  }

  node.style.transform = 'translate(-50%,-50%)';
  stage.appendChild(node);
  nodes[L.id] = node;
}

SCENE.layers.forEach(buildLayer);

/* ---------- render frame ---------- */
function render(frame){
  for (const L of SCENE.layers){
    const node = nodes[L.id];
    const local = frame - L.from;
    const visible = local >= 0 && local < L.dur;
    if (!visible){ node.style.display = 'none'; continue; }
    node.style.display = 'block';

    const tr = L.tracks || {};
    const v = (p, base) => trackValue(tr, p, local, base);

    const opacity = clamp01(v('opacity', L.opacity)) * (L.opacity !== 1 ? 1 : 1);
    const x = v('x', L.x), y = v('y', L.y);
    const sx = v('scale', 1) * v('scaleX', 1), sy = v('scale', 1) * v('scaleY', 1);
    const rot = v('rotate', L.rotate);
    const blur = v('blur', 0);
    const ct = v('clipTop', 0), cr = v('clipRight', 0), cb = v('clipBottom', 0), cl = v('clipLeft', 0);

    node.style.opacity = opacity;
    node.style.transform = `translate(-50%,-50%) translate(${x}px,${y}px) rotate(${rot}deg) scale(${sx},${sy})`;
    node.style.filter = blur > 0.05 ? `blur(${blur}px)` : 'none';
    node.style.clipPath = (ct || cr || cb || cl) ? `inset(${ct}% ${cr}% ${cb}% ${cl}%)` : 'none';
    node.style.zIndex = String(10 + L.track);
    if (L.blendMode) node.style.mixBlendMode = L.blendMode;

    if (node.__words){
      for (const w of node.__words){
        const wo = clamp01(trackValue(w.tracks, 'opacity', local, 1));
        const wy = trackValue(w.tracks, 'y', local, 0);
        const ws = trackValue(w.tracks, 'scale', local, 1);
        w.el.style.opacity = wo;
        w.el.style.transform = `translateY(${wy}px) scale(${ws})`;
      }
    }

    if (node.__counter){
      const c = L.content;
      const g = c.grow || { start: 0, dur: Math.max(12, Math.min(L.dur, 36)) };
      const p = clamp01((local - g.start) / g.dur);
      const ev = EASINGS[g.ease || 'easeOutExpo'](p);
      const val = c.from_value + (c.to_value - c.from_value) * ev;
      const txt = val.toFixed(c.decimals || 0).replace(/\B(?=(\d{3})+(?!\d))/g, c.decimals ? '' : '.');
      node.__counter.textContent = (c.prefix || '') + txt + (c.suffix || '');
    }

    if (node.__bars){
      const c = node.__chart;
      const g = c.grow || { start: 4, durationFrames: 26, intervalFrames: 4 };
      const max = Math.max.apply(null, c.values.concat([1]));
      node.__bars.forEach((b, i) => {
        const start = (g.start || 0) + i * (g.intervalFrames || 4);
        const p = clamp01((local - start) / (g.durationFrames || 26));
        const e = EASINGS['easeOutQuint'](p);
        b.style.height = ((c.values[i] / max) * (c.h - 46) * e) + 'px';
      });
    }
  }
}

/* ---------- fit stage ---------- */
function fit(){
  const wrap = stage.parentElement;
  const s = Math.min((wrap.clientWidth - 8) / W, (wrap.clientHeight - 8) / H);
  stage.style.transform = `translate(-50%,-50%) scale(${Math.max(0.1, s)})`;
}
window.addEventListener('resize', fit);
new ResizeObserver(fit).observe(document.querySelector('.wrap'));

/* ---------- controls ---------- */
const scrub = document.getElementById('scrub');
const tcEl = document.getElementById('tc');
const ph = document.getElementById('ph');
const ruler = document.getElementById('ruler');
scrub.max = TOTAL - 1;
document.getElementById('m-name').textContent = SCENE.meta.name;
document.getElementById('m-size').textContent = `${W}×${H}`;
document.getElementById('m-fps').textContent = `${FPS} fps`;
document.getElementById('m-layers').textContent = `${SCENE.layers.length} layer`;
document.getElementById('m-score').textContent = String(SCORE);
document.getElementById('preset').textContent = SCENE.meta.preset || 'custom';

SCENE.layers.forEach(L => {
  const c = el('div', 'clip', {
    left: (L.from / TOTAL * 100) + '%',
    width: Math.max(0.6, L.dur / TOTAL * 100) + '%',
    top: (4 + (L.track % 3) * 6) + 'px',
    opacity: 0.35 + 0.2 * (L.track % 3),
  });
  c.title = L.id;
  ruler.appendChild(c);
});

let frame = 0, playing = false, loop = true, last = 0;
function setFrame(f){
  frame = Math.max(0, Math.min(TOTAL - 1, Math.round(f)));
  render(frame);
  scrub.value = String(frame);
  tcEl.textContent = `${tc(frame)} / ${tc(TOTAL)} · f ${frame}/${TOTAL}`;
  ph.style.left = (frame / (TOTAL - 1) * 100) + '%';
}
function tick(ts){
  if (playing){
    if (!last) last = ts;
    const dt = (ts - last) / 1000;
    last = ts;
    let f = frame + dt * FPS;
    if (f >= TOTAL - 1){
      if (loop) f = 0; else { f = TOTAL - 1; playing = false; document.getElementById('play').textContent = '▶ Play'; }
    }
    setFrame(f);
  } else last = 0;
  requestAnimationFrame(tick);
}
document.getElementById('play').addEventListener('click', e => {
  playing = !playing;
  e.currentTarget.textContent = playing ? '❚❚ Pause' : '▶ Play';
  last = 0;
});
document.getElementById('restart').addEventListener('click', () => setFrame(0));
document.getElementById('loop').addEventListener('click', e => {
  loop = !loop;
  e.currentTarget.textContent = 'Loop: ' + (loop ? 'on' : 'off');
});
scrub.addEventListener('input', e => { playing = false; document.getElementById('play').textContent = '▶ Play'; setFrame(+e.target.value); });
ruler.addEventListener('click', e => {
  const r = ruler.getBoundingClientRect();
  setFrame((e.clientX - r.left) / r.width * (TOTAL - 1));
});
window.addEventListener('keydown', e => {
  if (e.code === 'Space'){ e.preventDefault(); document.getElementById('play').click(); }
  if (e.code === 'ArrowRight'){ playing = false; setFrame(frame + 1); }
  if (e.code === 'ArrowLeft'){ playing = false; setFrame(frame - 1); }
});

fit();
setFrame(0);
requestAnimationFrame(tick);
</script>
</body>
</html>
"""


def build(scene, out_path, score=100, scene_json_override=None):
    comp = scene["composition"]
    theme = scene["theme"] or {}
    payload = _payload(scene)
    name = scene["meta"]["name"]
    accent = theme.get("accent", "#7C5CFF")
    font = theme.get("font", "Inter, system-ui, sans-serif")
    doc = (TEMPLATE
           .replace("__NAME__", html.escape(name))
           .replace("__ACCENT__", accent)
           .replace("__FONT__", font)
           .replace("__BG__", comp.get("background", "#0B0B10"))
           .replace("__PRESET__", html.escape(scene["meta"].get("preset", "custom")))
           .replace("__SCENE__", json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
           .replace("__EASINGS__", EASING_JS)
           .replace("__TRACK__", "/* trackValue() disediakan oleh EASING_JS */")
           .replace("__SCORE__", str(int(score))))
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    return out_path
