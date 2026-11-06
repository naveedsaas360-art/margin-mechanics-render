// "Story3D": 3D-illustration storytelling. Each scene is a small lit 3D world (three.js) with a moving
// camera, plus crisp HTML overlays (titles, stats, bubbles) shared with the Doc style.
import {useMemo} from 'react';
import {AbsoluteFill, Easing, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
import {Element, Countdown, Ticker} from './Doc';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'};
const ease = Easing.inOut(Easing.cubic);
const lerp = (a, b, p) => a + (b - a) * p;
const lerp3 = (a, b, p) => [lerp(a[0], b[0], p), lerp(a[1], b[1], p), lerp(a[2], b[2], p)];
const useT = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return frame / fps; // scene-relative seconds
};

// ---------- textures drawn once on a canvas ----------
const canvasTex = (w, h, draw) => {
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  return t;
};
const billTex = () => canvasTex(512, 236, (g, w, h) => {
  g.fillStyle = '#3fbf74'; g.fillRect(0, 0, w, h);
  g.strokeStyle = '#1d6b40'; g.lineWidth = 14; g.strokeRect(10, 10, w - 20, h - 20);
  g.beginPath(); g.arc(w / 2, h / 2, 70, 0, Math.PI * 2); g.fillStyle = '#5fd690'; g.fill(); g.stroke();
  g.fillStyle = '#1d6b40'; g.font = 'bold 110px Arial'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText('$', w / 2, h / 2 + 6);
  for (const ex of [110, 402]) {
    g.beginPath(); g.arc(ex, h / 2 - 12, 30, 0, Math.PI * 2); g.fillStyle = '#fff'; g.fill();
    g.beginPath(); g.arc(ex + 6, h / 2 - 8, 14, 0, Math.PI * 2); g.fillStyle = '#111'; g.fill();
  }
});
const windowsTex = (lit) => canvasTex(256, 512, (g, w, h) => {
  g.fillStyle = '#2b3a55'; g.fillRect(0, 0, w, h);
  for (let y = 20; y < h - 20; y += 34) for (let x = 18; x < w - 18; x += 40) {
    g.fillStyle = (x * 7 + y * 13) % 5 < 3 ? lit : '#41557a';
    g.fillRect(x, y, 26, 20);
  }
});

// ---------- camera ----------
const Rig = ({from, to, look, dur}) => {
  const {camera} = useThree();
  const t = useT();
  const p = ease(Math.min(1, Math.max(0, t / Math.max(0.1, dur))));
  const [x, y, z] = lerp3(from, to || from, p);
  camera.position.set(x, y, z);
  camera.lookAt(...(look || [0, 1, 0]));
  return null;
};

const World = ({bg = '#f3e6d3', ground = '#e8d5bc', fog = true}) => (
  <>
    <color attach="background" args={[bg]} />
    {fog && <fog attach="fog" args={[bg, 18, 42]} />}
    <hemisphereLight args={['#ffffff', '#b9a48a', 1.1]} />
    <directionalLight position={[6, 12, 8]} intensity={1.6} />
    <directionalLight position={[-8, 6, -4]} intensity={0.45} color="#9fb7ff" />
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
      <circleGeometry args={[40, 64]} />
      <meshStandardMaterial color={ground} roughness={0.95} />
    </mesh>
  </>
);
const Shadow = ({r = 0.6, pos = [0, 0.01, 0], o = 0.18}) => (
  <mesh rotation={[-Math.PI / 2, 0, 0]} position={pos}>
    <circleGeometry args={[r, 32]} />
    <meshBasicMaterial color="#000" transparent opacity={o} depthWrite={false} />
  </mesh>
);

