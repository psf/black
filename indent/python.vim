if exists("b:did_indent")
    finish
endif
" Don't actually set b:did_indent, need to source indent/python.vim first.

if !get(g:, "black_indent", 0)
    finish
endif

" shiftwidth() does not exist on older Vim versions. BlackIndent should use s:sw
" for indentation to be correct regardless of the set shiftwidth (even if it
" should be 4), and Vim sets the shiftwidth for Python files to 4 by default
" anyway. If the user changes shiftwidth from 4, not our fault; at least it will
" still indent reasonably.
let s:sw = exists("*shiftwidth") ? "shiftwidth()" : "&sw"

let s:has_paren_patch = has("nvim-0.8.0") || has("patch-9.0.259")
if s:has_paren_patch
    let g:python_indent = get(g:, "python_indent", {})
    let g:python_indent.open_paren = s:sw
    let g:python_indent.nested_paren = s:sw
    " +1 is for with statements.
    let g:python_indent.continue = s:sw .. " + 1"
    let g:python_indent.closed_paren_align_last_line = v:false
else
    let g:pyindent_open_paren = s:sw
    let g:pyindent_nested_paren = s:sw
    " +1 is for with statements.
    let g:pyindent_continue = s:sw .. " + 1"
endif

if filereadable($VIMRUNTIME .. "/indent/python.vim")
    source $VIMRUNTIME/indent/python.vim
endif

if !exists("*GetPythonIndent")
    finish
endif

setlocal indentexpr=BlackIndent()

if exists("*BlackIndent")
    finish
endif

function BlackIndent()
    let original_indent = GetPythonIndent(v:lnum)
    let syntax_name = synID(v:lnum, match(getline(v:lnum), '\S') + 1, 1)
        \ ->synIDtrans()
        \ ->synIDattr("name")
    if syntax_name !=# "String"
        if !s:has_paren_patch && getline(v:lnum) =~# '^\s*\%(]\|}\|)\)'
            " Closing parens should be dedented from preceding line once.
            return original_indent - eval(s:sw)
        elseif getline(v:lnum) =~# '^\s*:' && getline(v:lnum - 1) =~# '\\$'
            " Lone colons (in the case of with statements) should be aligned
            " with the "with".
            return original_indent - (eval(s:sw) + 1)
        endif
    endif
    return original_indent
endfunction
