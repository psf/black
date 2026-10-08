# flags: --preview
# Regression test for https://github.com/psf/black/issues/3681.
def one():
    def two():
        def three():
            _zzzzzzz_zzzz_zzzz_zzzz(
                zzz.getZZZZZZZZZZZZZZZZZ("zzz_zzz_zzzz_zzzz")[0].getZZZZZZZZZZZZZZZZZ(  # type: ignore
                    "zzzzzzz_zzzz_zzz"
                )[0]
            )


def four():
    def five():
        def six():
            _zzzzzzz_zzzz_zzzz_zzzz(zzz.getZZZZZZZZZZZZZZZZZ("zzz_zzz_zzzz_zzzz")[0].getZZZZZZZZZZZZZZZZZ(  # type: ignore
"zzzzzzz_zzzz_zzz")[0])

# output

# Regression test for https://github.com/psf/black/issues/3681.
def one():
    def two():
        def three():
            _zzzzzzz_zzzz_zzzz_zzzz(
                zzz.getZZZZZZZZZZZZZZZZZ("zzz_zzz_zzzz_zzzz")[0].getZZZZZZZZZZZZZZZZZ(  # type: ignore
                    "zzzzzzz_zzzz_zzz"
                )[0]
            )


def four():
    def five():
        def six():
            _zzzzzzz_zzzz_zzzz_zzzz(
                zzz.getZZZZZZZZZZZZZZZZZ("zzz_zzz_zzzz_zzzz")[0].getZZZZZZZZZZZZZZZZZ(  # type: ignore
                    "zzzzzzz_zzzz_zzz"
                )[0]
            )
