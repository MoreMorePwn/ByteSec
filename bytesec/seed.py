"""Seed ByteSec content from markdown curricula under modules/."""

import json
import random
import re
import shutil
import zipfile
from datetime import timedelta
from pathlib import Path

from . import db
from .models import Article, CommunityChallenge, CommunityChallengeSolve, Lesson, LessonStep, Module, User, UserProgress, utc_now


ROOT_DIR = Path(__file__).resolve().parents[1]
CURRICULUM_ROOT = ROOT_DIR / "modules"
SQLI_MODULE_DIR = CURRICULUM_ROOT / "sqli"
RE_ASM_MODULE_DIR = CURRICULUM_ROOT / "reverse-engineering-assembly"
CRYPTO_MODULE_DIR = CURRICULUM_ROOT / "crypto"
PWN_MODULE_DIR = CURRICULUM_ROOT / "pwn"
FORENSICS_MODULE_DIR = CURRICULUM_ROOT / "forensics"
COMMUNITY_CHALLENGE_ROOT = ROOT_DIR / "ctf_chall" / "community"
SQLI_CTF_CHALLENGE_URL = "http://127.0.0.1:8004"
PWN_RET2WIN_ENDPOINT = "nc 127.0.0.1 9001"
SQLI_CTF_FLAG_HASH = "84f61f593ff27ff39777cfb98bf90598848c1bc9533e75bf8ee54b964b876ba9"
RE_ASM_CTF_FLAG_HASH = "57f7e67a47b26bc59fab7e5f4807ffeba2edce17ce39540e6395caf4ef9d1a2a"
CRYPTO_RSA_CTF_FLAG_HASH = "cc50860a061bc2af278112f0ebc8f347e27bf97a12c792e66082b68010de036a"
PWN_RET2WIN_CTF_FLAG_HASH = "8e7a8ab5ef6c8d0ffd605d16b6112704d0e493070046d4b382895fa722965587"
UPLOADER_NAMES = ("Reimu", "Erin", "Marisa", "Sakuya", "Scarlet", "Cirno", "Milk", "Shama", "Liz", "Acid")

