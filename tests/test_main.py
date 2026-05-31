'''Tests for cube_cli.main.'''
from cube_cli.main import main

def test_main_runs() -> None:
  '''Smoke-test that main() executes without raising.'''
  main()
