def _get_light_style(app: sphinx.application.Sphinx) -> Style:
    return (
        app  # type: ignore[no-any-return]
            .builder  # comment
            .highlighter  # type: ignore[attr-defined]
            .formatter_args["style"]
        )


def _get_dark_style(app: sphinx.application.Sphinx) -> Style:
    return (
        app  # comment
            .builder  # type: ignore[attr-defined]
            .highlighter  # type: ignore[attr-defined]
            .formatter_args["style"]
        )


# output


def _get_light_style(app: sphinx.application.Sphinx) -> Style:
    return (
        app  # type: ignore[no-any-return]
        .builder  # comment
        .highlighter  # type: ignore[attr-defined]
        .formatter_args["style"]
    )


def _get_dark_style(app: sphinx.application.Sphinx) -> Style:
    return (
        app  # comment
        .builder  # type: ignore[attr-defined]
        .highlighter  # type: ignore[attr-defined]
        .formatter_args["style"]
    )
