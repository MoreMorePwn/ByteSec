# ByteSec

ByteSec is an interactive CTF learning platform. The live tracks are Web Exploitation through SQL injection, Reverse Engineering through x86-64 assembly, Cryptography through CryptoBook-inspired core lessons, and Pwn through stack exploitation. The app is structured to later add Forensics with the same lesson, activity, progress, lab, and flag-submission model.

## Features

- Flask web app with login, registration, dashboard, course view, lesson view, leaderboard, and admin Docker controls.
- SQL injection curriculum loaded from markdown files in `modules/sqli`.
- Reverse engineering assembly curriculum loaded from markdown files in `modules/reverse-engineering-assembly`.
- Cryptography curriculum loaded from markdown files in `modules/crypto`.
- Pwn curriculum loaded from markdown files in `modules/pwn`.
- Markdown rendering for lesson prose, tables, code fences, links, lists, emphasis, and generated SVG diagram images.
- Interactive activity types: multiple choice, predict the output, fill in the blank, spot the vulnerable line, and flag submission.
- EzSQLi CTF challenge packaged with Docker Compose.
- XOR flag-checker reverse engineering challenge.
- Ret2win Pwn challenge packaged with Docker Compose.
- User progress tracking in SQLite.
- Service helper script to run the Flask app and CTF challenge together.

## Project Layout

```text
ByteSec/
  app.py                         Flask entrypoint
  bytesec/
    __init__.py                  App factory, CLI commands
    models.py                    SQLAlchemy models
    routes.py                    Views, APIs, renderers, admin Docker actions
    seed.py                      Markdown parser and database seeding
    templates/                   Jinja templates
  modules/sqli/                  SQL injection markdown curriculum source
  modules/reverse-engineering-assembly/
                                  Reverse engineering assembly markdown curriculum source
  modules/crypto/                Cryptography markdown curriculum source
  modules/pwn/                   Pwn markdown curriculum source
  ctf_chall/ezsqli/              Dockerized EzSQLi challenge
  ctf_chall/re_asm_xor_checker/  XOR flag-checker challenge
  ctf_chall/ret2win/             Dockerized ret2win challenge
  scripts/dev-services.sh        Web + CTF service runner
  instance/bytesec.db            SQLite database, created at runtime
```

## Requirements

- Python dependencies from `requirements.txt`.
- A Python virtual environment.
- Docker and Docker Compose for the EzSQLi and ret2win challenges.
- GCC and Make for rebuilding binary challenge artifacts.

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Run The App And CTF

Start the Flask app and Docker challenge services:

```bash
./scripts/dev-services.sh start
```

Manage services:

```bash
./scripts/dev-services.sh status
./scripts/dev-services.sh logs
./scripts/dev-services.sh restart
./scripts/dev-services.sh stop
```

Default URLs:

- ByteSec web app: `http://127.0.0.1:5000`
- EzSQLi challenge: `http://127.0.0.1:8004`
- Ret2win challenge: `nc 127.0.0.1 9001`
- Docker admin dashboard: `http://127.0.0.1:5000/admin/docker`

When running from WSL and opening the site from Windows Chrome, use the WSL IP if localhost does not work:

```bash
hostname -I | awk '{print $1}'
```

Then open:

- ByteSec: `http://<wsl-ip>:5000`
- EzSQLi: `http://<wsl-ip>:8004`
- Ret2win: `nc <wsl-ip> 9001`

## Accounts And Admin Access

The seed data includes:

- Username: `demo`
- Password: `demo123`

Admin Docker access is controlled by `BYTESEC_ADMIN_USERS`, a comma-separated list of usernames. If unset, it defaults to `demo`.

Example:

```bash
BYTESEC_ADMIN_USERS=demo,teacher ./scripts/dev-services.sh start
```

## Database Commands

Create missing tables and seed content only when needed:

```bash
flask --app app ensure-db
```

Reload course modules from markdown without deleting users:

```bash
flask --app app refresh-course
```

Fully wipe and recreate the database:

```bash
flask --app app init-db
```

Use `init-db` only when a full reset is intended. Normal restarts through `dev-services.sh` use `ensure-db`, so registered users are not wiped every restart.

## Curriculum Source

