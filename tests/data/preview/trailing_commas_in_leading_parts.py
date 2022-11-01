zero(
    one,
).two(
    three,
).four(
    five,
)

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
