CRC32_POLY = 0xEDB88320


crc32_table = None


def get_crc32_table():
    table = list(range(256))
    for i in range(256):
        x = i
        for j in range(8):
            if x & 1:
                x = (x >> 1) ^ CRC32_POLY
            else:
                x >>= 1
        table[i] = x
    return table


def crc32(data, crc = 0):
    global crc32_table
    if crc32_table is None:
        crc32_table = get_crc32_table()
    for b in data:
        crc = crc32_table[(crc & 0xFF) ^ b] ^ (crc >> 8)
    return crc


if __name__ == '__main__':
    import sys
    import io

    if len(sys.argv) != 2:
        print('Usage: '+ sys.argv[0] + ' data_file')
        sys.exit(0)

    file_name = sys.argv[1]
    with io.open(file_name, 'rb') as f:
        data = f.read()

    crc = crc32(data)

    print(hex(crc))
