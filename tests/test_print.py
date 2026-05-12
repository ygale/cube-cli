'''Tests for rubik_cli.print.'''

from collections.abc import Iterable
import pytest

from rubik_model import (Cube, Move, move, Multiplicity, Side,
  side_color, solved)
from rubik_cli.print import print_cube

# A reference cube for a source of sticker objrcts
_ref: Cube = solved()

def test_print_cube_solved_is_monochrome() -> None:
    '''Every cell on each face should show that face color char.'''
    cube = solved(initial = _ref)
    lines = list(print_cube(cube))
    face_chars: dict[Side, str] = {
        side: side_color(cube, side).name[0].lower()
        for side in Side
    }
    for i, row in enumerate(lines[4:7]):
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
    '''Output should be exactly 11 lines.'''
    cube = solved(initial = _ref)
    lines = list(print_cube(cube))
    # 3 top + sep + 3 horiz + sep + 3 bot = 11
    assert len(lines) == 11, f'expected 11 lines, got {len(lines)}'

def test_print_cube_solved_top_color() -> None:
    '''Top face rows should all be the top color char.'''
    cube = solved(initial = _ref)
    top_char = side_color(cube, Side.TOP).name[0].lower()
    lines = list(print_cube(cube))
    for row in lines[0:3]:
        for ch in row.strip().split():
            assert ch == top_char

def test_print_cube_solved_bottom_color() -> None:
    '''Bottom face rows should all be the bottom color char.'''
    cube = solved(initial = _ref)
    bot_char = side_color(cube, Side.BOTTOM).name[0].lower()
    lines = list(print_cube(cube))
    for row in lines[8:11]:
        for ch in row.strip().split():
            assert ch == bot_char

# The expected sequence of colors in each line of print output
# after a CW move on the given side on a solved cube.
_CW_MOVE: dict[Side, list[str]] = {
  Side.FRONT:
    ['www',
     'www',
     'ooo', '',
     'ooygggwrrbbb',
     'ooygggwrrbbb',
     'ooygggwrrbbb', '',
     'rrr',
     'yyy',
     'yyy'],
  Side.TOP:
    ['www',
     'www',
     'www', '',
     'gggrrrbbbooo',
     'ooogggrrrbbb',
     'ooogggrrrbbb', '',
     'yyy',
     'yyy',
     'yyy'],
  Side.RIGHT:
    ['wwg',
     'wwg',
     'wwg', '',
     'oooggyrrrwbb',
     'oooggyrrrwbb',
     'oooggyrrrwbb', '',
     'yyb',
     'yyb',
     'yyb'],
  Side.BOTTOM:
    ['www',
     'www',
     'www', '',
     'ooogggrrrbbb',
     'ooogggrrrbbb',
     'bbbooogggrrr', '',
     'yyy',
     'yyy',
     'yyy'],
  Side.LEFT:
    ['bww',
     'bww',
     'bww', '',
     'ooowggrrrbby',
     'ooowggrrrbby',
     'ooowggrrrbby', '',
     'gyy',
     'gyy',
     'gyy'],
  Side.BACK:
    ['rrr',
     'www',
     'www', '',
     'woogggrrybbb',
     'woogggrrybbb',
     'woogggrrybbb', '',
     'yyy',
     'yyy',
     'ooo'],
}

def check_print_output(
    actual: Iterable[str],
    expected: Iterable[str]
    ) -> bool:
  '''The sequence of colors in each line of the print
  output is as expected.'''
  actual_colors: list[str] = [
    ''.join(c for c in line if c in "bgorwy")
    for line in actual]
  return actual_colors == list(expected)

@pytest.mark.parametrize('side', Side)
def test_print_after_cw_move(side: Side) -> None:
  '''The order of colors in the print output is as ecpected after
  a CW move on the given side on a solved cube.'''
  cube: Cube = solved(initial = _ref)
  move(Move(side, Multiplicity.CW), cube)
  ok: bool = check_print_output(print_cube(cube), _CW_MOVE[side])
  assert ok, f'unexpected color order after {side.name} CW move'
