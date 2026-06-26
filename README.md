# cube-cli

A textual cli environment for manipulating a 3x3x3 cube and solving
puzzles based on it.

## Usage

    cube [options] [file]

`[file]` is a saved cube from a previous session. If not specified,
the cube is initialized to its solved state.

## Options

`--help`

`--version`

## Commands

Before you enter a command, the current state of the cube is printed
in a textual format.

**\<moves>**

A sequence of moves in standard cube move syntax.
Case-insensitive. To specify a wide move, use a 'w' suffix.

**^\<moves>**

A sequence of moves in standard cube move syntax.
Case-sensitive. To specify a wide move, use either a lower-case face
letter or a 'w' suffix.

**solve**

Return the cube to its initial solved position.

**shuffle**

Randomize the position of the cube.

**undo**

Undo the last previous command.

**redo**

If the last previous command was an undo, reverse its effect.

**save [file]**

Save the cube to a file. If `[file]` is not specified, save
to the last file used for a load or save, or to cube.json in the
current directory.

**load [file]**

Load a saved cube. If `[file]` is not specified, load from
the last file used for a load or save, or to cube.json in the
current directory.

**help, ?**

Print this command reference.

**quit, q**

Exit cube.
