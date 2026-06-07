# Module 06: Defense & Prevention

> ⭐⭐ Intermediate | ⏱️ 25 minutes | 8 activities

---

## Learning Objectives
By the end of this module, students will be able to:
- Implement parameterized queries (prepared statements) in multiple languages
- Apply input validation and output encoding
- Configure the principle of least privilege for database accounts
- Set up a Web Application Firewall (WAF) as defense-in-depth
- Apply a layered defense strategy

---

## Lesson Flow

### 6.1 — The Defense Pyramid

**Narrative**: *Defense against SQL injection isn't a single fix — it's a layered strategy. Think of it as a pyramid, where each layer catches what the previous one misses.*

**Interactive Visual**: Pyramid diagram (click each layer)

```
                    ╱╲
                   ╱  ╲
                  ╱ WAF ╲         ← Layer 4: Web Application Firewall
                 ╱────────╲
                ╱ Least    ╲      ← Layer 3: Principle of Least Privilege
               ╱ Privilege  ╲
              ╱──────────────╲
             ╱ Input Validation╲  ← Layer 2: Validate & Sanitize Input
            ╱──────────────────╲
           ╱  PARAMETERIZED     ╲ ← Layer 1: THE FOUNDATION
          ╱   QUERIES            ╲
         ╱════════════════════════╲
```

**⚠️ Critical**: Parameterized queries are the **only** reliable defense. All other layers are supplements, not replacements.

---

### 6.2 — Layer 1: Parameterized Queries (Prepared Statements)

**Narrative**: *This is the silver bullet. Parameterized queries separate **code** from **data**. The database engine knows exactly which parts are SQL commands and which parts are user values. Injection becomes impossible.*

**How it works**:

```
VULNERABLE (string concatenation):
  "SELECT * FROM users WHERE name = '" + input + "'"
  → Database sees: one big string (can't tell code from data)

SAFE (parameterized):
  "SELECT * FROM users WHERE name = ?"  +  [input as parameter]
  → Database sees: fixed SQL template + separate data value
  → User input can NEVER become SQL code
```

**Implementation in 5 languages**:

#### Python (with SQLite)
```python
# ❌ VULNERABLE
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)

# ✅ SAFE — Parameterized
query = "SELECT * FROM users WHERE username = ?"
cursor.execute(query, (username,))
```

#### JavaScript (Node.js with MySQL)
```javascript
// ❌ VULNERABLE
const query = `SELECT * FROM users WHERE username = '${username}'`;
db.query(query);

// ✅ SAFE — Parameterized
const query = 'SELECT * FROM users WHERE username = ?';
db.query(query, [username]);
```

#### Java (JDBC)
```java
// ❌ VULNERABLE
String query = "SELECT * FROM users WHERE username = '" + username + "'";
Statement stmt = conn.createStatement();
stmt.executeQuery(query);

// ✅ SAFE — PreparedStatement
String query = "SELECT * FROM users WHERE username = ?";
PreparedStatement pstmt = conn.prepareStatement(query);
pstmt.setString(1, username);
pstmt.executeQuery();
```

#### PHP (PDO)
```php
// ❌ VULNERABLE
$query = "SELECT * FROM users WHERE username = '$username'";
$result = $pdo->query($query);

// ✅ SAFE — Parameterized
$query = "SELECT * FROM users WHERE username = :username";
$stmt = $pdo->prepare($query);
$stmt->execute(['username' => $username]);
```

#### C# (.NET)
```csharp
// ❌ VULNERABLE
string query = $"SELECT * FROM users WHERE username = '{username}'";
SqlCommand cmd = new SqlCommand(query, conn);

// ✅ SAFE — Parameterized
string query = "SELECT * FROM users WHERE username = @username";
SqlCommand cmd = new SqlCommand(query, conn);
cmd.Parameters.AddWithValue("@username", username);
```

---

#### 🛡️ Activity 6.2a — FIX THE CODE

> **Type**: FIX  
> **Difficulty**: Medium

**Prompt**: This Python Flask endpoint is vulnerable. Rewrite it to use parameterized queries:

