'''Abstract Command base and all concrete REPL command types.'''
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self

from cube_model import shuffled, solved
from cube_model.action import Action, ParseError, act, parse_actions

from .repl_state import Exit, ReplState

@dataclass
class Command(ABC):
  '''Abstract base for all REPL commands.'''

  @classmethod
  @abstractmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Parse a raw input string; return an instance if it matches.'''

  @abstractmethod
  def run(self, rs: ReplState) -> Exit | None:
    '''Execute the command against the given REPL state.'''

@dataclass
class Shuffle(Command):
  '''Randomize the cube.'''

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return a Shuffle if cmd is "shuffle".'''
    if cmd.strip().lower() == 'shuffle':
      return cls()
    return None

  def run(self, rs: ReplState) -> Exit | None:
    '''Replace the cube with a shuffled copy.'''
    rs.cube = shuffled(initial=rs.cube)
    return None

@dataclass
class Solve(Command):
  '''Return the cube to its solved state.'''

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return a Solve if cmd is "solve".'''
    if cmd.strip().lower() == 'solve':
      return cls()
    return None

  def run(self, rs: ReplState) -> Exit | None:
    '''Replace the cube with a solved copy.'''
    rs.cube = solved(initial=rs.cube)
    return None

@dataclass
class Load(Command):
  '''Load cube state from a file.'''
  filename: str | None

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return a Load if cmd starts with "load".'''
    parts: list[str] = cmd.strip().split(maxsplit=1)
    if not parts or parts[0].lower() != 'load':
      return None
    filename: str | None = parts[1] if len(parts) > 1 else None
    return cls(filename=filename)

  def run(self, rs: ReplState) -> Exit | None:
    '''Load cube state from file (not yet implemented).'''
    print('cube: load not yet implemented')
    return None

@dataclass
class Save(Command):
  '''Save cube state to a file.'''
  filename: str | None

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return a Save if cmd starts with "save".'''
    parts: list[str] = cmd.strip().split(maxsplit=1)
    if not parts or parts[0].lower() != 'save':
      return None
    filename: str | None = parts[1] if len(parts) > 1 else None
    return cls(filename=filename)

  def run(self, rs: ReplState) -> Exit | None:
    '''Save cube state to file (not yet implemented).'''
    print('cube: save not yet implemented')
    return None

@dataclass
class Undo(Command):
  '''Undo the last command.'''

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return an Undo if cmd is "undo".'''
    if cmd.strip().lower() == 'undo':
      return cls()
    return None

  def run(self, rs: ReplState) -> Exit | None:
    '''Undo the last command (not yet implemented).'''
    print('cube: undo not yet implemented')
    return None

@dataclass
class Redo(Command):
  '''Redo the last undone command.'''

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return a Redo if cmd is "redo".'''
    if cmd.strip().lower() == 'redo':
      return cls()
    return None

  def run(self, rs: ReplState) -> Exit | None:
    '''Redo the last undone command (not yet implemented).'''
    print('cube: redo not yet implemented')
    return None

@dataclass
class Quit(Command):
  '''Exit the REPL.'''

  @classmethod
  def parse(cls, cmd: str) -> Self | None:
    '''Return a Quit if cmd is "quit" or "q".'''
    if cmd.strip().lower() in ('quit', 'q'):
      return cls()
    return None

  def run(self, rs: ReplState) -> Exit | None:
    '''Signal the REPL to exit.'''
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
    if cmd.strip().lower() in ('help', '?'):
      return cls()
    return None

  def run(self, rs: ReplState) -> Exit | None:
    '''Print the command reference to stdout.'''
    print(HELP_TEXT)
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
    stripped: str = cmd.strip()
    if not stripped:
      return None
    if stripped.startswith('^'):
      tail: str = stripped[1:]
      if not tail:
        return None
      ci: bool = False
    else:
      tail = stripped
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
    action: Action
    for action in self.actions:
      act(action, rs.cube)
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
  Move,
]
