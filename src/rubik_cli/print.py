'''Render a Cube as ASCII text lines.'''

from collections.abc import Iterator

from rubik_model import Cube, Side, all_colors, side_color


def _color_char(cube: Cube, side: Side) -> str:
    '''Return the single character for a side color.'''
    return side_color(cube, side).name[0].lower()


def _face_grid(cube: Cube, side: Side, colors: list[int]) -> list[str]:
    '''Return three display rows for a face.

    colors is a list of 9 indices into the all_colors list for this
    side: row0-col0, row0-col1, row0-col2, row1-col0, row1-col2,
    row2-col0, row2-col1, row2-col2 (center is side_color).
    The index -1 means use side_color (the center).
    '''
    ac: list[int] = colors
    raw: list[str] = [
        all_colors(cube)[side][i].name[0].lower() if i >= 0
        else _color_char(cube, side)
        for i in ac
    ]
    rows: list[str] = [
        ' '.join(raw[0:3]),
        ' '.join(raw[3:6]),
        ' '.join(raw[6:9]),
    ]
    return rows


def print_cube(cube: Cube) -> Iterator[str]:
    '''Render an ASCII representation of a cube.

    Layout:

         -----
         top
         -----
    left | front | right | back
         -----
         bottom
         -----

    Each face is three rows of three color chars separated by spaces.
    Faces in the horizontal row are separated by " | ".
    top/bottom are indented to align with front (5 chars = "xxx | ").
    The separator between top and the row is "-----", likewise below.

    For each face the 9 positions are filled from all_colors (8
    outer stickers) plus side_color (center), using the index mapping:
      [0][1][2]
      [7][c][3]
      [6][5][4]
    where the starting corner and CW direction follow all_colors docs.

    For the four horizontal faces the top row is the edge adjacent
    to top and the bottom row is adjacent to bottom, left-to-right
    as seen facing that face from outside.

    For top, the bottom row is adjacent to front and the top row is
    adjacent to back.  For bottom the opposite: top row adjacent to
    front, bottom row adjacent to back.
    '''
    ac: dict[Side, list[int]] = {
        # front: starts top-left (borders left,top), CW
        # row0=[0,1,2], row1=[7,c,3], row2=[6,5,4]
        Side.FRONT: [0, 1, 2, 7, -1, 3, 6, 5, 4],
        # top: starts front-left (borders front,left), CW
        # bottom edge (adj front) = [0,1,2]
        # top edge (adj back)     = [6,5,4]
        # display: top-row=[6,5,4], mid=[7,c,3], bot-row=[0,1,2]
        Side.TOP:    [6, 5, 4, 7, -1, 3, 0, 1, 2],
        # bottom: starts left-front (borders left,front), CW
        # top edge (adj front) = [0,1,2]
        # display: top-row=[0,1,2], mid=[7,c,3], bot-row=[6,5,4]
        Side.BOTTOM: [0, 1, 2, 7, -1, 3, 6, 5, 4],
        # left: starts top-front (borders top,front), CW
        # top edge (adj top): top-back=2, top=1, top-front=0 → [2,1,0]
        # bot edge (adj bot): bot-back=4, bot=5, bot-front=6 → [4,5,6]
        Side.LEFT:   [2, 1, 0, 7, -1, 3, 4, 5, 6],
        # right: starts front-top (borders front,top), CW
        # top edge (adj top): front-top=0, top=1, back-top=2 → [0,1,2]
        # bot edge (adj bot): front-bot=6, bot=5, back-bot=4 → [6,5,4]
        Side.RIGHT:  [0, 1, 2, 7, -1, 3, 6, 5, 4],
        # back: starts top-left (borders top,left), CW facing back
        # displayed left-to-right as seen from front (mirror):
        # top edge (adj top): top-right(back)=2, top=1, top-left(back)=0 → [2,1,0]
        # bot edge (adj bot): bot-right(back)=4, bot=5, bot-left(back)=6 → [4,5,6]
        Side.BACK:   [2, 1, 0, 3, -1, 7, 4, 5, 6],
    }

    indent: str = ' ' * 6
    sep: str = '-' * 5

    top_rows: list[str] = _face_grid(cube, Side.TOP, ac[Side.TOP])
    bot_rows: list[str] = _face_grid(cube, Side.BOTTOM, ac[Side.BOTTOM])
    left_rows: list[str] = _face_grid(cube, Side.LEFT, ac[Side.LEFT])
    front_rows: list[str] = _face_grid(cube, Side.FRONT, ac[Side.FRONT])
    right_rows: list[str] = _face_grid(cube, Side.RIGHT, ac[Side.RIGHT])
    back_rows: list[str] = _face_grid(cube, Side.BACK, ac[Side.BACK])

    yield indent + sep
    for row in top_rows:
        yield indent + row
    yield indent + sep
    for l, f, r, b in zip(left_rows, front_rows, right_rows, back_rows):
        yield f'{l} | {f} | {r} | {b}'
    yield indent + sep
    for row in bot_rows:
        yield indent + row
    yield indent + sep
