# These brackets are redundant, therefore remove.
try:
    a.something
except (AttributeError) as err:
    raise err

# This is tuple of exceptions.
# Although this could be replaced with just the exception,
# we do not remove brackets to preserve AST.
try:
    a.something
except (AttributeError,) as err:
    raise err

# This is a tuple of exceptions. Do not remove brackets.
try:
    a.something
except (AttributeError, ValueError) as err:
    raise err

# Test long variants.
try:
    a.something
except (some.really.really.really.looooooooooooooooooooooooooooooooong.module.over89.chars.Error) as err:
    raise err

try:
    a.something
except (some.really.really.really.looooooooooooooooooooooooooooooooong.module.over89.chars.Error,) as err:
    raise err

try:
    a.something
except (some.really.really.really.looooooooooooooooooooooooooooooooong.module.over89.chars.Error, some.really.really.really.looooooooooooooooooooooooooooooooong.module.over89.chars.Error) as err:
    raise err

# output
# These brackets are redundant, therefore remove.
try:
    a.something
except AttributeError as err:
    raise err

# This is tuple of exceptions.
# Although this could be replaced with just the exception,
# we do not remove brackets to preserve AST.
try:
    a.something
except (AttributeError,) as err:
    raise err

# This is a tuple of exceptions. Do not remove brackets.
try:
    a.something
except (AttributeError, ValueError) as err:
    raise err

# Test long variants.
try:
    a.something
except (
    some.really.really.really.looooooooooooooooooooooooooooooooong.module.over89.chars.Error
) as err:
    raise err

try:
    a.something
except (
    some.really.really.really.looooooooooooooooooooooooooooooooong.module.over89.chars.Error,
) as err:
    raise err

try:
    a.something
except (
    some.really.really.really.looooooooooooooooooooooooooooooooong.module.over89.chars.Error,
    some.really.really.really.looooooooooooooooooooooooooooooooong.module.over89.chars.Error,
) as err:
    raise err
