
def ensure(b, msg, exception=AssertionError):
    if b in [None, False]:
        raise exception(msg)

def isint(v):
    return str(v).lstrip('-+').isdigit()

def nth(x, n):
    "returns the nth value in x or None"
    ensure(isint(n), "n must be an integer", TypeError)
    try:
        return list(x)[n]
    except (KeyError, IndexError):
        return None
    except TypeError:
        raise

def first(x):
    "returns the first value in x"
    return nth(x, 0)

def lookup(data, path, default=0xDEADBEEF):
    if not isinstance(data, dict):
        raise ValueError("'data' must be a dictionary, not %r", type(path))
    if not isinstance(path, str):
        raise ValueError("'path' must be a string, not %r", type(path))
    try:
        bits = path.split('.', 1)
        if len(bits) > 1:
            bit, rest = bits
        else:
            bit, rest = bits[0], []
        val = data[bit]
        if rest:
            return lookup(val, rest, default)
        return val
    except KeyError:
        if default == 0xDEADBEEF:
            raise
        return default
