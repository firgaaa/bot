"""
Crée la base kfc_bot si elle n'existe pas.
Usage : python migrations/create_db.py
Depuis la racine du projet.
"""
import os
import sys
from pathlib import Path

# Ajouter la racine du projet au path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# .env à la racine du projet
load_dotenv(project_root / ".env")

DB_NAME = os.getenv("DB_NAME", "kfc_bot")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


def create_database():
    """Crée la base de données si elle n'existe pas."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database="postgres",
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (DB_NAME,),
    )
    exists = cur.fetchone()

    if not exists:
        cur.execute(f'CREATE DATABASE "{DB_NAME}"')
        print(f"[+] Base de données '{DB_NAME}' créée.")
    else:
        print(f"[i] Base de données '{DB_NAME}' existe déjà.")

    cur.close()
    conn.close()


def run_migrations():
    """Exécute les scripts SQL de migration (001, 002, ...)."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )
    conn.autocommit = True
    cur = conn.cursor()

    migrations_dir = Path(__file__).parent
    sql_files = sorted(migrations_dir.glob("*.sql"))

    for sql_path in sql_files:
        sql = sql_path.read_text(encoding="utf-8")

        # Supprimer les lignes de commentaires (-- en début de ligne)
        sql_clean = "\n".join(
            line for line in sql.split("\n")
            if not line.strip().startswith("--")
        )

        # Exécuter chaque commande SQL
        for statement in sql_clean.split(";"):
            stmt = statement.strip()
            if stmt:
                try:
                    cur.execute(stmt)
                except Exception as e:
                    err_lower = str(e).lower()
                    if "already exists" in err_lower:
                        print(f"[i] {e}")
                    elif "n'existe pas" in err_lower or "does not exist" in err_lower:
                        print(f"[i] Migration déjà appliquée ou colonne absente: {e}")
                    else:
                        raise

        print(f"[+] Migration {sql_path.name} exécutée.")

    cur.close()
    conn.close()
    print("[+] Migrations terminées.")


if __name__ == "__main__":
    create_database()
    run_migrations()
