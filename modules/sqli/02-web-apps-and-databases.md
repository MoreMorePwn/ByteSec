# Module 02: How Web Apps Talk to Databases

> ⭐ Beginner | ⏱️ 15 minutes | 5 activities

---

## Learning Objectives
By the end of this module, students will be able to:
- Trace the journey of a user input from browser to database
- Identify where SQL queries are constructed in backend code
- Understand the trust boundary between user input and server logic

---

## Lesson Flow

### 2.1 — The Request Journey (Concept + Visual)

**Narrative**: *When you type your username and password into a login form and click "Submit", a chain of events begins. Let's follow that journey.*

**Interactive Visual**: Animated flow diagram (student clicks "Next" to advance each step)

```
Step 1: [Browser]  →  User types "alice" and "s3cur3!" into a login form
Step 2: [Network]  →  Browser sends HTTP POST request to server
Step 3: [Server]   →  Backend code receives the input
Step 4: [Query]    →  Server builds a SQL query using the input
Step 5: [Database] →  Database executes the query and returns results
Step 6: [Response] →  Server sends "Login successful!" back to browser
```

---

### 2.2 — Inside the Backend Code

**Narrative**: *Let's peek behind the curtain. Here's what a typical (vulnerable!) login function looks like:*

```python
# Flask web application (Python)
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']   # Step 1: Get user input
    password = request.form['password']   # Step 1: Get user input
    
    # Step 2: Build SQL query (⚠️ DANGEROUS WAY)
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    # Step 3: Execute query
    result = db.execute(query)
    
    # Step 4: Check result
    if result:
        return "Login successful!"
    else:
        return "Invalid credentials."
```

**Highlight**: The f-string on line 7 is glowing red with a ⚠️ icon.

---

#### 🔍 Activity 2.2a — SPOT THE VULNERABILITY

> **Type**: SPOT  
> **Difficulty**: Easy

**Prompt**: Look at the code above. Which line introduces the security vulnerability? Click on it.

```python
# Line 1: username = request.form['username']
# Line 2: password = request.form['password']
# Line 3: query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
# Line 4: result = db.execute(query)
# Line 5: if result:
```

**Answer**: **Line 3** ✅

**Explanation**: *Line 3 directly inserts user input into the SQL string using an f-string. The user input is never validated, sanitized, or parameterized. This means whatever the user types becomes part of the SQL command.*

**Common wrong answer — Line 4**: *Line 4 executes the query, but the vulnerability was introduced on Line 3 when the query was built. Executing a safe query is fine — the problem is building an unsafe one.*

---

### 2.3 — The Trust Boundary

**Narrative**: *There's an invisible line in every application called the **trust boundary**. Everything on the user's side (browser, input fields, URLs) is **untrusted**. Everything should be validated before it crosses into the server side.*

**Visual**: Split diagram

```
╔══════════════════════════╗    ╔══════════════════════════╗
║    🚫 UNTRUSTED ZONE     ║    ║    ✅ TRUSTED ZONE        ║
║                          ║    ║                          ║
║  • Form inputs           ║    ║  • Validated data        ║
║  • URL parameters        ║    ║  • Parameterized queries ║
║  • Cookies               ║ →→ ║  • Server-side logic     ║
║  • HTTP headers          ║    ║  • Database engine       ║
║  • Hidden form fields    ║    ║                          ║
╚══════════════════════════╝    ╚══════════════════════════╝
         TRUST BOUNDARY →→→
```

---

#### 🧩 Activity 2.3a — MULTIPLE CHOICE

> **Type**: MC  
> **Difficulty**: Medium

**Prompt**: A developer hides the user role in a hidden HTML form field:

```html
<input type="hidden" name="role" value="user">
```

Is this safe from tampering?

**Options**:
- A) Yes, because the field is hidden from the user
- B) Yes, because only the server can set hidden fields
- C) No, because anything from the browser can be modified by the user ✅
- D) No, but only if the user knows JavaScript

**Answer**: **C** — Hidden fields are still part of the HTML sent to the browser. Anyone can open DevTools, change `"user"` to `"admin"`, and submit the form. **Never trust client-side data.**

---

### 2.4 — Following the Injection Path

**Narrative**: *Let's trace exactly what happens when an attacker enters a malicious input into our vulnerable login form.*

