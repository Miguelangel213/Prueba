import React from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type ReelProps = {
  starts: number[];
  ends: number[];
  total: number;
  hasVoice: boolean;
  bigAt?: number[];
  footAt?: number;
};

const Y = "#F5C400";
const INK = "#2B2B2E";
const GRAY = "#76767B";

const E_DEF = Easing.bezier(0.2, 0.9, 0.3, 1);
const E_OUT = Easing.bezier(0, 0, 0.58, 1);
const clamp01 = (x: number) => Math.max(0, Math.min(1, x));

type Anim = "w" | "bigw" | "pop" | "inTR" | "inR";

// Equivalente a `animation: name d ease t0 both` del CSS original.
const A = (
  t: number,
  name: Anim,
  t0: number,
  d = 0.45,
  ease: (x: number) => number = E_DEF,
): React.CSSProperties => {
  const p = ease(clamp01((t - t0) / d));
  switch (name) {
    case "w":
      return {
        opacity: p,
        transform: `translateY(${24 * (1 - p)}px)`,
        filter: `blur(${6 * (1 - p)}px)`,
      };
    case "bigw":
      return {
        opacity: p,
        transform: `scale(${0.82 + 0.18 * p})`,
        filter: `blur(${10 * (1 - p)}px)`,
      };
    case "pop":
      return { opacity: p, transform: `scale(${0.6 + 0.4 * p})` };
    case "inTR":
      return {
        opacity: p,
        transform: `translate(${220 * (1 - p)}px,${-220 * (1 - p)}px)`,
      };
    case "inR":
      return { opacity: p, transform: `translateX(${120 * (1 - p)}px)` };
  }
};

const drawOffset = (t: number, t0: number, d: number) =>
  1 - E_OUT(clamp01((t - t0) / d));


const FPS = 30;
const SP = (t: number, t0: number, damping = 10, stiffness = 130) =>
  spring({ frame: Math.max(0, (t - t0) * FPS), fps: FPS, config: { damping, stiffness, mass: 0.8 } });
const rnd = (i: number, k = 1) => {
  const x = Math.sin(i * 127.1 + k * 311.7) * 43758.5453;
  return x - Math.floor(x);
};

const Sticker: React.FC<{
  t: number; t0: number; e: string; x: number; y: number; size?: number; rot?: number; phase?: number;
}> = ({ t, t0, e, x, y, size = 110, rot = 0, phase = 0 }) => {
  const p = SP(t, t0);
  return (
    <div
      style={{
        position: "absolute", left: x, top: y, fontSize: size, lineHeight: 1,
        opacity: clamp01(p * 3),
        transform: `translateY(${Math.sin(t * 2.2 + phase) * 10}px) rotate(${rot + Math.sin(t * 1.7 + phase) * 6}deg) scale(${p})`,
        filter: "drop-shadow(0 12px 18px rgba(0,0,0,.18))",
      }}
    >
      {e}
    </div>
  );
};

const COLORS = [Y, INK, "#E5484D", "#fff", Y];
const Burst: React.FC<{ t: number; t0: number; x: number; y: number; n?: number }> = ({ t, t0, x, y, n = 22 }) => {
  const d = t - t0;
  if (d < 0 || d > 1.5) return null;
  return (
    <>
      {Array.from({ length: n }, (_, i) => {
        const ang = (i / n) * Math.PI * 2 + rnd(i) * 0.6;
        const sp = 450 + rnd(i, 2) * 550;
        const dist = (sp * (1 - Math.exp(-d * 3))) / 3;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x + Math.cos(ang) * dist,
              top: y + Math.sin(ang) * dist + 900 * d * d * 0.5,
              width: 14, height: 26, borderRadius: 4,
              background: COLORS[i % COLORS.length],
              boxShadow: "0 0 0 2px rgba(0,0,0,.08)",
              opacity: 1 - clamp01((d - 0.9) / 0.6),
              transform: `rotate(${d * 500 * (i % 2 ? 1 : -1)}deg)`,
            }}
          />
        );
      })}
    </>
  );
};

