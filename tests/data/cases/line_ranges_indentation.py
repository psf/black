# flags: --line-ranges=5-5
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.
if cond1:
  print("first")
  if cond2:
    print("second")
  else:
    print("else")

if another_cond:
  print("will not be changed")

# output

# flags: --line-ranges=5-5
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.
if cond1:
    print("first")
    if cond2:
        print("second")
    else:
        print("else")

if another_cond:
  print("will not be changed")