**Interactive Step-Through** (student clicks to advance):

**Normal Login**:
```
Input:  username = alice    password = s3cur3!
Query:  SELECT * FROM users WHERE username = 'alice' AND password = 's3cur3!'
Result: ✅ Returns Alice's row → Login successful
```

**Attack Login**:
```
Input:  username = ' OR 1=1 --    password = anything
Query:  SELECT * FROM users WHERE username = '' OR 1=1 --' AND password = 'anything'
Result: ⚠️ Returns ALL rows → Login successful (as first user!)
```

**Breakdown**:
- `'` → Closes the opening quote for username
- `OR 1=1` → Makes the WHERE clause always true
- `--` → Comments out the rest of the query (password check is ignored!)

---

#### 🧪 Activity 2.4a — PREDICT THE OUTPUT

> **Type**: PREDICT  
> **Difficulty**: Medium

**Prompt**: Given this backend code:

```python
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
```

If the attacker enters:
- Username: `admin'--`
- Password: `doesntmatter`

What is the final SQL query?

**Options**:
- A) `SELECT * FROM users WHERE username = 'admin'--' AND password = 'doesntmatter'` ✅
- B) `SELECT * FROM users WHERE username = 'admin--' AND password = 'doesntmatter'`
- C) `SELECT * FROM users WHERE username = 'admin' AND password = 'doesntmatter'`
- D) An error occurs

**Answer**: **A** — The `'` closes the username string, and `--` comments out everything after it. The effective query is:

```sql
SELECT * FROM users WHERE username = 'admin'
```

The password check is completely bypassed! The attacker logs in as admin without knowing the password.

---

### 2.5 — Where Can Injection Happen?

**Narrative**: *SQL injection isn't limited to login forms. Any place where user input touches a SQL query is a potential entry point.*

**Visual**: Diagram showing multiple injection points

```
🔴 Login forms          → username, password fields
🔴 Search bars          → search query parameter
🔴 URL parameters       → /product?id=5
🔴 Cookie values        → session tokens, preferences
🔴 HTTP headers         → User-Agent, Referer
🔴 File upload names    → filename metadata
🔴 API request bodies   → JSON/XML payloads
```

---

#### 🖱️ Activity 2.5a — DRAG & DROP (Matching)

> **Type**: DND (Match pairs)  
> **Difficulty**: Medium

**Prompt**: Match each user input source to its injection risk scenario:

| Input Source | Scenario |
|-------------|----------|
| Search bar | `SELECT * FROM products WHERE name LIKE '%____%'` |
| URL parameter | `SELECT * FROM products WHERE id = ___` |
| Login form | `SELECT * FROM users WHERE username = '___'` |
| Cookie | `SELECT * FROM sessions WHERE token = '___'` |

**Student drags** input sources to the correct query template.

**Answer**: Each source maps to the scenario where that type of input would be interpolated into a query.

---

#### 🧩 Activity 2.5b — MULTIPLE CHOICE

> **Type**: MC  
> **Difficulty**: Medium

**Prompt**: A web app has this URL for viewing products:

```
https://shop.com/product?id=42
```

The backend code is:

```python
product_id = request.args.get('id')
query = f"SELECT * FROM products WHERE id = {product_id}"
```

What makes this **especially** dangerous compared to string-based injection?

**Options**:
- A) Numbers can't be injected
- B) There are no quotes to escape, so the attacker doesn't need to close any string ✅
- C) URL parameters are automatically sanitized
- D) GET requests are safer than POST requests

**Answer**: **B** — Since the id is a number, it's inserted without quotes. The attacker doesn't even need to worry about quote characters. They can simply append SQL:

```
/product?id=42 UNION SELECT username, password FROM users--
```

---

## Module 2 Summary

| Concept | Key Takeaway |
|---------|-------------|
| Request Journey | User input travels: Browser → Server → Query → Database |
| Trust Boundary | Never trust any data from the client side |
| Query Building | String concatenation/f-strings create injection points |
| `--` (Comment) | Attackers use SQL comments to ignore the rest of the query |
| Injection Surfaces | Any user-controlled input can be an injection vector |

**Teaser for Module 03**: *You've seen how the attack works conceptually. Now it's time to get your hands dirty. In the next module, you'll craft your first SQL injection in a safe sandbox environment...*
