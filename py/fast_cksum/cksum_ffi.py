"""
Defines the FFI to crc32_fast
"""

__all__ = [
    'CRC32_FAST_SEED',
    'crc32_fast',
    'crc32_fast_partial',
    'crc32_fast_finalize',
    'ffi',
]

from os.path import join as pjoin, dirname

from cffi import FFI

ffi = FFI()

ffi.cdef("""
#define CRC32_FAST_SEED 0xFFFFFFFF
uint32_t crc32_fast(const void* data, size_t length);
uint32_t crc32_fast_partial(const void* data, size_t length, uint32_t previousCrc32);
uint32_t crc32_fast_finalize(size_t total_length, uint32_t previousCrc32);
""")

sopath = pjoin(dirname(__file__), 'libfast_cksum.so')
lib = ffi.dlopen(sopath)

CRC32_FAST_SEED = lib.CRC32_FAST_SEED
crc32_fast = lib.crc32_fast
crc32_fast_partial = lib.crc32_fast_partial
crc32_fast_finalize = lib.crc32_fast_finalize
