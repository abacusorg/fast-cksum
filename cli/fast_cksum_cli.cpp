/*

A fast version of the GNU cksum utility.

*/

#include <unistd.h>
#include <stdio.h>
#include <inttypes.h>
#include <stdlib.h>

#include "fast_cksum.cpp"

#define BUFSIZE (uint64_t) 64<<10  // 64 KB

void print_data(FILE *fp, const char *fn){
    void *buffer = NULL;
    int ret = posix_memalign(&buffer, 65536, BUFSIZE);
    if(ret != 0 || buffer == NULL){
        fprintf(stderr, "Failed to allocate %" PRIu64 " bytes\n", BUFSIZE);
        exit(1);
    }

    uint32_t partial_crc = CRC32_FAST_SEED;
    size_t totalsize = 0;
    size_t count;
    while((count = fread(buffer, 1, BUFSIZE, fp))){
        partial_crc = crc32_fast_partial(buffer, count, partial_crc);
        totalsize += count;
    }
    if(ferror(fp)){
        perror(fn);
        return;
    }

    uint32_t crc = crc32_fast_finalize(totalsize, partial_crc);

    // TOOD: double-check trailing space for blank fn
    printf("%" PRIu32 " %" PRIu64 " %s\n", crc, totalsize, fn);

    free(buffer);
}

int main(int argc, char *argv[]) {
    if (argc == 1)
        print_data(stdin, "");
    else {
        for (int f = 1; f < argc; f++) {
	        FILE *fp;
	        fp = fopen(argv[f],"rb");
	        if (fp == NULL) {
	            fprintf(stderr, "File %s not found or cannot be opened.\n", argv[f]);
	        	exit(1);
	        }
	        print_data(fp, argv[f]);
	        fclose(fp);
    	}
    }
    return 0;
}
