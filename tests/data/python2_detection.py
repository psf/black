# This uses a similar construction to the decorators.py test data file FYI.

print "hello, world!"

###

exec "print('hello, world!')"

###

def set_position((x, y), value):
    pass

###

try:
    pass
except Exception, err:
    pass

###

raise RuntimeError, "I feel like crashing today :p"

###

`wow_these_really_did_exist`

###

10L

# output

print("hello python three!")

###

exec("I'm not sure if you can use exec like this but that's not important here!")

###

try:
    pass
except make_exception(1, 2):
    pass

###

try:
    pass
except Exception as err:
    pass

###

raise RuntimeError(make_msg(1, 2))

###

def set_position(x, y, value):
    pass

###

10
