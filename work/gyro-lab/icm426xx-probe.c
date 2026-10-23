#include <errno.h>
#include <fcntl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    unsigned char reg = 0x75;
    unsigned char value = 0;
    struct i2c_msg msgs[2];
    struct i2c_rdwr_ioctl_data transfer;
    int fd;

    if (argc != 2) {
        fprintf(stderr, "usage: %s /dev/i2c-N\n", argv[0]);
        return 2;
    }

    fd = open(argv[1], O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        fprintf(stderr, "%s: open: %s\n", argv[1], strerror(errno));
        return 1;
    }

    msgs[0] = (struct i2c_msg) { .addr = 0x68, .flags = 0, .len = 1, .buf = &reg };
    msgs[1] = (struct i2c_msg) { .addr = 0x68, .flags = I2C_M_RD, .len = 1, .buf = &value };
    transfer = (struct i2c_rdwr_ioctl_data) { .msgs = msgs, .nmsgs = 2 };

    if (ioctl(fd, I2C_RDWR, &transfer) < 0) {
        fprintf(stderr, "%s: 0x68/0x75: %s\n", argv[1], strerror(errno));
        close(fd);
        return 1;
    }

    printf("%s: ICM426xx WHO_AM_I = 0x%02x\n", argv[1], value);
    close(fd);
    return 0;
}
