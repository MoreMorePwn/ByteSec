# Module 25: Evidence of Execution

> Beginner | 40 minutes | 5 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Explain what Prefetch, Amcache, SRUM, BAM/DAM, and process logs can show
- Identify useful artifact locations and timestamp caveats
- Choose follow-up pivots when one execution artifact appears
- Avoid overclaiming from a single execution trace

---

## Lesson Flow

### 25.1 - Prefetch

**Narrative**: Prefetch helps Windows improve application startup performance. For analysts, it can also provide evidence that an executable ran. Prefetch records are usually located under `%SystemRoot%\Prefetch` and use names that combine the executable name and a path-derived hash.

Analysis value:

- Evidence of execution
- Full executable path after parsing
- Last execution information
- Referenced files and modules touched shortly after process start

Caveats:

- Server systems may not enable Prefetch by default.
- Prefetch entries can rotate out.
- Files are written after execution, so filesystem timestamps may lag the actual launch.
- Different paths or command lines can create different Prefetch records for the same executable name.

---

#### Activity 25.1a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: What question does Prefetch commonly help answer?

**Options**:
- A) Did this executable likely run on the system?
- B) What is the user's password?
- C) Which browser tab is currently active?
- D) Which antivirus vendor is best?

**Answer**: **A** - Prefetch is a common evidence-of-execution artifact.

**Explanation**: Prefetch should be corroborated, but it is often a strong first execution lead.

---

### 25.2 - Amcache

**Narrative**: The Amcache hive stores metadata about installed applications, drivers, shortcuts, and executable files. It can contain file paths, names, publishers, sizes, and hashes. It is useful for identifying executables that existed on a host and often executables that ran or were associated with installed software.

Typical location:

```text
%SystemRoot%\AppCompat\Programs\Amcache.hve
```

Useful keys vary by Windows version. Analysts should first identify the Windows build, then parse the hive with tooling that understands that format.

---

#### Activity 25.2a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Easy

**Prompt**: The compatibility hive commonly used for executable metadata is named ______.hve.

**Expected Answer**: `amcache`

**Acceptable variations**: `Amcache`, `Amcache.hve`, `amcache.hve`

**Hint**: It lives below the AppCompat Programs directory.

**Explanation**: Amcache.hve is a registry hive frequently used during execution analysis.

---

### 25.3 - SRUM

**Narrative**: System Resource Usage Monitor records application resource usage and network-related telemetry. It can show application identifiers, user SIDs, bytes sent and received, CPU time, and disk I/O style metrics depending on provider tables.

Typical locations:

```text
%SystemRoot%\System32\sru\SRUDB.dat
SOFTWARE\Microsoft\Windows NT\CurrentVersion\SRUM\Extensions
```

SRUM is useful when a case needs rough application activity over a period of days or weeks. Network usage records are bucketed, so they should be interpreted as timeline estimates rather than exact connection start and stop times.

---

#### Activity 25.3a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: Why is SRUM useful during possible exfiltration triage?

**Options**:
- A) It can track per-application network usage and user SID context
- B) It stores every packet payload in clear text
- C) It stores passwords for all local accounts
- D) It replaces the need for network logs

**Answer**: **A** - SRUM can help estimate which application transferred data and under which user context.

**Explanation**: SRUM is a pivot, not a full packet capture.

---

### 25.4 - BAM, DAM, and Process Events

**Narrative**: Background Activity Moderator and Desktop Activity Moderator artifacts can provide execution-related traces, especially for user activity on modern Windows systems. Process creation Event ID 4688 can directly show new process creation when auditing is enabled. PowerShell script block logging Event ID 4104 can expose executed script content when configured.

No artifact is guaranteed to exist. Logging policy, OS version, cleanup, and collection timing all matter.

---

#### Activity 25.4a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: A host has process creation auditing enabled. Which event is commonly reviewed for new process creation?

**Options**:
- A) Event ID 4688
- B) Event ID 4624
- C) Event ID 1149
- D) Event ID 7045

**Answer**: **A** - Event ID 4688 is commonly associated with new process creation.

**Explanation shown after answering**: Event IDs become stronger when linked to account context and command-line fields.

---

### 25.5 - Corroboration Pattern

**Narrative**: If `tool.exe` appears in one artifact, look for:

- Prefetch entry for execution timing
- Amcache metadata for path and hash
- SRUM usage records for user SID and resource activity
- Process creation events for command line
- PowerShell events if script-driven
- File timestamps for creation and modification
- Persistence artifacts if repeated execution is likely

---

#### Activity 25.5a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: Why should execution evidence be corroborated?

**Options**:
- A) Each artifact has different collection rules and timestamp caveats
- B) Corroboration makes evidence weaker
- C) Windows never records execution
- D) Only one artifact can exist per executable

**Answer**: **A** - Corroboration reduces the chance of overclaiming from one imperfect trace.

**Explanation**: Strong timelines explain what each artifact means and where it may be incomplete.

