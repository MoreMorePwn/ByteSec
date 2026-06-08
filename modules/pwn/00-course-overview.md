# Pwn: Stack Exploitation

> A guided ByteSec learning path for stack-based binary exploitation, from process memory to a containerized ret2win challenge.

---

## Course Philosophy

Pwn is about turning a memory bug into controlled program behavior. This course keeps the first step narrow: understand where data lives, why oversized input can reach saved control-flow data, and how a ret2win challenge redirects execution to an existing function.

The course focuses on beginner-friendly Linux x86-64 targets. Each module introduces one exploit idea, then checks it with small activities before the final Docker lab.

---

## Course Structure

| Module | Title | Duration | Difficulty |
|--------|-------|----------|------------|
| 19 | Pwn Foundations: Memory, Registers, and the Stack | 25 min | Beginner |
| 20 | Stack Overflows and Control Data | 25 min | Beginner |
| 21 | Building a Ret2win Exploit | 25 min | Intermediate |
| 22 | Mitigations and Exploit Workflow | 25 min | Intermediate |
| 23 | CTF Challenge Lab: Ret2win | 25 min | Beginner |

---

## Interactive Element Types Used

### Multiple Choice
Used to identify memory regions, protection behavior, and exploit decisions.

### Predict the Output
Used to trace stack changes, byte order, and payload layout.

### Fill in the Blank
Used for exact vocabulary such as RIP, PIE, canary, and little-endian.

### Spot the Bug
Used for selecting the vulnerable input line or the relevant control-flow instruction.

### Flag Submission
Used for the final ret2win Docker lab.

---

## Progression Design

```text
Module 19: FOUNDATION
  "I can explain registers, virtual memory, stack frames, and return addresses."
       |
       v
Module 20: OVERFLOW MECHANICS
  "I can identify an unsafe input path and reason about what gets overwritten."
       |
       v
Module 21: RET2WIN
  "I can build a payload that replaces the saved return address with a target function."
       |
       v
Module 22-23: WORKFLOW AND LAB
  "I can account for common mitigations and solve a contained ret2win challenge."
```

---

## Target Audience

- CTF beginners starting binary exploitation
- Students who know basic C and want to understand memory corruption
- Reverse engineering students who want to move from reading binaries to controlling them

## Prerequisites

- Basic C syntax
- Comfortable running Linux command-line tools
- Basic x86-64 register vocabulary helps, but the course reviews the essentials
