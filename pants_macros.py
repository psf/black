# A macro alternative to parametrizing on the interpreter_constraints field
# of python_tests. We use this so we can pick just one representative
# parameterization on which to run mypy, flake8, black itself etc.  We won't
# need this once Pants supports configurations (see
# https://docs.google.com/document/d/1mzZWnXiE6OkgMH_Dm7WeA3ck9veusQmr_c6GWPb_tsQ/edit?usp=sharing)

# type: ignore

_interpreter_constraints = (
    ("py36", (">=3.6.2,<3.7",)),
    ("py37", ("==3.7.*",)),
    ("py38", ("==3.8.*",)),
    ("py39", ("==3.9.*",)),
    ("py310", ("==3.10.*",)),
    ("pypy37", ("PyPy==3.7.*",)),
)

_intepreter_to_lint_on = "py39"


def multi_interpreter_python_tests(**kwargs):
    name = kwargs.pop("name")
    for interpreter, constraints in _interpreter_constraints:
        kwargs["name"] = f"{name}-{interpreter}"
        kwargs["interpreter_constraints"] = constraints
        skip_lint = interpreter != _intepreter_to_lint_on
        kwargs["skip_flake8"] = skip_lint
        kwargs["skip_black"] = skip_lint
        kwargs["skip_mypy"] = skip_lint
        python_tests(**kwargs)
