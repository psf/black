# flags: --pyi
import sys

class C:
    def before_comment(self) -> None:
        """docs"""
    # leading comment for the next method
    def after_comment(self) -> None: ...
    def before_if(self) -> None:
        """docs"""
    if sys.version_info >= (3, 12):
        if_attr: int
