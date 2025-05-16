import os
from pathlib import Path

from dotenv import load_dotenv

# load .env (project root) before anything else 
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug mode can still be toggled via FLASK_ENV or here
    app.run(debug=True)
