# Module 19: Pwn Foundations: Memory, Registers, and the Stack

> Beginner | 25 minutes | 5 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Explain why compiled C programs depend on registers, machine code, and virtual memory
- Identify the role of the stack in ordinary function execution
- Describe what the saved return address does
- Connect stack variables, saved frame pointers, and return addresses to exploitation risk

---

## Lesson Flow

### 19.1 - What Pwn Studies

**Narrative**: Pwn focuses on program behavior after compilation. Source code is useful, but the exploit target is the running process: machine instructions, registers, memory permissions, function calls, and data movement.

A simple C program can hide useful code that is never called:

```c
void win(void) {
    puts("secret");
}

int main(void) {
    char name[32];
    gets(name);
    printf("Hello, %s\n", name);
}
```

The `win` function exists in the binary. The normal control flow just never reaches it. A ret2win challenge asks whether input can corrupt the saved return address so execution returns to `win`.

---

#### Activity 19.1a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: In a ret2win challenge, what is the exploit trying to control?

**Options**:
- A) The saved return address used by `ret`
- B) The file name of the source program
- C) The order of environment variables
- D) The color of terminal output

**Answer**: **A** - The payload aims to replace the saved return address with the address of a useful function such as `win`.

**Explanation**: `ret` reads the next instruction pointer from the stack. If an overflow reaches that value, the attacker can choose where execution resumes.

**Hint**: Focus on what happens after a vulnerable function finishes.

---

### 19.2 - Registers and Instruction State

**Narrative**: Registers are small storage locations inside the CPU. Exploitation often cares about a few of them:

| Register | Common role in beginner pwn |
|----------|------------------------------|
| `rip` | Address of the next instruction |
| `rsp` | Top of the stack |
| `rbp` | Frame pointer for the current stack frame |
| `rdi` | First function argument on Linux x86-64 |
| `rax` | Return value and scratch register |

The important idea is not memorizing every register. It is knowing which values decide where the program goes next and where arguments are placed.

---

#### Activity 19.2a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Easy

**Prompt**: The x86-64 register that holds the address of the next instruction is `____`.

**Expected Answer**: `rip`

**Acceptable Variations**: `RIP`

**Explanation**: `rip` is the instruction pointer. Ret2win succeeds when `rip` is changed to the address of the target function.

**Hint**: The register name ends with `ip`.

---

### 19.3 - Virtual Memory Regions

**Narrative**: A running process sees virtual memory, not raw physical RAM. Different regions serve different purposes:

| Region | Typical contents |
|--------|------------------|
| Text | Program instructions |
| PLT/GOT | Dynamic linking helpers and resolved function pointers |
| Data/BSS | Global and static variables |
| Heap | Dynamically allocated data |
| Stack | Function frames, stack variables, saved frame pointers, return addresses |
| Shared libraries | libc and other mapped libraries |

Most beginner stack exploitation starts with data written into a stack buffer. The problem appears when that write exceeds the buffer and reaches adjacent control data.

---

#### Activity 19.3a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: Which memory region commonly stores stack variables, saved frame pointers, and saved return addresses?

**Options**:
- A) Stack
- B) Text
- C) BSS
- D) GOT

**Answer**: **A** - Stack frames hold per-call data and the return address needed when a function returns.

**Explanation**: Overflowing a stack buffer is dangerous because important control-flow metadata can sit nearby.

**Hint**: Think about the region that grows and shrinks as functions are called and return.

---

### 19.4 - Function Calls and Return Addresses

**Narrative**: A `call` instruction transfers execution to a function and stores where to come back afterward. A `ret` instruction later pops that saved address and puts it into `rip`.

Simplified stack frame:

```text
higher addresses
+----------------------+
| saved return address |
+----------------------+
| saved rbp            |
+----------------------+
| char name[32]        |
+----------------------+
lower addresses
```

If an unsafe input writes past `name[32]`, it can overwrite saved `rbp` and then the saved return address.

---

#### Activity 19.4a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: A function has `char name[32]`, then saved `rbp`, then the saved return address. How many bytes normally reach the saved return address on x86-64?

**Options**:
- A) 8 bytes
- B) 32 bytes
- C) 40 bytes
- D) 64 bytes

**Answer**: **C** - 32 bytes fill the buffer and 8 more bytes overwrite saved `rbp`, so the next 8 bytes become the saved return address.

**Explanation**: x86-64 saved frame pointers are 8 bytes. A common ret2win starter offset is therefore 32 + 8 = 40 bytes.

**Hint**: Add the buffer size and the saved frame pointer size.

---

### 19.5 - Unsafe Input as the Trigger

**Narrative**: A memory layout is not a vulnerability by itself. The vulnerability appears when the program copies too much input into a fixed-size buffer.

Dangerous pattern:

```c
void greet(void) {
    char name[32];
    gets(name);
    printf("Hello, %s\n", name);
}
```

`gets` has no length argument. It keeps reading until newline or EOF, so the program cannot enforce the 32-byte buffer boundary.

---

#### Activity 19.5a - SPOT THE BUG

> **Type**: SPOT
> **Difficulty**: Easy

**Prompt**: Which line introduces the stack overflow risk?

```c
1 void greet(void) {
2     char name[32];
3     puts("Name:");
4     gets(name);
5     printf("Hello, %s\n", name);
6 }
```

**Answer**: Line 4 - `gets(name)` reads without knowing the size of `name`.

**Explanation**: The buffer has a fixed size, but `gets` does not enforce that size. An oversized input can continue into saved stack data.

**Hint**: Look for the input function with no length parameter.
