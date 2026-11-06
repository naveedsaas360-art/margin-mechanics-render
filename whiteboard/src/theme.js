import {loadFont as loadCaveat} from '@remotion/google-fonts/Caveat';
import {loadFont as loadMarker} from '@remotion/google-fonts/PermanentMarker';

export const HAND = loadCaveat('normal', {weights: ['400', '700'], subsets: ['latin']}).fontFamily;
export const MARKER = loadMarker('normal', {weights: ['400'], subsets: ['latin']}).fontFamily;

export const PAPER = '#FBFAF6';

// Marker colours; scenes refer to them by name.
export const INK = {
  black: '#1E1E24',
  blue: '#1F5FBF',
  red: '#D7362B',
  green: '#1B9E5A',
  orange: '#E8871E',
  grey: '#8A8A94',
  yellow: '#FFD84D',
  white: '#FFFFFF',
};

export const ink = (c) => INK[c] || c || INK.black;

// Default seconds to draw each element type.
export const DRAW_SECONDS = {
  write: 0.9, count: 1.2, icon: 1.0, bars: 2.0, arrow: 0.6,
  circle: 0.6, underline: 0.5, box: 0.7, highlight: 0.4, line: 0.5, clip: 0.5, peep: 0.6,
};
