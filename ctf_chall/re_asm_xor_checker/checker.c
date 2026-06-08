#include <ctype.h>
#include <stdio.h>
#include <string.h>

#define FLAG_LEN 25

static const unsigned char xor_key[] = {
    0x13, 0x37, 0x5a, 0xc0, 0x21, 0x09, 0x7e,
};

static const unsigned char encoded_flag[] = {
    0x51, 0x6e, 0x0e, 0x85, 0x72, 0x4c, 0x3d, 0x68, 0x55, 0x6d,
    0xa2, 0x40, 0x68, 0x1a, 0x26, 0x04, 0x3c, 0xf2, 0x13, 0x6f,
    0x1b, 0x77, 0x03, 0x6b, 0xbd,
};

static int has_flag_format(const char *input) {
    static const char prefix[] = {'B', 'Y', 'T', 'E', 'S', 'E', 'C', '{'};
    size_t len = strlen(input);

    if (len != FLAG_LEN) {
        return 0;
    }

    for (size_t i = 0; i < sizeof(prefix); i++) {
        if (input[i] != prefix[i]) {
            return 0;
        }
    }

    for (size_t i = 8; i < 24; i++) {
        if (!isxdigit((unsigned char)input[i])) {
            return 0;
        }
    }

    return input[24] == '}';
}

static int check_flag(const char *input) {
    unsigned int diff = 0;

    if (!has_flag_format(input)) {
        return 0;
    }

    for (size_t i = 0; i < FLAG_LEN; i++) {
        unsigned char ch = (unsigned char)input[i];
        if (i >= 8 && i < 24) {
            ch = (unsigned char)tolower(ch);
        }
        diff |= (unsigned int)((ch ^ xor_key[i % sizeof(xor_key)]) ^ encoded_flag[i]);
    }

    return diff == 0;
}

int main(int argc, char **argv) {
    char input[128];

    puts("ByteSec XOR checker");
    puts("Flag format: BYTESEC{16 hex characters}");

    if (argc > 1) {
        snprintf(input, sizeof(input), "%s", argv[1]);
    } else {
        printf("flag> ");
        if (fgets(input, sizeof(input), stdin) == NULL) {
            puts("no input");
            return 1;
        }
        input[strcspn(input, "\r\n")] = '\0';
    }

    if (check_flag(input)) {
        puts("correct");
        return 0;
    }

    puts("wrong");
    return 1;
}
