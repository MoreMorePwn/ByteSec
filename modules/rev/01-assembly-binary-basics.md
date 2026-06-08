# Module 01: Assembly & Binary Basics

> ⭐ Beginner | ⏱️ 20 minutes | 5 activities

---

## Learning Objectives
By the end of this module, students will be able to:
- Understand how programs are represented as binary data
- Identify common CPU registers and their roles
- Recognize basic x86-64 assembly instructions
- Trace simple assembly logic through register state changes

---

## Lesson Flow

### 1.1 — From Source to Binary

**Narrative**: *Before you can reverse engineer a program, you need to understand what happens when source code becomes a binary. The compiler takes your C/C++ code and transforms it into machine code — raw bytes that the CPU fetches and executes. Assembly language is the human-readable version of those bytes.*

**Visual**: Imagine a pipeline: `Source Code (.c)` → `Compiler` → `Object File (.o)` → `Linker` → `Executable (.exe/.elf)`

**Key concepts:**
- **Machine code**: Raw bytes the CPU understands (e.g., `0x89 0xD8`)
- **Assembly**: Mnemonic representation of machine code (e.g., `mov eax, ebx`)
- **Disassembly**: Reversing binary → assembly (the reverse engineer's starting point)
- **Decompilation**: Binary → higher-level pseudo-C (less precise, but faster to read)

---

### 1.2 — CPU Registers

**Narrative**: *Registers are the CPU's super-fast scratchpad. Unlike RAM (which takes dozens of cycles to access), registers can be read or written in a single cycle. x86-64 has about 16 general-purpose registers plus several special-purpose ones.*

**Common x86-64 registers:**

| Register | Purpose | Call Convention |
|----------|---------|-----------------|
| `rax`/`eax` | Accumulator — return values | Holds return value |
| `rbx`/`ebx` | Base — general purpose | Callee-saved |
| `rcx`/`ecx` | Counter — loop iteration | 4th argument |
| `rdx`/`edx` | Data — I/O, arithmetic | 3rd argument |
| `rsi`/`esi` | Source index | 2nd argument |
| `rdi`/`edi` | Destination index | 1st argument |
| `rsp`/`esp` | Stack pointer — top of stack | — |
| `rbp`/`ebp` | Base pointer — stack frame | Callee-saved |
| `rip`/`eip` | Instruction pointer — next instruction | — |

| Flags | |
|--------|---|
| `ZF` | Zero Flag — set if result is zero |
| `CF` | Carry Flag — set if arithmetic overflow |
| `SF` | Sign Flag — set if result is negative |

---

#### 🧪 Activity 1.2a — PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Easy

**Prompt**: After executing `mov rax, 42` followed by `add rax, 8`, what value is in `rax`?

**Options**:
- A) 8
- B) 42
- C) 50 ✅
- D) 34

**Answer**: **C** — `mov rax, 42` sets rax to 42, then `add rax, 8` adds 8, giving 50.

**Explanation shown after answering**: *The `mov` instruction loads a value into a register. The `add` instruction performs integer addition and stores the result in the destination register (the first operand).*

---

#### 🧪 Activity 1.2b — MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: Which register typically holds the function's return value in x86-64?

**Options**:
- A) `rdi`
- B) `rsp`
- C) `rax` ✅
- D) `rbp`

**Answer**: **C** — `rax` (or `eax` for 32-bit values) is used for return values.

**Explanation shown after answering**: *By the System V AMD64 calling convention, the `rax` register holds the return value. The caller reads `rax` after the callee returns.*

---

### 1.3 — Basic Instructions

**Narrative**: *Assembly instructions follow a simple pattern: `OPCODE DEST, SRC`. The opcode is the operation, DEST is where the result goes, and SRC is the source value. Let's learn the most common ones.*

**Common Instructions:**

