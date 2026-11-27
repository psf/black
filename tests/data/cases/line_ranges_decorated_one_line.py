# flags: --line-ranges=9-9
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.
class A:
  @property
  def f(self): ...
  @overload
  def g(self, x: int) -> int: ...
x  =  1

# output
# flags: --line-ranges=9-9
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.
class A:
    @property
    def f(self): ...
    @overload
    def g(self, x: int) -> int: ...
x = 1
