'''REPL loop and command parser for the cube CLI.'''
import readline

from cube_model import Cube, solved
from typing import cast

from .command import Command, Quit, Tabbable, all_commands
from .print import print_cube
from .repl_state import Alias, Exit, LoadError, ReplState
from .save_load import SaveError, load

# All tab completion candidates.
# Use cast to work around mypy bug.
_COMPLETIONS: list[str] = sorted(a.name
  for c in all_commands if issubclass(c, Tabbable)
  for a in cast(Tabbable, c).aliases)

# Do not tab complete if it might be a Move.
# Use cast to work around mypy bug.
_NON_COMPLETIONS: set[str] = {a.name[:a.min_chars - 1]
  for c in all_commands if issubclass(c, Tabbable)
  for a in cast(Tabbable, c).aliases if a.min_chars > 1}

# Cached tab completion candidates for a specific input text
_matches: list[str] = []

def _complete(text: str, state: int) -> str | None:
  '''Readline completer for REPL commands.

  Matches text against _COMPLETIONS case-insensitively, always
  returning lower-case completions. Returns no completions at all
  if text is a prefix of any entry in _NON_COMPLETIONS.
  '''
  global _matches
  text_lower: str = text.lower()
  if state == 0:
    if any(nc.startswith(text_lower) for nc in _NON_COMPLETIONS):
      _matches = []
    else:
      _matches = [c for c in _COMPLETIONS if c.startswith(text_lower)]
  if state < len(_matches):
    return _matches[state]
  return None

def _setup_readline() -> None:
  '''Register the REPL's tab completer with readline.'''
  readline.set_completer(_complete)
  if readline.__doc__ is not None and 'libedit' in readline.__doc__:
    readline.parse_and_bind('bind ^I rl_complete')
  else:
    readline.parse_and_bind('tab: complete')

def parse_command(inp: str) -> Command | None:
  '''Try each command type in order; return the first match.'''
  cmd_type: type[Command]
  for cmd_type in all_commands:
    cmd: Command | None = cmd_type.parse(inp)
    if cmd is not None:
      return cmd
  return None

def _initial_state(filename: str | None) -> ReplState:
  '''Build the initial REPL state, loading filename if given.

  If the load fails, report the error.
  '''
  if filename is None:
    return ReplState(cube=solved())
  result: Cube | LoadError = load(filename, solved())
  if isinstance(result, Cube):
    return ReplState(cube=result, last_file=filename)
  return ReplState(cube=solved(), load_error=result)

def repl(filename: str | None) -> None:
  '''Run the interactive REPL.

  If filename is given, load it as the initial cube state. If the
  load fails, fall back to a solved cube and report the error.
  '''
  _setup_readline()
  cmd: Command | None
  rs: ReplState = _initial_state(filename)
  while True:
    if rs.print_cube:
      line: str
      for line in print_cube(rs.cube):
        print(line)
    else:
      rs.print_cube = True # reset for next time
    if rs.load_error is not None:
      fn: str = rs.load_error.filename
      msg: str = rs.load_error.msg
      print(f'Could not load from {fn}: {msg}')
      rs.load_error = None # reset for next time
    try:
      inp: str = input(
        'Command (? for help, q to quit): ').strip()
    except EOFError:
      print()
      cmd = Quit()
    else:
      cmd = parse_command(inp)
      if cmd is None:
        print('Invalid command')
        rs.print_cube = False
        continue
    result: Exit | None = cmd.run(rs)
    if result is Exit.EXIT:
      break
