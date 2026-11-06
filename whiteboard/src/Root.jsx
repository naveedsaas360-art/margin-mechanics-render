import {Composition} from 'remotion';
import {Board} from './Board';
import {Doc} from './Doc';
import {Story3D} from './Story3D';

const FPS = 30;

// Size and length come from the props render.py writes.
const calculateMetadata = ({props}) => ({
  durationInFrames: Math.max(FPS, Math.ceil(props.duration * FPS)),
  width: props.width || 1920,
  height: props.height || 1080,
});

export const Root = () => (
  <>
  <Composition
    id="Story3D"
    component={Story3D}
    fps={FPS}
    width={1920}
    height={1080}
    durationInFrames={FPS * 10}
    defaultProps={{duration: 10, scenes: []}}
    calculateMetadata={calculateMetadata}
  />
  <Composition
    id="Doc"
    component={Doc}
    fps={FPS}
    width={1920}
    height={1080}
    durationInFrames={FPS * 10}
    defaultProps={{duration: 10, scenes: []}}
    calculateMetadata={calculateMetadata}
  />
  <Composition
    id="Board"
    component={Board}
    fps={FPS}
    width={1920}
    height={1080}
    durationInFrames={FPS * 10}
    defaultProps={{duration: 10, scenes: [], audio: null, captions: []}}
    calculateMetadata={calculateMetadata}
  />
  </>
);
