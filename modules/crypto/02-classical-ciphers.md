# Module 02: Classical Ciphers

> ⭐ Beginner | ⏱️ 20 minutes | 5 activities

---

## Learning Objectives
By the end of this module, students will be able to:
- Identify and break a Caesar cipher by brute force
- Understand how substitution ciphers work
- Apply frequency analysis to crack simple substitution
- Recognize the Vigenère cipher structure

---

## Lesson Flow

### 2.1 — Caesar Cipher

**Narrative**: *The Caesar cipher shifts each letter by a fixed number of positions. Julius Caesar used a shift of 3: A → D, B → E, ..., Z → C.*

```
Plain:   ABCDEFGHIJKLMNOPQRSTUVWXYZ
Shift 3: DEFGHIJKLMNOPQRSTUVWXYZABC

"HELLO" → "KHOOR"
```

**Breaking Caesar is trivial:** There are only 25 possible shifts (excluding shift 0). Try all of them — one will produce readable text.

| Shift | Output |
|-------|--------|
| 0 | `FRZDUGV RI WKH ILQDO FKIWHU` |
| 1 | `EQYCTFU ...` |
| ... | ... |
| 3 | `DOBTAST ...` |
| ... | ... |
| 16 | `THE QUICK BROWN FOX JUMPS` ✅ |

---

#### 🧪 Activity 2.1a — MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Easy

**Prompt**: A message is Caesar-ciphered: `WKH HDJOH LV IOLJK`. What is the original text?

**Options**:
- A) `THE EAGLE IS FLYING` — shift 3 ✅
- B) `THE HAWK IS SOARING` — shift 5
- C) `THE BIRD IS FLYING` — shift 7
- D) `WOLF EAGLE IS FLY` — shift 0

**Answer**: **A** — Shift back by 3: W→T, K→H, H→E, etc.

**Explanation shown after answering**: *Caesar cipher with shift 3. Reverse by shifting each letter backward by 3: W(23) → T(20), K(11) → H(8), H(8) → E(5). The full message is "THE EAGLE IS FLYING".*

---

### 2.2 — Substitution Ciphers

**Narrative**: *Unlike Caesar (which has a single, predictable shift), a substitution cipher uses a random permutation of the alphabet. Each letter maps to exactly one other letter.*

```
a→q, b→z, c→w, d→s, e→x, f→e, g→d, h→c, i→r, j→f, k→v, l→b, m→g,
n→t, o→y, p→h, q→n, r→u, s→m, t→j, u→i, v→k, w→o, x→p, y→l, z→a
```

**Key space**: 26! ≈ 4×10²⁶ — impossible to brute force by hand. But we can use **frequency analysis**.

**English letter frequency (descending):**
```
E T A O I N S H R D L C U M W F G Y P B V K J X Q Z
```

If `X` appears most frequently in a ciphertext, it likely substitutes for `E`. Then the second most common likely corresponds to `T`, and so on.

---

#### 🧪 Activity 2.2a — FILL IN THE BLANK

> **Type**: FITB
> **Difficulty**: Medium

**Prompt**: In a long substitution ciphertext, the character `Q` appears 142 times, `Z` appears 98 times, `M` appears 87 times, and `F` appears 6 times. Based on English letter frequency, `Q` most likely substitutes for which letter?

**Expected Answer**: `E`

**Acceptable variations**: `e`, `E`

**Hint (shown after 1 failed attempt)**: *The most common letter in English is E. The most common character in the ciphertext is Q.*

**Explanation**: *In any reasonably long English text, 'E' is by far the most common letter (~12.7% of all letters). The ciphertext character that appears most frequently is almost certainly a substitution for 'E'.*

---

### 2.3 — Frequency Analysis in Practice

**Narrative**: *Frequency analysis works because English has a statistical fingerprint. Beyond individual letters, you can look at:*

**Common digrams (2-letter pairs):** `TH`, `HE`, `IN`, `ER`, `AN`, `RE`, `ED`, `ON`, `ES`, `ST`
**Common trigrams (3-letter groups):** `THE`, `ING`, `AND`, `HER`, `ERE`, `ENT`, `THA`, `NTH`, `WAS`
**Common words:** `THE`, `AND`, `THAT`, `HAVE`, `WAS`, `FOR`, `NOT`, `ARE`, `WITH`, `YOU`

