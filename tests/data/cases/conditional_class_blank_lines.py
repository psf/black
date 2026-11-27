# flags: --preview
if first:

    class First:
        def method(self):
            return 1

elif second:

    @decorate
    class Second:
        pass

else:
    initialize()

    class Fallback:
        pass


def outer():
    if enabled:

        class Enabled:
            def method(self):
                return True

    else:

        @decorate
        class Disabled:
            pass

    return None


for item in items:

    class Loop:
        pass

else:

    @decorate
    class LoopFallback:
        pass


# output
if first:
    class First:
        def method(self):
            return 1
elif second:
    @decorate
    class Second:
        pass
else:
    initialize()

    class Fallback:
        pass


def outer():
    if enabled:
        class Enabled:
            def method(self):
                return True
    else:
        @decorate
        class Disabled:
            pass

    return None


for item in items:

    class Loop:
        pass

else:

    @decorate
    class LoopFallback:
        pass
