# flags: --minimum-version=3.12 --line-length=100
# Regression test for https://github.com/psf/black/issues/4723.
# Fixed by #4777 ("fix(3.12_generics_syntax): Fixed formatting of 3.12 generics syntax").
# Black used to split the tuple bound on the type param even though the
# whole `def` line fit within the line length.


class Example:
    @overload
    @classmethod
    def create_from[TBool: (Literal[True], Literal[False])](
        cls: type[SearchConfig[Any]],
        search_config: SearchConfig[Any],
        *,
        allow_boolean: TBool,
        **overrides: Any,
    ) -> SearchConfig[TBool]: ...

# output

# Regression test for https://github.com/psf/black/issues/4723.
# Fixed by #4777 ("fix(3.12_generics_syntax): Fixed formatting of 3.12 generics syntax").
# Black used to split the tuple bound on the type param even though the
# whole `def` line fit within the line length.


class Example:
    @overload
    @classmethod
    def create_from[TBool: (Literal[True], Literal[False])](
        cls: type[SearchConfig[Any]],
        search_config: SearchConfig[Any],
        *,
        allow_boolean: TBool,
        **overrides: Any,
    ) -> SearchConfig[TBool]: ...
