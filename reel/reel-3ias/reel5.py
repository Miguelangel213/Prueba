import asyncio, os, subprocess, shutil, json, base64
from playwright.async_api import async_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
FPS = 30
Y = "#F5C400"; INK = "#2B2B2E"; GRAY = "#76767B"

STARTS = [0.0, 3.4, 7.2, 12.0, 16.8, 21.8, 25.6]
T = 30.0
if os.path.exists(os.path.join(OUT, "timing.json")):
    d = json.load(open(os.path.join(OUT, "timing.json"))); STARTS = d["starts"]; T = d["total"]

EVENTS = []  # (t, tipo) para los efectos de sonido
def ev(t, k): EVENTS.append((round(t, 3), k)); return t

kf = []
def scene(i, a, b):
    p = lambda t: f"{max(0,min(100,t/T*100)):.3f}%"
    if b >= T:
        kf.append(f"@keyframes sc{i}{{0%{{opacity:0}}{p(a)}{{opacity:0}}{p(a+.15)}{{opacity:1}}100%{{opacity:1}}}}")
    else:
        kf.append(f"@keyframes sc{i}{{0%{{opacity:0}}{p(a)}{{opacity:0}}{p(a+.15)}{{opacity:1}}{p(b-.2)}{{opacity:1}}{p(b)}{{opacity:0}}100%{{opacity:0}}}}")
    return f'style="animation:sc{i} {T}s linear both"'
def an(name, t, d=.45, ease="cubic-bezier(.2,.9,.3,1)"):
    return f"animation:{name} {d}s {ease} {t:.2f}s both"

def logo(k, size):
    b = base64.b64encode(open(os.path.join(OUT, f"{k}.png"), "rb").read()).decode()
    return f'<span class="lg" style="width:{size}px;height:{size}px"><img src="data:image/png;base64,{b}" style="width:{int(size*.7)}px;height:{int(size*.7)}px;object-fit:contain"></span>'
def bub(txt, who, dark=False, extra=""):
    bg = INK if dark else "#fff"; fg = "#fff" if dark else INK
    return f'<div class="bub" style="background:{bg};color:{fg};{extra}"><small>{who}</small>{txt}</div>'
def words(ws, t0, step=.14):
    return " ".join(f'<span style="{an("w", t0+i*step)}">{w}</span>' for i, w in enumerate(ws.split()))
def head(sm, big, xs, t, top, left=150, bigsize=None):
    bs = f"font-size:{bigsize}px;" if bigsize else ""
    tb = t + .15 + len(sm.split())*.14
    ev(tb, "pop")
    return f'''<div class="txt" style="top:{top}px;left:{left}px">
<div class="sm">{words(sm, t+.1)}</div>
<div class="bg" style="{bs}white-space:nowrap;{an('bigw', tb, .5)}">{big}</div>
<div class="xs" style="{an('w', tb+.45)}">{xs}</div></div>'''
def obj(style, anim, t, inner, sfx="whoosh"):
    ev(t, sfx)
    return f'<div class="obj" style="{style};{an(anim, t, .6)}">{inner}</div>'

s = STARTS + [T]
S = []
# 1 HOOK
a = s[0]; ev(0, "riser")
S.append((a, s[1], obj("left:120px;top:250px", "inTR", a+.05,
  f'<div class="note"><div class="nt">SE BUSCA</div><div class="nn">Asistente</div><div class="nl"></div><div class="nl s"></div><svg class="cross" viewBox="0 0 100 100"><path d="M8 8 92 92M92 8 8 92" pathLength="1" style="stroke-dasharray:1;{an("draw", a+1.6, .45, "ease-out")}"/></svg></div>') +
  head('No contrates un asistente', 'TODAVÍA', 'prueba antes estas 3 IAs gratis', a, 900, bigsize=200)))
ev(a+1.6, "swish")
# 2 problema
a = s[1]
bl = [("¿Me mandas la cotización?", "cliente", 90, 230), ("¿Qué quedamos en la reunión?", "socio", 330, 410), ("¿Dónde está el catálogo?", "equipo", 120, 1370), ("¿Respondiste el correo?", "cliente", 380, 1530)]
S.append((a, s[2], "".join(obj(f"left:{x}px;top:{y}px", "pop", a+.15+i*.25, bub(t, w), "tick") for i, (t, w, x, y) in enumerate(bl)) +
  head('Notas, correos, buscar info…', 'TODO EL DÍA', 'en tareas que no venden', a, 760, bigsize=138)))
