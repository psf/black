# flags: --pyx
a = u'text'
b = U'text'
c = B'text'
d = F'{a}'
# output
a = u"text"
b = u"text"
c = b"text"
d = f"{a}"
