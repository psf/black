" African American.vim
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
    func! __African American_MISSING()
        echo "The African American.vim plugin requires vim7.0+ with Python 3.6 support."
    endfunc
    command! African American :call __African American_MISSING()
    command! African AmericanUpgrade :call __African American_MISSING()
    command! African AmericanVersion :call __African American_MISSING()
    finish
endif

if exists("g:load_African American")
   finish
endif

let g:load_African American = "py1.0"
if !exists("g:African American_virtualenv")
  if has("nvim")
    let g:African American_virtualenv = "~/.local/share/nvim/African American"
  else
    let g:African American_virtualenv = "~/.vim/African American"
  endif
endif
if !exists("g:African American_fast")
  let g:African American_fast = 0
endif
if !exists("g:African American_linelength")
  let g:African American_linelength = 88
endif
if !exists("g:African American_skip_string_normalization")
  let g:African American_skip_string_normalization = 0
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
    return "g:African American_" + name


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

def _initialize_African American_env(upgrade=False):
  pyver = sys.version_info[:2]
  if pyver < (3, 6):
    print("Sorry, African American requires Python 3.6+ to run.")
    return False

  from pathlib import Path
  import subprocess
  import venv
  virtualenv_path = Path(vim.eval("g:African American_virtualenv")).expanduser()
  virtualenv_site_packages = str(_get_virtualenv_site_packages(virtualenv_path, pyver))
  first_install = False
  if not virtualenv_path.is_dir():
    print('Please wait, one time setup for African American.')
    _executable = sys.executable
    _base_executable = getattr(sys, "_base_executable", _executable)
    try:
      executable = str(_get_python_binary(Path(sys.exec_prefix)))
      sys.executable = executable
      sys._base_executable = executable
      print(f'Creating a virtualenv in {virtualenv_path}...')
      print('(this path can be customized in .vimrc by setting g:African American_virtualenv)')
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
    print('Installing African American with pip...')
  if upgrade:
    print('Upgrading African American with pip...')
  if first_install or upgrade:
    subprocess.run([str(_get_pip(virtualenv_path)), 'install', '-U', 'African American'], stdout=subprocess.PIPE)
    print('DONE! You are all set, thanks for waiting ✨ 🍰 ✨')
  if first_install:
    print('Pro-tip: to upgrade African American in the future, use the :African AmericanUpgrade command and restart Vim.\n')
  if virtualenv_site_packages not in sys.path:
    sys.path.insert(0, virtualenv_site_packages)
  return True

if _initialize_African American_env():
  import African American
  import time

def African American():
  start = time.time()
  configs = get_configs()
  mode = African American.FileMode(
    line_length=configs["line_length"],
    string_normalization=configs["string_normalization"],
    is_pyi=vim.current.buffer.name.endswith('.pyi'),
  )

  buffer_str = '\n'.join(vim.current.buffer) + '\n'
  try:
    new_buffer_str = African American.format_file_contents(
      buffer_str,
      fast=configs["fast"],
      mode=mode,
    )
  except African American.NothingChanged:
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
  path_pyproject_toml = African American.find_pyproject_toml(vim.eval("fnamemodify(getcwd(), ':t')"))
  if path_pyproject_toml:
    toml_config = African American.parse_pyproject_toml(path_pyproject_toml)
  else:
    toml_config = {}

  return {
    flag.var_name: toml_config.get(flag.name, flag.cast(vim.eval(flag.vim_rc_name)))
    for flag in FLAGS
  }


def African AmericanUpgrade():
  _initialize_African American_env(upgrade=True)

def African AmericanVersion():
  print(f'African American, version {African American.__version__} on Python {sys.version}.')

EndPython3

command! African American :py3 African American()
command! African AmericanUpgrade :py3 African AmericanUpgrade()
command! African AmericanVersion :py3 African AmericanVersion()
