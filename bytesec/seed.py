"""Seed ByteSec content from markdown curricula under modules/."""

import json
import re
from pathlib import Path

from . import db
from .models import Lesson, LessonStep, Module, User, UserProgress


ROOT_DIR = Path(__file__).resolve().parents[1]
CURRICULUM_ROOT = ROOT_DIR / "modules"
SQLI_MODULE_DIR = CURRICULUM_ROOT / "sqli"
RE_ASM_MODULE_DIR = CURRICULUM_ROOT / "reverse-engineering-assembly"
CRYPTO_MODULE_DIR = CURRICULUM_ROOT / "crypto"
PWN_MODULE_DIR = CURRICULUM_ROOT / "pwn"
SQLI_CTF_CHALLENGE_URL = "http://127.0.0.1:8004"
PWN_RET2WIN_ENDPOINT = "nc 127.0.0.1 9001"
SQLI_CTF_FLAG_HASH = "84f61f593ff27ff39777cfb98bf90598848c1bc9533e75bf8ee54b964b876ba9"
RE_ASM_CTF_FLAG_HASH = "57f7e67a47b26bc59fab7e5f4807ffeba2edce17ce39540e6395caf4ef9d1a2a"
CRYPTO_RSA_CTF_FLAG_HASH = "cc50860a061bc2af278112f0ebc8f347e27bf97a12c792e66082b68010de036a"
PWN_RET2WIN_CTF_FLAG_HASH = "8e7a8ab5ef6c8d0ffd605d16b6112704d0e493070046d4b382895fa722965587"


def _j(obj):
    return json.dumps(obj)


USERS_TABLE = _j({
    "columns": ["id", "username", "password", "email", "role"],
    "rows": [
        [1, "alice", "s3cur3!", "alice@mail.com", "admin"],
        [2, "bob", "pass123", "bob@mail.com", "user"],
        [3, "charlie", "qwerty", "charlie@mail.com", "user"],
        [4, "diana", "hunter2", "diana@mail.com", "moderator"],
    ],
})


ICONS = {
    1: "database",
    2: "language",
    3: "terminal",
    4: "category",
    5: "bug_report",
    6: "shield",
    7: "emoji_events",
    8: "flag",
    9: "memory",
    10: "account_tree",
    11: "data_object",
    12: "travel_explore",
    13: "flag",
    14: "vpn_key",
    15: "functions",
    16: "key",
    17: "lock",
    18: "flag",
    19: "memory",
    20: "stacked_line_chart",
    21: "terminal",
    22: "shield",
    23: "flag",
}


DESCRIPTIONS = {
    1: "Write basic SELECT and WHERE queries, then see why string concatenation creates SQL injection risk.",
    2: "Trace input from browser to database and identify the trust boundary where user data becomes dangerous.",
    3: "Craft authentication bypass payloads, use SQL comments, and test whether a field is injectable.",
    4: "Classify in-band, blind, and out-of-band SQL injection techniques and choose the right workflow.",
    5: "Enumerate database metadata, extract target data, and reason about second-order injection.",
    6: "Apply parameterized queries, validation, least privilege, and defense-in-depth against SQL injection.",
    7: "Analyze real breaches and complete the final SQL injection assessment.",
    8: "Solve the local EzSQLi CTF challenge and submit the recovered flag.",
    9: "Read x86-64 registers, operands, comparisons, and common compiler idioms used in reverse engineering.",
    10: "Trace stack behavior, calls, returns, and Linux x86-64 function argument registers.",
    11: "Follow branch logic, byte loops, memory operands, and XOR-encoded data checks.",
    12: "Use static triage and byte-level reasoning to reverse a small flag checker workflow.",
    13: "Recover and submit the flag from a local XOR flag-checker binary.",
    14: "Read cryptographic notation, compute GCDs and residues, and distinguish correctness from security.",
    15: "Use primes, factorization, totients, modular exponents, and hard-problem intuition.",
    16: "Trace public-key ideas through RSA, Diffie-Hellman, and elliptic-curve style groups.",
    17: "Reason about shared-key encryption, one-time pads, XOR reuse, AES blocks, and modes.",
    18: "Recover a flag from a textbook RSA low-exponent challenge.",
    19: "Connect registers, virtual memory, stack frames, and return addresses to binary exploitation.",
    20: "Explain stack buffer overflows, crash behavior, endianness, and offset discovery.",
    21: "Build a ret2win exploit payload from a known offset and a fixed function address.",
    22: "Reason about stack canaries, NX, PIE, ASLR, RELRO, leaks, and ROP follow-up paths.",
    23: "Exploit a containerized ret2win service and submit the recovered flag.",
}


