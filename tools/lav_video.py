"""lav_video.py - en JSON-spec -> faerdig mp4 (1080x1920, 30 fps, altid med lyd).

Brug:
    python3 tools/lav_video.py specs/E01.json            -> output/E01.mp4

Spec (se specs/eksempel_video.json):
{
  "id": "E01",
  "scener": [
    {"foto": "assets/fotos/lampe.jpg", "titel": "Denne lampe kostede 40 KR",
     "sig": "Ved du hvad den her lampe kostede?", "tekst": ["kun", "40 KR"],
     "badge": 1, "stempel": "NEJ" | "JA", "zoom": "ind" | "ud" | "punch",
     "varighed": 2.2, "kredit": "Foto: Navn / Unsplash"}
  ],
  "outro": {"varighed": 2.6}
}
- "sig" = det stemmen siger (talesprog). "tekst" = undertekst-bidder (1-3 ord).
  Mangler "tekst", deles "sig" automatisk i bidder af 2 ord.
- Ord med STORE BOGSTAVER fremhaeves i brandfarven.
- Al animation styres af window.render(t). Ingen CSS-transitions, ingen tilfaeldighed uden seed.
"""
import base64
import io
import json
import math
import os
import random
import re
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import lyd  # noqa: E402
import stemme  # noqa: E402

FPS = 30
W, H = 540, 960
CHROME = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"


def load_brand():
    with open(os.path.join(HERE, "brand.json"), encoding="utf-8") as f:
        return json.load(f)


