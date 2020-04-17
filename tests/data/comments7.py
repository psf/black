from .config import (
    Any,
    Bool,
    ConfigType,
    ConfigTypeAttributes,
    Int,
    Path,
    #  String,
    #  resolve_to_config_type,
    #  DEFAULT_TYPE_ATTRIBUTES,
)


from .config import (
    Any,
    Bool,
    ConfigType,
    ConfigTypeAttributes,
    Int,
    no_comma_here_yet
    #  and some comments,
    #  resolve_to_config_type,
    #  DEFAULT_TYPE_ATTRIBUTES,
)


result = 1  # look ma, no comment migration xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

result = (
    1  # look ma, no comment migration xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
)

result = (
    "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # aaa
)

result = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # aaa


def func():
    c = call(
        0.0123,
        0.0456,
        0.0789,
        0.0123,
        0.0789,
        a[-1],  # type: ignore
    )

    # The type: ignore exception only applies to line length, not
    # other types of formatting.
    c = call(
        "aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaaaa",  # type: ignore
        "aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaaaa"
    )


# output

from .config import (
    Any,
    Bool,
    ConfigType,
    ConfigTypeAttributes,
    Int,
    Path,
    #  String,
    #  resolve_to_config_type,
    #  DEFAULT_TYPE_ATTRIBUTES,
)


from .config import (
    Any,
    Bool,
    ConfigType,
    ConfigTypeAttributes,
    Int,
    no_comma_here_yet,
    #  and some comments,
    #  resolve_to_config_type,
    #  DEFAULT_TYPE_ATTRIBUTES,
)


result = 1  # look ma, no comment migration xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

result = 1  # look ma, no comment migration xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

result = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # aaa

result = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # aaa


def func():
    c = call(0.0123, 0.0456, 0.0789, 0.0123, 0.0789, a[-1],)  # type: ignore

    # The type: ignore exception only applies to line length, not
    # other types of formatting.
    c = call(
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",  # type: ignore
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",
    )
