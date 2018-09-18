def f(
  a,
  **kwargs,
) -> A:
    with cache_dir():
        if something:
            result = (
                CliRunner().invoke(black.main, [str(src1), str(src2), "--diff", "--check"])
            )
    return A(
        very_long_argument_name1=very_long_value_for_the_argument,
        very_long_argument_name2=very_long_value_for_the_argument,
        **kwargs,
    )
def g():
    "Docstring."
    def inner():
        pass
    print("Inner defs should breathe a little.")
def h():
    def inner():
        pass
    print("Inner defs should breathe a little.")

# output

def f(a, **kwargs) -> A:
    with cache_dir():
        if something:
            result = CliRunner().invoke(
                black.main, [str(src1), str(src2), "--diff", "--check"]
            )
    return A(
        very_long_argument_name1=very_long_value_for_the_argument,
        very_long_argument_name2=very_long_value_for_the_argument,
        **kwargs,
    )


def g():
    "Docstring."

    def inner():
        pass

    print("Inner defs should breathe a little.")


def h():
    def inner():
        pass

    print("Inner defs should breathe a little.")
