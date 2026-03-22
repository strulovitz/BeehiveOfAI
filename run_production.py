"""
run_production.py — Production Server for BeehiveOfAI
=======================================================
Starts the BeehiveOfAI website using Waitress — a production-grade
web server that is safe for the public internet.

Use this file when running behind Cloudflare Tunnel (beehiveofai.com).
Use app.py directly only for local development.

Usage:
    python run_production.py

Requirements:
    - Set the BEEHIVE_SECRET_KEY environment variable before running:

      Windows Command Prompt:
        set BEEHIVE_SECRET_KEY=your-long-random-secret-key-here
        python run_production.py

      Windows PowerShell:
        $env:BEEHIVE_SECRET_KEY="your-long-random-secret-key-here"
        python run_production.py

    - Generate a good secret key by running:
        python -c "import secrets; print(secrets.token_hex(32))"
"""

import os
import sys
from waitress import serve
from app import app

HOST = '127.0.0.1'  # Localhost only — Cloudflare Tunnel connects here
PORT = 5000


def main():
    secret_key = os.environ.get('BEEHIVE_SECRET_KEY', '')

    if not secret_key or secret_key == 'dev-only-secret-key-not-for-production':
        print("=" * 60)
        print("ERROR: BEEHIVE_SECRET_KEY environment variable is not set!")
        print()
        print("To generate a secure key, run:")
        print('  python -c "import secrets; print(secrets.token_hex(32))"')
        print()
        print("Then set it before running:")
        print("  Windows Command Prompt:")
        print("    set BEEHIVE_SECRET_KEY=<your-key>")
        print("    python run_production.py")
        print()
        print("  Windows PowerShell:")
        print('    $env:BEEHIVE_SECRET_KEY="<your-key>"')
        print("    python run_production.py")
        print("=" * 60)
        sys.exit(1)

    print("=" * 60)
    print("  BeehiveOfAI — Production Server")
    print("=" * 60)
    print(f"  Server:  http://{HOST}:{PORT}")
    print(f"  Public:  https://beehiveofai.com (via Cloudflare Tunnel)")
    print(f"  Mode:    Production (Waitress)")
    print(f"  Debug:   OFF")
    print()
    print("  Press Ctrl+C to stop.")
    print("=" * 60)

    serve(app, host=HOST, port=PORT, threads=4)


if __name__ == '__main__':
    main()
