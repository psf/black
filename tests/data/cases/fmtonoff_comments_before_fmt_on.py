# Regression tests for https://github.com/psf/black/issues/3372.
# Comments that end a `# fmt: off` region inside brackets are kept
# verbatim.
def recv(
    self,
) -> (
        # fmt: off
        gym_old_venv_step_type     # old API step
        | gym_new_venv_step_type   # new API step
        | tuple[np.ndarray, dict]  # new API reset
        | np.ndarray               # old API reset
):  # fmt: on # noqa:E125
    ...


values = _parse_flags(
    # fmt:off
    './program'
    ' --test_config.other_with_default_overitten=True',  # Comment moved
    # fmt:on
)

foo(
    # fmt: off
    a  ,  # trailing
    # fmt: on
)

x = [
    # fmt: off
    1,   2,
    3,   4,  # last row
    # fmt: on
]

y = [
    # fmt: off
    1,   2,
       # odd   indent

    # another   one
    # fmt: on
    3,
]

z = {
    "a": [
        # fmt: off
        1,   2,  # no fmt: on inside the brackets
    ],
    "b":   3,
}

w = [
    # fmt: off
    1,   2,  # trailing
    # fmt: on
    3,
]

bar(
    # fmt: off
    a  ,  # trailing
       # standalone
    # fmt: on
    b,
)

# output

# Regression tests for https://github.com/psf/black/issues/3372.
# Comments that end a `# fmt: off` region inside brackets are kept
# verbatim.
def recv(
    self,
) -> (
    # fmt: off
        gym_old_venv_step_type     # old API step
        | gym_new_venv_step_type   # new API step
        | tuple[np.ndarray, dict]  # new API reset
        | np.ndarray               # old API reset
):  # fmt: on # noqa:E125
    ...


values = _parse_flags(
    # fmt:off
    './program'
    ' --test_config.other_with_default_overitten=True',  # Comment moved
    # fmt:on
)

foo(
    # fmt: off
    a  ,  # trailing
    # fmt: on
)

x = [
    # fmt: off
    1,   2,
    3,   4,  # last row
    # fmt: on
]

y = [
    # fmt: off
    1,   2,
       # odd   indent

    # another   one
    # fmt: on
    3,
]

z = {
    "a": [
        # fmt: off
        1,   2,  # no fmt: on inside the brackets
    ],
    "b": 3,
}

w = [
    # fmt: off
    1,   2,  # trailing
    # fmt: on
    3,
]

bar(
    # fmt: off
    a  ,  # trailing
       # standalone
    # fmt: on
    b,
)
