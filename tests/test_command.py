'''Tests for Command subclasses: unsaved tracking, confirmation, files.'''
import json
from pathlib import Path
from pytest import MonkeyPatch

from cube_model import shuffled, solved

from cube_cli.command import (
  DEFAULT_FILE,
  Help,
  Load,
  Move,
  Quit,
  Save,
  Shuffle,
  Solve,
  _is_solved,
  _resolve_file,
)
from cube_cli.repl_state import Exit, ReplState

def test_is_solved_true_for_solved_cube() -> None:
  assert _is_solved(solved()) is True

def test_is_solved_false_for_shuffled_cube() -> None:
  assert _is_solved(shuffled()) is False

def test_resolve_file_uses_given_filename() -> None:
  rs: ReplState = ReplState(cube=solved(), last_file='old.json')
  assert _resolve_file(rs, 'new.json') == 'new.json'

def test_resolve_file_uses_last_file_when_none_given() -> None:
  rs: ReplState = ReplState(cube=solved(), last_file='old.json')
  assert _resolve_file(rs, None) == 'old.json'

def test_resolve_file_uses_default_when_nothing_given() -> None:
  rs: ReplState = ReplState(cube=solved())
  assert _resolve_file(rs, None) == DEFAULT_FILE

def test_move_marks_unsaved_on_nontrivial_move() -> None:
  rs: ReplState = ReplState(cube=solved())
  cmd = Move.parse('R')
  assert cmd is not None
  cmd.run(rs)
  assert rs.unsaved is True

def test_move_marks_saved_when_returns_to_solved() -> None:
  rs: ReplState = ReplState(cube=solved())
  cmd = Move.parse("R R R R")
  assert cmd is not None
  cmd.run(rs)
  assert rs.unsaved is False

def test_shuffle_marks_unsaved() -> None:
  rs: ReplState = ReplState(cube=solved())
  Shuffle().run(rs)
  assert rs.unsaved is True

def test_shuffle_no_prompt_when_saved(monkeypatch: MonkeyPatch) -> None:
  rs: ReplState = ReplState(cube=solved(), unsaved=False)
  monkeypatch.setattr('builtins.input', lambda _: 'no')
  before = rs.cube
  Shuffle().run(rs)
  assert rs.cube is not before

