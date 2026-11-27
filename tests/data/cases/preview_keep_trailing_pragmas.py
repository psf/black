# flags: --preview
from my_module import some_function  # type: ignore [import]  # pylint: ignore=no-name-in-module
from my_module import some_function  # pylint: ignore=no-name-in-module  # type: ignore [import]
from my_module import some_function  # pylint: disable=no-name-in-module,unused-import,wrong-import-order
from my_module import some_function  # explanation # type:ignore[import] # extra explanation
from my_module import some_function  # noqa: F401  # this import is needed to register the plugin
from my_module import some_function  # noqa
from my_module import some_function  # noqa_like this is an ordinary comment that is long enough to cause wrapping

if True:
    if True:
        xxxx/=yyyy  # pyright: ignore[reportGeneralTypeIssues] # type:ignore[operator] # /
        xxxx /= yyyy  # pyright: ignore[reportGeneralTypeIssues,reportUnknownVariableType]

result = call(first_argument_with_a_very_long_name, second_argument_with_a_very_long_name)  # noqa
result = call(first_argument, second_argument,)  # pylint: disable=unsubscriptable-object
result = call(
    first_argument, second_argument
)  # pylint: disable=unsubscriptable-object,unexpected-keyword-arg
result = call(first_argument,  # noqa: some-really-long-code-that-makes-this-comment-overflow
              second_argument)

# output
from my_module import some_function  # type: ignore [import]  # pylint: ignore=no-name-in-module
from my_module import some_function  # pylint: ignore=no-name-in-module  # type: ignore [import]
from my_module import some_function  # pylint: disable=no-name-in-module,unused-import,wrong-import-order
from my_module import some_function  # explanation # type:ignore[import] # extra explanation
from my_module import some_function  # noqa: F401  # this import is needed to register the plugin
from my_module import some_function  # noqa
from my_module import (
    some_function,
)  # noqa_like this is an ordinary comment that is long enough to cause wrapping

if True:
    if True:
        xxxx /= yyyy  # pyright: ignore[reportGeneralTypeIssues] # type:ignore[operator] # /
        xxxx /= yyyy  # pyright: ignore[reportGeneralTypeIssues,reportUnknownVariableType]

result = call(
    first_argument_with_a_very_long_name, second_argument_with_a_very_long_name
)  # noqa
result = call(
    first_argument,
    second_argument,
)  # pylint: disable=unsubscriptable-object
result = call(
    first_argument, second_argument
)  # pylint: disable=unsubscriptable-object,unexpected-keyword-arg
result = call(
    first_argument,  # noqa: some-really-long-code-that-makes-this-comment-overflow
    second_argument,
)
