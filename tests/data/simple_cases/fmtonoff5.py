# Regression test for https://github.com/psf/black/issues/3129.
setup(
    entry_points={
        # fmt: off
        "console_scripts": [
            "foo-bar"
            "=foo.bar.:main",
        # fmt: on
        ]
    },
)
