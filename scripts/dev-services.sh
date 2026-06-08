#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT_DIR/.run"
LOG_DIR="$ROOT_DIR/logs"
WEB_PID_FILE="$RUN_DIR/bytesec-web.pid"
WEB_LOG="$LOG_DIR/bytesec-web.log"
CTF_DIR="$ROOT_DIR/ctf_chall/ezsqli"
PWN_CTF_DIR="$ROOT_DIR/ctf_chall/ret2win"
LEGACY_CTF_DIR="$ROOT_DIR/ctf_chall/baby_sqli"

WEB_HOST="${BYTESEC_HOST:-0.0.0.0}"
WEB_PORT="${BYTESEC_PORT:-5000}"
WEB_ACCESS_HOST="${BYTESEC_ACCESS_HOST:-127.0.0.1}"
WEB_URL="http://${WEB_ACCESS_HOST}:${WEB_PORT}"
CTF_URL="${BYTESEC_CTF_URL:-http://127.0.0.1:8004}"
PWN_CTF_ENDPOINT="${BYTESEC_PWN_CTF_ENDPOINT:-nc 127.0.0.1 9001}"

mkdir -p "$RUN_DIR" "$LOG_DIR"

venv_activate() {
  if [ -f "$ROOT_DIR/.venv/bin/activate" ]; then
    printf '%s\n' "$ROOT_DIR/.venv/bin/activate"
  elif [ -n "${VIRTUAL_ENV:-}" ] && [ -f "$VIRTUAL_ENV/bin/activate" ]; then
    printf '%s\n' "$VIRTUAL_ENV/bin/activate"
  elif [ -f "$HOME/ctf_env/bin/activate" ]; then
    printf '%s\n' "$HOME/ctf_env/bin/activate"
  else
    printf 'No virtualenv found. Create .venv in the project root or activate one before running this script.\n' >&2
    return 1
  fi
}

docker_ready() {
  docker info >/dev/null 2>&1
}

web_running() {
  [ -f "$WEB_PID_FILE" ] && kill -0 "$(cat "$WEB_PID_FILE")" >/dev/null 2>&1
}

web_responding() {
  command -v curl >/dev/null 2>&1 && curl -fsS "$WEB_URL" >/dev/null 2>&1
}

start_ctf() {
  if ! docker_ready; then
    printf 'Docker daemon is not reachable. Start Docker first, then rerun this command.\n' >&2
    return 1
  fi
  (cd "$CTF_DIR" && docker compose up -d --build)
  (cd "$PWN_CTF_DIR" && docker compose up -d --build)
}

stop_ctf() {
  if docker_ready; then
    (cd "$CTF_DIR" && docker compose down)
    (cd "$PWN_CTF_DIR" && docker compose down)
    if [ -d "$LEGACY_CTF_DIR" ]; then
      (cd "$LEGACY_CTF_DIR" && docker compose down) >/dev/null 2>&1 || true
    fi
  else
    printf 'Docker daemon is not reachable; skipped CTF shutdown.\n' >&2
  fi
}

start_web() {
  if web_running; then
    printf 'ByteSec web app is already running at %s (pid %s).\n' "$WEB_URL" "$(cat "$WEB_PID_FILE")"
    return 0
  fi
  if web_responding; then
    printf 'ByteSec web app is already responding at %s (unmanaged external process).\n' "$WEB_URL"
    return 0
  fi

  local activate
  activate="$(venv_activate)"

  (
    cd "$ROOT_DIR"
    source "$activate"
    flask --app app ensure-db
    if command -v setsid >/dev/null 2>&1; then
      setsid -f env BYTESEC_HOST="$WEB_HOST" BYTESEC_PORT="$WEB_PORT" python app.py >"$WEB_LOG" 2>&1
      sleep 0.5
      pgrep -f "python app.py" | while read -r pid; do
        if [ "$(readlink -f "/proc/$pid/cwd" 2>/dev/null || true)" = "$ROOT_DIR" ]; then
          printf '%s\n' "$pid" >"$WEB_PID_FILE"
          break
        fi
      done
    else
      BYTESEC_HOST="$WEB_HOST" BYTESEC_PORT="$WEB_PORT" nohup python app.py >"$WEB_LOG" 2>&1 &
      printf '%s\n' "$!" >"$WEB_PID_FILE"
    fi
  )

  for _ in 1 2 3 4 5; do
    if web_responding; then
      break
    fi
    sleep 1
  done

  if web_responding; then
    printf 'ByteSec web app started at %s (pid %s).\n' "$WEB_URL" "$(cat "$WEB_PID_FILE")"
  else
    printf 'ByteSec web app failed to start. Check %s.\n' "$WEB_LOG" >&2
    return 1
  fi
}

