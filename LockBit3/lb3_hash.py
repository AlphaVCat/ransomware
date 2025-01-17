
ror32 = lambda val, shift: \
    ((val & 0xFFFFFFFF) >> (shift & 0x1F)) | \
    ((val << (32 - (shift & 0x1F))) & 0xFFFFFFFF)


def get_wide_str_hash(s, n=0):
    """Get Unicode-string hash"""

    for ch in s:

        m = ord(ch)
        if (m >= 0x41) and (m <= 0x5A):
            m |= 0x20
        n = m + ror32(n, 13)

    return ror32(n, 13)


def get_str_hash(s, n=0):
    """Get string hash"""

    for ch in s:

        n = ord(ch) + ror32(n, 13)

    return ror32(n, 13)


def get_api_func_name_hash(lib_name, fnc_name):
    """Get API function name hash"""

    return get_str_hash(fnc_name, get_wide_str_hash(lib_name, 0))


if __name__ == '__main__':
    import io

    with io.open('api_names.txt', 'rt') as f:
        func_names = f.read().splitlines()

    with io.open('api_hashes.txt', 'wt') as f:
        for name in func_names:
            name = name.strip()
            if (name == ''):
                continue
            names = name.split('\t')
            h = get_api_func_name_hash(names[0], names[1])
            f.write('%08X\t%s\n' % (h, names[1]))