# 3 ChatGPT
a = s[2]
S.append((a, s[3], obj("left:110px;right:110px;top:240px", "inTR", a+.1,
  f'''<div class="card"><div class="ch">{logo('chatgpt', 72)}<b>ChatGPT</b><span class="free">GRATIS</span></div>
<div class="ub in" style="{an('pop', a+.6, .4)}">Respóndele a un cliente que pregunta si hacemos envíos a Bogotá</div>
<div class="ub out" style="{an('pop', a+1.4, .4)}">¡Hola! 😊 Sí, enviamos a Bogotá en 2 a 3 días hábiles. ¿Te comparto las opciones?</div></div>''') +
  f'<div class="num" style="{an("pop", a+.05, .5)}">01</div>' +
  head('La primera', 'ESCRIBE', 'respuestas, correos y descripciones por ti', a+.2, 1180, bigsize=190)))
ev(a+.6, "tick"); ev(a+1.4, "ding")
# 4 Fathom
a = s[3]
import random; random.seed(3)
bars = "".join(f'<i style="height:{h}%;animation:bar .5s ease-in-out {a+ k*.03:.2f}s infinite alternate"></i>' for k, h in enumerate(random.choice([20,35,50,70,90,60,40,80,30]) for _ in range(30)))
S.append((a, s[4], obj("left:110px;right:110px;top:240px", "inTR", a+.1,
  f'''<div class="card"><div class="ch">{logo('fathom', 72)}<b>Fathom</b><span class="free">GRATIS</span></div>
<div class="rec"><span class="dotr"></span>REC · Reunión con cliente</div><div class="wave">{bars}</div>
<div class="sum" style="{an('w', a+1.6)}"><b>✓</b> Quiere 3 automatizaciones</div>
<div class="sum" style="{an('w', a+1.9)}"><b>✓</b> Siguiente paso: enviar propuesta</div></div>''') +
  f'<div class="num" style="{an("pop", a+.05, .5)}">02</div>' +
  head('La segunda', 'ANOTA', 'graba tus reuniones y te da el resumen', a+.2, 1180, bigsize=190)))
ev(a+1.6, "tick"); ev(a+1.9, "tick")
# 5 Gemini Notebook
a = s[4]
srcs = ["Lista de precios.pdf", "Catálogo", "Políticas de envío"]
sh = "".join(f'<div class="src" style="{an("inR", a+.6+i*.3, .45)}"><span class="fi"></span>{n}<span class="ok">✓</span></div>' for i, n in enumerate(srcs))
for i in range(3): ev(a+.6+i*.3, "tick")
S.append((a, s[5], obj("left:110px;right:110px;top:240px", "inTR", a+.1,
  f'''<div class="card"><div class="ch">{logo('gemini', 72)}<b>Gemini Notebook</b><span class="free">GRATIS</span></div>{sh}
<div class="ask" style="{an('pop', a+1.7, .4)}">¿Cuánto cuesta el envío a Cali?<span class="go">→</span></div></div>''') +
  f'<div class="num" style="{an("pop", a+.05, .5)}">03</div>' +
  head('La tercera', 'APRENDE', 'tu negocio y responde con tu info', a+.2, 1180, bigsize=190) +
  f'<div class="foot" style="{an("w", a+1.6)}">antes se llamaba NotebookLM</div>'))
ev(a+1.7, "ding")
# 6 combo
a = s[5]
tiles = [("fathom", "Anota", 170), ("gemini", "Cruza", 450), ("chatgpt", "Escribe", 730)]
th = "".join(f'<div class="tl" style="left:{x}px;{an("pop", a+.2+i*.35, .45)}">{logo(k, 180)}<span>{lab}</span></div>' for i, (k, lab, x) in enumerate(tiles))
for i in range(3): ev(a+.2+i*.35, "pop2")
S.append((a, s[6], f'''<svg class="arc" viewBox="0 0 1080 1920"><path d="M260 520 L 820 520" stroke="{Y}" stroke-width="10" stroke-linecap="round" fill="none" pathLength="1" style="stroke-dasharray:1;{an('draw', a+.3, 1.1, 'ease-out')}"/></svg>
<div class="tiles">{th}</div>''' + head('Juntas trabajan como tu', 'ASISTENTE', 'y no te cobran sueldo', a+.4, 900, bigsize=150)))
# 7 CTA
a = s[6]
S.append((a, T, obj("right:120px;top:300px", "inTR", a+.1, bub('2️⃣', 'tú · comentario', False, "font-size:72px;font-weight:800")) +
  head('¿Cuál pruebas primero?', 'COMENTA', '1, 2 o 3 · y guárdalo para después', a, 780, bigsize=158) +
  f'<div class="brand" style="top:1260px;{an("w", a+1.4)}"><div class="logo">AG</div><div>@angelgomezhg1</div></div>'))
