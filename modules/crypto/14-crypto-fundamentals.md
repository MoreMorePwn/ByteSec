# Module 14: Crypto Fundamentals

> Beginner | 20 minutes | 4 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Interpret common mathematical notation used in cryptography
- Explain divisibility, quotient, remainder, and greatest common divisor
- Use modular arithmetic as arithmetic on remainders
- Recognize why correctness matters for encryption and decryption

Reference section: [CryptoBook Fundamentals](https://cryptohack.gitbook.io/cryptobook/fundamentals/notation)

---

## Lesson Flow

### 14.1 - Reading Crypto Notation

**Narrative**: Cryptography uses compact notation because protocols combine algebra, probability, and algorithms. The notation is not decoration: it tells you what kind of object you are manipulating.

Common symbols:

| Symbol | Meaning |
|--------|---------|
| `Z` | integers |
| `N` | non-negative integers |
| `a in S` | `a` is an element of set `S` |
| `forall` | for every |
| `exists` | there exists |
| `mod n` | work with remainders after division by `n` |

When solving CTF crypto, first identify the object type: integer, byte string, residue class, key, ciphertext, or group element.

---

#### Activity 14.1a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: In cryptographic notation, what does `a in Z` usually mean?

**Options**:
- A) `a` is an integer
- B) `a` is encrypted
- C) `a` is a byte array
- D) `a` is a public key

**Answer**: **A** - `Z` denotes the integers, so `a in Z` means `a` is an integer.

**Explanation**: Before computing anything, identify the mathematical domain. Integer arithmetic, byte arithmetic, and modular arithmetic have different rules.

---

### 14.2 - Division and GCD

**Narrative**: Division gives a quotient and a remainder:

```text
a = qn + r
```

The greatest common divisor `gcd(a, b)` is the largest integer that divides both `a` and `b`. In cryptography, `gcd` tells you when a modular inverse exists.

```text
gcd(21, 14) = 7
gcd(17, 12) = 1
```

When `gcd(a, n) = 1`, `a` is invertible modulo `n`.

---

#### Activity 14.2a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Easy

**Prompt**: What is `gcd(30, 18)`?

**Options**:
- A) `2`
- B) `3`
- C) `6`
- D) `12`

**Answer**: **C** - The common divisors include `1, 2, 3, 6`, and the greatest one is `6`.

**Explanation shown after answering**: `gcd` is a quick way to detect shared factors. In RSA-style problems, an unexpected shared factor can break a modulus.

---

### 14.3 - Modular Arithmetic

**Narrative**: Working modulo `n` means values that differ by a multiple of `n` are treated as equivalent.

```text
17 mod 5 = 2
17 == 2 (mod 5)
```

Addition and multiplication still work, but results are reduced back into the range of possible remainders.

```text
8 + 9 == 17 == 2 (mod 5)
8 * 9 == 72 == 2 (mod 5)
```

---

#### Activity 14.3a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Easy

**Prompt**: Compute `29 mod 7`.

**Expected Answer**: `1`

**Acceptable variations**: `01`, `29 = 1 mod 7`

**Hint**: Find the remainder after dividing `29` by `7`.

**Explanation**: `7 * 4 = 28`, so the remainder is `1`.

---

### 14.4 - Correctness

**Narrative**: A cryptographic encryption scheme must be correct: decrypting a valid ciphertext with the matching key should recover the original message.

```text
Dec(Enc(m, k), k) = m
```

Security asks what an attacker can learn. Correctness asks whether the intended receiver can recover the message at all.

---

#### Activity 14.4a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: What does correctness require for an encryption scheme?

**Options**:
- A) Ciphertexts must always be shorter than plaintexts
- B) Decrypting a valid encryption with the matching key recovers the message
- C) The public key must stay secret
- D) The same plaintext must always produce the same ciphertext

**Answer**: **B** - Correctness means legitimate encryption and decryption compose back to the original message.

**Explanation**: A scheme can be mathematically interesting but useless if legitimate receivers cannot reliably decrypt.

---

### 14.5 - Euclidean Algorithm Intuition

**Narrative**: The Euclidean algorithm computes `gcd(a, b)` by repeatedly replacing the larger number with a remainder.

```text
gcd(252, 105)
252 = 2 * 105 + 42
105 = 2 * 42 + 21
42 = 2 * 21 + 0
gcd(252, 105) = 21
```

This matters because modular inverses are built from the same idea. If `gcd(a, n) = 1`, then there are integers `x` and `y` such that:

```text
ax + ny = 1
```

Reducing that equation modulo `n` gives:

```text
ax == 1 (mod n)
```

So `x` is an inverse of `a` modulo `n`.

---

#### Activity 14.5a - SPOT THE STEP

> **Type**: SPOT
> **Difficulty**: Medium

**Prompt**: Click the line where the Euclidean algorithm reaches the final nonzero remainder.

```text
gcd(252, 105)
252 = 2 * 105 + 42
105 = 2 * 42 + 21
42 = 2 * 21 + 0
gcd(252, 105) = 21
```

**Answer**: Line 3

**Hint**: The final nonzero remainder appears one line before the remainder becomes zero.

**Explanation**: Line 3 shows remainder `21`. The next division has remainder `0`, so `21` is the GCD.

---

### 14.6 - Bytes, Integers, and Encodings

**Narrative**: CTF crypto often moves between bytes and integers.

```python
message = b"BY"
as_int = int.from_bytes(message, "big")
back = as_int.to_bytes(2, "big")
```

The bytes `b"BY"` are hexadecimal `42 59`, so the big-endian integer is:

```text
0x4259 = 16985
```

When a challenge gives a huge RSA integer, it may simply be a byte string interpreted as a number.

---

#### Activity 14.6a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: What integer does the byte string `b"A"` become in big-endian form?

**Options**:
- A) `1`
- B) `41`
- C) `65`
- D) `97`

**Answer**: **C** - ASCII `A` is decimal `65`, or hex `0x41`.

**Explanation shown after answering**: Crypto challenges frequently encode text as integers before applying modular arithmetic. Always identify the encoding step.

---

## Module Summary

Crypto starts with precise objects and operations. Know the set, know the modulus, know when inverses exist, and always separate correctness from security.
