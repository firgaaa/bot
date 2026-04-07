"""
Exporte toutes les lignes de kfc_storage : customer_id, email, password uniquement.

Sortie par défaut : JSONL (une ligne JSON par compte) — rapide à relire ligne par ligne.

Usage :
  python export_kfc_credentials.py
  python export_kfc_credentials.py -o /credentials.jsonl

Charge le .env à la racine du dépôt BOT (parent de insert/).

Dépendances : pip install python-dotenv psycopg2-binary
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("Installez psycopg2-binary : pip install psycopg2-binary", file=sys.stderr)
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore[misc, assignment]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_env() -> None:
    if load_dotenv:
        load_dotenv(repo_root() / ".env")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export kfc_storage (customer_id, email, password)")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "kfc_credentials.jsonl",
        help="Fichier de sortie JSONL",
    )
    args = parser.parse_args()

    load_env()
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL manquant (.env à la racine du repo)", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    out_path = args.output.resolve()

    sql = """
        SELECT customer_id, email, password
        FROM kfc_storage
        ORDER BY customer_id
    """

    t0 = time.perf_counter()
    count = 0
    # Curseur nommé = itération serveur (nécessite une transaction, pas autocommit)
    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor(name="export_kfc_cred", cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.itersize = 5000
            cur.execute(sql)
            with open(out_path, "w", encoding="utf-8", newline="\n") as f:
                for row in cur:
                    rec = {
                        "customer_id": row["customer_id"],
                        "email": row["email"],
                        "password": row["password"],
                    }
                    f.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")))
                    f.write("\n")
                    count += 1
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()

    elapsed = time.perf_counter() - t0
    size_b = out_path.stat().st_size if out_path.is_file() else 0

    print()
    print("— Résumé export kfc_storage —")
    print(f"  Lignes écrites     : {count}")
    print(f"  Durée (export)     : {elapsed:.3f} s")
    if count > 0 and elapsed > 0:
        print(f"  Débit              : {count / elapsed:.0f} lignes/s")
    print(f"  Fichier            : {out_path}")
    print(f"  Dossier            : {out_path.parent}")
    print(f"  Taille fichier     : {size_b:,} octets ({size_b / 1024:.1f} Ko)")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
