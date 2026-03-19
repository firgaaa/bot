"""
Lancement de l'API Flask Click & Collect KFC.

Usage : python run.py
"""
import sys
from pathlib import Path

# S'assurer que la racine du projet est dans le path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from app import app

if __name__ == "__main__":
    app.run(debug=True)
