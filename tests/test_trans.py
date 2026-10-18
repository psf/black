import pytest

from black import Mode
from black.mode import Preview
from black.trans import iter_fexpr_spans
from tests.util import assert_format


@pytest.mark.parametrize(
    "operator",
    ["+=", "-=", "*=", "@=", "/=", "//=", "%=", "**=", "<<=", ">>=", "&=", "|=", "^="],
)
@pytest.mark.parametrize("string", ["directory subdirectory file.txt", "foo bar"])
def test_string_splitting_augmented_assignment(operator: str, string: str) -> None:
    target = "x" if string.startswith("directory") else "variable"
    source = f'{target} {operator} "{string}"\n'
    strings = (
        '    "directory"\n    " subdirectory"\n    " file.txt"\n'
        if string.startswith("directory")
        else '    "foo bar"\n'
    )
    expected = f"{target} {operator} (\n{strings})\n"
    mode = Mode(
        line_length=20, preview=True, enabled_features={Preview.string_processing}
    )
    assert_format(source, expected, mode=mode)
    stable_expected = source if string.startswith("directory") else expected
    assert_format(source, stable_expected, mode=Mode(line_length=20))


@pytest.mark.parametrize(
    "operator",
    ["+", "-", "*", "@", "/", "//", "%", "**", "<<", ">>", "&", "|", "^"],
)
def test_string_splitting_overloaded_binary_operator(operator: str) -> None:
    source = f'x {operator} "directory subdirectory file.txt"\n'
    expected = (
        f'x {operator} (\n    "directory"\n    " subdirectory"\n    " file.txt"\n)\n'
    )
    mode = Mode(
        line_length=20, preview=True, enabled_features={Preview.string_processing}
    )
    assert_format(source, expected, mode=mode)


@pytest.mark.parametrize("operator", ["*", "@", "/", "//", "%", "**"])
def test_string_splitting_preserves_operator_precedence(operator: str) -> None:
    source = f'x {operator} "directory subdirectory file.txt" % y\n'
    mode = Mode(
        line_length=20, preview=True, enabled_features={Preview.string_processing}
    )
    assert_format(source, source, mode=mode)


def test_fexpr_spans() -> None:
    def check(
        string: str, expected_spans: list[tuple[int, int]], expected_slices: list[str]
    ) -> None:
        spans = list(iter_fexpr_spans(string))

        # Checking slices isn't strictly necessary, but it's easier to verify at
        # a glance than only spans
        assert len(spans) == len(expected_slices)
        for (i, j), slice in zip(spans, expected_slices, strict=True):
            assert 0 <= i <= j <= len(string)
            assert string[i:j] == slice

        assert spans == expected_spans

    # Most of these test cases omit the leading 'f' and leading / closing quotes
    # for convenience
    # Some additional property-based tests can be found in
    # https://github.com/psf/black/pull/2654#issuecomment-981411748
    check("""{var}""", [(0, 5)], ["{var}"])
    check("""f'{var}'""", [(2, 7)], ["{var}"])
    check("""f'{1 + f() + 2 + "asdf"}'""", [(2, 24)], ["""{1 + f() + 2 + "asdf"}"""])
    check("""text {var} text""", [(5, 10)], ["{var}"])
    check("""text {{ {var} }} text""", [(8, 13)], ["{var}"])
    check("""{a} {b} {c}""", [(0, 3), (4, 7), (8, 11)], ["{a}", "{b}", "{c}"])
    check("""f'{a} {b} {c}'""", [(2, 5), (6, 9), (10, 13)], ["{a}", "{b}", "{c}"])
    check("""{ {} }""", [(0, 6)], ["{ {} }"])
    check("""{ {{}} }""", [(0, 8)], ["{ {{}} }"])
    check("""{ {{{}}} }""", [(0, 10)], ["{ {{{}}} }"])
    check("""{{ {{{}}} }}""", [(5, 7)], ["{}"])
    check("""{{ {{{var}}} }}""", [(5, 10)], ["{var}"])
    check("""{f"{0}"}""", [(0, 8)], ["""{f"{0}"}"""])
    check("""{"'"}""", [(0, 5)], ["""{"'"}"""])
    check("""{"{"}""", [(0, 5)], ["""{"{"}"""])
    check("""{"}"}""", [(0, 5)], ["""{"}"}"""])
    check("""{"{{"}""", [(0, 6)], ["""{"{{"}"""])
    check("""{''' '''}""", [(0, 9)], ["""{''' '''}"""])
    check("""{'''{'''}""", [(0, 9)], ["""{'''{'''}"""])
    check("""{''' {'{ '''}""", [(0, 13)], ["""{''' {'{ '''}"""])
    check(
        '''f\'\'\'-{f"""*{f"+{f'.{x}.'}+"}*"""}-'y\\'\'\'\'''',
        [(5, 33)],
        ['''{f"""*{f"+{f'.{x}.'}+"}*"""}'''],
    )
    check(r"""{}{""", [(0, 2)], ["{}"])
    check("""f"{'{'''''''''}\"""", [(2, 15)], ["{'{'''''''''}"])
