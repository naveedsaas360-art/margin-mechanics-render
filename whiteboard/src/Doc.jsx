// "Doc" style: documentary hybrid. Real footage/photos with cinematic motion,
// crisp motion-graphics overlays. Authored in a 1920x1080 space, rendered at any size.
import {AbsoluteFill, Audio, Easing, Img, Loop, OffthreadVideo, Sequence, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig} from 'remotion';
import {loadFont as loadInter} from '@remotion/google-fonts/Inter';
import {Effigy} from '@opeepsfun/open-peeps';
import {loadFont as loadBebas} from '@remotion/google-fonts/BebasNeue';

const SANS = loadInter('normal', {weights: ['500', '700', '800', '900'], subsets: ['latin']}).fontFamily;
const DISPLAY = loadBebas('normal', {weights: ['400'], subsets: ['latin']}).fontFamily;
const C = {yellow: '#FFC531', red: '#FF4D4D', green: '#2BD67B', blue: '#4DA3FF', white: '#FFFFFF', ink: '#0E1116'};
const col = (c) => C[c] || c || C.white;
const ease = Easing.out(Easing.cubic);
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'};
const SHADOW = '0 4px 24px rgba(0,0,0,0.55), 0 2px 6px rgba(0,0,0,0.6)';

const measure = (text, font) => {
  measure.ctx = measure.ctx || document.createElement('canvas').getContext('2d');
  measure.ctx.font = font;
  return measure.ctx.measureText(text).width;
};
const fit = (text, weight, family, size, maxW) => {
  const w = Math.max(...String(text).split('\n').map((l) => measure(l, `${weight} ${size}px ${family}`)));
  return w > maxW ? Math.floor((size * maxW) / w) : size;
};

// Local progress of an element: s = seconds since it appeared.
const useLocal = (el) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = frame / fps - (el.t || 0);
  return {s, fps, frame: Math.round(s * fps)};
};

// ---------- Footage ----------
// Full-frame video or photo with a slow camera move, grade and crossfade-in.
const Shot = ({el}) => {
  const {s, fps} = useLocal(el);
  const fade = interpolate(s, [0, 0.35], [0, 1], clamp);
  const life = el.life || 6;
  const k = interpolate(s, [0, life], [0, 1], {extrapolateRight: 'extend'});
  const b = el.base ?? 1.04; // AI images use a higher base zoom so the generator's corner mark stays out of frame
  const moves = {
    in: {scale: b + 0.1 * k, x: 0, y: 0}, out: {scale: b + 0.1 - 0.1 * k, x: 0, y: 0},
    left: {scale: b + 0.08, x: 40 - 80 * k, y: 0}, right: {scale: b + 0.08, x: -40 + 80 * k, y: 0},
    up: {scale: b + 0.08, x: 0, y: 30 - 60 * k},
  };
  const m = moves[el.move || 'in'];
  const style = {width: '100%', height: '100%', objectFit: 'cover', objectPosition: el.focus || 'center'};
  const media = el.kind === 'image'
    ? <Img src={staticFile(el.src)} style={style} />
    : (
      <Loop durationInFrames={Math.max(1, Math.round((el.clipSeconds || 10) * fps))}>
        <OffthreadVideo src={staticFile(el.src)} muted style={style} />
      </Loop>
    );
  return (
    <AbsoluteFill style={{opacity: fade, overflow: 'hidden', background: '#000'}}>
      <AbsoluteFill style={{transform: `translate(${m.x}px, ${m.y}px) scale(${m.scale})`,
        filter: `contrast(1.08) saturate(${el.mono ? 0 : 1.08}) brightness(${1 - (el.dim ?? 0.25)})`}}>
        {media}
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 45%, rgba(0,0,0,0.55) 100%)'}} />
    </AbsoluteFill>
  );
};

