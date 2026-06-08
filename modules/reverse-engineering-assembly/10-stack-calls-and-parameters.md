# Module 10: Stack Frames, Calls, and Parameters

> Intermediate | 25 minutes | 4 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Explain the stack as a last-in, first-out memory region
- Recognize call and return behavior
- Identify common x86-64 Linux function argument registers
- Translate simple compare-and-branch assembly into source-like logic

---

## Lesson Flow

### 10.1 - The Stack in One Picture

**Narrative**: The stack is a memory region used for return addresses, saved registers, local variables, and temporary data. It is commonly described as last-in, first-out: the most recently pushed value is the first one popped.

On common x86-64 systems, the stack grows toward lower addresses. `rsp` points near the current top of the stack.

```text
High addresses
    |
    | old stack data
    | saved return address
rsp -> local or temporary data
    |
Low addresses
```

---

#### Activity 10.1a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: Which register normally points at the top of the current stack on x86-64?

**Options**:
- A) `rip`
- B) `rsp`
- C) `rax`
- D) `rdi`

**Answer**: **B** - `rsp` is the stack pointer.

**Explanation**: `rip` points at the next instruction. `rsp` tracks the top of the stack, and many function prologues adjust it to reserve local storage.

---

### 10.2 - Call and Return

**Narrative**: A `call` transfers execution to another function and saves the return address on the stack. A later `ret` pops that return address and continues after the call site.

```asm
main:
    call check_flag
    test eax, eax
    je fail
    call print_success
```

The return value from many C functions is placed in `eax` or `rax`.

---

#### Activity 10.2a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: In the snippet below, which value is tested immediately after `check_flag` returns?

```asm
call check_flag
test eax, eax
je fail
```

**Options**:
- A) The first command-line argument
- B) The return value in `eax`
- C) The stack pointer
- D) The next instruction pointer before the call

**Answer**: **B** - The function return value is in `eax`, and `test eax, eax` checks whether it is zero.

**Explanation shown after answering**: A common C pattern is `if (!check_flag(input)) fail();`. In assembly, that often becomes a call, a test of `eax`, and a conditional jump.

---

### 10.3 - Function Parameters on Linux x86-64

**Narrative**: Calling conventions define where function arguments go. On the common System V x86-64 ABI used by Linux, the first six integer or pointer arguments are passed in:

| Argument | Register |
|----------|----------|
| 1 | rdi |
| 2 | rsi |
| 3 | rdx |
| 4 | rcx |
| 5 | r8 |
| 6 | r9 |

If a checker calls `strcmp(input, "test")`, expect the input pointer and string pointer to be placed in the first two argument registers before the call.

```asm
mov rdi, rbx
lea rsi, [rip + expected_text]
call strcmp
```

---

#### Activity 10.3a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Easy

**Prompt**: On Linux x86-64, the first pointer argument to a function is usually passed in ______.

**Expected Answer**: `rdi`

**Acceptable variations**: `RDI`, `the rdi register`

**Hint**: The first two System V argument registers are `rdi` and `rsi`.

**Explanation**: `rdi` carries the first integer or pointer argument. This is why input pointers often show up in `rdi` at the start of checker functions.

---

### 10.4 - Reconstructing a Branch

**Narrative**: Reverse engineers constantly translate branch patterns into source-like conditions.

```asm
check_number:
    cmp edi, 5
    jne fail
    mov eax, 1
    ret
fail:
    xor eax, eax
    ret
```

This function returns `1` only when the first argument equals `5`.

---

#### Activity 10.4a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: What input makes `check_number` return `1`?

```asm
check_number:
    cmp edi, 5
    jne fail
    mov eax, 1
    ret
fail:
    xor eax, eax
    ret
```

**Options**:
- A) Any nonzero number
- B) Exactly `5`
- C) Any number less than `5`
- D) No input can return `1`

**Answer**: **B** - `jne fail` is taken when `edi` is not equal to `5`. The success path is only reached when `edi == 5`.

**Explanation shown after answering**: The comparison does not store a visible value. It sets flags, and `jne` decides whether to jump based on those flags.

---

## Module Summary

Function-level reversing is mostly disciplined bookkeeping: arguments enter through known registers, calls return through `rax` or `eax`, and conditional jumps reveal source-level decisions.
