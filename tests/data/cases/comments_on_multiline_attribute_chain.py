# Regression test for https://github.com/psf/black/issues/3869: inline comments
# (including `# type: ignore`) attached to different leaves of a multi-line
# attribute-access chain must never be merged onto the same output line. The AST
# records a `# type: ignore` once per physical line, so merging two of them
# together drops one and used to fail Black's own equivalence check.
def _get_light_style(app: sphinx.application.Sphinx) -> Style:
    return (
        app  # type: ignore[no-any-return]
            .builder
            .highlighter # type: ignore[attr-defined]
            .formatter_args["style"]
        )

# output

# Regression test for https://github.com/psf/black/issues/3869: inline comments
# (including `# type: ignore`) attached to different leaves of a multi-line
# attribute-access chain must never be merged onto the same output line. The AST
# records a `# type: ignore` once per physical line, so merging two of them
# together drops one and used to fail Black's own equivalence check.
def _get_light_style(app: sphinx.application.Sphinx) -> Style:
    return (
        app  # type: ignore[no-any-return]
        .builder.highlighter  # type: ignore[attr-defined]
        .formatter_args[
            "style"
        ]
    )
