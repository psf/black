#!/usr/bin/env python3
import asyncio
import sys

from third_party import X, Y, Z

from library import some_connection, \
                    some_decorator
f'trigger 3.6 mode'
def func_no_args():
  a; b; c
  if True: raise RuntimeError
  if False: ...
  for i in range(10):
    print(i)
    continue
  return None
async def coroutine(arg):
 "Single-line docstring. Multiline is harder to reformat."
 async with some_connection() as conn:
     await conn.do_what_i_mean('SELECT bobby, tables FROM xkcd', timeout=2)
 await asyncio.sleep(1)
@asyncio.coroutine
@some_decorator(
with_args=True,
many_args=[1,2,3]
)
def function_signature_stress_test(number:int,no_annotation=None,text:str="default",* ,debug:bool=False,**kwargs) -> str:
 return text[number:-1]
def spaces(a=1, b=(), c=[], d={}, e=True, f=-1, g=1 if False else 2, h="", i=r''):
 offset = attr.ib(default=attr.Factory( lambda: _r.uniform(10000, 200000)))
 assert task._cancel_stack[:len(old_stack)] == old_stack
def spaces2(result= _core.Value(None)):
 ...

def long_lines():
    if True:
        typedargslist.extend(
            gen_annotated_params(ast_args.kwonlyargs, ast_args.kw_defaults, parameters, implicit_default=True)
        )
    _type_comment_re = re.compile(
        r"""
        ^
        [\t ]*
        \#[ ]type:[ ]*
        (?P<type>
            [^#\t\n]+?
        )
        (?<!ignore)     # note: this will force the non-greedy + in <type> to match
                        # a trailing space which is why we need the silliness below
        (?<!ignore[ ]{1})(?<!ignore[ ]{2})(?<!ignore[ ]{3})(?<!ignore[ ]{4})
        (?<!ignore[ ]{5})(?<!ignore[ ]{6})(?<!ignore[ ]{7})(?<!ignore[ ]{8})
        (?<!ignore[ ]{9})(?<!ignore[ ]{10})
        [\t ]*
        (?P<nl>
            (?:\#[^\n]*)?
            \n?
        )
        $
        """, re.MULTILINE | re.VERBOSE
    )

# output


#!/usr/bin/env python3
import asyncio
import sys

from third_party import X, Y, Z

from library import some_connection, some_decorator

f'trigger 3.6 mode'


def func_no_args():
    a
    b
    c
    if True:
        raise RuntimeError

    if False:
        ...
    for i in range(10):
        print(i)
        continue

    return None


async def coroutine(arg):
    "Single-line docstring. Multiline is harder to reformat."
    async with some_connection() as conn:
        await conn.do_what_i_mean('SELECT bobby, tables FROM xkcd', timeout=2)
    await asyncio.sleep(1)


@asyncio.coroutine
@some_decorator(with_args=True, many_args=[1, 2, 3])
def function_signature_stress_test(
    number: int,
    no_annotation=None,
    text: str = "default",
    *,
    debug: bool = False,
    **kwargs,
) -> str:
    return text[number:-1]


def spaces(a=1, b=(), c=[], d={}, e=True, f=-1, g=1 if False else 2, h="", i=r''):
    offset = attr.ib(default=attr.Factory(lambda: _r.uniform(10000, 200000)))
    assert task._cancel_stack[:len(old_stack)] == old_stack


def spaces2(result=_core.Value(None)):
    ...


def long_lines():
    if True:
        typedargslist.extend(
            gen_annotated_params(
                ast_args.kwonlyargs,
                ast_args.kw_defaults,
                parameters,
                implicit_default=True,
            )
        )
    _type_comment_re = re.compile(
        r"""
        ^
        [\t ]*
        \#[ ]type:[ ]*
        (?P<type>
            [^#\t\n]+?
        )
        (?<!ignore)     # note: this will force the non-greedy + in <type> to match
                        # a trailing space which is why we need the silliness below
        (?<!ignore[ ]{1})(?<!ignore[ ]{2})(?<!ignore[ ]{3})(?<!ignore[ ]{4})
        (?<!ignore[ ]{5})(?<!ignore[ ]{6})(?<!ignore[ ]{7})(?<!ignore[ ]{8})
        (?<!ignore[ ]{9})(?<!ignore[ ]{10})
        [\t ]*
        (?P<nl>
            (?:\#[^\n]*)?
            \n?
        )
        $
        """,
        re.MULTILINE | re.VERBOSE,
    )
