
RND_SEED = 0xFFCAA1EA

RND_MULTIPLIER = 0x8088405


def decrypt(data, seed=RND_SEED):

    dec_data = b''

    n = seed

    pos = 0

    size = len(data)

    while (size != 0):

        n = (n * RND_MULTIPLIER + 1) & 0xFFFFFFFF
        x = (seed * n) >> 32

        xx = x.to_bytes(4, byteorder='little')

        block_size = min(4, size)

        for i in range(block_size):
            dec_data += bytes([data[pos + i] ^ xx[i]])

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