```python
@app.route('/search')
def search():
    term = request.args.get('q')
    query = f"SELECT * FROM products WHERE name LIKE '%{term}%'"
    results = db.execute(query).fetchall()
    return render_template('results.html', products=results)
```

**Expected Answer**:
```python
@app.route('/search')
def search():
    term = request.args.get('q')
    query = "SELECT * FROM products WHERE name LIKE ?"
    results = db.execute(query, ('%' + term + '%',)).fetchall()
    return render_template('results.html', products=results)
```

**Key point**: The `%` wildcards are added to the parameter value, not to the query string. The `?` placeholder ensures the search term is always treated as data.

**Common mistake**: Putting `%?%` in the query — this doesn't work because `?` must be a standalone placeholder.

---

#### 🔍 Activity 6.2b — SPOT THE VULNERABILITY

> **Type**: SPOT  
> **Difficulty**: Hard

**Prompt**: A developer claims this code is safe because it uses parameterized queries. Is it actually safe?

```python
table_name = request.args.get('table')
query = f"SELECT * FROM {table_name} WHERE id = ?"
cursor.execute(query, (user_id,))
```

**Answer**: **NOT SAFE** ❌ — Line 2 is still vulnerable!

**Explanation**: *The `id` parameter is properly parameterized, but the **table name** is still injected via string formatting! You cannot parameterize table names, column names, or SQL keywords — only values. An attacker could set `table_name` to `users; DROP TABLE products;--`.*

**Fix**: Use a whitelist for table names:
```python
ALLOWED_TABLES = {'products', 'categories', 'reviews'}
table_name = request.args.get('table')
if table_name not in ALLOWED_TABLES:
    abort(400)
query = f"SELECT * FROM {table_name} WHERE id = ?"
cursor.execute(query, (user_id,))
```

---

### 6.3 — Layer 2: Input Validation & Sanitization

**Narrative**: *Parameterized queries are your main defense, but input validation adds another layer. Validate inputs to ensure they match expected formats.*

**Types of validation**:

| Validation | Example | Purpose |
|-----------|---------|---------|
| **Type checking** | Ensure `id` is an integer | Reject non-numeric input |
| **Whitelist** | Only allow `['name', 'price', 'date']` for sort columns | Prevent arbitrary column names |
| **Length limits** | Max 50 chars for username | Limit payload size |
| **Regex patterns** | Email: `^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$` | Reject unexpected characters |
| **Encoding** | Escape `<`, `>`, `'`, `"` in output | Prevent XSS (related but different) |

**⚠️ Important**: Input validation alone is **NOT sufficient** defense against SQL injection. It should always be used **alongside** parameterized queries, never as a replacement.

---

#### 🧩 Activity 6.3a — MULTIPLE CHOICE

> **Type**: MC  
> **Difficulty**: Medium

**Prompt**: A developer adds this validation before using the input in a SQL query:

```python
def sanitize(input_string):
    return input_string.replace("'", "''")  # Escape single quotes
```

Is this a reliable defense against SQL injection?

**Options**:
- A) Yes, escaping quotes prevents all SQL injection
- B) No — it can be bypassed in certain character encodings and doesn't handle all injection types ✅
- C) Yes, but only for MySQL databases
- D) No — the function should also escape semicolons

**Answer**: **B** — Manual escaping is fragile. It can be bypassed via:
- Multi-byte character encoding attacks (GBK, SJIS)
- Numeric injection (no quotes to escape)
- Unicode homoglyph attacks
- Database-specific escape sequences

**The rule**: Parameterized queries > Manual escaping. Always.

---

### 6.4 — Layer 3: Principle of Least Privilege

**Narrative**: *Even if an attacker succeeds in injecting SQL, you can limit the damage by restricting what the database account can do.*

**Bad practice**:
```sql
-- Web app connects as root/admin with full privileges
GRANT ALL PRIVILEGES ON *.* TO 'webapp'@'localhost';
-- Attacker can: read all data, delete tables, read files, execute commands
```

