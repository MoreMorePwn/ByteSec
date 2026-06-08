# Module 01: Encoding & XOR Basics

> ⭐ Beginner | ⏱️ 20 minutes | 5 activities

---

## Learning Objectives
By the end of this module, students will be able to:
- Distinguish encoding from encryption
- Recognize and decode common encodings (hex, base64, binary)
- Understand XOR as a fundamental cryptographic operation
- Perform single-byte XOR decryption manually

---

## Lesson Flow

### 1.1 — Encoding vs. Encryption

**Narrative**: *A common beginner mistake is confusing encoding with encryption. The difference is critical:*

| | Encoding | Encryption |
|---|---|---|
| **Purpose** | Data representation | Data secrecy |
| **Key required?** | No | Yes |
| **Reversible without key?** | Yes (trivially) | No (computationally) |
| **Examples** | Base64, HEX, ASCII, URL encoding | AES, RSA, ChaCha20 |

**Encoding is NOT security.** Base64 doesn't hide anything — anyone can decode it instantly. Encryption, when done correctly, requires a secret key to reverse.

**Common CTF patterns:**
- Strings ending with `=` or `==` → base64
- Strings with only `0-9` and `a-f` → hex
- Strings with `%20` or `%3D` → URL encoding
- Strings looking like `...-...-...` → UUID or base58

---

#### 🧪 Activity 1.1a — PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Easy

**Prompt**: You find this string in a binary: `QlRGU1R7dzNjMG1lXzBfYzBkM30=`

Is this encrypted or encoded? What's the first step?

**Options**:
- A) It's encrypted with AES — we need a key
- B) It's base64 (the `=` padding gives it away) — decode it ✅
- C) It's a random string — ignore it
- D) It's binary data — run it as a program

**Answer**: **B** — The trailing `=` is characteristic of base64 padding.

**Explanation shown after answering**: *Base64 uses `=` as padding characters. Any string ending in `=` is almost certainly base64-encoded data. Decoding it reveals: `BTFST{...}`. The content might still be encoded inside, but the outer layer is base64.*

---

### 1.2 — Hexadecimal & Binary

**Narrative**: *Hex (base-16) is the most common way to represent binary data in a human-readable form. Each byte (8 bits) is represented by two hex characters — `0x00` through `0xFF`.*

**Quick conversions:**

| Binary | Hex | Decimal |
|--------|-----|---------|
| 0000 | 0 | 0 |
| 0001 | 1 | 1 |
| ... | ... | ... |
| 1001 | 9 | 9 |
| 1010 | A | 10 |
| 1011 | B | 11 |
| 1100 | C | 12 |
| 1101 | D | 13 |
| 1110 | E | 14 |
| 1111 | F | 15 |

**Example**: `0x41` = 65 decimal = 'A' in ASCII. `0x61` = 97 decimal = 'a' in ASCII.

**In CTFs**, hex-encoded data often looks like: `424954455345437b6833785f31735f663435745d7d`

Decoding: convert each pair to a byte → read as ASCII.

---

#### 🧪 Activity 1.2a — FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Easy

**Prompt**: The hex string `48656C6C6F` decodes to an ASCII string. What is it?

(Write just the decoded word, no quotes or punctuation.)

**Expected Answer**: `Hello`

**Acceptable variations**: `hello`

**Hint (shown after 1 failed attempt)**: *48 = H, 65 = e, 6C = l, 6C = l, 6F = o. Use an ASCII table.*

**Explanation**: *Each hex pair represents one ASCII character: 0x48 = 'H', 0x65 = 'e', 0x6C = 'l', 0x6C = 'l', 0x6F = 'o'. Concatenated: "Hello".*

---

### 1.3 — XOR: The Crypto Swiss Army Knife

**Narrative**: *XOR (exclusive OR, represented by `^` or `⊕`) is the single most important operation in cryptography. It has three magical properties:*

| A | B | A ⊕ B |
|---|---|--------|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

**Key properties:**

1. **Self-inverse**: `A ⊕ B ⊕ B = A` (XOR twice with the same value undoes itself)
2. **Commutative**: `A ⊕ B = B ⊕ A`
3. **Identity**: `A ⊕ 0 = A`

