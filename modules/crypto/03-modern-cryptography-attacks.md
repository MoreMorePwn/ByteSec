# Module 03: Modern Cryptography & Attacks

> ⭐ Intermediate | ⏱️ 30 minutes | 5 activities

---

## Learning Objectives
By the end of this module, students will be able to:
- Differentiate between hash functions, symmetric crypto, and asymmetric crypto
- Recognize ECB mode weaknesses (the "penguin" attack)
- Explain the padding oracle attack at a conceptual level
- Identify weak randomness and bad implementation patterns

---

## Lesson Flow

### 3.1 — Hash Functions

**Narrative**: *A hash function takes any input and produces a fixed-size output (digest). Good hash functions are:*

1. **Deterministic** — same input always gives same output
2. **One-way** — given a hash, you can't (easily) recover the input
3. **Collision-resistant** — hard to find two inputs with the same hash
4. **Avalanche effect** — changing one bit of input changes ~50% of output bits

```python
import hashlib
print(hashlib.md5(b"BYTESEC{test}").hexdigest())
# → "d41d8cd98f00b204e9800998ecf8427f" (example)
```

**Common hash functions in CTFs:**

| Hash | Output size | Still secure? | Notes |
|------|------------|---------------|-------|
| MD5 | 128-bit | ❌ Broken | Collisions found, do NOT use |
| SHA-1 | 160-bit | ❌ Broken | Theoretical collision attack practical |
| SHA-256 | 256-bit | ✅ Still secure | Standard choice today |
| bcrypt/scrypt/argon2 | Variable | ✅ Secure | Purpose-built for passwords |

**CTF use case**: Hashes are used for storing passwords, verifying file integrity, and as part of digital signatures. If you find a hash in a binary, you can try:
- **Google the hash** (if it's a known string)
- **Crack it** with hashcat or John the Ripper
- **Rainbow tables** (pre-computed hash lookups)

---

#### 🧪 Activity 3.1a — MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: A CTF challenge says "The flag's MD5 hash is `5d41402abc4b2a76b9719d911017c592`." What does this tell you about the flag?

**Options**:
- A) You now know the flag — MD5 is decryption
- B) You can try to look up the hash online or brute-force, but you can't reverse it directly ✅
- C) The flag is exactly 32 characters long
- D) The hash contains the flag in plaintext

**Answer**: **B** — Hashes are one-way; you can only search for known inputs or brute-force.

**Explanation shown after answering**: *Hashing is a one-way function. Knowing the hash of the flag doesn't reveal the flag — you need to either: (a) search an online hash database (for common inputs), (b) brute-force using a wordlist, or (c) use a different vulnerability. The hash of `"hello"` is `5d41402abc4b2a76b9719d911017c592`.*

---

### 3.2 — Symmetric Encryption (AES)

**Narrative**: *Symmetric encryption uses the same key for encryption and decryption. AES (Advanced Encryption Standard) is the industry standard, with key sizes of 128, 192, or 256 bits.*

**Modes of operation (critical for CTF challenges):**

| Mode | Description | Security Note |
|------|-------------|---------------|
| **ECB** | Each block encrypted independently | ❌ **INSECURE** — same plaintext block = same ciphertext block |
| **CBC** | Each block XORed with previous ciphertext | ✅ Good, but vulnerable to padding oracle |
| **CTR** | Counter mode — encrypts counter values | ✅ Good (parallelizable) |
| **GCM** | Authenticated encryption (CTR + MAC) | ✅ Best — encrypts AND authenticates |

**AES ECB weakness:** Because identical plaintext blocks produce identical ciphertext blocks, patterns in the plaintext survive in the ciphertext. This is famously demonstrated by encrypting a bitmap image of Tux (the Linux penguin) — you can still see the penguin shape in the ECB-encrypted version.

```
Plain:  [TUX IMAGE] → Encrypt → [TUX PATTERN VISIBLE]
```

---

#### 🧪 Activity 3.2a — PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: A CTF challenge encrypts a secret message using AES-ECB. The secret is: `"HelloAlice!HereIsMySecretFlag:BYTESEC{secret_stuff}"` and you control the text before this secret. If you can align your input such that `"Alice!Her"` is a full 16-byte AES block, what can you determine?

**Options**:
- A) Nothing — AES is secure
- B) You can brute-force the block by trying different 16-byte inputs until the ciphertext matches ✅
- C) You can decrypt the AES key
- D) You can read the flag directly

**Answer**: **B** — In ECB mode, you can perform a byte-at-a-time chosen-plaintext attack.

**Explanation shown after answering**: *ECB encrypts each 16-byte block independently. If you control text placed before the secret, you can: (1) align unknown bytes at block boundaries, (2) brute-force each byte by shifting your known prefix, and (3) compare ciphertext blocks byte-by-byte. This is the classic "byte-at-a-time ECB decryption" attack — one of the most important CTF crypto techniques.*

---

### 3.3 — Padding Oracle Attack