def test_shuffle_cancelled_when_not_confirmed(
    monkeypatch: MonkeyPatch) -> None:
  rs: ReplState = ReplState(cube=solved(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'no')
  before = rs.cube
  Shuffle().run(rs)
  assert rs.cube is before
  assert rs.unsaved is True

def test_shuffle_proceeds_when_confirmed(monkeypatch: MonkeyPatch) -> None:
  rs: ReplState = ReplState(cube=solved(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'yes')
  before = rs.cube
  Shuffle().run(rs)
  assert rs.cube is not before
  assert rs.unsaved is True

def test_solve_marks_saved() -> None:
  rs: ReplState = ReplState(cube=shuffled(), unsaved=False)
  Solve().run(rs)
  assert rs.unsaved is False

def test_solve_cancelled_when_not_confirmed(monkeypatch: MonkeyPatch) -> None:
  rs: ReplState = ReplState(cube=shuffled(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'no')
  before = rs.cube
  Solve().run(rs)
  assert rs.cube is before
  assert rs.unsaved is True

def test_solve_proceeds_when_confirmed(monkeypatch: MonkeyPatch) -> None:
  rs: ReplState = ReplState(cube=shuffled(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'yes')
  Solve().run(rs)
  assert rs.unsaved is False

def test_help_does_not_change_unsaved() -> None:
  rs: ReplState = ReplState(cube=shuffled(), unsaved=True)
  Help().run(rs)
  assert rs.unsaved is True
  rs2: ReplState = ReplState(cube=solved(), unsaved=False)
  Help().run(rs2)
  assert rs2.unsaved is False

def test_quit_exits_when_saved() -> None:
  rs: ReplState = ReplState(cube=solved(), unsaved=False)
  assert Quit().run(rs) is Exit.EXIT

def test_quit_cancelled_when_not_confirmed(monkeypatch: MonkeyPatch) -> None:
  rs: ReplState = ReplState(cube=shuffled(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'no')
  assert Quit().run(rs) is None

def test_quit_exits_when_confirmed(monkeypatch: MonkeyPatch) -> None:
  rs: ReplState = ReplState(cube=shuffled(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'yes')
  assert Quit().run(rs) is Exit.EXIT

def test_save_writes_file_and_updates_state(tmp_path: Path) -> None:
  f: str = str(tmp_path / 'cube.json')
  rs: ReplState = ReplState(cube=shuffled(), unsaved=True)
  Save(filename=f).run(rs)
  assert rs.unsaved is False
  assert rs.last_file == f
  with open(f) as fh:
    data = json.load(fh)
  assert isinstance(data, dict)

def test_save_uses_default_file_when_none_given(
    tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
  monkeypatch.chdir(tmp_path)
  rs: ReplState = ReplState(cube=solved())
  Save(filename=None).run(rs)
  assert rs.last_file == DEFAULT_FILE
  assert (tmp_path / DEFAULT_FILE).exists()

def test_save_failure_does_not_mark_saved(tmp_path: Path) -> None:
  bad_dir: str = str(tmp_path / 'is_a_dir')
  import os
  os.makedirs(bad_dir)
  rs: ReplState = ReplState(cube=shuffled(), unsaved=True)
  Save(filename=bad_dir).run(rs)
  assert rs.unsaved is True
  assert rs.last_file is None

def test_load_reads_file_and_updates_state(tmp_path: Path) -> None:
  f: str = str(tmp_path / 'cube.json')
  saved_cube = shuffled()
  rs0: ReplState = ReplState(cube=saved_cube)
  Save(filename=f).run(rs0)

  rs: ReplState = ReplState(cube=solved(), unsaved=False)
  result = Load(filename=f).run(rs)
  assert result is None
  assert rs.unsaved is False
  assert rs.last_file == f

def test_load_failure_does_not_update_state(tmp_path: Path) -> None:
  f: str = str(tmp_path / 'no_such_file.json')
  rs: ReplState = ReplState(cube=solved(), unsaved=False)
  before = rs.cube
  Load(filename=f).run(rs)
  assert rs.cube is before
  assert rs.last_file is None

def test_load_cancelled_when_not_confirmed(
    monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
  f: str = str(tmp_path / 'cube.json')
  Save(filename=f).run(ReplState(cube=shuffled()))
  rs: ReplState = ReplState(cube=solved(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'no')
  before = rs.cube
  Load(filename=f).run(rs)
  assert rs.cube is before
  assert rs.last_file is None

def test_load_parse_filename_with_internal_space() -> None:
  cmd = Load.parse('load my file.json')
  assert cmd is not None
  assert cmd.filename == 'my file.json'

def test_load_parse_strips_leading_whitespace_only() -> None:
  cmd = Load.parse('load   my file.json')
  assert cmd is not None
  assert cmd.filename == 'my file.json'

def test_load_parse_no_filename() -> None:
  cmd = Load.parse('load')
  assert cmd is not None
  assert cmd.filename is None

def test_load_parse_rejects_non_load_prefix() -> None:
  assert Load.parse('loadfoo.json') is None

def test_load_parse_case_insensitive_keyword() -> None:
  cmd = Load.parse('LOAD foo.json')
  assert cmd is not None
  assert cmd.filename == 'foo.json'

def test_save_parse_filename_with_internal_space() -> None:
  cmd = Save.parse('save my file.json')
  assert cmd is not None
  assert cmd.filename == 'my file.json'

def test_save_parse_strips_leading_whitespace_only() -> None:
  cmd = Save.parse('save   my file.json')
  assert cmd is not None
  assert cmd.filename == 'my file.json'

def test_save_parse_no_filename() -> None:
  cmd = Save.parse('save')
  assert cmd is not None
  assert cmd.filename is None

def test_save_parse_rejects_non_save_prefix() -> None:
  assert Save.parse('savefoo.json') is None
