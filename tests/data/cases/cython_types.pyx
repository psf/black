# flags: --pyx
ctypedef unsigned char uchar
ctypedef np.float64_t DTYPE_t
ctypedef int* int_ptr
ctypedef struct Point:
    int x
    int y
cdef struct Rect:
    Point top_left,bottom_right
    char *label
    pass
cdef enum Color:
    RED=1
    GREEN
    BLUE
cdef enum:
    ANON
cdef union Value:
    int i
    double d
cdef extern from "header.h":
    ctypedef int size_t
    int compute(int a,char **argv)
    enum: LIMIT
    cdef struct Foo:
        int a
cdef extern from *:
    pass
cdef extern from "other.h" nogil:
    void helper()
cdef class Base:
    cdef int value
    cdef readonly list items

    def __init__(self,int value):
        self.value=value
    cdef int get(self):
        return self.value
cdef class Child(Base):
    pass
@cython.final
cdef class Final:
    cpdef int run(self): return 1
# output
ctypedef unsigned char uchar
ctypedef np.float64_t DTYPE_t
ctypedef int *int_ptr


ctypedef struct Point:
    int x
    int y


cdef struct Rect:
    Point top_left, bottom_right
    char *label
    pass


cdef enum Color:
    RED = 1
    GREEN
    BLUE


cdef enum:
    ANON


cdef union Value:
    int i
    double d


cdef extern from "header.h":
    ctypedef int size_t
    int compute(int a, char **argv)
    enum: LIMIT

    cdef struct Foo:
        int a


cdef extern from *:
    pass


cdef extern from "other.h" nogil:
    void helper()


cdef class Base:
    cdef int value
    cdef readonly list items

    def __init__(self, int value):
        self.value = value

    cdef int get(self):
        return self.value


cdef class Child(Base):
    pass


@cython.final
cdef class Final:
    cpdef int run(self):
        return 1