SAMPLE_ARTICLES = [
    {
        "title": "Linux Rootkits: Hooking Models Defenders Should Recognize",
        "excerpt": (
            "A defender-focused tour of Linux rootkit evolution, from LD_PRELOAD tricks to LKM, "
            "ftrace, eBPF, and io_uring abuse."
        ),
        "content": """## Why Rootkits Matter

A rootkit is not defined by a single exploit or programming language. It is defined by its job: keep an intrusion present while making the machine lie about what is happening. A rootkit may hide a process, a socket, a file, a kernel module, a user account, a loaded library, a scheduled task, or the telemetry that would normally expose those items.

For defenders, the key point is that most rootkits do not need to defeat every possible observation path. They only need to defeat the paths that responders are likely to trust first. If an analyst only runs `ps`, `ls`, and `netstat`, then a userland hook that alters those tools may be enough. If the analyst only checks module lists, then a kernel implant that unlinks itself from common lists may survive. Good rootkit analysis is therefore less about one perfect detector and more about comparing independent views.

## Userland Hooking

The simplest Linux rootkits live in userland. A common pattern is to preload a shared object so common library calls are intercepted before they reach the real libc implementation. If a command asks for directory entries, the malicious library can filter out names that match the attacker's files. If a process listing tool reads process information, the library can hide selected PIDs. If a network tool reads socket state, the library can remove attacker-controlled connections before the output reaches the terminal.

Userland hooks have advantages. They are quick to deploy, easy to test, and do not require kernel code. They also have weaknesses. Statically linked tools, trusted recovery media, direct syscalls, alternative APIs, or external telemetry may bypass the hook. A userland rootkit often fails when responders stop trusting the local shell environment.

## Kernel-Level Rootkits

Kernel rootkits operate closer to the operating system's decision points. They may patch syscall tables, modify function pointers, hook filesystem or network paths, alter kernel data structures, or hide their own module from listing APIs. The goal is the same as a userland rootkit, but the hook sits under more tools.

This makes kernel rootkits more dangerous and more fragile. A bad hook can crash the host. A kernel version mismatch can break assumptions. Security features, kernel lockdown, module signing, and integrity monitoring can make installation harder. Still, when a kernel rootkit works, ordinary endpoint commands may all agree on a false view because they are ultimately asking a compromised kernel.

## Modern Hooking Surfaces

Linux has gained powerful observability and I/O frameworks. The same features that help administrators and defenders can be abused when attackers control them.

eBPF is a legitimate framework for running constrained programs in kernel context. Defenders use it for tracing, metrics, and security policy. An attacker with enough privilege can use it to observe sensitive activity, alter decisions in supported hook points, or avoid older module-focused detection logic.

Function tracing facilities can also become hook points. If a rootkit can redirect selected function execution or wrap a target function with its own logic, it can hide activity while keeping the system mostly operational.

io_uring changes how some I/O operations are submitted and completed. It can reduce the visibility of simple syscall-by-syscall monitoring because work is batched and completed through a ring interface. That does not make activity invisible, but it changes where defenders need to look.

## Detection By Cross-View Validation

Rootkit detection should start with disagreement. Ask the system the same question through different paths and compare answers.

Examples:

- Compare `ps` output with `/proc` enumeration and memory-derived process lists.
- Compare `ls` output with direct inode walks, filesystem images, or trusted boot media.
- Compare `netstat` or `ss` with packet capture, firewall counters, eBPF maps, and external flow logs.
- Compare kernel module lists with memory scans and kernel symbol state.
- Compare local endpoint telemetry with EDR, hypervisor, network, and authentication logs.

No single mismatch proves a rootkit. Containers, namespaces, permissions, stale telemetry, and collection timing can also create differences. The value is that mismatches tell you where to focus.

## Practical Triage Questions

When a Linux rootkit is suspected, work from these questions:

1. What exact object is hidden: file, process, port, module, account, log event, or telemetry field?
2. Which observation paths agree, and which disagree?
3. Is the suspicious behavior isolated to a shell session, a user, a namespace, or the whole host?
4. Are there new kernel modules, unusual BPF programs, unexpected tracing state, or tainted-kernel indicators?
5. Did persistence land in services, cron, shell profiles, startup scripts, package hooks, or kernel load paths?
6. Can the same activity be confirmed from network, hypervisor, or centralized logs?

## Response Guidance

Do not keep investigating a suspected kernel compromise entirely from the compromised machine. Preserve volatile evidence when possible, then collect from a trusted environment. If the host is critical, prioritize containment and evidence preservation over live cleanup. Removing a rootkit manually can destroy useful evidence or leave backup persistence behind.

For training environments, reproduce the hiding behavior in a lab and write down which tools were fooled. That exercise builds the instinct defenders need: every local output is just one view, not the truth.

## Takeaway

Rootkits succeed by making normal questions return curated answers. Defenders respond by asking better questions through independent paths. The most reliable habit is cross-view validation: never trust a single tool, a single layer, or a single timestamp when the system itself may be part of the intrusion.
""",
    },
    {
        "title": "Kernel Anti-Cheats and the Security Tradeoff",
        "excerpt": (
            "Kernel anti-cheats use privileged Windows primitives to protect games, which makes their architecture "
            "look similar to security tooling and sometimes to malware."
        ),
        "content": """## The Arms Race

Anti-cheat software exists because competitive games have real incentives around unfair automation, memory tampering, and account resale. Early cheats often lived in usermode: reading process memory, patching game code, injecting DLLs, or automating input. As games defended those paths, cheat developers moved deeper into the operating system. They used drivers, vulnerable signed drivers, DMA devices, firmware tricks, and sometimes hypervisors.

Kernel anti-cheat is a response to that escalation. If a cheat can run with kernel privileges, a purely usermode anti-cheat may not see it. A kernel driver gives the defender a better chance to observe handle access, process tampering, driver loads, memory manipulation, and low-level state that usermode code cannot reliably inspect.

## Typical Components

A kernel anti-cheat product usually has several layers:

- A kernel driver that registers callbacks, monitors sensitive events, and protects the game process.
- A privileged Windows service that starts early, manages driver communication, and sends telemetry or enforcement decisions.
- A usermode game module that performs local checks and communicates with the service.
- Backend systems that receive telemetry, correlate sessions, and apply bans or trust scores.

The driver is the most sensitive component. It can inspect or influence parts of the system that ordinary applications cannot touch. That power is why it can detect deeper cheats, and it is also why users and security teams scrutinize it.

## What The Driver Watches

Kernel anti-cheats commonly care about:

- Processes opening handles to the game with suspicious access rights.
- Threads being created inside protected processes.
- Memory pages being changed, mapped, or scanned in unusual ways.
- Unsigned, newly loaded, or suspicious drivers.
- Known vulnerable driver names and certificate patterns.
- Debugger attachment, breakpoint state, or instrumentation frameworks.
- Object callbacks that block or downgrade access to the game process.
- Attempts to hide modules, patch kernel routines, or alter callback lists.

None of these checks is perfect alone. Legitimate software can look invasive, and cheats can mimic normal behavior. The system becomes useful when many weak signals are combined with session context.

## Why It Looks Scary

From a capability perspective, kernel anti-cheat and malicious kernel software can overlap. Both may inspect memory, restrict process access, watch driver loading, and communicate with remote infrastructure. The difference is intent, consent, scope, update control, and transparency.

Security review should not stop at "it is for a game." A kernel driver can still introduce vulnerabilities, crash systems, leak data, conflict with security tools, or create a new supply-chain risk. The review question is whether the capability is necessary, bounded, and maintained responsibly.

## Trust Boundaries

The most important design boundary is between the user's machine, the game publisher, and the competitive environment. A publisher wants strong integrity. A player wants privacy and stability. A defender wants predictable behavior and a clear uninstall path.

Healthy implementations document what is collected, limit inspection to relevant signals, protect update delivery, avoid broad data collection, and fail safely when something goes wrong. Risky implementations run constantly without need, collect unrelated data, use fragile kernel hooks, or make removal difficult.

## Common Failure Modes

Kernel anti-cheats can fail in several ways:

1. A bug in the driver causes a system crash.
2. A vulnerable IOCTL lets a local attacker abuse the driver.
3. An update channel is compromised.
4. The driver conflicts with EDR, virtualization, overlays, accessibility tools, or debuggers.
5. The product blocks legitimate software without a clear explanation.
6. The driver remains loaded outside the game session longer than needed.

These are engineering and governance problems, not only security research problems.

## Analyst Review Checklist

When analyzing a kernel anti-cheat-like component, inspect:

- How the driver is installed, signed, started, stopped, and updated.
- Which IOCTLs are exposed to usermode callers.
- Whether access checks protect driver commands.
- Which callbacks are registered.
- Whether the driver scans arbitrary memory or only game-relevant regions.
- What telemetry leaves the machine.
- Whether errors are logged in a way users and administrators can understand.
- Whether the component can be removed cleanly.

## Defensive Takeaway

Kernel access can be a reasonable answer to kernel-level cheating, but it is never free. It changes the trust model of the machine. A good anti-cheat design should make that tradeoff explicit: narrow scope, strong update security, robust error handling, transparent operation, and a removal path that does not require a forensic investigation.
""",
    },
    {
        "title": "Self-XSS Still Deserves Threat Modeling",
        "excerpt": (
            "Self-XSS is often dismissed, but browser context, login CSRF, credentialless iframes, and stored payloads "
            "can turn it into real account impact."
        ),
        "content": """## The Usual Dismissal

Self-XSS is often treated as a low-value bug because the victim has to run script against themselves. If the only exploit path is "convince a user to paste JavaScript into the developer console," the practical risk is usually limited. But that shorthand becomes dangerous when teams stop analyzing how the payload reaches the page, which account owns the payload, and whether another bug can place a victim into the attacker's context.

The right question is not "is this self-XSS?" The right question is "can this script execute in a context where it can affect a different user, account, or session?"

## Stored Self-XSS

Stored self-XSS appears when a user-controlled field is rendered unsafely, but only back to that same user. A profile nickname, private note, dashboard widget, saved search name, or account description may fit this pattern. The application assumes the field is safe because users only harm themselves.

That assumption breaks when the field is later rendered in a shared context, an admin console, an embedded frame, a support view, an export preview, or an account-switching flow. The storage location matters less than the render paths. A value that is private today can become shared tomorrow after a small product change.

## Login CSRF As A Force Multiplier

Login CSRF is easy to underestimate. If an attacker can force a browser to log into an attacker-controlled account, then a stored payload in that attacker account can become a staging point. The victim may believe they are using their own session, but the browser is temporarily inside the attacker's account.

This does not automatically steal the victim's real account. The impact depends on what else the page can reach. If the attacker-controlled page can frame a victim-authenticated page, communicate with it, or trigger same-origin behavior, the chain becomes more interesting.

## Frame Context Matters

Modern browsers have many frame and credential modes. A page may be loaded with credentials, without credentials, sandboxed, or embedded by another page. Developers sometimes assume that removing credentials removes all risk, but same-origin relationships and frame access rules can still create surprising behavior.

If a site mixes credentialed and credentialless frames on the same origin, the security model needs careful review. The payload may not need direct cookie access if it can influence a same-origin page, read a reachable DOM, or trigger privileged flows through postMessage or frame navigation.

## CAPTCHA Is Not CSRF Protection

CAPTCHA can reduce automated abuse, but it does not prove request intent. A login form protected only by CAPTCHA may still be vulnerable to login CSRF if the browser can be forced through the login flow. CSRF controls need a token or equivalent request-binding mechanism that ties the action to a user-intended interaction.

This matters because authentication actions change state. Logging a browser into the attacker's account changes what the victim sees and what stored data is rendered.

## Threat Modeling The Chain

When reviewing a self-XSS report, map the full chain:

1. Where is the payload stored?
2. Who can cause the payload to be stored?
3. Which pages render it?
4. Which pages render it with HTML interpretation?
5. Can another user be navigated into the account or page that contains it?
6. Can the payload reach any same-origin frame or privileged endpoint?
7. Are login, logout, account switch, and invite flows protected by CSRF defenses?
8. Does the application allow framing where it is not needed?

If every answer stays scoped to the attacker account, severity remains low. If one answer crosses into victim context, the bug class changes.

## Defensive Controls

Start with output encoding. Treat every stored text field as untrusted, even if it is "private." Apply context-aware escaping for HTML, attributes, URLs, JavaScript strings, and markdown-rendered content.

Add CSRF protection to login and logout flows. Many teams protect only authenticated state-changing endpoints, but login changes the browser's account context and should be protected too.

Use frame controls. If the application does not need to be embedded, set headers that prevent framing. If framing is required, restrict it deliberately and review postMessage handlers.

Review credentialless and sandboxed frames as part of the app's threat model. Do not assume that a browser feature removes the need for application-level boundaries.

## Testing Checklist

- Store a harmless HTML marker in every user-visible private field.
- Search for alternate render locations such as admin views, support views, exports, previews, notifications, and embeds.
- Test login CSRF with a controlled account.
- Test whether the page can be framed.
- Inspect postMessage handlers for wildcard origins or missing source checks.
- Review whether same-origin iframes can access each other in the intended browser configuration.
- Confirm that markdown and rich-text renderers sanitize attributes, URLs, and embedded HTML.

## Takeaway

Self-XSS is a label, not a conclusion. Many cases are low impact, but the label should never replace threat modeling. Stored payloads, login CSRF, frame relationships, and same-origin behavior can combine into a real account-impacting chain. A mature review treats "self" as the starting hypothesis and then proves whether the payload can stay isolated.
""",
    },
]


