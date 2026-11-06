import {useMemo} from 'react';
import {AbsoluteFill, Easing, Loop, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Effigy} from '@opeepsfun/open-peeps';
import {getLength, getPointAtLength} from '@remotion/paths';
import rough from 'roughjs';
import {DRAW_SECONDS, HAND, INK, MARKER, ink} from './theme';

const gen = rough.generator();
const clamp01 = (v) => Math.min(1, Math.max(0, v));

// Element timing: el.t (seconds into the scene) and el.dur come from render.py.
const useProgress = (el) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const start = (el.t || 0) * fps;
  const dur = Math.max(1, (el.dur ?? DRAW_SECONDS[el.type] ?? 0.8) * fps);
  return {visible: frame >= start, p: clamp01((frame - start) / dur)};
};

const roughPaths = (drawable, extra = {}) =>
  gen.toPaths(drawable).map((p) => ({d: p.d, stroke: p.stroke, width: p.strokeWidth, ...extra}));

// Marker pen whose tip sits at (x, y).
const Pen = ({x, y, color}) => (
  <svg style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', pointerEvents: 'none'}} width="1" height="1">
    <g transform={`translate(${x},${y}) rotate(-52)`}>
      <polygon points="0,0 16,-9 16,9" fill={color} />
      <rect x="14" y="-12" width="18" height="24" rx="3" fill="#9A9AA2" />
      <rect x="30" y="-15" width="190" height="30" rx="8" fill="#2A2A30" />
      <rect x="36" y="-15" width="60" height="30" fill={color} opacity="0.9" />
      <rect x="214" y="-13" width="26" height="26" rx="6" fill={color} />
    </g>
  </svg>
);

// Draws a list of paths one after another; p in [0, 1] is overall progress.
// xf = {x, y, s} places paths drawn in their own unit space (icons).
const Strokes = ({paths, p, pen = true, xf = null}) => {
  const lengths = useMemo(() => paths.map((s) => Math.max(1, getLength(s.d))), [paths]);
  const total = lengths.reduce((a, b) => a + b, 0);
  let left = p * total;
  let tip = null;
  const items = paths.map((s, i) => {
    const len = lengths[i];
    const done = Math.min(len, Math.max(0, left));
    if (left > 0 && left < len) tip = {...getPointAtLength(s.d, done), color: s.stroke};
    left -= len;
    return (
      <path key={i} d={s.d} fill="none" stroke={s.stroke} strokeWidth={xf ? s.width / xf.s : s.width}
        strokeLinecap="round" strokeLinejoin="round" opacity={s.opacity ?? 1}
        strokeDasharray={len} strokeDashoffset={len - done} />
    );
  });
  if (tip && xf) tip = {...tip, x: xf.x + tip.x * xf.s, y: xf.y + tip.y * xf.s};
  return (
    <>
      <svg style={{position: 'absolute', inset: 0, overflow: 'visible'}} width="100%" height="100%">
        {xf ? <g transform={`translate(${xf.x} ${xf.y}) scale(${xf.s})`}>{items}</g> : items}
      </svg>
      {pen && tip && p < 1 && <Pen x={tip.x} y={tip.y} color={tip.color} />}
    </>
  );
};

// Real text width from the browser (fonts are loaded before frames are captured).
const measure = (text, font) => {
  measure.ctx = measure.ctx || document.createElement('canvas').getContext('2d');
  measure.ctx.font = font;
  return measure.ctx.measureText(text).width;
};

const Write = ({el, p}) => {
  const lines = String(el.text).split('\n');
  const marker = el.font === 'marker';
  const family = marker ? MARKER : HAND;
  const weight = marker ? 400 : 700;
  const W = el.w || 1700;
  // Shrink to fit the box instead of running off screen.
  let size = el.size || 72;
  const widest = Math.max(...lines.map((l) => measure(l, `${weight} ${size}px ${family}`)));
  if (widest > W) size = Math.floor((size * W) / widest);
  const lineH = size * 1.15;
  const align = el.align || 'center';
  const color = ink(el.color);
  const n = lines.length;
  const top = el.y - (n * lineH) / 2;
  let pen = null;
  const rows = lines.map((line, i) => {
    const lp = clamp01(p * n - i);
    const estW = Math.min(W, measure(line, `${weight} ${size}px ${family}`));
    const x0 = align === 'center' ? el.x - estW / 2 : el.x;
    if (lp > 0 && lp < 1) pen = {x: x0 + lp * estW, y: top + (i + 0.8) * lineH};
    return (
      <div key={i} style={{height: lineH, lineHeight: `${lineH}px`, whiteSpace: 'nowrap'}}>
        <span style={{display: 'inline-block', clipPath: `inset(-30% ${(1 - lp) * 100}% -30% 0)`}}>{line}</span>
      </div>
    );
  });
  return (
    <>
      <div style={{position: 'absolute', left: align === 'center' ? el.x - W / 2 : el.x, top, width: W,
        textAlign: align, fontFamily: family, fontWeight: weight,
        fontSize: size, color, transform: el.rotate ? `rotate(${el.rotate}deg)` : undefined}}>
        {rows}
      </div>
      {pen && <Pen x={pen.x} y={pen.y} color={color} />}
    </>
  );
};