**Narrative**: *CBC mode requires padding to fill the last block. If an application tells you whether padding is valid or not (the "oracle"), you can decrypt the entire ciphertext without knowing the key — one byte at a time.*

**The attack flow:**

```python
# You have: ciphertext blocks C0, C1, C2
# You want: plaintext P1 (of block C1)
# You control: fake intermediate block I

# For each byte position (15 → 0):
#   - Modify byte in I so that decrypted padding = 0x01, 0x02, 0x03...
#   - Send to server → if "padding OK", you've found the right value
#   - XOR to recover the plaintext byte
```

**Defense:** Always use **authenticated encryption** (GCM, ChaCha20-Poly1305) or add a MAC to CBC. Never reveal padding errors.

---

#### 🧪 Activity 3.3a — MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Hard

**Prompt**: A web application encrypts cookies using AES-CBC and returns a "decryption failed" error when the padding is incorrect. This vulnerability is called:

**Options**:
- A) SQL injection
- B) Padding oracle attack ✅
- C) Buffer overflow
- D) ECB byte-at-a-time attack

**Answer**: **B** — Padding oracle attack — the server leaks information through padding error messages.

**Explanation shown after answering**: *When a server gives different responses for "padding valid" vs "padding invalid," it acts as a padding oracle. This lets an attacker decrypt any ciphertext byte-by-byte without knowing the key. The fix is to use authenticated encryption (GCM) or to verify a MAC before checking padding.*

---

### 3.4 — Asymmetric Encryption (RSA Basics)

**Narrative**: *Asymmetric (public-key) cryptography uses a key pair: a public key (shared freely) and a private key (kept secret). RSA is the most well-known.*

**RSA in a nutshell:**

1. Choose two large primes `p` and `q`
2. Compute `n = p × q` (the modulus)
3. Compute `φ(n) = (p-1)(q-1)`
4. Choose `e` (public exponent, typically 65537)
5. Compute `d` (private exponent: `e × d ≡ 1 (mod φ(n))`)

**Encryption:** `c = m^e mod n`
**Decryption:** `m = c^d mod n`

**Common RSA attacks in CTFs:**

| Attack | When it applies |
|--------|----------------|
| **Small e** (e=3) | If `m^3 < n`, cube root attack |
| **Same n, two e's** | Common modulus attack |
| **Two n's with shared factor** | GCD attack |
| **Wiener's attack** | When private exponent d is too small |
| **Fermat factoring** | When p and q are very close together |

---

#### 🧪 Activity 3.4a — FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Medium

**Prompt**: In RSA, the public key is `(n, e)` and the private key is `(n, d)`. If an attacker can factor `n` into `p × q`, they can compute `d` using the formula `d = e^(-1) mod φ(n)`. Given that `p = 61` and `q = 53`, what is `φ(n)`?

Write just the number.

**Expected Answer**: `3120`

**Acceptable variations**: `3120`

**Hint (shown after 1 failed attempt)**: *φ(n) = (p - 1) × (q - 1). p - 1 = 60, q - 1 = 52.*

**Explanation**: *φ(n) = (61 - 1) × (53 - 1) = 60 × 52 = 3120. Once an attacker knows φ(n), they can compute d as the modular inverse of e modulo φ(n). This is why factoring large numbers is critical for RSA security.*

---

### 3.5 — Common Crypto Mistakes in CTFs

**Narrative**: *Real-world crypto failures usually aren't about breaking the algorithm itself — they're about implementation mistakes. Here are the most common ones seen in CTF challenges:*

**1. ECB Mode** — Pattern leaks. Never use ECB for anything.
**2. Weak Randomness** — Using `random` module instead of `secrets` or `os.urandom`:
```python
# BAD:
import random
key = random.randint(0, 2**128)  # Predictable!

# GOOD:
import secrets
key = secrets.token_bytes(16)  # Cryptographically secure
```
**3. Hardcoded Keys** — Keys in source code, `.env` files accidentally committed, or keys derived from predictable values (username, date, etc.)
**4. Hash Comparison Timing** — Using `==` instead of constant-time compare opens timing attacks
**5. Rolling Your Own Crypto** — Homebrew algorithms are almost always broken. Use standard libraries.

---

#### 🧪 Activity 3.5a — MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: A CTF challenge uses AES-CBC with a key derived as `hashlib.md5(username.encode()).hexdigest()[:16]`. What is the biggest vulnerability?

**Options**:
- A) MD5 is broken — collisions make it insecure
- B) The key is deterministic and predictable from the username ✅
- C) CBC mode is always insecure
- D) hexdigest() produces hexadecimal output

**Answer**: **B** — The key is derived from a known value (username) with no secret input.

**Explanation shown after answering**: *The encryption key is a deterministic function of the username. Anyone who knows the username (which is often publicly visible) can compute the same key and decrypt all data encrypted for that user. A proper key derivation uses a secret master key combined with a random salt — never the user's name alone.*
