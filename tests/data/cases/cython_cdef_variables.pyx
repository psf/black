# flags: --pyx
cdef int a
cdef int b=1,c = 2
cdef unsigned long long total = 0
cdef char *s = NULL
cdef char* t
cdef char ** argv
cdef int *p, *q
cdef int *r, s2
cdef double[:] view
cdef double[:,::1] matrix = zeros((3,3))
cdef np.ndarray[double,ndim=2] arr
cdef int table[10]
cdef readonly object name
cdef public int  level  # trailing comment
cpdef int exported = 3
cdef:
    int i,j
    double *buf = NULL
    char *name2

def f():
    cdef int local = 1
    cdef int other
    return local
# output
cdef int a
cdef int b = 1, c = 2
cdef unsigned long long total = 0
cdef char *s = NULL
cdef char *t
cdef char **argv
cdef int *p, *q
cdef int *r, s2
cdef double[:] view
cdef double[:, ::1] matrix = zeros((3, 3))
cdef np.ndarray[double, ndim=2] arr
cdef int table[10]
cdef readonly object name
cdef public int level  # trailing comment
cpdef int exported = 3
cdef:
    int i, j
    double *buf = NULL
    char *name2


def f():
    cdef int local = 1
    cdef int other
    return local
