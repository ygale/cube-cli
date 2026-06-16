'''REPL state and exit signal for the cube CLI.'''
from dataclasses import dataclass
from enum import Enum

from cube_model import Cube

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

@dataclass
class ReplState:
  '''Mutable state threaded through REPL command execution.'''
  cube: Cube
  unsaved: bool = False
  last_file: str | None = None
  load_error: LoadError | None = None
  print_cube: bool = True

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
