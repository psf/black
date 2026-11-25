# flags: --line-ranges=4-4
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.
x   =   1
if True:
    # fmt: off
    a  =  1
else:
    pass

try:
    # fmt: off
    a  =  1
except E:
    pass
finally:
    pass

# output
# flags: --line-ranges=4-4
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.
x = 1
if True:
    # fmt: off
    a  =  1
else:
    pass

try:
    # fmt: off
    a  =  1
except E:
    pass
finally:
    pass