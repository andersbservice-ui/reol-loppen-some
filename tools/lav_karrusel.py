"""lav_karrusel.py - JSON-spec -> 5-7 slides (1080x1920 JPEG; TikTok tager ikke PNG).

Brug:
    python3 tools/lav_karrusel.py specs/K01.json      -> output/K01/01.jpg, 02.jpg ...

Spec (se specs/eksempel_karrusel.json):
{
  "id": "K01",
  "slides": [
    {"type": "krog", "foto": "...", "titel": "5 fund under 50 KR", "tekst": "Nr. 3 er vildt"},
    {"type": "trin", "foto": "...", "titel": "Retro lampe", "tekst": "Kun 45 kr"},
    {"type": "outro", "foto": "..."}
  ]
}
Trin nummereres automatisk. Outro-slide bruger fast tekst fra brand.json.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from lav_video import CHROME, emph, esc, img_data_uri, load_brand  # noqa: E402

CSS = """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:540px;height:960px;overflow:hidden;background:#000;font-family:'__FONT__','Montserrat',sans-serif}
.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.gt{position:absolute;left:0;right:0;top:0;height:340px;background:linear-gradient(rgba(0,0,0,.8),rgba(0,0,0,.45) 55%,rgba(0,0,0,0))}
.gb{position:absolute;left:0;right:0;bottom:0;height:470px;background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.55) 40%,rgba(0,0,0,.88))}
.title{position:absolute;left:28px;top:112px;width:480px;color:#fff;font-weight:900;font-size:46px;line-height:1.04;text-shadow:0 2px 10px rgba(0,0,0,.5)}
.num{display:inline-flex;align-items:center;justify-content:center;width:62px;height:62px;border-radius:50%;background:__PRIM__;color:#161616;font-weight:900;font-size:36px;margin-bottom:12px}
.hl{color:__PRIM__}
.txt{position:absolute;left:28px;bottom:220px;width:420px;color:#fff;font-weight:800;font-size:34px;line-height:1.12;text-shadow:0 3px 12px rgba(0,0,0,.6)}
.swipe{display:inline-block;margin-top:16px;background:__PRIM__;color:#161616;font-weight:900;font-size:24px;padding:10px 22px;border-radius:40px}
.credit{position:absolute;left:28px;top:350px;color:rgba(255,255,255,.75);font-size:10px;font-weight:600}
.panel{position:absolute;left:28px;bottom:220px;width:420px;background:rgba(22,22,22,.93);border-radius:22px;padding:24px;border-left:8px solid __PRIM__}
.panel .logo{height:80px;max-width:300px;object-fit:contain;margin-bottom:12px;display:block}
.panel .cta{color:#fff;font-weight:900;font-size:40px;line-height:1.05}
.panel .sub{color:__PRIM__;font-weight:800;font-size:24px;margin-top:8px}
.side{position:absolute;right:92px;top:120px;color:rgba(255,255,255,.85);font-weight:800;font-size:18px}"""


def slide_html(s, n, total, brand):
    css = CSS.replace("__PRIM__", brand["farve_primaer"]).replace("__FONT__", brand.get("font", "Montserrat"))
    h = [f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>"]
    if s.get("foto"):
        h.append(f'<img class="bg" src="{img_data_uri(s["foto"], crop=s.get("beskaer"))}" '
                 f'style="object-position:{s.get("fokus", "50% 50%")}">')
    else:
        h.append(f'<div class="bg" style="background:{brand["farve_moerk"]}"></div>')
    h.append('<div class="gt"></div><div class="gb"></div>')
    t = s.get("type", "trin")
    if t == "krog":
        h.append(f'<div class="title">{emph(s.get("titel", ""))}</div>')
        h.append(f'<div class="txt">{emph(s.get("tekst", ""))}<br><span class="swipe">Swipe &rarr;</span></div>')
    elif t == "trin":
        h.append(f'<div class="title"><div class="num">{n}</div><br>{emph(s.get("titel", ""))}</div>')
        if s.get("tekst"):
            h.append(f'<div class="txt" style="font-size:52px;font-weight:900">{emph(s["tekst"])}</div>')
    else:  # outro
        logo = f'<img class="logo" src="{img_data_uri(brand["logo"], 400)}">' if brand.get("logo") else ""
        h.append(f'<div class="title">{emph(s.get("titel", "Nye fund HVER UGE"))}</div>')
        h.append(f'<div class="panel">{logo}<div class="cta">{esc(brand["cta"])}</div>'
                 f'<div class="sub">{esc(brand["cta_sub"])}</div></div>')
    if s.get("kredit"):
        h.append(f'<div class="credit">{esc(s["kredit"])}</div>')
    h.append("</body></html>")
    return "".join(h)


def build(spec_path):
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)
    brand = load_brand()
    kid = spec.get("id", os.path.splitext(os.path.basename(spec_path))[0])
    slides = spec["slides"]
    if not 5 <= len(slides) <= 7:
        print(f"ADVARSEL: {len(slides)} slides - anbefalet er 5-7.")
    outdir = os.path.join(ROOT, "output", kid)
    shutil.rmtree(outdir, ignore_errors=True)
    os.makedirs(outdir)
    tmp = tempfile.mkdtemp()
    from playwright.sync_api import sync_playwright
    paths, step = [], 0
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROME if os.path.exists(CHROME) else None)
        pg = br.new_page(viewport={"width": 540, "height": 960}, device_scale_factor=2)
        for i, s in enumerate(slides):
            if s.get("type", "trin") == "trin":
                step += 1
            hp = os.path.join(tmp, f"{i}.html")
            with open(hp, "w", encoding="utf-8") as f:
                f.write(slide_html(s, step, len(slides), brand))
            pg.goto("file://" + hp)
            pg.wait_for_timeout(150)
            p = os.path.join(outdir, f"{kid}_{i + 1:02d}.jpg")
            pg.screenshot(path=p, type="jpeg", quality=90)
            paths.append(p)
        br.close()
    print("\n".join(paths))
    return paths


if __name__ == "__main__":
    build(sys.argv[1])
