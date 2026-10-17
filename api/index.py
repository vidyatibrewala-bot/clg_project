import os
import sys
from urllib.parse import parse_qs, urlencode

# Add project root directory to sys.path so server.py and database.py are importable
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from server import app


class VercelPathFixMiddleware:
    """
    WSGI Middleware to restore original request paths on Vercel.
    
    When Vercel rewrites requests with:
      "source": "/(.*)", "destination": "/api/index?__path=$1"
    it passes the captured original URL in query param '__path'.
    This middleware restores PATH_INFO and cleans up QUERY_STRING so
    Flask routes and request.args match accurately.
    """

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        query_string = environ.get("QUERY_STRING", "")
        params = parse_qs(query_string, keep_blank_values=True)

        if "__path" in params:
            raw_path = params["__path"][0].strip() if params["__path"] else ""
            if not raw_path or not raw_path.startswith("/"):
                raw_path = "/" + raw_path
            environ["PATH_INFO"] = raw_path

            # Clean up __path from QUERY_STRING
            remaining = {k: v for k, v in params.items() if k != "__path"}
            environ["QUERY_STRING"] = urlencode(remaining, doseq=True)
        elif environ.get("PATH_INFO") in ("/api/index", "/api/index.py", "/api/index/"):
            environ["PATH_INFO"] = "/"

        return self.wsgi_app(environ, start_response)


# Wrap Flask with path restoration middleware
app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)

__all__ = ["app"]
