def get_requires_for_build_sdist(
    # pylint: disable-next=unused-argument
    config_settings: dict[str, str | list[str]] | None = None,
) -> list[str]:
    return ["pathspec", "pyproject_metadata"]


(
    a
    and b
    # comment
    and c
    and d
)

(
    # comment
    a and b and c and d
)