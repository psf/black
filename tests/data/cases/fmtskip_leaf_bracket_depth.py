# A `# fmt: skip` on a line with multiple inline comments used to crash
# `is_line_short_enough` with `AttributeError: 'Leaf' object has no attribute 'bracket_depth'`.

with tempfile.TemporaryDirectory() as fp:
    path_alternative_dest_folder_1 = fp
    reg = ExtractorLoggingConfig(  # type: ignore[arg-type]  # pyright: ignore[something]  # fmt: skip
        package_name_raw,
        path_alternative_dest_folder=path_alternative_dest_folder_1,  # type: ignore[arg-type]
        is_test_file=is_test_file_1,
    )

func(  # type: ignore[arg-type]  # pyright: ignore[something]  # fmt: skip
    arg1,
    kwarg=val,  # type: ignore[arg-type]
    arg2=val2,
)