**Good practice**:
```sql
-- Create a restricted account for the web app
CREATE USER 'webapp_readonly'@'localhost' IDENTIFIED BY 'strong_password';

-- Grant ONLY what's needed
GRANT SELECT ON webapp_db.products TO 'webapp_readonly'@'localhost';
GRANT SELECT ON webapp_db.categories TO 'webapp_readonly'@'localhost';
GRANT SELECT, INSERT ON webapp_db.orders TO 'webapp_readonly'@'localhost';

-- Explicitly deny dangerous operations
-- No DELETE, DROP, FILE, EXECUTE privileges
```

**Impact comparison**:

| Scenario | Root Account | Restricted Account |
|----------|-------------|-------------------|
| `SELECT * FROM users` | ✅ Returns all users | ❌ Permission denied |
| `DROP TABLE products` | ✅ Table deleted 💀 | ❌ Permission denied |
| `LOAD_FILE('/etc/passwd')` | ✅ File contents leaked | ❌ Permission denied |
| `INTO OUTFILE '/var/www/shell.php'` | ✅ Webshell uploaded | ❌ Permission denied |

---

#### 🖱️ Activity 6.4a — DRAG & DROP (Permission Assignment)

> **Type**: DND (Match pairs)  
> **Difficulty**: Medium

**Prompt**: Match each web application function to the **minimum** database permissions it needs:

| Application Function | Required Permission |
|---------------------|-------------------|
| Product search page | `SELECT` on products |
| User registration | `INSERT` on users |
| Order placement | `SELECT` on products + `INSERT` on orders |
| Admin delete user | `DELETE` on users |
| Profile update | `UPDATE` on users |

**Student drags** permission sets to each function.

---

### 6.5 — Layer 4: Web Application Firewall (WAF)

**Narrative**: *A WAF sits between users and your application, analyzing HTTP requests for malicious patterns. It can block common SQL injection payloads before they reach your code.*

**How a WAF works**:

```
User Request → [WAF] → Application → Database
                 ↓
         Checks for patterns:
         • ' OR 1=1
         • UNION SELECT
         • ; DROP TABLE
         • SLEEP(
         • Hex-encoded attacks
         
         If suspicious → BLOCK ❌
         If clean → ALLOW ✅
```

**Popular WAFs**: ModSecurity, AWS WAF, Cloudflare WAF, Imperva

**⚠️ Limitation**: WAFs can be bypassed with advanced encoding, comment insertion, or case manipulation:

```sql
-- Standard (blocked by WAF):
' UNION SELECT password FROM users--

-- Evasion attempt (may bypass WAF):
' uNiOn SeLeCt password FrOm users--
' /*!UNION*/ /*!SELECT*/ password FROM users--
' UNION%0aSELECT password FROM users--
```

**This is why WAFs are Layer 4 (supplement), not Layer 1 (foundation).**

---

#### 🧩 Activity 6.5a — MULTIPLE CHOICE

> **Type**: MC  
> **Difficulty**: Medium

**Prompt**: A company relies solely on a WAF to protect against SQL injection and doesn't use parameterized queries. An attacker discovers a bypass for their WAF's rules. What happens?

**Options**:
- A) The database's built-in security will still prevent the injection
- B) The application is fully compromised because there are no other defenses ✅
- C) The operating system firewall will catch the injection
- D) The WAF will learn and adapt to block the bypass

**Answer**: **B** — Without parameterized queries as the foundation, bypassing the WAF means the application is fully exposed. This is why defense-in-depth is essential — no single layer should be your only protection.

---

### 6.6 — Bonus Layer: ORM & Stored Procedures

**Narrative**: *Two additional tools in your defense arsenal:*

#### Object-Relational Mappers (ORMs)
```python
# Instead of writing raw SQL...
query = f"SELECT * FROM users WHERE name = '{name}'"

# Use an ORM like SQLAlchemy:
user = User.query.filter_by(name=name).first()

# The ORM generates parameterized queries automatically!
```

#### Stored Procedures
```sql
-- Define a procedure in the database:
CREATE PROCEDURE GetUser(IN p_username VARCHAR(50))
BEGIN
    SELECT * FROM users WHERE username = p_username;
END;

-- Call from application:
CALL GetUser('alice');
-- The procedure treats the input as data, not code
```

