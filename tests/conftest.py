# tests/conftest.py
import os, sys

# Insert the project root (one level up from tests/) into Python’s module search path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)