# Module 09: Assembly Foundations for Reverse Engineering

> Beginner | 20 minutes | 4 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Explain why reverse engineers read assembly instead of source code
- Identify common x86-64 registers and register sizes
- Read Intel-style source and destination operands
- Recognize simple data movement, arithmetic, comparison, and zeroing patterns

---

## Lesson Flow

### 9.1 - Assembly Is Program Behavior

**Narrative**: A compiled binary does not keep the original source code structure. Instead, it stores machine instructions. A disassembler translates those bytes into assembly so you can inspect what the CPU will do.

When reversing a flag checker, you are usually asking:

- Where does input enter?
- What checks reject bad input?
- What data is compared against the transformed input?
- Which branch prints success?

```c
if (input[0] == 'B') {
    puts("ok");
} else {
    puts("nope");
}
```

The compiled version may become a sequence like:

```asm
movzx eax, byte ptr [rdi]
cmp al, 0x42
jne fail
```

---

#### Activity 9.1a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: What does a disassembler help you recover from a compiled binary?

**Options**:
- A) The exact original source code with comments
- B) A readable view of the CPU instructions
- C) The developer's password manager
- D) The database schema used by the application

**Answer**: **B** - A disassembler translates machine code bytes into assembly instructions. It will not restore comments or exact source code, but it exposes the logic you need to reason about behavior.

**Explanation**: Reverse engineering starts from observable behavior and instructions. Assembly is lower-level than C, but it is enough to reconstruct checks, branches, and data transformations.

---

### 9.2 - Registers and Sizes

**Narrative**: Registers are small storage locations inside the CPU. In x86-64, general-purpose registers include `rax`, `rbx`, `rcx`, `rdx`, `rsi`, `rdi`, `rsp`, `rbp`, and `r8` through `r15`.

The same physical register can be accessed at different sizes:

| 64-bit | 32-bit | 16-bit | 8-bit low |
|--------|--------|--------|-----------|
| rax | eax | ax | al |
| rbx | ebx | bx | bl |
| rcx | ecx | cx | cl |
| rdx | edx | dx | dl |

Writing to a 32-bit register such as `eax` clears the upper 32 bits of the matching 64-bit register `rax`.

```asm
mov rax, 0xffffffffffffffff
mov eax, 0
mov al, 0x42
```

---

#### Activity 9.2a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: After these instructions execute, what is the value of `rax`?

```asm
mov rax, 0xffffffffffffffff
mov eax, 0
mov al, 0x42
```

**Options**:
- A) `0xffffffffffff0042`
- B) `0x0000000000000042`
- C) `0xffffffffffffffff`
- D) `0x00000000ffffffff`

**Answer**: **B** - `mov eax, 0` zeroes the lower 32 bits and clears the upper 32 bits of `rax`; `mov al, 0x42` then sets only the lowest byte.

**Explanation shown after answering**: On x86-64, writes to 32-bit subregisters zero-extend into the full 64-bit register. This pattern appears constantly in compiler output.

---

### 9.3 - Intel Syntax and Operand Direction

**Narrative**: The lessons use Intel syntax because it is common in tools such as Ghidra, IDA, Binary Ninja, and many `objdump` configurations.

In Intel syntax, the destination is usually on the left and the source is on the right.

```asm
mov rdi, rax
add rdi, 8
```

Read that as:

1. Copy `rax` into `rdi`.
2. Add `8` to `rdi`.

---

#### Activity 9.3a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Easy

**Prompt**: In `mov rdi, rax`, which register receives the copied value?

**Expected Answer**: `rdi`

**Acceptable variations**: `RDI`, `the rdi register`

**Hint**: In Intel syntax, the destination operand is on the left.

**Explanation**: `rdi` is the destination. The value currently in `rax` is copied into `rdi`.

---

### 9.4 - Common First Patterns

**Narrative**: A few instructions show up so often that recognizing them makes reversing much faster.

| Instruction | Typical meaning |
|-------------|-----------------|
| `mov dst, src` | Copy data |
| `lea dst, [addr]` | Compute an address without reading memory |
| `xor eax, eax` | Set `eax` to zero |
| `cmp a, b` | Compare by subtracting internally and setting flags |
| `test a, a` | Check whether a value is zero |
| `je target` | Jump if equal / zero |
| `jne target` | Jump if not equal / not zero |

```asm
xor eax, eax
cmp dil, 0x42
sete al
ret
```

---

#### Activity 9.4a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: Why do compilers often emit `xor eax, eax`?

**Options**:
- A) To encrypt the program
- B) To set `eax` to zero
- C) To call another function
- D) To push a value onto the stack

**Answer**: **B** - XORing a register with itself always produces zero.

**Explanation**: `xor reg, reg` is a compact and common zeroing idiom. When you see it before a comparison result is written into `al`, the compiler is often preparing a boolean return value.

---

## Module Summary

Assembly is not magic. It is a compact list of CPU operations. Start by tracking registers, operand direction, comparisons, and jumps. These are the building blocks for reversing real validation logic.
