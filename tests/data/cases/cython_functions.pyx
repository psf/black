# flags: --pyx
cdef int add(int a,int b):
    return a+b
cpdef double scale(double x, double factor=2.0) except *:
    return x*factor
cdef void work(int n) nogil:
    pass
cdef int check(char *s) except -1:
    return 0
cdef inline int fast(int x) noexcept nogil: return x
cdef np.ndarray[double, ndim=1] build(int n, double[:] src, char **names=NULL, object callback=None):
    pass
cdef int a_function_with_a_very_long_name(int first_argument, double second_argument, char *third) except -1:
    pass
cdef int unchanged(int a, int b)

@cython.boundscheck(False)
@cython.wraparound(False)
cdef int decorated(int a):
    return a
def typed(int a, double b=1.0, char *c=NULL, *args, int d=2, **kwargs):
    pass
def mixed(a, b: int = 2, int c=3):
    pass
# output
cdef int add(int a, int b):
    return a + b


cpdef double scale(double x, double factor=2.0) except *:
    return x * factor


cdef void work(int n) nogil:
    pass


cdef int check(char *s) except -1:
    return 0


cdef inline int fast(int x) noexcept nogil:
    return x


cdef np.ndarray[double, ndim=1] build(
    int n, double[:] src, char **names=NULL, object callback=None
):
    pass


cdef int a_function_with_a_very_long_name(
    int first_argument, double second_argument, char *third
) except -1:
    pass


cdef int unchanged(int a, int b)


@cython.boundscheck(False)
@cython.wraparound(False)
cdef int decorated(int a):
    return a


def typed(int a, double b=1.0, char *c=NULL, *args, int d=2, **kwargs):
    pass


def mixed(a, b: int = 2, int c=3):
    pass
