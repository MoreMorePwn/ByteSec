# Module 17: Symmetric Cryptography

> Intermediate | 25 minutes | 4 activities

---

## Learning Objectives

By the end of this module, students will be able to:

- Define symmetric encryption as shared-key encryption
- Explain one-time pad correctness and the danger of key reuse
- Recognize AES as a block cipher over 16-byte blocks
- Identify why block cipher modes and nonces matter

Reference sections: [Symmetric Encryption](https://cryptohack.gitbook.io/cryptobook/symmetric-cryptography/encryption), [One Time Pad](https://cryptohack.gitbook.io/cryptobook/symmetric-cryptography/the-one-time-pad), [AES](https://cryptohack.gitbook.io/cryptobook/symmetric-cryptography/aes)

---

## Lesson Flow

### 17.1 - Shared-Key Encryption

**Narrative**: Symmetric encryption uses the same secret key for encryption and decryption.

```text
c = Enc(m, k)
m = Dec(c, k)
```

The sender and receiver must both know `k`. Anyone who learns `k` can decrypt messages protected by that key.

---

#### Activity 17.1a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: What makes an encryption scheme symmetric?

**Options**:
- A) It uses the same shared secret key for encryption and decryption
- B) It has no key
- C) It uses a public key for everyone
- D) It only works for prime numbers

**Answer**: **A** - Symmetric encryption is shared-key encryption.

**Explanation**: Symmetric crypto is fast and widely used, but the parties need a secure way to agree on or transport the key.

---

### 17.2 - One-Time Pad and XOR

**Narrative**: A one-time pad can be expressed with XOR:

```text
c = m xor k
m = c xor k
```

This works because XOR cancels itself:

```text
x xor y xor y = x
```

The security requirement is strict: the key must be random, as long as the message, and never reused.

---

#### Activity 17.2a - PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Easy

**Prompt**: If `c = m xor k`, how do you recover `m` when you know `k`?

**Options**:
- A) `m = c xor k`
- B) `m = c + k`
- C) `m = c * k`
- D) `m = k - c`

**Answer**: **A** - XORing the ciphertext with the same key recovers the message.

**Explanation shown after answering**: XOR is its own inverse. This is why the same operation can encrypt and decrypt in XOR-based schemes.

---

### 17.3 - Key Reuse

**Narrative**: Reusing a one-time pad key is catastrophic.

```text
c1 = m1 xor k
c2 = m2 xor k
c1 xor c2 = m1 xor m2
```

The key cancels out, leaking a relationship between the two plaintexts. In CTFs, repeated-key XOR often becomes a crib-dragging or frequency-analysis problem.

---

#### Activity 17.3a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: Why is one-time pad key reuse dangerous?

**Options**:
- A) It makes the ciphertext longer
- B) It lets attackers cancel the key by XORing ciphertexts together
- C) It turns XOR into addition
- D) It prevents the receiver from decrypting

**Answer**: **B** - If two ciphertexts use the same XOR pad, XORing them cancels the key.

**Explanation**: Perfect secrecy depends on one-time use. Reuse changes the problem from impossible to attackable.

---

### 17.4 - AES and Blocks

**Narrative**: AES is a block cipher. It transforms one 16-byte block at a time using a secret key.

For longer messages, a mode of operation defines how blocks are chained or combined with counters/nonces.

Inside AES, rounds mix the state using transformations such as adding round keys, substituting bytes, shifting rows, and mixing columns. For CTF basics, remember:

- AES block size is 16 bytes.
- Key size can be 128, 192, or 256 bits.
- Modes and nonce handling are part of safe use.

---

#### Activity 17.4a - FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Easy

**Prompt**: AES encrypts one block of ______ bytes at a time.

**Expected Answer**: `16`

**Acceptable variations**: `sixteen`, `16 bytes`

**Hint**: AES state is commonly represented as a 4 by 4 matrix of bytes.

**Explanation**: AES has a fixed 16-byte block size. Long messages require a mode of operation.

---

### 17.5 - Modes and Nonces

**Narrative**: A block cipher only encrypts one block. A mode of operation turns that block cipher into a scheme for longer messages.

Some modes use a nonce or IV. The rules depend on the mode, but a common CTF lesson is:

- Never reuse a stream/counter nonce with the same key.
- Never assume ECB hides repeated plaintext blocks.
- Always authenticate ciphertexts in real protocols.

CTR mode is especially close to a stream cipher:

```text
keystream = AES_k(nonce || counter)
ciphertext = plaintext xor keystream
```

If the same nonce and key generate the same keystream twice, the attack resembles repeated one-time pad reuse.

---

#### Activity 17.5a - SPOT THE MISUSE

> **Type**: SPOT
> **Difficulty**: Medium

**Prompt**: Click the line that causes nonce reuse with the same key.

```python
key = load_secret_key()
nonce = b"fixed-fixed-1234"
c1 = aes_ctr_encrypt(key, nonce, message1)
c2 = aes_ctr_encrypt(key, nonce, message2)
```

**Answer**: Line 4

**Hint**: The problem appears when the same key and nonce are used again.

**Explanation**: Line 4 repeats the same key and nonce pair, producing the same keystream pattern for a different message.

---

### 17.6 - ECB Pattern Leakage

**Narrative**: Electronic Codebook mode encrypts each block independently:

```text
C_i = AES_k(P_i)
```

That means equal plaintext blocks become equal ciphertext blocks. ECB may hide the bytes, but it can leak structure.

---

#### Activity 17.6a - MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: Why does ECB mode leak patterns?

**Options**:
- A) Equal plaintext blocks encrypt to equal ciphertext blocks under the same key
- B) It uses no key
- C) AES has no rounds in ECB mode
- D) It only supports one-byte messages

**Answer**: **A** - ECB applies the same block permutation independently to every block.

**Explanation**: ECB can reveal repeated structure even when the individual block contents are not directly readable.

---

## Module Summary

Symmetric cryptography is fast and practical, but it is unforgiving about key handling. One-time pads require one-time keys; AES requires correct modes and nonce discipline.
