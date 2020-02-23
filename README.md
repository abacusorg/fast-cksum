# fast-cksum
A fast, drop-in replacement for the GNU `cksum` utility.  Also has C and Python bindings.

## Overview
The GNU `cksum` utility is very useful for computing 32-bit CRC checksums on files,
but it's too slow for many applications.  Much faster CRC32 implementations are possible
and are widely available online, but most (none?) of them use the same CRC algorithm
as `cksum` because of its slightly non-standard algorithm.  Due to its ubiquity, however,
it can be convenient to follow `cksum`'s conventions.  `fast-cksum` is designed to achieve
the speed of modern CRC32 implementations while using the `cksum` algorithm.

In particular, this code directly uses [Stephan Brumme's Fast CRC32 code](https://create.stephan-brumme.com/crc32/)
as the core of its CRC32 functionality, but with newly computed lookup tables
and a slightly modified algorithm to match `cksum`.

## Requirements
`fast-cksum` is written in C++11, although the header will compile against C99 code, too.  The Python bindings use Python 3 and CFFI.  The build system uses make.

## Compiling
Run `make` from the repository root to build the command-line interface (CLI) and the Python bindings.  The CLI will be installed to `bin`.


## CLI Usage
The usage of the CLI is very similar to GNU `cksum`: 
```console
$ ./bin/fast_cksum FILE [FILE]...
```

The output format is identical to that of GNU `cksum`.  In particular, there is one line of output per file in the format `<checksum> <file size> <filename>`.
For example:
```
1758675646 144185735 DESI_L760_N2660_prototype.z0.100.slab0000.field_pack9.dat
1906361843 123906288 DESI_L760_N2660_prototype.z0.100.slab0000.field_pack9_pids.dat
3087645703 100255241 DESI_L760_N2660_prototype.z0.100.slab0000.L0_pack9.dat
2775744001 88244488 DESI_L760_N2660_prototype.z0.100.slab0000.L0_pack9_pids.dat
```

## Python Usage
TODO

## Performance
High performance in CRC32 is obtained by precomputing a lookup table with 256 values,
one for each possible outcome of 1 byte convolved with the CRC32 generating polynomial.
And even higher performance is obtained by precomputing 16 such tables from the
composition of lookups, allowing for processing 16 bytes at a time.  This gets the
performance up to several GB/s on one CPU core, which is almost memory-bandwidth limited.

We also include an extension of the table scheme to 32 bytes, but it has virtually no
impact on performance (while going from 8 to 16 is about a factor of 2).


## GNU cksum
The GNU coreutils' cksum uses an unfortuantely non-standard variant of CRC32, but cksum's
ubiquity on Linux system means we probably want to conform to that variant.  The generating
polynomial is the usual one, just bit-reversed (see: https://en.wikipedia.org/wiki/Cyclic_redundancy_check#Polynomial_representations_of_cyclic_redundancy_checks).
The byte processing order is also swapped.  We regenerated the lookup
tables in Stephan Brumme's CRC32 code in this convention, and modified the algorithms
similarly.

This page describes GNU's cksum variant: https://pubs.opengroup.org/onlinepubs/009695399/utilities/cksum.html


## Source layout
The `src` directory contains the core C++ source code and header files.

The `cli` directory contains the `fast_cksum` command-line interface, as well as a `fast_cksum_store` utility.  They will be installed into the `bin` directory by default.

The `fast_cksum` directory contains Python bindings.

## TODO
- Migrate installation to pip or conda
- Add multi-threaded support
- Add big-endian support
- Python documentation
- CLI help
- More performance numbers
