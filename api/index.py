import sys
import os

# Tambahkan direktori root proyek ke sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Middleware untuk membersihkan prefix /api/index yang dikirimkan oleh rewrite Vercel
class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        if path.startswith('/api/index'):
            new_path = path[len('/api/index'):]
            environ['PATH_INFO'] = new_path if new_path else '/'
        return self.app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
application = app
