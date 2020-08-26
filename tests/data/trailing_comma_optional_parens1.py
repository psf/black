if e1234123412341234.winerror not in (_winapi.ERROR_SEM_TIMEOUT,
                        _winapi.ERROR_PIPE_BUSY) or _check_timeout(t):
    pass