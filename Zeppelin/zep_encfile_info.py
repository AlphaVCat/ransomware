import sys
import io
import struct
import zep_dec


MARKER0 = b'\xDA\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xBF\x0D\x0A\xB3'
MARKER1 = b'ZEPPELIN'
MARKER2 = b'\xB3\x0D\x0A\xC0\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xD9\x0D\x0A'
MARKER = MARKER0 + MARKER1 + MARKER2


def save_data_to_file(filename, data):
    """Save binary data to file."""
    with io.open(filename, 'wb') as f:
        f.write(data)


#
# Main
#
if len(sys.argv) != 2:
    print('Usage: '+ sys.argv[0] + ' filename')
    sys.exit(0)

filename = sys.argv[1]

with io.open(filename, 'rb') as f:

    data = f.read(len(MARKER))
    if data != MARKER:
        print('Error: file not encrypted or damaged')
        sys.exit(1)

    print('Encrypted marker: OK')

    data = f.read(16)
    enc_size, orig_size = struct.unpack_from('<QQ', data, 0)
    print('Encrypted data size: %d' % enc_size)
    print('Original data size: %d' % orig_size)

    f.seek(-4, 2)
    data = f.read(4)
    metadata_size = int.from_bytes(data, byteorder='little')
    print('Metadata size: %d' % metadata_size)

    f.seek(-metadata_size, 2)
    metadata = f.read(metadata_size)

    pos = 0

    # Block offset list
    size, = struct.unpack_from('<L', metadata, pos)
    pos += 4
    off_list_data = zep_dec.decrypt_data(metadata[pos : pos + size])
    pos += size

    save_data_to_file(filename + '.offsets', off_list_data)

    num_blocks = len(off_list_data) // 8
    print('Number of blocks: %d' % num_blocks)

    block_offsets = []

    for i in range(num_blocks):
        offset, = struct.unpack_from('<Q', off_list_data, i * 8)
        block_offsets.append(offset)
        print('Blocks[%02d] offset: %08X' % (i, offset))

    # Encrypted AES key and IV
    size, = struct.unpack_from('<L', metadata, pos)
    pos += 4
    aes_key_data = zep_dec.decrypt_data(metadata[pos : pos + size])
    pos += size

    save_data_to_file(filename + '.encaeskey', aes_key_data)

    # Encrypted RSA-155 private key
    size, = struct.unpack_from('<L', metadata, pos)
    pos += 4
    rsa_key_data = zep_dec.decrypt_data(metadata[pos : pos + size])
    pos += size

    save_data_to_file(filename + '.encrsakey', rsa_key_data)

    # Block size, original file size
    block_size, file_size = struct.unpack_from('<LQ', metadata, pos)

    print('Block size: %d' % block_size)
    print('Original file size: %d' % file_size)

    # Encrypted data
    f.seek(len(MARKER))
    enc_data = f.read(block_size - len(MARKER))

    for i in range(1, num_blocks):
        f.seek(block_offsets[i])
        enc_data += f.read(block_size)

    f.seek(file_size)
    enc_data += f.read(enc_size + len(MARKER) + 16 - num_blocks * block_size)

    save_data_to_file(filename + '.encdata', enc_data)