const Count = ({el, p}) => {
  // Small whole numbers (e.g. 1 trillion) pop in; counting 0 -> 1 just looks odd.
  const counts = !((el.value || 0) < 10 && !el.decimals);
  const v = counts ? (el.value || 0) * Easing.out(Easing.cubic)(p) : (el.value || 0);
  const scale = interpolate(p, [0, 0.15], [0.6, 1], {extrapolateRight: 'clamp'});
  const fmt = (n) => `${el.prefix || ''}${n.toLocaleString('en-US', {minimumFractionDigits: el.decimals || 0, maximumFractionDigits: el.decimals || 0})}${el.suffix || ''}`;
  const text = fmt(v);
  // Size to the final value so the number never wraps or changes size while counting.
  let size = el.size || 160;
  const full = measure(fmt(el.value || 0), `400 ${size}px ${MARKER}`);
  if (full > (el.w || 1750)) size = Math.floor((size * (el.w || 1750)) / full);
  return (
    <div style={{position: 'absolute', left: el.x - 900, top: el.y - size * 0.6, width: 1800, whiteSpace: 'nowrap',
      textAlign: 'center', fontFamily: MARKER, fontSize: size, color: ink(el.color),
      transform: `scale(${scale})`}}>
      {text}
    </div>
  );
};

const Icon = ({el, p}) => {
  const size = el.size || 200;
  const paths = useMemo(() => (el.paths || []).map((d) => ({
    d, stroke: ink(el.color), width: el.stroke || Math.max(4, size / 30),
  })), [el]);
  return <Strokes paths={paths} p={p} xf={{x: el.x - size / 2, y: el.y - size / 2, s: size / 24}} />;
};

const Bars = ({el, p}) => {
  const data = el.data || [];
  const max = Math.max(...data.map((d) => d.value), 1);
  const slot = el.w / data.length;
  const bw = slot * 0.55;
  const geo = data.map((d, i) => {
    const h = (d.value / max) * el.h;
    return {x: el.x + slot * i + (slot - bw) / 2, h, d};
  });
  const groups = useMemo(() => {
    const g = [roughPaths(gen.line(el.x - 20, el.y, el.x + el.w + 20, el.y, {seed: 3, roughness: 1, strokeWidth: 5, stroke: INK.black}))];
    geo.forEach((b, i) => g.push(roughPaths(gen.rectangle(b.x, el.y - b.h, bw, b.h, {
      seed: 11 + i, roughness: 1.4, strokeWidth: 5, stroke: ink(b.d.color),
      fill: ink(b.d.color), fillStyle: 'hachure', hachureGap: 14, fillWeight: 3,
    }))));
    return g;
  }, [el]);
  const all = groups.flat();
  // Each bar's label appears once that bar has been drawn.
  const n = groups.length;
  return (
    <>
      <Strokes paths={all} p={p} />
      {geo.map((b, i) => {
        const shown = p >= (i + 2) / n - 0.02;
        return shown ? (
          <div key={i}>
            <div style={{position: 'absolute', left: b.x - 100, width: bw + 200, top: el.y + 14, textAlign: 'center',
              fontFamily: HAND, fontWeight: 700, fontSize: el.labelSize || 52, color: INK.black}}>{b.d.label}</div>
            <div style={{position: 'absolute', left: b.x - 100, width: bw + 200, top: el.y - b.h - 92, textAlign: 'center',
              fontFamily: MARKER, fontSize: el.valueSize || 64, color: ink(b.d.color)}}>{b.d.valueLabel ?? b.d.value}</div>
          </div>
        ) : null;
      })}
    </>
  );
};

const Arrow = ({el, p}) => {
  const paths = useMemo(() => {
    const [x1, y1] = el.from;
    const [x2, y2] = el.to;
    const c = ink(el.color);
    const a = Math.atan2(y2 - y1, x2 - x1);
    const head = (s) => [x2 - 34 * Math.cos(a + s), y2 - 34 * Math.sin(a + s)];
    const bend = el.bend || 0;
    const mx = (x1 + x2) / 2 - bend * Math.sin(a);
    const my = (y1 + y2) / 2 + bend * Math.cos(a);
    const o = {seed: 5, roughness: 1, strokeWidth: 6, stroke: c};
    return [
      ...roughPaths(bend ? gen.curve([[x1, y1], [mx, my], [x2, y2]], o) : gen.line(x1, y1, x2, y2, o)),
      ...roughPaths(gen.linearPath([head(0.45), [x2, y2], head(-0.45)], o)),
    ];
  }, [el]);
  return <Strokes paths={paths} p={p} />;
};

