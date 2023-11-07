# flags: --line-ranges=9-11
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# This is a specific case for Black's two-pass formatting behavior in `format_str`.
# The second pass must respect the line ranges before the first pass.


def restrict_to_this_line(arg1,
  arg2,
  arg3):
    print  ( "This should not be formatted." )
    print  ( "Note that in the second pass, the original line range 9-11 will cover these print lines.")

# output

# flags: --line-ranges=9-11
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# This is a specific case for Black's two-pass formatting behavior in `format_str`.
# The second pass must respect the line ranges before the first pass.


def restrict_to_this_line(arg1, arg2, arg3):
    print  ( "This should not be formatted." )
    print  ( "Note that in the second pass, the original line range 9-11 will cover these print lines.")
