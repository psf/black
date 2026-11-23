# flags: --preview --line-length 40
first_condition and second_condition and third_condition and fourth_condition
first_condition or second_condition or third_condition or fourth_condition
a and b

a and not b or third_condition or fourth_condition

def example():
    first_condition and second_condition and third_condition and fourth_condition

# output
(
    first_condition
    and second_condition
    and third_condition
    and fourth_condition
)
(
    first_condition
    or second_condition
    or third_condition
    or fourth_condition
)
a and b

(
    a
    and not b
    or third_condition
    or fourth_condition
)


def example():
    (
        first_condition
        and second_condition
        and third_condition
        and fourth_condition
    )
