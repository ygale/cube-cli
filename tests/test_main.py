'''Tests for cube_cli.main argument parsing.'''
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
