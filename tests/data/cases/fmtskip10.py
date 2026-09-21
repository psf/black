def foo(): return "mock"  # fmt: skip
if True: print("yay")  # fmt: skip
for i in range(10): print(i)  # fmt: skip
if True: print("this"); print("that")  # fmt: skip
while True: print("loop"); break  # fmt: skip
for x in [1, 2]: print(x); print("done")  # fmt: skip
def f(x: int): return x # fmt: skip

j =     1 # fmt: skip
while j < 10: j += 1  # fmt: skip

b = [c for c in "A very long string that would normally generate some kind of collapse, since it is this long"] # fmt: skip

v = (
    foo_dict  # fmt: skip
    .setdefault("a", {})
    .setdefault("b", {})
    .setdefault("c", {})
    .setdefault("d", {})
    .setdefault("e", {})
)


async def afn():
    async with give_me_async_context(): print("a"); print("b")  # fmt: skip
    async for i in some_async_iter(): print(i); print("done")  # fmt: skip
    async def inner(): x = 1; return x  # fmt: skip
