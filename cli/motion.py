#!/usr/bin/env python3
"""
MOTION SKILL — CLI
==================
Satu scene.json → Remotion / HyperFrames / Motion Canvas / preview HTML.

Credit: rajxzdev · Lisensi Apache-2.0 · Python 3.9+, tanpa dependency.

Contoh:
    python3 cli/motion.py list
    python3 cli/motion.py validate examples/ads-hook.scene.json
    python3 cli/motion.py build examples/ads-hook.scene.json --target all --out out/
    python3 cli/motion.py new ads --name MyAd --out my-ad.scene.json
    python3 cli/motion.py references --category ads
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import core  # noqa: E402
import build_preview  # noqa: E402
import build_hyperframes  # noqa: E402
import build_remotion  # noqa: E402
import build_motioncanvas  # noqa: E402

C = {
    "reset": "\033[0m", "dim": "\033[2m", "bold": "\033[1m",
    "red": "\033[31m", "yellow": "\033[33m", "green": "\033[32m",
    "cyan": "\033[36m", "magenta": "\033[35m",
}


def _tty():
    return sys.stdout.isatty()


def paint(text, color):
    if not _tty():
        return text
    return f"{C.get(color, '')}{text}{C['reset']}"


BANNER = r"""
  ███╗   ███╗ ██████╗ ████████╗██╗ ██████╗ ███╗   ██╗
  ████╗ ████║██╔═══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
  ██╔████╔██║██║   ██║   ██║   ██║██║   ██║██╔██╗ ██║
  ██║╚██╔╝██║██║   ██║   ██║   ██║██║   ██║██║╚██╗██║
  ██║ ╚═╝ ██║╚██████╔╝   ██║   ██║╚██████╔╝██║ ╚████║
  ╚═╝     ╚═╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
  S K I L L   ·   motion graphics as code
  credit: rajxzdev · Apache-2.0
