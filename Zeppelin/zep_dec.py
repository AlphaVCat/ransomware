import base64


KEY_LEN = 32


def rc4_init(key):
    """RC4 initialization"""

    key_len = len(key)
    if (key_len <= 0):
        raise ValueError('Invalid RC4 key length.')

    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % key_len]) & 0xFF
        S[i], S[j] = S[j], S[i]

    return S


def rc4(data, key):
    """RC4 implementation"""

    S = rc4_init(key)
    res_data = bytearray(data)

    k = 0
    m = 0
    for i in range(len(res_data)):
        m = (m + 1) & 0xFF
        k = (k + S[m]) & 0xFF
        S[k], S[m] = S[m], S[k]
        res_data[i] ^= S[(S[m] + S[k]) & 0xFF]

    return bytes(res_data)


def decrypt_data(data):
    """Decrypt data"""
    return rc4(data[KEY_LEN:], data[:KEY_LEN])


def decrypt_from_b64(data):
    """Base64 decode and decrypt data"""
    data = base64.b64decode(data)
    return rc4(data[KEY_LEN:], data[:KEY_LEN])


if __name__ == '__main__':
    import sys
    import io

    if len(sys.argv) != 2:
        print('Usage: '+ sys.argv[0] + ' filename')
        sys.exit(0)

    filename = sys.argv[1]

    with io.open(filename, 'rb') as f:
        data = f.read()

    dec_data = decrypt_from_b64(data)

    new_filename = filename + '.dec'
    with io.open(new_filename, 'wb') as f:
        f.write(dec_data)

    print('Done!')
