a, b, c = 3, 4,       5
if (
    a ==    3
    and b    != 9  # fmt: skip
    and c is not None
):
    print("I'm good!")
else:
    print("I'm bad")

if (
    a ==    3  # fmt: skip
    and b    != 9  # fmt: skip
    and c is not None
):
    print("I'm good!")
else:
    print("I'm bad")

x = [
    1      ,  # fmt: skip
    2   ,
    3 , 4  # fmt: skip
]

# output

a, b, c = 3, 4, 5
if (
    a == 3
    and b    != 9  # fmt: skip
    and c is not None
):
    print("I'm good!")
else:
    print("I'm bad")

if (
    a ==    3  # fmt: skip
    and b    != 9  # fmt: skip
    and c is not None
):
    print("I'm good!")
else:
    print("I'm bad")

x = [
    1      ,  # fmt: skip
    2,
    3 , 4  # fmt: skip
]
