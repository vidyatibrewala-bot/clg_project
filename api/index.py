import os
import sys

# Add project root directory to sys.path so server.py and database.py are importable
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from server import app


class VercelPathFixMiddleware:
    """
    WSGI Middleware to restore original request paths on Vercel.
    
    When Vercel rewrites requests (e.g. /(.*) -> /api/index),
    it passes the destination path (/api/index) into PATH_INFO while storing
    the original client URL in headers like HTTP_X_MATCHED_PATH or HTTP_X_VERCEL_PATH.
    This middleware restores the real PATH_INFO so Flask routes match accurately.
    """

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # Retrieve original path from Vercel edge proxy headers
        raw_path = (
            environ.get("HTTP_X_MATCHED_PATH")
            or environ.get("HTTP_X_VERCEL_PATH")
            or environ.get("HTTP_X_FORWARDED_URI")
            or environ.get("HTTP_X_ORIGINAL_URI")
        )

        if raw_path:
            # Strip query string if embedded in the header
            clean_path = raw_path.split("?", 1)[0]
            if clean_path:
                environ["PATH_INFO"] = clean_path

        # Fallback: if PATH_INFO is /api/index, treat it as root /
        current_path = environ.get("PATH_INFO", "")
        if current_path in ("/api/index", "/api/index.py", "/api/index/"):
            environ["PATH_INFO"] = "/"

        return self.wsgi_app(environ, start_response)


# Wrap Flask with path restoration middleware
app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)

__all__ = ["app"]
