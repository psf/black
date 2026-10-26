# A standalone comment between `lambda` and its parameters puts the parameters on a
# line without `lambda`. Their commas must not be split like tuple elements.
f = (
    lambda  # comment 1
    # comment 2
    *args, **kwargs: # comment 3
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa(*args, **kwargs) + 1
)

g = (
    lambda
    # comment
    x, y=1, *z: (x, y, z)
)

# output
# A standalone comment between `lambda` and its parameters puts the parameters on a
# line without `lambda`. Their commas must not be split like tuple elements.
f = (
    lambda  # comment 1
    # comment 2
    *args, **kwargs: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa(  # comment 3
        *args, **kwargs
    )
    + 1
)

g = (
    lambda
    # comment
    x, y=1, *z: (x, y, z)
)
