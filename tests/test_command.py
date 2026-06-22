'''Tests for Command subclasses: unsaved tracking, confirmation, files.'''
import json
from pathlib import Path
from pytest import CaptureFixture, MonkeyPatch

from cube_model import Cube, shuffled, solved

from cube_cli.command import (
  DEFAULT_FILE,
  Help,
  Load,
  Move,
  Noop,
  Quit,
  Redo,
  Save,
  Shuffle,
  Solve,
  Tabbable,
  Undo,
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

def test_move_pushes_undo_item() -> None:
  rs: ReplState = ReplState(cube=solved())
  cmd: Move | None = Move.parse('R U')
  assert cmd is not None
  cmd.run(rs)
  assert len(rs.undo_buf) == 1
  assert rs.redo_buf == []

def test_undo_after_move_restores_previous_cube() -> None:
  rs: ReplState = ReplState(cube=solved())
  before: Cube = rs.cube
  cmd: Move | None = Move.parse('R U')
  assert cmd is not None
  cmd.run(rs)
  Undo().run(rs)
  assert rs.cube == before
  assert rs.unsaved is False
  assert rs.undo_buf == []
  assert len(rs.redo_buf) == 1

def test_redo_after_undo_of_move_reapplies_move() -> None:
  rs: ReplState = ReplState(cube=solved())
  cmd: Move | None = Move.parse('R U')
  assert cmd is not None
  cmd.run(rs)
  after_move: Cube = rs.cube
  Undo().run(rs)
  Redo().run(rs)
  assert rs.cube == after_move
  assert rs.unsaved is True
  assert rs.redo_buf == []
  assert len(rs.undo_buf) == 1

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

def test_shuffle_pushes_undo_item_when_confirmed(
    monkeypatch: MonkeyPatch) -> None:
  rs: ReplState = ReplState(cube=solved(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'yes')
  Shuffle().run(rs)
  assert len(rs.undo_buf) == 1
  assert rs.redo_buf == []

def test_shuffle_does_not_push_undo_item_when_cancelled(
    monkeypatch: MonkeyPatch) -> None:
  rs: ReplState = ReplState(cube=solved(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'no')
  Shuffle().run(rs)
  assert rs.undo_buf == []

def test_undo_after_shuffle_restores_previous_cube() -> None:
  rs: ReplState = ReplState(cube=solved())
  before: Cube = rs.cube
  Shuffle().run(rs)
  Undo().run(rs)
  assert rs.cube is before
  assert rs.unsaved is False
  assert rs.undo_buf == []
  assert len(rs.redo_buf) == 1

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

def test_solve_pushes_undo_item_when_confirmed(
    monkeypatch: MonkeyPatch) -> None:
  rs: ReplState = ReplState(cube=shuffled(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'yes')
  Solve().run(rs)
  assert len(rs.undo_buf) == 1
  assert rs.redo_buf == []

def test_solve_does_not_push_undo_item_when_cancelled(
    monkeypatch: MonkeyPatch) -> None:
  rs: ReplState = ReplState(cube=shuffled(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'no')
  Solve().run(rs)
  assert rs.undo_buf == []

def test_undo_after_solve_restores_previous_cube() -> None:
  rs: ReplState = ReplState(cube=shuffled())
  before: Cube = rs.cube
  Solve().run(rs)
  Undo().run(rs)
  assert rs.cube is before
  assert rs.unsaved is False
  assert rs.undo_buf == []
  assert len(rs.redo_buf) == 1

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

def test_load_pushes_undo_item_on_success(tmp_path: Path) -> None:
  f: str = str(tmp_path / 'cube.json')
  saved_cube: Cube = shuffled()
  Save(filename=f).run(ReplState(cube=saved_cube))
  rs: ReplState = ReplState(cube=solved(), unsaved=False)
  Load(filename=f).run(rs)
  assert len(rs.undo_buf) == 1
  assert rs.redo_buf == []

def test_load_does_not_push_undo_item_on_failure(
    tmp_path: Path) -> None:
  f: str = str(tmp_path / 'no_such_file.json')
  rs: ReplState = ReplState(cube=solved())
  Load(filename=f).run(rs)
  assert rs.undo_buf == []

def test_load_does_not_push_undo_item_when_cancelled(
    monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
  f: str = str(tmp_path / 'cube.json')
  Save(filename=f).run(ReplState(cube=shuffled()))
  rs: ReplState = ReplState(cube=solved(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'no')
  Load(filename=f).run(rs)
  assert rs.undo_buf == []

def test_undo_after_load_restores_previous_cube_without_reload(
    tmp_path: Path) -> None:
  f: str = str(tmp_path / 'cube.json')
  saved_cube: Cube = shuffled()
  Save(filename=f).run(ReplState(cube=saved_cube))
  rs: ReplState = ReplState(cube=solved(), unsaved=False)
  before: Cube = rs.cube
  Load(filename=f).run(rs)
  Undo().run(rs)
  assert rs.cube is before
  assert rs.unsaved is False
  assert rs.last_file == f
  assert rs.undo_buf == []
  assert len(rs.redo_buf) == 1

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

def test_undo_parse_matches_undo() -> None:
  assert Undo.parse('undo') is not None

def test_undo_parse_rejects_other_input() -> None:
  assert Undo.parse('undone') is None

def test_undo_with_empty_buffer_prints_message(
    capsys: CaptureFixture[str]) -> None:
  rs: ReplState = ReplState(cube=solved())
  Undo().run(rs)
  assert capsys.readouterr().out.strip() == 'Nothing to undo'

def test_undo_with_empty_buffer_suppresses_cube_print() -> None:
  rs: ReplState = ReplState(cube=solved())
  Undo().run(rs)
  assert rs.print_cube is False

def test_redo_parse_matches_redo() -> None:
  assert Redo.parse('redo') is not None

def test_redo_parse_rejects_other_input() -> None:
  assert Redo.parse('redone') is None

def test_redo_with_empty_buffer_prints_message(
    capsys: CaptureFixture[str]) -> None:
  rs: ReplState = ReplState(cube=solved())
  Redo().run(rs)
  assert capsys.readouterr().out.strip() == 'Nothing to redo'

def test_redo_with_empty_buffer_suppresses_cube_print() -> None:
  rs: ReplState = ReplState(cube=solved())
  Redo().run(rs)
  assert rs.print_cube is False

def test_new_move_after_undo_clears_redo_buf() -> None:
  rs: ReplState = ReplState(cube=solved())
  cmd: Move | None = Move.parse('R')
  assert cmd is not None
  cmd.run(rs)
  Undo().run(rs)
  assert len(rs.redo_buf) == 1
  cmd2: Move | None = Move.parse('U')
  assert cmd2 is not None
  cmd2.run(rs)
  assert rs.redo_buf == []

def test_shuffle_aliases_requires_two_chars() -> None:
  assert [(a.name, a.min_chars) for a in Shuffle.aliases] == [('shuffle', 2)]

def test_solve_aliases_requires_two_chars() -> None:
  assert [(a.name, a.min_chars) for a in Solve.aliases] == [('solve', 2)]

def test_undo_aliases_requires_two_chars() -> None:
  assert [(a.name, a.min_chars) for a in Undo.aliases] == [('undo', 2)]

def test_redo_aliases_requires_three_chars() -> None:
  assert [(a.name, a.min_chars) for a in Redo.aliases] == [('redo', 3)]

def test_quit_aliases_is_quit_and_q() -> None:
  assert [a.name for a in Quit.aliases] == ['quit', 'q']

def test_help_aliases_is_help_and_question_mark() -> None:
  assert [a.name for a in Help.aliases] == ['help', '?']

def test_load_alias_requires_two_chars() -> None:
  assert [(a.name, a.min_chars) for a in Load.aliases] == [('load', 2)]

def test_save_alias_requires_two_chars() -> None:
  assert [(a.name, a.min_chars) for a in Save.aliases] == [('save', 2)]

def test_move_and_noop_are_not_tabbable() -> None:
  assert not issubclass(Move, Tabbable)
  assert not issubclass(Noop, Tabbable)

def test_match_true_for_exact_alias() -> None:
  assert Shuffle.match('shuffle') is True

def test_match_false_for_non_alias() -> None:
  assert Shuffle.match('shuffled') is False

def test_match_true_for_any_of_several_aliases() -> None:
  assert Quit.match('quit') is True
  assert Quit.match('q') is True

def test_match_false_for_empty_string() -> None:
  assert Shuffle.match('') is False