const Background: React.FC<{ t: number }> = ({ t }) => (
  <>
    {[0, 1, 2].map((i) => (
      <div
        key={i}
        style={{
          position: "absolute", width: 760, height: 760, borderRadius: "50%",
          left: 540 + Math.cos(t * 0.35 + i * 2.1) * 380 - 380,
          top: 960 + Math.sin(t * 0.28 + i * 1.7) * 700 - 380,
          background: `radial-gradient(circle,rgba(245,196,0,${i === 1 ? 0.3 : 0.17}),transparent 65%)`,
        }}
      />
    ))}
    {Array.from({ length: 28 }, (_, i) => {
      const size = 8 + rnd(i, 3) * 20;
      const y = (((rnd(i, 4) * 2100 - t * (30 + rnd(i, 5) * 60)) % 2100) + 2100) % 2100 - 100;
      const ring = i % 3 === 0;
      return (
        <div
          key={i}
          style={{
            position: "absolute",
            left: rnd(i, 6) * 1080 + Math.sin(t * 0.8 + i) * 30,
            top: y, width: size, height: size, borderRadius: "50%",
            background: ring ? "transparent" : i % 2 ? "rgba(245,196,0,.55)" : "rgba(43,43,46,.16)",
            border: ring ? "3px solid rgba(43,43,46,.18)" : "none",
          }}
        />
      );
    })}
  </>
);

const Logo: React.FC<{ k: string; size: number }> = ({ k, size }) => (
  <span className="lg" style={{ width: size, height: size }}>
    <img
      src={staticFile(`${k}.png`)}
      style={{ width: Math.round(size * 0.7), height: Math.round(size * 0.7), objectFit: "contain" }}
    />
  </span>
);

const Bub: React.FC<{ who: string; children: React.ReactNode; style?: React.CSSProperties }> = ({
  who,
  children,
  style,
}) => (
  <div className="bub" style={{ background: "#fff", color: INK, ...style }}>
    <small>{who}</small>
    {children}
  </div>
);

const Words: React.FC<{ t: number; text: string; t0: number; step?: number }> = ({
  t,
  text,
  t0,
  step = 0.14,
}) => (
  <>
    {text.split(" ").map((w, i) => (
      <React.Fragment key={i}>
        {i > 0 && " "}
        <span style={A(t, "w", t0 + i * step)}>{w}</span>
      </React.Fragment>
    ))}
  </>
);

const tbOf = (t0: number, sm: string) => t0 + 0.15 + sm.split(" ").length * 0.14;

const Head: React.FC<{
  t: number;
  sm: string;
  big: string;
  xs: string;
  t0: number;
  top: number;
  bigsize?: number;
  tbAt?: number;
}> = ({ t, sm, big, xs, t0, top, bigsize, tbAt }) => {
  const tb = tbAt ?? tbOf(t0, sm);
  const sp = SP(t, tb, 9, 150);
  return (
    <div className="txt" style={{ top, left: 150 }}>
      <div className="sm">
        <Words t={t} text={sm} t0={t0 + 0.1} />
      </div>
      <div style={{ position: "relative", width: "fit-content" }}>
        <div
          style={{
            position: "absolute", left: -12, right: -12, bottom: "10%", height: "34%",
            background: Y, borderRadius: 10, transformOrigin: "left center",
            transform: `scaleX(${E_DEF(clamp01((t - tb - 0.1) / 0.45))})`,
          }}
        />
        <div
          className="bg"
          style={{
            position: "relative", fontSize: bigsize, whiteSpace: "nowrap",
            opacity: clamp01(sp * 4),
            transform: `scale(${0.6 + 0.4 * sp})`,
            filter: `blur(${10 * (1 - clamp01(sp))}px)`,
          }}
        >
          {big}
        </div>
      </div>
      <div className="xs" style={A(t, "w", tb + 0.45)}>
        {xs}
      </div>
    </div>
  );
};