def _j(obj):
    return json.dumps(obj)


def _slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-") or "item"


def _get_or_create_user(username, email, password, streak_days=0):
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
    else:
        if not user.check_password(password):
            user.set_password(password)
        if user.email != email and not User.query.filter(User.email == email, User.id != user.id).first():
            user.email = email
    user.streak_days = max(user.streak_days or 0, streak_days)
    return user


def _strip_yaml_scalar(value):
    value = (value or "").strip()
    if "#" in value and not value.startswith(("http://", "https://")):
        value = value.split("#", 1)[0].strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    return value.strip()


def _capture_yaml_block(lines, start_index):
    captured = []
    for line in lines[start_index + 1:]:
        if line.strip() and not line.startswith((" ", "\t")):
            break
        captured.append(line)
    while captured and not captured[0].strip():
        captured.pop(0)
    while captured and not captured[-1].strip():
        captured.pop()
    indents = [
        len(line) - len(line.lstrip(" "))
        for line in captured
        if line.strip()
    ]
    trim = min(indents) if indents else 0
    return "\n".join(line[trim:] if len(line) >= trim else line for line in captured).strip()


def _capture_yaml_list(lines, start_index):
    values = []
    for line in lines[start_index + 1:]:
        stripped = line.strip()
        if not stripped:
            continue
        if not line.startswith((" ", "\t")):
            break
        if stripped.startswith("- "):
            values.append(_strip_yaml_scalar(stripped[2:]))
    return values


