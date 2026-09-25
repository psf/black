# flags: --line-ranges=10-11
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# Regression for https://github.com/psf/black/issues/4033.
# Repeated unformatted lines outside the requested range must stay unchanged.
# The output below covers only the two selected lines.

print ( "format me" )
print ( "format me" )
print ( "format me" )
print ( "format me" )
print ( "format me" )

# output
# flags: --line-ranges=10-11
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# Regression for https://github.com/psf/black/issues/4033.
# Repeated unformatted lines outside the requested range must stay unchanged.
# The output below covers only the two selected lines.

print ( "format me" )
print("format me")
print("format me")
print ( "format me" )
print ( "format me" )
