# flags: --minimum-version=3.10
# Test fmt: skip on multiline case statements with backslash line continuation
# See https://github.com/psf/black/issues/5122

match (method, *path.split("/")):

    case ("GET", "parent", _, "resource", resource_id) \
            | ("GET", "resource", resource_id):  # fmt: skip
        pass

    case _:
        pass


match x:
    case a \
        | b \
        | c:  # fmt: skip
        pass
