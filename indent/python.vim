if exists("b:did_indent") || !exists("g:black_indent") || g:black_indent == 0
    finish
endif
let b:did_indent = 1

setlocal nolisp
setlocal autoindent
setlocal indentexpr=BlackIndent()
setlocal indentkeys+=<:>,=elif,=except

" Four-space indentation no matter what.
setlocal shiftwidth=4
setlocal expandtab

let b:undo_indent = "setl ai< inde< lisp< sw< et<"

if exists("*BlackIndent")
    finish
endif

function s:SyntaxName(lnum, cnum)
    return synIDattr(synID(a:lnum, a:cnum, 1), "name")
endfunction

function s:NoComment(lnum)
    let line = getline(a:lnum)
    let len = strlen(line)
    while s:SyntaxName(a:lnum, len) =~# '\(Comment\|Todo\)$'
        let len = len - 1
    endwhile
    return strpart(line, 0, len)
endfunction

" prevnonblank() doesn't ignore entirely comment lines.
function s:PrevNonBlankOrComment(lnum)
    let l = prevnonblank(a:lnum)
    while getline(l) =~# '^\s*#'
        let l = prevnonblank(l - 1)
    endwhile
    return l
endfunction

function s:ForceDedent(lnum)
    if indent(a:lnum) <= indent(s:PrevNonBlankOrComment(a:lnum - 1)) - &sw
        return -1
    else
        return indent(a:lnum - 1) - &sw
    endif
endfunction

function! BlackIndent()
    " First line gets no indent.
    if v:lnum == 1
        return 0
    endif

    " Strings and doctests should not be touched.
    if s:SyntaxName(v:lnum, 1) =~# '\(String\|Quotes\)$\|Doctest'
        return -1
    endif

    " Lines after a line ending in an open paren or a colon should be indented.
    if s:NoComment(v:lnum - 1) =~# '[[({:]\s*$'
        return indent(v:lnum - 1) + &sw
    endif

    " Lines beginning with a closing paren should be dedented.
    if getline(v:lnum) =~# '^\s*[])}]'
        return indent(v:lnum - 1) - &sw
    endif

    " Backslash-continued lines are only used in the case of `with` statements.
    if getline(v:lnum - 1) =~# '\\$'
        if getline(v:lnum - 2) !~# '\\$'
            " The first line after a backslash line should be indented 5.
            return indent(v:lnum - 1) + &sw + 1
        elseif getline(v:lnum) =~# '^\s*:'
            " The final colon after a continued line should be dedented.
            return indent(v:lnum - 1) - &sw - 1
        else
            return -1
        endif
    endif

    " Lines after ones using these keywords are unreachable, so dedent.
    if getline(v:lnum - 1) =~# '^\s*\(break\|continue\|pass\|raise\|return\)\>'
        return s:ForceDedent(v:lnum)
    endif

    " Lines starting with these always have less indent than the line before.
    if getline(v:lnum) =~# '^\s*\(elif\|except\|finally\)\>'
        return s:ForceDedent(v:lnum)
    endif

    " `else` is special because it can be used in `x if y else z` expressions
    " that span multiple lines, and can come after a single line `if` clause.
    if getline(v:lnum) =~# '^\s*else\>'
        if getline(v:lnum - 1) '^\s*if\>'
            return -1
        else
            return s:ForceDedent(v:lnum)
        endif
    endif

    " Otherwise, keep the current indent.
    return -1
endfunction
