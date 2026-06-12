import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Vercel needs 'app' at top module level (static analysis)
from app import app

# WSGI handler for Vercel
handler = app
