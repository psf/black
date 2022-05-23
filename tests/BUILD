python_test_utils(
    name="test_utils",
    sources=["conftest.py", "optional.py", "util.py"],
    overrides={
        "conftest.py": {"dependencies": ["tests/optional.py:test_utils"]},
        "util.py": {"dependencies": ["tests/data"]},
    },
)

files(
    name="toml",
    sources=["*.toml"],
)

multi_interpreter_python_tests(
    name="tests",
    overrides={
        "test_black.py": {"dependencies": [":toml"]},
        "test_blackd.py": {"dependencies": ["src:extra-d"]},
        "test_format.py": {"dependencies": ["//:test_format_files"]},
        "test_ipynb.py": {"dependencies": ["src:extra-jupyter"]},
        "test_no_ipynb.py": {"dependencies": ["src:extra-jupyter"]},
    },
)
