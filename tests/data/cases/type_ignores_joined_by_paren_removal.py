x = (
    f(a)  # type: ignore[arg-type]
)  # type: ignore[assignment]

x = (
    [a]  # type: ignore[arg-type]
)  # type: ignore[assignment]

x = (
    f(a).run  # type: ignore[arg-type]
)  # type: ignore[assignment]

current_callable = (
    torch._C._aoti.AOTIModelContainerRunnerCuda(  # type: ignore[call-arg]
        current_callable,
        1,
        self.device_type,
        "",
        True,
    ).run  # type: ignore[attr-defined]
)  # type: ignore[attr-defined]

# A single `# type: ignore` still allows removing the parentheses.

x = (
    f(a)  # type: ignore[arg-type]
)

# output

x = (
    f(a)  # type: ignore[arg-type]
)  # type: ignore[assignment]

x = (
    [a]  # type: ignore[arg-type]
)  # type: ignore[assignment]

x = (
    f(a).run  # type: ignore[arg-type]
)  # type: ignore[assignment]

current_callable = (
    torch._C._aoti.AOTIModelContainerRunnerCuda(  # type: ignore[call-arg]
    current_callable,
    1,
    self.device_type,
    "",
    True,
    ).run  # type: ignore[attr-defined]
)  # type: ignore[attr-defined]

# A single `# type: ignore` still allows removing the parentheses.

x = f(a)  # type: ignore[arg-type]
