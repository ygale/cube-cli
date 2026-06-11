'''REPL loop and command parser for the cube CLI.'''
import readline

from cube_model import Cube, solved

from .command import Command, Load, Quit, all_commands
from .print import print_cube
from .repl_state import Exit, ReplState

def parse_command(inp: str) -> Command | None:
  '''Try each command type in order; return the first match.'''
  cmd_type: type[Command]
  for cmd_type in all_commands:
    cmd: Command | None = cmd_type.parse(inp)
    if cmd is not None:
      return cmd
  return None

def repl(filename: str | None) -> None:
  '''Run the interactive REPL.

  If filename is given, run a Load command as the first command.
  Otherwise start from a solved cube.
  '''
  cube: Cube = solved()
  rs: ReplState = ReplState(cube=cube)
  if filename is not None:
    Load(filename=filename).run(rs)
  print_cube_now: bool = True
  while True:
    if print_cube_now:
      line: str
      for line in print_cube(rs.cube):
        print(line)
    print_cube_now = True
    try:
      inp: str = input('Command (? for help, q to quit): ')
    except EOFError:
      Quit().run(rs)
      break
    if not inp.strip():
      print_cube_now = False
      continue
    cmd: Command | None = parse_command(inp)
    if cmd is None:
      print('Invalid command')
      print_cube_now = False
      continue
    result: Exit | None = cmd.run(rs)
    if result is Exit.EXIT:
      break