def _parse_challenge_metadata(path):
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    meta = {
        "name": path.parent.name,
        "category": "Miscellaneous",
        "description": "",
        "value": 100,
        "flags": [],
        "tags": [],
        "files": [],
        "state": "visible",
    }
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, raw = stripped.split(":", 1)
        key = key.strip().lower()
        raw = raw.strip()
        if key in ("name", "category", "state"):
            meta[key] = _strip_yaml_scalar(raw)
        elif key == "description":
            meta["description"] = _capture_yaml_block(lines, index) if raw.startswith("|") else _strip_yaml_scalar(raw)
        elif key == "value":
            try:
                meta["value"] = int(_strip_yaml_scalar(raw))
            except ValueError:
                meta["value"] = 100
        elif key in ("flags", "tags", "files"):
            meta[key] = _capture_yaml_list(lines, index)

    description = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", meta["description"], flags=re.IGNORECASE)
    description = re.sub(r"<[^>]+>", " ", description)
    description = re.sub(r"(?im)^\s*author\s*:.*(?:\n|$)", "", description)
    description = re.sub(r"\n{3,}", "\n\n", description)
    description = re.sub(r"[ \t]{2,}", " ", description)
    description = description.strip() or "Imported community challenge."
    if len(description) > 2000:
        description = description[:2000].rsplit("\n", 1)[0].strip() + "\n\n[Description shortened from imported challenge metadata.]"
    meta["description"] = description
    return meta


