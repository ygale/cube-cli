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
- Whitespace is ignored in REPL commands, except inside the
  filename when specified in a load or save command.
- If a filename is specified on the cube command line, load the cube
  from the file before starting the REPL.
- REPL loop:
  - Print the cube.
  - Prompt: 'Command (? for help, q to quit): '
  - Parse the command.
  - If the parse succeeds, run the command. Otherwise, print
    'Invalid command' and prompt again without printing the cube.
  - Exit if the command requested it.
- quit, q, and ^d are recognized as a Quit command.

## Save and Load

- The Save command only saves the cube itself, not any other
  application state.

### Filename

- A filename can optionally be provided in a save or load command.
  After the word 'load' or 'save' and then one or more whitespace
  characters, the filename is the first non-whitespace character and
  all following characters including whitespace.
  Whitespace following the filename at the end if the line is
  ignored.
- If no filename is specified for a save or load, the last previous
  filename used for a save or load is used.
- If there was no previous save or load, `cube.json` is used, in the
  current directory where the application was run.
- If a filename is specified on the command to run the application,
  it is used to load the cube before the REPL starts.
  If no filename is specified, the REPL starts with a solved cube.

### File format

- The cube is saved as a JSON object.
- The fields of the JSON object are the version of the application and the fields of the Cube object.
- Dict objects are stored as JSON objects.
- An EdgeSticker is represented as a string of length two, the color
  of the sticker and the color of its other sticker.
- A CornerSticker is represented as a string of length three, the
  color of the sticker and the color of its two other stickers in
  clockwise order.
- A color is represented by the lower-case first letter of its name.
- The load command ignores the version field for now. We will use
  it later if we change the file format in a future version of this
  application.

### Are you sure prompts

- When the cube is considered unsaved and the user enters a command
  that would completely discard the current cube, the user is
  presented with an "Are you sure?" prompt.
- If the user does not respond with case-insensitive yes or y,
  the command is cancelled and the cube is not redrawn.
- The cube is considered unsaved after a move that does not result
  in a uniform color on each of the sides of the cube.
- A shuffle command also causes the cube to be considered unsaved.
- A help command does not change the saved or unsaved status of the
  cube.
- Any other command causes the cube to be considered saved.
- Commands that completely discard the current cube are:
  - load
  - shuffle
  - solve
  - quit

### Errors during save and load

- If the save command fails, print
  'Could not save to {filename}: {msg}'
  where {msg} is a short simple one-line human-readable message
  with whatever information we have about what went wrong. Prompt
  again without printing the cube.
- If the load command fails, print
  'Could not load from {filename}: {msg}'
  where {msg} is a short simple one-line human-readable message
  with whatever information we have about what went wrong. Prompt
  again without printing the cube.
- If initial loading fails when a filename is specified on the cube
  command, print
  'Could not load from {filename}: {msg}'
  after printing the fallback solved cube and before the first
  prompt, so that the user will notice it.