**Practical approach:**
1. Count letter frequencies in ciphertext
2. Assume the most frequent = E, second = T, third = A
3. Try those substitutions — see if words emerge
4. Look for `THE` pattern (T??E → if ? is H, it forms a common word)
5. Iteratively refine

---

#### 🧪 Activity 2.3a — PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: In a substitution ciphertext, you see the sequence `XQZ` appear 5 times. You suspect it's the word `THE`. What does this tell you about the substitution mapping?

**Options**:
- A) X→T, Q→H, Z→E ✅
- B) X→H, Q→E, Z→T
- C) X→T, Q→E, Z→H
- D) Cannot determine without more data

**Answer**: **A** — `XQZ` mapping to `THE` means X→T, Q→H, Z→E.

**Explanation shown after answering**: *The three most common letters in English appearing as `THE` is a powerful crib. Since `XQZ` appears repeatedly, and `THE` is the most common English trigram, it's a strong statistical signal. This gives us three substitutions at once: X→T, Q→H, Z→E. These become anchors for the rest of the decryption.*

---

### 2.4 — Vigenère Cipher

**Narrative**: *The Vigenère cipher uses a keyword to apply different Caesar shifts to each letter. It's "polyalphabetic" — the same plaintext letter can encrypt to different ciphertext letters depending on position.*

```
Key:     KEYKEYKEYKEY...
Plain:   ATTACKATDAWN
Cipher:  KXVTTPKXETKE?
```

**How it works:** For each position, the key letter determines the shift. A=shift 0, B=shift 1, ..., Z=shift 25.

| Pos | Plain | Key | Shift | Cipher |
|-----|-------|-----|-------|--------|
| 0 | A | K (10) | 10 | K |
| 1 | T | E (4) | 4 | X |
| 2 | T | Y (24) | 24 | T (going backwards) |

**Breaking Vigenère:**
1. **Find key length** — use Kasiski examination (repeated trigrams) or index of coincidence
2. **Split into groups** — position 0, K, 2K, 3K... use same key byte
3. **Solve each group as Caesar cipher** (frequency analysis on each)

---

#### 🧪 Activity 2.4a — MULTIPLE CHOICE

> **Type**: MC
> **Difficulty**: Medium

**Prompt**: A Vigenère cipher uses a 4-letter key. After splitting the ciphertext into 4 groups (every 4th letter starting from offset 0, 1, 2, 3), you analyze group 0 and find that shifting all letters in group 0 backward by 17 produces English text. What is the first byte of the key?

**Options**:
- A) Q (the 17th letter)
- B) R (the 18th letter) ✅
- C) S (the 19th letter)
- D) Cannot determine

Wait — let me think. In Vigenère, the shift value is the key letter's position. If the best shift is 17, that means the key letter at that position has value 17. Letter with value 17 (0-indexed) is R (A=0, B=1, ..., R=17).

So the answer is R.

**Answer**: **B** — shift of 17 = key letter R.

**Explanation shown after answering**: *In Vigenère, the key determines the shift: A=0, B=1, ..., R=17, ..., Z=25. If the optimal Caesar shift for group 0 is 17 (meaning we shift group 0 backward by 17 to get English), then the key byte at position 0 is the letter corresponding to Caesar shift 17, which is 'R'.*

---

#### 🧪 Activity 2.5a — PREDICT THE OUTPUT

> **Type**: PREDICT
> **Difficulty**: Medium

**Prompt**: What makes Vigenère harder to break than a simple substitution cipher?

**Options**:
- A) It uses a longer alphabet
- B) The same plaintext letter can map to different ciphertext letters ✅
- C) It cannot be broken by computers
- D) It doesn't use letters

**Answer**: **B** — Vigenère is polyalphabetic; the same plaintext letter encrypts differently depending on position.

**Explanation shown after answering**: *With simple substitution, 'e' always encrypts to the same letter — frequency analysis works directly. With Vigenère, 'e' encrypts to different letters depending on the key letter at that position. This flattens the frequency distribution, which is why we must first find the key length before applying standard frequency analysis to each group independently.*
