with \
     make_context_manager1() as cm1, \
     make_context_manager2() as cm2, \
     make_context_manager3() as cm3, \
     make_context_manager4() as cm4 \
:
    pass


# Leading comment
with \
     make_context_manager1() as cm1, \
     make_context_manager2(), \
     make_context_manager3() as cm3, \
     make_context_manager4() \
:
    pass


with \
     new_new_new1() as cm1, \
     new_new_new2() \
:
    pass


with (
     new_new_new1() as cm1,
     new_new_new2()
):
    pass


# Leading comment.
with (
     # First comment.
     new_new_new1() as cm1,
     # Second comment.
     new_new_new2()
     # Last comment.
):
    pass


with \
    this_is_a_very_long_call(looong_arg1=looong_value1, looong_arg2=looong_value2) as cm1, \
    this_is_a_very_long_call(looong_arg1=looong_value1, looong_arg2=looong_value2, looong_arg3=looong_value3, looong_arg4=looong_value4) as cm2 \
:
    pass


with mock.patch.object(
    self.my_runner, "first_method", autospec=True
) as mock_run_adb, mock.patch.object(
    self.my_runner, "second_method", autospec=True, return_value="foo"
):
    pass


with xxxxxxxx.some_kind_of_method(
    some_argument=[
        "first",
        "second",
        "third",
    ]
).another_method() as cmd:
    pass


async def func():
    async with \
        make_context_manager1() as cm1, \
        make_context_manager2() as cm2, \
        make_context_manager3() as cm3, \
        make_context_manager4() as cm4 \
    :
        pass

    async with some_function(
        argument1, argument2, argument3="some_value"
    ) as some_cm, some_other_function(
        argument1, argument2, argument3="some_value"
    ):
        pass



# don't remove the brackets here, it changes the meaning of the code.
with (x, y) as z:
    pass


# don't remove the brackets here, it changes the meaning of the code.
# even though the code will always trigger a runtime error
with (name_5, name_4), name_5:
    pass


def test_tuple_as_contextmanager():
    from contextlib import nullcontext

    try:
        with (nullcontext(),nullcontext()),nullcontext():
            pass
    except TypeError: 
        # test passed
        pass
    else:
        # this should be a type error
        assert False

# output


with (
    make_context_manager1() as cm1,
    make_context_manager2() as cm2,
    make_context_manager3() as cm3,
    make_context_manager4() as cm4,
):
    pass


# Leading comment
with (
    make_context_manager1() as cm1,
    make_context_manager2(),
    make_context_manager3() as cm3,
    make_context_manager4(),
):
    pass


with new_new_new1() as cm1, new_new_new2():
    pass


with new_new_new1() as cm1, new_new_new2():
    pass


# Leading comment.
with (
    # First comment.
    new_new_new1() as cm1,
    # Second comment.
    new_new_new2(),
    # Last comment.
):
    pass


with (
    this_is_a_very_long_call(
        looong_arg1=looong_value1, looong_arg2=looong_value2
    ) as cm1,
    this_is_a_very_long_call(
        looong_arg1=looong_value1,
        looong_arg2=looong_value2,
        looong_arg3=looong_value3,
        looong_arg4=looong_value4,
    ) as cm2,
):
    pass


with (
    mock.patch.object(self.my_runner, "first_method", autospec=True) as mock_run_adb,
    mock.patch.object(
        self.my_runner, "second_method", autospec=True, return_value="foo"
    ),
):
    pass


with xxxxxxxx.some_kind_of_method(
    some_argument=[
        "first",
        "second",
        "third",
    ]
).another_method() as cmd:
    pass


async def func():
    async with (
        make_context_manager1() as cm1,
        make_context_manager2() as cm2,
        make_context_manager3() as cm3,
        make_context_manager4() as cm4,
    ):
        pass

    async with (
        some_function(argument1, argument2, argument3="some_value") as some_cm,
        some_other_function(argument1, argument2, argument3="some_value"),
    ):
        pass


# don't remove the brackets here, it changes the meaning of the code.
with (x, y) as z:
    pass


# don't remove the brackets here, it changes the meaning of the code.
# even though the code will always trigger a runtime error
with (name_5, name_4), name_5:
    pass


def test_tuple_as_contextmanager():
    from contextlib import nullcontext

    try:
        with (nullcontext(), nullcontext()), nullcontext():
            pass
    except TypeError:
        # test passed
        pass
    else:
        # this should be a type error
        assert False
