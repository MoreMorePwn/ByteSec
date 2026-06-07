# Module 01: SQL Fundamentals Refresher

> ⭐ Beginner | ⏱️ 15 minutes | 6 activities

---

## Learning Objectives
By the end of this module, students will be able to:
- Write basic SELECT, INSERT, UPDATE, and DELETE statements
- Understand how WHERE clauses filter data
- Recognize how string concatenation works in SQL

---

## Lesson Flow

### 1.1 — What is a Database? (Concept)

**Narrative**: *Imagine a massive spreadsheet with millions of rows — that's essentially a database table. SQL (Structured Query Language) is the language you use to ask it questions.*

**Visual**: Show animated table called `users` with columns: `id`, `username`, `password`, `email`, `role`

| id | username | password | email | role |
|----|----------|----------|-------|------|
| 1 | alice | s3cur3! | alice@mail.com | admin |
| 2 | bob | pass123 | bob@mail.com | user |
| 3 | charlie | qwerty | charlie@mail.com | user |
| 4 | diana | hunter2 | diana@mail.com | moderator |

---

### 1.2 — Your First Query

**Narrative**: *To retrieve data, we use the `SELECT` statement. Let's grab all usernames from the table.*

```sql
SELECT username FROM users;
```

**Result shown**: `alice`, `bob`, `charlie`, `diana`

---

#### 🧪 Activity 1.2a — PREDICT THE OUTPUT

> **Type**: PREDICT  
> **Difficulty**: Easy

**Prompt**: What will this query return?

```sql
SELECT username, role FROM users WHERE role = 'admin';
```

**Options**:
- A) All usernames and roles
- B) Only `alice | admin`  ✅
- C) Only `admin`
- D) An error

**Answer**: **B** — The WHERE clause filters to only rows where `role` equals `'admin'`. Only Alice is an admin.

**Explanation shown after answering**: *The `WHERE` clause acts as a filter. It checks each row and only returns rows that match the condition. Think of it as an `if` statement for your database.*

---

### 1.3 — Filtering with WHERE

**Narrative**: *The `WHERE` clause is the gatekeeper. It decides which rows come back. This is also the exact place where SQL injection happens — but we'll get to that later.*

```sql
SELECT * FROM users WHERE username = 'bob';
```

**Result**: Shows only Bob's row

---

#### 🔤 Activity 1.3a — FILL IN THE BLANK

> **Type**: FITB  
> **Difficulty**: Easy

**Prompt**: Complete the query to find all users with the role `'moderator'`:

```sql
SELECT * FROM users WHERE _________;
```

**Expected Answer**: `role = 'moderator'`

**Acceptable variations**: `role='moderator'`, `role = "moderator"`

**Hint (shown after 1 failed attempt)**: *Which column stores the user type? What value are we looking for?*

**Explanation**: *We check the `role` column and compare it to the string `'moderator'`. SQL uses single quotes for string values.*

---

### 1.4 — Combining Conditions: AND & OR

**Narrative**: *You can chain multiple conditions together.*

```sql
-- AND: Both conditions must be true
SELECT * FROM users WHERE role = 'user' AND id > 2;

-- OR: At least one condition must be true  
SELECT * FROM users WHERE role = 'admin' OR role = 'moderator';
```

---

#### 🧩 Activity 1.4a — MULTIPLE CHOICE

> **Type**: MC  
> **Difficulty**: Easy

**Prompt**: What does this query return?

```sql
SELECT username FROM users WHERE role = 'user' OR role = 'admin';
```

**Options**:
- A) `alice, bob, charlie` ✅
- B) `bob, charlie`
- C) `alice`
- D) All four users

**Answer**: **A** — `alice` is admin, `bob` and `charlie` are users. `diana` is moderator, so she's excluded.

---

### 1.5 — The Danger of String Concatenation

**Narrative**: *Here's where things get interesting. Many web applications build SQL queries by gluing strings together. Watch carefully:*

```python
# Python backend code
query = "SELECT * FROM users WHERE username = '" + user_input + "'"
```

*If `user_input` is `bob`, the query becomes:*

```sql
SELECT * FROM users WHERE username = 'bob'
```

*Looks fine, right? But what if the user types something... unexpected?*

---

#### 🧪 Activity 1.5a — PREDICT THE OUTPUT

> **Type**: PREDICT  
> **Difficulty**: Medium

**Prompt**: A web app builds queries like this:

```python
query = "SELECT * FROM users WHERE username = '" + user_input + "'"
```

If `user_input` is: `bob' OR '1'='1`

What will the final SQL query look like?

**Options**:
- A) `SELECT * FROM users WHERE username = 'bob' OR '1'='1'` ✅
- B) `SELECT * FROM users WHERE username = 'bob OR 1=1'`
- C) An error will occur
- D) `SELECT * FROM users WHERE username = 'bob'`

**Answer**: **A** — The single quote in the input *closes* the original string, and the rest becomes part of the SQL logic. `'1'='1'` is always true, so this returns ALL users.

**💡 Key Insight**: *This is the fundamental mechanism behind SQL injection. The user's input "escapes" from the data context and becomes executable SQL code. You just saw your first injection — we'll master this in Module 03.*

---

### 1.6 — Quick-Fire Round

#### 🖱️ Activity 1.6a — DRAG & DROP

> **Type**: DND  
> **Difficulty**: Easy

**Prompt**: Arrange these SQL fragments to build a valid query that finds all admin users' emails:

**Fragments** (shuffled):
- `FROM users`
- `SELECT email`
- `WHERE role = 'admin'`

**Correct order**:
```sql
SELECT email
FROM users
WHERE role = 'admin'
```

---

## Module 1 Summary

| Concept | Key Takeaway |
|---------|-------------|
| SELECT | Retrieves data from tables |
| WHERE | Filters rows based on conditions |
| AND / OR | Combines multiple conditions |
| String concatenation | Building queries with user input is **dangerous** ⚠️ |

**Teaser for Module 02**: *Now you know SQL basics. But how does a web application actually send these queries? And where exactly does user input enter the picture? Let's find out...*
