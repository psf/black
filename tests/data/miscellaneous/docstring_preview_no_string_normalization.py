def do_not_touch_this_prefix():
    R"""There was a bug where docstring prefixes would be normalized even with -S."""


def do_not_touch_this_prefix2():
    F'There was a bug where docstring prefixes would be normalized even with -S.'


def do_not_touch_this_prefix3():
    uR'''There was a bug where docstring prefixes would be normalized even with -S.'''
