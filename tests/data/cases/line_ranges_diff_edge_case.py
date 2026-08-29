# flags: --line-ranges=10-11
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# Reproducible example for https://github.com/psf/black/issues/4033, fixed here by a
# diagonal-preferring diff (https://github.com/psf/black/issues/4052): only the lines
# within --line-ranges should be reformatted, even though the surrounding lines match.

print ( "format me" )
print ( "format me" )
print ( "format me" )
print ( "format me" )
print ( "format me" )

# output
# flags: --line-ranges=10-11
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# Reproducible example for https://github.com/psf/black/issues/4033, fixed here by a
# diagonal-preferring diff (https://github.com/psf/black/issues/4052): only the lines
# within --line-ranges should be reformatted, even though the surrounding lines match.

print ( "format me" )
print("format me")
print("format me")
print ( "format me" )
print ( "format me" )
