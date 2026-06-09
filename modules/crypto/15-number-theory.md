# Module 15: Number Theory for Cryptography

> Intermediate | 25 minutes | 4 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Explain why primes and factorization matter in cryptography
- Use Euler's totient in small examples
- Apply Fermat and Euler style exponent rules conceptually
- Recognize the difference between easy multiplication and hard factorization

---

## Lesson Flow

### 15.1 - Primes and Factorization

**Narrative**: Multiplying primes is easy. Reversing that multiplication can be hard when the numbers are large.

```text
17 * 23 = 391
391 = 17 * 23
```

The second direction is factorization. Modern public-key cryptography often relies on choosing parameters so the forward direction is easy and the reverse direction is infeasible at real sizes.

---

#### Activity 15.1a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Easy

**Prompt**: Factor `91` into primes.

**Options**:
- A) `3 * 31`
- B) `7 * 13`
- C) `9 * 11`
- D) `2 * 45 + 1`

**Answer**: **B** - `7 * 13 = 91`, and both factors are prime.

**Explanation shown after answering**: Small examples are easy by trial division. Cryptographic moduli use numbers large enough that naive trial division is not practical.

---

### 15.2 - Totients

**Narrative**: Euler's totient `phi(n)` counts how many integers from `1` to `n` are coprime to `n`.

For a prime `p`:

```text
phi(p) = p - 1
```

For two distinct primes `p` and `q`:

```text
phi(pq) = (p - 1)(q - 1)
```

This matters because RSA private exponents are built using `phi(n)` or a related value.

---

#### Activity 15.2a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Medium

**Prompt**: If `n = 5 * 11`, what is `phi(n)`?

**Expected Answer**: `40`

**Acceptable variations**: `(5-1)*(11-1)`, `4*10`

**Hint**: For distinct primes, use `(p - 1)(q - 1)`.

**Explanation**: `phi(55) = (5 - 1)(11 - 1) = 4 * 10 = 40`.

---

### 15.3 - Modular Exponents

**Narrative**: Cryptographic systems often compute powers modulo a number:

```text
c = m^e mod n
```

The result is reduced after division by `n`. Efficient algorithms do not compute the giant power first; they reduce throughout the exponentiation.

```text
3^4 mod 7 = 81 mod 7 = 4
```

---

#### Activity 15.3a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: What is `2^5 mod 13`?

**Options**:
- A) `5`
- B) `6`
- C) `7`
- D) `8`

**Answer**: **B** - `2^5 = 32`, and `32 mod 13 = 6`.

**Explanation**: Modular exponentiation is the workhorse behind RSA, Diffie-Hellman, and many signature systems.

---

### 15.4 - Hard Problems

**Narrative**: Cryptosystems are designed around problems that are easy in one direction and hard in another.

| Easy direction | Hard direction |
|----------------|----------------|
| Multiply primes | Factor the product |
| Compute `g^a mod p` | Recover `a` from `g` and `g^a` |

The second hard direction is the discrete logarithm problem.

---

#### Activity 15.4a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: Which problem is the discrete logarithm problem?

**Options**:
- A) Given `g` and `a`, compute `g^a mod p`
- B) Given `g`, `p`, and `g^a mod p`, recover `a`
- C) Given `p`, list all integers less than `p`
- D) Given a ciphertext, guess whether it is ASCII

**Answer**: **B** - Discrete log asks for the exponent that produced a public modular power.

**Explanation**: Diffie-Hellman relies on exponentiation being easy and reversing the exponent being hard in the chosen group.

---

### 15.5 - Modular Inverses

**Narrative**: A modular inverse solves:

```text
a * x == 1 (mod n)
```

For example, `3 inverse mod 11` is `4` because:

```text
3 * 4 = 12 == 1 (mod 11)
```

In RSA, the private exponent is chosen so it inverts the public exponent modulo a totient-related value.

---

#### Activity 15.5a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Medium

**Prompt**: Find the inverse of `3 mod 11`.

**Expected Answer**: `4`

**Acceptable variations**: `04`, `3^-1 = 4`

**Hint**: Find `x` such that `3x` leaves remainder `1` when divided by `11`.

**Explanation**: `3 * 4 = 12`, and `12 mod 11 = 1`.

---

### 15.6 - Spotting Factorization Leaks

**Narrative**: If two RSA moduli accidentally share a prime, `gcd(n1, n2)` reveals that shared factor.

```python
n1 = p * q1
n2 = p * q2
shared = gcd(n1, n2)
```

This is why good randomness is essential when generating primes. Reusing a prime destroys the assumption that `n` is hard to factor.

---

#### Activity 15.6a - SPOT THE LEAK

> **Type**: SPOT
> **Difficulty**: Medium

**Prompt**: Click the line that reveals the shared RSA prime.

```python
from math import gcd
n1 = 11413
n2 = 14039
shared = gcd(n1, n2)
print(shared)
```

**Answer**: Line 4

**Hint**: Look for the operation that compares both moduli mathematically.

**Explanation**: `gcd(n1, n2)` reveals any shared prime factor. If the result is larger than `1`, both moduli are compromised.

---

## Module Summary

Number theory gives cryptography its trapdoors and hard problems: primes, coprimality, modular exponents, factorization, and discrete logarithms.
