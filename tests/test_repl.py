'''Tests for the REPL initial-state loading and tab completion.'''
from pathlib import Path
from pytest import CaptureFixture

from cube_model import solved

from cube_cli.command import Save
from cube_cli.repl import (
  _COMPLETIONS,
  _NON_COMPLETIONS,
  _complete,
  _initial_state,
)
from cube_cli.repl_state import ReplState

def test_no_filename_starts_solved() -> None:
  rs: ReplState = _initial_state(None)
  assert rs.cube == solved()
  assert rs.last_file is None
  assert rs.unsaved is False

def test_valid_filename_loads_state( tmp_path: Path) -> None:
  f: str = str(tmp_path / 'cube.json')
  Save(filename=f).run(ReplState(cube=solved()))
  rs: ReplState = _initial_state(f)
  assert rs.load_error is None
  assert rs.last_file == f
  assert rs.unsaved is False

def test_invalid_filename_falls_back_to_solved( tmp_path: Path) -> None:
  missing: str = str(tmp_path / 'no_such_file.json')
  rs: ReplState = _initial_state(missing)
  assert rs.load_error is not None
  assert rs.load_error.filename == missing
  assert rs.last_file is None
  assert rs.unsaved is False
  assert rs.cube == solved()

def _all_matches(text: str) -> list[str]:
  '''Collect every completion _complete offers for text, in order.'''
  matches: list[str] = []
  state: int
  for state in range(len(_COMPLETIONS) + 10):
    match: str | None = _complete(text, state)
    if match is None:
      break
    matches.append(match)
    state += 1
  return matches

def test_completions_cover_all_command_aliases() -> None:
  assert sorted(_COMPLETIONS) == sorted([
    'shuffle', 'solve', 'load', 'save', 'undo', 'redo', 'quit', 'q',
    'help', '?',
  ])

def test_non_completions_for_all_protected_aliases() -> None:
  assert _NON_COMPLETIONS == {'s', 'l', 'u', 'red'}

def test_complete_blocks_bare_move_letters() -> None:
  '''Bare letters that are also valid moves do not complete:
  s (slice), l (face), u (face), r (face).
  '''
  assert _all_matches('s') == []
  assert _all_matches('l') == []
  assert _all_matches('u') == []
  assert _all_matches('r') == []

def test_complete_blocks_empty_text() -> None:
  assert _all_matches('') == []

def test_complete_blocks_re_for_redo() -> None:
  '''"red" alone still does not complete; "redo" does.'''
  assert _all_matches('red') == []
  assert _all_matches('redo') == ['redo']

def test_complete_matches_once_past_min_chars() -> None:
  assert _all_matches('sh') == ['shuffle']
  assert _all_matches('so') == ['solve']
  assert _all_matches('sa') == ['save']
  assert _all_matches('un') == ['undo']
  assert _all_matches('lo') == ['load']

def test_complete_is_case_insensitive_and_lower_case() -> None:
  assert _all_matches('Q') == ['q', 'quit']
  assert _all_matches('q') == ['q', 'quit']

def test_complete_no_match_returns_none() -> None:
  assert _complete('zz', 0) is None