stop_web() {
  if web_running; then
    kill "$(cat "$WEB_PID_FILE")"
    rm -f "$WEB_PID_FILE"
    printf 'ByteSec web app stopped.\n'
  else
    rm -f "$WEB_PID_FILE"
    printf 'ByteSec web app is not running.\n'
  fi
}

status_services() {
  if web_running; then
    printf 'web: running at %s (pid %s)\n' "$WEB_URL" "$(cat "$WEB_PID_FILE")"
  elif web_responding; then
    printf 'web: running at %s (unmanaged external process)\n' "$WEB_URL"
  else
    printf 'web: stopped\n'
  fi

  if docker_ready; then
    printf 'ctf: docker reachable\n'
    printf 'web ctf target: %s\n' "$CTF_URL"
    (cd "$CTF_DIR" && docker compose ps)
    printf 'pwn ctf target: %s\n' "$PWN_CTF_ENDPOINT"
    (cd "$PWN_CTF_DIR" && docker compose ps)
  else
    printf 'ctf: docker daemon not reachable\n'
  fi
}

show_logs() {
  printf '== ByteSec web log ==\n'
  if [ -f "$WEB_LOG" ]; then
    tail -n 80 "$WEB_LOG"
  else
    printf 'No web log yet: %s\n' "$WEB_LOG"
  fi

  printf '\n== EzSQLi Docker logs ==\n'
  if docker_ready; then
    (cd "$CTF_DIR" && docker compose logs --tail=80)
  else
    printf 'Docker daemon is not reachable.\n'
  fi

  printf '\n== Ret2win Docker logs ==\n'
  if docker_ready; then
    (cd "$PWN_CTF_DIR" && docker compose logs --tail=80)
  else
    printf 'Docker daemon is not reachable.\n'
  fi
}

start_all() {
  local ctf_status=0
  start_ctf || ctf_status=$?
  start_web
  printf '\nByteSec web: %s\n' "$WEB_URL"
  if [ "$WEB_HOST" = "0.0.0.0" ]; then
    local wsl_ip
    wsl_ip="$(hostname -I 2>/dev/null | awk '{print $1}')"
    if [ -n "$wsl_ip" ]; then
      printf 'ByteSec web from Windows fallback: http://%s:%s\n' "$wsl_ip" "$WEB_PORT"
    fi
  fi
  printf 'EzSQLi CTF: %s\n' "$CTF_URL"
  printf 'Ret2win CTF: %s\n' "$PWN_CTF_ENDPOINT"
  if [ "$ctf_status" -ne 0 ]; then
    printf 'CTF Docker lab did not start because Docker is not reachable.\n' >&2
    return "$ctf_status"
  fi
}

case "${1:-start}" in
  start)
    start_all
    ;;
  stop)
    stop_web
    stop_ctf
    ;;
  restart)
    stop_web
    stop_ctf
    start_all
    ;;
  status)
    status_services
    ;;
  logs)
    show_logs
    ;;
  *)
    printf 'Usage: %s {start|stop|restart|status|logs}\n' "$0" >&2
    exit 2
    ;;
esac
