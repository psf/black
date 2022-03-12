match_count += new_value == old_value

if on_windows := os.name == "nt":
    ...

on_windows: bool = (os.name == "nt")

implementation_version = (
    platform.python_version() if platform.python_implementation() == "CPython" else "Unknown"
)

is_mac = platform.system() == 'Darwin'

s = y == 2 + y == 4

name1 = name2 = name3

name1 == name2 == name3

check_sockets(on_windows=os.name == "nt")

if a := b == c:
    pass

a = [y := f(x) == True, y ** 2, y ** 3]

a = lambda line: (m := re.match(pattern, line) == True)

a = b in c and b == d

a = b == c == d

a = b == c in d

a = b >= c == True

a = b in c

a = b > c

# output

match_count += (new_value == old_value)

if on_windows := (os.name == "nt"):
    ...

on_windows: bool = (os.name == "nt")

implementation_version = (
    platform.python_version()
    if platform.python_implementation() == "CPython"
    else "Unknown"
)

is_mac = (platform.system() == "Darwin")

s = (y == 2 + y == 4)

name1 = name2 = name3

name1 == name2 == name3

check_sockets(on_windows=os.name == "nt")

if a := (b == c):
    pass

a = [y := (f(x) == True), y**2, y**3]

a = lambda line: (m := (re.match(pattern, line) == True))

a = b in c and b == d

a = (b == c == d)

a = (b == c in d)

a = (b >= c == True)

a = b in c

a = b > c
