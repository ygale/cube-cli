@python.md
@README.md

# cube-cli — Claude Project Notes

A Python CLI application that wraps `cube_model` to provide
command-line interaction with a cube puzzle model.

## cube command

- Use argparse to parse the cube command.
- README.md and cube --help have the same content. Only the format
  is different.
- The only options are --help and --version.
- If a file is specified, use it to load the initial cube state and
  set it as the last used file. Otherwise, use a solved cube as the
  initial cube state, and there is initially no last used file.

## REPL

- Use readline.
- If a file is specified on the cube command line, run a Load.
- REPL loop:
  - Print the cube.
  - Prompt: 'Command (? for help, q to quit): '
  - Parse the command.
  - If the parse succeeds, run the command. Otherwise, print
    'Invalid command'
  - Exit if the command requested it.
- quit, q, and ^d are recognized as a Quit command.
