'''Tests for the REPL initial-state loading behavior.'''
from pathlib import Path
from pytest import CaptureFixture

from cube_model import solved

from cube_cli.command import Save
from cube_cli.repl import _initial_state
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
