CC ?= gcc
CFLAGS ?= -O0 -g -fno-stack-protector -no-pie -Wall -Wextra
TARGET := xor_checker

.PHONY: all clean

all: $(TARGET)

$(TARGET): checker.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f $(TARGET)
