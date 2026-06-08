CC ?= gcc
CFLAGS ?= -O0 -g -fno-stack-protector -no-pie -z noexecstack -Wall -Wextra

.PHONY: all clean

all: ret2win

ret2win: ret2win.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f ret2win
