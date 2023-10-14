# flags: --preview
from .config import (
    Any,
    Bool,
    ConfigType,
    ConfigTypeAttributes,
    Int,
    Path,
    #  String,
    #  resolve_to_config_type,
    #  DEFAULT_TYPE_ATTRIBUTES,
)


from .config import (
    Any,
    Bool,
    ConfigType,
    ConfigTypeAttributes,
    Int,
    no_comma_here_yet
    #  and some comments,
    #  resolve_to_config_type,
    #  DEFAULT_TYPE_ATTRIBUTES,
)
from com.my_lovely_company.my_lovely_team.my_lovely_project.my_lovely_component import (
    MyLovelyCompanyTeamProjectComponent  # NOT DRY
)
from com.my_lovely_company.my_lovely_team.my_lovely_project.my_lovely_component import (
    MyLovelyCompanyTeamProjectComponent as component  # DRY
)


result = 1  # look ma, no comment migration xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

result = (
    1  # look ma, no comment migration xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
)

result = (
    "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # aaa
)

result = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # aaa


def func():
    c = call(
        0.0123,
        0.0456,
        0.0789,
        0.0123,
        0.0789,
        a[-1],  # type: ignore
    )
    c = call(
        0.0123,
        0.0456,
        0.0789,
        0.0123,
        0.0789,
        a[-1]  # type: ignore
    )
    c = call(
        0.0123,
        0.0456,
        0.0789,
        0.0123,
        0.0456,
        0.0789,
        0.0123,
        0.0456,
        0.0789,
        a[-1]  # type: ignore
    )

    # The type: ignore exception only applies to line length, not
    # other types of formatting.
    c = call(
        "aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaaaa",  # type: ignore
        "aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaaaa", "aaaaaaaa"
    )


class C:
    @pytest.mark.parametrize(
        ("post_data", "message"),
        [
            # metadata_version errors.
            (
                {},
                "None is an invalid value for Metadata-Version. Error: This field is"
                " required. see"
                " https://packaging.python.org/specifications/core-metadata"
            ),
            (
                {"metadata_version": "-1"},
                "'-1' is an invalid value for Metadata-Version. Error: Unknown Metadata"
                " Version see"
                " https://packaging.python.org/specifications/core-metadata"
            ),
            # name errors.
            (
                {"metadata_version": "1.2"},
                "'' is an invalid value for Name. Error: This field is required. see"
                " https://packaging.python.org/specifications/core-metadata"
            ),
            (
                {"metadata_version": "1.2", "name": "foo-"},
                "'foo-' is an invalid value for Name. Error: Must start and end with a"
                " letter or numeral and contain only ascii numeric and '.', '_' and"
                " '-'. see https://packaging.python.org/specifications/core-metadata"
            ),
            # version errors.
            (
                {"metadata_version": "1.2", "name": "example"},
                "'' is an invalid value for Version. Error: This field is required. see"
                " https://packaging.python.org/specifications/core-metadata"
            ),
            (
                {"metadata_version": "1.2", "name": "example", "version": "dog"},
                "'dog' is an invalid value for Version. Error: Must start and end with"
                " a letter or numeral and contain only ascii numeric and '.', '_' and"
                " '-'. see https://packaging.python.org/specifications/core-metadata"
            )
        ]
    )
    def test_fails_invalid_post_data(
        self, pyramid_config, db_request, post_data, message
    ):
        ...

square = Square(4) # type: Optional[Square]

# Regression test for https://github.com/psf/black/issues/3756.
[
    (
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"  # aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    ),
]
[
    (  # aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"  # aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    ),
]

# output

from .config import (
    Any,
    Bool,
    ConfigType,
    ConfigTypeAttributes,
    Int,
    Path,
    #  String,
    #  resolve_to_config_type,
    #  DEFAULT_TYPE_ATTRIBUTES,
)


from .config import (
    Any,
    Bool,
    ConfigType,
    ConfigTypeAttributes,
    Int,
    no_comma_here_yet,
    #  and some comments,
    #  resolve_to_config_type,
    #  DEFAULT_TYPE_ATTRIBUTES,
)
from com.my_lovely_company.my_lovely_team.my_lovely_project.my_lovely_component import (
    MyLovelyCompanyTeamProjectComponent,  # NOT DRY
)
from com.my_lovely_company.my_lovely_team.my_lovely_project.my_lovely_component import (
    MyLovelyCompanyTeamProjectComponent as component,  # DRY
)


result = 1  # look ma, no comment migration xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

result = 1  # look ma, no comment migration xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

result = (  # aaa
    "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
)

result = (  # aaa
    "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
)


def func():
    c = call(
        0.0123,
        0.0456,
        0.0789,
        0.0123,
        0.0789,
        a[-1],  # type: ignore
    )
    c = call(0.0123, 0.0456, 0.0789, 0.0123, 0.0789, a[-1])  # type: ignore
    c = call(
        0.0123,
        0.0456,
        0.0789,
        0.0123,
        0.0456,
        0.0789,
        0.0123,
        0.0456,
        0.0789,
        a[-1],  # type: ignore
    )

    # The type: ignore exception only applies to line length, not
    # other types of formatting.
    c = call(
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",  # type: ignore
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",
        "aaaaaaaa",
    )


class C:
    @pytest.mark.parametrize(
        ("post_data", "message"),
        [
            # metadata_version errors.
            (
                {},
                (
                    "None is an invalid value for Metadata-Version. Error: This field"
                    " is required. see"
                    " https://packaging.python.org/specifications/core-metadata"
                ),
            ),
            (
                {"metadata_version": "-1"},
                (
                    "'-1' is an invalid value for Metadata-Version. Error: Unknown"
                    " Metadata Version see"
                    " https://packaging.python.org/specifications/core-metadata"
                ),
            ),
            # name errors.
            (
                {"metadata_version": "1.2"},
                (
                    "'' is an invalid value for Name. Error: This field is required."
                    " see https://packaging.python.org/specifications/core-metadata"
                ),
            ),
            (
                {"metadata_version": "1.2", "name": "foo-"},
                (
                    "'foo-' is an invalid value for Name. Error: Must start and end"
                    " with a letter or numeral and contain only ascii numeric and '.',"
                    " '_' and '-'. see"
                    " https://packaging.python.org/specifications/core-metadata"
                ),
            ),
            # version errors.
            (
                {"metadata_version": "1.2", "name": "example"},
                (
                    "'' is an invalid value for Version. Error: This field is required."
                    " see https://packaging.python.org/specifications/core-metadata"
                ),
            ),
            (
                {"metadata_version": "1.2", "name": "example", "version": "dog"},
                (
                    "'dog' is an invalid value for Version. Error: Must start and end"
                    " with a letter or numeral and contain only ascii numeric and '.',"
                    " '_' and '-'. see"
                    " https://packaging.python.org/specifications/core-metadata"
                ),
            ),
        ],
    )
    def test_fails_invalid_post_data(
        self, pyramid_config, db_request, post_data, message
    ): ...


square = Square(4)  # type: Optional[Square]

# Regression test for https://github.com/psf/black/issues/3756.
[
    (  # aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    ),
]
[
    (  # aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"  # aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    ),
]