SQL injection modules are parsed from:

```text
modules/sqli/01-sql-fundamentals.md
modules/sqli/02-web-apps-and-databases.md
modules/sqli/03-your-first-injection.md
modules/sqli/04-types-of-sql-injection.md
modules/sqli/05-exploitation-techniques.md
modules/sqli/06-defense-and-prevention.md
modules/sqli/07-real-world-cases-final-challenge.md
```

`modules/sqli/00-course-overview.md` documents the curriculum shape and is not seeded as an app module.

The app adds module 8 separately as the EzSQLi CTF flag-submission lab.

Reverse engineering assembly modules are parsed from:

```text
modules/reverse-engineering-assembly/09-assembly-foundations.md
modules/reverse-engineering-assembly/10-stack-calls-and-parameters.md
modules/reverse-engineering-assembly/11-control-flow-memory-and-xor.md
modules/reverse-engineering-assembly/12-reversing-flag-checker-workflow.md
```

`modules/reverse-engineering-assembly/00-course-overview.md` documents the curriculum shape and is not seeded as an app module.

The app adds module 13 separately as the XOR Flag Checker flag-submission lab.

Cryptography modules are parsed from:

```text
modules/crypto/14-crypto-fundamentals.md
modules/crypto/15-number-theory.md
modules/crypto/16-asymmetric-cryptography.md
modules/crypto/17-symmetric-cryptography.md
```

`modules/crypto/00-course-overview.md` documents the curriculum shape and is not seeded as an app module.

The app adds module 18 separately as the RSA Starter flag-submission lab.

Pwn modules are parsed from:

```text
modules/pwn/19-pwn-foundations.md
modules/pwn/20-stack-overflows-and-control-data.md
modules/pwn/21-building-a-ret2win-exploit.md
modules/pwn/22-mitigations-and-exploit-workflow.md
```

`modules/pwn/00-course-overview.md` documents the curriculum shape and is not seeded as an app module.

The app adds module 23 separately as the Ret2win flag-submission lab.

## Markdown Parsing Rules

The parser in `bytesec/seed.py` reads each module markdown file and creates:

- `# Module NN: Title` as a course module.
- `### N.N - Lesson Title` as a lesson.
- Supported `#### Activity` blocks as lesson steps.

Supported activity types:

- `MC` or `MULTIPLE CHOICE`
- `PREDICT`
- `FITB` or fill in the blank
- `SPOT`
- `flag`, added by the app for the final CTF module

Unsupported classroom-only activity types such as drag/drop, build-query, and free-form fix-code activities are skipped instead of being shown as placeholder tasks.

## CTF Challenges

The active SQL injection challenge lives in:

```text
ctf_chall/ezsqli/
```

It is a Django app backed by SQLite. Docker Compose maps it to port `8004`.

Useful direct commands:

```bash
cd ctf_chall/ezsqli
docker compose up -d --build
docker compose ps
docker compose logs --tail=80
docker compose down
```

The admin dashboard exposes Docker controls for the active CTF services from the web UI.

The reverse engineering challenge lives in:

```text
ctf_chall/re_asm_xor_checker/
```

Build and run it directly:

```bash
cd ctf_chall/re_asm_xor_checker
make
./xor_checker
```

The ret2win challenge runs as a TCP service through Docker Compose:

```bash
cd ctf_chall/ret2win
docker compose up -d --build
docker compose ps
nc 127.0.0.1 9001
docker compose down
```

## Verification

Basic checks:

```bash
python -m compileall -q app.py bytesec
flask --app app refresh-course
make -C ctf_chall/re_asm_xor_checker
make -C ctf_chall/ret2win
./scripts/dev-services.sh status
```

HTTP checks:

```bash
curl -fsSI http://127.0.0.1:5000/ | head -1
curl -fsSI http://127.0.0.1:8004/ | head -1
printf 'test\n' | nc -w 2 127.0.0.1 9001
```

## Notes For Future Tracks

Keep future Forensics tracks in the same shape:

- Markdown lessons for concept content.
- Dockerized CTF challenges for hands-on practice.
- Flag hash stored in ByteSec, not the plaintext flag.
- Admin Docker controls for challenge lifecycle.
