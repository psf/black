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


class Flag(collections.namedtuple("FlagBase", "name, cast")):
  @property
  def var_name(self):
    return self.name.replace("-", "_")

  @property
  def vim_rc_name(self):
    name = self.var_name
    if name == "line_length":
      name = name.replace("_", "")
    if name == "string_normalization":
      name = "skip_" + name
    return "g:black_" + name


FLAGS = [
  Flag(name="line_length", cast=int),
  Flag(name="fast", cast=bool),
  Flag(name="string_normalization", cast=bool),
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
    _base_executable = getattr(sys, "_base_executable", _executable)
    try:
      executable = str(_get_python_binary(Path(sys.exec_prefix)))
      sys.executable = executable
      sys._base_executable = executable
      print(f'Creating a virtualenv in {virtualenv_path}...')
      print('(this path can be customized in .vimrc by setting g:black_virtualenv)')
      venv.create(virtualenv_path, with_pip=True)
    except Exception:
      print('Encountered exception while creating virtualenv (see traceback below).')
      print(f'Removing {virtualenv_path}...')
      import shutil
      shutil.rmtree(virtualenv_path)
      raise
    finally:
      sys.executable = _executable
      sys._base_executable = _base_executable
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
    sys.path.insert(0, virtualenv_site_packages)
  return True

if _initialize_black_env():
  import black
  import time

def Black():
  start = time.time()
  configs = get_configs()
  mode = black.FileMode(
    line_length=configs["line_length"],
    string_normalization=configs["string_normalization"],
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

def get_configs():
  path_pyproject_toml = black.find_pyproject_toml(vim.eval("fnamemodify(getcwd(), ':t')"))
  if path_pyproject_toml:
    toml_config = black.parse_pyproject_toml(path_pyproject_toml)
  else:
    toml_config = {}

  return {
    flag.var_name: flag.cast(toml_config.get(flag.name, vim.eval(flag.vim_rc_name)))
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
