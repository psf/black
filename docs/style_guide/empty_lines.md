## Empty lines

*Black* avoids spurious vertical whitespace.  This is in the spirit of
PEP 8 which says that in-function vertical whitespace should only be
used sparingly.  One exception is control flow statements: *Black* will
always emit an extra empty line after ``return``, ``raise``, ``break``,
``continue``, and ``yield``.  This is to make changes in control flow
more prominent to readers of your code.

*Black* will allow single empty lines inside functions, and single and
double empty lines on module level left by the original editors, except
when they're within parenthesized expressions.  Since such expressions
are always reformatted to fit minimal space, this whitespace is lost.

It will also insert proper spacing before and after function definitions.
It's one line before and after inner functions and two lines before and
after module-level functions.  *Black* will put those empty lines also
between the function definition and any standalone comments that
immediately precede the given function.  If you want to comment on the
entire function, use a docstring or put a leading comment in the function
body.