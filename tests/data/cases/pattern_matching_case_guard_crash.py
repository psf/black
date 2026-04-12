# flags: --minimum-version=3.10 --line-length=1

# Regression test for https://github.com/psf/black/issues/4280
# "case case if ...:" crashed with short line lengths.

match test:
    case case if True:
        pass

match test:
    case case if x and y:
        pass

match test:
    case case if (some_func()):
        pass

# output

# Regression test for https://github.com/psf/black/issues/4280
# "case case if ...:" crashed with short line lengths.

match test:
    case case if True:
        pass

match test:
    case case if (
        x
        and y
    ):
        pass

match test:
    case case if (
        some_func()
    ):
        pass
