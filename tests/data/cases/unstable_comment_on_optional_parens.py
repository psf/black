# Regression for https://github.com/psf/black/issues/3701
# Inline comment on optional parentheses must not migrate across formatter passes.
assert some_long_name, (  # long __________________________ comment
        'long ___________________________________ string %s' % str(variable))


# Related case from https://github.com/psf/black/issues/4384
if 1:
    takeoff_effective_friction_coefficient = (  # From Torenbeek, Eq. 5-76; an approximation
            friction_coefficient +
            0.72 * (CD_zero_lift / CL_max)
    )

# output

# Regression for https://github.com/psf/black/issues/3701
# Inline comment on optional parentheses must not migrate across formatter passes.
assert some_long_name, (  # long __________________________ comment
    "long ___________________________________ string %s" % str(variable)
)


# Related case from https://github.com/psf/black/issues/4384
if 1:
    takeoff_effective_friction_coefficient = (  # From Torenbeek, Eq. 5-76; an approximation
        friction_coefficient + 0.72 * (CD_zero_lift / CL_max)
    )
