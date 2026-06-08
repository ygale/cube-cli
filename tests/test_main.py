'''Tests for cube_cli.main.'''
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
  '''No args should print 11-line cube and return normally.'''
  with patch('sys.argv', ['cube']):
    main()
  out: str = capsys.readouterr().out
  lines: list[str] = out.splitlines()
  assert len(lines) == 11

def test_main_file_arg_exits(
  capsys: pytest.CaptureFixture[str],
) -> None:
  '''A file argument should exit non-zero with not-implemented msg.'''
  with patch('sys.argv', ['cube', 'my.json']):
    with pytest.raises(SystemExit) as exc:
      main()
  assert exc.value.code != 0
  err: str = capsys.readouterr().err
  assert 'not yet implemented' in err