const Obj: React.FC<{
  t: number;
  pos: React.CSSProperties;
  anim: Anim;
  t0: number;
  children: React.ReactNode;
}> = ({ t, pos, anim, t0, children }) => (
  <div className="obj" style={{ ...pos, ...A(t, anim, t0, 0.6) }}>
    <div style={{ transform: `translateY(${Math.sin(t * 1.9 + t0 * 3) * 8 * clamp01((t - t0 - 0.6) / 0.4)}px)` }}>
      {children}
    </div>
  </div>
);

const Num: React.FC<{ t: number; a: number; n: string }> = ({ t, a, n }) => (
  <div className="num" style={{ transform: `scale(${SP(t, a + 0.05, 8, 160)}) rotate(${(1 - SP(t, a + 0.05, 8, 160)) * -20}deg)` }}>
    {n}
  </div>
);

// Fathom: barras de onda (animation infinite alternate con delay)
const WAVE_HEIGHTS = (() => {
  let seed = 3;
  const rnd = () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff;
    return seed / 0x7fffffff;
  };
  const opts = [20, 35, 50, 70, 90, 60, 40, 80, 30];
  return Array.from({ length: 30 }, () => opts[Math.floor(rnd() * opts.length)]);
})();
const EASE_IO = Easing.inOut(Easing.ease);
const barScale = (t: number, delay: number) => {
  if (t < delay) return 1;
  const ph = (t - delay) / 0.5;
  const cyc = Math.floor(ph);
  const fr = ph - cyc;
  const e = EASE_IO(cyc % 2 === 0 ? fr : 1 - fr);
  return 0.35 + 0.65 * e;
};

