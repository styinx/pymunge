def fnv1a_32(s: str) -> int:
    h = 0x811C9DC5
    for c in s:
        h = (h ^ (ord(c) | 0x20)) * 0x1000193
        h &= 0xFFFFFFFF  # emulate 32-bit overflow
    return h
