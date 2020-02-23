/*

Reads data from stdin and writes it to FILENAME.
Writes the checksum to stdout.

Usage: generate_data | fast_cksum_store FILENAME [ >> CHECKSUM_FILE]

TODO: overlap compute and IO

*/

#include <unistd.h>
#include <cstdio>
#include <cinttypes>
#include <cstdlib>
#include <cerrno>

#include "fast_cksum.cpp"

#define BUFSIZE (uint64_t) 64<<10  // 64 KB

int main(int argc, char *argv[]) {
    if (argc != 2){
        fprintf(stderr, "Incorrect number of arguments.\nUsage: generate_data | fast_cksum_store FILENAME [ >> CHECKSUM_FILE]\n");
        exit(1);
    }

    const char *fn = argv[1];

    void *buffer = NULL;
    int ret = posix_memalign(&buffer, 65536, BUFSIZE);
    if(ret != 0 || buffer == NULL){
        fprintf(stderr, "Failed to allocate %" PRIu64 " bytes\n", BUFSIZE);
        exit(1);
    }

    FILE *fp = fopen(fn, "rb");
    if (fp == NULL) {
        if(errno)
            perror(fn);
        else
            fprintf(stderr, "File %s not found or cannot be opened.\n", fn);
        exit(1);
    }

    uint32_t partial_crc = CRC32_FAST_SEED;
    size_t totalsize = 0;
    size_t count;
    while((count = fread(buffer, 1, BUFSIZE, stdin))){
        fwrite(buffer, 1, count, fp);
        if(ferror(stdout)){
            perror("stdout");
            exit(1);
        }
        partial_crc = crc32_fast_partial(buffer, count, partial_crc);
        totalsize += count;
    }
    if(ferror(stdin)){
        perror("stdin");
    }

    fclose(fp);

    uint32_t crc = crc32_fast_finalize(totalsize, partial_crc);

    printf("%" PRIu32 " %" PRIu64 " %s\n", crc, totalsize, fn);

    free(buffer);
}