// ---------- Text ----------
// Kinetic headline: words rise in one after another. *word* = highlighted with a marker sweep.
const Title = ({el}) => {
  const {s} = useLocal(el);
  const size0 = el.size || 96;
  const font = el.font === 'display' ? DISPLAY : SANS;
  const weight = el.font === 'display' ? 400 : 900;
  const maxW = el.w || 1600;
  const size = fit(String(el.text).replace(/\*/g, ''), weight, font, size0, maxW);
  const lines = String(el.text).split('\n');
  let n = 0;
  const out = s > (el.hold || 1e9) ? interpolate(s - el.hold, [0, 0.3], [1, 0], clamp) : 1;
  return (
    <div style={{position: 'absolute', left: el.x - maxW / 2, top: el.y - (lines.length * size * 1.08) / 2, width: maxW,
      textAlign: el.align || 'center', fontFamily: font, fontWeight: weight, fontSize: size, lineHeight: 1.08,
      color: col(el.color), textShadow: SHADOW, letterSpacing: el.font === 'display' ? 1 : -0.5, opacity: out,
      textTransform: el.upper === false ? 'none' : 'uppercase'}}>
      {lines.map((line, li) => (
        <div key={li}>
          {(() => { let on = false; return line.split(' ').map((raw) => {
            const opens = raw.startsWith('*');
            const closes = /\*[^A-Za-z0-9]*$/.test(raw);
            const hl = on || opens;
            on = hl && !closes;
            return {w: raw.replace(/\*/g, ''), hl};
          }); })().map(({w, hl}, wi) => {
            const i = n++;
            const p = interpolate(s, [i * 0.07, i * 0.07 + 0.35], [0, 1], clamp);
            const sweep = interpolate(s, [i * 0.07 + 0.2, i * 0.07 + 0.55], [0, 100], clamp);
            return (
              <span key={wi} style={{display: 'inline-block', marginRight: size * 0.25, position: 'relative',
                opacity: ease(p), transform: `translateY(${(1 - ease(p)) * size * 0.45}px)`,
                color: hl ? C.ink : undefined, textShadow: hl ? 'none' : undefined}}>
                {hl && <span style={{position: 'absolute', left: -size * 0.12, right: -size * 0.12, top: '8%', bottom: '4%',
                  background: col(el.hl || 'yellow'), clipPath: `inset(0 ${100 - sweep}% 0 0)`, zIndex: -1}} />}
                <span style={{position: 'relative'}}>{w}</span>
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};

// Small caption line (supporting text, sources).
const Caption = ({el}) => {
  const {s} = useLocal(el);
  const p = ease(interpolate(s, [0, 0.4], [0, 1], clamp));
  const size = fit(el.text, 600, SANS, el.size || 38, el.w || 1500);
  return (
    <div style={{position: 'absolute', left: el.x - (el.w || 1500) / 2, top: el.y - size * 0.6, width: el.w || 1500,
      textAlign: el.align || 'center', fontFamily: SANS, fontWeight: 600, fontSize: size, color: col(el.color || 'white'),
      opacity: p * (el.opacity ?? 0.92), transform: `translateY(${(1 - p) * 14}px)`, textShadow: SHADOW, letterSpacing: 0.2}}>
      {el.text}
    </div>
  );
};

// Big animated number with label, on a dark glass card.
const Stat = ({el}) => {
  const {s} = useLocal(el);
  const p = interpolate(s, [0, el.dur || 1.2], [0, 1], clamp);
  const counts = !((el.value || 0) < 10 && !el.decimals);
  const v = counts ? (el.value || 0) * ease(p) : el.value;
  const txt = `${el.prefix || ''}${v.toLocaleString('en-US', {minimumFractionDigits: el.decimals || 0, maximumFractionDigits: el.decimals || 0})}${el.suffix || ''}`;
  const finalTxt = `${el.prefix || ''}${(el.value || 0).toLocaleString('en-US', {minimumFractionDigits: el.decimals || 0, maximumFractionDigits: el.decimals || 0})}${el.suffix || ''}`;
  const size = fit(finalTxt, 400, DISPLAY, el.size || 220, (el.w || 1100) - 80);
  const pop = interpolate(s, [0, 0.18, 0.32], [0.85, 1.04, 1], clamp);
  const card = el.card !== false;
  return (
    <div style={{position: 'absolute', left: el.x - (el.w || 1100) / 2, top: el.y - size * 0.75, width: el.w || 1100,
      textAlign: 'center', transform: `scale(${pop})`, opacity: interpolate(s, [0, 0.15], [0, 1], clamp),
      padding: card ? '18px 40px 26px' : 0, borderRadius: 18,
      background: card ? 'rgba(10,12,16,0.62)' : 'none', 
      borderTop: card ? `6px solid ${col(el.color || 'yellow')}` : 'none'}}>
      <div style={{fontFamily: DISPLAY, fontSize: size, lineHeight: 1, color: col(el.color || 'yellow'), letterSpacing: 2,
        textShadow: card ? 'none' : SHADOW}}>{txt}</div>
      {el.label && <div style={{fontFamily: SANS, fontWeight: 700, fontSize: el.labelSize || 40, color: '#fff',
        marginTop: 10, opacity: interpolate(s, [0.3, 0.7], [0, 0.95], clamp), textTransform: 'uppercase', letterSpacing: 2}}>{el.label}</div>}
    </div>
  );
};

// News-style headline card (recreated text + source line; never a screenshot).
const Headline = ({el}) => {
  const {s, fps, frame} = useLocal(el);
  const sp = spring({frame, fps, config: {damping: 16, stiffness: 120}});
  const w = el.w || 1100;
  const size = fit(el.text, 800, SANS, el.size || 54, w - 90);
  return (
    <div style={{position: 'absolute', left: el.x - w / 2, top: el.y - 110, width: w, background: '#fff', borderRadius: 14,
      padding: '28px 44px 32px', boxShadow: '0 30px 70px rgba(0,0,0,0.55)', opacity: Math.min(1, sp * 1.5),
      transform: `perspective(1600px) rotateX(${(1 - sp) * 18}deg) rotateZ(${el.tilt ?? -1.2}deg) translateY(${(1 - sp) * 80}px)`}}>
      <div style={{fontFamily: SANS, fontWeight: 800, fontSize: 26, color: col(el.color || 'red'), letterSpacing: 2,
        textTransform: 'uppercase', marginBottom: 10}}>{el.source}</div>
      <div style={{fontFamily: SANS, fontWeight: 800, fontSize: size, lineHeight: 1.12, color: C.ink}}>{el.text}</div>
    </div>
  );
};

// Lower-third label bar.
const Lower = ({el}) => {
  const {s} = useLocal(el);
  const p = ease(interpolate(s, [0, 0.45], [0, 1], clamp));
  return (
    <div style={{position: 'absolute', left: el.x ?? 110, top: el.y ?? 860, display: 'flex', alignItems: 'stretch',
      clipPath: `inset(0 ${100 - p * 100}% 0 0)`}}>
      <div style={{width: 12, background: col(el.color || 'yellow')}} />
      <div style={{background: 'rgba(10,12,16,0.82)', padding: '14px 28px'}}>
        <div style={{fontFamily: SANS, fontWeight: 900, fontSize: el.size || 46, color: '#fff', textTransform: 'uppercase'}}>{el.text}</div>
        {el.sub && <div style={{fontFamily: SANS, fontWeight: 600, fontSize: 28, color: 'rgba(255,255,255,0.8)', marginTop: 4}}>{el.sub}</div>}
      </div>
    </div>
  );
};

// Clean animated bar chart on a dark panel.
const Chart = ({el}) => {
  const {s} = useLocal(el);
  const data = el.data || [];
  const max = Math.max(...data.map((d) => d.value)) * 1.1;
  const W = el.w || 1300;
  const H = el.h || 600;
  const slot = (W - 120) / data.length;
  const step = (el.dur || 3) / Math.max(1, data.length);
  return (
    <div style={{position: 'absolute', left: el.x - W / 2, top: el.y - H / 2, width: W, height: H, borderRadius: 18,
      background: 'rgba(10,12,16,0.8)', opacity: interpolate(s, [0, 0.3], [0, 1], clamp)}}>
      {el.title && <div style={{position: 'absolute', left: 50, top: 28, fontFamily: SANS, fontWeight: 800, fontSize: 40,
        color: '#fff', textTransform: 'uppercase', letterSpacing: 1}}>{el.title}</div>}
      {[0.25, 0.5, 0.75, 1].map((g) => (
        <div key={g} style={{position: 'absolute', left: 60, right: 60, bottom: 90 + (H - 220) * g, height: 2, background: 'rgba(255,255,255,0.08)'}} />
      ))}
      {data.map((d, i) => {
        const p = ease(interpolate(s, [0.3 + i * step, 0.3 + i * step + Math.min(1.2, step)], [0, 1], clamp));
        const bh = (H - 220) * (d.value / max) * p;
        const bx = 60 + slot * i + slot * 0.18;
        return (
          <div key={i}>
            <div style={{position: 'absolute', left: bx, width: slot * 0.64, bottom: 90, height: bh, borderRadius: '10px 10px 0 0',
              background: `linear-gradient(180deg, ${col(d.color || 'yellow')}, ${col(d.color || 'yellow')}aa)`}} />
            <div style={{position: 'absolute', left: bx - 40, width: slot * 0.64 + 80, bottom: 100 + bh, textAlign: 'center',
              fontFamily: DISPLAY, fontSize: 64, color: '#fff', opacity: p}}>{d.valueLabel ?? d.value}</div>
            <div style={{position: 'absolute', left: bx - 40, width: slot * 0.64 + 80, bottom: 30, textAlign: 'center',
              fontFamily: SANS, fontWeight: 700, fontSize: 34, color: 'rgba(255,255,255,0.88)'}}>{d.label}</div>
          </div>
        );
      })}
    </div>
  );
};

// Clean drawn highlight: ring or arrow (stroke reveal), for pointing at things in footage.
const Mark = ({el}) => {
  const {s} = useLocal(el);
  const p = ease(interpolate(s, [0, 0.5], [0, 1], clamp));
  const c = col(el.color || 'yellow');
  if (el.shape === 'arrow') {
    const [x1, y1] = el.from;
    const [x2, y2] = el.to;
    const len = Math.hypot(x2 - x1, y2 - y1);
    const a = Math.atan2(y2 - y1, x2 - x1);
    const h = (sg) => `${x2 - 34 * Math.cos(a + sg)},${y2 - 34 * Math.sin(a + sg)}`;
    return (
      <svg style={{position: 'absolute', inset: 0, overflow: 'visible'}} width="1920" height="1080">
        <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={c} strokeWidth={9} strokeLinecap="round"
          strokeDasharray={len} strokeDashoffset={len * (1 - p)} />
        {p > 0.95 && <polyline points={`${h(0.5)} ${x2},${y2} ${h(-0.5)}`} fill="none" stroke={c} strokeWidth={9}
          strokeLinecap="round" strokeLinejoin="round" />}
      </svg>
    );
  }
  const rx = el.w / 2;
  const ry = el.h / 2;
  const L = 2 * Math.PI * Math.sqrt((rx * rx + ry * ry) / 2) * 1.1;
  return (
    <svg style={{position: 'absolute', inset: 0, overflow: 'visible'}} width="1920" height="1080">
      <ellipse cx={el.x} cy={el.y} rx={rx} ry={ry} fill="none" stroke={c} strokeWidth={8}
        strokeDasharray={L} strokeDashoffset={L * (1 - p)} transform={`rotate(-8 ${el.x} ${el.y})`} />
    </svg>
  );
};

// Full-screen dark panel behind graphics scenes (with a subtle moving gradient).
const Panel = ({el}) => {
  const {s} = useLocal(el);
  return <AbsoluteFill style={{background: `radial-gradient(circle at ${50 + Math.sin(s * 0.4) * 20}% ${40 + Math.cos(s * 0.3) * 15}%, #1b2230 0%, #0b0e13 70%)`,
    opacity: el.opacity ?? 1}} />;  // no fade from black: panels cut in solid
};

// The money loop: three nodes on a ring; each arrow draws in at its cue time (el.reveal[i],
// scene seconds) and then carries a steady stream of dollar coins. el.reverse flips the flow.
const MoneyLoop = ({el}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const s = t - (el.t || 0);
  const cx = el.x ?? 960;
  const cy = el.y ?? 560;
  const R = el.r ?? 330;
  const nodes = el.nodes || [];
  const ang = (i) => (-90 + i * 120) * (Math.PI / 180);
  const pos = (a, r = R) => [cx + r * Math.cos(a), cy + r * Math.sin(a)];
  const gap = 0.36; // radians kept clear around each node
  const arcPt = (i, u) => {
    let a0 = ang(i) + gap;
    let a1 = ang(i + 1) - gap;
    if (el.reverse) [a0, a1] = [ang(i + 1) - gap, ang(i) + gap];
    return pos(a0 + (a1 - a0) * u);
  };
  const appear = interpolate(s, [0, 0.4], [0, 1], clamp);
  const flowColor = el.reverse ? C.red : C.green;
  return (
    <AbsoluteFill style={{opacity: appear}}>
      <svg width="1920" height="1080" style={{position: 'absolute', inset: 0}}>
        <defs>
          <filter id="glow"><feGaussianBlur stdDeviation="6" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
        </defs>
        {nodes.map((_, i) => {
          const tr = (el.reveal || [])[i] ?? (el.t || 0) + 0.6 + i * 0.8;
          const p = ease(interpolate(t, [tr, tr + 0.7], [0, 1], clamp));
          if (p <= 0) return null;
          const N = 40;
          const pts = Array.from({length: Math.max(2, Math.round(N * p))}, (_, k) => arcPt(i, (k / (N - 1)) * 1));
          const d = 'M ' + pts.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join(' L ');
          const [hx, hy] = arcPt(i, Math.min(1, p));
          const [bx, by] = arcPt(i, Math.max(0, Math.min(1, p) - 0.03));
          const ha = Math.atan2(hy - by, hx - bx);
          const head = (sg) => `${hx - 30 * Math.cos(ha + sg)},${hy - 30 * Math.sin(ha + sg)}`;
          const coins = p >= 1 ? [0, 1, 2].map((k) => arcPt(i, ((t - tr) * 0.32 + k / 3) % 1)) : [];
          return (
            <g key={i}>
              <path d={d} fill="none" stroke={flowColor} strokeWidth={8} strokeLinecap="round" opacity={0.85} filter="url(#glow)" />
              <polyline points={`${head(0.55)} ${hx},${hy} ${head(-0.55)}`} fill="none" stroke={flowColor} strokeWidth={8}
                strokeLinecap="round" strokeLinejoin="round" />
              {coins.map(([x, y], k) => (
                <g key={k} transform={`translate(${x} ${y})`}>
                  <circle r={26} fill={C.yellow} stroke="#B8860B" strokeWidth={3} />
                  <text textAnchor="middle" dominantBaseline="central" fontFamily={DISPLAY} fontSize={34} fill="#5a3d00">$</text>
                </g>
              ))}
              {el.labels && el.labels[i] && p >= 1 && (() => {
                const [lx, ly] = pos(ang(i) + Math.PI / 3, R + (i === 1 ? 90 : 100));
                return <text x={lx} y={ly} textAnchor="middle" fontFamily={SANS} fontWeight={800} fontSize={30}
                  fill="#fff" opacity={interpolate(t, [tr + 0.6, tr + 1], [0, 1], clamp)}>{el.labels[i]}</text>;
              })()}
            </g>
          );
        })}
        {nodes.map((n, i) => {
          const [x, y] = pos(ang(i));
          const pop = spring({frame: Math.round((s - i * 0.15) * fps), fps, config: {damping: 13, stiffness: 140}});
          const c = col(n.color || 'blue');
          return (
            <g key={`n${i}`} transform={`translate(${x} ${y}) scale(${pop})`}>
              <circle r={128} fill="#0f141c" stroke={c} strokeWidth={8} filter="url(#glow)" />
              <text textAnchor="middle" y={-6} fontFamily={SANS} fontWeight={900} fontSize={n.label.length > 9 ? 34 : 42} fill="#fff">{n.label}</text>
              {n.sub && <text textAnchor="middle" y={40} fontFamily={SANS} fontWeight={600} fontSize={24} fill={c}>{n.sub}</text>}
            </g>
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};

// Cold-open impact text: slams in from oversized, shakes the frame, white flash on hit.
const Slam = ({el}) => {
  const {s} = useLocal(el);
  const size = fit(el.text, 400, DISPLAY, el.size || 300, el.w || 1700);
  const scale = interpolate(s, [0, 0.12, 0.24], [2.2, 0.94, 1], clamp);
  const shake = interpolate(s, [0.1, 0.45], [1, 0], clamp);
  const dx = Math.sin(s * 90) * 22 * shake;
  const dy = Math.cos(s * 77) * 14 * shake;
  const flash = interpolate(s, [0.1, 0.13, 0.35], [0, 0.55, 0], clamp);
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: 960 - 900 + dx, top: (el.y ?? 540) - size * 0.55 + dy, width: 1800, textAlign: 'center',
        fontFamily: DISPLAY, fontSize: size, lineHeight: 1, letterSpacing: 4, color: col(el.color || 'white'),
        transform: `scale(${scale})`, opacity: interpolate(s, [0, 0.08], [0, 1], clamp),
        textShadow: '0 10px 50px rgba(0,0,0,0.75)'}}>{el.text}</div>
      <AbsoluteFill style={{background: '#fff', opacity: flash}} />
    </AbsoluteFill>
  );
};

// ---------- Animated storytelling pieces ----------

// Flat colour backdrop with slow-drifting soft shapes (never a still frame).
const Bg = ({el}) => {
  const {s} = useLocal(el);
  const [a, b] = el.colors || ['#1d2b53', '#0b1020'];
  const blobs = [[18, 30, 380], [78, 22, 300], [62, 78, 420], [12, 82, 260]];
  return (
    <AbsoluteFill style={{background: `linear-gradient(135deg, ${a}, ${b})`}}>
      {blobs.map(([x, y, r], i) => (
        <div key={i} style={{position: 'absolute', left: `${x + Math.sin(s * 0.5 + i) * 3}%`, top: `${y + Math.cos(s * 0.4 + i) * 3}%`,
          width: r, height: r, borderRadius: '50%', background: 'rgba(255,255,255,0.06)', transform: 'translate(-50%,-50%)'}} />
      ))}
    </AbsoluteFill>
  );
};

// Open Peeps character (CC0): springs in, breathes, and swaps face/pose at cue times (el.reacts[{t, face, body}]).
const Peep = ({el}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const since = t - (el.t || 0);
  let face = el.face || 'Calm';
  let body = el.body || 'Explaining';
  let last = -10;
  for (const r of el.reacts || []) if (t >= r.t) { face = r.face || face; body = r.body || body; last = r.t; }
  const enter = spring({frame: Math.round(since * fps), fps, config: {damping: 12, stiffness: 140}});
  const jolt = interpolate(t - last, [0, 0.12, 0.35], [1, 1.07, 1], clamp);
  const h = el.size || 620;
  const w = h * (940.27 / 1130.59);
  return (
    <div style={{position: 'absolute', left: el.x - w / 2, top: el.y - h / 2 + (1 - enter) * 200 + Math.sin(since * 2) * 6,
      width: w, height: h, opacity: Math.min(1, enter * 2), transformOrigin: '50% 100%',
      transform: `scaleX(${el.flip ? -1 : 1}) rotate(${Math.sin(since * 1.2) * 1.3}deg) scale(${jolt})`,
      filter: 'drop-shadow(0 18px 30px rgba(0,0,0,0.35))'}}>
      <Effigy body={{type: body, options: el.bodyOptions || {}}} head={{type: el.head || 'ShortOne', options: {}}}
        face={{type: face, options: {}}} style={{width: '100%', height: '100%', overflow: 'visible'}} />
    </div>
  );
};

// The story's dollar bill: a little character with eyes that hops from `from` to `to`.
const Dollar = ({el}) => {
  const {s} = useLocal(el);
  const travel = el.travel || 1.2;
  const p = Easing.inOut(Easing.cubic)(interpolate(s, [0.15, 0.15 + travel], [0, 1], clamp));
  const [x1, y1] = el.from || [960, 540];
  const [x2, y2] = el.to || el.from || [960, 540];
  const x = x1 + (x2 - x1) * p;
  const y = y1 + (y2 - y1) * p - Math.sin(p * Math.PI) * (el.hop ?? 160);
  const moving = p > 0 && p < 1;
  const squash = moving ? 1 : 1 + Math.sin(s * 6) * 0.04;
  const sc = (el.size || 1) * interpolate(s, [0, 0.25], [0, 1], clamp);
  const look = Math.sign(x2 - x1) * 5;
  const n = el.copies || 1;
  return (
    <>
      {Array.from({length: n}, (_, i) => {
        const ang = (i / n) * Math.PI * 2;
        const spread = n > 1 ? interpolate(s, [0.2, 1.2], [0, 1], clamp) * (140 + (i % 3) * 70) : 0;
        const dx = Math.cos(ang) * spread;
        const dy = Math.sin(ang) * spread * 0.6;
        return (
          <svg key={i} width="240" height="160" viewBox="-120 -80 240 160" style={{position: 'absolute', left: x + dx - 120,
            top: y + dy - 80, overflow: 'visible', transform: `scale(${sc * (i ? 0.7 : 1)}) rotate(${moving ? (x2 > x1 ? 8 : -8) : Math.sin(s * 3 + i) * 4}deg) scaleY(${squash})`}}>
            <rect x="-92" y="-48" width="184" height="96" rx="14" fill="#2BD67B" stroke="#0d5c35" strokeWidth="6" />
            <circle cx="0" cy="0" r="30" fill="none" stroke="#0d5c35" strokeWidth="5" />
            <text x="0" y="13" textAnchor="middle" fontFamily={DISPLAY} fontSize="46" fill="#0d5c35">$</text>
            {[-52, 52].map((ex) => (
              <g key={ex}>
                <circle cx={ex} cy="-8" r="13" fill="#fff" />
                <circle cx={ex + look} cy="-6" r="6" fill="#111" />
              </g>
            ))}
            <path d="M -60 22 Q -52 30 -44 22" stroke="#0d5c35" strokeWidth="4" fill="none" />
          </svg>
        );
      })}
    </>
  );
};

// Crisp line icon (Tabler) that draws itself, then floats gently.
const Icon = ({el}) => {
  const {s} = useLocal(el);
  const p = ease(interpolate(s, [0, el.dur || 0.7], [0, 1], clamp));
  const size = el.size || 220;
  const k = size / 24;
  const c = col(el.color || 'white');
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" style={{position: 'absolute', left: el.x - size / 2,
      top: el.y - size / 2 + Math.sin(s * 1.6) * 6, overflow: 'visible', filter: 'drop-shadow(0 10px 18px rgba(0,0,0,0.35))'}}>
      {(el.paths || []).map((d, i) => (
        <path key={i} d={d} fill="none" stroke={c} strokeWidth={1.9} strokeLinecap="round"
          strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
      ))}
      {el.label && <text x="12" y="29" textAnchor="middle" fontFamily={SANS} fontWeight="800" fontSize="3.6" fill="#fff"
        opacity={interpolate(s, [0.5, 0.9], [0, 1], clamp)}>{el.label}</text>}
    </svg>
  );
};

// Phone showing a stock chart that crashes in red.
const Phone = ({el}) => {
  const {s} = useLocal(el);
  const enter = ease(interpolate(s, [0, 0.4], [0, 1], clamp));
  const p = interpolate(s, [0.5, el.crash || 2.2], [0, 1], clamp);
  const pts = [[0, 0.30], [0.1, 0.26], [0.2, 0.32], [0.3, 0.22], [0.42, 0.27], [0.5, 0.2], [0.6, 0.35], [0.7, 0.5], [0.8, 0.62],
    [0.9, 0.8], [1, 0.9]];
  const W = 300;
  const H = 300;
  const shown = pts.filter(([x]) => x <= p);
  const d = shown.map(([x, y], i) => `${i ? 'L' : 'M'} ${20 + x * W} ${40 + y * H}`).join(' ');
  const red = p > 0.55;
  const pct = interpolate(p, [0.55, 1], [0, 28.6], clamp);
  return (
    <div style={{position: 'absolute', left: el.x - 180, top: el.y - 330 + (1 - enter) * 300, width: 360, height: 660,
      borderRadius: 48, background: '#111', border: '10px solid #2a2a2e', boxShadow: '0 30px 60px rgba(0,0,0,0.5)',
      transform: `rotate(${el.tilt ?? 6}deg)`, opacity: enter}}>
      <div style={{position: 'absolute', left: 20, top: 40, fontFamily: SANS, fontWeight: 800, fontSize: 26, color: '#aaa'}}>{el.ticker || 'CHIPS'}</div>
      <div style={{position: 'absolute', left: 20, top: 74, fontFamily: DISPLAY, fontSize: 64, color: red ? C.red : C.green}}>
        {red ? `-${pct.toFixed(1)}%` : '+0.4%'}</div>
      <svg width="340" height="420" style={{position: 'absolute', left: 0, top: 170}}>
        <path d={d} fill="none" stroke={red ? C.red : C.green} strokeWidth="7" strokeLinejoin="round" strokeLinecap="round" />
      </svg>
    </div>
  );
};

// Speech or thought bubble that pops in.
const Bubble = ({el}) => {
  const {s, fps, frame} = useLocal(el);
  const sp = spring({frame, fps, config: {damping: 11, stiffness: 160}});
  const w = el.w || 620;
  const size = fit(el.text, 800, SANS, el.size || 60, w - 70);
  return (
    <div style={{position: 'absolute', left: el.x - w / 2, top: el.y - 90, width: w, transform: `scale(${sp})`,
      transformOrigin: el.tail === 'right' ? '90% 100%' : '10% 100%'}}>
      <div style={{background: '#fff', borderRadius: 34, padding: '26px 34px', fontFamily: SANS, fontWeight: 800, fontSize: size,
        color: C.ink, textAlign: 'center', boxShadow: '0 20px 40px rgba(0,0,0,0.35)'}}>{el.text}</div>
      {el.thought
        ? [24, 14].map((r, i) => <div key={i} style={{position: 'absolute', [el.tail === 'right' ? 'right' : 'left']: 60 - i * 26,
            bottom: -30 - i * 34, width: r * 2, height: r * 2, borderRadius: r, background: '#fff'}} />)
        : <div style={{position: 'absolute', [el.tail === 'right' ? 'right' : 'left']: 70, bottom: -26, width: 0, height: 0,
            borderLeft: '22px solid transparent', borderRight: '22px solid transparent', borderTop: '30px solid #fff'}} />}
    </div>
  );
};

// Falling red bars, for crash moments.
const Crash = ({el}) => {
  const {s} = useLocal(el);
  const n = 7;
  return (
    <svg width="1920" height="1080" style={{position: 'absolute', inset: 0}}>
      {Array.from({length: n}, (_, i) => {
        const p = ease(interpolate(s, [i * 0.08, i * 0.08 + 0.6], [0, 1], clamp));
        const h0 = 420 - i * 45;
        const h = h0 * (0.25 + 0.75 * (1 - p * (i / n)));
        const x = (el.x ?? 560) + i * 120;
        return <rect key={i} x={x} y={(el.y ?? 900) - h} width="80" height={h} rx="8" fill={i > 2 ? C.red : '#ff8a8a'} opacity={0.9} />;
      })}
    </svg>
  );
};

// Atmosphere: rain streaks or floating dust motes, deterministic per frame.
const Fx = ({el}) => {
  const {s} = useLocal(el);
  const n = el.n || (el.kind === 'rain' ? 140 : 60);
  const rnd = (i, k) => { const x = Math.sin(i * 127.1 + k * 311.7) * 43758.5453; return x - Math.floor(x); };
  return (
    <svg width="1920" height="1080" style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
      {Array.from({length: n}, (_, i) => {
        if (el.kind === 'rain') {
          const sp = 1400 + rnd(i, 1) * 900;
          const y = ((rnd(i, 2) * 1300 + s * sp) % 1300) - 150;
          const x = rnd(i, 3) * 2100 - 90 + (y * 0.12);
          return <line key={i} x1={x} y1={y} x2={x - 6} y2={y + 46} stroke="rgba(200,220,255,0.35)" strokeWidth={1.6} />;
        }
        const x = (rnd(i, 4) * 1920 + Math.sin(s * 0.5 + i) * 30) % 1920;
        const y = (rnd(i, 5) * 1080 - s * (10 + rnd(i, 6) * 25) + 2160) % 1080;
        return <circle key={i} cx={x} cy={y} r={1.5 + rnd(i, 7) * 2.5} fill={`rgba(255,230,180,${0.15 + rnd(i, 8) * 0.35})`} />;
      })}
      {el.flicker && <rect width="1920" height="1080" fill="#000" opacity={Math.max(0, Math.sin(s * 17) * Math.sin(s * 5.3)) * 0.18} />}
    </svg>
  );
};

const KINDS = {fx: Fx, loop: MoneyLoop, shot: Shot, title: Title, caption: Caption, stat: Stat, headline: Headline, lower: Lower, chart: Chart,
  mark: Mark, panel: Panel, bg: Bg, slam: Slam, peep: Peep, dollar: Dollar, icon: Icon, phone: Phone, bubble: Bubble, crash: Crash};

const Element = ({el}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const Kind = KINDS[el.type];
  if (!Kind || frame < (el.t || 0) * fps) return null;
  if (el.until != null && frame > el.until * fps) return null;
  // graphics leaving on a cue fade out over their last 0.2 s instead of vanishing
  const out = el.until != null && el.type !== 'shot'
    ? interpolate(frame / fps, [el.until - 0.2, el.until], [1, 0], clamp) : 1;
  return out < 1 ? <AbsoluteFill style={{opacity: out}}><Kind el={el} /></AbsoluteFill> : <Kind el={el} />;
};

const EXIT = 12;
// The outgoing scene stays solid for EXIT frames while the next scene's first shot fades in on top.
const Scene = ({scene}) => {
  const base = (el) => el.type === 'shot' || el.type === 'panel' || el.type === 'bg';
  const shots = scene.elements.filter(base);
  const overlays = scene.elements.filter((el) => !base(el));
  return (
    <AbsoluteFill>
      {shots.map((el, i) => <Element key={`s${i}`} el={el} />)}
      {overlays.map((el, i) => <Element key={i} el={el} />)}
    </AbsoluteFill>
  );
};

// Subtle film grain over everything.
const Grain = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{opacity: 0.06, mixBlendMode: 'overlay', pointerEvents: 'none'}}>
      <svg width="1920" height="1080">
        <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={frame % 8} /></filter>
        <rect width="1920" height="1080" filter="url(#grain)" />
      </svg>
    </AbsoluteFill>
  );
};

// Channel identity: "Explained in 6 Minutes" clock, always ticking in the top-right corner.
const Countdown = ({from}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const left = Math.max(0, from - frame / fps);
  const m = Math.floor(left / 60);
  const sec = Math.floor(left % 60);
  const pulse = 0.55 + 0.45 * Math.abs(Math.sin((frame / fps) * Math.PI));
  return (
    <div style={{position: 'absolute', right: 48, top: 40, display: 'flex', alignItems: 'center', gap: 14,
      background: 'rgba(10,12,16,0.78)', padding: '10px 22px 10px 18px', borderRadius: 10, borderLeft: `6px solid ${C.yellow}`}}>
      <div style={{width: 14, height: 14, borderRadius: 7, background: C.red, opacity: pulse}} />
      <div style={{fontFamily: DISPLAY, fontSize: 54, lineHeight: 1, color: '#fff', letterSpacing: 2}}>
        {m}:{String(sec).padStart(2, '0')}
      </div>
      <div style={{fontFamily: SANS, fontWeight: 800, fontSize: 18, color: C.yellow, lineHeight: 1.1, textTransform: 'uppercase'}}>
        explained<br />in 6 min
      </div>
    </div>
  );
};

// News-package ticker: verified facts scrolling along the bottom edge.
const Ticker = ({items}) => {
  const frame = useCurrentFrame();
  const text = items.join('     •     ');
  const unit = measure(text + '     •     ', `700 30px ${SANS}`);
  const x = -((frame * 3.2) % Math.max(1, unit));
  return (
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 58, background: 'rgba(8,10,14,0.88)',
      borderTop: `3px solid ${C.yellow}`, overflow: 'hidden', display: 'flex', alignItems: 'center'}}>
      <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, zIndex: 2, background: C.yellow, padding: '0 22px',
        display: 'flex', alignItems: 'center', fontFamily: SANS, fontWeight: 900, fontSize: 26, color: C.ink}}>MARGIN MECHANICS</div>
      <div style={{position: 'absolute', left: 300 + x, whiteSpace: 'nowrap', fontFamily: SANS, fontWeight: 700, fontSize: 30,
        color: '#fff'}}>{text + '     •     ' + text + '     •     ' + text}</div>
    </div>
  );
};

export const Doc = ({scenes, width, countdown, ticker}) => {
  const {fps} = useVideoConfig();
  const k = (width || 1920) / 1920;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transform: `scale(${k})`, transformOrigin: '0 0'}}>
        {scenes.map((s, i) => (
          <Sequence key={i} from={Math.round(s.start * fps)}
            durationInFrames={Math.max(1, Math.round((s.end - s.start) * fps)) + (i < scenes.length - 1 ? EXIT : 0)}>
            <Scene scene={s} />
          </Sequence>
        ))}
        {ticker && ticker.length > 0 && <Ticker items={ticker} />}
        {countdown && <Countdown from={countdown} />}
      </div>
    </AbsoluteFill>
  );
};
export {Element, Countdown, Ticker};
