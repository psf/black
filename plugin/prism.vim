" prism.vim
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

if exists("g:load_prism")
  finish
endif

if v:version < 700 || !has('python3')
    func! __BLACK_MISSING()
        echo "The prism.vim plugin requires vim7.0+ with Python 3.6 support."
    endfunc
    command! Prism :call __BLACK_MISSING()
    command! PrismUpgrade :call __BLACK_MISSING()
    command! PrismVersion :call __BLACK_MISSING()
    finish
endif

let g:load_prism = "py1.0"
if !exists("g:prism_virtualenv")
  if has("nvim")
    let g:prism_virtualenv = "~/.local/share/nvim/prism"
  else
    let g:prism_virtualenv = "~/.vim/prism"
  endif
endif
if !exists("g:prism_fast")
  let g:prism_fast = 0
endif
if !exists("g:prism_linelength")
  let g:prism_linelength = 88
endif
if !exists("g:prism_skip_string_normalization")
  if exists("g:prism_string_normalization")
    let g:prism_skip_string_normalization = !g:prism_string_normalization
  else
    let g:prism_skip_string_normalization = 0
  endif
endif
if !exists("g:prism_skip_magic_trailing_comma")
  if exists("g:prism_magic_trailing_comma")
    let g:prism_skip_magic_trailing_comma = !g:prism_magic_trailing_comma
  else
    let g:prism_skip_magic_trailing_comma = 0
  endif
endif
if !exists("g:prism_quiet")
  let g:prism_quiet = 0
endif
if !exists("g:prism_target_version")
  let g:prism_target_version = ""
endif
if !exists("g:prism_use_virtualenv")
  let g:prism_use_virtualenv = 1
endif
if !exists("g:prism_preview")
  let g:prism_preview = 0
endif

function PrismComplete(ArgLead, CmdLine, CursorPos)
  return [
\    'target_version=py27',
\    'target_version=py36',
\    'target_version=py37',
\    'target_version=py38',
\    'target_version=py39',
\    'target_version=py310',
\  ]
endfunction

command! -nargs=* -complete=customlist,PrismComplete Prism :call prism#Prism(<f-args>)
command! PrismUpgrade :call prism#PrismUpgrade()
command! PrismVersion :call prism#PrismVersion()
