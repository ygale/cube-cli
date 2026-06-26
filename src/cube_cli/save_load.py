'''Save and load cube state to and from JSON files.'''
import json
from typing import NewType

from cube_model import Cube

from ._version import get_version
from .cube_json import (CubeJSON, JSONError, any_to_json,
  cube_to_json, json_to_cube)
from .repl_state import LoadError

# The error message resulting from a failed save of the cube to
# a file.
SaveError = NewType('SaveError', str)

def save(cube: Cube, filename: str) -> SaveError | None:
  '''Serialise cube to a JSON file, including the current version.

  Returns a SaveError on failure, None on success.
  '''
  cj: CubeJSON = cube_to_json(cube)
  cj['version'] = get_version()
  try:
    with open(filename, 'w') as f:
      json.dump(cj, f, separators=(',',':'))
  except PermissionError:
    return SaveError('permission denied')
  except OSError:
    return SaveError('could not write file')
  return None

def load(filename: str, initial: Cube) -> Cube | LoadError:
  '''Deserialise a Cube from a JSON file, ignoring the version field.

  Returns a LoadError on failure. Use isinstance(result, Cube) to
  distinguish success from error at runtime.
  '''
  try:
    with open(filename) as f:
      raw = json.load(f)
  except FileNotFoundError:
    return LoadError(filename, 'file not found')
  except PermissionError:
    return LoadError(filename, 'permission denied')
  except OSError:
    return LoadError(filename, 'could not read file')
  except json.JSONDecodeError:
    return LoadError(filename, 'not a valid JSON file')
  cj: CubeJSON | JSONError = any_to_json(raw)
  if not isinstance(cj, dict):
    return LoadError(filename, 'JSON has invalid format')
  result: Cube | JSONError = json_to_cube(cj, initial)
  if not isinstance(result, Cube):
    return LoadError(filename, 'JSON has invalid format')
  return result
