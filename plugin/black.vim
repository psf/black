" black.vim
" Author: Łukasz Langa
" Created: Mon Mar 26 23:27:53 2018 -0700
" Requires: Vim Ver7.0+
" Version:  1.1
"
" Documentation:
"   This plugin formats Python files.
"
" History:
"  1.0:
"    - initial version
"  1.1:
"    - restore cursor/window position after formatting

if v:version < 700 || !has('python3')
    func! __BLACK_MISSING()
        echo "The black.vim plugin requires vim7.0+ with Python 3.6 support."
    endfunc
    command! Black :call __BLACK_MISSING()
    command! BlackUpgrade :call __BLACK_MISSING()
    command! BlackVersion :call __BLACK_MISSING()
    finish
endif

if exists("g:load_black")
   finish
endif

let g:load_black = "py1.0"
if !exists("g:black_virtualenv")
  if has("nvim")
    let g:black_virtualenv = "~/.local/share/nvim/black"
  else
    let g:black_virtualenv = "~/.vim/black"
  endif
endif
if !exists("g:black_fast")
  let g:black_fast = 0
endif
if !exists("g:black_linelength")
  let g:black_linelength = 88
endif
if !exists("g:black_skip_string_normalization")
  let g:black_skip_string_normalization = 0
endif

python3 << EndPython3
import collections
import os
import sys
import vim

from typing import Any, Dict, Iterable, Optional
from pathlib import Path
from functools import lru_cache


class Flag(collections.namedtuple("FlagBase", "name, cast")):
  @property
  def var_name(self):
    return self.name.replace("-", "_")

  @property
  def vim_rc_name(self):
    name = self.var_name
    if name == "line_length":
      name = name.replace("_", "")
    return "g:black_" + name


FLAGS = [
  Flag(name="line_length", cast=int),
  Flag(name="fast", cast=lambda val: val.strip().lower() in ('1', 'true')),
  Flag(name="skip_string_normalization", cast=lambda val: val.strip().lower() in ('1', 'true')),
]


def _get_python_binary(exec_prefix):
  try:
    default = vim.eval("g:pymode_python").strip()
  except vim.error:
    default = ""
  if default and os.path.exists(default):
    return default
  if sys.platform[:3] == "win":
    return exec_prefix / 'python.exe'
  return exec_prefix / 'bin' / 'python3'

def _get_pip(venv_path):
  if sys.platform[:3] == "win":
    return venv_path / 'Scripts' / 'pip.exe'
  return venv_path / 'bin' / 'pip'

def _get_virtualenv_site_packages(venv_path, pyver):
  if sys.platform[:3] == "win":
    return venv_path / 'Lib' / 'site-packages'
  return venv_path / 'lib' / f'python{pyver[0]}.{pyver[1]}' / 'site-packages'

def _initialize_black_env(upgrade=False):
  pyver = sys.version_info[:2]
  if pyver < (3, 6):
    print("Sorry, Black requires Python 3.6+ to run.")
    return False

  from pathlib import Path
  import subprocess
  import venv
  virtualenv_path = Path(vim.eval("g:black_virtualenv")).expanduser()
  virtualenv_site_packages = str(_get_virtualenv_site_packages(virtualenv_path, pyver))
  first_install = False
  if not virtualenv_path.is_dir():
    print('Please wait, one time setup for Black.')
    _executable = sys.executable
    try:
      sys.executable = str(_get_python_binary(Path(sys.exec_prefix)))
      print(f'Creating a virtualenv in {virtualenv_path}...')
      print('(this path can be customized in .vimrc by setting g:black_virtualenv)')
      venv.create(virtualenv_path, with_pip=True)
    finally:
      sys.executable = _executable
    first_install = True
  if first_install:
    print('Installing Black with pip...')
  if upgrade:
    print('Upgrading Black with pip...')
  if first_install or upgrade:
    subprocess.run([str(_get_pip(virtualenv_path)), 'install', '-U', 'black'], stdout=subprocess.PIPE)
    print('DONE! You are all set, thanks for waiting ✨ 🍰 ✨')
  if first_install:
    print('Pro-tip: to upgrade Black in the future, use the :BlackUpgrade command and restart Vim.\n')
  if virtualenv_site_packages not in sys.path:
    sys.path.append(virtualenv_site_packages)
  return True

