# Module 02: Static Analysis

> ⭐ Beginner | ⏱️ 25 minutes | 5 activities

---

## Learning Objectives
By the end of this module, students will be able to:
- Use the `strings` utility to extract readable text from binaries
- Read a basic disassembly listing
- Identify function prologues and calling conventions
- Recognize control flow patterns in disassembly

---

## Lesson Flow

### 2.1 — Strings: The Low-Hanging Fruit

**Narrative**: *One of the first things a reverse engineer does is run `strings` on a binary. It extracts sequences of printable characters — often revealing error messages, debug strings, flag formats, API calls, and hints about the program's logic.*

```bash
strings crackme.exe | head -20
```

**Common findings:**
- **"Correct!" / "Wrong!"** — victory/game-over strings (password checkers)
- **"flag{" or "BYTESEC{"** — actual flags accidentally compiled into binaries
- **File paths** — config files, dependencies, hidden assets
- **Function names** — `check_password`, `validate_key`, `decrypt_flag`
- **Base64 strings** — sometimes the flag is just encoded, not encrypted

---

#### 🧪 Activity 2.1a — PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Easy

**Prompt**: A CTF challenge binary prints "Access Denied" when you run it. You run `strings` and find `"ZmxhZyB7MzFhZjN9"` alongside "Access Denied". What is the most likely next step?

**Options**:
- A) The binary is broken, ignore it
- B) Decode the base64 string to check if it's a flag ✅
- C) Recompile the binary
- D) Delete the binary

**Answer**: **B** — Base64-encoded strings in binaries are often flags or passwords.

**Explanation shown after answering**: *Base64 is encoding, not encryption. Anyone can decode it. This is a common CTF trope — the flag is visible in `strings` output but encoded to avoid being obvious. Always decode any suspicious base64 you find!*

---

### 2.2 — Reading Disassembly

**Narrative**: *Disassembly converts machine code back into assembly mnemonics. Tools like `objdump`, `Ghidra`, `IDA Pro`, and `Binary Ninja` do this. A typical function in assembly looks like:*

```asm
0x401020  push rbp           ; Save old base pointer
0x401021  mov rbp, rsp       ; Set up stack frame
0x401024  sub rsp, 0x20      ; Allocate 32 bytes of local vars
         ; ... function body ...
0x401040  mov rsp, rbp       ; Restore stack
0x401043  pop rbp            ; Restore base pointer
0x401044  ret                ; Return
```

**This pattern (push rbp; mov rbp, rsp) is called the "function prologue".** Every standard function starts with it. The epilogue (mov rsp, rbp; pop rbp; ret) reverses it.

**Functions and arguments:**

| Calling Convention | 1st Arg | 2nd Arg | 3rd Arg | 4th Arg | Cleanup |
|-|-|-|-|-|-|
| **System V AMD64** (Linux) | `rdi` | `rsi` | `rdx` | `rcx` | Caller |
| **Microsoft x64** (Windows) | `rcx` | `rdx` | `r8` | `r9` | Caller |

---

#### 🧪 Activity 2.2a — MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: In the disassembly below, what is the purpose of `sub rsp, 0x30`?

```asm
push rbp
mov rbp, rsp
sub rsp, 0x30
```

**Options**:
- A) It pushes 0x30 onto the stack
- B) It allocates 48 bytes of space for local variables ✅
- C) It subtracts 0x30 from rbp
- D) It is a NOP instruction

**Answer**: **B** — `sub rsp, 0x30` allocates 48 bytes of stack space.

**Explanation shown after answering**: *The stack grows downward. `sub rsp, 0x30` moves the stack pointer down by 48 (0x30) bytes, creating space for local variables. This is a standard part of function prologue.*

---

### 2.3 — Control Flow in Assembly

**Narrative**: *Programs make decisions using comparisons (`cmp`) followed by conditional jumps. Understanding these patterns lets you trace program logic even without source code.*

**Common patterns:**

**if-else:**
```asm
cmp rax, 5         ; compare variable with 5
jne else_branch    ; if not equal, go to else
; ... if body ...
jmp end_if
else_branch:
; ... else body ...
end_if:
```

**loop:**
```asm
mov rcx, 0         ; counter = 0
loop_start:
cmp rcx, 10        ; counter < 10?
jge loop_end       ; if counter >= 10, exit
; ... loop body ...
inc rcx            ; counter++
jmp loop_start
loop_end:
```

**strcmp pattern (checking passwords):**
```asm
lea rdi, [user_input]    ; first arg = user input
lea rsi, [hardcoded_pw] ; second arg = stored password
call strcmp               ; compare
test eax, eax             ; check if result is 0
jne wrong_password        ; if not equal, jump to fail
; ... correct path ...
```

---

#### 🧪 Activity 2.3a — SPOT THE PATTERN

> **Type**: SPOT
> **Difficulty**: Medium

**Prompt**: Which line contains the conditional jump that decides if the password check passed?

```asm
1: lea rdi, [input_buf]
2: lea rsi, [secret_key]
3: call strcmp
4: test eax, eax
5: jne fail_label
6: mov rax, 1
7: jmp done_label
8: fail_label:
9: mov rax, 0
10: done_label:
11: ret
```

**Answer**: **5**

**Explanation shown after answering**: *Line 5 (`jne fail_label`) is the conditional jump that branches to the fail path if `strcmp` returned a non-zero value (strings differ). If they match, execution continues to line 6 (success path).*

---

#### 🧪 Activity 2.4a — MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: Looking at the strcmp pattern above, which register holds the return value of `strcmp`?

**Options**:
- A) `rdi`
- B) `rsi`
- C) `eax` ✅
- D) `rcx`

**Answer**: **C** — `eax` (the lower 32 bits of `rax`) holds the return value.

**Explanation shown after answering**: *By the System V AMD64 calling convention, `rax` (or `eax` for 32-bit values) always holds the return value of any function. After `call strcmp`, `eax` contains 0 if strings matched, non-zero if they differed.*

---

### 2.4 — Reading Function Signatures

**Narrative**: *Reverse engineers often rename functions based on how they're called. Once you understand calling conventions, you can infer a function's signature from its call site:*

```asm
mov rdi, [rbp-0x8]     ; Arg 1: pointer from local var
mov rsi, 100           ; Arg 2: immediate value 100
call some_function     ; Result in rax
```

**This tells us:** `some_function` takes a pointer and an integer, returns something in rax. Likely signature: `int some_function(void* buf, int size)`.

---

#### 🧪 Activity 2.5a — FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Medium

**Prompt**: Based on this call site, fill in the blank:

```asm
mov rdi, [rbp-0x10]    ; char* filename
mov rsi, 0             ; int flags = 0
mov rdx, 0x1A4         ; mode = 420 octal
call open
```

The function being called is `open(const char *filename, int flags, ____)`. What is the third parameter?

**Expected Answer**: `mode_t mode`

**Acceptable variations**: `mode`, `int mode`, `mode_t`

**Hint (shown after 1 failed attempt)**: *The third argument (rdx) is the permissions bitmask when creating a file. Look up the Linux `open()` syscall signature.*

**Explanation**: *The `open()` system call takes 3 arguments: pathname, flags, and mode. The mode argument specifies the file permissions (like 0644) and is only used when O_CREAT is specified in flags.*
