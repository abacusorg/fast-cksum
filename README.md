# fast-cksum
A fast, drop-in replacement for the GNU cksum utility.  Also has C and Python bindings.

## Overview
fast-cksum is a checksum utility that computes a 32-bit CRC in the GNU cksum convention,
using lookup tables for high performance.  This means that one can compute checksums
with this utility and they can be verified by end users with GNU cksum (which, as part
of GNU coreutils, is already installed on most Linux systems).

In particular, this code directly uses [Stephan Brumme's Fast CRC32 code](https://github.com/stbrumme/crc32)
as the core of its CRC32 functionality, but with newly computed lookup tables
and a slightly modified algorithm to match cksum.

## Requirements
fast-cksum is written in C++11, although the header will compile against C99 code, too.  The Python bindings use Python 3 and CFFI.  The build system uses make.

## Compiling
Run `make` from the repository root to build the command-line interface (CLI) and the Python bindings.  The CLI will be installed to `bin`.


## CLI Usage
The usage of the CLI is very similar to GNU cksum: 
```console
$ fast_cksum FILE [FILE]...
```

The output format is identical to that of GNU cksum.  In particular, there is one line of output per file in the format `<checksum> <file size> <filename>`.
For example:
```
1758675646 144185735 file1.dat
1906361843 123906288 file2.dat
3087645703 100255241 file3.dat
2775744001 88244488 file4.dat
```

Another utility called `fast_cksum_store` is provided to read data from stdin and write it to a file while writing the checksum to stdout.
For example, to write data from the `generate_data` program to `out.dat` while appending the checksum to `checksums.crc32`, use:
```console
$ generate_data | fast_cksum_store out.dat >> checksums.crc32
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
The GNU coreutils' cksum uses an non-standard variant of CRC32, but cksum's
ubiquity on Linux systems makes it useful to conform to that variant.  The generating
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

## License
fast-cksum is licensed under the GPLv3, a copy of which is found in the `LICENSE` file.

Stephan Brumme's Fast CRC32 code is used under the terms of the zlib license, a copy of which is found in the `license-stbrumme.crc32` file.
