#!/usr/bin/env python3
"""
Merges checksum files in the cksum convention, sorting on filename.
Writes to stdout.

Usage
-----
$ ./merge_checksum_files.py --delete *.crc32 > checksums.crc32
"""

import os
import sys
import argparse


def merge(checksum_files, delete=False):
    lines = []
    for fn in checksum_files:
        with open(fn, 'r') as fp:
            lines += fp.readlines()
    lines = [line.split() for line in set(lines)]
    lines.sort(key=lambda L: L[-1])

    # Duplicates check
    for i, line in enumerate(lines[:-1]):
        if line[-1] == lines[i + 1][-1]:
            print(
                f'[merge_checksum_files.py] Error: duplicate filename {line[-1]} found',
                file=sys.stderr,
            )
            sys.exit(1)  # Almost certainly want to exit, no good can come of this!

    lines = [' '.join(line) for line in lines]

    # Write the sorted result to stdout
    print('\n'.join(lines))

    if delete:
        for fn in checksum_files:
            os.remove(fn)


class ArgParseFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=ArgParseFormatter
    )
    parser.add_argument(
        'checksum_files',
        nargs='+',
        help='One or more checksum files to merge',
        metavar='FILE',
    )
    parser.add_argument('--delete', action='store_true', help='Delete the input files')

    args = parser.parse_args()
    args = vars(args)

    merge(**args)
