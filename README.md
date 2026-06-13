# ByteSec

<div align="center">
  <h3>Interactive cybersecurity learning platform for guided lessons, graded activities, and CTF-style practice labs.</h3>
  <p>Built with Flask, markdown-seeded course content, and local challenge services for hands-on security education.</p>
</div>

---

# Interactive Cybersecurity Learning Platform

ByteSec combines structured lessons, challenge-driven practice, and community content workflows in one web app. Learners can move through curated tracks, answer interactive checks, submit flags, and track progress, while admins can review articles, community challenges, and local lab services from the same interface.

---

## Overview

| Item | Details |
| --- | --- |
| Name | ByteSec |
| Type | Web-based cybersecurity learning platform |
| Stack | Flask, Flask-SQLAlchemy, Jinja, Tailwind CSS, SQLite by default, optional Turso |
| Focus | Guided CTF-style learning across web exploitation, reverse engineering, cryptography, pwn, and Windows forensics |
| Activity Types | Multiple choice, predict the output, fill in the blank, spot the vulnerable line, flag submission |
| Supporting Modules | Articles, community challenges, leaderboards, profile management, and Docker lab controls |

---

## Features

- Guided course tracks seeded from `modules/`
- Interactive lesson steps with instant correctness feedback
- Multiple activity families for concept checks and applied exercises
- Downloadable and locally hosted CTF labs
- Progress tracking through `UserProgress`
- Course and community leaderboards
- Article submission, preview, and admin publishing workflow
- Community challenge upload, review, approval, and download flow
- Theme persistence, login, logout, and profile editing
- Docker admin dashboard for local challenge services

---

## What ByteSec Solves

Cybersecurity learning is often split between static notes, separate lab environments, and manual challenge distribution. ByteSec brings those pieces together in one platform so students can:

- read structured lesson material and answer checks in context
- move from explanation to practice without leaving the platform
- download or run companion labs for applied exercises
- submit community content through moderated workflows
- measure progress with stored completion data and leaderboards

---

## Course Tracks

| Track | Modules | Source |
| --- | ---: | --- |
| Web Exploitation: SQL Injection | 1-8 | `modules/sqli/` plus EzSQLi lab |
| Reverse Engineering: x86-64 Assembly | 9-13 | `modules/reverse-engineering-assembly/` plus XOR checker lab |
| Cryptography: CryptoBook Core | 14-18 | `modules/crypto/` plus RSA starter lab |
| Pwn: Stack Exploitation | 19-23 | `modules/pwn/` plus ret2win lab |
| Windows Forensics Investigation Workflow | 24-30 | `modules/forensics/` |

---

## Seeded Content

### Demo Accounts

| Username | Password | Role |
| --- | --- | --- |
| `demo` | `demo123` | Default admin/demo account |
| `student` | `student123` | Sample learner account |

Uploader accounts are also seeded with password `bytesec123`:

```text
Reimu
Erin
Marisa
Sakuya
Scarlet
Cirno
Milk
Shama
Liz
Acid
```

Admin access is controlled by `BYTESEC_ADMIN_USERS`. If it is unset, only `demo` is treated as admin.

### Seeded Articles

- Linux Rootkits: Hooking Models Defenders Should Recognize
- Kernel Anti-Cheats and the Security Tradeoff
- Self-XSS Still Deserves Threat Modeling

### Imported Community Challenges

The repo includes community challenge sources under `ctf_chall/community/`:

```text
Ai C
Brixton Bullies
Opening set
Pirate's Hook V2
World's end loneliness
cold storage leak
donut goes brrr
joe mama
lagi-dengerin-lagu-apa-mas
pppnnnggg
sigmaboy67
syududu
```

Runtime challenge copies are generated under `instance/community_uploads/`.

---

## Technology Stack

### Core Application

- Flask 3.1
- Flask-SQLAlchemy 3.1
- Jinja templates
- Vanilla JavaScript
- Tailwind CSS CDN
- Google Material Symbols

### Data and Runtime

- SQLite for local development
- Optional Turso via the bundled pure-Python HTTP driver
- Runtime-generated instance data under `instance/`
- Vercel-compatible entrypoint in `api/index.py`

### Content and Labs

- Markdown course modules
- Docker Compose for web and pwn lab services
- GCC and Make for native challenge binaries

---

## Prerequisites

Make sure these are available locally:

- Python with SQLite support
- `pip`
- Docker and Docker Compose
- GCC and Make

If startup fails with `ModuleNotFoundError: No module named '_sqlite3'`, use a Python build that includes SQLite.

---

## How to Run Locally

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the App

```bash
flask --app app run --debug
```

You can also run:

```bash
python app.py
```

Default URL:

```text
http://127.0.0.1:5000
```

### 3. Optional Environment Variables

```text
BYTESEC_HOST
BYTESEC_PORT
SECRET_KEY
BYTESEC_ADMIN_USERS
TURSO_DATABASE_URL
TURSO_AUTH_TOKEN
```

### 4. Database Commands

Create missing data without wiping users:

```bash
flask --app app ensure-db
```

Reload markdown course content while preserving registered users:

```bash
flask --app app refresh-course
```

Fully wipe and recreate the database:

```bash
flask --app app init-db
```

---

## Run App and Lab Services

The helper script manages the Flask app plus the Docker-backed services:

