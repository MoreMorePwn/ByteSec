# Module 20: Stack Overflows and Control Data

> Beginner | 25 minutes | 5 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Explain how a stack overflow moves from data corruption to control-flow corruption
- Recognize unsafe C input patterns
- Use endianness when placing addresses in payloads
- Describe how offset discovery turns a crash into a repeatable exploit primitive

---

## Lesson Flow

### 20.1 - From Long Input to Crash

**Narrative**: A segmentation fault is not automatically exploitable, but it is an important signal. If a long input crashes a program after returning from a function, the crash may happen because the saved return address was overwritten with bytes from the input.

Example payload shape:

```text
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
BBBBBBBB
CCCCCCCC
```

For a 32-byte buffer, the `A` bytes fill the buffer, the `B` bytes overwrite saved `rbp`, and the `C` bytes are interpreted as the next return address.

---

#### Activity 20.1a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Easy

**Prompt**: If the saved return address is overwritten with eight `C` bytes, what value would those bytes represent in hexadecimal ASCII?

**Options**:
- A) `0x4141414141414141`
- B) `0x4242424242424242`
- C) `0x4343434343434343`
- D) `0x0000000000000000`

**Answer**: **C** - ASCII `C` is `0x43`, repeated eight times.

**Explanation**: Seeing `0x4343434343434343` in an instruction pointer crash is a strong sign that input reached saved control data.

**Hint**: ASCII `A`, `B`, and `C` are `0x41`, `0x42`, and `0x43`.

---

### 20.2 - Unsafe and Safer Input Functions

**Narrative**: The core issue is whether the input function knows the destination buffer size.

| Pattern | Risk |
|---------|------|
| `gets(buf)` | Always unsafe; no size limit |
| `scanf("%s", buf)` | Unsafe unless a width is supplied |
| `scanf("%31s", buf)` | Better for a 32-byte string buffer |
| `fgets(buf, sizeof(buf), stdin)` | Safer when size is correct |

Safer code is not just about picking a different function. The length must match the destination buffer and leave room for a null terminator when treating data as a C string.

---

#### Activity 20.2a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: Which input pattern is safest for `char name[32]` among these options?

**Options**:
- A) `fgets(name, sizeof(name), stdin)`
- B) `gets(name)`
- C) `scanf("%s", name)`
- D) `read(0, name, 128)`

**Answer**: **A** - `fgets` receives the destination size through `sizeof(name)`.

**Explanation**: The other options can write more than 32 bytes into the buffer.

**Hint**: Pick the option that includes the buffer size.

---

### 20.3 - Little-Endian Address Packing

**Narrative**: x86-64 stores multi-byte integers in little-endian order. That means the least significant byte appears first in memory.

Address:

```text
0x0000000000401186
```

Payload bytes:

```text
86 11 40 00 00 00 00 00
```

When building payloads in Python, `struct.pack("<Q", address)` packs an unsigned 64-bit value in little-endian order.

---

#### Activity 20.3a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Medium

**Prompt**: In Python, the `struct.pack` format for a little-endian unsigned 64-bit integer is `____`.

**Expected Answer**: `<Q`

**Acceptable Variations**: `"<Q"`, `'<Q'`

**Explanation**: `<` means little-endian and `Q` means unsigned long long, which is 8 bytes.

**Hint**: One character chooses byte order and one character chooses size/type.

---

### 20.4 - Offset Discovery

**Narrative**: The exploit offset is the number of bytes before the saved return address. In training binaries, you can often calculate it from the stack frame. In unknown binaries, use a cyclic pattern so the crash value tells you exactly which input bytes reached `rip`.

Common workflow:

```bash
python3 - <<'PY'
from string import ascii_uppercase
print("".join(a+b+c for a in ascii_uppercase for b in ascii_uppercase for c in ascii_uppercase)[:120])
PY
```

Tools such as pwntools and GDB plugins can automate cyclic pattern generation and lookup, but the idea is simple: use a non-repeating input so the crash value maps back to one offset.

---

#### Activity 20.4a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: Why is a cyclic pattern more useful than `AAAA...` for offset discovery?

**Options**:
- A) Each crash substring maps back to a unique position
- B) It prevents the program from crashing
- C) It disables stack canaries
- D) It changes the binary from PIE to non-PIE

**Answer**: **A** - Unique pattern chunks make it possible to identify the exact overwrite offset.

**Explanation**: Repeated `A` bytes prove control, but they do not reveal which exact byte position reached the saved return address.

**Hint**: A useful crash pattern should encode position.

---

### 20.5 - Reading the Crash Carefully

**Narrative**: A crash should answer specific questions:

- Did the process crash before or after returning from the vulnerable function?
- Did input bytes reach saved `rbp`?
- Did input bytes reach the saved return address?
- Are addresses stable across runs?
- Which mitigations are enabled?

This keeps exploitation disciplined. The goal is not "make it crash"; the goal is to learn whether the input controls a value that matters.

---

#### Activity 20.5a - SPOT THE BUG

> **Type**: SPOT
> **Difficulty**: Medium

**Prompt**: Which line turns a bounded stack buffer into a control-flow risk?

```c
1 void handle(void) {
2     char order[48];
3     puts("Order:");
4     read(0, order, 96);
5     puts("Thanks");
6 }
```

**Answer**: Line 4 - the program reads 96 bytes into a 48-byte buffer.

**Explanation**: `read` can be safe when the count is correct. Here the count is twice the buffer size, so input can continue into saved stack data.

**Hint**: Compare the byte count with the array size.
