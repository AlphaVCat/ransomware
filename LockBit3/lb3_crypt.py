import struct


RSA_KEY_SIZE = 128
RSA_E = 0x10001

SALSA_KEY_DATA_SIZE = 64


MASK32 = 0xFFFFFFFF

add32 = lambda x, y: (x + y) & MASK32

rol32 = lambda v, s: ((v << s) & MASK32) | ((v & MASK32) >> (32 - s))


class Salsa(object):

    """Pure python implementation of Salsa cipher"""


    @staticmethod
    def quarter_round(x, a, b, c, d):
        """Perform a Salsa round"""

        x[a] ^= rol32(add32(x[d], x[c]), 7)
        x[b] ^= rol32(add32(x[a], x[d]), 9)
        x[c] ^= rol32(add32(x[b], x[a]), 13)
        x[d] ^= rol32(add32(x[c], x[b]), 18)


    @staticmethod
    def salsa_block(init_state, rounds, block_num):
        """Generate a state of a single block"""

        state = init_state[:]

        # Increase block counter
        c = (state[8] | (state[9] << 32)) + block_num
        state[8] = c & MASK32
        state[9] = (c >> 32) & MASK32

        working_state = state[:]

        for _ in range(0, rounds // 2):
            # Perform round of Salsa cipher

            Salsa.quarter_round(working_state,  4,  8, 12,  0)
            Salsa.quarter_round(working_state,  9, 13,  1,  5)
            Salsa.quarter_round(working_state, 14,  2,  6, 10)
            Salsa.quarter_round(working_state,  3,  7, 11, 15)
            Salsa.quarter_round(working_state,  1,  2,  3,  0)
            Salsa.quarter_round(working_state,  6,  7,  4,  5)
            Salsa.quarter_round(working_state, 11,  8,  9, 10)
            Salsa.quarter_round(working_state, 12, 13, 14, 15)

        return [add32(st, wrkSt) for st, wrkSt in zip(state, working_state)]


    @staticmethod
    def words_to_bytes(state):
        """Convert state to little endian bytestream"""

        return bytes(struct.pack('<16L', *state))


    @staticmethod
    def _bytes_to_words(data):
        """Convert a bytearray to array of word sized ints"""

        return list(struct.unpack('<' + str(len(data) // 4) + 'L', data))


    def __init__(self, init_state, rounds=20):
        """Set the initial state for the Salsa cipher"""

        if len(init_state) != 64:
            raise ValueError('Initial state must be 64 byte long')

        self.rounds = rounds

        # Convert bytearray state to little endian 32 bit unsigned ints
        self.init_state = Salsa._bytes_to_words(init_state)


    def encrypt(self, plaintext):
        """Encrypt the data"""

        encrypted_message = b''
        for i, block in enumerate(plaintext[i : i + 64] for i
                                  in range(0, len(plaintext), 64)):

            # Receive the key stream for nth block
            key_stream = Salsa.salsa_block(self.init_state, self.rounds, i)
            key_stream = Salsa.words_to_bytes(key_stream)

            encrypted_message += bytes(x ^ y for x, y
                                       in zip(key_stream, block))

        return encrypted_message


    def decrypt(self, ciphertext):
        """Decrypt the data"""

        return self.encrypt(ciphertext)


def rsa_encrypt(pub_key_data, data):
    """RSA encrypt data"""

    n = int.from_bytes(pub_key_data[:RSA_KEY_SIZE], byteorder='little')
    x = int.from_bytes(data, 'little')
    res = int(pow(x, RSA_E, n))
    return res.to_bytes(RSA_KEY_SIZE, byteorder='little')


def rsa_decrypt(priv_key_data, enc_data):
    """RSA decrypt data"""

    d = int.from_bytes(priv_key_data[:RSA_KEY_SIZE], byteorder='little')
    n = int.from_bytes(priv_key_data[RSA_KEY_SIZE:], byteorder='little')
    x = int.from_bytes(enc_data, 'little')
    res = int(pow(x, d, n))
    return res.to_bytes(RSA_KEY_SIZE, byteorder='little')


def salsa_encrypt(key_data, data):
    """Salsa20 encrypt data"""

    cipher = Salsa(key_data)
    return cipher.encrypt(data)


def salsa_decrypt(key_data, enc_data):
    """Salsa20 decrypt data"""

    cipher = Salsa(key_data)
    return cipher.decrypt(enc_data)


if __name__ == '__main__':
    import sys
    import io

    if len(sys.argv) != 2:
        print('Usage: '+ sys.argv[0] + ' filename')
        exit(0)

    filename = sys.argv[1]

    with io.open(filename, 'rb') as f:
        enc_data = f.read()

    with io.open('key.bin', 'rb') as f:
        key_data = f.read()

    data = salsa_decrypt(key_data, enc_data)

    new_filename = filename + '.dec'
    with io.open(new_filename, 'wb') as f:
        f.write(data)
