# ByteSec

<div align="center">
  <h3>Interactive cybersecurity learning platform for guided lessons, graded activities, and CTF-style practice labs.</h3>
  <p>Built with Flask, markdown course content, and integrated challenge services for hands-on security education.</p>
</div>

---

# Interactive Cybersecurity Learning Platform

ByteSec is a web platform for learning cybersecurity through guided modules, short activity checks, article publishing, community challenge sharing, and hands-on challenge practice. It brings structured lesson flow and CTF-style exercises into one interface for both learners and admins.

---

## Overview

| Item | Details |
| --- | --- |
| Name | ByteSec |
| Type | Web-based cybersecurity learning platform |
| Stack | Flask, Flask-SQLAlchemy, Jinja, Tailwind CSS, SQLite, optional Turso |
| Focus | Web exploitation, reverse engineering, cryptography, pwn, and Windows forensics |
| Activity Types | Multiple choice, predict the output, fill in the blank, spot the vulnerable line, flag submission |
| Included Areas | Courses, articles, community challenges, leaderboards, profile management, and admin review pages |

---

## Features

- Guided course tracks loaded from `modules/`
- Interactive lesson checks with immediate feedback
- Multiple activity formats for concept validation and hands-on practice
- Downloadable challenge materials and challenge service integration
- Course progress tracking and leaderboard support
- Article submission and review workflow
- Community challenge submission, review, approval, and solve flow
- Theme toggle, authentication, and profile editing
- Admin surfaces for article, challenge, and service management

---

## Problem Solved

Security learning often gets split across slide decks, notes, challenge portals, and separate practice environments. ByteSec closes that gap by combining structured explanation, interactive checking, and challenge practice in one application so learners can move from concept to execution without changing tools.

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

## Demo Account

| Username | Password | Access |
| --- | --- | --- |
| `demo` | `demo123` | Demo account with admin access |

---

## Screenshots

The gallery below was captured with Playwright using [`demo/capture_readme_screenshots.py`](demo/capture_readme_screenshots.py).

### Public Pages

| Landing | Sign In | Register |
| --- | --- | --- |
| <img src="docs/screenshots/landing.jpg" alt="ByteSec landing page" width="100%"> | <img src="docs/screenshots/login.jpg" alt="ByteSec sign in page" width="100%"> | <img src="docs/screenshots/register.jpg" alt="ByteSec registration page" width="100%"> |

### Learning Flow

| Dashboard | Course Catalog | Course Track |
| --- | --- | --- |
| <img src="docs/screenshots/dashboard.jpg" alt="ByteSec dashboard" width="100%"> | <img src="docs/screenshots/course-catalog.jpg" alt="ByteSec course catalog" width="100%"> | <img src="docs/screenshots/course-track-web.jpg" alt="ByteSec web track page" width="100%"> |

| Multiple Choice | Predict | Fill in the Blank |
| --- | --- | --- |
| <img src="docs/screenshots/lesson-mcq.jpg" alt="Multiple choice lesson activity" width="100%"> | <img src="docs/screenshots/lesson-predict.jpg" alt="Predict the output lesson activity" width="100%"> | <img src="docs/screenshots/lesson-fitb.jpg" alt="Fill in the blank lesson activity" width="100%"> |

| Spot the Vulnerability | Flag Submission | Leaderboard |
| --- | --- | --- |
| <img src="docs/screenshots/lesson-spot.jpg" alt="Spot the vulnerability lesson activity" width="100%"> | <img src="docs/screenshots/lesson-flag.jpg" alt="Flag submission lesson activity" width="100%"> | <img src="docs/screenshots/leaderboard.jpg" alt="ByteSec leaderboard page" width="100%"> |

### Articles and Community

| Articles | Article Detail | New Article |
| --- | --- | --- |
| <img src="docs/screenshots/articles.jpg" alt="Articles page" width="100%"> | <img src="docs/screenshots/article-detail.jpg" alt="Article detail page" width="100%"> | <img src="docs/screenshots/article-new.jpg" alt="New article page" width="100%"> |

| Community | Challenge Detail | Submit Challenge |
| --- | --- | --- |
| <img src="docs/screenshots/community.jpg" alt="Community challenges page" width="100%"> | <img src="docs/screenshots/community-detail.jpg" alt="Community challenge detail page" width="100%"> | <img src="docs/screenshots/community-submit.jpg" alt="Community challenge submission page" width="100%"> |

### Account and Admin Pages

| Submissions | Profile |
| --- | --- |
| <img src="docs/screenshots/submissions.jpg" alt="Submissions page" width="100%"> | <img src="docs/screenshots/profile.jpg" alt="Profile page" width="100%"> |

| Admin Articles | Admin Community | Admin Docker |
| --- | --- | --- |
| <img src="docs/screenshots/admin-articles.jpg" alt="Admin articles page" width="100%"> | <img src="docs/screenshots/admin-community.jpg" alt="Admin community page" width="100%"> | <img src="docs/screenshots/admin-docker.jpg" alt="Admin docker page" width="100%"> |

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

- SQLite
- Optional Turso via the bundled pure-Python HTTP driver
- Runtime data under `instance/`
- Vercel-compatible entrypoint in `api/index.py`

### Content and Tooling

- Markdown course modules
- Docker Compose
- GCC and Make
- Playwright for README screenshot capture

---

## Prerequisites

Make sure these are installed on your machine:

- Python with SQLite support
- `pip`
- Docker and Docker Compose
- GCC and Make

If startup fails with `ModuleNotFoundError: No module named '_sqlite3'`, use a Python build that includes SQLite.

---

## How to Run

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

## Run App and Challenge Services

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

When running from WSL and opening from Windows, you may need the WSL IP instead of the default loopback address:

```bash
hostname -I | awk '{print $1}'
```

---

## Made by Kelompok 4

| Name | Student ID |
| --- | --- |
| Jonathan Irvin Susanto | 2802440430 |
| Owen Ourelio Bong | 2802461196 |
| Huang Earl Gunawan | 2802444523 |
| Haikal Satrio Dewandaru | 2802459600 |
| Fathia Ramadhanti Hardianto | 2802477414 |
