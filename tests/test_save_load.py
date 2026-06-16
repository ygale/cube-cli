'''Tests for save_load save and load functions.'''
import json
import os
from pathlib import Path

import pytest
from cube_model import Cube, shuffled, solved

from cube_cli.repl_state import LoadError
from cube_cli.save_load import load, save

def test_save_creates_file(tmp_path: Path) -> None:
  '''save creates a file at the given path.'''
  f: str = str(tmp_path / 'cube.json')
  assert save(solved(), f) is None
  assert os.path.exists(f)

def test_save_writes_valid_json(tmp_path: Path) -> None:
  '''save writes parseable JSON.'''
  f: str = str(tmp_path / 'cube.json')
  save(solved(), f)
  with open(f) as fh:
    data = json.load(fh)
  assert isinstance(data, dict)

def test_save_includes_version(tmp_path: Path) -> None:
  '''save includes a version field.'''
  f: str = str(tmp_path / 'cube.json')
  save(solved(), f)
  with open(f) as fh:
    data = json.load(fh)
  assert 'version' in data

def test_save_permission_denied(tmp_path: Path) -> None:
  '''save returns SaveError on permission denied.'''
  f: str = str(tmp_path / 'cube.json')
  os.makedirs(f)  # make it a directory so open for write fails
  result = save(solved(), f)
  assert isinstance(result, str)
  assert 'permission' in result or 'write' in result

def test_save_returns_none_on_success(tmp_path: Path) -> None:
  '''save returns None on success.'''
  f: str = str(tmp_path / 'cube.json')
  assert save(shuffled(), f) is None

def test_load_roundtrip_solved(tmp_path: Path) -> None:
  '''load recovers a saved solved cube.'''
  f: str = str(tmp_path / 'cube.json')
  cube: Cube = solved()
  save(cube, f)
  result = load(f, solved())
  assert isinstance(result, Cube), result
  assert cube == result

def test_load_roundtrip_shuffled(tmp_path: Path) -> None:
  '''load recovers ten saved shuffled cubes.'''
  f: str = str(tmp_path / 'cube.json')
  for _ in range(10):
    cube: Cube = shuffled()
    save(cube, f)
    result = load(f, solved())
    assert isinstance(result, Cube), result
    assert cube == result

def test_load_ignores_version(tmp_path: Path) -> None:
  '''load succeeds even when the version field differs.'''
  f: str = str(tmp_path / 'cube.json')
  cube: Cube = solved()
  save(cube, f)
  with open(f) as fh:
    data = json.load(fh)
  data['version'] = '0.0.0.ancient'
  with open(f, 'w') as fh:
    json.dump(data, fh)
  result = load(f, solved())
  assert isinstance(result, Cube), result

def test_load_file_not_found(tmp_path: Path) -> None:
  '''load returns LoadError when file does not exist.'''
  result = load(str(tmp_path / 'no_such_file.json'), solved())
  assert isinstance(result, LoadError)
  assert 'not found' in result.msg

@pytest.mark.skipif(os.getuid() == 0, reason='chmod has no effect as root')
def test_load_permission_denied(tmp_path: Path) -> None:
  '''load returns LoadError on permission denied.'''
  f: str = str(tmp_path / 'cube.json')
  save(solved(), f)
  os.chmod(f, 0o000)
  result = load(f, solved())
  os.chmod(f, 0o644)
  assert isinstance(result, LoadError)
  assert 'permission' in result.msg

def test_load_not_json(tmp_path: Path) -> None:
  '''load returns LoadError when file is not valid JSON.'''
  f: str = str(tmp_path / 'cube.json')
  with open(f, 'w') as fh:
    fh.write('this is not json')
  result = load(f, solved())
  assert isinstance(result, LoadError)
  assert 'JSON' in result.msg

def test_load_invalid_format(tmp_path: Path) -> None:
  '''load returns LoadError when JSON has invalid cube format.'''
  f: str = str(tmp_path / 'cube.json')
  with open(f, 'w') as fh:
    json.dump({'version': '1.0', 'front_color': 'g'}, fh)
  result = load(f, solved())
  assert isinstance(result, LoadError)
  assert 'format' in result.msg
