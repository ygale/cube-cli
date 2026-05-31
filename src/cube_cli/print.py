'''Render a Cube as ASCII text lines.'''

from collections.abc import Iterator

from cube_model import Color, Cube, Side, all_colors, side_color

def _center(cube: Cube, side: Side) -> str:
  '''The color of the center of a side.'''
  c: str = side_color(cube, side).name[0].lower()
  return c

def _face_grid(
  cube: Cube, side: Side, indices: list[int]
) -> list[str]:
  '''The three display rows for a face.

  indices is a list of 9 values indexing into all_colors for this
  side, or -1 for the center, in order left-to-right then
  top-to-bottom.
  '''
  ac: list[Color] = all_colors(cube)[side]
  raw: list[str] = [
    ac[i].name[0].lower() if i >= 0
    else _center(cube, side)
    for i in indices
  ]
  return [
    ' '.join(raw[0:3]),
    ' '.join(raw[3:6]),
    ' '.join(raw[6:9]),
  ]

def print_cube(cube: Cube) -> Iterator[str]:
  '''Render an ASCII representation of a cube.

  Layout:

         top
         -----
  left | front | right | back
         -----
         bottom

  Each face is three rows of three color chars separated by spaces.
  Faces in the horizontal row are separated by " | ".
  Faces in the vertical column are separated by "-----".
  Top/bottom are indented to align with front.
  '''
  # For each face, the indices into the all_colors color list,
  # or -1 for the center, to get the colors for that face
  # in the correct order for display.
  # The indices for a face depend on the starting corner of
  # the all_corners color list for the face.
  face_indices: dict[Side, list[int]] = {
    # front: top-left start
    Side.FRONT:  [0, 1, 2,  7, -1, 3,  6, 5, 4],
    # top: front-left start
    Side.TOP:    [2, 3, 4,  1, -1, 5,  0, 7, 6],
    # bottom: left-front start
    Side.BOTTOM: [0, 1, 2,  7, -1, 3,  6, 5, 4],
    # left: top-front start
    Side.LEFT:   [6, 7, 0,  5, -1, 1,  4, 3, 2],
    # right: front-top start
    Side.RIGHT:  [0, 1, 2,  7, -1, 3,  6, 5, 4],
    # back: top-right start
    Side.BACK:   [6, 7, 0,  5, -1, 1,  4, 3, 2],
  }
  indent: str = ' ' * 6
  sep: str = '-' * 5
  rows: dict[Side, list[str]] = {
    s: _face_grid(cube, s, face_indices[s])
    for s in Side
  }
  row: str
  for row in rows[Side.TOP]:
    yield indent + row
  yield indent + sep
  middle: tuple[Side, Side, Side, Side] = (
    Side.LEFT, Side.FRONT, Side.RIGHT, Side.BACK
  )
  l: str; f: str; r: str; b: str
  for l, f, r, b in zip(*(rows[s] for s in middle)):
    yield f'{l} | {f} | {r} | {b}'
  yield indent + sep
  for row in rows[Side.BOTTOM]:
    yield indent + row
