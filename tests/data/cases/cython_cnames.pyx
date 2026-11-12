# flags: --pyx
cdef extern from "h.h":
    ctypedef int vint "volatile int"
    WeakSet weakref_steal_as_weakset "weakref_steal"(PyObject* obj)
    int py_value 'c_value'
    cdef struct py_struct "c_struct":
        int x "c_x"
    cdef enum py_enum "c_enum":
        A "C_A"
cdef int x "cx", *y "cy"
# output
cdef extern from "h.h":
    ctypedef int vint "volatile int"
    WeakSet weakref_steal_as_weakset "weakref_steal"(PyObject *obj)
    int py_value "c_value"

    cdef struct py_struct "c_struct":
        int x "c_x"

    cdef enum py_enum "c_enum":
        A "C_A"


cdef int x "cx", *y "cy"
