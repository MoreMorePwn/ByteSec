# Module 03: Dynamic Analysis & Debugging

> ⭐ Intermediate | ⏱️ 25 minutes | 4 activities

---

## Learning Objectives
By the end of this module, students will be able to:
- Understand how debuggers work (breakpoints, stepping, memory inspection)
- Use GDB basics to trace program execution
- Identify anti-debugging techniques at a conceptual level
- Apply simple patches (NOPing) to bypass checks

---

## Lesson Flow

### 3.1 — What is Dynamic Analysis?

**Narrative**: *Static analysis is like reading a book's plot summary. Dynamic analysis is like watching the movie — you see exactly what happens when the program runs. Debuggers let you pause execution, inspect memory, and step through code one instruction at a time.*

**Key debugging operations:**

| Operation | What it does |
|-----------|-------------|
| **Breakpoint** | Pause execution at a specific address or function |
| **Step Into** | Execute one instruction, stepping into `call` targets |
| **Step Over** | Execute one instruction, skipping over `call` targets |
| **Continue** | Resume execution until next breakpoint |
| **Inspect** | Read register values and memory contents |
| **Modify** | Change register/memory values during execution |

**Example GDB session:**
```bash
gdb ./crackme
(gdb) break main           # Set breakpoint at main
(gdb) run                  # Run until main
(gdb) info registers       # See all register values
(gdb) x/8gx $rsp           # Examine 8 qwords on stack
(gdb) continue             # Resume execution
```

---

#### 🧪 Activity 3.1a — PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Easy

**Prompt**: You set a breakpoint at address `0x401050` in GDB, then continue execution. The program hits the breakpoint. You type `info registers` and see `rax = 0`. You then type `continue`. What happens?

**Options**:
- A) The debugger exits
- B) The program runs to completion or until the next breakpoint ✅
- C) The program restarts from the beginning
- D) Nothing happens

**Answer**: **B** — `continue` resumes execution until the program ends or hits another breakpoint.

**Explanation shown after answering**: *The `continue` command in GDB resumes normal execution. The program will run until it finishes (exits) or encounters another breakpoint. The fact that we already hit a breakpoint doesn't matter — continue just unpauses.*

---

### 3.2 — Tracing a Simple CrackMe

**Narrative**: *Let's trace a hypothetical crackme that checks a password. Without source code, we can use GDB to observe the comparison in real time.*

```asm
; Assume: user input is in a buffer at [rbp-0x20]
0x401150  lea rdi, [rbp-0x20]     ; our input
0x401154  lea rsi, [0x402010]     ; some address
0x40115b  call strcmp
0x401160  test eax, eax
0x401162  jne 0x401200             ; jump if wrong
0x401168  mov rax, 1               ; success!
0x40116f  ret
; ...
0x401200  xor rax, rax             ; failure (return 0)
0x401203  ret
```

**Debugging approach:**
1. Set breakpoint at `0x40115b` (before `strcmp`)
2. Run the program with a test input like "AAAA"
3. Inspect `rsi` — the comparison string at `0x402010`:
   ```bash
   (gdb) x/s 0x402010
   ```
4. This reveals the expected password directly from memory!

---

#### 🧪 Activity 3.2a — MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: At breakpoint `0x401160` (after `strcmp`), you inspect `eax` and see `eax = 1`. Then execution is at `0x401162` which is `jne 0x401200`. Where will execution go next?

**Options**:
- A) It jumps to `0x401200` (failure path) ✅
- B) It continues to `0x401168` (success path)
- C) It returns from the function
- D) It restarts the program

**Answer**: **A** — `jne` jumps if the zero flag is NOT set. Since `eax = 1` (strcmp result, not zero), ZF = 0, so `jne` takes the jump to `0x401200` (failure).

