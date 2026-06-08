'''Package version string.'''
from importlib.metadata import PackageNotFoundError, version

def get_version() -> str:
  '''Return the installed package version, or a dev fallback.'''
  try:
    return version('cube-cli')
  except PackageNotFoundError:
    return '0.0.0.dev0'
