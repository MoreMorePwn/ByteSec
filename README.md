# ByteSec

ByteSec is an interactive CTF learning platform. The first live track is Web Exploitation through SQL injection, and the app is structured to later add Reverse Engineering, Pwn, Forensics, and Cryptography tracks with the same lesson, activity, progress, Docker lab, and flag-submission model.

## Features

- Flask web app with login, registration, dashboard, course view, lesson view, leaderboard, and admin Docker controls.
- SQL injection curriculum loaded from markdown files in `modules/sqli`.
- Markdown rendering for lesson prose, tables, code fences, links, lists, emphasis, and generated SVG diagram images.
- Interactive activity types: multiple choice, predict the output, fill in the blank, spot the vulnerable line, and flag submission.
- Local EzSQLi CTF challenge packaged with Docker Compose.
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
  modules/sqli/                  Markdown curriculum source
  ctf_chall/ezsqli/              Dockerized EzSQLi challenge
  scripts/dev-services.sh        Web + CTF service runner
  instance/bytesec.db            Local SQLite database, created at runtime
```

## Requirements

- Python dependencies from `requirements.txt`.
- A virtualenv at `~/ctf_env/bin/activate` or `.venv/bin/activate`.
- Docker and Docker Compose for the EzSQLi challenge.

Install Python dependencies:

```bash
source ~/ctf_env/bin/activate
pip install -r requirements.txt
```

## Run The App And CTF

Start both the Flask app and EzSQLi challenge:

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
- Docker admin dashboard: `http://127.0.0.1:5000/admin/docker`

When running from WSL and opening the site from Windows Chrome, use the WSL IP if localhost does not work:

```bash
hostname -I | awk '{print $1}'
```

Then open:

- ByteSec: `http://<wsl-ip>:5000`
- EzSQLi: `http://<wsl-ip>:8004`

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
source ~/ctf_env/bin/activate
flask --app app ensure-db
```

Reload course modules from markdown without deleting users:

```bash
source ~/ctf_env/bin/activate
flask --app app refresh-course
```

Fully wipe and recreate the database:

```bash
source ~/ctf_env/bin/activate
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

## CTF Challenge

The active local challenge lives in:

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

The admin dashboard exposes these same CTF container controls from the web UI.

## Verification

Basic local checks:

```bash
source ~/ctf_env/bin/activate
python -m compileall -q app.py bytesec
flask --app app refresh-course
./scripts/dev-services.sh status
```

HTTP checks:

```bash
curl -fsSI http://127.0.0.1:5000/ | head -1
curl -fsSI http://127.0.0.1:8004/ | head -1
```

## Notes For Future Tracks

Keep future Reverse Engineering, Pwn, Forensics, and Cryptography tracks in the same shape:

- Markdown lessons for concept content.
- Dockerized CTF challenges for hands-on practice.
- Flag hash stored in ByteSec, not the plaintext flag.
- Admin Docker controls for challenge lifecycle.
