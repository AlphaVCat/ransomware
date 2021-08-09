import base64
import struct
import md4
import bm_hash


MACHINE_GUID = '873ba7f3-0986-40d0-97df-a1e48ced854f'


def get_victim_id(machine_guid):

    h = 0xFFFFFFFF
    for _ in range(3):
        h = bm_hash.get_wide_str_hash(MACHINE_GUID, h)

    s = h.to_bytes(4, byteorder='little')
    s += s[::-1]

    victim_id = base64.encodebytes(s).strip()
    victim_id = bytearray(victim_id[:9])
    for i in range(len(victim_id)):
        if (victim_id[i] == 0x2B):    # '+'
            victim_id[i] = 0x78       # 'x'
        elif (victim_id[i] == 0x2F):  # '/'
            victim_id[i] = 0x69       # 'i'
        elif (victim_id[i] == 0x3D):  # '='
            victim_id[i] = 0x7A       # 'z'

    return victim_id.decode()


def get_bot_id(machine_guid, bigendian=False):

    h1 = bm_hash.get_wide_str_hash(MACHINE_GUID, 0)

    h2 = md4.hash(h1.to_bytes(4, byteorder='little'))

    n = struct.unpack(('>' if bigendian else '<') + '4L', h2)

    return ('%.8x%.8x%.8x%.8x' % n)


victim_id = get_victim_id(MACHINE_GUID)
print('victim_id: \"%s\"' % victim_id)

bot_id = get_bot_id(MACHINE_GUID, True)
print('bot_id:    \"%s\"' % bot_id)

mutex_name = get_bot_id(MACHINE_GUID, False)
print('mutex:     \"Global\\%s\"' % mutex_name)
