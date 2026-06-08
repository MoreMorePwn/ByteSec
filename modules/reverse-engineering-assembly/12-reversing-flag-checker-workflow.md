# Module 12: Reversing a Flag Checker Workflow

> Intermediate | 20 minutes | 4 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Triage a provided binary with standard command-line tools
- Locate validation functions and success/failure strings
- Recover input constraints from comparisons
- Reverse a simple XOR byte array by hand

---

## Lesson Flow

### 12.1 - Static Triage First

**Narrative**: Before debugging, inspect the file. A calm first pass often reveals architecture, symbols, strings, and candidate functions.

Useful commands:

```bash
file ./xor_checker
strings -a ./xor_checker
objdump -d -M intel ./xor_checker | less
```

`strings` is helpful, but encoded flags usually will not appear directly. That is the point of the checker.

---

#### Activity 12.1a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: Why might `strings` fail to show the full flag in an XOR checker?

**Options**:
- A) The flag bytes are stored in encoded form
- B) The binary cannot contain strings
- C) The CPU deletes strings at runtime
- D) `strings` only works on Python files

**Answer**: **A** - XOR checkers often store transformed bytes instead of the plaintext flag.

**Explanation**: If the binary compares `input[i] ^ key[i]` to an encoded byte, the full plaintext flag does not need to exist as a contiguous string in the file.

---

### 12.2 - Reading Length and Format Checks

**Narrative**: Most flag checkers reject obvious bad input before doing deeper validation.

```asm
call strlen
cmp rax, 25
jne fail
```

This means the accepted input length must be 25 bytes. For `BYTESEC{16_hex_chars}`, that length makes sense:

```text
BYTESEC{ = 8 bytes
16 hex characters = 16 bytes
} = 1 byte
Total = 25 bytes
```

---

#### Activity 12.2a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Easy

**Prompt**: What length does this checker require?

```asm
call strlen
cmp rax, 25
jne fail
```

**Options**:
- A) 16 bytes
- B) 24 bytes
- C) 25 bytes
- D) Any length

**Answer**: **C** - The code jumps to failure unless the result from `strlen` equals `25`.

**Explanation shown after answering**: Length checks are quick wins in reversing. They constrain the answer before you inspect the byte-by-byte loop.

---

### 12.3 - Reversing XOR Bytes

**Narrative**: XOR is its own inverse:

```text
encoded = plain ^ key
plain = encoded ^ key
```

If a checker has:

```c
expected[0] = 0x51;
key[0] = 0x13;
```

Then:

```text
0x51 ^ 0x13 = 0x42
```

`0x42` is ASCII `B`.

---

#### Activity 12.3a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Medium

**Prompt**: Recover the original byte from `expected = 0x51` and `key = 0x13`. Answer as a hex byte.

**Expected Answer**: `0x42`

**Acceptable variations**: `42`, `B`, `b`

**Hint**: XOR the expected byte with the key byte.

**Explanation**: `0x51 ^ 0x13 = 0x42`, which is the ASCII value for `B`.

---

### 12.4 - Workflow for the Final Lab

**Narrative**: The final lab is intentionally small. The goal is not to fight tooling; the goal is to practice a clean workflow:

1. Run the binary with a test input.
2. Use `strings` to find success and failure text.
3. Disassemble the checker function.
4. Confirm the length and format checks.
5. Identify the XOR key and encoded byte array.
6. XOR the arrays to recover the flag.
7. Submit the flag in ByteSec.

---

#### Activity 12.4a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: Which step directly recovers the flag from an XOR checker once you have the key and encoded bytes?

**Options**:
- A) Delete the failure branch
- B) XOR each encoded byte with the matching key byte
- C) Convert the binary to SQL
- D) Run `strings` again with administrator privileges

**Answer**: **B** - XORing the encoded bytes with the same key recovers the original bytes.

**Explanation**: Patching can bypass a check, but recovering the actual flag requires reversing the byte transformation.

---

## Module Summary

Good reversing is repeatable: triage, find strings, find references, read checks, decode data, confirm by running the program.
