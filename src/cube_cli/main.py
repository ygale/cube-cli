'''Entry point for the cube_cli application.'''
import argparse
import sys

from cube_model import Cube, solved

from ._version import get_version
from .print import print_cube

_EPILOG: str = '''\
Commands:

  Before you enter a command, the current state of the cube is
  printed in a textual format.

  <moves>   A sequence of moves in standard cube move syntax.
            Case-insensitive. To specify a wide move, use a
            'w' suffix.

  ^<moves>  A sequence of moves in standard cube move syntax.
            Case-sensitive. To specify a wide move, use either
            a lower-case face letter or a 'w' suffix.

  solve     Return the cube to its initial solved position.

  shuffle   Randomize the position of the cube.

  undo      Undo the last previous command.

  redo      If the last previous command was an undo, reverse
            its effect.

  save [file]
            Save the cube to a file. If [file] is not
            specified, save to the last file used for a load
            or save, or to cube.json in the current directory.

  load [file]
            Load a saved cube. If [file] is not specified,
            load from the last file used for a load or save,
            or to cube.json in the current directory.

  quit      Exit cube.'''

def _make_parser() -> argparse.ArgumentParser:
  '''Build the argument parser for the cube command.'''
  parser: argparse.ArgumentParser = argparse.ArgumentParser(
    prog='cube',
    description=(
      'A textual CLI environment for manipulating a 3x3x3 cube\n'
      'and solving puzzles based on it.'
    ),
    epilog=_EPILOG,
    formatter_class=argparse.RawDescriptionHelpFormatter,
  )
  parser.add_argument(
    '--version',
    action='version',
    version=f'cube {get_version()}',
  )
  parser.add_argument(
    'file',
    nargs='?',
    metavar='file',
    help=(
      'Saved cube from a previous session. '
      'If not specified, the cube starts solved.'
    ),
  )
  return parser

def main() -> None:
  '''Run the cube CLI.'''
  ref: Cube = solved()
  parser: argparse.ArgumentParser = _make_parser()
  args: argparse.Namespace = parser.parse_args()
  last_file: str | None = args.file
  if last_file is not None:
    print('cube: file loading not yet implemented', file=sys.stderr)
    sys.exit(1)
  cube: Cube = solved(initial=ref)
  line: str
  for line in print_cube(cube):
    print(line)
