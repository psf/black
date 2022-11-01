zero(
    one,
).two(
    three,
).four(
    five,
)

func1(arg1).func2(arg2,).func3(arg3).func4(arg4,).func5(arg5)

# Inner one-element tuple shouldn't explode
func1(arg1).func2(arg1, (one_tuple,)).func3(arg3)

(
    a,
    b,
    c,
    d,
) = func1(
    arg1
) and func2(arg2)


# Example from https://github.com/psf/black/issues/3229
def refresh_token(self, device_family, refresh_token, api_key):
    return self.orchestration.refresh_token(
        data={
            "refreshToken": refresh_token,
        },
        api_key=api_key,
    )["extensions"]["sdk"]["token"]


# output


zero(
    one,
).two(
    three,
).four(
    five,
)

func1(arg1).func2(
    arg2,
).func3(arg3).func4(
    arg4,
).func5(arg5)

# Inner one-element tuple shouldn't explode
func1(arg1).func2(arg1, (one_tuple,)).func3(arg3)

(
    a,
    b,
    c,
    d,
) = func1(
    arg1
) and func2(arg2)


# Example from https://github.com/psf/black/issues/3229
def refresh_token(self, device_family, refresh_token, api_key):
    return self.orchestration.refresh_token(
        data={
            "refreshToken": refresh_token,
        },
        api_key=api_key,
    )["extensions"]["sdk"]["token"]
