x = (
    f(a)  # type: ignore[arg-type]
)  # type: ignore[assignment]

x = (
    [a]  # type: ignore[list-item]
)  # type: ignore[assignment]

x = (
    f(a).run  # type: ignore[attr-defined]
)  # type: ignore[assignment]

x = (
    y  # type: ignore[arg-type]
)  # type: ignore[assignment]

x = (
    y.attr  # type: ignore[attr-defined]
)  # type: ignore[assignment]

x = (
    a[0]  # type: ignore[index]
)  # type: ignore[assignment]

x = (
    {a: b}  # type: ignore[dict-item]
)  # type: ignore[assignment]

x = (
    (a, b)  # type: ignore[arg-type]
)  # type: ignore[assignment]

x = (
    (
        f(a)  # type: ignore[arg-type]
    )  # type: ignore[assignment]
)  # type: ignore[misc]

x = (
    f(
        a,  # type: ignore[arg-type]
    )  # type: ignore[call-arg]
)  # type: ignore[assignment]


def get_runner():
    current_callable = (
        torch._C._aoti.AOTIModelContainerRunnerCuda(  # type: ignore[call-arg]
            current_callable,
            1,
            self.device_type,
            "",
            True,
        ).run  # type: ignore[attr-defined]
    )  # type: ignore[attr-defined]


x = f(a)  # type: ignore[arg-type]  # type: ignore[assignment]

x = (
    f(a)  # type: ignore[arg-type]
)  # comment

x = (
    f(a)  # comment
)  # type: ignore[assignment]

# output
x = (
    f(a)  # type: ignore[arg-type]
)  # type: ignore[assignment]

x = (
    [a]  # type: ignore[list-item]
)  # type: ignore[assignment]

x = (
    f(a).run  # type: ignore[attr-defined]
)  # type: ignore[assignment]

x = (
    y  # type: ignore[arg-type]
)  # type: ignore[assignment]

x = (
    y.attr  # type: ignore[attr-defined]
)  # type: ignore[assignment]

x = (
    a[0]  # type: ignore[index]
)  # type: ignore[assignment]

x = (
    {a: b}  # type: ignore[dict-item]
)  # type: ignore[assignment]

x = (
    (a, b)  # type: ignore[arg-type]
)  # type: ignore[assignment]

x = (
    f(a)  # type: ignore[arg-type]
    # type: ignore[assignment]
)  # type: ignore[misc]

x = (
    f(
        a,  # type: ignore[arg-type]
    )  # type: ignore[call-arg]
)  # type: ignore[assignment]


def get_runner():
    current_callable = (
        torch._C._aoti.AOTIModelContainerRunnerCuda(  # type: ignore[call-arg]
        current_callable,
        1,
        self.device_type,
        "",
        True,
        ).run  # type: ignore[attr-defined]
    )  # type: ignore[attr-defined]


x = f(a)  # type: ignore[arg-type]  # type: ignore[assignment]

x = f(a)  # type: ignore[arg-type]  # comment

x = f(a)  # type: ignore[assignment]  # comment
