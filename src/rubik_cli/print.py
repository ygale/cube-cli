'''Render a Cube as ASCII text lines.'''

from collections.abc import Iterator

from rubik_model import Color, Cube, Side, all_colors, side_color


def _color_char(cube: Cube, side: Side) -> str:
    '''Return the single character for a side color.'''
    c: str = side_color(cube, side).name[0].lower()
    return c


def _face_grid(
    cube: Cube, side: Side, indices: list[int]
) -> list[str]:
    '''Return three display rows for a face.

    indices is a list of 9 values indexing into all_colors for this
    side. The value -1 means use side_color (the center sticker).
    '''
    ac: list[Color] = all_colors(cube)[side]
    raw: list[str] = [
        ac[i].name[0].lower() if i >= 0
        else _color_char(cube, side)
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
    top/bottom are indented to align with front.
    Separators appear only between adjacent faces.

    Index mapping into all_colors (8 outer stickers, -1 = center):
      [0][1][2]
      [7][c][3]
      [6][5][4]

    Starting corners and CW directions per all_colors docstring:
      front:  borders left, top  → top-left corner, CW
      top:    borders front, left → front-left corner, CW (looking down)
      right:  borders front, top  → front-top corner, CW (looking right)
      left:   borders top, front  → top-front corner, CW (looking left)
      bottom: borders left, front → left-front corner, CW (looking up)
      back:   borders top, left   → top-left(back)=top-right(cube), CW (looking back)
    '''
    face_indices: dict[Side, list[int]] = {
        # front: top-left start, CW looking front
        Side.FRONT:  [0, 1, 2,  7, -1, 3,  6, 5, 4],
        # top: front-left start, CW looking down
        Side.TOP:    [2, 3, 4,  1, -1, 5,  0, 7, 6],
        # bottom: left-front start, CW looking up
        Side.BOTTOM: [0, 1, 2,  7, -1, 3,  6, 5, 4],
        # left: top-front start, CW looking from left
        Side.LEFT:   [6, 7, 0,  5, -1, 1,  4, 3, 2],
        # right: front-top start, CW looking from right
        Side.RIGHT:  [0, 1, 2,  7, -1, 3,  6, 5, 4],
        # back: top-right start, CW looking from back
        Side.BACK:   [6, 7, 0,  5, -1, 1,  4, 3, 2],
    }
    indent: str = ' ' * 6
    sep: str = '-' * 5
    top_rows: list[str] = _face_grid(
        cube, Side.TOP, face_indices[Side.TOP]
    )
    bot_rows: list[str] = _face_grid(
        cube, Side.BOTTOM, face_indices[Side.BOTTOM]
    )
    left_rows: list[str] = _face_grid(
        cube, Side.LEFT, face_indices[Side.LEFT]
    )
    front_rows: list[str] = _face_grid(
        cube, Side.FRONT, face_indices[Side.FRONT]
    )
    right_rows: list[str] = _face_grid(
        cube, Side.RIGHT, face_indices[Side.RIGHT]
    )
    back_rows: list[str] = _face_grid(
        cube, Side.BACK, face_indices[Side.BACK]
    )
    for row in top_rows:
        yield indent + row
    yield indent + sep
    for l, f, r, b in zip(left_rows, front_rows, right_rows, back_rows):
        yield f'{l} | {f} | {r} | {b}'
    yield indent + sep
    for row in bot_rows:
        yield indent + row
