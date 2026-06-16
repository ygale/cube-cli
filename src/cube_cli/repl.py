'''REPL loop and command parser for the cube CLI.'''
import readline

from cube_model import Cube, solved

from .command import Command, Quit, all_commands
from .print import print_cube
from .repl_state import Exit, LoadError, ReplState
from .save_load import SaveError, load

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
