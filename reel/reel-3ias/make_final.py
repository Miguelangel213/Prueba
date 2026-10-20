import os, sys, json, base64, subprocess, requests
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
load_dotenv(os.path.join(HERE, ".env"))
KEY = os.environ.get("ELEVENLABS_API_KEY")
if not KEY: sys.exit("Falta ELEVENLABS_API_KEY en .env")
H = {"xi-api-key": KEY}

FRASES = [
 "No contrates un asistente todavía. Primero prueba estas tres IAs gratis.",
 "Porque notas, correos, buscar información… se te va todo el día en tareas que no venden.",
 "La primera: ChatGPT. Escribe respuestas, correos y descripciones por ti.",
 "La segunda: Fathom. Graba tus reuniones y te entrega el resumen.",
 "La tercera: Gemini Notebook, antes NotebookLM. Se aprende tu negocio y responde con tu información.",
 "Juntas trabajan como tu asistente… y no te cobran sueldo.",
 "¿Cuál pruebas primero? Comenta uno, dos o tres.",
]
TEXTO = " ".join(FRASES)

def run(*a): subprocess.run(list(a), check=True)

# 3. voz
if not os.path.exists("timing.json") or not os.path.exists("voz.mp3"):
    vs = requests.get("https://api.elevenlabs.io/v1/voices", headers=H).json()["voices"]
    def score(v):
        l = v.get("labels", {}); d = (v.get("description") or "") + " " + " ".join(l.values())
        d = d.lower(); s = 0
        if l.get("gender") == "male": s += 4
        if "spanish" in d or "español" in d or l.get("language") == "es": s += 3
        if any(w in d for w in ("latin", "mexic", "colomb", "argent", "latam")): s += 3
        if any(w in d for w in ("energetic", "confident", "warm", "social", "conversational")): s += 1
        return s
    vs.sort(key=score, reverse=True)
    print("Voces (top 8):"); [print(f"  {score(v)}  {v['name']}  {v.get('labels')}") for v in vs[:8]]
    voz = vs[int(os.environ.get("VOICE_INDEX", 0))]
    print("USADA:", voz["name"], voz["voice_id"])
    r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voz['voice_id']}/with-timestamps",
        headers=H, params={"output_format": "mp3_44100_128"},
        json={"text": TEXTO, "model_id": "eleven_multilingual_v2",
              "voice_settings": {"stability": .45, "similarity_boost": .8, "style": .3, "use_speaker_boost": True}})
    r.raise_for_status(); j = r.json()
    open("voz.mp3", "wb").write(base64.b64decode(j["audio_base64"]))
    al = j["alignment"]; st = al["character_start_times_seconds"]; en = al["character_end_times_seconds"]
    starts, pos = [], 0
    for f in FRASES:
        starts.append(st[pos]); pos += len(f) + 1
    starts = [0.0] + [round(max(0, x - .15), 3) for x in starts[1:]]
    total = round(en[-1] + 1.5, 3)
    json.dump({"starts": starts, "total": total, "voice": voz["name"]}, open("timing.json", "w"))
    json.dump({"starts_voz": [round(x, 3) for x in starts]}, open("voz_alineacion.json", "w"))
    print("starts", starts, "total", total)

T = json.load(open("timing.json"))["total"]
# 5. animación + sfx
run("python3", "reel5.py"); run("python3", "sfx.py", "sfx.wav")
# 6. música
if os.path.exists("musica.mp3"):
    run("ffmpeg","-y","-loglevel","error","-i","musica.mp3","-t",str(T),"-af",f"afade=t=in:d=.3,afade=t=out:st={T-1.5}:d=1.5","music.wav")
else:
    run("python3", "music.py", str(T), "music.wav")
# 7. mezcla
fc = ("[0:a]apad=whole_dur=%f,asplit=2[v][vs];[1:a]volume=0.7[sf];[2:a]volume=0.18[m0];"
      "[m0][vs]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[m];"
      "[v][sf][m]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.89[a]") % T
run("ffmpeg","-y","-loglevel","error","-i","voz.mp3","-i","sfx.wav","-i","music.wav","-i","video_silent.mp4",
    "-filter_complex",fc,"-map","3:v","-map","[a]","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
    "-t",str(T),"-movflags","+faststart","reel_3IAs_final.mp4")
print("LISTO reel_3IAs_final.mp4")