const Chips: React.FC<{ t: number; a: number }> = ({ t, a }) => {
  const t0 = a + 2.2;
  const idx = Math.max(0, Math.floor((t - t0) / 0.7));
  const frac = Math.max(0, ((t - t0) / 0.7) % 1);
  const cur = idx % 3;
  const prev = idx === 0 ? 0 : (idx + 2) % 3;
  const cx = (i: number) => 150 + i * 230 + 85;
  const move = E_DEF(clamp01(frac / 0.3));
  const fx = cx(prev) + (cx(cur) - cx(prev)) * move;
  const press = 1 - 0.1 * Math.sin(Math.PI * clamp01(frac / 0.25));
  return (
    <>
      {[1, 2, 3].map((n, i) => {
        const on = t > t0 && i === cur;
        const sp = SP(t, a + 1.8 + i * 0.15, 9, 160);
        return (
          <div key={n} style={{ position: "absolute", left: 150 + i * 230, top: 1450, width: 170, height: 170, borderRadius: 44, background: on ? Y : "#fff", color: INK, fontFamily: "'Inter Display','Inter'", fontWeight: 800, fontSize: 100, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 24px 50px rgba(0,0,0,.14)", transform: `scale(${sp * (on ? 1.1 * press : 1)})` }}>{n}</div>
        );
      })}
      <div style={{ position: "absolute", left: fx - 50, top: 1570 + (1 - press) * 120, fontSize: 100, lineHeight: 1, opacity: clamp01(SP(t, a + 2.1) * 3), transform: `rotate(-12deg) scale(${SP(t, a + 2.1)})`, filter: "drop-shadow(0 12px 14px rgba(0,0,0,.2))" }}>👆</div>
    </>
  );
};

export const Reel: React.FC<ReelProps> = ({ starts, ends, total: T, hasVoice, bigAt, footAt }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const s = [...starts, T];

  const impacts = [
    bigAt?.[0] ?? tbOf(s[0], "No contrates un asistente"),
    bigAt?.[1] ?? tbOf(s[1], "Notas, correos, buscar info…"),
    bigAt?.[2] ?? tbOf(s[2] + 0.2, "La primera"),
    bigAt?.[3] ?? tbOf(s[3] + 0.2, "La segunda"),
    bigAt?.[4] ?? tbOf(s[4] + 0.2, "La tercera"),
    bigAt?.[5] ?? tbOf(s[5] + 0.4, "Juntas trabajan como tu"),
    bigAt?.[6] ?? tbOf(s[6], "¿Cuál pruebas primero?"),
  ];
  const sceneStyle = (i: number): React.CSSProperties => {
    const a = s[i], b = s[i + 1];
    const inn = clamp01((t - a) / 0.15);
    const out = b >= T ? 1 : 1 - clamp01((t - (b - 0.2)) / 0.2);
    const d = t - impacts[i];
    const hit = d > 0 && d < 0.45;
    const shake = hit ? 14 * Math.exp(-d * 9) * Math.sin(d * 60) : 0;
    const punch = d > 0 && d < 0.3 ? 0.03 * Math.exp(-d * 14) : 0;
    const zoom = 1 + 0.045 * clamp01((t - a) / (b - a)) + punch;
    return { opacity: Math.min(inn, out), transform: `translate(${shake}px,${-shake * 0.6}px) scale(${zoom})` };
  };

  const scenes: React.ReactNode[] = [];

  // 1 HOOK
  {
    const a = s[0];
    scenes.push(
      <>
        <Obj t={t} pos={{ left: 120, top: 250 }} anim="inTR" t0={a + 0.05}>
          <div className="note">
            <div className="nt">SE BUSCA</div>
            <div className="nn">Asistente</div>
            <div className="nl" />
            <div className="nl s" />
            <svg className="cross" viewBox="0 0 100 100">
              <path
                d="M8 8 92 92M92 8 8 92"
                pathLength={1}
                style={{ strokeDasharray: 1, strokeDashoffset: drawOffset(t, a + 1.6, 0.45) }}
              />
            </svg>
          </div>
        </Obj>
        <Head t={t} sm="No contrates un asistente" tbAt={bigAt?.[0]} big="TODAVÍA" xs="prueba antes estas 3 IAs gratis" t0={a} top={900} bigsize={200} />
        <Sticker t={t} t0={a + 0.6} e="💸" x={760} y={300} size={150} rot={12} />
        <Sticker t={t} t0={a + 0.9} e="⏰" x={830} y={560} size={110} rot={-10} phase={2} />
        <Burst t={t} t0={bigAt?.[0] ?? tbOf(a, "No contrates un asistente")} x={430} y={1010} />
      </>,
    );
  }
  // 2 problema
  {
    const a = s[1];
    const bl: [string, string, number, number][] = [
      ["¿Me mandas la cotización?", "cliente", 90, 230],
      ["¿Qué quedamos en la reunión?", "socio", 330, 410],
      ["¿Dónde está el catálogo?", "equipo", 120, 1370],
      ["¿Respondiste el correo?", "cliente", 380, 1530],
    ];
    scenes.push(
      <>
        {bl.map(([txt, who, x, y], i) => (
          <Obj key={i} t={t} pos={{ left: x, top: y }} anim="pop" t0={a + 0.15 + i * 0.25}>
            <Bub who={who}>{txt}</Bub>
          </Obj>
        ))}
        <Head t={t} sm="Notas, correos, buscar info…" tbAt={bigAt?.[1]} big="TODO EL DÍA" xs="en tareas que no venden" t0={a} top={760} bigsize={138} />
        <Sticker t={t} t0={a + 0.5} e="📧" x={790} y={240} size={120} rot={8} />
        <Sticker t={t} t0={a + 1.0} e="📝" x={830} y={1380} size={120} rot={-8} phase={1} />
        <div style={{ position: "absolute", left: 585, top: 190, width: 84, height: 84, borderRadius: "50%", background: "#E5484D", color: "#fff", fontWeight: 800, fontSize: 34, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 8px 20px rgba(229,72,77,.4)", transform: `scale(${SP(t, a + 0.7, 7, 200)})` }}>99+</div>
        <Burst t={t} t0={bigAt?.[1] ?? tbOf(a, "Notas, correos, buscar info…")} x={450} y={870} n={16} />
      </>,
    );
  }
  // 3 ChatGPT
  {
    const a = s[2];
    scenes.push(
      <>
        <Obj t={t} pos={{ left: 110, right: 110, top: 240 }} anim="inTR" t0={a + 0.1}>
          <div className="card">
            <div className="ch">
              <Logo k="chatgpt" size={72} />
              <b>ChatGPT</b>
              <span className="free">GRATIS</span>
            </div>
            <div className="ub in" style={A(t, "pop", a + 0.6, 0.4)}>
              Respóndele a un cliente que pregunta si hacemos envíos a Bogotá
            </div>
            <div className="ub out" style={A(t, "pop", a + 1.4, 0.4)}>
              ¡Hola! 😊 Sí, enviamos a Bogotá en 2 a 3 días hábiles. ¿Te comparto las opciones?
            </div>
          </div>
        </Obj>
        <Num t={t} a={a} n="01" />
        <Head t={t} sm="La primera" tbAt={bigAt?.[2]} big="ESCRIBE" xs="respuestas, correos y descripciones por ti" t0={a + 0.2} top={1180} bigsize={190} />
        <Sticker t={t} t0={a + 0.5} e="✨" x={880} y={180} size={120} rot={10} />
        <Sticker t={t} t0={a + 1.2} e="💬" x={820} y={860} size={120} rot={-8} phase={2} />
        <Burst t={t} t0={bigAt?.[2] ?? tbOf(a + 0.2, "La primera")} x={480} y={1330} />
      </>,
    );
  }
  // 4 Fathom
  {
    const a = s[3];
    scenes.push(
      <>
        <Obj t={t} pos={{ left: 110, right: 110, top: 240 }} anim="inTR" t0={a + 0.1}>
          <div className="card">
            <div className="ch">
              <Logo k="fathom" size={72} />
              <b>Fathom</b>
              <span className="free">GRATIS</span>
            </div>
            <div className="rec">
              <span className="dotr" />
              REC · Reunión con cliente
            </div>
            <div className="wave">
              {WAVE_HEIGHTS.map((h, k) => (
                <i key={k} style={{ height: `${h}%`, transform: `scaleY(${barScale(t, a + k * 0.03)})` }} />
              ))}
            </div>
            <div className="sum" style={A(t, "w", a + 1.6)}>
              <b>✓</b> Quiere 3 automatizaciones
            </div>
            <div className="sum" style={A(t, "w", a + 1.9)}>
              <b>✓</b> Siguiente paso: enviar propuesta
            </div>
          </div>
        </Obj>
        <Num t={t} a={a} n="02" />
        <Head t={t} sm="La segunda" tbAt={bigAt?.[3]} big="ANOTA" xs="graba tus reuniones y te da el resumen" t0={a + 0.2} top={1180} bigsize={190} />
        <Sticker t={t} t0={a + 0.5} e="🎙️" x={880} y={180} size={120} rot={10} />
        <Sticker t={t} t0={a + 2.1} e="📝" x={830} y={900} size={110} rot={-8} phase={1} />
        <Burst t={t} t0={bigAt?.[3] ?? tbOf(a + 0.2, "La segunda")} x={420} y={1330} />
      </>,
    );
  }
  // 5 Gemini Notebook
  {
    const a = s[4];
    const srcs = ["Lista de precios.pdf", "Catálogo", "Políticas de envío"];
    scenes.push(
      <>
        <Obj t={t} pos={{ left: 110, right: 110, top: 240 }} anim="inTR" t0={a + 0.1}>
          <div className="card">
            <div className="ch">
              <Logo k="gemini" size={72} />
              <b>Gemini Notebook</b>
              <span className="free">GRATIS</span>
            </div>
            {srcs.map((n, i) => (
              <div className="src" key={n} style={A(t, "inR", a + 0.6 + i * 0.3, 0.45)}>
                <span className="fi" />
                {n}
                <span className="ok">✓</span>
              </div>
            ))}
            <div className="ask" style={A(t, "pop", a + 1.7, 0.4)}>
              ¿Cuánto cuesta el envío a Cali?<span className="go">→</span>
            </div>
          </div>
        </Obj>
        <Num t={t} a={a} n="03" />
        <Head t={t} sm="La tercera" tbAt={bigAt?.[4]} big="APRENDE" xs="tu negocio y responde con tu info" t0={a + 0.2} top={1180} bigsize={190} />
        <Sticker t={t} t0={a + 0.5} e="🧠" x={880} y={170} size={120} rot={10} />
        <Sticker t={t} t0={a + 2.0} e="📚" x={850} y={930} size={110} rot={-8} phase={2} />
        <Burst t={t} t0={bigAt?.[4] ?? tbOf(a + 0.2, "La tercera")} x={500} y={1330} />
        <div className="foot" style={A(t, "w", footAt ?? a + 1.6)}>
          antes se llamaba NotebookLM
        </div>
      </>,
    );
  }
  // 6 combo
  {
    const a = s[5];
    const tiles: [string, string, number][] = [
      ["fathom", "Anota", 170],
      ["gemini", "Cruza", 450],
      ["chatgpt", "Escribe", 730],
    ];
    scenes.push(
      <>
        <svg className="arc" viewBox="0 0 1080 1920">
          <path
            d="M260 520 L 820 520"
            stroke={Y}
            strokeWidth={10}
            strokeLinecap="round"
            fill="none"
            pathLength={1}
            style={{ strokeDasharray: 1, strokeDashoffset: drawOffset(t, a + 0.3, 1.1) }}
          />
        </svg>
        <div className="tiles">
          {tiles.map(([k, lab, x], i) => (
            <div className="tl" key={k} style={{ left: x, ...A(t, "pop", a + 0.2 + i * 0.35, 0.45) }}>
              <Logo k={k} size={180} />
              <span>{lab}</span>
            </div>
          ))}
        </div>
        <Head t={t} sm="Juntas trabajan como tu" tbAt={bigAt?.[5]} big="ASISTENTE" xs="y no te cobran sueldo" t0={a + 0.4} top={900} bigsize={150} />
        {[400, 680].map((x, i) => (
          <div key={x} style={{ position: "absolute", left: x - 38, top: 482, width: 76, height: 76, borderRadius: "50%", background: Y, color: INK, fontWeight: 900, fontSize: 56, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 10px 24px rgba(0,0,0,.15)", transform: `scale(${SP(t, a + 0.6 + i * 0.35, 7, 200)})` }}>+</div>
        ))}
        <Sticker t={t} t0={a + 1.0} e="✨" x={110} y={240} size={100} rot={-12} />
        <Sticker t={t} t0={a + 1.3} e="⭐" x={880} y={250} size={100} rot={12} phase={2} />
        <div style={{ position: "absolute", left: 560, top: 1330, padding: "14px 30px", border: "7px solid #E5484D", color: "#E5484D", borderRadius: 18, fontWeight: 800, fontSize: 64, letterSpacing: 2, transform: `rotate(-8deg) scale(${1.6 - 0.6 * SP(t, a + 2.2, 12, 220)})`, opacity: clamp01(SP(t, a + 2.2, 12, 220) * 3) }}>$0 SUELDO</div>
        <Burst t={t} t0={bigAt?.[5] ?? tbOf(a + 0.4, "Juntas trabajan como tu")} x={540} y={1020} n={26} />
      </>,
    );
  }
  // 7 CTA
  {
    const a = s[6];
    scenes.push(
      <>
        <Obj t={t} pos={{ right: 120, top: 300 }} anim="inTR" t0={a + 0.1}>
          <Bub who="tú · comentario" style={{ fontSize: 72, fontWeight: 800 }}>2️⃣</Bub>
        </Obj>
        <Head t={t} sm="¿Cuál pruebas primero?" tbAt={bigAt?.[6]} big="COMENTA" xs="1, 2 o 3 · y guárdalo para después" t0={a} top={780} bigsize={158} />
        <Sticker t={t} t0={a + 0.8} e="❤️" x={880} y={610} size={100} rot={10} />
        <Chips t={t} a={a} />
        <Burst t={t} t0={bigAt?.[6] ?? tbOf(a, "¿Cuál pruebas primero?")} x={520} y={900} />
        <div className="brand" style={{ top: 1260, ...A(t, "w", a + 1.4) }}>
          <div className="logo">AG</div>
          <div>@angelgomezhg1</div>
        </div>
      </>,
    );
  }

  // música con ducking: baja mientras habla la voz
  const musicVol = (f: number) => {
    const tt = f / fps;
    let duck = 0;
    if (hasVoice) {
      for (let i = 0; i < starts.length; i++) {
        const v = interpolate(tt, [starts[i] + 0.15 - 0.25, starts[i] + 0.15, ends[i], ends[i] + 0.4], [0, 1, 1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        duck = Math.max(duck, v);
      }
    }
    const base = 0.2 - (0.2 - 0.1) * duck;
    return base * interpolate(tt, [0, 0.3, T - 1.5, T], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  };

  const lineStyle = (t0: number, d: number): React.CSSProperties => ({
    strokeDashoffset: drawOffset(t, t0, d),
  });

  return (
    <AbsoluteFill className="root">
      <style>{CSS}</style>
      <div className="paper" />
      <div className="grid" />
      <Background t={t} />
      <svg
        className="lines"
        viewBox="0 0 1080 1920"
        style={{ transform: `translate(${-60 * (t / T)}px,${50 * (t / T)}px)` }}
      >
        <path className="ln" pathLength={1} d="M-50 700 L1150 260" style={lineStyle(0.1, 1.4)} />
        <path className="ln" pathLength={1} d="M780 -40 L180 1960" style={lineStyle(0.3, 1.6)} />
        <path className="ln" pathLength={1} d="M-40 1500 L1120 1180" style={lineStyle(s[2], 1.4)} />
        <path className="ln" pathLength={1} d="M200 -40 L1000 1960" style={lineStyle(s[5], 1.6)} />
      </svg>
      {scenes.map((h, i) => (
        <div className="sc" key={i} style={sceneStyle(i)}>
          {h}
        </div>
      ))}
      {s.slice(1, 7).map((a, i) => {
        if (t < a - 0.25 || t > a + 0.25) return null;
        const x = interpolate(t, [a - 0.22, a + 0.22], [-1500, 1500], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
        return <div key={i} style={{ position: "absolute", top: -100, bottom: -100, left: x, width: 1300, background: Y, transform: "skewX(-14deg)", zIndex: 20 }} />;
      })}
      {hasVoice && <Audio src={staticFile("voz.mp3")} volume={1} />}
      <Audio src={staticFile("sfx.wav")} volume={0.14} />
      <Audio src={staticFile("music.wav")} volume={musicVol} />
    </AbsoluteFill>
  );
};

const CSS = `
.root{background:#E7E6E1;color:${INK};font-family:'Inter',sans-serif;overflow:hidden}
.paper{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,#F2F1ED 0%,#E4E3DE 70%,#D8D7D1 100%)}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(0,0,0,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(0,0,0,.045) 1px,transparent 1px);background-size:64px 64px}
.lines{position:absolute;inset:0;width:1080px;height:1920px}
.sc{position:absolute;inset:0} .obj{position:absolute}
.arc{position:absolute;inset:0;width:1080px;height:1920px}
.txt{position:absolute;right:110px}
.sm{font-size:58px;font-weight:500;color:${GRAY};letter-spacing:-1px;line-height:1.2;max-width:820px}
.sm span{display:inline-block}
.bg{font-family:'Inter Display','Inter';font-weight:800;font-size:190px;letter-spacing:-6px;line-height:.95;color:${INK};margin:8px 0 10px;transform-origin:left center}
.xs{font-size:50px;font-weight:500;color:${GRAY};padding-left:6px;max-width:800px;line-height:1.25}
.num{position:absolute;left:150px;top:1060px;font-family:'Inter Display','Inter';font-weight:800;font-size:72px;color:${INK};background:${Y};padding:6px 26px;border-radius:20px}
.foot{position:absolute;left:156px;top:1660px;font-size:36px;color:${GRAY};font-weight:600;background:rgba(0,0,0,.05);padding:10px 20px;border-radius:14px}
.bub{font-size:42px;font-weight:600;padding:26px 36px;border-radius:40px 40px 40px 10px;box-shadow:0 30px 60px rgba(0,0,0,.14),0 4px 10px rgba(0,0,0,.06);max-width:700px;line-height:1.25}
.bub small{display:block;font-size:26px;font-weight:600;opacity:.55;margin-bottom:6px}
.note{width:560px;background:#FFFDF2;border-radius:24px;padding:40px 44px;box-shadow:0 40px 80px rgba(0,0,0,.16);transform:rotate(-4deg);position:relative}
.nt{font-size:30px;letter-spacing:6px;font-weight:800;color:${GRAY}} .nn{font-family:'Inter Display','Inter';font-size:84px;font-weight:800;margin:6px 0 24px}
.nl{height:14px;background:#E9E6D8;border-radius:7px;margin-bottom:14px} .nl.s{width:60%}
.cross{position:absolute;inset:-20px;width:calc(100% + 40px);height:calc(100% + 40px)} .cross path{stroke:#E5484D;stroke-width:9;stroke-linecap:round;fill:none}
.card{background:#fff;border-radius:44px;padding:36px 38px;box-shadow:0 40px 90px rgba(0,0,0,.14),0 4px 12px rgba(0,0,0,.05)}
.ch{display:flex;align-items:center;gap:22px;margin-bottom:28px} .ch b{font-family:'Inter Display','Inter';font-size:52px;font-weight:800}
.free{margin-left:auto;background:${Y};font-weight:800;font-size:26px;letter-spacing:2px;padding:8px 18px;border-radius:12px}
.lg{display:inline-flex;align-items:center;justify-content:center;background:#fff;border-radius:22px;box-shadow:0 0 0 2px #ECEBE6,0 10px 24px rgba(0,0,0,.08);flex:none}
.ub{font-size:36px;line-height:1.3;padding:20px 28px;border-radius:28px;margin-bottom:16px;max-width:88%}
.ub.in{background:#F0EFEA} .ub.out{background:${INK};color:#fff;margin-left:auto;border-radius:28px 28px 8px 28px}
.rec{display:flex;align-items:center;gap:14px;font-size:30px;font-weight:700;color:#E5484D}
.dotr{width:18px;height:18px;border-radius:50%;background:#E5484D;box-shadow:0 0 0 7px rgba(229,72,77,.18)}
.wave{display:flex;align-items:center;gap:8px;height:130px;margin:14px 0 18px}
.wave i{flex:1;background:${INK};border-radius:5px;transform-origin:center}
.sum{font-size:36px;font-weight:600;margin-top:10px} .sum b{color:#B48A00}
.src{display:flex;align-items:center;gap:18px;background:#F6F5F1;border-radius:20px;padding:18px 22px;font-size:34px;font-weight:600;margin-bottom:14px}
.fi{width:44px;height:54px;border-radius:8px;background:#E2E0D8;position:relative;flex:none} .fi:after{content:"";position:absolute;left:10px;right:10px;top:16px;height:5px;background:${Y};box-shadow:0 11px 0 #B9B7AE,0 22px 0 #B9B7AE}
.ok{margin-left:auto;color:#B48A00;font-weight:900}
.ask{display:flex;align-items:center;justify-content:space-between;border:3px solid ${Y};border-radius:999px;padding:16px 18px 16px 30px;font-size:34px;color:${GRAY};margin-top:20px}
.go{width:60px;height:60px;border-radius:50%;background:${Y};color:${INK};font-weight:900;display:flex;align-items:center;justify-content:center;font-size:34px}
.tiles{position:absolute;left:0;right:0;top:430px;height:300px}
.tl{position:absolute;display:flex;flex-direction:column;align-items:center;gap:18px;font-size:40px;font-weight:700}
.brand{position:absolute;left:150px;display:flex;align-items:center;gap:20px;font-size:44px;font-weight:700}
.logo{width:84px;height:84px;border-radius:24px;background:${Y};font-family:'Inter Display','Inter';font-weight:900;font-size:38px;display:flex;align-items:center;justify-content:center}
.ln{stroke:#5a5a5f;stroke-opacity:.3;stroke-width:2.5;fill:none;stroke-dasharray:1}
`;