if _initialize_black_env():
  import black
  import time

def Black():
  start = time.time()
  configs = get_configs()
  mode = black.FileMode(
    line_length=configs["line_length"],
    string_normalization=not configs["skip_string_normalization"],
    is_pyi=vim.current.buffer.name.endswith('.pyi'),
  )

  buffer_str = '\n'.join(vim.current.buffer) + '\n'
  try:
    new_buffer_str = black.format_file_contents(
      buffer_str,
      fast=configs["fast"],
      mode=mode,
    )
  except black.NothingChanged:
    print(f'Already well formatted, good job. (took {time.time() - start:.4f}s)')
  except Exception as exc:
    print(exc)
  else:
    current_buffer = vim.current.window.buffer
    cursors = []
    for i, tabpage in enumerate(vim.tabpages):
      if tabpage.valid:
        for j, window in enumerate(tabpage.windows):
          if window.valid and window.buffer == current_buffer:
            cursors.append((i, j, window.cursor))
    vim.current.buffer[:] = new_buffer_str.split('\n')[:-1]
    for i, j, cursor in cursors:
      window = vim.tabpages[i].windows[j]
      try:
        window.cursor = cursor
      except vim.error:
        window.cursor = (len(window.buffer), 0)
    print(f'Reformatted in {time.time() - start:.4f}s.')


def find_pyproject_toml(path_search_start: Iterable[str]) -> Optional[str]:
    """Find the absolute filepath to a pyproject.toml if it exists"""
    path_project_root = find_project_root(path_search_start)
    path_pyproject_toml = path_project_root / "pyproject.toml"
    return str(path_pyproject_toml) if path_pyproject_toml.is_file() else None

@lru_cache()
def find_project_root(srcs: Iterable[str]) -> Path:
    """Return a directory containing .git, .hg, or pyproject.toml.
    That directory will be a common parent of all files and directories
    passed in `srcs`.
    If no directory in the tree contains a marker that would specify it's the
    project root, the root of the file system is returned.
    """
    if not srcs:
        return Path("/").resolve()

    path_srcs = [Path(src).resolve() for src in srcs]

    # A list of lists of parents for each 'src'. 'src' is included as a
    # "parent" of itself if it is a directory
    src_parents = [
        list(path.parents) + ([path] if path.is_dir() else []) for path in path_srcs
    ]

    common_base = max(
        set.intersection(*(set(parents) for parents in src_parents)),
        key=lambda path: path.parts,
    )

    for directory in (common_base, *common_base.parents):
        if (directory / ".git").exists():
            return directory

        if (directory / ".hg").is_dir():
            return directory

        if (directory / "pyproject.toml").is_file():
            return directory

    return directory


def parse_pyproject_toml(path_config: str) -> Dict[str, Any]:
    """Parse a pyproject toml file, pulling out relevant parts for Black
    If parsing fails, will raise a toml.TomlDecodeError
    """
    import toml
    pyproject_toml = toml.load(path_config)
    config = pyproject_toml.get("tool", {}).get("black", {})
    return {k.replace("--", "").replace("-", "_"): v for k, v in config.items()}


def get_configs():
  # Old versions of black
  old_version = os.path.basename(black.__file__) == 'black.py'
  if old_version:
      path_pyproject_toml = find_pyproject_toml(vim.eval("fnamemodify(getcwd(), ':t')"))
  else:
      path_pyproject_toml = black.find_pyproject_toml(vim.eval("fnamemodify(getcwd(), ':t')"))

  toml_config = {}
  if path_pyproject_toml:
      if old_version:
          toml_config = parse_pyproject_toml(path_pyproject_toml)
      else:
          toml_config = black.parse_pyproject_toml(path_pyproject_toml)

  return {
    flag.var_name: toml_config.get(flag.name, flag.cast(vim.eval(flag.vim_rc_name)))
    for flag in FLAGS
  }


def BlackUpgrade():
  _initialize_black_env(upgrade=True)

def BlackVersion():
  print(f'Black, version {black.__version__} on Python {sys.version}.')

EndPython3

command! Black :py3 Black()
command! BlackUpgrade :py3 BlackUpgrade()
command! BlackVersion :py3 BlackVersion()
