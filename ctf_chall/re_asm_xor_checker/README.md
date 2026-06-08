# XOR Flag Checker

ByteSec local reverse engineering challenge for the assembly module.

Goal: recover a flag matching:

```text
BYTESEC{16_hex_characters}
```

## Build

```bash
make
```

## Run

```bash
./xor_checker
./xor_checker BYTESEC{exampleexample}
```

## Suggested Tools

```bash
file ./xor_checker
strings -a ./xor_checker
objdump -d -M intel ./xor_checker | less
gdb ./xor_checker
```

## Challenge Notes

The checker rejects incorrect length and format before the XOR comparison. The flag bytes are stored as encoded values and checked with a repeating key.

For a student-facing distribution, provide the compiled `xor_checker` binary. The C source is kept here so the project can rebuild the challenge consistently.
