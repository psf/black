values = [item.value for item in  # type: ignore[attr-defined]
    items  # type: ignore[union-attr]
]

values = [item.value for item  # type: ignore[attr-defined]
    in items  # type: ignore[union-attr]
]

values = [item for item in items if  # type: ignore[operator]
    item > 0  # type: ignore[operator]
]

mapping = {key: value for key, value in  # type: ignore[attr-defined]
    data.items()  # type: ignore[union-attr]
}

total = sum(item.value for item in  # type: ignore[attr-defined]
    items  # type: ignore[union-attr]
)

callbacks = [lambda item  # type: ignore[misc]
    : item.value  # type: ignore[attr-defined]
]


# output
values = [
    item.value
    for item in  # type: ignore[attr-defined]
    items  # type: ignore[union-attr]
]

values = [
    item.value
    for item  # type: ignore[attr-defined]
    in items  # type: ignore[union-attr]
]

values = [
    item
    for item in items  # type: ignore[operator]
    if item > 0  # type: ignore[operator]
]

mapping = {
    key: value
    for key, value in  # type: ignore[attr-defined]
    data.items()  # type: ignore[union-attr]
}

total = sum(
    item.value
    for item in  # type: ignore[attr-defined]
    items  # type: ignore[union-attr]
)

callbacks = [
    lambda item  # type: ignore[misc]
    : item.value  # type: ignore[attr-defined]
]
