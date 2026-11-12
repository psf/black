# flags: --unstable --line-length=46

x = r"你你你你你你你你你你" r"好好好好好好好好好好"
exact = r"aaaaaaaaaaaaaaa" r"bbbbbbbbbbbbbbbbbbbb"

# output

x = (
    r"你你你你你你你你你你"
    r"好好好好好好好好好好"
)
exact = r"aaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbbbb"
