import sys
import io
import struct
import os.path
import aplib
import lb3_crypt


MAX_METADATA_SIZE = 0x2E0

KEYDATA_SIZE = 0x80
KEYDATA_HASH_SIZE = 4
METADATA_FIXED_SIZE = KEYDATA_SIZE + KEYDATA_HASH_SIZE + 2
MIN_METADATA_SIZE = 0xD8

MAX_BLOCK_SIZE = 0xFA1
DIVIDER = 0x1000F


def get_data_hash(data, rsa_n_dword0, n=0):
    """Get data hash"""

    n0 = n & 0xFFFF
    n1 = n >> 16

    size = len(data)

    pos = 0

    while (size != 0):

        block_size = min(size, MAX_BLOCK_SIZE)

        for i in range(block_size):
            n0 += data[pos + i]
            n1 += n0

        n0 %= DIVIDER
        n1 %= DIVIDER

        pos += block_size
        size -= block_size

    return ((n0 + (n1 << 16)) & 0xFFFFFFFF) ^ rsa_n_dword0


def get_meta_data_hash(data, rsa_n_dword0):
    """Get metadata hash"""

    h = 0x0D6917A

    for _ in range(3):

        h2 = get_data_hash(data, rsa_n_dword0, h)
        h = int.from_bytes(h2.to_bytes(4, 'little'), 'big')

    return h


def is_file_encrypted(filename, rsa_n_dword0):
    """Check if file is encrypted"""

    with io.open(filename, 'rb') as f:

        try:
            f.seek(-(KEYDATA_SIZE + KEYDATA_HASH_SIZE), 2)
        except OSError:
            return False

        keydata = f.read()

    key_hash = int.from_bytes(keydata[:4], 'little')
    h = get_meta_data_hash(keydata[4:], rsa_n_dword0)
    return (h == key_hash)
        

def read_metadata(filename):
    """Read encrypted file metadata"""

    with io.open(filename, 'rb') as f:
        f.seek(-METADATA_FIXED_SIZE, 2)
        metadata_size = int.from_bytes(f.read(2), 'little')
        metadata_size += METADATA_FIXED_SIZE
        f.seek(-metadata_size, 2)
        metadata = f.read()

    return metadata


def decrypt_metadata(rsa_priv_key_data, metadata):
    """Decrypt metadata"""

    # Decrypt key data
    key_data = lb3_crypt.rsa_decrypt(rsa_priv_key_data,
                                     metadata[-KEYDATA_SIZE:])

    # Check decrypted key data
    rsa_n_dword0, = struct.unpack_from('<L', rsa_priv_key_data,
                                       lb3_crypt.RSA_KEY_SIZE)
    i, = struct.unpack_from('<L', key_data, KEYDATA_SIZE - 4)
    i = (((i * 0x8088405 + 1) & 0xFFFFFFFF) * 0x78) >> 32
    check_num, = struct.unpack_from('<L', key_data, i)
    if rsa_n_dword0 != check_num:
        return None

    # Decrypt metadata
    salsa_key_data = key_data[:lb3_crypt.SALSA_KEY_DATA_SIZE]
    enc_data = metadata[:len(metadata) - METADATA_FIXED_SIZE]
    dec_data = lb3_crypt.salsa_decrypt(salsa_key_data, enc_data)

    return dec_data + \
           metadata[-METADATA_FIXED_SIZE : -METADATA_FIXED_SIZE + 6] + \
           key_data


#
# Main
#
if len(sys.argv) != 2:
    print('Usage: '+ sys.argv[0] + ' filename')
    sys.exit(0)

filename = sys.argv[1]

# Read private RSA key data (d, n)
with io.open('rsa_privkey.bin', 'rb') as f:
    rsa_priv_key_data = f.read(2 * lb3_crypt.RSA_KEY_SIZE)

# Check if file is encrypted
rsa_n_dword0, = struct.unpack_from('<L', rsa_priv_key_data,
                                   lb3_crypt.RSA_KEY_SIZE)
if not is_file_encrypted(filename, rsa_n_dword0):
    print('Error: file not encrypted or damaged')
    sys.exit(1)

# Read encrypted file metadata
metadata = read_metadata(filename)
print('metadata size: %d' % len(metadata))
metadata_var_size = len(metadata) - METADATA_FIXED_SIZE
print('metadata variable part size: %d' % metadata_var_size)

# Decrypt metadata
metadata = decrypt_metadata(rsa_priv_key_data, metadata)
if metadata is None:
    print('Error: file rsa key not valid')
    sys.exit(1)

new_filename = filename + '.metadata'
with io.open(new_filename, 'wb') as f:
    f.write(metadata)

pos = len(metadata) - MIN_METADATA_SIZE

# Original file name
pack_filename_size, = struct.unpack_from('<H', metadata, pos)
unpacked_filename = aplib.decompress(metadata[:pack_filename_size])
orig_filename = unpacked_filename.decode('UTF-16LE')
i = orig_filename.find('\0')
if i >= 0:
    orig_filename = orig_filename[:i]
print('original file name: \"%s\"' % orig_filename)

# Salsa decryption key
pos += 18
salsa_key_data = metadata[pos : pos + lb3_crypt.SALSA_KEY_DATA_SIZE]

# Decrypt first 256K
with io.open(filename, 'rb') as f:
    enc_data = f.read(256 * 1024)

dec_data = lb3_crypt.salsa_decrypt(salsa_key_data, enc_data)

dest_filename = os.path.join(os.path.dirname(os.path.abspath(filename)),
                             orig_filename)
with io.open(dest_filename, 'wb') as f:
    f.write(dec_data)
