# flags: --pyx
cdef class Handle
cdef class SocketHandle(Handle)

cdef class Timer(Handle)
cdef class Idle( Handle )
ctypedef object (*method_t)(object)
cdef class Loop:
    cdef Handle handle
cdef class Handle:
    pass
# output
cdef class Handle
cdef class SocketHandle(Handle)

cdef class Timer(Handle)
cdef class Idle(Handle)
ctypedef object (*method_t)(object)


cdef class Loop:
    cdef Handle handle


cdef class Handle:
    pass
