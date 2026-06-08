# Reverse Engineering Assembly: From Registers to Flag Checkers

> A guided ByteSec learning path for reading x86-64 assembly, recognizing compiler patterns, and reversing small validation binaries.

---

## Course Philosophy

Reverse engineering rewards careful observation. This path keeps each concept small: read a short assembly pattern, predict what it does, then apply that reasoning to a checker-style challenge.

The lessons adapt a practical x86-64 progression: registers, the stack, calls, control flow, boolean logic, Linux assembly examples, and a small binary-bomb-style final lab.

---

## Course Structure

| Module | Title | Duration | Difficulty |
|--------|-------|----------|------------|
| 09 | Assembly Foundations for Reverse Engineering | 20 min | Beginner |
| 10 | Stack Frames, Calls, and Parameters | 25 min | Intermediate |
| 11 | Control Flow, Memory, and Encoded Data | 25 min | Intermediate |
| 12 | Reversing a Flag Checker Workflow | 20 min | Intermediate |
| 13 | CTF Challenge Lab: XOR Flag Checker | 20 min | Beginner |

---

## Interactive Element Types Used

### Multiple Choice
Used for identifying what an instruction pattern means.

### Predict the Output
Used for tracing register values and branch outcomes before seeing the explanation.

### Fill in the Blank
Used for precise vocabulary and operand reasoning.

### Spot the Logic
Used for selecting the exact line where validation, branching, or decoding happens.

### Flag Submission
Used for the final XOR checker download challenge.

---

## Progression Design

```text
Module 09: FOUNDATION
  "I can read registers, operands, and simple instructions."
       |
       v
Module 10: FUNCTIONS
  "I can identify stack use, calls, returns, and arguments."
       |
       v
Module 11: CONTROL AND DATA
  "I can trace branches, loops, memory references, and XOR logic."
       |
       v
Module 12-13: REVERSING WORKFLOW
  "I can inspect a small binary and recover a hidden flag."
```

---

## Target Audience

- Students who have used C or Python but are new to binaries
- CTF beginners preparing for reverse engineering categories
- Web/security students who want to understand compiled challenge logic

## Prerequisites

- Basic command-line comfort
- Basic programming concepts: variables, if statements, loops, and functions
- No prior assembly experience required
