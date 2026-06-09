# Module 30: Timeline and Triage Playbook

> Intermediate | 40 minutes | 5 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Build a concise Windows forensic timeline from multiple artifact families
- Mark confidence and caveats for each timeline entry
- Prioritize pivots during a time-limited triage
- Produce a finding that separates fact, inference, and open questions

---

## Lesson Flow

### 30.1 - Timeline Structure

**Narrative**: A useful timeline is not a dump of every timestamp. It is a structured explanation of what happened and why the analyst believes it happened.

Recommended fields:

| Field | Purpose |
|-------|---------|
| Time | Normalized timestamp |
| Artifact | Evidence source |
| Host | Endpoint name |
| Account | Username or SID |
| Path | File, process, service, or URL |
| Action | What the artifact suggests |
| Confidence | High, medium, or low |
| Caveat | What the artifact cannot prove |

---

#### Activity 30.1a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: What makes a forensic timeline defensible?

**Options**:
- A) It records artifact source, interpretation, confidence, and caveats
- B) It contains only one timestamp
- C) It ignores time zones
- D) It removes all uncertainty

**Answer**: **A** - A good timeline shows both evidence and limits.

**Explanation**: Investigation reports should separate observed facts from analyst inference.

---

### 30.2 - Confidence Levels

**Narrative**: Not every artifact carries the same confidence. A process creation event with command line may be high-confidence evidence of a process start if auditing was enabled and logs are intact. A lone file timestamp may be lower-confidence because copies, extraction, and metadata changes can alter it.

Confidence example:

- High: service install event plus matching file creation and process execution
- Medium: Prefetch plus Amcache path match without account context
- Low: one timestamp with no corroborating artifact

---

#### Activity 30.2a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: Which finding is stronger?

**Options**:
- A) Event 7045, file creation, and process execution all reference the same path
- B) One file timestamp exists with no context
- C) A filename looks suspicious but was never found
- D) A user remembers something happened last month

**Answer**: **A** - Multiple independent artifacts agreeing on a path and time create a stronger finding.

**Explanation shown after answering**: Corroboration is the difference between a lead and a defensible conclusion.

---

### 30.3 - Triage Order

**Narrative**: In a time-limited incident, collect the highest-value pivots first:

1. Current scope: host, user, suspected time window.
2. Execution evidence for suspicious paths.
3. Account logons and remote access.
4. Persistence mechanisms.
5. Network and file movement evidence.
6. Browser and user activity.
7. External telemetry comparison.

The goal is to decide whether the host is clean, suspicious, or confirmed compromised, then preserve deeper evidence as needed.

---

#### Activity 30.3a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: In triage, why define the suspected time window early?

**Options**:
- A) It reduces noise and helps choose relevant artifacts
- B) It guarantees no attacker activity happened outside it
- C) It makes timestamps unnecessary
- D) It deletes irrelevant evidence

**Answer**: **A** - Time windows help prioritize, but analysts should widen them if pivots require it.

**Explanation**: Triage is iterative; the first time window is a starting point.

---

### 30.4 - Fact vs Inference

**Narrative**: Reports should distinguish what the artifact says from what the analyst concludes.

Example:

```text
Fact: Event 7045 records service "UpdaterSvc" installed at 10:14 UTC with image path C:\ProgramData\updater.exe.
Fact: Prefetch indicates updater.exe executed on the same host.
Inference: The service likely provided persistence for updater.exe.
Caveat: Additional evidence is needed to attribute the action to a specific human operator.
```

---

#### Activity 30.4a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Easy

**Prompt**: A report should separate observed facts from analyst ______.

**Expected Answer**: `inference`

**Acceptable variations**: `inferences`, `conclusion`, `conclusions`

**Hint**: It is what the analyst reasons from the facts.

**Explanation**: Clear reports show evidence and reasoning separately.

---

### 30.5 - Final Playbook

**Narrative**: A compact Windows endpoint triage playbook:

1. Identify user, host, and time window.
2. Pull execution artifacts.
3. Pull account and remote access artifacts.
4. Pull persistence artifacts.
5. Pull network and file activity artifacts.
6. Normalize timestamps.
7. Correlate paths, SIDs, Logon IDs, hashes, and hostnames.
8. Mark confidence and caveats.
9. Decide next action: close, monitor, contain, or escalate.

---

#### Activity 30.5a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: What is the best final output of a triage playbook?

**Options**:
- A) A decision supported by evidence, confidence, and caveats
- B) A random list of every timestamp
- C) A deleted evidence folder
- D) A screenshot with no explanation

**Answer**: **A** - Triage should produce an actionable decision with evidence behind it.

**Explanation**: Good forensic work is useful because it is clear, scoped, and defensible.

