'''Tests for cube_cli.main.'''
from io import StringIO
from unittest.mock import patch

import pytest

from cube_cli.main import main

def test_main_help_exits(capsys: pytest.CaptureFixture[str]) -> None:
  '''--help should exit 0 and print usage.'''
  with patch('sys.argv', ['cube', '--help']):
    with pytest.raises(SystemExit) as exc:
      main()
  assert exc.value.code == 0
  out: str = capsys.readouterr().out
  assert 'usage' in out.lower()

def test_main_version_exits(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''--version should exit 0 and print version.'''
  with patch('sys.argv', ['cube', '--version']):
    with pytest.raises(SystemExit) as exc:
      main()
  assert exc.value.code == 0
  out: str = capsys.readouterr().out
  assert 'cube' in out

def test_main_no_args_prints_cube(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''No args should print the cube then exit cleanly on q.'''
  with patch('sys.argv', ['cube']):
    with patch('sys.stdin', StringIO('q\n')):
      main()
  out: str = capsys.readouterr().out
  lines: list[str] = out.splitlines()
  assert len(lines) == 13

def test_main_file_arg_starts_repl(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''A file argument should start the repl (load is not yet implemented).'''
  with patch('sys.argv', ['cube', 'my.json']):
    with patch('sys.stdin', StringIO('q\n')):
      main()
  out: str = capsys.readouterr().out
  assert 'not yet implemented' in out
