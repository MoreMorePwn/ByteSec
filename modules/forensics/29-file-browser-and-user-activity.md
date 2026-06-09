# Module 29: File, Browser, and User Activity

> Beginner | 35 minutes | 4 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Use Recycle Bin records as file deletion clues
- Explain how shell items and jump lists reveal user interaction
- Identify browser artifacts that support web activity timelines
- Connect file activity to account and execution evidence

---

## Lesson Flow

### 29.1 - Recycle Bin Records

**Narrative**: Modern Windows Recycle Bin activity creates paired records. One record stores metadata such as original path and deletion time, while the companion record stores the deleted content. Recycle Bin folders are tied to user SIDs.

Analysis value:

- Deleted file original path
- Deletion time
- User SID context
- Potential recovery of deleted content

---

#### Activity 29.1a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: Why are Recycle Bin records useful?

**Options**:
- A) They can show original path, deletion time, and user SID context
- B) They store every password typed by a user
- C) They replace all file timestamps
- D) They only exist on Linux

**Answer**: **A** - Recycle Bin metadata can support file deletion timelines.

**Explanation**: Deleted-file evidence is stronger when tied to the user SID and surrounding activity.

---

### 29.2 - Jump Lists and Shell Items

**Narrative**: Jump lists and shell items can show files, folders, and applications a user interacted with. They are useful when a case asks what a user opened, browsed to, or pinned. They can also show paths to removable media or network shares.

Review:

- AutomaticDestinations and CustomDestinations
- Link file metadata
- Shellbag-style folder interaction traces
- Recent documents
- Volume and path references

---

#### Activity 29.2a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Easy

**Prompt**: A jump list references `E:\tools\dump.exe`. What is a reasonable next pivot?

**Options**:
- A) Check removable media and execution artifacts for that path
- B) Change the desktop wallpaper
- C) Ignore it because paths are never useful
- D) Only review browser cookies

**Answer**: **A** - The path can connect user activity to removable media and execution evidence.

**Explanation shown after answering**: File paths are powerful pivots across Windows artifacts.

---

### 29.3 - Browser Artifacts

**Narrative**: Browser artifacts can show visited URLs, downloads, cache entries, cookies, form history, and extension activity depending on browser and configuration. These artifacts can help connect phishing, payload download, and command-and-control staging.

Browser analysis questions:

- What URLs were visited?
- What files were downloaded?
- Which profile was active?
- Was the file later executed?
- Did browser history align with proxy or DNS logs?

---

#### Activity 29.3a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: A browser download record is most useful when paired with which follow-up evidence?

**Options**:
- A) File creation and execution artifacts for the downloaded path
- B) Monitor brightness settings
- C) Keyboard repeat delay
- D) Printer ink level

**Answer**: **A** - Download evidence should be tied to file and execution activity.

**Explanation**: Downloaded does not always mean executed.

---

### 29.4 - File Timeline Discipline

**Narrative**: File timestamps are helpful but easy to overread. Creation, modification, access, and metadata-change times have different meanings and may be affected by copying, extraction, mounting, or application behavior.

Use file artifacts with:

- Execution evidence
- Account activity
- Browser downloads
- Recycle Bin records
- Hash and path matching
- Time zone normalization

---

#### Activity 29.4a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Easy

**Prompt**: File timestamps should be normalized to a consistent time ______ before building a timeline.

**Expected Answer**: `zone`

**Acceptable variations**: `timezone`, `time zone`

**Hint**: Local time and UTC can otherwise be mixed.

**Explanation**: Time zone mistakes can create false sequence conclusions.