"""


# ----------------------------------------------------------------------------- validate
def cmd_validate(args):
    scene = core.load(args.scene)
    report = core.validate(scene)
    print()
    print(paint(f"  {os.path.basename(args.scene)}", "bold"))
    st = report["stats"]
    print(paint(f"  {st['layers']} layer · {st['animations']} animasi · "
                f"{st['fps']}fps · {st['durationSeconds']}s · score {report['score']}/100", "dim"))
    print()
    for e in report["errors"]:
        print("  " + paint("✗ ERROR  ", "red") + e)
    for w in report["warnings"]:
        print("  " + paint("! WARN   ", "yellow") + w)
    if args.verbose:
        for n in report["notes"]:
            print("  " + paint("· info   ", "dim") + paint(n, "dim"))
    if not report["errors"] and not report["warnings"]:
        print("  " + paint("✓ bersih", "green") + " — tidak ada error/warning. Siap render.")
    print()
    bar_len = int(report["score"] / 100 * 34)
    color = "green" if report["score"] >= 85 else "yellow" if report["score"] >= 60 else "red"
    print("  smoothness " + paint("█" * bar_len + "░" * (34 - bar_len), color)
          + f" {report['score']}/100")
    print()
    return 0 if report["ok"] else 1


# -------------------------------------------------------------------------------- build
def cmd_build(args):
    scene = core.load(args.scene)
    report = core.validate(scene)
    if report["errors"] and not args.force:
        print(paint("✗ scene punya error — perbaiki dulu (atau pakai --force):", "red"))
        for e in report["errors"]:
            print("   • " + e)
        return 1
    compiled = core.compile_scene(scene)
    out = args.out or os.path.join(ROOT, "out", compiled["meta"]["name"])
    os.makedirs(out, exist_ok=True)

    targets = core.RENDERERS if args.target == "all" else (args.target,)
    made = []
    if "preview" in targets:
        p = build_preview.build(compiled, os.path.join(out, "preview.html"), report["score"])
        made.append(("preview", p))
    if "hyperframes" in targets:
        p = build_hyperframes.build(compiled, os.path.join(out, "hyperframes"), report["score"])
        made.append(("hyperframes", p))
    if "remotion" in targets:
        p = build_remotion.build(compiled, os.path.join(out, "remotion"), report["score"])
        made.append(("remotion", p))
    if "motion-canvas" in targets:
        p = build_motioncanvas.build(compiled, os.path.join(out, "motion-canvas"), report["score"])
        made.append(("motion-canvas", p))

    build_report = {
        "scene": os.path.abspath(args.scene),
        "name": compiled["meta"]["name"],
        "preset": compiled["meta"]["preset"],
        "credit": "rajxzdev",
        "license": "Apache-2.0",
        "composition": compiled["composition"],
        "smoothness": report["score"],
        "errors": report["errors"],
        "warnings": report["warnings"],
        "targets": [{"renderer": t, "path": os.path.relpath(p, out)} for t, p in made],
        "layers": [{"id": l["id"], "type": l["type"], "from": l["from"], "dur": l["dur"]}
                   for l in compiled["layers"]],
    }
    with open(os.path.join(out, "build-report.json"), "w", encoding="utf-8") as fh:
        json.dump(build_report, fh, indent=2)

    print()
    print(paint(f"  build {compiled['meta']['name']}", "bold")
          + paint(f"  ({report['score']}/100)", "green" if report["score"] >= 85 else "yellow"))
    for t, p in made:
        print("  " + paint("✓", "green") + f" {t:<14}" + paint(os.path.relpath(p, os.getcwd()), "dim"))
    print("  " + paint("✓", "green") + f" {'report':<14}" + paint(os.path.relpath(os.path.join(out, 'build-report.json'), os.getcwd()), "dim"))
    if report["warnings"]:
        print()
        print(paint(f"  {len(report['warnings'])} warning (detail: build-report.json)", "yellow"))
    print()
    if "preview" in targets:
        print("  buka " + paint(os.path.relpath(os.path.join(out, "preview.html"), os.getcwd()), "cyan")
              + paint(" di browser untuk frame review.", "dim"))
    print()
    return 0


# ----------------------------------------------------------------------------- new/list
def cmd_new(args):
    preset = args.preset
    template = os.path.join(ROOT, "examples", f"{preset}.scene.json")
    if not os.path.exists(template):
        print(paint(f"✗ template preset '{preset}' tidak ada. Pilih: ads | education | 3d", "red"))
        return 1
    scene = core.load(template)
    scene["meta"]["name"] = args.name
    scene["meta"]["credit"] = "rajxzdev"
    scene["meta"]["license"] = "Apache-2.0"
    out = args.out or f"{args.name}.scene.json"
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(scene, fh, indent=2, ensure_ascii=False)
    print()
    print("  " + paint("✓", "green") + f" {out} " + paint(f"({preset} template, {len(scene['layers'])} layer)", "dim"))
    print("  " + paint("→", "cyan") + f" python3 cli/motion.py validate {out}")
    print("  " + paint("→", "cyan") + f" python3 cli/motion.py build {out} --target all --out out/{args.name}")
    print()
    return 0


def cmd_list(args):
    print(BANNER)
    print("  " + paint("PRESET", "bold"))
    presets_dir = os.path.join(ROOT, "presets")
    for f in sorted(os.listdir(presets_dir)):
        if not f.endswith(".json"):
            continue
        with open(os.path.join(presets_dir, f), encoding="utf-8") as fh:
            data = json.load(fh)
        desc = data.get("description") or data.get("_description") or ""
        print(f"    {f[:-5]:<26}" + paint(desc, "dim"))
    print()
    print("  " + paint("EASING", "bold") + paint(" (21) ", "dim"))
    print("    " + paint(", ".join(core.EASINGS.keys()), "dim"))
    print()
    print("  " + paint("TARGET", "bold"))
    print("    preview · hyperframes · remotion · motion-canvas  " + paint("(atau: all)", "dim"))
    print()
    print("  " + paint("CONTOH", "bold"))
    for f in sorted(os.listdir(os.path.join(ROOT, "examples"))):
        if f.endswith(".scene.json"):
            print("    examples/" + f)
    print()
    return 0


def cmd_references(args):
    path = os.path.join(ROOT, "references", "catalog.json")
    data = json.load(open(path, encoding="utf-8"))
    items = data["items"]
    if args.category:
        items = [i for i in items if i["category"] == args.category]
    print()
    print("  " + paint(f"{len(items)} referensi", "bold")
          + paint(f" · total {data['total']} · credit {data['credit']}", "dim"))
    print()
    cur = None
    for it in items:
        if it["category"] != cur:
            cur = it["category"]
            print("  " + paint(cur.upper(), "magenta"))
        print(f"    {it['id']:<14}{it['creator']:<26}" + paint(it["url"], "dim"))
    print()
    print("  " + paint("Cara pakai:", "bold") + " baca docs/WORKFLOW-reference-to-motion.md")
    print("  " + paint("Setiap referensi:", "dim") + " amati → catat timing → tuang ke scene.json → build → bandingkan frame.")
    print()
    return 0


def cmd_doctor(args):
    print(BANNER)
    checks = []
    checks.append(("python", sys.version.split()[0], True))
    checks.append(("scene schema", core.SCHEMA_VERSION, os.path.exists(os.path.join(ROOT, "spec", "scene.schema.json"))))
    checks.append(("catalog", f"{len(json.load(open(os.path.join(ROOT, 'references', 'catalog.json')))['items'])} refs", True))
    checks.append(("presets", "ok", os.path.isdir(os.path.join(ROOT, "presets"))))
    checks.append(("examples", "ok", os.path.isdir(os.path.join(ROOT, "examples"))))
    for tool, cmd in (("node", "node --version"), ("npm", "npm --version"),
                      ("ffmpeg", "ffmpeg -version"), ("git", "git --version")):
        checks.append((tool, "ditemukan" if shutil.which(tool) else "tidak ada", bool(shutil.which(tool))))
    for name, detail, ok in checks:
        mark = paint("✓", "green") if ok else paint("!", "yellow")
        print(f"    {mark} {name:<16}" + paint(detail, "dim"))
    print()
    print("  " + paint("Catatan:", "bold") + " Node 18+ dibutuhkan Remotion; Node 22+ & FFmpeg untuk HyperFrames.")
    print()
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="motion", description="MOTION SKILL — motion graphics as code (credit: rajxzdev)")
    sub = p.add_subparsers(dest="cmd")

    v = sub.add_parser("validate", help="lint scene + skor smoothness")
    v.add_argument("scene")
    v.add_argument("-v", "--verbose", action="store_true")
    v.set_defaults(func=cmd_validate)

    b = sub.add_parser("build", help="compile scene ke renderer")
    b.add_argument("scene")
    b.add_argument("--target", default="all", choices=["all", *core.RENDERERS])
    b.add_argument("--out", default=None)
    b.add_argument("--force", action="store_true", help="build walau ada error")
    b.set_defaults(func=cmd_build)

    n = sub.add_parser("new", help="buat scene baru dari template preset")
    n.add_argument("preset", choices=["ads", "education", "3d"])
    n.add_argument("--name", required=True)
    n.add_argument("--out", default=None)
    n.set_defaults(func=cmd_new)

    l = sub.add_parser("list", help="daftar preset, easing, target")
    l.set_defaults(func=cmd_list)

    r = sub.add_parser("references", help="daftar referensi video")
    r.add_argument("--category", choices=["ads", "education", "3d"], default=None)
    r.set_defaults(func=cmd_references)

    d = sub.add_parser("doctor", help="cek environment")
    d.set_defaults(func=cmd_doctor)

    args = p.parse_args(argv)
    if not getattr(args, "func", None):
        p.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