| Instruction | Meaning | Example |
|-------------|---------|---------|
| `mov` | Copy value | `mov rax, rbx` — copy rbx into rax |
| `add` | Add | `add rax, 5` — rax = rax + 5 |
| `sub` | Subtract | `sub rsp, 16` — rsp = rsp - 16 |
| `cmp` | Compare (sets flags) | `cmp rax, rbx` — compare rax with rbx |
| `jmp` | Unconditional jump | `jmp 0x401000` — jump to address |
| `je`/`jne` | Jump if equal/not equal | `je 0x401200` — jump if ZF=1 |
| `call` | Call a function | `call 0x401500` — push return addr, then jump |
| `ret` | Return from function | `ret` — pop return addr and jump |
| `push` | Push onto stack | `push rax` — decrement rsp, store rax |
| `pop` | Pop from stack | `pop rbx` — load value at rsp into rbx, increment rsp |

---

#### 🧪 Activity 1.3a — PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: Trace this code:
```asm
mov rax, 10
mov rbx, 3
sub rax, rbx
cmp rax, 5
```
After execution, what is the Zero Flag (`ZF`) value?

**Options**:
- A) ZF = 0 (not set, because rax ≠ 0)
- B) ZF = 1 (set, because rax = 5) ✅
- C) ZF is unpredictable
- D) ZF = 1 because the comparison failed

Wait — let me recalculate. `sub rax, rbx` → rax = 10 - 3 = 7. Then `cmp rax, 5` subtracts 5 from 7 (result = 2). ZF is set if result is zero. Since 2 ≠ 0, ZF = 0.

**Options**:
- A) ZF = 0 (correct — 7 - 5 = 2, not zero) ✅
- B) ZF = 1 (incorrect, result is not zero)
- C) ZF depends on previous operations
- D) ZF = 1 because the comparison failed

**Answer**: **A** — After `sub rax, rbx`, rax = 7. Then `cmp rax, 5` computes 7 - 5 = 2, which is non-zero, so ZF = 0.

**Explanation shown after answering**: *The `sub` instruction modifies rax to 7. Then `cmp` subtracts 5 from 7 internally (without storing the result — it only updates flags). Since 7 - 5 = 2 ≠ 0, ZF stays 0.*

---

### 1.4 — The Stack

**Narrative**: *The stack is a Last-In-First-Out (LIFO) data structure in memory. The `rsp` register points to the current top. When you `push`, rsp decreases and the value is stored at the new rsp. When you `pop`, the value at rsp is loaded and rsp increases.*

```
; Initially RSP = 0x7FFF
push rax       ; RSP = 0x7FF7, memory[0x7FF7] = rax
push rbx       ; RSP = 0x7FEF, memory[0x7FEF] = rbx
pop rcx        ; rcx = rbx, RSP = 0x7FF7
pop rdx        ; rdx = rax, RSP = 0x7FFF
```

The stack grows **downward** (toward lower addresses). This is important for understanding stack buffer overflows (a common Pwn vulnerability).

---

#### 🧪 Activity 1.4a — FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Medium

**Prompt**: After executing this sequence, complete the statement:

```asm
push 10
push 20
pop rax
pop rbx
```

After execution, `rax` = ____ and `rbx` = ____.

(Write both values separated by a comma, like: `10, 20`)

**Expected Answer**: `20, 10`

**Acceptable variations**: `20,10`, `20, 10`, `rax=20, rbx=10`

**Hint (shown after 1 failed attempt)**: *The stack is LIFO — the last value pushed (20) is the first one popped (into rax).*

**Explanation**: *First push stores 10 on the stack. Second push stores 20 on top. `pop rax` removes the top value (20) into rax. `pop rbx` removes the next value (10) into rbx. So rax=20, rbx=10 — the values swapped!*

---

#### 🧪 Activity 1.5a — SPOT THE BUG

> **Type**: SPOT
> **Difficulty**: Medium

**Prompt**: The following code should compute `result = a + b` and store it in `rax`, but there's a mistake. Which line number contains the error?

```asm
1: mov rax, 5     ; a = 5
2: mov rbx, 3     ; b = 3
3: add rbx, rax   ; this line is wrong
4: mov rax, rbx   ; store result
```

**Answer**: **3**

**Explanation shown after answering**: *Line 3 uses `add rbx, rax`, which computes rbx = rbx + rax, overwriting the original value of b. It should be `add rax, rbx` so that rax = rax + b. The result would then already be in rax without needing line 4.*

**Hint 1**: *Look at which register receives the result of the addition.*
