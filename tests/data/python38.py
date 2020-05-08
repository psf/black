#!/usr/bin/env python3.8


def starred_return():
    my_list = ["value2", "value3"]
    return "value1", *my_list


def starred_yield():
    my_list = ["value2", "value3"]
    yield "value1", *my_list


# output


#!/usr/bin/env python3.8


def starred_return():
    my_list = ["value2", "value3"]
    return "value1", *my_list


def starred_yield():
    my_list = ["value2", "value3"]
    yield "value1", *my_list
