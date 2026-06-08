# Module 16: Asymmetric Cryptography

> Intermediate | 30 minutes | 4 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Distinguish public keys from private keys
- Trace textbook RSA encryption and decryption at a conceptual level
- Explain Diffie-Hellman shared secret agreement
- Recognize elliptic curve cryptography as group-based public-key cryptography

Reference sections: [RSA](https://cryptohack.gitbook.io/cryptobook/untitled/rsa-application), [Diffie-Hellman](https://cryptohack.gitbook.io/cryptobook/diffie-hellman)

---

## Lesson Flow

### 16.1 - Public and Private Keys

**Narrative**: Asymmetric cryptography uses different keys for different roles.

- The public key can be shared.
- The private key must remain secret.

This enables encryption to a recipient without first sharing a symmetric secret, and signatures that anyone can verify but only the private-key holder can create.

---

#### Activity 16.1a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: In a public-key encryption system, which key should remain secret?

**Options**:
- A) The public key
- B) The private key
- C) The ciphertext
- D) The modulus name

**Answer**: **B** - The private key is the secret key.

**Explanation**: The public key is designed to be distributed. The private key is what allows decryption or signing.

---

### 16.2 - Textbook RSA Shape

**Narrative**: In textbook RSA, the public key is typically `(n, e)` and the private key uses a secret exponent `d`.

```text
c = m^e mod n
m = c^d mod n
```

The modulus `n` is a product of large primes. Knowing the prime factors lets you compute the private exponent; not knowing them should make that infeasible at real sizes.

---

#### Activity 16.2a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: In textbook RSA, what does the public exponent `e` do?

**Options**:
- A) It encrypts by exponentiating the message modulo `n`
- B) It stores the plaintext
- C) It factors `n`
- D) It is the same value as the private exponent

**Answer**: **A** - Textbook RSA encryption computes `m^e mod n`.

**Explanation shown after answering**: Real RSA needs padding and careful implementation. The textbook equation explains the mathematical core, not a complete safe protocol.

---

### 16.3 - Diffie-Hellman

**Narrative**: Diffie-Hellman lets two parties derive the same shared secret across a public channel.

```text
public values: p, g
Alice private: a
Bob private: b

Alice sends A = g^a mod p
Bob sends B = g^b mod p

Alice computes B^a mod p
Bob computes A^b mod p
Both get g^(ab) mod p
```

An eavesdropper sees `p`, `g`, `A`, and `B`, but should not be able to compute the shared secret without solving discrete logs.

---

#### Activity 16.3a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Medium

**Prompt**: If Alice sends `A = g^a mod p` and Bob sends `B = g^b mod p`, both parties derive `g^__ mod p`.

**Expected Answer**: `ab`

**Acceptable variations**: `a*b`, `ba`, `b*a`

**Hint**: Alice raises Bob's public value to `a`; Bob raises Alice's public value to `b`.

**Explanation**: `(g^b)^a = g^(ba)` and `(g^a)^b = g^(ab)`. Multiplication of the exponents gives the same shared value.

---

### 16.4 - Elliptic Curve Cryptography

**Narrative**: Elliptic curve cryptography also uses a public group operation and a hard reverse problem.

Instead of powers like `g^a`, ECC often uses repeated point addition:

```text
Q = dG
```

`G` is a public base point, `d` is a private scalar, and `Q` is a public point. The hard problem is recovering `d` from `G` and `Q`.

---

#### Activity 16.4a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: In elliptic curve cryptography, what is usually hard for an attacker?

**Options**:
- A) Adding two public points once
- B) Recovering the private scalar from the base point and public point
- C) Reading a public key
- D) Checking whether two strings are equal

**Answer**: **B** - ECC relies on the elliptic curve discrete logarithm problem.

**Explanation**: The operation `Q = dG` is easy to compute, but recovering `d` from `G` and `Q` should be infeasible for well-chosen curves and key sizes.

---

### 16.5 - Why Padding Matters

**Narrative**: Textbook RSA is deterministic and algebraic. That makes it useful for learning, but unsafe as a real encryption scheme.

If the public exponent is small and the message is small enough, encryption may not wrap around the modulus:

```text
c = m^3 mod n
if m^3 < n, then c = m^3
```

In that case, the attacker can recover `m` by taking an integer cube root. Proper RSA encryption uses padding schemes such as OAEP to avoid this kind of structure.

---

#### Activity 16.5a - SPOT THE WEAKNESS

> **Type**: SPOT
> **Difficulty**: Medium

**Prompt**: Click the line that creates the textbook RSA low-exponent risk.

```python
n = public_modulus
e = 3
m = bytes_to_long(flag)
c = pow(m, e, n)
print(c)
```

**Answer**: Line 2

**Hint**: Look for the unusually small public exponent.

**Explanation**: `e = 3` is not automatically broken, but textbook RSA without padding can become vulnerable when the message is small enough.

---

### 16.6 - Man-in-the-Middle Intuition

**Narrative**: Diffie-Hellman by itself creates a shared secret, but it does not prove who is on the other side.

If an attacker can replace Alice's public value before Bob sees it, and replace Bob's public value before Alice sees it, the attacker can create two separate shared secrets:

```text
Alice <-> Attacker
Attacker <-> Bob
```

Real protocols authenticate the exchange with signatures, certificates, or pre-shared trust.

---

#### Activity 16.6a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: What is missing from plain Diffie-Hellman if Alice and Bob need to know who they are talking to?

**Options**:
- A) Authentication
- B) Modular multiplication
- C) A prime modulus
- D) A shared final value

**Answer**: **A** - Plain Diffie-Hellman needs authentication to stop active substitution attacks.

**Explanation**: Diffie-Hellman solves key agreement over a public channel, but active attackers require identity checks too.

---

## Module Summary

Asymmetric cryptography lets public information support private operations. RSA leans on factorization; Diffie-Hellman and ECC lean on discrete logarithm-style assumptions.
