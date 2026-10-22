# flags: --pyx
cimport cython
cimport numpy as np, libc.math
from libc.stdlib cimport malloc,free
from libc.string cimport (memcpy)
from cpython.object cimport *
from . cimport sibling
from ..pkg.sub cimport (first_name_that_is_long, second_name_that_is_long, third_name_that_is_long)
import numpy as np
cdef int x = 1
# output
cimport cython
cimport numpy as np, libc.math
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy
from cpython.object cimport *
from . cimport sibling
from ..pkg.sub cimport (
    first_name_that_is_long,
    second_name_that_is_long,
    third_name_that_is_long,
)
import numpy as np

cdef int x = 1