LESSON_RE = re.compile(r"^###\s+(\d+)\.(\d+)\s+[-\u2013\u2014]\s+(.+?)\s*$", re.MULTILINE)
ACTIVITY_RE = re.compile(r"^####\s+(.*?Activity.+?)\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"^\*\*(.+?)\*\*:\s*(.*)$")
CODE_RE = re.compile(r"```([A-Za-z0-9_-]*)\n(.*?)\n```", re.DOTALL)
OPTION_RE = re.compile(r"^-\s*([A-Z])\)\s*(.+?)\s*$")


def _clean(value):
    value = value or ""
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def _plain(value):
    value = re.sub(r"`([^`]+)`", r"\1", value or "")
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = value.replace("\u2705", "")
    return value.strip()


def _module_files():
    files = []
    for module_dir in (SQLI_MODULE_DIR, RE_ASM_MODULE_DIR, CRYPTO_MODULE_DIR, PWN_MODULE_DIR):
        if not module_dir.exists():
            continue
        files.extend(
            path
            for path in module_dir.glob("[0-9][0-9]-*.md")
            if not path.name.startswith("00-")
        )
    return sorted(files, key=_module_file_sort_key)


def _module_file_sort_key(path):
    match = re.match(r"^([0-9]{2})-", path.name)
    order = int(match.group(1)) if match else 999
    return order, str(path)


def _expected_module_count():
    ctf_count = 4
    return len(_module_files()) + ctf_count


def _module_meta(text, fallback_order):
    heading = re.search(r"^#\s+Module\s+(\d+):\s+(.+?)\s*$", text, re.MULTILINE)
    order = int(heading.group(1)) if heading else fallback_order
    title = heading.group(2).strip() if heading else f"Learning Module {fallback_order}"

    difficulty = "Beginner"
    difficulty_match = re.search(r"\b(Beginner|Intermediate|Advanced)\b", text)
    if difficulty_match:
        difficulty = difficulty_match.group(1)

    minutes = 20
    minutes_match = re.search(r"(\d+)\s+minutes", text, re.IGNORECASE)
    if minutes_match:
        minutes = int(minutes_match.group(1))

    return order, title, difficulty, minutes


def _field_label(line):
    match = FIELD_RE.match(line.strip())
    return match.group(1).strip().lower() if match else None


def _field_value(block, *names):
    wanted = tuple(name.lower() for name in names)
    lines = block.splitlines()
    capture = False
    values = []

    for line in lines:
        match = FIELD_RE.match(line.strip())
        if match:
            label = match.group(1).strip().lower()
            if capture and label not in wanted:
                break
            capture = any(label.startswith(name) for name in wanted)
            if capture:
                values.append(match.group(2).strip())
            continue

        if capture:
            values.append(line.rstrip())

    return _clean("\n".join(values))


def _before_answer_material(block):
    lines = []
    for line in block.splitlines():
        label = _field_label(line)
        if label and (
            label.startswith("answer")
            or label.startswith("explanation")
            or label.startswith("expected answer")
            or label.startswith("acceptable")
            or label.startswith("hint")
        ):
            break
        if line.strip().startswith("> **Type**") or line.strip().startswith("> **Difficulty**"):
            continue
        lines.append(line)
    return _clean("\n".join(lines))


def _activity_title(heading):
    title = re.sub(r"^.*?Activity\s+[\w.]+[a-z]?\s*[-\u2013\u2014]\s*", "", heading)
    return _plain(title).upper() or "ACTIVITY"


def _activity_type(block, title):
    type_value = _field_value(block, "type")
    source = f"{type_value} {title}".upper()
    if "GAUNTLET" in source:
        return "mcq"
    if any(token in source for token in ("SANDBOX", "DRAG", "DND", "BUILD", "FIX")):
        return "skip"
    if "PREDICT" in source:
        return "predict"
    if "MULTIPLE CHOICE" in source or re.search(r"\bMC\b", source):
        return "mcq"
    if "FILL" in source or "FITB" in source:
        return "fitb"
    if "SPOT" in source:
        return "spot"
    return "mcq"


def _options_from_block(block):
    options_text = _field_value(block, "options")
    options = []
    correct = None
    for line in options_text.splitlines():
        match = OPTION_RE.match(line.strip())
        if not match:
            continue
        option_id = match.group(1)
        text = match.group(2).replace("\u2705", "").strip()
        if "\u2705" in match.group(2):
            correct = option_id
        options.append({"id": option_id, "text": text})
    return options, correct


def _answer_text(block):
    return _field_value(block, "answer")


def _option_answer_from_text(answer):
    match = re.search(r"\*\*([A-Z])\*\*", answer)
    if not match:
        match = re.search(r"^\s*([A-Z])(?:\)|\s|[-\u2013\u2014])", _plain(answer))
    return match.group(1) if match else None


def _fitb_answers(block):
    answers = []
    expected = _field_value(block, "expected answer")
    acceptable = _field_value(block, "acceptable variations")
    for source in (expected, acceptable):
        answers.extend(re.findall(r"`([^`]+)`", source))
        if source and "`" not in source:
            answers.append(_plain(source))

    cleaned = []
    for answer in answers:
        normalized = answer.strip().lower()
        if normalized and normalized not in cleaned:
            cleaned.append(normalized)
    return cleaned or ["done"]


def _spot_answer(block):
    answer = _plain(_answer_text(block))
    joined = re.search(r"\bLines?\s+([0-9,\sand]+)", answer, re.IGNORECASE)
    if joined:
        numbers = re.findall(r"[0-9]+", joined.group(1))
        if len(numbers) == 1:
            return numbers[0]
        if numbers:
            return numbers

    return "1"


def _explanation(block):
    parts = []
    answer = _answer_text(block)
    if " - " in answer or "\u2014" in answer:
        detail = re.split(r"\s+[-\u2013\u2014]\s+", answer, maxsplit=1)
        if len(detail) == 2:
            parts.append(detail[1])
    for name in (
        "explanation shown after answering",
        "explanation",
        "common wrong answer",
        "key insight",
    ):
        value = _field_value(block, name)
        if value:
            parts.append(value)
    return _clean("\n\n".join(parts)) or "Good work. Continue to the next lesson."


def _hints(block):
    hints = []
    for line in block.splitlines():
        label = _field_label(line)
        if label and label.startswith("hint"):
            hint = FIELD_RE.match(line.strip()).group(2).strip()
            if hint:
                hints.append(hint)
    return hints


def _first_code_block(text):
    match = CODE_RE.search(text or "")
    if not match:
        return None, None
    return match.group(2).strip("\n"), (match.group(1) or "text").strip() or "text"


def _remove_first_code_block(text):
    return _clean(CODE_RE.sub("", text or "", count=1))


def _step_from_activity(lesson_id, order_index, heading, block):
    title = _activity_title(heading)
    kind = _activity_type(block, title)
    if kind == "skip":
        return None

    prompt = _field_value(block, "prompt") or _before_answer_material(block)
    options, checked_answer = _options_from_block(block)
    answer = checked_answer or _option_answer_from_text(_answer_text(block))
    code_snippet = None
    code_language = None

    if "GAUNTLET" in title:
        question_match = re.search(
            r"(Which of the following is TRUE about SQL injection defense\?)",
            block,
            re.IGNORECASE,
        )
        prompt = question_match.group(1) if question_match else "Which defense statement is correct?"

    if kind == "spot":
        code_snippet, code_language = _first_code_block(prompt)
        if code_snippet:
            prompt = _remove_first_code_block(prompt)

    if kind in ("mcq", "predict"):
        if not options:
            return None
        correct_answer = answer or options[0]["id"]
    elif kind == "fitb":
        correct_answer = _fitb_answers(block)
    elif kind == "spot":
        if not code_snippet:
            return None
        else:
            correct_answer = _spot_answer(block)
    return LessonStep(
        lesson_id=lesson_id,
        order_index=order_index,
        kind=kind,
        title=title,
        prompt=prompt,
        options=_j(options),
        correct_answer=_j(correct_answer),
        explanation=_explanation(block),
        hints=_j(_hints(block)),
        code_snippet=code_snippet,
        code_language=code_language,
    )


def _activity_blocks(lesson_block):
    matches = list(ACTIVITY_RE.finditer(lesson_block))
    if not matches:
        return _clean(lesson_block), []

    material = _clean(lesson_block[:matches[0].start()])
    activities = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(lesson_block)
        activities.append((match.group(1), _clean(lesson_block[match.end():end])))
    return material, activities


def _seed_markdown_module(path, fallback_order):
    text = path.read_text(encoding="utf-8")
    order, title, difficulty, minutes = _module_meta(text, fallback_order)
    module = Module(
        order_index=order,
        title=title,
        description=DESCRIPTIONS.get(order, ""),
        icon=ICONS.get(order, "database"),
        difficulty=difficulty,
        estimated_minutes=minutes,
    )
    db.session.add(module)
    db.session.flush()

    lesson_matches = list(LESSON_RE.finditer(text))
    for idx, match in enumerate(lesson_matches, 1):
        end = lesson_matches[idx].start() if idx < len(lesson_matches) else len(text)
        lesson_block = _clean(text[match.end():end])
        material, activities = _activity_blocks(lesson_block)
        lesson = Lesson(
            module_id=module.id,
            order_index=int(match.group(2)),
            title=_plain(match.group(3)),
            narrative=material,
            code_snippet=None,
            code_language=None,
            table_data=USERS_TABLE if order == 1 else None,
        )
        db.session.add(lesson)
        db.session.flush()

        added_steps = 0
        for activity_index, (heading, activity_block) in enumerate(activities, 1):
            step = _step_from_activity(lesson.id, activity_index, heading, activity_block)
            if step is not None:
                db.session.add(step)
                added_steps += 1

        if added_steps == 0 and not lesson.narrative:
            db.session.delete(lesson)


def _seed_sqli_ctf_module():
    module = Module(
        order_index=8,
        title="CTF Challenge Lab: EzSQLi",
        description=DESCRIPTIONS[8],
        icon=ICONS[8],
        difficulty="Advanced",
        estimated_minutes=30,
    )
    db.session.add(module)
    db.session.flush()

    lesson = Lesson(
        module_id=module.id,
        order_index=1,
        title="Get the Flag",
        narrative=(
            "## Get Flag\n\n"
            f"Open the challenge at [{SQLI_CTF_CHALLENGE_URL}]({SQLI_CTF_CHALLENGE_URL}).\n\n"
            "Explore the EzSQLi endpoints, recover the `BYTESEC{...}` flag, and submit it here.\n\n"
            "**Scope**: Only test this lab or systems where you have explicit permission."
        ),
        code_snippet=None,
        code_language=None,
        table_data=None,
    )
    db.session.add(lesson)
    db.session.flush()
    db.session.add(LessonStep(
        lesson_id=lesson.id,
        order_index=1,
        kind="flag",
        title="SUBMIT THE FLAG",
        prompt="Submit the exact `BYTESEC{...}` flag shown by the challenge.",
        options=_j([]),
        correct_answer=SQLI_CTF_FLAG_HASH,
        explanation="Flag accepted. You solved the EzSQLi challenge.",
        hints=_j([
            "Look at how request parameters are forwarded into the helper object.",
            "A debug path can be influenced before the admin debug check runs.",
        ]),
    ))


def _seed_re_asm_ctf_module():
    module = Module(
        order_index=13,
        title="CTF Challenge Lab: XOR Flag Checker",
        description=DESCRIPTIONS[13],
        icon=ICONS[13],
        difficulty="Beginner",
        estimated_minutes=20,
    )
    db.session.add(module)
    db.session.flush()

    lesson = Lesson(
        module_id=module.id,
        order_index=1,
        title="Recover the XOR Flag",
        narrative=(
            "## Recover the XOR Flag\n\n"
            "Download the challenge archive from [Download XOR checker](/downloads/re-asm-xor-checker).\n\n"
            "The archive contains a Linux x86-64 checker binary and a short README.\n\n"
            "After extracting it, run and inspect the checker:\n\n"
            "```bash\n"
            "chmod +x xor_checker\n"
            "./xor_checker\n"
            "strings -a ./xor_checker\n"
            "objdump -d -M intel ./xor_checker | less\n"
            "```\n\n"
            "Recover the `BYTESEC{16 hex characters}` flag and submit it here."
        ),
        code_snippet=None,
        code_language=None,
        table_data=None,
    )
    db.session.add(lesson)
    db.session.flush()
    db.session.add(LessonStep(
        lesson_id=lesson.id,
        order_index=1,
        kind="flag",
        title="SUBMIT THE XOR FLAG",
        prompt="Submit the exact `BYTESEC{16 hex characters}` flag recovered from the checker.",
        options=_j([]),
        correct_answer=RE_ASM_CTF_FLAG_HASH,
        explanation="Flag accepted. You solved the XOR checker challenge.",
        hints=_j([
            "Start with `strings` to find user-facing messages and confirm the expected format.",
            "Disassemble `check_flag` and look for the repeating XOR key and encoded byte array.",
            "XOR is reversible: original_byte = encoded_byte ^ key_byte.",
        ]),
    ))


def _seed_crypto_rsa_ctf_module():
    module = Module(
        order_index=18,
        title="CTF Challenge Lab: RSA Starter",
        description=DESCRIPTIONS[18],
        icon=ICONS[18],
        difficulty="Intermediate",
        estimated_minutes=25,
    )
    db.session.add(module)
    db.session.flush()

    lesson = Lesson(
        module_id=module.id,
        order_index=1,
        title="Recover the RSA Flag",
        narrative=(
            "## Recover the RSA Flag\n\n"
            "Download the challenge archive from [Download RSA challenge](/downloads/crypto-rsa-starter).\n\n"
            "The archive contains the public RSA values and ciphertext. Inspect the parameters and recover the `BYTESEC{...}` flag.\n\n"
            "Useful Python operations:\n\n"
            "```python\n"
            "pow(m, e, n)\n"
            "int.to_bytes(length, 'big')\n"
            "int.from_bytes(data, 'big')\n"
            "```\n\n"
            "Focus on whether textbook RSA actually wrapped around the modulus."
        ),
        code_snippet=None,
        code_language=None,
        table_data=None,
    )
    db.session.add(lesson)
    db.session.flush()
    db.session.add(LessonStep(
        lesson_id=lesson.id,
        order_index=1,
        kind="flag",
        title="SUBMIT THE RSA FLAG",
        prompt="Submit the exact `BYTESEC{...}` flag recovered from the RSA challenge.",
        options=_j([]),
        correct_answer=CRYPTO_RSA_CTF_FLAG_HASH,
        explanation="Flag accepted. You solved the RSA starter challenge.",
        hints=_j([
            "The public exponent is very small.",
            "Check whether the plaintext power is smaller than the modulus.",
            "If `c = m^3` without modular wraparound, recover `m` with an integer cube root.",
        ]),
    ))


def _seed_pwn_ret2win_ctf_module():
    module = Module(
        order_index=23,
        title="CTF Challenge Lab: Ret2win",
        description=DESCRIPTIONS[23],
        icon=ICONS[23],
        difficulty="Beginner",
        estimated_minutes=25,
    )
    db.session.add(module)
    db.session.flush()

    lesson = Lesson(
        module_id=module.id,
        order_index=1,
        title="Exploit the Ret2win Service",
        narrative=(
            "## Exploit the Ret2win Service\n\n"
            "Download the challenge archive from [Download ret2win challenge](/downloads/pwn-ret2win).\n\n"
            "The archive contains a Linux x86-64 target binary, a README, and a small payload template.\n\n"
            "The same challenge is exposed through the Docker lab endpoint:\n\n"
            "```bash\n"
            f"{PWN_RET2WIN_ENDPOINT}\n"
            "```\n\n"
            "Use the training workflow from this course: confirm the mitigations, find the `win` function address, "
            "fill the buffer up to the saved return address, then place the `win` address in little-endian form.\n\n"
            "Recover the `BYTESEC{...}` flag from the service and submit it here."
        ),
        code_snippet=None,
        code_language=None,
        table_data=None,
    )
    db.session.add(lesson)
    db.session.flush()
    db.session.add(LessonStep(
        lesson_id=lesson.id,
        order_index=1,
        kind="flag",
        title="SUBMIT THE RET2WIN FLAG",
        prompt="Submit the exact `BYTESEC{...}` flag printed by the ret2win service.",
        options=_j([]),
        correct_answer=PWN_RET2WIN_CTF_FLAG_HASH,
        explanation="Flag accepted. You redirected control flow to the win function.",
        hints=_j([
            "The binary is intentionally compiled without PIE and without a stack canary.",
            "The saved return address is reached after the 32-byte buffer and saved RBP.",
            "Use little-endian packing for the target function address.",
        ]),
    ))


def _seed_course_content():
    for model in (UserProgress, LessonStep, Lesson, Module):
        db.session.query(model).delete()

    for fallback_order, path in enumerate(_module_files(), 1):
        _seed_markdown_module(path, fallback_order)
    _seed_sqli_ctf_module()
    _seed_re_asm_ctf_module()
    _seed_crypto_rsa_ctf_module()
    _seed_pwn_ret2win_ctf_module()


def _ensure_demo_user():
    demo = User.query.filter_by(username="demo").first()
    if demo is None:
        demo = User(username="demo", email="demo@bytesec.local")
        demo.set_password("demo123")
        db.session.add(demo)
    elif not demo.check_password("demo123"):
        demo.set_password("demo123")


def refresh_course_content():
    """Reload lessons/modules from markdown while preserving registered users."""
    db.create_all()
    _ensure_demo_user()
    _seed_course_content()
    db.session.commit()
    print(f"Refreshed {Module.query.count()} modules, {Lesson.query.count()} lessons, {LessonStep.query.count()} steps.")


def seed_database():
    db.drop_all()
    db.create_all()
    _ensure_demo_user()
    _seed_course_content()
    db.session.commit()
    print(f"Seeded {Module.query.count()} modules, {Lesson.query.count()} lessons, {LessonStep.query.count()} steps.")


def _course_is_stale():
    if Module.query.count() != _expected_module_count():
        return True
    leaked_ctf = (
        Lesson.query
        .join(Module)
        .filter(
            (Lesson.title == "Solve the Baby SQLi Challenge")
            | (Lesson.narrative.contains("scripts/dev-services.sh"))
            | (Lesson.code_language == "bash")
            | (Module.title == "CTF Challenge Lab: Baby SQLi")
        )
        .first()
    )
    if leaked_ctf is not None:
        return True
    missing_re = Module.query.filter_by(title="CTF Challenge Lab: XOR Flag Checker").first()
    if missing_re is None:
        return True
    missing_crypto = Module.query.filter_by(title="CTF Challenge Lab: RSA Starter").first()
    if missing_crypto is None:
        return True
    missing_pwn = Module.query.filter_by(title="CTF Challenge Lab: Ret2win").first()
    return missing_pwn is None


def ensure_database():
    """Create missing data without wiping users on ordinary restarts."""
    db.create_all()
    _ensure_demo_user()

    if Module.query.count() == 0 or _course_is_stale():
        _seed_course_content()

    db.session.commit()
    print(
        f"Database ready with {Module.query.count()} modules, "
        f"{Lesson.query.count()} lessons, {LessonStep.query.count()} steps, "
        f"{User.query.count()} users."
    )
