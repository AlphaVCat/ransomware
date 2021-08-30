import sys
import io
import os
import errno
import struct
import base64
import aplib
import bm_dec


CFG_POS = 0x12000

RSA_PUB_KEY_SIZE = 0x80
BOT_COMPANY_SIZE = 0x10
AES_KEY_SIZE = 0x10

FLAGS = [
    'encrypt odd blocks in large files',
    'logon with cfg user accounts',
    'mount volumes, encrypt Exchange files',
    'encrypt net share files',
    'kill processes',
    'stop and kill services',
    'create mutex',
    'print ransom note',
    'c&c communication',
]

DATA_FIELDS = [
    ( 'dir_names',      False ),
    ( 'file_names',     False ),
    ( 'file_exts',      False ),
    ( 'computer_names', False ),
    ( 'unknown0',       False ),
    ( 'processes',      False ),
    ( 'services',       False ),
    ( 'c&c',            False ),
    ( 'accounts',       True ),
    ( 'ransom_note',    True ),
]


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
    print('rnd seed: %04X' % rnd_seed)

    pack_cfg_data_size = int.from_bytes(f.read(4), byteorder='little',
                                        signed=False)
    print('compressed cfg data size: %d' % pack_cfg_data_size)

    enc_cfg_data = f.read(pack_cfg_data_size)

pack_cfg_data = bm_dec.decrypt(enc_cfg_data, rnd_seed)

cfg_data = aplib.decompress(pack_cfg_data)

print('cfg data size: %d' % len(cfg_data))

save_data_to_file(dest_dir + 'cfg_data.bin', cfg_data)
print('cfg data saved to file.')

print()

pos = 0

rsa_pub_key = cfg_data[pos : pos + RSA_PUB_KEY_SIZE]
save_data_to_file(dest_dir + 'rsa_pub_key.bin', rsa_pub_key)
print('RSA public key saved to file.')

pos += RSA_PUB_KEY_SIZE

bot_company = cfg_data[pos : pos + BOT_COMPANY_SIZE]
print('bot_company: \"%.8x%.8x%.8x%.8x\"' % struct.unpack('>4L', bot_company))

save_data_to_file(dest_dir + 'bot_company.bin', bot_company)
print('bot_company saved to file.')

pos += BOT_COMPANY_SIZE

aes_key = cfg_data[pos : pos + AES_KEY_SIZE]
save_data_to_file(dest_dir + 'aes_key.bin', aes_key)
print('AES key saved to file.')

pos += AES_KEY_SIZE

flags_size = len(FLAGS)

flags = cfg_data[pos : pos + flags_size]

print()

print('flags:')

for i in range(flags_size):
    print('%s: %d' % (FLAGS[i], flags[i]))

print()

pos += flags_size

data_pos = pos

for fld in DATA_FIELDS:

    ofs, = struct.unpack_from('<L', cfg_data, pos)
    if (ofs != 0):

        i = cfg_data.find(0, data_pos + ofs)
        if (i >= 0):
            b64_data = cfg_data[data_pos + ofs : i]
        else:
            b64_data = cfg_data[data_pos + ofs:]

        data = base64.decodebytes(b64_data)

        if fld[1]:
            data = bm_dec.decrypt(data, rnd_seed)

        save_data_to_file(dest_dir + fld[0] + '.bin', data)
        print(fld[0] + ' saved to file.')

    pos += 4

print()

ransom_hash, = struct.unpack_from('<L', cfg_data, pos)

print('ransom note hash: %08X' % ransom_hash)
