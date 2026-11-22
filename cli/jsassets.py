"""Easing JS/TS — satu sumber kebenaran untuk semua renderer."""

EASING_JS = r"""
function easeLinear(t){return t}
function easeInQuad(t){return t*t}
function easeOutQuad(t){return 1-(1-t)*(1-t)}
function easeInOutQuad(t){return t<0.5?2*t*t:1-Math.pow(-2*t+2,2)/2}
function easeInCubic(t){return t*t*t}
function easeOutCubic(t){return 1-Math.pow(1-t,3)}
function easeInOutCubic(t){return t<0.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2}
function easeInQuart(t){return t*t*t*t}
function easeOutQuart(t){return 1-Math.pow(1-t,4)}
function easeInOutQuart(t){return t<0.5?8*t*t*t*t:1-Math.pow(-2*t+2,4)/2}
function easeOutQuint(t){return 1-Math.pow(1-t,5)}
function easeInOutQuint(t){return t<0.5?16*t*t*t*t*t:1-Math.pow(-2*t+2,5)/2}
function easeOutExpo(t){return t>=1?1:1-Math.pow(2,-10*t)}
function easeInOutExpo(t){if(t===0||t===1)return t;return t<0.5?Math.pow(2,20*t-10)/2:(2-Math.pow(2,-20*t+10))/2}
function easeOutCirc(t){return t<1?Math.sqrt(1-Math.pow(t-1,2)):1}
function easeOutBack(t,s){s=s===undefined?1.70158:s;var c3=s+1;return 1+c3*Math.pow(t-1,3)+s*Math.pow(t-1,2)}
function easeInOutBack(t,s){s=s===undefined?1.70158:s;var c2=s*1.525;return t<0.5?(Math.pow(2*t,2)*((c2+1)*2*t-c2))/2:(Math.pow(2*t-2,2)*((c2+1)*(t*2-2)+c2)+2)/2}
function easeOutElastic(t){if(t===0||t===1)return t;var c4=(2*Math.PI)/3;return Math.pow(2,-10*t)*Math.sin((t*10-0.75)*c4)+1}
function easeOutBounce(t){var n1=7.5625,d1=2.75;if(t<1/d1){return n1*t*t}if(t<2/d1){t-=1.5/d1;return n1*t*t+0.75}if(t<2.5/d1){t-=2.25/d1;return n1*t*t+0.9375}t-=2.625/d1;return n1*t*t+0.984375}
function springSoft(t){if(t>=1)return 1;var w=12;return 1-Math.exp(-0.85*w*t)*(1+0.85*w*t*(1-t)*0.35)}
function springSnappy(t){if(t>=1)return 1;var w=18;return 1-Math.exp(-0.62*w*t)*Math.cos(1.35*w*t*0.35)}

var EASINGS = {
  linear: easeLinear,
  easeInQuad: easeInQuad, easeOutQuad: easeOutQuad, easeInOutQuad: easeInOutQuad,
  easeInCubic: easeInCubic, easeOutCubic: easeOutCubic, easeInOutCubic: easeInOutCubic,
  easeInQuart: easeInQuart, easeOutQuart: easeOutQuart, easeInOutQuart: easeInOutQuart,
  easeOutQuint: easeOutQuint, easeInOutQuint: easeInOutQuint,
  easeOutExpo: easeOutExpo, easeInOutExpo: easeInOutExpo,
  easeOutCirc: easeOutCirc, easeOutBack: easeOutBack, easeInOutBack: easeInOutBack,
  easeOutElastic: easeOutElastic, easeOutBounce: easeOutBounce,
  springSoft: springSoft, springSnappy: springSnappy
};

/** Nilai properti pada frame lokal. Keyframe belakangan menang. */
function trackValue(tracks, prop, frame, base){
  var keys = tracks && tracks[prop];
  if(!keys || !keys.length) return base;
  var value = base, applied = false;
  for(var i=0;i<keys.length;i++){
    var k = keys[i];
    var t = (frame - k.start)/k.dur;
    if(t < 0) continue;
    applied = true;
    var e = EASINGS[k.ease] || EASINGS.easeOutCubic;
    var p = e(t > 1 ? 1 : t);
    value = k.from + (k.to - k.from) * p;
  }
  return applied ? value : keys[0].from;
}
"""

# GSAP equivalent untuk target HyperFrames (detik + easename GSAP)
GSAP_EASE_MAP = {
    "linear": "none",
    "easeInQuad": "power1.in", "easeOutQuad": "power1.out", "easeInOutQuad": "power1.inOut",
    "easeInCubic": "power2.in", "easeOutCubic": "power2.out", "easeInOutCubic": "power2.inOut",
    "easeInQuart": "power3.in", "easeOutQuart": "power3.out", "easeInOutQuart": "power3.inOut",
    "easeOutQuint": "power4.out", "easeInOutQuint": "power4.inOut",
    "easeOutExpo": "expo.out", "easeInOutExpo": "expo.inOut",
    "easeOutCirc": "circ.out",
    "easeOutBack": "back.out(1.7)", "easeInOutBack": "back.inOut(1.7)",
    "easeOutElastic": "elastic.out(1, 0.45)", "easeOutBounce": "bounce.out",
    "springSoft": "power3.out", "springSnappy": "back.out(1.35)",
}

# Motion Canvas: easing function name yang tersedia di @motion-canvas/core
MC_EASE_MAP = {
    "linear": "linear",
    "easeInQuad": "easeInQuad", "easeOutQuad": "easeOutQuad", "easeInOutQuad": "easeInOutQuad",
    "easeInCubic": "easeInCubic", "easeOutCubic": "easeOutCubic", "easeInOutCubic": "easeInOutCubic",
    "easeInQuart": "easeInQuart", "easeOutQuart": "easeOutQuart", "easeInOutQuart": "easeInOutQuart",
    "easeOutQuint": "easeOutQuint", "easeInOutQuint": "easeInOutQuint",
    "easeOutExpo": "easeOutExpo", "easeInOutExpo": "easeInOutExpo",
    "easeOutCirc": "easeOutCirc",
    "easeOutBack": "easeOutBack", "easeInOutBack": "easeInOutBack",
    "easeOutElastic": "easeOutElastic", "easeOutBounce": "easeOutBounce",
    "springSoft": "easeOutCubic", "springSnappy": "easeOutBack",
}