def img_data_uri(path, max_h=1600, crop=None):
    """crop = [x0, y0, x1, y1] i brøkdele (0-1) - bruges til at skære logoer/ansigter fra."""
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    if crop:
        w, h = im.size
        im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    if im.height > max_h:
        im = im.resize((int(im.width * max_h / im.height), max_h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=90)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def chunk_words(text, n=2):
    words = text.split()
    out, i = [], 0
    while i < len(words):
        take = n
        # undgaa et enkelt ord alene til sidst
        if len(words) - i == n + 1:
            take = n + 1
        out.append(" ".join(words[i:i + take]))
        i += take
    return out


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def emph(s):
    """Ord i STORE bogstaver (min. 2 tegn, gerne med tal/%) faar brandfarve."""
    def rep(m):
        return f'<b class="hl">{m.group(0)}</b>'
    return re.sub(r"\b[0-9A-ZÆØÅ%][0-9A-ZÆØÅ%,.\-]{1,}\b", rep, esc(s))


HTML = r"""<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:540px;height:960px;overflow:hidden;background:#000;font-family:'__FONT__','Montserrat','Inter',sans-serif}
.scene{position:absolute;inset:0;overflow:hidden;display:none}
.scene img{position:absolute;left:50%;top:50%;width:100%;height:100%;object-fit:cover;transform-origin:50% 50%}
.gt{position:absolute;left:0;right:0;top:0;height:330px;background:linear-gradient(rgba(0,0,0,.78),rgba(0,0,0,.45) 55%,rgba(0,0,0,0))}
.gb{position:absolute;left:0;right:0;bottom:0;height:470px;background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.5) 40%,rgba(0,0,0,.85))}
.title{position:absolute;left:28px;top:112px;width:480px;color:#fff;font-weight:900;font-size:40px;line-height:1.05;letter-spacing:-.5px;text-shadow:0 2px 10px rgba(0,0,0,.5)}
.badge{display:inline-flex;align-items:center;justify-content:center;width:52px;height:52px;border-radius:50%;background:__PRIM__;color:#161616;font-weight:900;font-size:30px;margin-right:10px;vertical-align:middle;transform-origin:50% 50%}
.hl{color:__PRIM__}
.sub{position:absolute;left:28px;bottom:220px;width:420px;color:#fff;font-weight:900;font-size:52px;line-height:1.02;text-transform:none;text-shadow:0 3px 14px rgba(0,0,0,.6);transform-origin:0 100%}
.sub span{background:rgba(0,0,0,.0)}
.stamp{position:absolute;left:60px;top:400px;padding:6px 26px;border:8px solid;border-radius:14px;font-weight:900;font-size:96px;letter-spacing:4px;transform-origin:50% 50%;background:rgba(255,255,255,.12)}
.stamp.nej{color:#FF3B30;border-color:#FF3B30}
.stamp.ja{color:#34C759;border-color:#34C759}
.credit{position:absolute;left:28px;top:350px;color:rgba(255,255,255,.75);font-size:10px;font-weight:600}
#flash{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none}
#outro{position:absolute;left:28px;bottom:220px;width:420px;display:none}
#outro .panel{background:rgba(22,22,22,.92);border-radius:22px;padding:22px 24px;border-left:8px solid __PRIM__}
#outro .logo{height:70px;max-width:300px;object-fit:contain;margin-bottom:12px;display:block}
#outro .cta{color:#fff;font-weight:900;font-size:38px;line-height:1.05}
#outro .ctasub{color:__PRIM__;font-weight:800;font-size:24px;margin-top:8px}
#outro .pin{display:inline-block;margin-top:14px;background:__PRIM__;color:#161616;font-weight:900;font-size:20px;padding:10px 18px;border-radius:40px}
</style></head><body>
__SCENES__
<div id="outro"><div class="panel">__LOGO__<div class="cta">__CTA__</div><div class="ctasub">__CTASUB__</div><div class="pin">__PIN__</div></div></div>
<div id="flash"></div>
<script>
const S = __DATA__;
function clamp(x,a,b){return Math.max(a,Math.min(b,x))}
function easeOut(x){x=clamp(x,0,1);return 1-Math.pow(1-x,3)}
function back(x){x=clamp(x,0,1);const c=1.9;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)}
window.render = function(t){
  const sc = S.scenes; let idx = sc.length-1;
  for(let i=0;i<sc.length;i++){ if(t < sc[i].end){ idx=i; break; } }
  document.querySelectorAll('.scene').forEach((el,i)=>{el.style.display = (i===idx)?'block':'none'});
  const s = sc[idx], lt = t - s.start, d = s.end - s.start, p = clamp(lt/d,0,1);
  const el = document.getElementById('sc'+idx), img = el.querySelector('img');
  // Ken Burns + punch
  let sc0 = s.zoom==='ud' ? 1.17 - 0.11*p : 1.06 + 0.11*p;
  if(s.zoom==='punch' || idx===0){ sc0 *= 1 + 0.14*(1-easeOut(lt/0.35)); }
  for(const pt of s.punches){ if(lt>=pt) sc0 *= 1 + 0.07*easeOut((lt-pt)/0.2); }
  const dx = s.dx*p, dy = s.dy*p;
  img.style.transform = `translate(-50%,-50%) translate(${dx}px,${dy}px) scale(${sc0})`;
  // titel (staar fra 0,0 s i foerste scene)
  const ti = el.querySelector('.title');
  if(ti){ const a = idx===0 ? 1 : easeOut(lt/0.18); ti.style.opacity=a; ti.style.transform=`translateY(${(1-a)*-14}px)`; }
  const bd = el.querySelector('.badge');
  if(bd){ bd.style.transform = `scale(${idx===0?1:back(lt/0.3)})`; }
  // undertekster 1-3 ord ad gangen
  const sub = el.querySelector('.sub');
  if(sub){
    let k=-1; for(let j=0;j<s.subt.length;j++){ if(lt>=s.subt[j]) k=j; }
    if(idx===0 && k<0) k=0;
    if(k<0){ sub.innerHTML=''; } else {
      if(sub.dataset.k != k){ sub.innerHTML = s.subs[k]; sub.dataset.k = k; }
      const a = (idx===0&&k===0) ? 1 : back((lt - s.subt[k])/0.16);
      sub.style.transform = `scale(${0.85+0.15*a})`; sub.style.opacity = clamp(a,0,1);
    }
  }
  const st = el.querySelector('.stamp');
  if(st){ const at=s.stampAt; if(lt<at){st.style.opacity=0;} else { const a=(lt-at)/0.22; st.style.opacity=1; st.style.transform=`rotate(-12deg) scale(${2.2-1.2*easeOut(a)})`; } }
  // hvidt blink ved sceneskift
  let fl = 0; if(idx>0 && lt<0.14) fl = 0.85*(1-lt/0.14);
  document.getElementById('flash').style.opacity = fl;
  // outro oven paa sidste billede
  const o = document.getElementById('outro');
  if(t >= S.outroStart){ const a = easeOut((t-S.outroStart)/0.3); o.style.display='block'; o.style.opacity=a; o.style.transform=`translateY(${(1-a)*40}px)`;
    if(sub) sub.style.opacity = 0; if(st) st.style.opacity = 0; }
  else { o.style.display='none'; }
};
</script></body></html>"""


def build(spec_path, out_path=None, preview_only=False):
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)
    brand = load_brand()
    vid = spec.get("id", os.path.splitext(os.path.basename(spec_path))[0])
    out_path = out_path or os.path.join(ROOT, "output", f"{vid}.mp4")
    rnd = random.Random(vid)
    scenes = spec["scener"]

    # 1) stemme
    says = [s.get("sig", "") for s in scenes]
    voices = stemme.say_scenes(says) if any(says) else None
    if voices is None and any(says):
        print("ADVARSEL: piper-stemme ikke fundet - videoen faar musik og effekter uden stemme.")

    # 2) tider
    timeline, t = [], 0.0
    for i, s in enumerate(scenes):
        d = float(s.get("varighed", 2.2))
        if voices is not None and len(voices[i]):
            d = max(d, len(voices[i]) / lyd.SR + 0.3)
        subs = s.get("tekst") or (chunk_words(s["sig"]) if s.get("sig") else [])
        # undertekst-tider: fordelt efter laengde
        lens = [max(3, len(x)) for x in subs]
        tot = sum(lens) or 1
        speak = (len(voices[i]) / lyd.SR) if (voices is not None and len(voices[i])) else d * 0.92
        subt, acc = [], 0.0
        for L in lens:
            subt.append(round(acc * speak / tot, 3))
            acc += L
        punches = [round(x, 2) for x in np.arange(2.2, d - 0.4, 2.2)]  # ingen stillestaaende scene > 3 s
        timeline.append({
            "start": round(t, 3), "end": round(t + d, 3), "zoom": s.get("zoom", "ind"),
            "dx": rnd.uniform(-14, 14), "dy": rnd.uniform(-18, 18),
            "subs": [emph(x) for x in subs], "subt": subt, "punches": punches,
            "stampAt": float(s.get("stempel_tid", 0.35)),
        })
        t += d
    outro_d = float(spec.get("outro", {}).get("varighed", 2.6))
    outro_start = t
    timeline[-1]["end"] = round(t + outro_d, 3)
    total = t + outro_d

    # 3) HTML
    parts = []
    for i, s in enumerate(scenes):
        pos = s.get("fokus", "50% 50%")
        h = [f'<div class="scene" id="sc{i}"><img src="{img_data_uri(s["foto"], crop=s.get("beskaer"))}" style="object-position:{pos}">',
             '<div class="gt"></div><div class="gb"></div>']
        if s.get("titel"):
            b = f'<span class="badge">{s["badge"]}</span>' if s.get("badge") else ""
            h.append(f'<div class="title">{b}{emph(s["titel"])}</div>')
        if s.get("kredit"):
            h.append(f'<div class="credit">{esc(s["kredit"])}</div>')
        h.append('<div class="sub"></div>')
        if s.get("stempel"):
            k = "ja" if s["stempel"].upper() == "JA" else "nej"
            h.append(f'<div class="stamp {k}">{esc(s["stempel"].upper())}</div>')
        h.append("</div>")
        parts.append("".join(h))
    logo = ""
    if brand.get("logo"):
        logo = f'<img class="logo" src="{img_data_uri(brand["logo"], 400)}">'
    html = (HTML.replace("__SCENES__", "\n".join(parts))
            .replace("__DATA__", json.dumps({"scenes": timeline, "outroStart": outro_start}))
            .replace("__PRIM__", brand["farve_primaer"]).replace("__FONT__", brand.get("font", "Montserrat"))
            .replace("__LOGO__", logo).replace("__CTA__", esc(spec.get("outro", {}).get("cta", brand["cta"])))
            .replace("__CTASUB__", esc(brand["cta_sub"]))
            .replace("__PIN__", esc(spec.get("outro", {}).get("knap", "Nye fund hver uge"))))
    tmp = tempfile.mkdtemp()
    html_path = os.path.join(tmp, "v.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # 4) lyd
    events = []
    for i, tl in enumerate(timeline):
        if i > 0:
            events.append((tl["start"], "cut"))
        for st in tl["subt"][1:]:
            events.append((tl["start"] + st, "pop"))
        if scenes[i].get("stempel"):
            events.append((tl["start"] + tl["stampAt"], "pop"))
    events.append((outro_start + 0.1, "chime"))
    voice = None
    if voices is not None:
        voice = np.zeros(int(total * lyd.SR) + 1, dtype=np.float32)
        for i, v in enumerate(voices):
            a = int((timeline[i]["start"] + 0.08) * lyd.SR)
            b = min(len(voice), a + len(v))
            voice[a:b] += v[: b - a]
    wav = os.path.join(tmp, "a.wav")
    lyd.make_track(total, events, wav, voice=voice, seed=sum(map(ord, vid)))

    # 5) frames -> ffmpeg
    from playwright.sync_api import sync_playwright
    nframes = int(round(total * FPS))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-c:v", "mjpeg",
                           "-framerate", str(FPS), "-i", "-", "-i", wav,
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out_path],
                          stdin=subprocess.PIPE)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROME if os.path.exists(CHROME) else None)
        pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
        pg.goto("file://" + html_path)
        pg.wait_for_timeout(300)
        for fi in range(nframes):
            pg.evaluate(f"window.render({fi / FPS})")
            ff.stdin.write(pg.screenshot(type="jpeg", quality=93))
        br.close()
    ff.stdin.close()
    ff.wait()
    print(f"{out_path}  ({total:.1f} s, stemme: {'ja' if voices is not None else 'nej'})")
    return out_path


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
