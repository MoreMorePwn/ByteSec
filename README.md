# ByteSec

ByteSec is a Flask-based interactive cybersecurity learning platform for CTF-style education. It includes guided courses, interactive lesson checks, Docker-backed challenge labs, community challenge submissions, article publishing with admin review, progress tracking, and leaderboards.

The current project lives in `project2/`.

## What Is Included

- Flask app factory in `bytesec/__init__.py`.
- SQLite persistence through Flask-SQLAlchemy.
- Runtime database at `instance/bytesec.db`.
- Markdown-driven course seeding from `modules/`.
- Interactive lessons with multiple choice, prediction, fill-in-the-blank, line spotting, and flag submission.
- Docker admin controls for local CTF lab services.
- Published article browsing plus article submission review.
- Community challenge browsing, download, solve, submit, and review workflows.
- Course leaderboard and community challenge leaderboard.
- User registration, login, logout, theme persistence, and profile editing.

## Live Course Tracks

The course tracks are defined in `bytesec/routes.py` and loaded from markdown plus app-generated CTF lab modules.

| Track | Modules | Content Directory |
| --- | ---: | --- |
| Web Exploitation: SQL Injection | 1-8 | `modules/sqli/` plus EzSQLi lab |
| Reverse Engineering: x86-64 Assembly | 9-13 | `modules/reverse-engineering-assembly/` plus XOR checker lab |
| Cryptography: CryptoBook Core | 14-18 | `modules/crypto/` plus RSA starter lab |
| Pwn: Stack Exploitation | 19-23 | `modules/pwn/` plus ret2win lab |
| Windows Forensics Investigation Workflow | 24-30 | `modules/forensics/` |

## Seeded Articles

The app seeds three published sample articles:

- Linux Rootkits: Hooking Models Defenders Should Recognize
- Kernel Anti-Cheats and the Security Tradeoff
- Self-XSS Still Deserves Threat Modeling

Article content is rendered with the same small markdown renderer used by lesson narratives.

## Community Challenges

The project includes imported community challenges under:

```text
ctf_chall/community/
```

Imported challenge folders:

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

Each challenge has a `challenge.yml` file. Seed logic parses:

- `name`
- `category`
- `description`
- `value`
- `flags`
- `tags`
- `files`

Multi-file challenge attachments are packed into a zip during seeding. Single-file attachments are copied as their original file. Generated runtime copies are placed under:

```text
instance/community_uploads/
```

That directory is created at runtime and should not be treated as source content.

## User Accounts

Seeded accounts:

| Username | Password | Purpose |
| --- | --- | --- |
| `demo` | `demo123` | Default admin/demo account |
| `student` | `student123` | Sample normal user with seeded progress and challenge solves |

Community uploader accounts are also seeded with password `bytesec123`:

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

Example:

```bash
BYTESEC_ADMIN_USERS=demo,teacher flask --app app run
```

## Core Workflows

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
3. Normal user submissions always save as `pending`.
4. Users can see their own article submissions and statuses on `/submissions`.
5. Admins review articles at `/admin/articles`.
6. Admins can render/preview any article from the review dashboard.
7. Admins can publish, unpublish, reject, edit, or delete articles.

Article statuses:

```text
draft
pending
published
rejected
```

### Community Challenges

1. Approved challenges are listed at `/community`.
2. Any logged-in user can submit a challenge at `/community/submit`.
3. User submissions always save as `pending`.
4. Users can see their own challenge submissions and statuses on `/submissions`.
5. Submitters and admins can preview pending/rejected challenge pages.
6. Only approved challenges are publicly listed and solvable.
7. Admins review challenges at `/admin/community`.
8. Admins can render/preview challenges from the review dashboard.
9. Community leaderboard ranks users by approved challenge solves and points.

Challenge statuses:

```text
pending
approved
rejected
```

### Account Menu

Clicking the username in the navbar opens a dropdown with:

- Edit Profile
- Dashboard
- Challenge Status
- Article Status
- Admin review links for admins
- Log Out

Profile editing is available at `/profile`.

## Project Layout

```text
project2/
  app.py
  requirements.txt
  README.md
  bytesec/
    __init__.py
    models.py
    routes.py
    seed.py
    templates/
      admin_articles.html
      admin_community.html
      admin_docker.html
      article.html
      article_form.html
      articles.html
      base.html
      community.html
      community_challenge.html
      community_submit.html
      course.html
      dashboard.html
      index.html
      leaderboard.html
      lesson.html
      login.html
      profile.html
      register.html
      submissions.html
  modules/
    crypto/
    forensics/
    pwn/
    rev/
    reverse-engineering-assembly/
    sqli/
  ctf_chall/
    baby_sqli/
    community/
    ezsqli/
    re_asm_xor_checker/
    ret2win/
  demo/
  scripts/
    dev-services.sh
```

## Main Python Modules

### `app.py`

Creates the Flask app through `create_app()` and runs it when executed directly.

Environment variables:

```text
BYTESEC_HOST
BYTESEC_PORT
```

Defaults:

```text
host = 0.0.0.0
port = 5000
```

### `bytesec/__init__.py`

Defines:

- `db = SQLAlchemy()`
- `create_app(test_config=None)`
- CLI command `init-db`
- CLI command `ensure-db`
- CLI command `refresh-course`

On app startup, `ensure_database()` runs automatically.

### `bytesec/models.py`

Defines:

