'''Tests for cube_cli.repl.'''
from io import StringIO
from unittest.mock import patch

import pytest

from cube_model import Cube, solved

from cube_cli.repl import parse_command, repl
from cube_cli.command import (
  Help, Load, Move, Quit, Redo, Save, Shuffle, Solve, Undo,
)
from cube_cli.print import print_cube
from cube_cli.repl_state import ReplState

def _run_cap_raw(
  inp: str,
  capsys: pytest.CaptureFixture[str],
  filename: str | None = None,
) -> str:
  '''Run the repl with literal stdin input and return captured stdout.'''
  with patch('sys.stdin', StringIO(inp)):
    repl(filename)
  return capsys.readouterr().out

def _run_cap(
  commands: list[str],
  capsys: pytest.CaptureFixture[str],
  filename: str | None = None,
) -> str:
  '''Run the repl with a list of commands and return captured stdout.'''
  return _run_cap_raw('\n'.join(commands) + '\n', capsys, filename)

def _cube_lines(out: str) -> list[str]:
  '''Extract only cube-rendering lines from repl output.'''
  return [
    l for l in out.splitlines()
    if not l.startswith('Command') and l.strip()
    and 'not yet implemented' not in l
    and 'Invalid command' not in l
  ]

def _first_cube(out: str) -> list[str]:
  '''Return the first 11 cube lines from repl output.'''
  return _cube_lines(out)[:11]

def _last_cube(out: str) -> list[str]:
  '''Return the last 11 cube lines from repl output.'''
  return _cube_lines(out)[-11:]

def _render(cube: Cube) -> list[str]:
  '''Render a cube to lines using print_cube.'''
  return list(print_cube(cube))

# --- parse_command ---

def test_parse_shuffle() -> None:
  assert isinstance(parse_command('shuffle'), Shuffle)

def test_parse_shuffle_case() -> None:
  assert isinstance(parse_command('SHUFFLE'), Shuffle)

def test_parse_solve() -> None:
  assert isinstance(parse_command('solve'), Solve)

def test_parse_load_no_file() -> None:
  cmd: object = parse_command('load')
  assert isinstance(cmd, Load)
  assert cmd.filename is None

def test_parse_load_with_file() -> None:
  cmd: object = parse_command('load my.json')
  assert isinstance(cmd, Load)
  assert cmd.filename == 'my.json'

def test_parse_save_no_file() -> None:
  cmd: object = parse_command('save')
  assert isinstance(cmd, Save)
  assert cmd.filename is None

def test_parse_save_with_file() -> None:
  cmd: object = parse_command('save my.json')
  assert isinstance(cmd, Save)
  assert cmd.filename == 'my.json'

def test_parse_undo() -> None:
  assert isinstance(parse_command('undo'), Undo)

def test_parse_redo() -> None:
  assert isinstance(parse_command('redo'), Redo)

def test_parse_quit() -> None:
  assert isinstance(parse_command('quit'), Quit)

def test_parse_q() -> None:
  assert isinstance(parse_command('q'), Quit)

def test_parse_help() -> None:
  assert isinstance(parse_command('help'), Help)

def test_parse_question_mark() -> None:
  assert isinstance(parse_command('?'), Help)

def test_parse_move() -> None:
  assert isinstance(parse_command('R U'), Move)

def test_parse_move_case_sensitive() -> None:
  assert isinstance(parse_command('^R U'), Move)

def test_parse_invalid() -> None:
  assert parse_command('123') is None

def test_parse_empty() -> None:
  assert parse_command('') is None

# --- repl behaviour ---

def test_repl_prints_cube(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''Repl should print 11 cube lines before the prompt.'''
  out: str = _run_cap(['q'], capsys)
  assert len(_cube_lines(out)) == 11

def test_repl_starts_with_file(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''Repl with a filename should report load not yet implemented.'''
  out: str = _run_cap(['q'], capsys, filename='my.json')
  assert 'not yet implemented' in out

def test_repl_invalid_command(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''An unrecognized command should print Invalid command.'''
  out: str = _run_cap(['123', 'q'], capsys)
  assert 'Invalid command' in out

def test_repl_invalid_does_not_reprint_cube(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''An invalid command should not reprint the cube immediately.'''
  out: str = _run_cap(['123', 'q'], capsys)
  assert len(_cube_lines(out)) == 11

def test_repl_empty_does_not_reprint_cube(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''Empty input should not reprint the cube immediately.'''
  out: str = _run_cap(['', 'q'], capsys)
  assert len(_cube_lines(out)) == 11

def test_repl_shuffle(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''shuffle should change the cube display.'''
  out: str = _run_cap(['shuffle', 'q'], capsys)
  assert _first_cube(out) != _last_cube(out)

def test_repl_solve(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''solve after shuffle should restore the solved cube.'''
  rs: ReplState = ReplState(cube=solved())
  Shuffle().run(rs)
  Solve().run(rs)
  assert _render(rs.cube) == _render(solved())

def test_repl_move(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''A valid move should change the cube display.'''
  out_before: str = _run_cap(['q'], capsys)
  out_after: str = _run_cap(['R', 'q'], capsys)
  assert _first_cube(out_before) != _last_cube(out_after)

def test_repl_help(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''help should print the command reference.'''
  out: str = _run_cap(['?', 'q'], capsys)
  assert 'quit' in out

def test_repl_undo_stub(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''undo should print not yet implemented.'''
  out: str = _run_cap(['undo', 'q'], capsys)
  assert 'not yet implemented' in out

def test_repl_redo_stub(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''redo should print not yet implemented.'''
  out: str = _run_cap(['redo', 'q'], capsys)
  assert 'not yet implemented' in out

def test_repl_save_stub(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''save should print not yet implemented.'''
  out: str = _run_cap(['save', 'q'], capsys)
  assert 'not yet implemented' in out

def test_repl_load_stub(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''load should print not yet implemented.'''
  out: str = _run_cap(['load', 'q'], capsys)
  assert 'not yet implemented' in out

def test_repl_eod_quits(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''EOF (^d) should quit cleanly without an exception.'''
  _run_cap_raw('', capsys)
