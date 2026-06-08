# ByteSec Demo Script

This folder contains a recordable browser automation flow for the ByteSec app.

## What it covers

- Landing page
- Theme toggle
- Login with the seeded demo account
- Dashboard
- Leaderboard
- Admin Docker page
- Course tabs for Web, Reverse Engineering, and Cryptography
- Representative lesson interactions for:
  - `predict`
  - `mcq`
  - `fitb`
  - `spot`
  - `flag`
- Logout

## Default credentials

- Username: `demo`
- Password: `demo123`

## Run against an already running app

```bash
python demo/bytesec_demo.py --headed --base-url http://127.0.0.1:5009
```

## Start the app automatically and then run the demo

```bash
python demo/bytesec_demo.py --headed --start-app --base-url http://127.0.0.1:5009
```

## Useful flags

- `--headed` show the browser for screen recording
- `--slow-mo 500` make interactions slower
- `--username ...` override login user
- `--password ...` override login password
- `--flag ...` override the demo flag value

## Notes

- The script is designed for demo recording, so it intentionally pauses between actions.
- It uses Playwright and Chromium.
- For the bundled seeded content, the default demo flag is `BYTESEC{196f5dee6f071643}`.
