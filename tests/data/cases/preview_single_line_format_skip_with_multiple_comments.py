# flags: --preview
foo =  123  # fmt: skip # noqa: E501 # pylint
bar =    (
    123   ,
    (        1      +           5      )  # pylint # fmt:skip
)
baz = "a"    +   "b"  # pylint; fmt: skip; noqa: E501
skip_will_not_work =  "a" +  "b"  # pylint fmt:skip
skip_will_not_work2 =  "a" +  "b"  # some text; fmt:skip happens to be part of it

# output

foo =  123  # fmt: skip # noqa: E501 # pylint
bar = (
    123   ,
    (        1      +           5      )  # pylint # fmt:skip
)
baz = "a"    +   "b"  # pylint; fmt: skip; noqa: E501
skip_will_not_work = "a" + "b"  # pylint fmt:skip
skip_will_not_work2 = "a" + "b"  # some text; fmt:skip happens to be part of it
