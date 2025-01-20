"""
Defines the FFI to crc32_fast
"""

from os.path import join as pjoin, dirname

from cffi import FFI

ffi = FFI()

ffi.cdef("""
    #define CRC32_FAST_SEED 0xFFFFFFFF
    uint32_t crc32_fast(const void* data, size_t length);
    uint32_t crc32_fast_partial(const void* data, size_t length, uint32_t previousCrc32);
    uint32_t crc32_fast_finalize(size_t total_length, uint32_t previousCrc32);
    """)

sopath = pjoin(dirname(__file__), 'fast_cksum.so')
lib = ffi.dlopen(sopath)

globals().update({f: getattr(lib, f) for f in dir(lib)})
