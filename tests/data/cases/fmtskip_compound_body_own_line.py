# `# fmt: skip` on a semicolon-separated body that is on its own line under a
# compound statement header. Only the body line is skipped: it must stay on its
# own line, and the header is formatted as usual.
if   x  :
    a; b  # fmt: skip
if x:
    print( 1 ); print(2)  # fmt: skip
elif y:
    a  ;  b  # fmt: skip
else:
    f(); g()  # fmt: skip
while x:
    a; b  # fmt: skip
for i in  range(3):
    a; b  # fmt: skip
with open( f ) as g:
    a; b  # fmt: skip
try:
    a; b  # fmt: skip
except E:
    a; b  # fmt: skip
finally:
    a; b  # fmt: skip
class C:
    a = 1; b = 2  # fmt: skip
def f( x ):
    a; return x  # fmt: skip
async def g():
    async with x:
        a; b  # fmt: skip
    async for i in y:
        a; b  # fmt: skip

# output
# `# fmt: skip` on a semicolon-separated body that is on its own line under a
# compound statement header. Only the body line is skipped: it must stay on its
# own line, and the header is formatted as usual.
if x:
    a; b  # fmt: skip
if x:
    print( 1 ); print(2)  # fmt: skip
elif y:
    a  ;  b  # fmt: skip
else:
    f(); g()  # fmt: skip
while x:
    a; b  # fmt: skip
for i in range(3):
    a; b  # fmt: skip
with open(f) as g:
    a; b  # fmt: skip
try:
    a; b  # fmt: skip
except E:
    a; b  # fmt: skip
finally:
    a; b  # fmt: skip


class C:
    a = 1; b = 2  # fmt: skip


def f(x):
    a; return x  # fmt: skip


async def g():
    async with x:
        a; b  # fmt: skip
    async for i in y:
        a; b  # fmt: skip
