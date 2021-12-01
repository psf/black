" black.vim
" Author: Łukasz Langa
" Created: Mon Mar 26 23:27:53 2018 -0700
" Requires: Vim Ver7.0+
" Version:  1.2
"
" Documentation:
"   This plugin formats Python files.
"
" History:
"  1.0:
"    - initial version
"  1.1:
"    - restore cursor/window position after formatting
"  1.2:
"    - use autoload script

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
  if exists("g:black_string_normalization")
    let g:black_skip_string_normalization = !g:black_string_normalization
  else
    let g:black_skip_string_normalization = 0
  endif
endif
if !exists("g:black_skip_magic_trailing_comma")
  if exists("g:black_magic_trailing_comma")
    let g:black_skip_magic_trailing_comma = !g:black_magic_trailing_comma
  else
    let g:black_skip_magic_trailing_comma = 0
  endif
endif
if !exists("g:black_quiet")
  let g:black_quiet = 0
endif
if !exists("g:black_target_version")
  let g:black_target_version = ""
endif

function BlackComplete(ArgLead, CmdLine, CursorPos)
  return [
\    'target_version=py27',
\    'target_version=py36',
\    'target_version=py37',
\    'target_version=py38',
\    'target_version=py39',
\    'target_version=py310',
\  ]
endfunction

command! -nargs=* -complete=customlist,BlackComplete Black :call black#Black(<f-args>)
command! BlackUpgrade :call black#BlackUpgrade()
command! BlackVersion :call black#BlackVersion()
