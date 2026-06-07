# ByteSec

ByteSec is an interactive CTF learning platform. The first live track is Web Exploitation through SQL injection modules, and the app is structured to later add Reverse Engineering, Pwn, Forensics, and Cryptography tracks with the same lesson, activity, progress, and lab model.

## What Is Included

- Flask web app with login, registration, course dashboard, progress tracking, and lesson activities.
- SQL injection curriculum parsed from `modules/sqli/*.md`.
- A local Baby SQLi Docker challenge used by the final CTF module.
- Service helper script that starts and stops both the web app and the challenge.

## Requirements

- Python dependencies from `requirements.txt`.
- A virtualenv at `~/ctf_env/bin/activate` or `.venv/bin/activate`.
- Docker and Docker Compose for the Baby SQLi challenge.

Install dependencies:

```bash
source ~/ctf_env/bin/activate
pip install -r requirements.txt
```

## Run The App And Challenge

Start both services:

```bash
./scripts/dev-services.sh start
```

Useful commands:

```bash
./scripts/dev-services.sh status
./scripts/dev-services.sh logs
./scripts/dev-services.sh restart
./scripts/dev-services.sh stop
```

Default URLs:

- ByteSec web app: `http://127.0.0.1:5000`
- Baby SQLi challenge: `http://127.0.0.1:8004`

When running from WSL and opening the site from Windows Chrome, use the WSL IP if localhost does not work:

```bash
hostname -I | awk '{print $1}'
```

Then open `http://<wsl-ip>:5000` for ByteSec and `http://<wsl-ip>:8004` for the challenge.

## Login

The seed data includes a demo account:

- Username: `demo`
- Password: `demo123`

Registered users are stored in `instance/bytesec.db`.

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

Use `init-db` only when a full reset is intended. Normal restarts through `dev-services.sh` use `ensure-db`, so users are not wiped every restart.

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

`modules/sqli/00-course-overview.md` is documentation for the curriculum structure and is not seeded as an app module.

The app adds module 8 separately as the local Baby SQLi CTF flag submission lab.
