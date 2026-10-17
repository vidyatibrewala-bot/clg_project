import os
import sys

# Add project root directory to sys.path so server.py and database.py are importable
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from server import app

# Expose WSGI application callable for Vercel Serverless runtime
__all__ = ["app"]