// ---------- characters & props ----------
const SKIN = '#c98a5a';
const Maya = ({pos = [0, 0, 0], rot = 0, face = 'calm', hold = null, t0 = 0, reacts = []}) => {
  const t = useT();
  let f = face;
  for (const r of reacts) if (t >= r.t) f = r.face || f;
  const bob = Math.sin((t - t0) * 2.2) * 0.03;
  const blink = (t % 3.4) < 0.12 ? 0.1 : 1;
  const wide = f === 'fear' || f === 'surprised' ? 1.45 : 1;
  const turn = Math.sin(t * 0.8) * 0.12;
  return (
    <group position={pos} rotation={[0, rot, 0]}>
      <Shadow r={0.55} />
      {[-0.13, 0.13].map((x) => (
        <mesh key={x} position={[x, 0.36, 0]}><cylinderGeometry args={[0.09, 0.1, 0.72, 16]} /><meshStandardMaterial color="#2f3e5c" roughness={0.7} /></mesh>
      ))}
      <group position={[0, bob, 0]}>
        <mesh position={[0, 1.08, 0]}><capsuleGeometry args={[0.32, 0.42, 8, 24]} /><meshStandardMaterial color="#f2b33d" roughness={0.6} /></mesh>
        {[-1, 1].map((sx) => (
          <mesh key={sx} position={[sx * 0.4, 1.05, hold ? 0.18 : 0]} rotation={[hold ? -1.1 : 0, 0, sx * 0.25]}>
            <capsuleGeometry args={[0.085, 0.42, 6, 16]} /><meshStandardMaterial color="#f2b33d" roughness={0.6} />
          </mesh>
        ))}
        {hold === 'mug' && <mesh position={[0.32, 1.12, 0.42]}><cylinderGeometry args={[0.1, 0.09, 0.2, 20]} /><meshStandardMaterial color="#d6453d" /></mesh>}
        {hold === 'phone' && <mesh position={[0, 1.15, 0.45]} rotation={[-0.5, 0, 0]}><boxGeometry args={[0.32, 0.55, 0.04]} /><meshStandardMaterial color="#111" /></mesh>}
        <group position={[0, 1.66, 0]} rotation={[0, turn, f === 'suspicious' ? 0.12 : 0]}>
          <mesh><sphereGeometry args={[0.3, 32, 32]} /><meshStandardMaterial color={SKIN} roughness={0.65} /></mesh>
          <mesh position={[0, 0.06, -0.05]} scale={[1.08, 1.02, 1.05]}><sphereGeometry args={[0.31, 32, 32, 0, Math.PI * 2, 0, Math.PI / 1.9]} /><meshStandardMaterial color="#2a1d18" roughness={0.8} /></mesh>
          <mesh position={[0, -0.2, -0.17]}><boxGeometry args={[0.56, 0.5, 0.16]} /><meshStandardMaterial color="#2a1d18" roughness={0.8} /></mesh>
          {[-0.11, 0.11].map((x) => (
            <group key={x} position={[x, 0.02, 0.27]} scale={[wide, wide * blink, wide]}>
              {wide > 1 && <mesh position={[0, 0, -0.01]}><sphereGeometry args={[0.055, 16, 16]} /><meshStandardMaterial color="#fff" /></mesh>}
              <mesh position={[0, 0, 0.02]}><sphereGeometry args={[0.035, 16, 16]} /><meshStandardMaterial color="#111" /></mesh>
            </group>
          ))}
          {[-0.11, 0.11].map((x) => (
            <mesh key={`b${x}`} position={[x, 0.13 + (f === 'suspicious' && x > 0 ? 0.04 : 0) + (wide > 1 ? 0.03 : 0), 0.27]}
              rotation={[0, 0, f === 'suspicious' ? (x > 0 ? -0.35 : 0.1) : (wide > 1 ? x * 2 : 0)]}>
              <boxGeometry args={[0.1, 0.022, 0.02]} /><meshStandardMaterial color="#2a1d18" />
            </mesh>
          ))}
          {wide > 1
            ? <mesh position={[0, -0.12, 0.27]}><sphereGeometry args={[0.045, 16, 16]} /><meshStandardMaterial color="#5a1f1f" /></mesh>
            : <mesh position={[0, -0.1, 0.27]} rotation={[0, 0, Math.PI]}><torusGeometry args={[0.06, 0.012, 8, 24, Math.PI]} /><meshStandardMaterial color="#5a1f1f" /></mesh>}
        </group>
      </group>
    </group>
  );
};

