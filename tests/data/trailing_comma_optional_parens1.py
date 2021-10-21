if e1234123412341234.winerror not in (_winapi.ERROR_SEM_TIMEOUT,
                        _winapi.ERROR_PIPE_BUSY) or _check_timeout(t):
    pass

if x:
    if y:
        new_id = max(Vegetable.objects.order_by('-id')[0].id,
                     Mineral.objects.order_by('-id')[0].id) + 1
