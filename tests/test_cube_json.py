'''Tests for cube_json serialisation and deserialisation.'''
import json
from typing import Any

from cube_model import Cube, CornerSticker, EdgeSticker, shuffled, solved
from cube_model.reachable import reachable

from cube_cli.cube_json import (
  CubeJSON,
  JSONError,
  any_to_json,
  cube_to_json,
  json_to_cube,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _roundtrip(cube: Cube) -> Cube | JSONError:
  '''Serialise then deserialise a cube, reusing a fresh solved initial.'''
  return json_to_cube(cube_to_json(cube), solved())

# ---------------------------------------------------------------------------
# cube_to_json structure
# ---------------------------------------------------------------------------

def test_cube_to_json_keys() -> None:
  '''cube_to_json returns the expected top-level keys.'''
  cj: CubeJSON = cube_to_json(solved())
  assert 'front_color' in cj
  assert 'top_color' in cj
  assert 'home' in cj
  assert 'next_edge' in cj
  assert 'next_corner' in cj

def test_cube_to_json_next_edge_count() -> None:
  '''next_edge has 24 entries (one per directed corner sticker).'''
  cj: CubeJSON = cube_to_json(solved())
  assert isinstance(cj['next_edge'], dict)
  assert len(cj['next_edge']) == 24

def test_cube_to_json_next_corner_count() -> None:
  '''next_corner has 24 entries (one per directed edge sticker).'''
  cj: CubeJSON = cube_to_json(solved())
  assert isinstance(cj['next_corner'], dict)
  assert len(cj['next_corner']) == 24

def test_cube_to_json_corner_key_lengths() -> None:
  '''next_edge keys are 3-char strings.'''
  cj: CubeJSON = cube_to_json(solved())
  ne = cj['next_edge']
  assert isinstance(ne, dict)
  for k in ne:
    assert len(k) == 3

def test_cube_to_json_edge_value_lengths() -> None:
  '''next_edge values are 2-char strings.'''
  cj: CubeJSON = cube_to_json(solved())
  ne = cj['next_edge']
  assert isinstance(ne, dict)
  for v in ne.values():
    assert len(v) == 2

def test_cube_to_json_edge_key_lengths() -> None:
  '''next_corner keys are 2-char strings.'''
  cj: CubeJSON = cube_to_json(solved())
  nc = cj['next_corner']
  assert isinstance(nc, dict)
  for k in nc:
    assert len(k) == 2

def test_cube_to_json_corner_value_lengths() -> None:
  '''next_corner values are 3-char strings.'''
  cj: CubeJSON = cube_to_json(solved())
  nc = cj['next_corner']
  assert isinstance(nc, dict)
  for v in nc.values():
    assert len(v) == 3

def test_cube_to_json_home_length() -> None:
  '''home is a 3-char string.'''
  cj: CubeJSON = cube_to_json(solved())
  assert isinstance(cj['home'], str)
  assert len(cj['home']) == 3

def test_cube_to_json_valid_color_chars() -> None:
  '''All color characters are valid.'''
  valid: set[str] = set('wyrobg')
  cj: CubeJSON = cube_to_json(shuffled())
  home = cj['home']
  assert isinstance(home, str)
  for ch in home:
    assert ch in valid
  ne = cj['next_edge']
  assert isinstance(ne, dict)
  for k, v in ne.items():
    for ch in k + v:
      assert ch in valid, f'unexpected char {ch!r}'
  nc = cj['next_corner']
  assert isinstance(nc, dict)
  for k, v in nc.items():
    for ch in k + v:
      assert ch in valid, f'unexpected char {ch!r}'

def test_cube_to_json_is_json_serialisable() -> None:
  '''cube_to_json output survives json.dumps/loads.'''
  cj: CubeJSON = cube_to_json(shuffled())
  raw: str = json.dumps(cj)
  back: Any = json.loads(raw)
  assert isinstance(back, dict)

# ---------------------------------------------------------------------------
# Round-trip: solved cube
# ---------------------------------------------------------------------------

def test_roundtrip_solved() -> None:
  '''A solved cube round-trips correctly.'''
  cube: Cube = solved()
  result = _roundtrip(cube)
  assert isinstance(result, Cube), result
  assert cube == result

# ---------------------------------------------------------------------------
# Round-trip: shuffled cubes
# ---------------------------------------------------------------------------

def test_roundtrip_shuffled_10() -> None:
  '''Ten random shuffled cubes round-trip correctly.'''
  for _ in range(10):
    cube: Cube = shuffled()
    result = _roundtrip(cube)
    assert isinstance(result, Cube), result
    assert cube == result

def test_roundtrip_preserves_reachability() -> None:
  '''Round-tripped shuffled cubes remain reachable.'''
  for _ in range(5):
    cube: Cube = shuffled()
    result = _roundtrip(cube)
    assert isinstance(result, Cube), result
    assert reachable(result)

def test_roundtrip_via_json_string() -> None:
  '''Round-trip through json.dumps/loads + any_to_json works.'''
  cube: Cube = shuffled()
  raw: str = json.dumps(cube_to_json(cube))
  loaded: Any = json.loads(raw)
  as_cj = any_to_json(loaded)
  assert isinstance(as_cj, dict), as_cj
  result = json_to_cube(as_cj, solved())
  assert isinstance(result, Cube), result
  assert cube == result

# ---------------------------------------------------------------------------
# json_to_cube error cases
# ---------------------------------------------------------------------------

def test_json_to_cube_missing_front_color() -> None:
  cj: dict[str, Any] = dict(cube_to_json(solved()))
  del cj['front_color']
  assert not isinstance(json_to_cube(cj, solved()), Cube)

def test_json_to_cube_bad_front_color() -> None:
  cj: dict[str, Any] = dict(cube_to_json(solved()))
  cj['front_color'] = 'z'
  assert not isinstance(json_to_cube(cj, solved()), Cube)

def test_json_to_cube_missing_top_color() -> None:
  cj: dict[str, Any] = dict(cube_to_json(solved()))
  del cj['top_color']
  assert not isinstance(json_to_cube(cj, solved()), Cube)

def test_json_to_cube_missing_home() -> None:
  cj: dict[str, Any] = dict(cube_to_json(solved()))
  del cj['home']
  assert not isinstance(json_to_cube(cj, solved()), Cube)

def test_json_to_cube_missing_next_edge() -> None:
  cj: dict[str, Any] = dict(cube_to_json(solved()))
  del cj['next_edge']
  assert not isinstance(json_to_cube(cj, solved()), Cube)

def test_json_to_cube_missing_next_corner() -> None:
  cj: dict[str, Any] = dict(cube_to_json(solved()))
  del cj['next_corner']
  assert not isinstance(json_to_cube(cj, solved()), Cube)

def test_json_to_cube_next_edge_not_dict() -> None:
  cj: dict[str, Any] = dict(cube_to_json(solved()))
  cj['next_edge'] = 'oops'
  assert not isinstance(json_to_cube(cj, solved()), Cube)

def test_json_to_cube_next_corner_not_dict() -> None:
  cj: dict[str, Any] = dict(cube_to_json(solved()))
  cj['next_corner'] = 42
  assert not isinstance(json_to_cube(cj, solved()), Cube)

# ---------------------------------------------------------------------------
# any_to_json
# ---------------------------------------------------------------------------

def test_any_to_json_accepts_valid() -> None:
  result = any_to_json(cube_to_json(solved()))
  assert isinstance(result, dict), result

def test_any_to_json_rejects_non_dict() -> None:
  assert not isinstance(any_to_json('hello'), dict)

def test_any_to_json_rejects_list() -> None:
  assert not isinstance(any_to_json([1, 2, 3]), dict)

def test_any_to_json_rejects_nested_non_string_value() -> None:
  assert not isinstance(any_to_json({'next_edge': {'gwr': 42}}), dict)

def test_any_to_json_rejects_non_string_top_value() -> None:
  assert not isinstance(any_to_json({'front_color': 123}), dict)

def test_any_to_json_roundtrip_via_json_string() -> None:
  cube: Cube = shuffled()
  raw: str = json.dumps(cube_to_json(cube))
  loaded: Any = json.loads(raw)
  as_cj = any_to_json(loaded)
  assert isinstance(as_cj, dict)
  result = json_to_cube(as_cj, solved())
  assert isinstance(result, Cube)
  assert cube == result