// Flying 3D dollar bill(s). path: from -> to between times [a, b]; copies swarm out at swarmAt.
const Bills = ({from, to, a = 0, b = 1.2, hop = 1.2, scale = 1, copies = 1, swarmAt = null}) => {
  const t = useT();
  const tex = useMemo(billTex, []);
  const p = ease(Math.min(1, Math.max(0, (t - a) / Math.max(0.1, b - a))));
  const base = lerp3(from, to || from, p);
  base[1] += Math.sin(p * Math.PI) * hop + Math.sin(t * 3) * 0.05;
  const k = swarmAt != null ? Math.min(1, Math.max(0, (t - swarmAt) / 1.2)) : 0;
  return (
    <>
      {Array.from({length: copies}, (_, i) => {
        const ang = i * 2.4;
        const r = i === 0 ? 0 : k * (1.2 + (i % 3) * 0.6);
        const pos = [base[0] + Math.cos(ang) * r, base[1] + (i ? Math.sin(t * 2 + i) * 0.3 + k * (i % 4) * 0.3 : 0), base[2] + Math.sin(ang) * r];
        if (i && k <= 0) return null;
        return (
          <mesh key={i} position={pos} rotation={[0.3 + Math.sin(t * 2 + i) * 0.2, t * 1.5 + i, Math.sin(t * 3 + i) * 0.25]}
            scale={scale * (i ? 0.7 : 1)}>
            <boxGeometry args={[1.1, 0.5, 0.03]} />
            <meshStandardMaterial map={tex} roughness={0.5} />
          </mesh>
        );
      })}
    </>
  );
};

const Coin = ({pos, t0 = 0, fall = 2.5}) => {
  const t = useT();
  const p = Math.min(1, Math.max(0, (t - t0) / 0.8));
  const y = lerp(pos[1] + fall, pos[1], Easing.in(Easing.quad)(p));
  if (t < t0) return null;
  return (
    <mesh position={[pos[0], y, pos[2]]} rotation={[Math.PI / 2, t * 4, 0]}>
      <cylinderGeometry args={[0.22, 0.22, 0.05, 32]} /><meshStandardMaterial color="#f5c542" metalness={0.6} roughness={0.3} />
    </mesh>
  );
};

const Building = ({pos, h = 4, w = 1.5, t0 = 0, color = '#ffd36b'}) => {
  const t = useT();
  const {fps} = useVideoConfig();
  const tex = useMemo(() => windowsTex(color), [color]);
  const sp = t < t0 ? 0 : spring({frame: Math.round((t - t0) * fps), fps, config: {damping: 13, stiffness: 90}});
  const hh = Math.max(0.01, h * sp);
  return (
    <group position={pos}>
      <Shadow r={w * 0.9} />
      <mesh position={[0, hh / 2, 0]} scale={[1, 1, 1]}>
        <boxGeometry args={[w, hh, w]} />
        <meshStandardMaterial map={tex} roughness={0.6} />
      </mesh>
      {sp > 0.05 && <mesh position={[0, hh + 0.08, 0]}><boxGeometry args={[w * 1.05, 0.16, w * 1.05]} /><meshStandardMaterial color="#e9ecf2" /></mesh>}
    </group>
  );
};

const Rack = ({pos}) => {
  const t = useT();
  return (
    <group position={pos}>
      <mesh position={[0, 1.1, 0]}><boxGeometry args={[0.9, 2.2, 0.9]} /><meshStandardMaterial color="#2a2f3a" roughness={0.5} metalness={0.2} /></mesh>
      {Array.from({length: 8}, (_, i) => (
        <mesh key={i} position={[0, 0.3 + i * 0.24, 0.46]}>
          <boxGeometry args={[0.6, 0.05, 0.02]} />
          <meshStandardMaterial color="#2bd67b" emissive="#2bd67b" emissiveIntensity={0.6 + 0.6 * Math.abs(Math.sin(t * 5 + i * 1.7 + pos[0]))} />
        </mesh>
      ))}
    </group>
  );
};

