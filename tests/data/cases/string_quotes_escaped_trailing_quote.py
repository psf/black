# Regression test for quote normalisation of triple-quoted strings whose body
# already ends in an escaped double quote.
x = '''\'''\"'''
y = b'''\'''\"'''
z = '''a\"'''
# Here the backslashes escape each other, so the trailing quote is bare and
# escaping it would add an escape - the original quotes are kept.
w = '''\\"'''
v = '''a"'''

# output

# Regression test for quote normalisation of triple-quoted strings whose body
# already ends in an escaped double quote.
x = """'''\""""
y = b"""'''\""""
z = """a\""""
# Here the backslashes escape each other, so the trailing quote is bare and
# escaping it would add an escape - the original quotes are kept.
w = '''\\"'''
v = '''a"'''
