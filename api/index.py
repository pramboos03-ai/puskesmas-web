import sys
import os

# Tambahkan direktori root ke sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Handler serverless Vercel
application = app