const Chip = ({pos = [0, 0, 0], s = 1, glow = 1}) => {
  const t = useT();
  const pulse = 0.6 + 0.4 * Math.sin(t * 3);
  return (
    <group position={pos} scale={s}>
      <mesh position={[0, 0.1, 0]}><boxGeometry args={[3.2, 0.2, 3.2]} /><meshStandardMaterial color="#1e6b45" roughness={0.6} /></mesh>
      <mesh position={[0, 0.35, 0]}><boxGeometry args={[1.8, 0.3, 1.8]} /><meshStandardMaterial color="#15171c" roughness={0.35} metalness={0.4} /></mesh>
      <mesh position={[0, 0.51, 0]}><boxGeometry args={[1.0, 0.03, 1.0]} />
        <meshStandardMaterial color="#76b900" emissive="#76b900" emissiveIntensity={glow * pulse * 1.5} /></mesh>
      {Array.from({length: 24}, (_, i) => {
        const side = Math.floor(i / 6);
        const k = (i % 6) / 5 - 0.5;
        const x = side < 2 ? k * 1.5 : (side === 2 ? -1 : 1);
        const z = side < 2 ? (side === 0 ? -1 : 1) : k * 1.5;
        return <mesh key={i} position={[x, 0.25, z]}><boxGeometry args={[0.12, 0.06, 0.12]} /><meshStandardMaterial color="#c9a34a" metalness={0.8} roughness={0.3} /></mesh>;
      })}
    </group>
  );
};

// Phone whose screen chart crashes red; the screen texture is redrawn each frame.
const Phone = ({pos, t0 = 0, crash = 2.5}) => {
  const t = useT();
  const p = Math.min(1, Math.max(0, (t - t0 - 0.3) / crash));
  const tex = useMemo(() => {
    const c = document.createElement('canvas');
    c.width = 360; c.height = 720;
    const tx = new THREE.CanvasTexture(c);
    tx.colorSpace = THREE.SRGBColorSpace;
    return tx;
  }, []);
  const g = tex.image.getContext('2d');
  const pts = [0.3, 0.26, 0.32, 0.22, 0.27, 0.2, 0.35, 0.5, 0.62, 0.8, 0.92];
  const red = p > 0.55;
  g.fillStyle = '#0d0f14'; g.fillRect(0, 0, 360, 720);
  g.fillStyle = '#9aa3b2'; g.font = 'bold 34px Arial'; g.fillText('CHIP STOCKS', 30, 80);
  g.fillStyle = red ? '#ff4d4d' : '#2bd67b'; g.font = 'bold 72px Arial';
  g.fillText(red ? `-${(28.6 * Math.min(1, (p - 0.55) / 0.45)).toFixed(1)}%` : '+0.4%', 30, 170);
  g.strokeStyle = red ? '#ff4d4d' : '#2bd67b'; g.lineWidth = 9; g.lineJoin = 'round'; g.beginPath();
  pts.forEach((y, i) => { const x = i / (pts.length - 1); if (x <= p) { const X = 30 + x * 300; const Y = 260 + y * 400; i ? g.lineTo(X, Y) : g.moveTo(X, Y); } });
  g.stroke();
  tex.needsUpdate = true;
  return (
    <group position={pos} rotation={[-0.15, -0.35, 0.05]}>
      <mesh><boxGeometry args={[1.0, 1.95, 0.1]} /><meshStandardMaterial color="#1b1d22" roughness={0.3} metalness={0.4} /></mesh>
      <mesh position={[0, 0, 0.052]}><planeGeometry args={[0.9, 1.8]} /><meshBasicMaterial map={tex} toneMapped={false} /></mesh>
    </group>
  );
};