def _difficulty_from_tags(tags):
    lowered = {str(tag).lower() for tag in tags}
    if "hard" in lowered:
        return "hard"
    if "medium" in lowered:
        return "medium"
    return "easy" if lowered.intersection({"easy", "baby"}) else "medium"


def _category_label(value):
    value = (value or "Miscellaneous").strip()
    mapping = {
        "forensic": "Forensics",
        "forensics": "Forensics",
        "misc": "Miscellaneous",
        "miscellaneous": "Miscellaneous",
        "binary exploitation": "Binary Exploitation",
        "pwn": "Binary Exploitation",
        "reverse": "Reverse Engineering",
        "rev": "Reverse Engineering",
        "reverse engineering": "Reverse Engineering",
        "crypto": "Cryptography",
        "cryptography": "Cryptography",
        "web": "Web Exploitation",
        "web exploitation": "Web Exploitation",
        "osint": "OSINT",
    }
    return mapping.get(value.lower(), value)


def _sync_challenge_asset(challenge, source_dir, files):
    upload_dir = ROOT_DIR / "instance" / "community_uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"{challenge.id}_"
    source_files = [
        source_dir / file_name
        for file_name in files
        if file_name and (source_dir / file_name).is_file()
    ]
    existing_files = [
        old_file
        for old_file in upload_dir.iterdir()
        if old_file.is_file() and old_file.name.startswith(prefix)
    ]
    if not source_files:
        for old_file in existing_files:
            old_file.unlink()
        challenge.file_name = None
        challenge.file_size = None
        return

    if len(source_files) == 1:
        source_file = source_files[0]
        if (
            existing_files
            and challenge.file_name == source_file.name
            and challenge.file_size == source_file.stat().st_size
        ):
            return
        for old_file in existing_files:
            old_file.unlink()
        disk_name = f"{challenge.id}_seed_{source_file.name}"
        destination = upload_dir / disk_name
        shutil.copy2(source_file, destination)
        challenge.file_name = source_file.name
        challenge.file_size = destination.stat().st_size
        return

    archive_name = f"{_slugify(challenge.title)}-files.zip"
    if existing_files and challenge.file_name == archive_name:
        return
    for old_file in existing_files:
        old_file.unlink()
    destination = upload_dir / f"{challenge.id}_seed_{archive_name}"
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for source_file in source_files:
            zf.write(source_file, arcname=str(source_file.relative_to(source_dir)))
    challenge.file_name = archive_name
    challenge.file_size = destination.stat().st_size


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
    24: "travel_explore",
    25: "terminal",
    26: "manage_accounts",
    27: "construction",
    28: "lan",
    29: "folder_open",
    30: "account_tree",
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
    24: "Build an artifact-first Windows investigation map and learn how shared fields drive pivots.",
    25: "Use Prefetch, Amcache, SRUM, BAM/DAM, event logs, and PowerShell logs as evidence of execution.",
    26: "Correlate logons, SIDs, Logon IDs, RDP events, and process creation into account activity timelines.",
    27: "Investigate services, scheduled tasks, Run keys, IFEO debugger keys, and other persistence locations.",
    28: "Use SRUM, firewall events, tracing keys, and network connection artifacts to reason about traffic and exfiltration.",
    29: "Inspect Recycle Bin records, shell items, jump lists, browser artifacts, and file timestamps for user activity.",
    30: "Build a concise Windows forensic timeline that handles timestamp caveats and cross-artifact validation.",
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
    module_ranges = (
        (SQLI_MODULE_DIR, 1, 7),
        (RE_ASM_MODULE_DIR, 9, 12),
        (CRYPTO_MODULE_DIR, 14, 17),
        (PWN_MODULE_DIR, 19, 22),
        (FORENSICS_MODULE_DIR, 24, 30),
    )
    for module_dir, start, end in module_ranges:
        if not module_dir.exists():
            continue
        files.extend(
            path
            for path in module_dir.glob("[0-9][0-9]-*.md")
            if not path.name.startswith("00-")
            and start <= _module_file_order(path) <= end
        )
    return sorted(files, key=_module_file_sort_key)


