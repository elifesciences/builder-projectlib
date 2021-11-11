
def ensure(b, msg, exception=AssertionError):
    if b in [None, False]:
        raise exception(msg)

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