const Bars = ({t0 = 0}) => {
  const t = useT();
  return (
    <group position={[-2.2, 0, 0]}>
      {Array.from({length: 7}, (_, i) => {
        const p = ease(Math.min(1, Math.max(0, (t - t0 - i * 0.12) / 0.9)));
        const h0 = 4 - i * 0.35;
        const h = Math.max(0.1, h0 * (1 - p * (0.25 + i * 0.1)));
        return (
          <mesh key={i} position={[i * 0.75, h / 2, 0]}>
            <boxGeometry args={[0.55, h, 0.55]} /><meshStandardMaterial color={i > 2 ? '#e8463f' : '#f08a7e'} roughness={0.5} />
          </mesh>
        );
      })}
    </group>
  );
};

const Piggy = ({pos, t0 = 0}) => {
  const t = useT();
  const wob = Math.sin(t * 3) * 0.04;
  return (
    <group position={pos} rotation={[0, -0.6 + wob, 0]}>
      <Shadow r={0.9} />
      <mesh position={[0, 0.85, 0]} scale={[1.25, 1, 1]}><sphereGeometry args={[0.7, 32, 32]} /><meshStandardMaterial color="#f4a3b5" roughness={0.5} /></mesh>
      <mesh position={[0.9, 0.85, 0]} rotation={[0, 0, Math.PI / 2]}><cylinderGeometry args={[0.2, 0.22, 0.2, 24]} /><meshStandardMaterial color="#ef8ea4" /></mesh>
      {[-0.25, 0.25].map((z) => <mesh key={z} position={[0.5, 1.45, z]}><coneGeometry args={[0.13, 0.25, 16]} /><meshStandardMaterial color="#ef8ea4" /></mesh>)}
      {[[-0.4, -0.35], [-0.4, 0.35], [0.4, -0.35], [0.4, 0.35]].map(([x, z]) => (
        <mesh key={`${x}${z}`} position={[x, 0.2, z]}><cylinderGeometry args={[0.1, 0.1, 0.4, 12]} /><meshStandardMaterial color="#ef8ea4" /></mesh>))}
      <mesh position={[0, 1.55, 0]}><boxGeometry args={[0.4, 0.05, 0.08]} /><meshStandardMaterial color="#5a2b35" /></mesh>
      {[0, 0.5, 1.0, 1.5].map((d) => <Coin key={d} pos={[0, 1.6, 0]} t0={t0 + d} />)}
    </group>
  );
};