**Explanation shown after answering**: *After `strcmp`, `eax = 0` means strings match (ZF = 1, `jne` won't jump). `eax ≠ 0` means strings differ (ZF = 0, `jne` WILL jump). Here eax = 1, so they differ, and we jump to the failure path at 0x401200.*

---

### 3.3 — Patching: Changing Program Behavior

**Narrative**: *Sometimes you don't need to understand the whole algorithm — you just need to change one byte. If a `jne` (conditional jump) controls access, replacing it with `jmp` (unconditional jump) or `nop` (no operation) can bypass the check entirely.*

**Common patches:**

| Original | Patch | Effect |
|----------|-------|--------|
| `jne 0x401200` (`75 9E`) | `nop; nop` (`90 90`) | Always fall through to success |
| `jne 0x401200` (`75 9E`) | `je 0x401200` (`74 9E`) | Invert the condition |
| `je 0x401200` (`74 9E`) | `jmp 0x401200` (`EB 9E`) | Always jump (force fail) |
| `call check_pw` | `mov eax, 1; nop; nop` | Skip check, force success |

**Warning**: Patching a binary is aggressive — you're modifying the file on disk. Always work on a copy!

---

#### 🧪 Activity 3.3a — FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Medium

**Prompt**: At address `0x401162`, the instruction is `jne 0x401200` with bytes `75 9E`. To bypass the check (always succeed regardless of password), you want to replace the conditional jump with NOP instructions so execution always falls through to the next instruction at `0x401168`.

The `jne` is 2 bytes long. How many bytes of NOP (`0x90`) do you write? Enter just the number.

**Expected Answer**: `2`

**Acceptable variations**: `2`, `two`

**Hint (shown after 1 failed attempt)**: *The original instruction `75 9E` is 2 bytes. NOP replaces bytes — you need to replace all of them.*

**Explanation**: *Since `jne` is a 2-byte instruction (`75 9E`), overwriting both bytes with `90 90` changes it to two NOPs. Execution will then "fall through" to `0x401168` and take the success path regardless of the comparison result.*

---

### 3.4 — Anti-Debugging Techniques (Conceptual)

**Narrative**: *Crackmes and real-world malware often detect debuggers and change behavior. These are anti-debugging techniques — you should be aware they exist even if you can't always easily bypass them.*

**Common techniques:**

| Technique | How it works | Simple bypass |
|-----------|-------------|---------------|
| `ptrace` check | Calls `ptrace(0, 0, 0, 0)` — fails if already traced | Patch the `call` or change the return value |
| `TCC` / `Trap Flag` | Checks `(flags & 0x100)` on the stack | Modify the check jump |
| Timing checks | Measures execution time of a critical section | NOP the timing calls |
| `IsDebuggerPresent` (Windows) | Checks PEB flag | Patch `mov al, [peb+2]` to `xor al, al` |
| Software breakpoint scan | Scans code for `0xCC` (INT3) bytes | Use hardware breakpoints instead |

**Rule of thumb**: Anti-debug can be bypassed, but it requires patience. Start by identifying WHERE the check happens (find the "wrong" message or unusual syscalls), then patch or override it.

---

#### 🧪 Activity 3.4a — MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: A crackme calls `ptrace(PTRACE_TRACEME, 0, 0, 0)` at the start. If the call fails (returns -1), it exits. The binary is already running in GDB. What is the simplest bypass?

**Options**:
- A) Restart the binary outside GDB
- B) Set a breakpoint after the ptrace call and manually set `rax = 0` ✅
- C) Remove GDB and use a different debugger
- D) Recompile the binary

**Answer**: **B** — Set a breakpoint after `ptrace`, check `rax`, and modify it to 0 to indicate success.

**Explanation shown after answering**: *`ptrace` returns 0 on success and -1 on failure. When running inside GDB, `ptrace(PTRACE_TRACEME)` fails (returns -1 in rax). By setting a breakpoint right after the call and using `set $rax = 0` in GDB, you bypass the check. This technique works for many anti-debugging tricks — find the return value and override it.*
