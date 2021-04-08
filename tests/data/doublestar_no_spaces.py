#!/usr/bin/env python3.7


def function(**kwargs):
    t = a**2 + b**3


def function_no_spaces():
    return t**2


def function_replace_spaces(**kwargs):
    t = a **2 + b** 3 + c ** 4


def function_dont_replace_spaces():
    t = t ** 2
    {**a, **b, **c}



# output


#!/usr/bin/env python3.7


def function(**kwargs):
    t = a**2 + b**3


def function_no_spaces():
    return t ** 2


def function_replace_spaces(**kwargs):
    t = a**2 + b**3 + c**4


def function_dont_replace_spaces():
    t = t ** 2
    {**a, **b, **c}

