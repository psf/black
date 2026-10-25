# A `# fmt: skip` on a line of its own between statements skips nothing: the
# statement above is formatted and the blank line before the comment stays.
import os

x   =   1

# a comment  # fmt: skip
y   =   [1,2]

# fmt: skip
class A:
    def f(self):
        z   =   1

  # fmt: skip
    def g(self):
        pass

# output

# A `# fmt: skip` on a line of its own between statements skips nothing: the
# statement above is formatted and the blank line before the comment stays.
import os

x = 1

# a comment  # fmt: skip
y = [1, 2]


# fmt: skip
class A:
    def f(self):
        z = 1

    # fmt: skip
    def g(self):
        pass
