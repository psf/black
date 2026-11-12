# `# fmt: skip` on one-line clauses with semicolon-separated bodies that follow
# another skipped one-line clause of the same statement.
if x: f(); g()  # fmt: skip
else: f(); g()  # fmt: skip
if x: a; b  # fmt: skip
elif y: a; b  # fmt: skip
else: a; b  # fmt: skip
try: f(); g()  # fmt: skip
except E: f(); g()  # fmt: skip
finally: f(); g()  # fmt: skip
try:
    pass
except E: f(); g()  # fmt: skip
else: f(); g()  # fmt: skip
for i in r: f(); g()  # fmt: skip
else: f(); g()  # fmt: skip
while x: f(); g()  # fmt: skip
else: a; b  # fmt: skip


async def h():
    async for i in r: f(); g()  # fmt: skip
    else: f(); g()  # fmt: skip
x  =  1

# output
# `# fmt: skip` on one-line clauses with semicolon-separated bodies that follow
# another skipped one-line clause of the same statement.
if x: f(); g()  # fmt: skip
else: f(); g()  # fmt: skip
if x: a; b  # fmt: skip
elif y: a; b  # fmt: skip
else: a; b  # fmt: skip
try: f(); g()  # fmt: skip
except E: f(); g()  # fmt: skip
finally: f(); g()  # fmt: skip
try:
    pass
except E: f(); g()  # fmt: skip
else: f(); g()  # fmt: skip
for i in r: f(); g()  # fmt: skip
else: f(); g()  # fmt: skip
while x: f(); g()  # fmt: skip
else: a; b  # fmt: skip


async def h():
    async for i in r: f(); g()  # fmt: skip
    else: f(); g()  # fmt: skip


x = 1
