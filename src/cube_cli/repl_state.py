'''REPL state and exit signal for the cube CLI.'''
from dataclasses import dataclass
from enum import Enum

from cube_model import Cube

class Exit(Enum):
  '''Singleton signal that the REPL should exit.'''
  EXIT = 'exit'

@dataclass
class ReplState:
  '''Mutable state threaded through REPL command execution.'''
  cube: Cube
