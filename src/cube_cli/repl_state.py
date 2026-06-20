'''REPL state and exit signal for the cube CLI.'''
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

from cube_model import Cube, Move
from cube_model.action import Action, Rotation, SliceMove, WideMove, act
from cube_model.move import invert

class Exit(Enum):
  '''Singleton signal that the REPL should exit.'''
  EXIT = 'exit'

@dataclass
class LoadError:
  '''The error message resulting from a failed load of the cube from
  a file.
  '''
  filename: str
  msg: str

def _invert_action(action: Action) -> Action:
  '''Return the inverse of a single action.

  Inverting a Move inverts its multiplicity directly. Inverting a
  Rotation, WideMove, or SliceMove inverts the multiplicity of the
  Move it wraps, preserving the wrapper type.
  '''
  match action:
    case Rotation(move=m):
      return Rotation(Move(m.face, invert[m.mult]))
    case WideMove(move=m):
      return WideMove(Move(m.face, invert[m.mult]))
    case SliceMove(move=m):
      return SliceMove(Move(m.face, invert[m.mult]))
    case Move() as m:
      return Move(m.face, invert[m.mult])

def _invert_actions(actions: list[Action]) -> list[Action]:
  '''Return the inverse of a sequence of actions.

  The order of the actions is reversed, and each action's
  multiplicity is inverted.
  '''
  return [_invert_action(a) for a in reversed(actions)]

@dataclass
class UndoItem(ABC):
  '''Abstract base for an entry in a ReplState undo or redo stack.'''
  unsaved: bool

  @abstractmethod
  def undo(self, rs: ReplState) -> None:
    '''Undo this item against rs, preparing self for the redo
    buffer.
    '''

  @abstractmethod
  def redo(self, rs: ReplState) -> None:
    '''Redo this item against rs, preparing self for the undo
    buffer.
    '''

@dataclass
class UndoCube(UndoItem):
  '''Undo item capturing a full previous cube and saved state.

  Used by the Shuffle, Solve, and Load commands, which completely
  replace the cube.
  '''
  cube: Cube

  @classmethod
  def push(cls, rs: ReplState) -> None:
    '''Snapshot rs's current cube and unsaved flag onto the undo
    buffer, and clear the redo buffer.
    '''
    rs.undo_buf.append(cls(unsaved=rs.unsaved, cube=rs.cube))
    rs.redo_buf.clear()

  def undo(self, rs: ReplState) -> None:
    '''Swap unsaved and cube with rs.'''
    rs.unsaved, self.unsaved = self.unsaved, rs.unsaved
    rs.cube, self.cube = self.cube, rs.cube

  def redo(self, rs: ReplState) -> None:
    '''Identical to undo: swap unsaved and cube with rs.'''
    self.undo(rs)

@dataclass
class UndoMove(UndoItem):
  '''Undo item capturing a sequence of actions to invert or reapply.

  Used by the Move command.
  '''
  actions: list[Action]

  @classmethod
  def push(cls, rs: ReplState, actions: list[Action]) -> None:
    '''Snapshot rs's current unsaved flag and the actions about to
    be applied onto the undo buffer, and clear the redo buffer.
    '''
    rs.undo_buf.append(cls(unsaved=rs.unsaved, actions=actions))
    rs.redo_buf.clear()

  def undo(self, rs: ReplState) -> None:
    '''Swap unsaved with rs and apply the inverse of the actions.'''
    rs.unsaved, self.unsaved = self.unsaved, rs.unsaved
    action: Action
    for action in _invert_actions(self.actions):
      act(action, rs.cube)

  def redo(self, rs: ReplState) -> None:
    '''Swap unsaved with rs and reapply the actions.'''
    rs.unsaved, self.unsaved = self.unsaved, rs.unsaved
    action: Action
    for action in self.actions:
      act(action, rs.cube)

@dataclass
class ReplState:
  '''Mutable state threaded through REPL command execution.'''
  cube: Cube
  unsaved: bool = False
  last_file: str | None = None
  load_error: LoadError | None = None
  print_cube: bool = True
  undo_buf: list[UndoItem] = field(default_factory=list)
  redo_buf: list[UndoItem] = field(default_factory=list)

def are_you_sure(rs: ReplState) -> bool:
  '''Prompt for confirmation if the cube is unsaved.

  Returns True if the action should proceed: either the cube is
  already saved, or the user confirmed with (case-insensitive)
  "yes" or "y". Returns False otherwise.
  '''
  if not rs.unsaved:
    return True
  answer: str = input('The cube is not saved. Are you sure? ')
  if answer.strip().lower() in ('yes', 'y'):
    return True
  rs.print_cube = False
  return False
