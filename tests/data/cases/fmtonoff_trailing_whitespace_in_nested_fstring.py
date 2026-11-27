# flags: --minimum-version=3.14
# Trailing whitespace after `# fmt: off` in a field where Python keeps the source
# as text. Python also keeps the comments of a nested f-string there, so the
# whitespace has to stay.

x = f"{f'{b
# fmt: off   
+ c}'=}"

x = f"{f'{b
    # comment   
    # fmt: off	
    +  c}' = }"

x = f"{f'{b
# fmt: off   
# fmt: on   
+ c}'=}"

x = f"""{f'''{[a,
    # fmt: off   
    b]}'''=!r}"""

x = f"{t'{b
# fmt: off   
+ c}'=}"

x = t"{f'{b
# fmt: off   
+ c}'}"

x = f"{b
# fmt: off   
+ c=}"
