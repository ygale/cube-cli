'''JSON serialisation and deserialisation for the Cube model.'''
from typing import Any, NewType, cast

from cube_model import Color, CornerSticker, Cube, EdgeSticker

# JSON alias for a serialised cube object
type CubeJSON = dict[str, str | dict[str, str]]

# JSONError is a NewType of str. At runtime it is just str; use
# isinstance(result, Cube) to distinguish success from error.
JSONError = NewType('JSONError', str)

def _color_ch(c: Color) -> str:
  return c.name[0].lower()

def _corner_str(cs: CornerSticker) -> str:
  '''Encode a CornerSticker as a 3-char string.'''
  return ''.join([
    _color_ch(cs.color),
    _color_ch(cs.other.color),
    _color_ch(cs.other.other.color),
  ])

def _edge_str(es: EdgeSticker) -> str:
  '''Encode an EdgeSticker as a 2-char string.'''
  return ''.join([_color_ch(es.color), _color_ch(es.other.color)])

def cube_to_json(cube: Cube) -> CubeJSON:
  '''Serialise a Cube to a CubeJSON dict.'''
  return {
    'front_color': _color_ch(cube.front_color),
    'top_color': _color_ch(cube.top_color),
    'home': _corner_str(cube.home),
    'next_edge': {
      _corner_str(cs): _edge_str(es)
      for cs, es in cube.next_edge.items()
    },
    'next_corner': {
      _edge_str(es): _corner_str(cs)
      for es, cs in cube.next_corner.items()
    },
  }

def json_to_cube(cube_json: CubeJSON, initial: Cube) -> Cube | JSONError:
  '''Deserialise a CubeJSON dict into a Cube, reusing stickers from initial.

  Assumes well-formed input (i.e. produced by cube_to_json). Returns a
  JSONError string on failure. Use isinstance(result, Cube) to distinguish
  success from error at runtime.
  '''
  ch_to_color: dict[str, Color] = {_color_ch(c): c for c in Color}
  corners: dict[str, CornerSticker] = {
    _corner_str(cs): cs for cs in initial.next_edge
  }
  edges: dict[str, EdgeSticker] = {
    _edge_str(es): es for es in initial.next_corner
  }
  try:
    return Cube(
      home=corners[cast(str, cube_json['home'])],
      front_color=ch_to_color[cast(str, cube_json['front_color'])],
      top_color=ch_to_color[cast(str, cube_json['top_color'])],
      next_edge={
        corners[k]: edges[v]
        for k, v in cast(dict[str, str], cube_json['next_edge']).items()
      },
      next_corner={
        edges[k]: corners[v]
        for k, v in cast(dict[str, str], cube_json['next_corner']).items()
      },
    )
  except (KeyError, AttributeError, TypeError) as e:
    return JSONError(str(e))

def any_to_json(value: Any) -> CubeJSON | JSONError:
  '''Validate that an arbitrary parsed JSON value is a valid CubeJSON.

  Returns a JSONError (str at runtime) on failure. Use isinstance(result,
  dict) to distinguish success from error.
  '''
  if not isinstance(value, dict):
    return JSONError('expected a JSON object at the top level')
  result: CubeJSON = {}
  k: object
  v: object
  for k, v in value.items():
    if not isinstance(k, str):
      return JSONError(f'non-string key: {k!r}')
    if isinstance(v, str):
      result[k] = v
    elif isinstance(v, dict):
      inner: dict[str, str] = {}
      ik: object
      iv: object
      for ik, iv in v.items():
        if not isinstance(ik, str) or not isinstance(iv, str):
          return JSONError(f'non-string entry in nested object {k!r}')
        inner[ik] = iv
      result[k] = inner
    else:
      return JSONError(
        f'value for {k!r} must be str or object, got {type(v).__name__}'
      )
  return result