**⚠️ Caveat**: ORMs and stored procedures can still be vulnerable if you use raw SQL features within them:
```python
# ❌ Still vulnerable — raw SQL within ORM
User.query.filter(text(f"name = '{name}'"))

# ✅ Safe — using ORM's built-in filtering
User.query.filter_by(name=name)
```

---

#### 🛡️ Activity 6.6a — FIX THE CODE (Comprehensive)

> **Type**: FIX  
> **Difficulty**: Hard

**Prompt**: This Express.js (Node.js) API has three SQL injection vulnerabilities. Fix all of them:

**Vulnerable Code**:
```javascript
app.get('/api/products', (req, res) => {
    const search = req.query.q;
    const sort = req.query.sort;
    const limit = req.query.limit;
    
    const query = `SELECT * FROM products 
                   WHERE name LIKE '%${search}%' 
                   ORDER BY ${sort} 
                   LIMIT ${limit}`;
    
    db.query(query, (err, results) => {
        res.json(results);
    });
});
```

**Expected Answer**:
```javascript
const ALLOWED_SORT_COLUMNS = ['name', 'price', 'created_at', 'rating'];

app.get('/api/products', (req, res) => {
    const search = req.query.q;
    const sort = req.query.sort;
    const limit = parseInt(req.query.limit) || 20;
    
    // Whitelist sort column
    const sortColumn = ALLOWED_SORT_COLUMNS.includes(sort) ? sort : 'name';
    
    // Parameterize search, validate limit, whitelist sort
    const query = `SELECT * FROM products 
                   WHERE name LIKE ? 
                   ORDER BY ${sortColumn} 
                   LIMIT ?`;
    
    db.query(query, [`%${search}%`, limit], (err, results) => {
        res.json(results);
    });
});
```

**Fixes applied**:
1. **search** → Parameterized with `?`
2. **sort** → Whitelisted against allowed column names
3. **limit** → Parsed as integer (type validation) + parameterized

---

### 6.7 — The Defense Checklist

**Interactive Checklist** (student checks items they would implement):

```
✅ MUST-HAVE (Non-negotiable)
  □ Use parameterized queries for ALL database interactions
  □ Never concatenate user input into SQL strings
  □ Use least-privilege database accounts

✅ SHOULD-HAVE (Strongly recommended)
  □ Validate all inputs (type, length, format)
  □ Whitelist allowed values for table/column names
  □ Use an ORM with proper configuration
  □ Disable detailed error messages in production

✅ NICE-TO-HAVE (Additional protection)
  □ Deploy a WAF with SQL injection rules
  □ Implement logging and monitoring for suspicious queries
  □ Use stored procedures for complex operations
  □ Regular security audits and penetration testing
  □ Keep database software up to date
```

---

#### 🧩 Activity 6.7a — MULTIPLE CHOICE (Final Scenario)

> **Type**: MC  
> **Difficulty**: Hard

**Prompt**: You're reviewing a Python web application. Which combination of defenses provides the STRONGEST protection?

**Options**:
- A) WAF + Input validation + Manual quote escaping
- B) Parameterized queries + Least privilege + Input validation + WAF ✅
- C) Stored procedures only
- D) Input validation + Output encoding + HTTPS

**Answer**: **B** — This is proper defense-in-depth:
1. **Parameterized queries** make injection impossible (Layer 1)
2. **Least privilege** limits damage if somehow breached (Layer 3)
3. **Input validation** catches malformed inputs early (Layer 2)
4. **WAF** provides an external monitoring/blocking layer (Layer 4)

---

## Module 6 Summary

| Defense Layer | Effectiveness | Role |
|--------------|--------------|------|
| Parameterized queries | 🟢 Essential | **Primary defense** — makes injection impossible |
| Input validation | 🟡 Important | Secondary filter — rejects malformed input |
| Least privilege | 🟡 Important | Damage control — limits what attacker can do |
| WAF | 🟠 Supplementary | External monitoring — blocks known patterns |
| ORM | 🟢 Effective | Generates safe queries automatically |
| Stored procedures | 🟡 Helpful | Encapsulates query logic in database |

**Teaser for Module 07**: *Theory is powerful, but real stories are unforgettable. In the final module, you'll analyze real-world SQL injection breaches that cost companies millions, and prove your mastery in a final challenge...*