```bash
./scripts/dev-services.sh start
./scripts/dev-services.sh status
./scripts/dev-services.sh logs
./scripts/dev-services.sh restart
./scripts/dev-services.sh stop
```

Default service locations:

| Service | Endpoint |
| --- | --- |
| ByteSec web app | `http://127.0.0.1:5000` |
| EzSQLi challenge | `http://127.0.0.1:8004` |
| Ret2win challenge | `nc 127.0.0.1 9001` |
| Docker admin dashboard | `http://127.0.0.1:5000/admin/docker` |

When running from WSL and opening from Windows, you may need the WSL IP instead of `localhost`:

```bash
hostname -I | awk '{print $1}'
```

---

## CTF Labs

### EzSQLi

```bash
cd ctf_chall/ezsqli
docker compose up -d --build
docker compose ps
docker compose logs --tail=80
docker compose down
```

### XOR Flag Checker

```bash
cd ctf_chall/re_asm_xor_checker
make
./xor_checker
```

Download route: `/downloads/re-asm-xor-checker`

### RSA Starter

Generated by the app and exposed at `/downloads/crypto-rsa-starter`.

### Ret2win

```bash
cd ctf_chall/ret2win
docker compose up -d --build
docker compose ps
nc 127.0.0.1 9001
docker compose down
```

Download route: `/downloads/pwn-ret2win`

---

## Platform Workflows

### Courses

1. Users open `/course`.
2. They choose a track.
3. Lessons are shown in module order.
4. Activities are completed through `/api/complete-step` or `/api/check-flag-step`.
5. Progress is stored in `UserProgress`.
6. Course leaderboard ranks users by completed lesson steps.

### Articles

1. Published articles are listed at `/articles`.
2. Any logged-in user can submit an article at `/articles/new`.
3. Normal user submissions are stored as `pending`.
4. Users can review their submission statuses on `/submissions`.
5. Admins review, preview, publish, reject, edit, or delete content from `/admin/articles`.

### Community Challenges

1. Approved challenges are listed at `/community`.
2. Logged-in users can submit a challenge at `/community/submit`.
3. User submissions are stored as `pending`.
4. Users can review their challenge statuses on `/submissions`.
5. Submitters and admins can preview pending or rejected challenge pages.
6. Admins review approvals from `/admin/community`.

---

## Project Structure

```text
.
|-- api/
|   `-- index.py
|-- app.py
|-- bytesec/
|   |-- __init__.py
|   |-- models.py
|   |-- routes.py
|   |-- seed.py
|   |-- turso_driver.py
|   `-- templates/
|-- ctf_chall/
|   |-- baby_sqli/
|   |-- community/
|   |-- ezsqli/
|   |-- re_asm_xor_checker/
|   `-- ret2win/
|-- demo/
|-- modules/
|   |-- crypto/
|   |-- forensics/
|   |-- pwn/
|   |-- rev/
|   |-- reverse-engineering-assembly/
|   `-- sqli/
|-- scripts/
|   `-- dev-services.sh
|-- README.md
|-- requirements.txt
`-- vercel.json
```

---

## Curriculum Parser Rules

The parser in `bytesec/seed.py` reads markdown files and builds lesson data from these headings:

```markdown
# Module NN: Title
### N.N - Lesson Title
#### Activity ...
```

Supported activity families:

- `MC`
- `MULTIPLE CHOICE`
- `PREDICT`
- `FITB`
- fill in the blank
- `SPOT`
- app-generated `flag` steps

Skipped classroom-only formats:

- drag/drop
- build-query
- fix-code
- sandbox
- other free-form activities not represented by the current UI

---

## Important Routes

### Main Pages

```text
/
/register
/login
/logout
/dashboard
/profile
/submissions
/course
/course/<track_key>
/lesson/<lesson_id>
/leaderboard
/articles
/articles/<slug>
/articles/new
/community
/community/submit
/community/<challenge_id>
```

### Admin Pages

```text
/admin/docker
/admin/community
/admin/articles
```

### Download Routes

```text
/downloads/re-asm-xor-checker
/downloads/crypto-rsa-starter
/downloads/pwn-ret2win
/community/<challenge_id>/download
```

### API Routes

```text
/api/complete-step
/api/check-flag-step
/api/set-theme
```

---

## Verification

Syntax-only check:

```bash
python - <<'PY'
import ast
from pathlib import Path

for path in [Path('app.py'), *Path('bytesec').glob('*.py')]:
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    print('ok', path)
PY
```

Flask smoke check:

```bash
python - <<'PY'
from bytesec import create_app

app = create_app({'TESTING': True})
client = app.test_client()

for path in ['/', '/leaderboard', '/articles']:
    print(path, client.get(path).status_code)
PY
```

Build binary labs:

```bash
make -C ctf_chall/re_asm_xor_checker
make -C ctf_chall/ret2win
```

Check managed service status:

```bash
./scripts/dev-services.sh status
```

---

## Important Notes

- `instance/` and `__pycache__/` are runtime-generated artifacts.
- The app seeds core content automatically on startup.
- Normal users cannot immediately publish articles or community challenges.
- `ctf_chall/baby_sqli/` exists in the repo, but the active SQL injection lab route uses `ctf_chall/ezsqli/`.
- `modules/rev/` is present, but the active reverse engineering track loads from `modules/reverse-engineering-assembly/`.
