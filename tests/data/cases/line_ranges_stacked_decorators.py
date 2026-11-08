# flags: --line-ranges=10-11
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.
class A:
  @a
  @b
  def f(self):
    pass

  def g(self):
    pass

# output
# flags: --line-ranges=10-11
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.
class A:
    @a
    @b
    def f(self):
        pass

    def g(self):
        pass