// ---------- the sets: one per story beat ----------
// r = cue times (scene seconds) resolved from reveal_at; dur = scene length.
const SETS = {
  room: ({r, dur}) => (<>
    <World bg="#f6dcc3" ground="#e9c9a8" />
    <mesh position={[1.1, 0.42, -0.4]}><boxGeometry args={[1.8, 0.08, 0.9]} /><meshStandardMaterial color="#9a6a48" roughness={0.6} /></mesh>
    {[[0.35, -0.75], [1.85, -0.75], [0.35, -0.05], [1.85, -0.05]].map(([x, z]) => (
      <mesh key={`${x}${z}`} position={[x, 0.2, z]}><boxGeometry args={[0.07, 0.4, 0.07]} /><meshStandardMaterial color="#7a5038" /></mesh>))}
    <mesh position={[1.6, 0.75, -0.55]}><cylinderGeometry args={[0.03, 0.03, 0.6, 12]} /><meshStandardMaterial color="#333" /></mesh>
    <mesh position={[1.6, 1.08, -0.5]} rotation={[0.5, 0, 0]}><coneGeometry args={[0.2, 0.25, 24, 1, true]} /><meshStandardMaterial color="#f2c14e" side={THREE.DoubleSide} emissive="#f2c14e" emissiveIntensity={0.25} /></mesh>
    <mesh position={[0.7, 0.58, -0.6]}><cylinderGeometry args={[0.12, 0.1, 0.25, 16]} /><meshStandardMaterial color="#c86b4a" /></mesh>
    {[0, 1, 2, 3, 4].map((i) => <mesh key={i} position={[0.7 + Math.sin(i * 1.3) * 0.12, 0.82 + (i % 2) * 0.08, -0.6 + Math.cos(i * 1.3) * 0.12]}>
      <sphereGeometry args={[0.13, 16, 16]} /><meshStandardMaterial color="#4f9d5b" /></mesh>)}
    <mesh position={[0.4, 2.2, -1.4]}><boxGeometry args={[1.6, 1.1, 0.05]} /><meshStandardMaterial color="#bfe3ff" emissive="#bfe3ff" emissiveIntensity={0.35} /></mesh>
    <mesh position={[0.4, 2.2, -1.43]}><boxGeometry args={[1.75, 1.25, 0.04]} /><meshStandardMaterial color="#ffffff" /></mesh>
    <mesh position={[0.4, 1.5, -1.5]}><boxGeometry args={[8, 3, 0.1]} /><meshStandardMaterial color="#f0cfae" roughness={0.9} /></mesh>
    <Maya pos={[-0.4, 0, 0.3]} rot={0.25} face="calm" hold="mug" />
    <Rig from={[2.6, 2.1, 4.2]} to={[1.1, 1.85, 3.0]} look={[-0.1, 1.35, 0]} dur={dur} />
  </>),
  piggy: ({r, dur}) => (<>
    <World bg="#e6dcf5" ground="#d3c4ee" />
    <Maya pos={[-1.8, 0, 0.6]} rot={0.5} reacts={[{t: r[0] ?? 99, face: 'calm'}]} />
    <Piggy pos={[1.4, 0, 0]} t0={r[0] ?? 1} />
    <Rig from={[0, 2.6, 7]} to={[0.6, 2.2, 5.2]} look={[0, 1.1, 0]} dur={dur} />
  </>),
  phone: ({r, dur}) => (<>
    <World bg="#d9e2ef" ground="#c2cfe2" />
    <Maya pos={[-1.2, 0, 0.3]} rot={0.35} hold="phone" reacts={[{t: r[1] ?? 99, face: 'fear'}]} />
    <group scale={0.55}><Phone pos={[0.4, 2.85, 2.4]} t0={r[0] ?? 0.4} /></group>
    <Rig from={[0.9, 1.9, 3.6]} to={[0.1, 1.75, 2.6]} look={[-0.3, 1.5, 0]} dur={dur} />
  </>),
  crash: ({r, dur}) => (<>
    <World bg="#3a1416" ground="#5a2224" fog={false} />
    <Bars t0={r[0] ?? 0.3} />
    <Rig from={[5, 3.5, 7]} to={[3.2, 2.2, 5.6]} look={[0.2, 1.4, 0]} dur={dur} />
  </>),
  question: ({r, dur}) => (<>
    <World bg="#e3d6f0" ground="#cdb9e6" />
    <Maya pos={[-0.9, 0, 0.3]} rot={0.3} face="suspicious" />
    <mesh position={[1.6, 0.9, -0.4]} rotation={[0, -0.4, 0]}><boxGeometry args={[1.8, 1.1, 0.12]} /><meshStandardMaterial color="#222" /></mesh>
    <mesh position={[1.6, 0.25, -0.4]}><cylinderGeometry args={[0.05, 0.25, 0.5, 16]} /><meshStandardMaterial color="#444" /></mesh>
    <Rig from={[-2.5, 2.4, 5]} to={[0.5, 2.1, 4.4]} look={[0, 1.3, 0]} dur={dur} />
  </>),
  dollar: ({r, dur}) => (<>
    <World bg="#d7efe1" ground="#bfe3cd" />
    <Bills from={[0, 1.6, 0]} a={0} b={0.1} hop={0} scale={1.6} />
    <Rig from={[0, 2.0, 5.5]} to={[0.8, 1.8, 3.2]} look={[0, 1.6, 0]} dur={dur} />
  </>),
  city: ({r, dur}) => (<>
    <World bg="#dbe6f5" ground="#c6d4ea" />
    {[[-4.5, 4.5], [-1.5, 5.5], [1.5, 4], [4.5, 5]].map(([x, h], i) => <Building key={i} pos={[x, 0, -1]} h={h} t0={r[i] ?? 0.4 + i * 0.5} />)}
    <Bills from={[-6, 1.2, 1.5]} to={[0, 1.6, 1.5]} a={r[0] ?? 0.5} b={(r[3] ?? 3) + 0.4} hop={0.8} copies={10} swarmAt={r[4] ?? 99} />
    <Rig from={[-2, 4, 11]} to={[1.5, 3.2, 9]} look={[0, 2.2, 0]} dur={dur} />
  </>),
  datacenter: ({r, dur}) => (<>
    <World bg="#10202a" ground="#1a2c38" fog />
    {[-1.6, 1.6].map((x) => [0, -1.6, -3.2, -4.8, -6.4].map((z) => <Rack key={`${x}${z}`} pos={[x, 0, z]} />))}
    <Bills from={[0, 1.4, 3]} to={[0, 1.4, -5]} a={r[0] ?? 0.3} b={(r[0] ?? 0.3) + 2.6} hop={0.3} />
    <Chip pos={[0, 0, -8.5]} s={0.8} />
    <Rig from={[0, 1.9, 5.5]} to={[0, 1.7, 0.5]} look={[0, 1.2, -6]} dur={dur} />
  </>),
  nvidia: ({r, dur}) => (<>
    <World bg="#0f2414" ground="#173a20" fog={false} />
    <Chip pos={[0, 0, 0]} s={1.3} />
    <Bills from={[-5, 4, 2]} to={[0, 1.2, 0]} a={r[0] ?? 0.4} b={(r[0] ?? 0.4) + 1.4} hop={1.5} />
    <Rig from={[4, 4.5, 6]} to={[-2.5, 3.6, 5]} look={[0, 0.6, 0]} dur={dur} />
  </>),
  boomerang: ({r, dur}) => (<>
    <World bg="#2a1238" ground="#3d1c50" fog={false} />
    <Chip pos={[-1.2, 0, 0]} s={1.0} />
    <Bills from={[-1.2, 1, 0]} to={[3.5, 2.8, 2.5]} a={r[0] ?? 0.8} b={(r[0] ?? 0.8) + 1.2} hop={2} />
    <Maya pos={[3, 0, -0.5]} rot={-0.6} face="calm" reacts={[{t: r[1] ?? 99, face: 'surprised'}]} />
    <Rig from={[0.5, 3, 7.5]} to={[1.5, 2.6, 6]} look={[0.6, 1.2, 0]} dur={dur} />
  </>),
};

