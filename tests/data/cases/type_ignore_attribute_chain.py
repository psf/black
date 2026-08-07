def _get_light_style(app: sphinx.application.Sphinx) -> Style:
    return (
        app  # type: ignore[no-any-return]
            .builder
            .highlighter  # type: ignore[attr-defined]
            .formatter_args["style"]
        )


# output


def _get_light_style(app: sphinx.application.Sphinx) -> Style:
    return (
        app  # type: ignore[no-any-return]
        .builder.highlighter  # type: ignore[attr-defined]
        .formatter_args["style"]
    )
