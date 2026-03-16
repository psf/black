# flags: --minimum-version=3.12 --target-version=py312
# this is invalid in versions below py312
class ClassA[T: str]:
    def method1(self) -> T:
        ...

# output
# this is invalid in versions below py312
class ClassA[T: str]:
    def method1(self) -> T: ...
