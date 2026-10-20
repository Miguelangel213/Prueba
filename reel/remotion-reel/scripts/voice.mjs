// Genera public/voz.mp3 y public/timing.json con ElevenLabs (with-timestamps).
// La llave se lee de ELEVENLABS_API_KEY (entorno o .env) y nunca se imprime.
import fs from "node:fs";

try { process.loadEnvFile(".env"); } catch {}
const KEY = process.env.ELEVENLABS_API_KEY;
if (!KEY) { console.error("Falta ELEVENLABS_API_KEY (variable de entorno o .env)"); process.exit(1); }
const H = { "xi-api-key": KEY };

const FRASES = [
  "No contrates un asistente todavía. Primero prueba estas tres IAs gratis.",
  "Porque notas, correos, buscar información… se te va todo el día en tareas que no venden.",
  "La primera: ChatGPT. Escribe respuestas, correos y descripciones por ti.",
  "La segunda: Fathom. Graba tus reuniones y te entrega el resumen.",
  "La tercera: Gemini Notebook, antes NotebookLM. Se aprende tu negocio y responde con tu información.",
  "Juntas trabajan como tu asistente… y no te cobran sueldo.",
  "¿Cuál pruebas primero? Comenta uno, dos o tres.",
];
const TEXTO = FRASES.join(" ");

const score = (v) => {
  const l = v.labels ?? {};
  const d = `${v.description ?? ""} ${Object.values(l).join(" ")}`.toLowerCase();
  let s = 0;
  if (l.gender === "male") s += 4;
  if (/spanish|español/.test(d) || l.language === "es") s += 3;
  if (/latin|mexic|colomb|argent|latam/.test(d)) s += 3;
  if (/energetic|confident|warm|social|conversational/.test(d)) s += 1;
  return s;
};

const res = await fetch("https://api.elevenlabs.io/v1/voices", { headers: H });
if (!res.ok) { console.error("voices:", res.status); process.exit(1); }
const voices = (await res.json()).voices.sort((a, b) => score(b) - score(a));
console.log("Voces (top 8):");
voices.slice(0, 8).forEach((v) => console.log(`  ${score(v)}  ${v.name}  ${JSON.stringify(v.labels)}`));
const voz = voices[Number(process.env.VOICE_INDEX ?? 0)];
console.log("USADA:", voz.name, voz.voice_id);

const r = await fetch(
  `https://api.elevenlabs.io/v1/text-to-speech/${voz.voice_id}/with-timestamps?output_format=mp3_44100_128`,
  {
    method: "POST",
    headers: { ...H, "content-type": "application/json" },
    body: JSON.stringify({
      text: TEXTO,
      model_id: "eleven_multilingual_v2",
      voice_settings: { stability: 0.45, similarity_boost: 0.8, style: 0.3, use_speaker_boost: true },
    }),
  },
);
if (!r.ok) { console.error("tts:", r.status, (await r.text()).slice(0, 300)); process.exit(1); }
const j = await r.json();
fs.writeFileSync("public/voz.mp3", Buffer.from(j.audio_base64, "base64"));

const st = j.alignment.character_start_times_seconds;
const en = j.alignment.character_end_times_seconds;
const r3 = (x) => Math.round(x * 1000) / 1000;
const starts = [], ends = [];
let pos = 0;
for (const f of FRASES) {
  starts.push(st[pos]);
  ends.push(en[pos + f.length - 1]);
  pos += f.length + 1;
}
const timing = {
  starts: starts.map((x, i) => (i === 0 ? 0 : r3(Math.max(0, x - 0.15)))),
  ends: ends.map(r3),
  total: r3(en[en.length - 1] + 1.5),
  voice: voz.name,
};
fs.writeFileSync("public/timing.json", JSON.stringify(timing));
console.log(JSON.stringify(timing));
