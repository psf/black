from pathlib import Path

from pysource_codegen import generate
from pysource_minimize import minimize

import black

base_path = Path(__file__).parent


def bug_in_code(src_contents: str, mode: black.FileMode) -> bool:
    try:
        dst_contents = black.format_str(src_contents, mode=mode)

        black.assert_equivalent(src_contents, dst_contents)
        black.assert_stable(src_contents, dst_contents, mode=mode)
    except Exception as e:
        print("error:", e)
        return True
    return False


def find_issue() -> None:
    mode = black.FileMode(
        line_length=80,
        string_normalization=True,
        is_pyi=False,
        magic_trailing_comma=False,
    )
    for seed in range(1000):
        src_code = generate(seed)
        print("seed:", seed)

        compile(src_code, "<string>", "exec")

        if bug_in_code(src_code, mode):
            minimized = minimize(src_code, lambda code: bug_in_code(code, mode))
            assert bug_in_code(minimized, mode)

            print("seed:", seed)
            print("minimized code:")
            print(minimized)

            if "with" in minimized:
                # propably known issue
                # https://github.com/psf/black/issues/3678
                # https://github.com/psf/black/issues/3677
                continue

            (base_path / "min_code.py").write_text(minimized)
            return


if __name__ == "__main__":
    find_issue()
