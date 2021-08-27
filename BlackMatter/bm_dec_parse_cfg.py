import sys
import io
import os
import errno
import struct
import base64
import bm_dec


CFG_POS = 0x4E00

RSA_KEY_SIZE = 0x100


def mkdirs(dir):

    try:
        os.makedirs(dir)

    except OSError as exception:
        if (exception.errno != errno.EEXIST):
            raise


def save_data_to_file(file_name, data):

    with io.open(file_name, 'wb') as f:
        f.write(data)


if len(sys.argv) != 2:
    print('Usage: '+ sys.argv[0] + ' filename')
    sys.exit(0)

file_name = sys.argv[1]

dest_dir = os.path.dirname(file_name) + '/cfg/'
mkdirs(dest_dir)

with io.open(file_name, 'rb') as f:

    f.seek(CFG_POS)

    rnd_seed = int.from_bytes(f.read(4), byteorder='little', signed=False)
    print('rnd seed: %08X' % rnd_seed)

    cfg_data_size = int.from_bytes(f.read(4), byteorder='little', signed=False)
    print('cfg data size: %d' % cfg_data_size)

    enc_cfg_data = f.read(cfg_data_size)

cfg_data = bm_dec.decrypt(enc_cfg_data, rnd_seed)

save_data_to_file(dest_dir + 'cfg_data.bin', cfg_data)
print('Configuration saved to file.')

pos = 0

ransom_hash, = struct.unpack_from('<L', cfg_data, pos)
print('ransom note hash: %08X' % ransom_hash)

pos += 4

ransom_size, = struct.unpack_from('<L', cfg_data, pos)
print('ransom note size: %d' % ransom_size)

pos += 4

rsa_key = cfg_data[pos : pos + RSA_KEY_SIZE]
save_data_to_file(dest_dir + 'rsa_key.bin', rsa_key)
print('RSA key saved to file.')

pos += RSA_KEY_SIZE

i = cfg_data.find(0, pos)
if (i >= 0):
    b64_data = cfg_data[pos : i]
else:
    b64_data = cfg_data[pos:]

data = base64.decodebytes(b64_data)

save_data_to_file(dest_dir + 'dir_names.bin', data)
print('dir_names.bin saved to file.')
