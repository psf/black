# This file doesn't used any Python 3.9+ only grammars.


with \
     make_context_manager1() as cm1, \
     make_context_manager2() as cm2, \
     make_context_manager3() as cm3, \
     make_context_manager4() as cm4 \
:
    pass


# output
# This file doesn't used any Python 3.9+ only grammars.


with make_context_manager1() as cm1, make_context_manager2() as cm2, make_context_manager3() as cm3, make_context_manager4() as cm4:
    pass
