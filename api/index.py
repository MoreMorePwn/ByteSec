import sys
import os
import traceback
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from app import app as _app

    # Vercel requires a WSGI callable named 'handler' or 'app'
    handler = _app
    app = _app
except Exception:
    tb = traceback.format_exc()
    print(f"VERCEL INIT ERROR:\n{tb}", flush=True, file=sys.stderr)
    # Re-raise so Vercel shows it in the logs
    raise
