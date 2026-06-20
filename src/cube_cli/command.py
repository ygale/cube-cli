'''Abstract Command base and all concrete REPL command types.'''
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self

from cube_model import Color, Cube, Side, shuffled, solved
from cube_model.action import Action, ParseError, act, parse_actions
from cube_model.navigation import all_colors, side_color

from .repl_state import (
  Exit,
  LoadError,
  ReplState,
  UndoCube,
  UndoItem,
  UndoMove,
  are_you_sure,
)
from .save_load import SaveError, load, save

DEFAULT_FILE: str = 'cube.json'

_LOAD_RE: re.Pattern[str] = re.compile(r'^load(?:\s+(\S.*?))?$', re.IGNORECASE)
_SAVE_RE: re.Pattern[str] = re.compile(r'^save(?:\s+(\S.*?))?$', re.IGNORECASE)

def _resolve_file(rs: ReplState, filename: str | None) -> str:
  '''Resolve the filename to use for a save or load.

  Uses filename if given, otherwise the last used file, otherwise
  the default file.
  '''
  if filename is not None:
    return filename
  if rs.last_file is not None:
    return rs.last_file
  return DEFAULT_FILE

def _is_solved(cube: Cube) -> bool:
  '''Return True if every side shows a single uniform color.'''
  colors: dict[Side, list[Color]] = all_colors(cube)
  side: Side
  for side in colors:
    center: Color = side_color(cube, side)
    if any(c != center for c in colors[side]):
      return False
  return True

@dataclass
class Command(ABC):
  '''Abstract base for all REPL commands.'''

  @classmethod
  @abstractmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Parse a raw input string; return an instance if it matches.
    Assumes that strip() has already been applied.'''

  @abstractmethod
  def run(self, rs: ReplState) -> Exit | None:
    '''Execute the command against the given REPL state.'''

@dataclass
class Shuffle(Command):
  '''Randomize the cube.'''

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return a Shuffle if cmd is "shuffle".'''
    if cmd == 'shuffle':
      return cls()
    return None

  def run(self, rs: ReplState) -> Exit | None:
    '''Replace the cube with a shuffled copy, if confirmed.'''
    if not are_you_sure(rs):
      return None
    UndoCube.push(rs)
    rs.cube = shuffled(initial=rs.cube)
    rs.unsaved = True
    return None

@dataclass
class Solve(Command):
  '''Return the cube to its solved state.'''

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return a Solve if cmd is "solve".'''
    if cmd == 'solve':
      return cls()
    return None

  def run(self, rs: ReplState) -> Exit | None:
    '''Replace the cube with a solved copy, if confirmed.'''
    if not are_you_sure(rs):
      return None
    UndoCube.push(rs)
    rs.cube = solved(initial=rs.cube)
    rs.unsaved = False
    return None

@dataclass
class Load(Command):
  '''Load cube state from a file.'''
  filename: str | None

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return a Load if cmd starts with "load".

    The filename, if any, runs from the first non-whitespace
    character after "load" to the end of the line, with only
    trailing whitespace stripped.
    '''
    m: re.Match[str] | None = _LOAD_RE.match(cmd)
    if m is None:
      return None
    return cls(filename=m.group(1))

  def run(self, rs: ReplState) -> Exit | None:
    '''Load cube state from file, if confirmed.'''
    if not are_you_sure(rs):
      return None
    target: str = _resolve_file(rs, self.filename)
    result: Cube | LoadError = load(target, rs.cube)
    if not isinstance(result, Cube):
      rs.load_error = result
      rs.print_cube = False
      return None
    UndoCube.push(rs)
    rs.cube = result
    rs.last_file = target
    rs.unsaved = False
    return None

@dataclass
class Save(Command):
  '''Save cube state to a file.'''
  filename: str | None

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return a Save if cmd starts with "save".

    The filename, if any, runs from the first non-whitespace
    character after "save" to the end of the line, with only
    trailing whitespace stripped.
    '''
    m: re.Match[str] | None = _SAVE_RE.match(cmd)
    if m is None:
      return None
    return cls(filename=m.group(1))

  def run(self, rs: ReplState) -> Exit | None:
    '''Save cube state to file.'''
    rs.print_cube = False
    target: str = _resolve_file(rs, self.filename)
    err: SaveError | None = save(rs.cube, target)
    if err is not None:
      print(f'Could not save to {target}: {err}')
      return None
    print(f'Cube saved to {target}')
    rs.last_file = target
    rs.unsaved = False
    return None

@dataclass
class Undo(Command):
  '''Undo the last command.'''

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return an Undo if cmd is "undo".'''
    if cmd == 'undo':
      return cls()
    return None

  def run(self, rs: ReplState) -> Exit | None:
    '''Pop and apply the last undo item, if any.

    If the undo buffer is empty, print 'Nothing to undo' instead
    and do not print the cube.
    '''
    if not rs.undo_buf:
      print('Nothing to undo')
      rs.print_cube = False
      return None
    item: UndoItem = rs.undo_buf.pop()
    item.undo(rs)
    rs.redo_buf.append(item)
    return None

