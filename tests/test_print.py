'''Tests for rubik_cli.print.'''

from rubik_model import Side, solved, side_color
from rubik_cli.print import print_cube


def test_print_cube_solved_is_monochrome() -> None:
    '''Every cell on each face should show that face's color char.'''
    cube = solved()
    lines = list(print_cube(cube))
    face_chars = {
        side: side_color(cube, side).name[0].lower()
        for side in Side
    }
    horiz_start = 5
    for i, row in enumerate(lines[horiz_start:horiz_start + 3]):
        parts = row.split(' | ')
        assert len(parts) == 4, f'row {i}: expected 4 faces, got {parts}'
        for part, side in zip(
            parts, [Side.LEFT, Side.FRONT, Side.RIGHT, Side.BACK]
        ):
            expected = face_chars[side]
            for ch in part.split():
                assert ch == expected, (
                    f'side {side}: expected {expected!r}, got {ch!r}'
                )


def test_print_cube_solved_line_count() -> None:
    '''Output should be exactly 13 lines.'''
    cube = solved()
    lines = list(print_cube(cube))
    assert len(lines) == 13, f'expected 13 lines, got {len(lines)}'


def test_print_cube_solved_top_color() -> None:
    '''Top face rows should all be the top color char.'''
    cube = solved()
    top_char = side_color(cube, Side.TOP).name[0].lower()
    lines = list(print_cube(cube))
    for row in lines[1:4]:
        for ch in row.strip().split():
            assert ch == top_char


def test_print_cube_solved_bottom_color() -> None:
    '''Bottom face rows should all be the bottom color char.'''
    cube = solved()
    bot_char = side_color(cube, Side.BOTTOM).name[0].lower()
    lines = list(print_cube(cube))
    for row in lines[9:12]:
        for ch in row.strip().split():
            assert ch == bot_char
