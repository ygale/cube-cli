'''Entry point for the cube_cli application.'''
import argparse

from ._version import get_version
from .command import HELP_TEXT
from .repl import repl

def _make_parser() -> argparse.ArgumentParser:
  '''Build the argument parser for the cube command.'''
  parser: argparse.ArgumentParser = argparse.ArgumentParser(
    prog='cube',
    description=(
      'A textual CLI environment for manipulating a 3x3x3 cube\n'
      'and solving puzzles based on it.'
    ),
    epilog=HELP_TEXT,
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
  parser: argparse.ArgumentParser = _make_parser()
  args: argparse.Namespace = parser.parse_args()
  repl(args.file)
