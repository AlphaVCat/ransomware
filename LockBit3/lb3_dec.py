from unicorn import *
from unicorn.x86_const import *


# Decrypt helper offset
DECR_HELPER_OFFSET = 0x83


# Emulation
BASE_ADDR = 0x10000
# Stack
STACK_SIZE = 0x10000
STACK_INIT_POS = (STACK_SIZE // 2) & ~0xFF


def decrypt_block_helper(helper_code, seed, n):
    """Decrypt block helper"""

    try:

        # Initialize emulator
        mu = Uc(UC_ARCH_X86, UC_MODE_32)

        code_size = (len(helper_code) + 1 + 0xFFFF) & ~0xFFFF
        stack_addr = BASE_ADDR + code_size

        # Map memory for this emulation
        mu.mem_map(BASE_ADDR, code_size + STACK_SIZE)

        end_code_addr = BASE_ADDR + len(helper_code)

        # Write code to memory
        mu.mem_write(BASE_ADDR, helper_code)
        # Add nop to code
        mu.mem_write(end_code_addr, b'\x90')

        stack_pos = stack_addr + STACK_INIT_POS

        # Write function parameters to memory
        # Write n
        mu.mem_write(stack_pos, n.to_bytes(8, byteorder='little'))
        # Write seed
        mu.mem_write(stack_pos + 8, seed.to_bytes(8, byteorder='little'))
        # Write n address
        mu.mem_write(stack_pos - 4, stack_pos.to_bytes(4, byteorder='little'))
        # Write seed address
        mu.mem_write(stack_pos - 8, (stack_pos + 8).to_bytes(4, byteorder='little'))
        # Write return address
        mu.mem_write(stack_pos - 12, end_code_addr.to_bytes(4, byteorder='little'))

        mu.reg_write(UC_X86_REG_ESP, stack_pos - 12)
        mu.reg_write(UC_X86_REG_EBP, stack_pos)

        # Emulate machine code in infinite time
        mu.emu_start(BASE_ADDR + DECR_HELPER_OFFSET, end_code_addr + 1)

        # Get mask
        x0 = mu.reg_read(UC_X86_REG_EAX)
        x1 = mu.reg_read(UC_X86_REG_EDX)

        # Read n value
        n_data = mu.mem_read(stack_pos, 8)

        return ((x1 << 32) | x0), int.from_bytes(n_data, byteorder='little')

    except UcError as e:

        print('Emu Error: %s' % e)
        return None


def make_byte_mask(x):

    mask = b''

    x0 = x & 0xFFFFFFFF
    x1 = x >> 32

    for _ in range(2):

        mask += bytes([x0 & 0xFF])
        x0 >>= 8
        b3 = x1 & 0xFF
        x1 >>= 8
        mask += bytes([x1 & 0xFF])
        mask += bytes([x0 & 0xFF])
        mask += bytes([b3])

        x0 >>= 8
        x1 >>= 8

    return mask


def decrypt(helper_code, data, seed):

    dec_data = b''

    n = seed

    pos = 0

    size = len(data)

    while (size != 0):

        r = decrypt_block_helper(helper_code, seed, n)
        if r is None:
            return None

        x = make_byte_mask(r[0])
        n = r[1]

        block_size = min(8, size)

        for i in range(block_size):
            dec_data += bytes([data[pos + i] ^ x[i]])

        pos += block_size
        size -= block_size

    return dec_data
