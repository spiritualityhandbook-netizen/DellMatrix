/**
 * ASCII body pack — agents as rotatable / walkable text figures
 * No music content. Pure visual agent representation.
 */

export const DIRS = {
  N:  ['  o  ', ' /|\\ ', ' / \\ '],
  NE: ['  o  ', ' /|> ', ' / \\ '],
  E:  ['  o  ', '  |\\ ', ' / \\ '],
  SE: ['  o  ', '  |> ', ' \\ \\ '],
  S:  ['  o  ', ' \\|/ ', ' / \\ '],
  SW: ['  o  ', ' <|  ', ' / / '],
  W:  ['  o  ', ' /|  ', ' / \\ '],
  NW: ['  o  ', ' /|\\ ', ' / \\ ']
};

export const BODIES = {
  stick: { name: 'Stick', frames: DIRS },
  block: {
    name: 'Block',
    frames: {
      N: ['  O  ', ' [|] ', ' / \\ '],
      E: ['  O  ', '  |] ', ' / \\ '],
      S: ['  O  ', ' [|] ', ' / \\ '],
      W: ['  O  ', ' [|  ', ' / \\ ']
    }
  },
  shadow: {
    name: 'Shadow',
    frames: {
      N: ['  °  ', ' /|\\ ', ' / \\ '],
      E: ['  °  ', '  |\\ ', ' / \\ '],
      S: ['  °  ', ' \\|/ ', ' / \\ '],
      W: ['  °  ', ' /|  ', ' / \\ ']
    }
  },
  robot: {
    name: 'Robot',
    frames: {
      N: [' [==] ', ' |00| ', ' /||\\ '],
      E: [' [==] ', ' |00| ', '  ||\\ '],
      S: [' [==] ', ' |00| ', ' /||\\ '],
      W: [' [==] ', ' |00| ', ' /||  ']
    }
  }
};

export function renderBody(type = 'stick', dir = 'N') {
  const body = BODIES[type] || BODIES.stick;
  const frame = body.frames[dir] || body.frames.N || DIRS.N;
  return frame.join('\n');
}

export function listBodies() {
  return Object.keys(BODIES);
}
