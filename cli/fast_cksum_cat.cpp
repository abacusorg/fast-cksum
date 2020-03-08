/*

Echos files to stdout while verifying their checksum.

Usage: fast_cksum_cat -c CHECKSUM_FILE FILENAME [FILENAME ...]

TODO: overlap compute and IO

*/

#include <unistd.h>
#include <cstdio>
#include <cinttypes>
#include <cstdlib>
#include <cerrno>
#include <cstring>
#include <unordered_map>

#include "fast_cksum.cpp"

#define BUFSIZE (uint64_t) 64<<10  // 64 KB

int main(int argc, char *argv[]) {
    if (argc < 4){
        fprintf(stderr, "[fast_cksum_cat Error] Incorrect number of arguments.\nUsage: fast_cksum_cat -c CHECKSUM_FILE FILENAME [FILENAME ...]\n");
        exit(1);
    }

    // Parse the arguments
    char *checksum_fn = NULL;
    char *input_fns[argc-3];
    int ninputs = 0;
    for(int i = 1; i < argc; i++){
        if(strcmp(argv[i],"-c") == 0){
            if(checksum_fn != NULL){
                fprintf(stderr, "[fast_cksum_cat Error] May only specify -c once!\n");
                exit(1);
            }
            i++;
            checksum_fn = argv[i];
        }
        else {
            input_fns[ninputs++] = argv[i];
        }
    }

    if (checksum_fn == NULL){
        fprintf(stderr, "[fast_cksum_cat Error] Must specify -c CHECKSUM_FILE!\n");
        exit(1);
    }

    // Allocate the read buffer
    void *buffer = NULL;
    int ret = posix_memalign(&buffer, 65536, BUFSIZE);
    if(ret != 0 || buffer == NULL){
        fprintf(stderr, "[fast_cksum_cat Error] Failed to allocate %" PRIu64 " bytes\n", BUFSIZE);
        exit(1);
    }

    // Read the checksums from the checksum file
    FILE *cfp = fopen(checksum_fn, "r");
    if (cfp == NULL) {
        if(errno)
            perror(checksum_fn);
        else
            fprintf(stderr, "[fast_cksum_cat Error] File %s not found or cannot be opened.\n", checksum_fn);
        exit(1);
    }
    
    std::unordered_map<std::string,uint32_t> known_crcs;
    std::unordered_map<std::string,size_t> known_sizes;
    char *line = NULL;  size_t linen = 0;
    while(getline(&line, &linen, cfp) != -1){
        uint32_t _crc; size_t _sz; char _fn[1024];
        int count = sscanf(line, "%u %zu %1023s\n", &_crc, &_sz, _fn);
        if(count != 3){
            fprintf(stderr, "[fast_cksum_cat Error] Did not understand line \"%s\" in checksum file %s\n", line, checksum_fn);
            exit(1);
        }
        if(known_sizes.count(_fn) || known_crcs.count(_fn)){
            fprintf(stderr, "[fast_cksum_cat Error] Duplicate entry \"%s\" in checksum file %s!\n", _fn, checksum_fn);
            exit(1);
        }
        known_sizes[_fn] = _sz;
        known_crcs[_fn] = _crc;
    }
    free(line);
    fclose(cfp);

    // Check that all input files are present in the checksum list
    for(int i = 0; i < ninputs; i++){
        const char *fn = input_fns[i];
        if(!known_crcs.count(fn)){
            fprintf(stderr, "[fast_cksum_cat Error] File \"%s\" not found in checksum file %s\n", fn, checksum_fn);
            exit(1);
        }
    }


    // Now start cat-ing and checksumming the input files
    for(int i = 0; i < ninputs; i++){
        const char *fn = input_fns[i];

        FILE *fp = fopen(fn, "rb");
        if (fp == NULL) {
            if(errno)
                perror(fn);
            else
                fprintf(stderr, "[fast_cksum_cat Error] File %s not found or cannot be opened.\n", fn);
            exit(1);
        }

        uint32_t partial_crc = CRC32_FAST_SEED;
        size_t totalsize = 0;
        size_t count;
        while((count = fread(buffer, 1, BUFSIZE, fp))){
            fwrite(buffer, 1, count, stdout);
            if(ferror(stdout)){
                perror("stdout");
                exit(1);
            }
            partial_crc = crc32_fast_partial(buffer, count, partial_crc);
            totalsize += count;
        }
        if(ferror(fp)){
            perror(fn);
            exit(1);
        }
        fclose(fp);

        uint32_t crc = crc32_fast_finalize(totalsize, partial_crc);

        if(totalsize != known_sizes[fn]){
            fprintf(stderr, "[fast_cksum_cat Error] Read size %zu from file %s; expected %zu based on checksum file %s\n",
                totalsize, fn, known_sizes[fn], checksum_fn);
            exit(1);
        }

        if(crc != known_crcs[fn]){
            fprintf(stderr, "[fast_cksum_cat Error] Computed checksum %u from file %s; expected %u based on checksum file %s\n",
                crc, fn, known_crcs[fn], checksum_fn);
            exit(1);
        }

    }

    free(buffer);

    return 0;
}
