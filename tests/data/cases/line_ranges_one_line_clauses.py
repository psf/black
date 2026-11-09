# flags: --line-ranges=16-16 --line-ranges=24-24 --line-ranges=29-29
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# Clauses with their body on the same line are kept as they are outside the ranges.
if sys.platform == "win32": import msvcrt
else:
    import termios

def read_config(path):
    try: f = open(path)
    except OSError:
        return None
    if f.closed:
        return None
    else: data = f.read( )
    f.close()
    return data

class Reader:
    def read(self):
        while self.more(): self.step()
        else: self.done = True
        return  self.done

async def drain(queue):
    async for item in queue: handle(  item )
    else: finish(  queue )
    return  queue

# output
# flags: --line-ranges=16-16 --line-ranges=24-24 --line-ranges=29-29
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# Clauses with their body on the same line are kept as they are outside the ranges.
if sys.platform == "win32": import msvcrt
else:
    import termios

def read_config(path):
    try: f = open(path)
    except OSError:
        return None
    if f.closed:
        return None
    else:
        data = f.read()
    f.close()
    return data

class Reader:
    def read(self):
        while self.more(): self.step()
        else: self.done = True
        return self.done

async def drain(queue):
    async for item in queue: handle(  item )
    else: finish(  queue )
    return queue
