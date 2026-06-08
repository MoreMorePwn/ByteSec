# Module 11: Control Flow, Memory, and Encoded Data

> Intermediate | 25 minutes | 4 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Interpret common compare, test, and conditional jump patterns
- Trace simple loops over input bytes
- Read byte-oriented memory operands
- Recognize XOR as a reversible encoding operation

---

## Lesson Flow

### 11.1 - Comparisons and Conditional Jumps

**Narrative**: `cmp` and `test` set CPU flags. Conditional jumps read those flags.

```asm
cmp eax, 0
je is_zero
jne is_not_zero
```

For reverse engineering, the exact flag math matters less at first than the branch meaning: which path is taken for valid input?

---

#### Activity 11.1a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: What does `je success` mean immediately after `cmp al, 0x42`?

**Options**:
- A) Jump to `success` when `al` equals `0x42`
- B) Jump to `success` when `al` is greater than `0x42`
- C) Always jump to `success`
- D) Call the function named `success`

**Answer**: **A** - `je` means jump if equal.

**Explanation**: After `cmp al, 0x42`, the zero flag is set when both values are equal. `je` follows that equal path.

---

### 11.2 - Loops Over Bytes

**Narrative**: Flag checkers often loop over every input byte. The loop counter may live in `ecx`, `edx`, or another register. Memory operands such as `[rdi + rcx]` mean "read from the address in `rdi` plus the index in `rcx`."

```asm
xor ecx, ecx
loop_start:
    movzx eax, byte ptr [rdi + rcx]
    cmp al, byte ptr [rsi + rcx]
    jne fail
    inc rcx
    cmp rcx, 25
    jne loop_start
```

---

#### Activity 11.2a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: How many byte positions does this loop check before it can finish successfully?

```asm
xor ecx, ecx
loop_start:
    movzx eax, byte ptr [rdi + rcx]
    cmp al, byte ptr [rsi + rcx]
    jne fail
    inc rcx
    cmp rcx, 25
    jne loop_start
```

**Options**:
- A) 1
- B) 24
- C) 25
- D) It never stops

**Answer**: **C** - The counter starts at `0`, checks positions `0` through `24`, then stops when `rcx` becomes `25`.

**Explanation shown after answering**: Zero-based loops often compare the counter against the total length after incrementing. A final compare against `25` means 25 bytes were processed.

---

### 11.3 - Memory Operands and Byte Access

**Narrative**: A memory expression inside brackets reads or writes memory. The size marker tells you how many bytes are being accessed.

```asm
movzx eax, byte ptr [rdi + rcx]
```

Read this as:

1. Take the pointer in `rdi`.
2. Add index `rcx`.
3. Read one byte from that address.
4. Zero-extend it into `eax`.

---

#### Activity 11.3a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Easy

**Prompt**: In `byte ptr [rdi + rcx]`, which register is being used as the index?

**Expected Answer**: `rcx`

**Acceptable variations**: `RCX`, `the rcx register`

**Hint**: The base pointer is `rdi`; the value added to it changes each loop iteration.

**Explanation**: `rcx` is the index. If `rdi` points to the start of the input, then `[rdi + rcx]` reads the current input byte.

---

### 11.4 - XOR Encoding

**Narrative**: XOR is reversible. If a program stores `encoded = plain ^ key`, then the original byte is recovered with `plain = encoded ^ key`.

That makes XOR common in beginner reverse engineering challenges. It hides strings from `strings`, but it is not encryption when the key and encoded bytes are inside the binary.

```c
int check(const unsigned char *input) {
    unsigned char key = 0x37;
    unsigned char expected = 0x75;
    if (input[0] == 0) return 0;
    unsigned char value = input[0];
    value = value ^ key;
    return value == expected;
}
```

---

#### Activity 11.4a - SPOT THE LOGIC

> **Type**: SPOT
> **Difficulty**: Medium

**Prompt**: Click the line where the input byte is transformed before comparison.

```c
int check(const unsigned char *input) {
    unsigned char key = 0x37;
    unsigned char expected = 0x75;
    if (input[0] == 0) return 0;
    unsigned char value = input[0];
    value = value ^ key;
    return value == expected;
}
```

**Answer**: Line 6

**Hint**: Look for the operator that combines the input-derived byte with the key.

**Explanation**: Line 6 applies XOR to the input-derived value. To reverse this kind of check, XOR the expected byte with the same key.

---

## Module Summary

Control flow tells you which inputs survive. Memory operands tell you which bytes are checked. XOR tells you how stored bytes can be decoded.