def _module_file_order(path):
    match = re.match(r"^([0-9]{2})-", path.name)
    return int(match.group(1)) if match else 999


def _module_file_sort_key(path):
    order = _module_file_order(path)
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
    return _get_or_create_user("demo", "demo@bytesec.local", "demo123", streak_days=4)


def _ensure_uploader_users():
    users = []
    for name in UPLOADER_NAMES:
        users.append(_get_or_create_user(name, f"{name.lower()}@bytesec.local", "bytesec123"))
    return users


def _ensure_sample_articles(author):
    for article_data in SAMPLE_ARTICLES:
        slug = _slugify(article_data["title"])
        article = Article.query.filter_by(slug=slug).first()
        if article is None:
            article = Article(
                title=article_data["title"],
                slug=slug,
                content=article_data["content"],
                excerpt=article_data["excerpt"],
                cover_image=None,
                author_id=author.id,
                status="published",
                published_at=utc_now(),
            )
            db.session.add(article)
            continue
        article.title = article_data["title"]
        article.content = article_data["content"]
        article.excerpt = article_data["excerpt"]
        article.author_id = author.id
        if article.status in ("draft", "pending", "rejected"):
            article.status = "published"
            article.published_at = utc_now()


def _ensure_community_challenges():
    if not COMMUNITY_CHALLENGE_ROOT.exists():
        return

    uploaders = _ensure_uploader_users()
    challenge_paths = sorted(COMMUNITY_CHALLENGE_ROOT.glob("*/challenge.yml"), key=lambda path: path.parent.name.lower())
    for index, challenge_yml in enumerate(challenge_paths):
        source_dir = challenge_yml.parent
        meta = _parse_challenge_metadata(challenge_yml)
        title = meta["name"]
        if not title:
            continue
        uploader = uploaders[index % len(uploaders)]
        flag = meta["flags"][0] if meta["flags"] else f"BYTESEC{{{_slugify(title)}}}"
        challenge = CommunityChallenge.query.filter_by(title=title).first()
        if challenge is None:
            challenge = CommunityChallenge(
                title=title,
                category=_category_label(meta["category"]),
                description=meta["description"],
                difficulty=_difficulty_from_tags(meta["tags"]),
                flag=flag,
                points=meta["value"],
                hint=None,
                author_id=uploader.id,
                status="approved",
                reviewed_by=User.query.filter_by(username="demo").first().id,
                reviewed_at=utc_now(),
            )
            db.session.add(challenge)
            db.session.flush()
        else:
            challenge.category = _category_label(meta["category"])
            challenge.description = meta["description"]
            challenge.difficulty = _difficulty_from_tags(meta["tags"])
            challenge.flag = flag
            challenge.points = meta["value"]
            challenge.author_id = uploader.id
            if challenge.status == "pending":
                challenge.status = "approved"
                challenge.reviewed_by = User.query.filter_by(username="demo").first().id
                challenge.reviewed_at = utc_now()
        _sync_challenge_asset(challenge, source_dir, meta["files"])


