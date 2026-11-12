# flags: --pyx
ctypedef object (*method_t)(object, object)
ctypedef void (* uv_close_cb)(uv_handle_t* handle) with gil
ctypedef void (*cb_t)(void *data) noexcept nogil
ctypedef int (*cmp_func)(const void *, const void *)
cdef int (*fp)(int, int) except -1 nogil
cdef double (**pp)(double)
cdef void (*handler)() noexcept
cdef struct Ops:
    int (*add)(int a,int b)
    void (*release)(void *p) noexcept
cdef extern from "lib.h":
    ctypedef void (*log_func)(const char *msg, int level) nogil
    void set_logger(log_func logger)
    void qsort(void *base, size_t n, size_t size, int (*compar)(const void *, const void *))
ctypedef some_long_return_type_name (*a_long_callback_name_t)(first_argument_type first, second_argument_type second) noexcept nogil
cdef void register_callback(void (*cb)(int) noexcept, int priority):
    pass
def call(int (*f)(int,int), int a=1):
    return f(a, a)
# output
ctypedef object (*method_t)(object, object)
ctypedef void (*uv_close_cb)(uv_handle_t *handle) with gil
ctypedef void (*cb_t)(void *data) noexcept nogil
ctypedef int (*cmp_func)(const void *, const void *)
cdef int (*fp)(int, int) except -1 nogil
cdef double (**pp)(double)
cdef void (*handler)() noexcept


cdef struct Ops:
    int (*add)(int a, int b)
    void (*release)(void *p) noexcept


cdef extern from "lib.h":
    ctypedef void (*log_func)(const char *msg, int level) nogil
    void set_logger(log_func logger)
    void qsort(
        void *base, size_t n, size_t size, int (*compar)(const void *, const void *)
    )


ctypedef some_long_return_type_name (*a_long_callback_name_t)(
    first_argument_type first, second_argument_type second
) noexcept nogil


cdef void register_callback(void (*cb)(int) noexcept, int priority):
    pass


def call(int (*f)(int, int), int a=1):
    return f(a, a)
