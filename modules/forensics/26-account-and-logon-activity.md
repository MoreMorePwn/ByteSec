# Module 26: Account and Logon Activity

> Intermediate | 35 minutes | 4 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Use successful logon events as attribution pivots
- Explain why SID and Logon ID fields matter
- Distinguish interactive, network, service, and remote activity clues
- Correlate account activity with execution and persistence artifacts

---

## Lesson Flow

### 26.1 - Successful Logons

**Narrative**: Event ID 4624 records successful logons when Security auditing is available. It can include the account name, domain, SID, source details, Logon Type, and Logon ID. A Logon ID is especially useful because it can tie later activity to the same session.

Common Logon Type meanings:

| Type | Meaning |
|------|---------|
| 2 | Interactive logon |
| 3 | Network logon |
| 4 | Batch logon |
| 5 | Service logon |
| 10 | Remote interactive logon |

---

#### Activity 26.1a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Easy

**Prompt**: A field often used to correlate activity within the same session is the ______ ID.

**Expected Answer**: `logon`

**Acceptable variations**: `Logon`, `Logon ID`, `logon id`

**Hint**: It appears in successful logon records.

**Explanation**: Logon ID can help connect account authentication to later actions.

---

### 26.2 - RDP Clues

**Narrative**: Remote Desktop activity often leaves multiple traces. Event ID 1149 can show that user authentication succeeded for a remote connection. Security logon events may show remote interactive logons. Terminal Services logs can expose connection and session changes.

RDP investigation pattern:

1. Identify remote authentication.
2. Extract account, source address, and session identifiers.
3. Look for nearby process creation.
4. Check file and execution artifacts for the same user.
5. Check persistence artifacts created after the session.

---

#### Activity 26.2a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: Which artifact family is useful when investigating Remote Desktop activity?

**Options**:
- A) Terminal Services event logs
- B) CPU fan speed only
- C) Wallpaper cache only
- D) Keyboard LED state

**Answer**: **A** - Terminal Services event logs can record remote connection and session activity.

**Explanation**: RDP timelines are stronger when authentication, session, and process events agree.

---

### 26.3 - SID Pivots

**Narrative**: Usernames can change. SIDs are more stable identifiers for accounts. A SID can connect Security logs, profile paths under `C:\Users`, Recycle Bin folders, SRUM records, and other user-specific artifacts.

When a suspicious activity is tied to a SID, translate it carefully. Domain and local accounts can have different SID structures, and reused usernames can mislead an investigation.

---

#### Activity 26.3a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: Why is a SID often better than a display username as a pivot?

**Options**:
- A) It is a stable account identifier across many artifacts
- B) It is always shorter
- C) It contains the account password
- D) It only appears in browser history

**Answer**: **A** - SIDs help connect account activity across Windows artifacts.

**Explanation**: Display names can be ambiguous; SIDs reduce ambiguity.

---

### 26.4 - From Account To Action

**Narrative**: Account attribution is not the finish line. After finding a suspicious logon, pivot to what happened during or after that session:

- Process creation events
- Prefetch and Amcache records
- SRUM application records
- Service installs
- Scheduled task creation
- File creation and deletion artifacts
- RDP session events

---

#### Activity 26.4a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: A network logon appears shortly before a remote service install. Which event should be reviewed for the service creation?

**Options**:
- A) Event ID 7045
- B) Event ID 4104
- C) Event ID 1149
- D) Event ID 1

**Answer**: **A** - Event ID 7045 is commonly associated with service installation.

**Explanation shown after answering**: A remote service install timeline often pairs a network logon with service-control activity.

