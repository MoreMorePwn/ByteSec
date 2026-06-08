# ByteSec Ret2win

Beginner stack exploitation target for the Pwn course.

The binary is intentionally compiled without PIE and without stack canaries. The intended solution is to overflow the input buffer, overwrite the saved return address, and redirect execution to `win`.

## Build

```bash
make
```

## Run The Docker Service

```bash
docker compose up -d --build
nc 127.0.0.1 9001
```

## Suggested Checks

```bash
file ./ret2win
checksec --file=./ret2win
nm -n ./ret2win | grep ' win'
```
