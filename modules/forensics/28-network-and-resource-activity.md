# Module 28: Network and Resource Activity

> Intermediate | 30 minutes | 4 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Use SRUM network data as an exfiltration triage pivot
- Interpret firewall rule change events
- Explain tracing-key evidence
- Combine endpoint network artifacts with external logs

---

## Lesson Flow

### 28.1 - SRUM Network Usage

**Narrative**: SRUM network records can show application-level byte counts, user SID, interface type, and time buckets. This can help answer "which process moved data?" when packet captures are unavailable.

Interpretation rules:

- Treat times as approximate buckets.
- Correlate application identifiers with execution artifacts.
- Translate SIDs to users.
- Compare byte volume to external firewall or proxy logs.
- Remember that absence does not prove no traffic occurred.

---

#### Activity 28.1a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: What is the best use of SRUM network records?

**Options**:
- A) Estimating application-level network usage over time
- B) Recovering all encrypted payload contents
- C) Replacing disk imaging
- D) Disabling the firewall

**Answer**: **A** - SRUM can estimate which applications transferred data and when.

**Explanation**: SRUM is a triage and correlation artifact, not full packet capture.

---

### 28.2 - Firewall Events

**Narrative**: Windows firewall events can expose rule creation, modification, and deletion. Rule changes can indicate legitimate administration, software installation, or attacker preparation for inbound access.

Useful review questions:

- What rule changed?
- Which program path does it reference?
- Who made the change?
- Was the change near suspicious logon or service activity?
- Was the rule later deleted?

---

#### Activity 28.2a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Easy

**Prompt**: A firewall rule was added minutes after a suspicious logon. What should the analyst do next?

**Options**:
- A) Correlate the rule path, account, timestamp, and related process activity
- B) Ignore it because firewall events are never useful
- C) Delete all logs immediately
- D) Assume the case is solved without more evidence

**Answer**: **A** - Firewall events are strongest when tied to account and execution context.

**Explanation shown after answering**: A rule change is a lead. Correlation turns it into evidence.

---

### 28.3 - Tracing Registry Keys

**Narrative**: Some Windows tracing keys can show that an executable used specific networking libraries or connection paths. These artifacts are narrow, but they can support a timeline when paired with execution and network records.

Use them carefully:

- They may show first use rather than every use.
- They may not exist for every application.
- They should be paired with process and SRUM evidence.

---

#### Activity 28.3a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: Why should tracing-key evidence be treated carefully?

**Options**:
- A) It can be narrow and may not record every connection
- B) It always contains full packet captures
- C) It proves the user typed every command manually
- D) It is unrelated to networking

**Answer**: **A** - Tracing artifacts are useful but limited.

**Explanation**: Narrow artifacts become valuable when they agree with stronger telemetry.

---

### 28.4 - External Corroboration

**Narrative**: Endpoint network artifacts should be compared with network-side telemetry whenever possible:

- Firewall logs
- Proxy logs
- DNS logs
- VPN logs
- NetFlow records
- EDR network events
- Cloud access logs

The endpoint may show which process and user were involved. The network may show destination, volume, and perimeter timing.

---

#### Activity 28.4a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Easy

**Prompt**: Endpoint SRUM can identify application network usage, while external logs can help confirm destination and traffic ______.

**Expected Answer**: `volume`

**Acceptable variations**: `volumes`, `amount`, `size`

**Hint**: Think bytes sent and received.

**Explanation**: Network-side telemetry can validate the magnitude and destination of endpoint activity.

