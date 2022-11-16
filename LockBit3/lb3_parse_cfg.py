"""
LockBit3 configuration data parser.

GitHub: https://github.com/rivitna/
E-mail: rivitna@gmail.com
"""

import sys
import io
import os
import errno
import struct
import base64
import binascii
import json
import aplib
import lb3_dec


# Configuration data file position
CFG_POS = 0x22E00
# Encrypted helper code file position
ENC_HELPER_CODE_POS = 0x22BBB


RSA_PUB_KEY_SIZE = 0x80
UID_SIZE = 0x10
AES_KEY_SIZE = 0x10


# Settings
SETTING_UNKNOWN = 0
SETTING_BOOL = 1
SETTING_WORD = 2

SETTINGS = [
    ( 'encrypt_mode',        SETTING_UNKNOWN ),
    ( 'encrypt_filename',    SETTING_BOOL ),
    ( 'impersonation',       SETTING_BOOL ),
    ( 'skip_hidden_folders', SETTING_BOOL ),
    ( 'language_check',      SETTING_BOOL ),
    ( 'local_disks',         SETTING_BOOL ),
    ( 'network_shares',      SETTING_BOOL ),
    ( 'kill_processes',      SETTING_BOOL ),
    ( 'kill_services',       SETTING_BOOL ),
    ( 'running_one',         SETTING_BOOL ),
    ( 'print_note',          SETTING_BOOL ),
    ( 'set_wallpaper',       SETTING_BOOL ),
    ( 'set_icons',           SETTING_BOOL ),
    ( 'send_report',         SETTING_BOOL ),
    ( 'self_destruct',       SETTING_BOOL ),
    ( 'kill_defender',       SETTING_BOOL ),
    ( 'wipe_freespace',      SETTING_BOOL ),
    ( 'psexec_netspread',    SETTING_BOOL ),
    ( 'gpo_netspread',       SETTING_BOOL ),
    ( 'gpo_ps_update',       SETTING_BOOL ),
    ( 'shutdown_system',     SETTING_BOOL ),
    ( 'delete_eventlogs',    SETTING_BOOL ),
    ( 'delete_gpo_delay',    SETTING_WORD ),
]


# Fields
FIELD_UNKNOWN = 0
FIELD_STRLIST = 1
FIELD_HASHLIST = 2
FIELD_TEXT = 3

FIELDS = [
    ( 'white_folders',   FIELD_HASHLIST, False ),
    ( 'white_files',     FIELD_HASHLIST, False ),
    ( 'white_extens',    FIELD_HASHLIST, False ),
    ( 'white_hosts',     FIELD_HASHLIST, False ),
    ( 'unknown',         FIELD_UNKNOWN,  False ),
    ( 'kill_processes',  FIELD_STRLIST,  False ),
    ( 'kill_services',   FIELD_STRLIST,  False ),
    ( 'gate_urls',       FIELD_STRLIST,  False ),
    ( 'impers_accounts', FIELD_STRLIST,  True ),
    ( 'note',            FIELD_TEXT,     True ),
]


def extract_helper_code(file_data, pos):
    """Extract helper code"""

    size, = struct.unpack_from('<L', file_data, pos)
    pos += 4
    data = bytearray(file_data[pos : pos + size])

    for i in range(len(data)):
        data[i] ^= 0x30

    return aplib.decompress(data)


def mkdirs(dir):
    """Create directory hierarchy"""

    try:
        os.makedirs(dir)

    except OSError as exception:
        if (exception.errno != errno.EEXIST):
            raise


def save_data_to_file(file_name, data):
    """Save binary data to file."""
    with io.open(file_name, 'wb') as f:
        f.write(data)


#
# Main
#
if len(sys.argv) != 2:
    print('Usage: '+ sys.argv[0] + ' filename')
    sys.exit(0)

file_name = sys.argv[1]

# Load file data
with io.open(file_name, 'rb') as f:
    file_data = f.read()

# Extract helper code
helper_code = extract_helper_code(file_data, ENC_HELPER_CODE_POS)

dest_dir = os.path.abspath(os.path.dirname(file_name)) + '/cfg/'
mkdirs(dest_dir)

save_data_to_file(dest_dir + 'helper_code.bin', helper_code)
print('helper code saved to file.')

# Extract configuration data
cfg_pos = CFG_POS

rnd_seed, = struct.unpack_from('<Q', file_data, cfg_pos)
print(('rnd seed: %08X') % rnd_seed)

cfg_pos += 8

pack_cfg_data_size, = struct.unpack_from('<L', file_data, cfg_pos)
print('compressed cfg data size: %d' % pack_cfg_data_size)

cfg_pos += 4

enc_cfg_data = file_data[cfg_pos : cfg_pos + pack_cfg_data_size]

pack_cfg_data = lb3_dec.decrypt(helper_code, enc_cfg_data, rnd_seed)

cfg_data = aplib.decompress(pack_cfg_data)

print('cfg data size: %d' % len(cfg_data))

save_data_to_file(dest_dir + 'cfg_data.bin', cfg_data)
print('cfg data saved to file.')

pos = 0

# RSA public key
rsa_pub_key = cfg_data[pos : pos + RSA_PUB_KEY_SIZE]
save_data_to_file(dest_dir + 'rsa_pub_key.bin', rsa_pub_key)
print('RSA public key saved to file.')

pos += RSA_PUB_KEY_SIZE

config = {}

bot = {}

# UID
uid = binascii.hexlify(cfg_data[pos : pos + UID_SIZE]).decode()
bot['uid'] = uid
print('uid: \"%s\"' % uid)

pos += UID_SIZE

# AES key
bot['key'] = binascii.hexlify(cfg_data[pos : pos + AES_KEY_SIZE]).decode()

config['bot'] = bot

pos += AES_KEY_SIZE

cfg = {}

# Settings
settings = {}

for setting in SETTINGS:

    if setting[1] == SETTING_BOOL:

        settings[setting[0]] = (cfg_data[pos] != 0)
        pos += 1

    elif setting[1] == SETTING_WORD:

        settings[setting[0]], = struct.unpack_from('<H', cfg_data, pos)
        pos += 2

    else:
        settings[setting[0]] = cfg_data[pos]
        pos += 1

cfg['settings'] = settings

# Fields

data_pos = pos

for fld in FIELDS:

    if fld[1] != FIELD_UNKNOWN:

        ofs, = struct.unpack_from('<L', cfg_data, pos)

        fld_data = ''

        if (ofs != 0):

            i = cfg_data.find(0, data_pos + ofs)
            if (i >= 0):
                b64_data = cfg_data[data_pos + ofs : i]
            else:
                b64_data = cfg_data[data_pos + ofs:]

            data = base64.decodebytes(b64_data)

            if fld[2]:
                data = lb3_dec.decrypt(helper_code, data, rnd_seed)

            if fld[1] == FIELD_HASHLIST:

                for i in range(0, len(data), 4):
                    h, = struct.unpack_from('<L', data, i)
                    if h != 0:
                        if fld_data != '':
                            fld_data += ';'
                        fld_data += '0x%08X' % h

            if fld[1] == FIELD_STRLIST:

                fld_data = data.decode('utf-16le')
                str_list = list(filter(None, fld_data.split('\0')))
                fld_data = ';'.join(str_list)

            elif fld[1] == FIELD_TEXT:

                fld_data = data.decode()

            if fld[0] == 'note':
                save_data_to_file(dest_dir + 'ransom_note.txt', data)
                print('ransom note saved to file.')

        cfg[fld[0]] = fld_data

    pos += 4

config['config'] = cfg

# Save configuration data
with io.open(dest_dir + 'config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)