const Shape = ({el, p}) => {
  const paths = useMemo(() => {
    const c = ink(el.color || (el.type === 'circle' ? 'red' : 'black'));
    const o = {seed: 9, roughness: el.type === 'circle' ? 1.6 : 1.1, strokeWidth: el.stroke || 6, stroke: c};
    if (el.type === 'circle') return roughPaths(gen.ellipse(el.x, el.y, el.w, el.h, o));
    if (el.type === 'box') return roughPaths(gen.rectangle(el.x, el.y, el.w, el.h, o));
    if (el.type === 'underline') return roughPaths(gen.curve([[el.x, el.y], [el.x + el.w / 2, el.y + 7], [el.x + el.w, el.y - 3]], o));
    if (el.type === 'line') return roughPaths(gen.line(el.from[0], el.from[1], el.to[0], el.to[1], o));
    if (el.type === 'highlight') {
      return [{d: `M ${el.x} ${el.y} L ${el.x + el.w} ${el.y}`, stroke: ink(el.color || 'yellow'), width: el.h || 70, opacity: 0.55}];
    }
    return [];
  }, [el]);
  return <Strokes paths={paths} p={p} pen={el.type !== 'highlight'} />;
};

// Real footage: full-screen (el.full) or a taped-on photo card that slides in.
// Wrapped in a Sequence by Element so playback starts when the clip appears.
const Clip = ({el}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = clamp01(frame / (0.5 * fps));
  const ease = Easing.out(Easing.cubic)(p);
  const video = (
    <Loop durationInFrames={Math.max(1, Math.round((el.clipSeconds || 10) * fps))}>
      <OffthreadVideo src={staticFile(el.src)} muted
        style={{width: '100%', height: '100%', objectFit: 'cover'}} />
    </Loop>
  );
  if (el.full) {
    const zoom = 1.04 + 0.06 * (frame / (fps * 20));
    return (
      <AbsoluteFill style={{opacity: ease, overflow: 'hidden'}}>
        <AbsoluteFill style={{transform: `scale(${zoom})`}}>{video}</AbsoluteFill>
        <AbsoluteFill style={{background: `rgba(10,10,14,${el.dim ?? 0.35})`}} />
      </AbsoluteFill>
    );
  }
  const w = el.w || 900;
  const h = el.h || 506;
  const tape = (left, rot) => (
    <div style={{position: 'absolute', top: -22, left, width: 150, height: 44, background: 'rgba(255,216,77,0.75)',
      transform: `rotate(${rot}deg)`}} />
  );
  return (
    <div style={{position: 'absolute', left: el.x - w / 2, top: el.y - h / 2, width: w, height: h,
      transform: `translateY(${(1 - ease) * 120}px) rotate(${el.rotate ?? -1.5}deg)`, opacity: ease,
      background: '#fff', padding: 14, boxShadow: '0 18px 40px rgba(0,0,0,0.25)'}}>
      <div style={{position: 'relative', width: '100%', height: '100%', overflow: 'hidden'}}>{video}</div>
      {tape(w * 0.1, -6)}
      {tape(w * 0.72, 5)}
    </div>
  );
};

// Hand-drawn character (Open Peeps, CC0). Pops in, breathes, and swaps face/pose on cue words.
const PEEP_RATIO = 940.27 / 1130.59;
const Peep = ({el}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const since = t - (el.t || 0);
  let face = el.face || 'Calm';
  let body = el.body || 'Explaining';
  let lastReact = -10;
  for (const r of el.reacts || []) {
    if (t >= r.t) {
      face = r.face || face;
      body = r.body || body;
      lastReact = r.t;
    }
  }
  const enter = spring({frame: Math.round(since * fps), fps, config: {damping: 11, stiffness: 140}});
  // A small "jolt" each time the expression changes, so the reaction reads.
  const jolt = interpolate(t - lastReact, [0, 0.12, 0.35], [1, 1.08, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const bob = Math.sin(since * 2.1) * 5;
  const tilt = Math.sin(since * 1.2) * 1.4;
  const h = el.size || 520;
  const w = h * PEEP_RATIO;
  return (
    <div style={{position: 'absolute', left: el.x - w / 2, top: el.y - h / 2 + (1 - enter) * 160 + bob, width: w, height: h,
      opacity: Math.min(1, enter * 2), transformOrigin: '50% 100%',
      transform: `scaleX(${el.flip ? -1 : 1}) rotate(${tilt}deg) scale(${jolt})`}}>
      <Effigy body={{type: body, options: el.bodyOptions || {}}} head={{type: el.head || 'ShortOne', options: el.headOptions || {}}}
        face={{type: face, options: {}}} style={{width: '100%', height: '100%', overflow: 'visible'}} />
    </div>
  );
};

const KINDS = {write: Write, count: Count, icon: Icon, bars: Bars, arrow: Arrow, peep: Peep,
  circle: Shape, box: Shape, underline: Shape, line: Shape, highlight: Shape};

export const Element = ({el}) => {
  const {fps} = useVideoConfig();
  const {visible, p} = useProgress(el);
  if (el.type === 'clip') {
    return el.src ? (
      <Sequence from={Math.round((el.t || 0) * fps)} layout="none"><Clip el={el} /></Sequence>
    ) : null;
  }
  const Kind = KINDS[el.type];
  if (!visible || !Kind) return null;
  return <Kind el={el} p={p} />;
};