- `User`
- `Module`
- `Lesson`
- `LessonStep`
- `UserProgress`
- `CommunityChallenge`
- `CommunityChallengeSolve`
- `Article`

### `bytesec/routes.py`

Defines:

- auth routes
- dashboard route
- course and lesson routes
- markdown/material rendering helpers
- Docker admin routes
- community challenge routes
- article routes
- admin review routes
- leaderboard route
- progress/theme APIs

### `bytesec/seed.py`

Handles:

- markdown curriculum parsing
- course module seeding
- generated CTF lab module seeding
- demo/admin user seeding
- sample normal user seeding
- sample article seeding
- community challenge import seeding
- sample progress and solve seeding

## Database

The app uses SQLite by default:

```text
instance/bytesec.db
```

The database is created at runtime. `instance/` is not part of the source curriculum.

Create missing data without wiping users:

```bash
flask --app app ensure-db
```

Reload course content from markdown while preserving registered users:

```bash
flask --app app refresh-course
```

Fully wipe and recreate all tables:

```bash
flask --app app init-db
```

Use `init-db` only when a reset is intended.

## Requirements

Python dependencies:

```text
Flask==3.1.0
Flask-SQLAlchemy==3.1.1
```

Install:

```bash
pip install -r requirements.txt
```

The Python interpreter must include SQLite support. If startup fails with `ModuleNotFoundError: No module named '_sqlite3'`, use a Python build that includes the SQLite extension.

Docker and Docker Compose are needed for the Docker-backed CTF labs.

GCC and Make are needed to rebuild binary artifacts.

## Run The App

Run directly:

```bash
flask --app app run --debug
```

Or:

```bash
python app.py
```

Default web app URL:

```text
http://127.0.0.1:5000
```

## Run App And CTF Services

The helper script manages the Flask app and Docker CTF services:

```bash
./scripts/dev-services.sh start
./scripts/dev-services.sh status
./scripts/dev-services.sh logs
./scripts/dev-services.sh restart
./scripts/dev-services.sh stop
```

Default service locations:

| Service | URL or endpoint |
| --- | --- |
| ByteSec web app | `http://127.0.0.1:5000` |
| EzSQLi challenge | `http://127.0.0.1:8004` |
| Ret2win challenge | `nc 127.0.0.1 9001` |
| Docker admin dashboard | `http://127.0.0.1:5000/admin/docker` |

When running from WSL and opening from Windows, use the WSL IP if `localhost` does not work:

```bash
hostname -I | awk '{print $1}'
```

Then open:

```text
http://<wsl-ip>:5000
http://<wsl-ip>:8004
nc <wsl-ip> 9001
```

## CTF Labs

### EzSQLi

Path:

```text
ctf_chall/ezsqli/
```

Direct commands:

```bash
cd ctf_chall/ezsqli
docker compose up -d --build
docker compose ps
docker compose logs --tail=80
docker compose down
```

### XOR Flag Checker

Path:

```text
ctf_chall/re_asm_xor_checker/
```

Direct commands:

```bash
cd ctf_chall/re_asm_xor_checker
make
./xor_checker
```

The app also exposes a download route:

```text
/downloads/re-asm-xor-checker
```

### RSA Starter

The RSA starter is generated by the app and exposed as a download route:

```text
/downloads/crypto-rsa-starter
```

### Ret2win

Path:

```text
ctf_chall/ret2win/
```

Direct commands:

```bash
cd ctf_chall/ret2win
docker compose up -d --build
docker compose ps
nc 127.0.0.1 9001
docker compose down
```

The app also exposes a download route:

```text
/downloads/pwn-ret2win
```

## Curriculum Parser Rules

The parser in `bytesec/seed.py` reads markdown and creates course content.

Module heading:

```markdown
# Module NN: Title
```

Lesson heading:

```markdown
### N.N - Lesson Title
```

Activity heading:

```markdown
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

Skipped classroom-only activity families:

- drag/drop
- build-query
- fix-code
- sandbox
- other free-form activities not represented by current UI controls

## Rendering Support

The app includes a small markdown renderer for lesson and article material.

Supported content:

- headings
- paragraphs
- links
- inline code
- bold and italic text
- unordered lists
- ordered lists
- blockquotes
- tables
- code fences
- horizontal rules
- simple diagram-like code blocks rendered as SVG images

## Important Routes

Public or auth routes:

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

Admin routes:

```text
/admin/docker
/admin/community
/admin/articles
```

Download routes:

```text
/downloads/re-asm-xor-checker
/downloads/crypto-rsa-starter
/downloads/pwn-ret2win
/community/<challenge_id>/download
```

API routes:

```text
/api/complete-step
/api/check-flag-step
/api/set-theme
```

## Verification

Syntax-only check without writing bytecode:

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

Check service status:

```bash
./scripts/dev-services.sh status
```

## Notes

- `instance/` and `__pycache__/` are runtime/generated artifacts.
- The app seeds content automatically on startup.
- Normal users cannot publish articles immediately.
- Normal users cannot publish community challenges immediately.
- Admins can render article and community challenge submissions before approving or rejecting them.
- Course leaderboard rows start with the normal surface background and use blue-green highlighting on hover.
- `ctf_chall/baby_sqli/` is present but the active SQL injection lab route uses `ctf_chall/ezsqli/`.
- `modules/rev/` is present, but the active reverse engineering course track is loaded from `modules/reverse-engineering-assembly/`.
