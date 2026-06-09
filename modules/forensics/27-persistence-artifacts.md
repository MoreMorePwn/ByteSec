# Module 27: Persistence Artifacts

> Intermediate | 35 minutes | 4 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Identify common Windows persistence artifact families
- Interpret service install and scheduled task evidence
- Explain Image File Execution Options debugger persistence
- Build a persistence review checklist

---

## Lesson Flow

### 27.1 - Services

**Narrative**: Windows services are a common persistence and lateral movement mechanism. Event ID 7045 can record service installation in the System channel. Service configuration can also be found in the SYSTEM registry hive.

Useful fields:

- Service name
- Display name
- Image path
- Start type
- Account name
- Install timestamp
- Computer name

Remote service creation often appears near a network logon. Check for Type 3 logons, service install events, process creation, and file creation around the same time.

---

#### Activity 27.1a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: Which field is especially important when reviewing a suspicious service install?

**Options**:
- A) Image path
- B) Screen resolution
- C) Mouse cursor size
- D) Desktop background color

**Answer**: **A** - The image path shows what executable the service will run.

**Explanation**: The executable path can pivot into file, execution, and hash analysis.

---

### 27.2 - Scheduled Tasks

**Narrative**: Scheduled tasks can run commands at logon, on a timer, or when a trigger fires. Task Scheduler operational logs and task files can reveal creation, update, execution, and deletion. Task deletion can be high-signal because attackers often remove tasks after use.

Review:

- Task name
- Author field
- Action command
- Trigger
- Last run time
- Creation or registration events
- Deletion events

---

#### Activity 27.2a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Easy

**Prompt**: A Windows persistence mechanism that runs commands on a trigger is a scheduled ______.

**Expected Answer**: `task`

**Acceptable variations**: `Task`, `scheduled task`

**Hint**: It is managed by Task Scheduler.

**Explanation**: Scheduled tasks are common in legitimate administration and attacker persistence.

---

### 27.3 - Run Keys

**Narrative**: Run and RunOnce registry keys launch programs during user logon or system startup depending on hive and location. They are easy to inspect and easy to abuse.

Common review points:

- HKCU Run keys for user-level persistence
- HKLM Run keys for machine-wide persistence
- Value name and command path
- Referenced executable existence
- File creation time near account activity
- Related execution artifacts

---

#### Activity 27.3a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: Which registry area is commonly reviewed for logon persistence?

**Options**:
- A) `Software\Microsoft\Windows\CurrentVersion\Run`
- B) `%SystemRoot%\Prefetch`
- C) `C:\Windows\Temp`
- D) `HKLM\SAM\Domains\Account`

**Answer**: **A** - Run keys are classic logon persistence locations.

**Explanation**: Registry persistence findings should be paired with execution and file evidence.

---

### 27.4 - IFEO Debugger Keys

**Narrative**: Image File Execution Options can attach a debugger command to a target executable. Attackers can abuse this by configuring a debugger value that launches their payload when the target program starts.

Common registry areas:

```text
SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\
SOFTWARE\WOW6432Node\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\
```

Review executable-named subkeys and look for unexpected `Debugger` values.

---

#### Activity 27.4a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: A suspicious IFEO subkey for `sethc.exe` contains a `Debugger` value pointing to `cmd.exe`. What is the likely concern?

**Options**:
- A) A debugger-based persistence or privilege abuse trick
- B) Normal wallpaper loading
- C) Browser cache cleanup
- D) Password policy export

**Answer**: **A** - IFEO debugger values can redirect execution to another program.

**Explanation shown after answering**: Always verify who created the key and whether the referenced binary executed.