@dataclass
class Redo(Command):
  '''Redo the last undone command.'''

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return a Redo if cmd is "redo".'''
    if cmd == 'redo':
      return cls()
    return None

  def run(self, rs: ReplState) -> Exit | None:
    '''Pop and apply the last redo item, if any.

    If the redo buffer is empty, print 'Nothing to redo' instead
    and do not print the cube.
    '''
    if not rs.redo_buf:
      print('Nothing to redo')
      rs.print_cube = False
      return None
    item: UndoItem = rs.redo_buf.pop()
    item.redo(rs)
    rs.undo_buf.append(item)
    return None

@dataclass
class Quit(Command):
  '''Exit the REPL.'''

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return a Quit if cmd is "quit" or "q".'''
    if cmd in ('quit', 'q'):
      return cls()
    return None

  def run(self, rs: ReplState) -> Exit | None:
    '''Signal the REPL to exit, if confirmed.'''
    if not are_you_sure(rs):
      return None
    return Exit.EXIT

# Command reference text, shared with the --help epilog.
HELP_TEXT: str = '''\
Commands:

  Before you enter a command, the current state of the cube is
  printed in a textual format.

  <moves>     A sequence of moves in standard cube move syntax.
              Case-insensitive. To specify a wide move, use a
              'w' suffix.

  ^<moves>    A sequence of moves in standard cube move syntax.
              Case-sensitive. To specify a wide move, use either
              a lower-case face letter or a 'w' suffix.

  solve       Return the cube to its initial solved position.

  shuffle     Randomize the position of the cube.

  undo        Undo the last previous command.

  redo        If the last previous command was an undo, reverse
              its effect.

  save [file] Save the cube to a file. If [file] is not
              specified, save to the last file used for a load
              or save, or to cube.json in the current directory.

  load [file] Load a saved cube. If [file] is not specified,
              load from the last file used for a load or save,
              or to cube.json in the current directory.

  help, ?     Print this command reference.

  quit, q     Exit cube.'''

@dataclass
class Help(Command):
  '''Print a summary of available commands.'''

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return a Help if cmd is "help" or "?".'''
    if cmd in ('help', '?'):
      return cls()
    return None

  def run(self, rs: ReplState) -> Exit | None:
    '''Print the command reference to stdout.'''
    print(HELP_TEXT)
    return None

@dataclass
class Noop(Command):
  '''Do nothing.'''

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return a Noop if cmd is the empty string.'''
    if not cmd:
      return cls()
    return None

  def run(self, rs: ReplState) -> Exit | None:
    '''Do nothing. Not even print the cube.'''
    rs.print_cube = False
    return None

@dataclass
class Move(Command):
  '''Apply a parsed sequence of actions to the cube.'''
  actions: list[Action]

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Parse a move sequence, with optional "^" prefix for case-sensitivity.

    A leading "^" enables case-sensitive parsing. Without it, parsing
    is case-insensitive. Returns None if the input is empty or cannot
    be parsed as a valid move sequence.
    '''
    if cmd.startswith('^'):
      tail: str = cmd[1:]
      if not tail:
        return None
      ci: bool = False
    else:
      tail = cmd
      ci = True
    try:
      actions: list[Action] = parse_actions(tail, ci=ci)
    except ParseError:
      return None
    if not actions:
      return None
    return cls(actions=actions)

  def run(self, rs: ReplState) -> Exit | None:
    '''Apply each action in sequence to the cube.'''
    UndoMove.push(rs, self.actions)
    action: Action
    for action in self.actions:
      act(action, rs.cube)
    rs.unsaved = not _is_solved(rs.cube)
    return None

# All command types in parse-priority order.
all_commands: list[type[Command]] = [
  Shuffle,
  Solve,
  Load,
  Save,
  Undo,
  Redo,
  Quit,
  Help,
  Noop,
  Move,
]
