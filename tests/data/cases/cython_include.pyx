# flags: --pyx
cimport cython
from libc.stdlib cimport malloc
include 'includes/consts.pxi'
include "includes/stdlib.pxi"
import os
x = 1
cdef class Loop:
    cdef int y
    def run(self):
        pass
# output
cimport cython
from libc.stdlib cimport malloc
include "includes/consts.pxi"
include "includes/stdlib.pxi"
import os

x = 1


cdef class Loop:
    cdef int y

    def run(self):
        pass
