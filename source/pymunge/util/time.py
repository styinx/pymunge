from time import perf_counter_ns as timer


def duration(d: int, pad: bool = False):
    ns = d % 1000
    us = d // 1000 % 1000
    ms = d // (1000 * 1000) % 1000
    s = d // (1000 * 1000 * 1000) % 60
    m = d // (1000 * 1000 * 1000 * 60) % 60

    f = ''

    if m:
        f += f'{m:2d}m '
    if s or f and pad:
        f += f'{s:2d}s '
    if ms or f and pad:
        f += f'{ms:3d}ms '
    if us or f and pad:
        f += f'{us:3d}us '
    if ns or f and pad:
        f += f'{ns:3d}ns '

    return f.strip()


def measure(f: callable, *args, **kwargs):
    start = timer()
    res = f(*args, **kwargs)
    return timer() - start, res
