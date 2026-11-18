# flags: --line-ranges=5-5
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.
command = "go north"
match command.split():
  case [action]:
    pass
  case [action, obj]:
    pass

match command:
  case _:
    pass

# output
# flags: --line-ranges=5-5
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.
command = "go north"
match command.split():
    case [action]:
        pass
    case [action, obj]:
        pass

match command:
  case _:
    pass
