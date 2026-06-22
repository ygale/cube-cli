'''Tests for ReplState fields and are_you_sure.'''
from cube_model import Cube, solved
from cube_model.action import Action, act, parse_actions
from pytest import MonkeyPatch

from cube_cli.repl_state import (
  Alias,
  ReplState,
  UndoCube,
  UndoItem,
  UndoMove,
  are_you_sure,
)

def test_default_unsaved_is_false() -> None:
  '''A freshly constructed ReplState defaults to unsaved=False.'''
  rs: ReplState = ReplState(cube=solved())
  assert rs.unsaved is False

def test_default_last_file_is_none() -> None:
  '''A freshly constructed ReplState defaults to last_file=None.'''
  rs: ReplState = ReplState(cube=solved())
  assert rs.last_file is None

def test_are_you_sure_skips_prompt_when_saved(
    monkeypatch: MonkeyPatch) -> None:
  '''are_you_sure returns True without prompting if cube is saved.'''
  rs: ReplState = ReplState(cube=solved(), unsaved=False)
  called: list[str] = []

  def fake_input(prompt: str) -> str:
    called.append(prompt)
    return 'no'

  monkeypatch.setattr('builtins.input', fake_input)
  assert are_you_sure(rs) is True
  assert called == []

def test_are_you_sure_yes(monkeypatch: MonkeyPatch) -> None:
  '''are_you_sure returns True on "yes".'''
  rs: ReplState = ReplState(cube=solved(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'yes')
  assert are_you_sure(rs) is True

def test_are_you_sure_y(monkeypatch: MonkeyPatch) -> None:
  '''are_you_sure returns True on "y".'''
  rs: ReplState = ReplState(cube=solved(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'y')
  assert are_you_sure(rs) is True

def test_are_you_sure_case_insensitive(monkeypatch: MonkeyPatch) -> None:
  '''are_you_sure is case-insensitive for "YES" and "Y".'''
  rs: ReplState = ReplState(cube=solved(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'YES')
  assert are_you_sure(rs) is True
  monkeypatch.setattr('builtins.input', lambda _: 'Y')
  assert are_you_sure(rs) is True

def test_are_you_sure_no(monkeypatch: MonkeyPatch) -> None:
  '''are_you_sure returns False on "no".'''
  rs: ReplState = ReplState(cube=solved(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'no')
  assert are_you_sure(rs) is False

def test_are_you_sure_empty(monkeypatch: MonkeyPatch) -> None:
  '''are_you_sure returns False on empty input.'''
  rs: ReplState = ReplState(cube=solved(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: '')
  assert are_you_sure(rs) is False

def test_are_you_sure_garbage(monkeypatch: MonkeyPatch) -> None:
  '''are_you_sure returns False on unrelated input.'''
  rs: ReplState = ReplState(cube=solved(), unsaved=True)
  monkeypatch.setattr('builtins.input', lambda _: 'maybe')
  assert are_you_sure(rs) is False

def test_default_undo_buf_and_redo_buf_are_empty() -> None:
  '''A freshly constructed ReplState has empty undo/redo buffers.'''
  rs: ReplState = ReplState(cube=solved())
  assert rs.undo_buf == []
  assert rs.redo_buf == []

def test_alias_defaults_min_chars_to_one() -> None:
  alias: Alias = Alias(name='solve')
  assert alias.min_chars == 1

def test_alias_accepts_explicit_min_chars() -> None:
  alias: Alias = Alias(name='load', min_chars=2)
  assert alias.min_chars == 2

def test_undo_cube_push_appends_current_state() -> None:
  '''UndoCube.push snapshots rs's current cube and unsaved flag.'''
  before: Cube = solved()
  rs: ReplState = ReplState(cube=before, unsaved=True)
  UndoCube.push(rs)
  assert len(rs.undo_buf) == 1
  item: UndoItem = rs.undo_buf[0]
  assert isinstance(item, UndoCube)
  assert item.cube is before
  assert item.unsaved is True

def test_undo_cube_push_clears_redo_buf() -> None:
  '''UndoCube.push clears any pending redo items.'''
  rs: ReplState = ReplState(cube=solved())
  rs.redo_buf.append(UndoCube(unsaved=False, cube=solved()))
  assert rs.redo_buf != []
  UndoCube.push(rs)
  assert rs.redo_buf == []

def test_undo_cube_undo_restores_previous_cube_and_unsaved() -> None:
  '''UndoCube.undo swaps rs's cube and unsaved with its own.'''
  before: Cube = solved()
  rs: ReplState = ReplState(cube=before, unsaved=False)
  UndoCube.push(rs)
  rs.cube = solved()
  rs.unsaved = True
  item: UndoItem = rs.undo_buf.pop()
  item.undo(rs)
  assert rs.cube is before
  assert rs.unsaved is False

def test_undo_cube_redo_restores_state_after_undo() -> None:
  '''Undoing then redoing an UndoCube round-trips rs's state.'''
  before: Cube = solved()
  after: Cube = solved()
  rs: ReplState = ReplState(cube=before, unsaved=False)
  UndoCube.push(rs)
  rs.cube = after
  rs.unsaved = True
  item: UndoItem = rs.undo_buf.pop()
  item.undo(rs)
  assert rs.cube is before
  assert rs.unsaved is False
  item.redo(rs)
  assert rs.cube is after
  assert rs.unsaved is True

def test_undo_move_push_appends_actions_and_unsaved() -> None:
  '''UndoMove.push snapshots rs's unsaved flag and the actions.'''
  rs: ReplState = ReplState(cube=solved(), unsaved=False)
  actions: list[Action] = parse_actions('R U', ci=True)
  UndoMove.push(rs, actions)
  assert len(rs.undo_buf) == 1
  item: UndoItem = rs.undo_buf[0]
  assert isinstance(item, UndoMove)
  assert item.actions == actions
  assert item.unsaved is False

def test_undo_move_push_clears_redo_buf() -> None:
  '''UndoMove.push clears any pending redo items.'''
  rs: ReplState = ReplState(cube=solved())
  rs.redo_buf.append(UndoMove(unsaved=False, actions=[]))
  assert rs.redo_buf != []
  UndoMove.push(rs, parse_actions('U', ci=True))
  assert rs.redo_buf == []

def test_undo_move_undo_applies_inverse_actions() -> None:
  '''UndoMove.undo swaps unsaved and undoes the moves on rs.cube.'''
  rs: ReplState = ReplState(cube=solved(), unsaved=False)
  actions: list[Action] = parse_actions('R U', ci=True)
  UndoMove.push(rs, actions)
  action: Action
  for action in actions:
    act(action, rs.cube)
  rs.unsaved = True
  item: UndoItem = rs.undo_buf.pop()
  item.undo(rs)
  assert rs.cube == solved()
  assert rs.unsaved is False

def test_undo_move_undo_then_redo_round_trip() -> None:
  '''Undoing then redoing an UndoMove round-trips rs.cube and unsaved.'''
  rs: ReplState = ReplState(cube=solved(), unsaved=False)
  actions: list[Action] = parse_actions('R U', ci=True)
  UndoMove.push(rs, actions)
  action: Action
  for action in actions:
    act(action, rs.cube)
  rs.unsaved = True
  after_move: Cube = rs.cube
  item: UndoItem = rs.undo_buf.pop()
  item.undo(rs)
  assert rs.cube == solved()
  assert rs.unsaved is False
  item.redo(rs)
  assert rs.cube == after_move
  assert rs.unsaved is True
