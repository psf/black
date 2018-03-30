## Trailing commas

*Black* will add trailing commas to expressions that are split
by comma where each element is on its own line.  This includes function
signatures.

Unnecessary trailing commas are removed if an expression fits in one
line.  This makes it 1% more likely that your line won't exceed the
allotted line length limit.  Moreover, in this scenario, if you added
another argument to your call, you'd probably fit it in the same line
anyway.  That doesn't make diffs any larger.

One exception to removing trailing commas is tuple expressions with
just one element.  In this case *Black* won't touch the single trailing
comma as this would unexpectedly change the underlying data type.  Note
that this is also the case when commas are used while indexing.  This is
a tuple in disguise: ```numpy_array[3, ]```.

One exception to adding trailing commas is function signatures
containing `*`, `*args`, or `**kwargs`.  In this case a trailing comma
is only safe to use on Python 3.6.  *Black* will detect if your file is
already 3.6+ only and use trailing commas in this situation.  If you
wonder how it knows, it looks for f-strings and existing use of trailing
commas in function signatures that have stars in them.  In other words,
if you'd like a trailing comma in this situation and *Black* didn't
recognize it was safe to do so, put it there manually and *Black* will
keep it.
