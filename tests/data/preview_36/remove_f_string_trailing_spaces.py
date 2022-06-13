print(f"there are { 2 } unnecessary spaces in this f string")
print(f"there are {   3} unnecessary spaces on the left")
print(f"there are {3   } unnecessary spaces on the right")
print(f"you should trim { 'me' } and {   'me!'  }")
print(f"trimming is easy as {  1    +     1   } == {2}")
print("There should be no trimming if {    f_prefix     } is not present")
print(f"No {  'trimming' } if we use {{ double_curly_brackets   }} in string")
print(
    "We know how to trim strings in any case needed, even when the strings are joined. "
    f"Just take a look {  'here' } and you'll see that the problem is solved."
)
print(f"{ bar : .{ baz }f }")

# output

print(f"there are {2} unnecessary spaces in this f string")
print(f"there are {3} unnecessary spaces on the left")
print(f"there are {3} unnecessary spaces on the right")
print(f"you should trim {'me'} and {'me!'}")
print(f"trimming is easy as {1 + 1} == {2}")
print("There should be no trimming if {    f_prefix     } is not present")
print(f"No {'trimming'} if we use {{ double_curly_brackets   }} in string")
print(
    "We know how to trim strings in any case needed, even when the strings are joined."
    f" Just take a look {'here'} and you'll see that the problem is solved."
)
print(f"{bar:.{baz}f}")
