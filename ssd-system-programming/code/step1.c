// step1.c : write COUNT blocks one after another and time every single write.
//
//   gcc -O2 -Wall -o step1 step1.c        (from ssd-system-programming/code/)
//   truncate -s 1G /tmp/fake-ssd.img                 # a fake "drive" (a plain file)
//   ./step1 /tmp/fake-ssd.img 2000 > direct.csv        # O_DIRECT: skip the page cache
//   ./step1 /tmp/fake-ssd.img 2000 buffered > buf.csv  # normal writes: into RAM first
//
// Output: CSV, one line per write: i, offset in bytes, latency in microseconds.

#define _GNU_SOURCE             // O_DIRECT is a Linux extension: this makes <fcntl.h> define it
#include <fcntl.h>              // open(), O_* flags
#include <unistd.h>             // pwrite(), close()
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>               // clock_gettime()

// Time now in microseconds. CLOCK_MONOTONIC never jumps (unlike the wall clock,
// which NTP can move), so the difference of two calls is a true duration.
static double now_us(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e6 + t.tv_nsec / 1e3;
}

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "usage: %s FILE COUNT [buffered]\n", argv[0]);
        return 2;
    }
    const char *path = argv[1];
    long count = atol(argv[2]);
    int buffered = argc > 3 && strcmp(argv[3], "buffered") == 0;
    const size_t bs = 4096;     // one 4 KiB block: the FTL's mapping unit on most SSDs

    // 1. Open. O_DIRECT asks the kernel to move data straight between our buffer
    //    and the device, with no copy in the page cache. Without it, write()
    //    only copies into RAM and returns; the disk is written later.
    int flags = O_WRONLY | (buffered ? 0 : O_DIRECT);
    int fd = open(path, flags);
    if (fd < 0) {
        perror("open");         // prints e.g. "open: No such file or directory"
        return 1;
    }

    // 2. A buffer. O_DIRECT needs the buffer address, the length and the file
    //    offset all aligned (to the logical block size; 4096 is always safe).
    //    malloc() gives only 16-byte alignment, so use posix_memalign().
    void *buf;
    int err = posix_memalign(&buf, 4096, bs);
    if (err) {
        fprintf(stderr, "posix_memalign: %s\n", strerror(err));
        return 1;
    }

    // 3. Fill it with random-looking bytes (xorshift), not zeros: some controllers
    //    compress or skip zero data, and then we would measure that, not the NAND.
    uint64_t x = 88172645463325252ULL;
    for (size_t i = 0; i < bs / 8; i++) {
        x ^= x << 13; x ^= x >> 7; x ^= x << 17;
        ((uint64_t *)buf)[i] = x;
    }

    // 4. Write block 0, 1, 2 ... and time each pwrite().
    //    pwrite() = write at an explicit offset (no seek, no shared file position).
    printf("i,offset,lat_us\n");
    for (long i = 0; i < count; i++) {
        off_t off = (off_t)i * bs;
        double t0 = now_us();
        ssize_t n = pwrite(fd, buf, bs, off);
        double t1 = now_us();
        if (n != (ssize_t)bs) {             // -1 = error, smaller = short write
            if (n < 0) perror("pwrite");
            else fprintf(stderr, "short write: %zd of %zu bytes\n", n, bs);
            return 1;
        }
        printf("%ld,%lld,%.1f\n", i, (long long)off, t1 - t0);
    }

    free(buf);
    close(fd);
    return 0;
}
