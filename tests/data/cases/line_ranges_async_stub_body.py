# flags: --line-ranges=10-10 --line-ranges=14-14
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.
# Selecting only the `...` body of an `async def` used to move the `...` to
# column 0, which is invalid code. The unselected header lines stay as written.
x  =  1


async def fetch():
    ...


def close():
    ...


y  =  2