ev(a+1.4, "ding")

body = "".join(f'<div class="sc" {scene(i,a,b)}>{h}</div>' for i, (a, b, h) in enumerate(S))

CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;background:#E7E6E1;color:{INK};font-family:'Inter',sans-serif;overflow:hidden;position:relative}}
.paper{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,#F2F1ED 0%,#E4E3DE 70%,#D8D7D1 100%)}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(0,0,0,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(0,0,0,.045) 1px,transparent 1px);background-size:64px 64px}}
.lines{{position:absolute;inset:0}}
.prog{{position:absolute;top:120px;left:110px;right:110px;height:5px;background:rgba(0,0,0,.08);border-radius:3px;overflow:hidden;z-index:9}}
.prog i{{display:block;height:100%;background:{INK};transform-origin:left;animation:gx {T}s linear both}}
@keyframes gx{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
.sc{{position:absolute;inset:0}} .obj{{position:absolute}}
.arc{{position:absolute;inset:0;width:1080px;height:1920px}}
.txt{{position:absolute;right:110px}}
.sm{{font-size:58px;font-weight:500;color:{GRAY};letter-spacing:-1px;line-height:1.2;max-width:820px}}
.sm span{{display:inline-block}}
.bg{{font-family:'Inter Display','Inter';font-weight:800;font-size:190px;letter-spacing:-6px;line-height:.95;color:{INK};margin:8px 0 10px;transform-origin:left center}}
.xs{{font-size:50px;font-weight:500;color:{GRAY};padding-left:6px;max-width:800px;line-height:1.25}}
.num{{position:absolute;left:150px;top:1060px;font-family:'Inter Display','Inter';font-weight:800;font-size:72px;color:{INK};background:{Y};padding:6px 26px;border-radius:20px}}
.foot{{position:absolute;left:156px;top:1660px;font-size:36px;color:{GRAY};font-weight:600;background:rgba(0,0,0,.05);padding:10px 20px;border-radius:14px}}
.bub{{font-size:42px;font-weight:600;padding:26px 36px;border-radius:40px 40px 40px 10px;box-shadow:0 30px 60px rgba(0,0,0,.14),0 4px 10px rgba(0,0,0,.06);max-width:700px;line-height:1.25}}
.bub small{{display:block;font-size:26px;font-weight:600;opacity:.55;margin-bottom:6px}}
.note{{width:560px;background:#FFFDF2;border-radius:24px;padding:40px 44px;box-shadow:0 40px 80px rgba(0,0,0,.16);transform:rotate(-4deg);position:relative}}
.nt{{font-size:30px;letter-spacing:6px;font-weight:800;color:{GRAY}}} .nn{{font-family:'Inter Display','Inter';font-size:84px;font-weight:800;margin:6px 0 24px}}
.nl{{height:14px;background:#E9E6D8;border-radius:7px;margin-bottom:14px}} .nl.s{{width:60%}}
.cross{{position:absolute;inset:-20px;width:calc(100% + 40px);height:calc(100% + 40px)}} .cross path{{stroke:#E5484D;stroke-width:9;stroke-linecap:round;fill:none}}
.card{{background:#fff;border-radius:44px;padding:36px 38px;box-shadow:0 40px 90px rgba(0,0,0,.14),0 4px 12px rgba(0,0,0,.05)}}
.ch{{display:flex;align-items:center;gap:22px;margin-bottom:28px}} .ch b{{font-family:'Inter Display','Inter';font-size:52px;font-weight:800}}
.free{{margin-left:auto;background:{Y};font-weight:800;font-size:26px;letter-spacing:2px;padding:8px 18px;border-radius:12px}}
.lg{{display:inline-flex;align-items:center;justify-content:center;background:#fff;border-radius:22px;box-shadow:0 0 0 2px #ECEBE6,0 10px 24px rgba(0,0,0,.08);flex:none}}
.ub{{font-size:36px;line-height:1.3;padding:20px 28px;border-radius:28px;margin-bottom:16px;max-width:88%}}
.ub.in{{background:#F0EFEA}} .ub.out{{background:{INK};color:#fff;margin-left:auto;border-radius:28px 28px 8px 28px}}
.rec{{display:flex;align-items:center;gap:14px;font-size:30px;font-weight:700;color:#E5484D}}
.dotr{{width:18px;height:18px;border-radius:50%;background:#E5484D;box-shadow:0 0 0 7px rgba(229,72,77,.18)}}
.wave{{display:flex;align-items:center;gap:8px;height:130px;margin:14px 0 18px}}
.wave i{{flex:1;background:{INK};border-radius:5px;transform-origin:center}}
@keyframes bar{{from{{transform:scaleY(.35)}}to{{transform:scaleY(1)}}}}
.sum{{font-size:36px;font-weight:600;margin-top:10px}} .sum b{{color:#B48A00}}
.src{{display:flex;align-items:center;gap:18px;background:#F6F5F1;border-radius:20px;padding:18px 22px;font-size:34px;font-weight:600;margin-bottom:14px}}
.fi{{width:44px;height:54px;border-radius:8px;background:#E2E0D8;position:relative;flex:none}} .fi:after{{content:"";position:absolute;left:10px;right:10px;top:16px;height:5px;background:{Y};box-shadow:0 11px 0 #B9B7AE,0 22px 0 #B9B7AE}}
.ok{{margin-left:auto;color:#B48A00;font-weight:900}}
.ask{{display:flex;align-items:center;justify-content:space-between;border:3px solid {Y};border-radius:999px;padding:16px 18px 16px 30px;font-size:34px;color:{GRAY};margin-top:20px}}
.go{{width:60px;height:60px;border-radius:50%;background:{Y};color:{INK};font-weight:900;display:flex;align-items:center;justify-content:center;font-size:34px}}
.tiles{{position:absolute;left:0;right:0;top:430px;height:300px}}
.tl{{position:absolute;display:flex;flex-direction:column;align-items:center;gap:18px;transform:translateX(-50%);font-size:40px;font-weight:700}}
.brand{{position:absolute;left:150px;display:flex;align-items:center;gap:20px;font-size:44px;font-weight:700}}
.logo{{width:84px;height:84px;border-radius:24px;background:{Y};font-family:'Inter Display','Inter';font-weight:900;font-size:38px;display:flex;align-items:center;justify-content:center}}
@keyframes w{{from{{opacity:0;transform:translateY(24px);filter:blur(6px)}}to{{opacity:1;transform:none;filter:blur(0)}}}}
@keyframes bigw{{from{{opacity:0;transform:scale(.82);filter:blur(10px)}}to{{opacity:1;transform:none;filter:blur(0)}}}}
@keyframes pop{{from{{opacity:0;transform:scale(.6)}}to{{opacity:1;transform:none}}}}
@keyframes inTR{{from{{opacity:0;transform:translate(220px,-220px)}}to{{opacity:1;transform:none}}}}
@keyframes inR{{from{{opacity:0;transform:translateX(120px)}}to{{opacity:1;transform:none}}}}
@keyframes draw{{from{{stroke-dashoffset:1}}to{{stroke-dashoffset:0}}}}
@keyframes drift{{from{{transform:translate(0,0)}}to{{transform:translate(-60px,50px)}}}}
.ln{{stroke:#5a5a5f;stroke-opacity:.3;stroke-width:2.5;fill:none;stroke-dasharray:1}}
{''.join(kf)}
"""
LINES = f"""<svg class="lines" viewBox="0 0 1080 1920" style="animation:drift {T}s linear both">
<path class="ln" pathLength="1" d="M-50 700 L1150 260" style="{an('draw',.1,1.4,'ease-out')}"/>
<path class="ln" pathLength="1" d="M780 -40 L180 1960" style="{an('draw',.3,1.6,'ease-out')}"/>
<path class="ln" pathLength="1" d="M-40 1500 L1120 1180" style="{an('draw',s[2],1.4,'ease-out')}"/>
<path class="ln" pathLength="1" d="M200 -40 L1000 1960" style="{an('draw',s[5],1.6,'ease-out')}"/></svg>"""
HTML = f"""<html><head><style>{CSS}</style></head><body><div class="paper"></div><div class="grid"></div>{LINES}<div class="prog"><i></i></div>{body}</body></html>"""

json.dump({"events": sorted(EVENTS), "starts": STARTS, "total": T}, open(os.path.join(OUT, "events.json"), "w"))

async def main():
    fr = os.path.join(OUT, "frames"); shutil.rmtree(fr, ignore_errors=True); os.makedirs(fr)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.set_content(HTML); await pg.wait_for_timeout(300)
        for k in range(int(T * FPS)):
            await pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={k/FPS*1000}}})")
            await pg.screenshot(path=f"{fr}/{k:04d}.jpg", type="jpeg", quality=92)
        await b.close()
    subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",f"{fr}/%04d.jpg","-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",os.path.join(OUT,"video_silent.mp4")],check=True)
asyncio.run(main())
