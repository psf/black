'\''
'"'
"'"
"\""
"Hello"
"Don't do that"
'Here is a "'
'What\'s the deal here?'
"What's the deal \"here\"?"
"And \"here\"?"
"""Strings with "" in them"""
'''Strings with "" in them'''
'''Here's a "'''
'''Here's a " '''
'''Just a normal triple
quote'''
f"just a normal {f} string"
f'''This is a triple-quoted {f}-string'''
f'MOAR {" ".join([])}'
f"MOAR {' '.join([])}"
r"raw string ftw"
r'Date d\'expiration:(.*)'
r'Tricky "quote'
r'Not-so-tricky \"quote'
'\n\
The \"quick\"\n\
brown fox\n\
jumps over\n\
the \'lazy\' dog.\n\
'
re.compile(r'[\\"]')

# output

"'"
'"'
"'"
'"'
"Hello"
"Don't do that"
'Here is a "'
"What's the deal here?"
'What\'s the deal "here"?'
'And "here"?'
"""Strings with "" in them"""
"""Strings with "" in them"""
'''Here's a "'''
"""Here's a " """
"""Just a normal triple
quote"""
f"just a normal {f} string"
f"""This is a triple-quoted {f}-string"""
f'MOAR {" ".join([])}'
f"MOAR {' '.join([])}"
r"raw string ftw"
r"Date d\'expiration:(.*)"
r'Tricky "quote'
r"Not-so-tricky \"quote"
"\n\
The \"quick\"\n\
brown fox\n\
jumps over\n\
the 'lazy' dog.\n\
"
re.compile(r'[\\"]')
