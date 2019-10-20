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
    echo "This script requires vim7.0+ with Python 3.6 support."
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

python3 << endpython3
import os
import sys
import vim

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
  fast = bool(int(vim.eval("g:black_fast")))
  mode = black.FileMode(
    line_length=int(vim.eval("g:black_linelength")),
    string_normalization=not bool(int(vim.eval("g:black_skip_string_normalization"))),
    is_pyi=vim.current.buffer.name.endswith('.pyi'),
  )
  (cursor_line, cursor_column) = vim.current.window.cursor
  cb = vim.current.buffer[:]
  cb_bc = cb[0:cursor_line]
  # Format all code before the cursor.
  # Detect unclosed blocks, close them with pass.
  last_line = cb_bc[-1]
  if last_line.rstrip().endswith(":"):
      cb_bc[-1] = last_line + " pass"
  # Determine old:new cursor location mapping
  buffer_str_before = '\n'.join(cb_bc)+'\n'
  try:
    new_buffer_str_before = black.format_file_contents(buffer_str_before, fast=fast, mode=mode)
    new_cb = new_buffer_str_before.split('\n')[:-1]
    new_cursor_line = len(new_cb)
    new_cursor = (new_cursor_line, cursor_column)
  except black.NothingChanged:
    new_cursor_line = cursor_line
    new_cursor = (new_cursor_line, cursor_column)
  except Exception as exc:
    print(exc)
  # Now we know where the cursor should be
  # when we format the entire buffer. Do it:
  buffer_str = '\n'.join(cb) + '\n'
  try:
    new_buffer_str = black.format_file_contents(buffer_str, fast=fast, mode=mode)
  except black.NothingChanged:
    print(f'Already well formatted, good job. (took {time.time() - start:.4f}s)')
  except Exception as exc:
    print(exc)
  else:
    # Replace the buffer
    new_cb = new_buffer_str.split('\n')[:-1]
    vim.current.buffer[:] = new_cb
    # Restore the cursor to its rightful place
    try:
      vim.current.window.cursor = new_cursor
    except vim.error:
      vim.current.window.cursor = (len(vim.current.buffer), 0)
    print(f'Reformatted in {time.time() - start:.4f}s.')

def BlackUpgrade():
  _initialize_black_env(upgrade=True)

def BlackVersion():
  print(f'Black, version {black.__version__} on Python {sys.version}.')

endpython3

command! Black :py3 Black()
command! BlackUpgrade :py3 BlackUpgrade()
command! BlackVersion :py3 BlackVersion()
