'''Tests for ReplState fields and are_you_sure.'''
from cube_model import solved
from pytest import MonkeyPatch

from cube_cli.repl_state import ReplState, are_you_sure

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