const Set3D = ({el, dur, width, height}) => {
  const frame = useCurrentFrame();
  const Fn = SETS[el.set];
  const fade = interpolate(frame, [0, 8], [0, 1], clamp);
  if (!Fn) return null;
  return (
    <AbsoluteFill style={{opacity: fade}}>
      <ThreeCanvas width={width} height={height} linear={false} gl={{antialias: true}}
        camera={{fov: 40, near: 0.1, far: 120, position: [0, 2, 8]}}>
        <Fn r={el.reveal || []} dur={dur} />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};

const EXIT = 12;
export const Story3D = ({scenes, width, height, countdown, ticker}) => {
  const {fps} = useVideoConfig();
  const k = (width || 1920) / 1920;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {scenes.map((s, i) => {
        const dur = s.end - s.start;
        const set = s.elements.find((e) => e.type === 'set3d');
        const overlays = s.elements.filter((e) => e.type !== 'set3d');
        return (
          <Sequence key={i} from={Math.round(s.start * fps)}
            durationInFrames={Math.max(1, Math.round(dur * fps)) + (i < scenes.length - 1 ? EXIT : 0)}>
            {set && <Set3D el={set} dur={dur + EXIT / fps} width={width} height={height} />}
            <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transform: `scale(${k})`, transformOrigin: '0 0'}}>
              {overlays.map((e, j) => <Element key={j} el={e} />)}
            </div>
          </Sequence>
        );
      })}
      <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transform: `scale(${k})`, transformOrigin: '0 0'}}>
        {ticker && ticker.length > 0 && <Ticker items={ticker} />}
        {countdown && <Countdown from={countdown} />}
      </div>
    </AbsoluteFill>
  );
};
