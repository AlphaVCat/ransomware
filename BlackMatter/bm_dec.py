
RND_SEED = 0xFFCAA1EA

RND_MULTIPLIER = 0x8088405



def xor_dword(data, pos, size, x):

    dec_data = b''

    for i in range(size):
        dec_data += bytes([data[pos + i] ^ (x & 0xFF)])
        x >>= 8

    return dec_data


def decrypt(data, seed=RND_SEED):

    dec_data = b''

    n = RND_SEED

    pos = 0

    size = len(data)

    while (size != 0):

        n = (n * RND_MULTIPLIER + 1) & 0xFFFFFFFF
        x = (RND_SEED * n) >> 32

        block_size = min(4, size)

        dec_data += xor_dword(data, pos, block_size, x)

        pos += block_size
        size -= block_size

    return dec_data


if __name__ == '__main__':
    import sys
    import io

    if len(sys.argv) != 2:
        print('Usage: '+ sys.argv[0] + ' filename')
        sys.exit(0)

    file_name = sys.argv[1]
    with io.open(file_name, 'rb') as f:
        data = f.read()

    dec_data = decrypt(data)

    new_file_name = file_name + '.dec'
    with io.open(new_file_name, 'wb') as f:
        f.write(dec_data)

    print('Done!')
