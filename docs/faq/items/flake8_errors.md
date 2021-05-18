# Why are Flake8's E203 and W503 violated?

Because they go against PEP 8. E203 falsely triggers on list
[slices](../../the_black_code_style/current_style.md#slices), and adhering to W503
hinders readability because operators are misaligned. Disable W503 and enable the
disabled-by-default counterpart W504. E203 should be disabled while changes are still
[discussed](https://github.com/PyCQA/pycodestyle/issues/373).
