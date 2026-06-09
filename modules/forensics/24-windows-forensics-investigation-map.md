# Module 24: Windows Forensics Investigation Map

> Beginner | 30 minutes | 4 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Classify Windows artifacts by investigation question
- Use shared fields such as SID, username, file path, timestamp, and Logon ID as pivot points
- Separate artifact presence from artifact interpretation
- Plan a small Windows endpoint triage workflow

---

## Lesson Flow

### 24.1 - Start With The Question

**Narrative**: Windows forensics works best when the analyst starts from a concrete question. The operating system leaves many traces, but those traces have different meanings and different caveats.

Common questions:

| Question | Useful artifact families |
|----------|--------------------------|
| What executed? | Prefetch, Amcache, SRUM, BAM/DAM, process creation logs, PowerShell logs |
| Who was active? | Security logons, SIDs, profile hives, Logon IDs, RDP logs |
| How did it persist? | Services, scheduled tasks, Run keys, IFEO debugger keys |
| What touched the network? | SRUM, firewall events, tracing keys, RDP events |
| What files changed? | Recycle Bin records, shell items, jump lists, file timestamps |

The analyst's job is to connect weak signals into a coherent timeline. One artifact can suggest an answer. Two independent artifacts can support it. Three artifacts with matching timestamps, paths, and account context can become a defensible finding.

---

#### Activity 24.1a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: Why should an analyst start with an investigation question instead of opening artifacts randomly?

**Options**:
- A) The question tells the analyst which artifact families are likely to answer it
- B) Random artifact review is always faster
- C) Windows artifacts all contain the same fields
- D) Timelines are unnecessary if one artifact exists

**Answer**: **A** - A clear question narrows the first pivots and prevents noisy evidence collection.

**Explanation**: Windows has many artifacts. The question decides which traces matter first.

---

### 24.2 - Shared Pivot Fields

**Narrative**: Artifacts become more powerful when they share fields. A username from a logon event can connect to a SID. A SID can connect to SRUM records, Recycle Bin folders, profile paths, and process events. A file path can connect execution artifacts to file timestamps and persistence keys.

Useful pivot fields:

- Username
- Security Identifier
- Logon ID
- Computer name
- Executable path
- File hash
- Service name
- Task name
- IP address
- Timestamp

Treat each pivot as a hypothesis. If a suspicious executable appears in Amcache, look for Prefetch, SRUM, process creation logs, scheduled tasks, services, and file timestamps around the same period.

---

#### Activity 24.2a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Easy

**Prompt**: A Windows account's stable identity value is often abbreviated as ______.

**Expected Answer**: `sid`

**Acceptable variations**: `SID`, `security identifier`, `Security Identifier`

**Hint**: It is used to tie account activity to profile and registry artifacts.

**Explanation**: A SID is more stable than a display name and appears across many Windows artifacts.

---

### 24.3 - Artifact Meaning vs Artifact Presence

**Narrative**: Finding an artifact is not the same as interpreting it correctly. A Prefetch file can indicate execution, but not always the exact first execution. Amcache can record installed software and executables, but update timing depends on compatibility appraiser activity. SRUM can show application resource and network usage, but its records are bucketed and may need database repair after improper shutdown.

The pattern is:

1. Identify what the artifact can prove.
2. Identify what it cannot prove.
3. Record timestamp semantics.
4. Corroborate with a second artifact.

---

#### Activity 24.3a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: What is the safest interpretation habit when one artifact suggests suspicious execution?

**Options**:
- A) Treat the artifact as a lead and corroborate it with independent evidence
- B) Immediately declare compromise without checking timestamp semantics
- C) Ignore it because Windows artifacts are noisy
- D) Delete the file before preserving evidence

**Answer**: **A** - One artifact should guide the next pivot, not replace the whole investigation.

**Explanation**: Strong findings usually combine several traces that agree on path, time, account, and action.

---

### 24.4 - Mini Triage Plan

**Narrative**: A small triage plan keeps an investigation consistent:

1. Define the suspected time window.
2. Identify relevant accounts and hosts.
3. Pull execution artifacts for suspicious paths.
4. Pull account artifacts for logon context.
5. Pull persistence locations for repeat execution.
6. Pull network and file activity artifacts for impact.
7. Normalize timestamps.
8. Build a timeline with confidence notes.

---

#### Activity 24.4a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Easy

**Prompt**: An analyst has a suspicious executable path and wants to know whether it was likely run. Which category should be checked first?

**Options**:
- A) Evidence of execution
- B) Wallpaper settings
- C) Keyboard layout
- D) Screen brightness

**Answer**: **A** - Execution artifacts are designed to answer whether a program ran or was prepared to run.

**Explanation shown after answering**: Start from the question, then choose the artifact family that can answer it.

