'''Tests for rubik_cli.main.'''
from rubik_cli.main import main


def test_main_runs() -> None:
    '''Smoke-test that main() executes without raising.'''
    main()