**Because XOR is self-inverse, it's perfect for both encryption AND decryption with the same operation:**

```python
plaintext = "HELLO"
key = 0x42
ciphertext = bytes(b ^ key for b in plaintext.encode())
decrypted = bytes(b ^ key for b in ciphertext)
print(decrypted.decode())  # HELLO
```

---

#### 🧪 Activity 1.3a — MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: If `ciphertext = flag XOR key` and you know the plaintext starts with "BYTESEC{", how can you recover the first 8 bytes of the key?

**Options**:
- A) XOR the ciphertext with "BYTESEC{" ✅
- B) You cannot recover the key without brute force
- C) Base64-decode the ciphertext
- D) Hash the ciphertext with MD5

**Answer**: **A** — Since XOR is self-inverse, `key = ciphertext XOR known_plaintext`.

**Explanation shown after answering**: *If `c = p ⊕ k`, then `k = c ⊕ p`. This is how known-plaintext attacks work against XOR-based encryption. If you know any segment of the plaintext, you can recover the corresponding key bytes. This is why repeating-key XOR (Vigenère-like) is vulnerable when you have known plaintext.*

---

### 1.4 — Single-Byte XOR Decryption

**Narrative**: *Single-byte XOR encrypts each byte with the same key byte. It's trivially breakable — there are only 256 possible keys (0-255). Brute force each one and look for readable English text.*

```python
cipher = bytes.fromhex("1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736")
for key in range(256):
    decrypted = bytes(b ^ key for b in cipher)
    try:
        text = decrypted.decode("ascii")
        if text.isprintable() and ' ' in text:
            print(f"Key {key:02x}: {text}")
    except:
        pass
```

**Score each decryption by English letter frequency** to automatically find the correct key without manual inspection.

**Letter frequency in English:** `ETAOIN SHRDLU...` (E is most common, then T, A, etc.)

---

#### 🧪 Activity 1.4a — PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: You try all 256 keys on a single-byte XOR ciphertext. For key `0x13`, the decrypted text is `"Cooking MC's like a pound of bacon"`. For key `0x42`, the decrypted text is `"㪘㫋㪃㪏㪎㪉㫍㫃㪌㪏㪞㫆㪌㫏㪍"`. For key `0x69`, the decrypted text is `"xqnlhl!iv&afp!pkzx!xk!qwlc!ut!ywml"`. Which key is correct?

**Options**:
- A) 0x13 ✅
- B) 0x42
- C) 0x69
- D) All of them

**Answer**: **A** — Only key 0x13 produces readable English text.

**Explanation shown after answering**: *When brute-forcing single-byte XOR, almost all keys produce garbage. The correct key produces a coherent English sentence. This is known as the "Cooking MC's" example from Matasano's crypto challenges — it's a classic test case.*

---

### 1.5 — Multi-Byte XOR (Repeating Key)

**Narrative**: *Instead of one key byte, what if the key is multiple bytes that repeat? This is "repeating-key XOR" (similar to Vigenère for bytes instead of letters).*

```python
def repeating_key_xor(text, key):
    result = bytearray()
    for i, byte in enumerate(text):
        result.append(byte ^ key[i % len(key)])
    return bytes(result)
```

**Breaking repeating-key XOR** requires two steps:
1. **Find the key length** — try different lengths and look for the one where the same key byte hits the same positions
2. **Break each position** as single-byte XOR (since the same key byte is used at positions 0, N, 2N, 3N, etc.)

---

#### 🧪 Activity 1.5a — MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: A ciphertext was encrypted with repeating-key XOR using a 3-byte key. How many single-byte XOR sub-problems do you need to solve?

**Options**:
- A) 1
- B) 3 ✅
- C) 256
- D) It depends on the message length

**Answer**: **B** — 3 sub-problems, one for each key byte position.

**Explanation shown after answering**: *If the key is 3 bytes (`K0, K1, K2`), then every 3rd byte is XORed with `K0`, every 3rd+1 byte with `K1`, and every 3rd+2 byte with `K2`. Each of these 3 groups is a single-byte XOR problem that can be brute-forced independently using frequency analysis.*
