# flags: --preview
XpressDirect._addCols = lambda self, prob, objx, mstart, mrwind, dmatval, bdl, bdu, names, types: prob.addcols(objx, mstart, mrwind, dmatval, bdl, bdu, names, types)
result = lambda value: calculate(value, additional_positional_argument, another_positional_argument)
XpressDirect._addCols = lambda a_very_long_parameter_name, a_second_very_long_parameter_name, a_third_very_long_parameter_name: calculate(a_very_long_parameter_name, a_second_very_long_parameter_name, a_third_very_long_parameter_name)


def type_ignore_control():
    if condition:
        if condition:
            factory = lambda x, **kwds: PeriodIndex.from_ordinals(  # type: ignore[assignment]
                x, freq=kwds.get("freq", None)
            )._rename(kwds["name"])


def subscript_target_control():
    if condition:
        if condition:
            if condition:
                _composite_getters[self.composite_class] = (
                    lambda obj: obj.__composite_values__()
                )

# output
XpressDirect._addCols = (
    lambda self, prob, objx, mstart, mrwind, dmatval, bdl, bdu, names, types: (
        prob.addcols(objx, mstart, mrwind, dmatval, bdl, bdu, names, types)
    )
)
result = lambda value: calculate(
    value, additional_positional_argument, another_positional_argument
)
XpressDirect._addCols = (
    lambda a_very_long_parameter_name, a_second_very_long_parameter_name, a_third_very_long_parameter_name: calculate(
        a_very_long_parameter_name,
        a_second_very_long_parameter_name,
        a_third_very_long_parameter_name,
    )
)


def type_ignore_control():
    if condition:
        if condition:
            factory = lambda x, **kwds: PeriodIndex.from_ordinals(  # type: ignore[assignment]
                x, freq=kwds.get("freq", None)
            )._rename(kwds["name"])


def subscript_target_control():
    if condition:
        if condition:
            if condition:
                _composite_getters[self.composite_class] = (
                    lambda obj: obj.__composite_values__()
                )
