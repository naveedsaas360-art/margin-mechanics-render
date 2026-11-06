import {AbsoluteFill, Audio, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Element} from './elements';
import {HAND, INK, PAPER} from './theme';

const Paper = () => (
  <AbsoluteFill style={{background: PAPER}}>
    <svg width="100%" height="100%" style={{position: 'absolute', opacity: 0.35}}>
      <filter id="grain">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" />
        <feColorMatrix values="0 0 0 0 0.45  0 0 0 0 0.42  0 0 0 0 0.38  0 0 0 0.12 0" />
      </filter>
      <rect width="100%" height="100%" filter="url(#grain)" />
    </svg>
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, transparent 60%, rgba(60,50,30,0.10) 100%)'}} />
  </AbsoluteFill>
);

const EXIT = 14; // frames a board keeps sliding out after its scene ends

// One board per scene: it slides in, then drifts slightly closer while drawing.
const Scene = ({scene, index}) => {
  const frame = useCurrentFrame();
  const {fps, width, durationInFrames} = useVideoConfig();
  const enter = index === 0 ? 1 : spring({frame, fps, durationInFrames: 14, config: {damping: 200}});
  const sceneFrames = Math.round((scene.end - scene.start) * fps);
  const zoom = interpolate(frame, [0, Math.max(1, sceneFrames)], [1, 1.05], {extrapolateRight: 'clamp'});
  // Push transition: the board slides out left while the next one slides in.
  const exit = interpolate(frame, [sceneFrames, sceneFrames + EXIT], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  // Slow camera drift so no board is ever still.
  const drift = Math.sin((frame / fps) * 0.35 + index) * 14;
  const clips = scene.elements.filter((el) => el.type === 'clip');
  const drawings = scene.elements.filter((el) => el.type !== 'clip');
  return (
    <AbsoluteFill style={{transform: `translateX(${((1 - enter) - exit) * width + drift}px) scale(${zoom})`}}>
      {clips.map((el, i) => <Element key={`c${i}`} el={el} />)}
      <AbsoluteFill style={{filter: 'url(#boil)'}}>
        {drawings.map((el, i) => <Element key={i} el={el} />)}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// Hand-drawn "line boil": the wobble pattern changes every 4 frames.
const Boil = () => {
  const frame = useCurrentFrame();
  return (
    <svg width="0" height="0" style={{position: 'absolute'}}>
      <filter id="boil" x="-5%" y="-5%" width="110%" height="110%">
        <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed={Math.floor(frame / 4) % 6} />
        <feDisplacementMap in="SourceGraphic" scale="3.5" />
      </filter>
    </svg>
  );
};

// Word-by-word captions for vertical Shorts.
const Captions = ({captions}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const i = captions.findIndex((c) => t >= c.s && t < c.e);
  if (i < 0) return null;
  const group = captions.slice(Math.floor(i / 3) * 3, Math.floor(i / 3) * 3 + 3);
  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 260}}>
      <div style={{fontFamily: HAND, fontWeight: 700, fontSize: 96, color: INK.black, textAlign: 'center',
        background: 'rgba(255,216,77,0.85)', padding: '6px 28px', borderRadius: 18}}>
        {group.map((c, j) => (
          <span key={j} style={{color: c === captions[i] ? INK.red : INK.black}}>{c.w} </span>
        ))}
      </div>
    </AbsoluteFill>
  );
};

export const Board = ({scenes, audio, sfx, captions}) => {
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill>
      <Boil />
      <Paper />
      {scenes.map((s, i) => (
        <Sequence key={i} from={Math.round(s.start * fps)}
          durationInFrames={Math.max(1, Math.round((s.end - s.start) * fps)) + (i < scenes.length - 1 ? EXIT : 0)}>
          <Scene scene={s} index={i} />
        </Sequence>
      ))}
      {captions && captions.length > 0 && <Captions captions={captions} />}
      {audio && <Audio src={staticFile(audio)} />}
      {sfx && <Audio src={staticFile(sfx)} volume={0.5} />}
    </AbsoluteFill>
  );
};