def _ensure_sample_user_progress():
    _get_or_create_user("student", "student@bytesec.local", "student123", streak_days=7)
    seeded_users = [
        user for user in User.query.filter(User.username.in_(("student", *UPLOADER_NAMES))).all()
        if user.username != "demo"
    ]
    if not seeded_users:
        return

    user_ids = [user.id for user in seeded_users]
    db.session.query(UserProgress).filter(UserProgress.user_id.in_(user_ids)).delete(synchronize_session=False)
    db.session.query(CommunityChallengeSolve).filter(
        CommunityChallengeSolve.user_id.in_(user_ids)
    ).delete(synchronize_session=False)

    steps = LessonStep.query.order_by(LessonStep.id).all()
    approved_challenges = CommunityChallenge.query.filter_by(status="approved").order_by(CommunityChallenge.id).all()

    for user in seeded_users:
        rng = random.Random(f"bytesec-progress:{user.username}")
        user.streak_days = rng.randint(1, 18)
        user.last_active = utc_now() - timedelta(hours=rng.randint(1, 96))

        if steps:
            min_steps = max(1, len(steps) // 12)
            max_steps = max(min_steps, len(steps) * 7 // 10)
            target_count = rng.randint(min_steps, max_steps)
            for step in rng.sample(steps, target_count):
                db.session.add(UserProgress(user_id=user.id, step_id=step.id))

        if approved_challenges:
            solve_count = rng.randint(0, min(len(approved_challenges), 7))
            for challenge in rng.sample(approved_challenges, solve_count):
                db.session.add(CommunityChallengeSolve(user_id=user.id, challenge_id=challenge.id))

    demo = User.query.filter_by(username="demo").first()
    if demo is not None and approved_challenges:
        for challenge in approved_challenges[: min(5, len(approved_challenges))]:
            exists = CommunityChallengeSolve.query.filter_by(
                user_id=demo.id,
                challenge_id=challenge.id,
            ).first()
            if exists is None:
                db.session.add(CommunityChallengeSolve(user_id=demo.id, challenge_id=challenge.id))


def refresh_course_content():
    """Reload lessons/modules from markdown while preserving registered users."""
    db.create_all()
    demo = _ensure_demo_user()
    _seed_course_content()
    _ensure_sample_articles(demo)
    _ensure_community_challenges()
    _ensure_sample_user_progress()
    db.session.commit()
    print(f"Refreshed {Module.query.count()} modules, {Lesson.query.count()} lessons, {LessonStep.query.count()} steps.")


def seed_database():
    db.drop_all()
    db.create_all()
    demo = _ensure_demo_user()
    _seed_course_content()
    _ensure_sample_articles(demo)
    _ensure_community_challenges()
    _ensure_sample_user_progress()
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
    demo = _ensure_demo_user()

    if Module.query.count() == 0 or _course_is_stale():
        _seed_course_content()

    _ensure_sample_articles(demo)
    _ensure_community_challenges()
    _ensure_sample_user_progress()
    db.session.commit()
    print(
        f"Database ready with {Module.query.count()} modules, "
        f"{Lesson.query.count()} lessons, {LessonStep.query.count()} steps, "
        f"{User.query.count()} users."
    )
