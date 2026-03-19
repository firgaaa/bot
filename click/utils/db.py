"""
Module de connexion PostgreSQL pour API Click & Collect.
Gestion du pool de connexions et helpers.
"""
import os
from contextlib import contextmanager
from typing import Generator, Optional

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor


# Pool de connexions (initialisé à la première utilisation)
_connection_pool: Optional[pool.ThreadedConnectionPool] = None


def get_pool() -> pool.ThreadedConnectionPool:
    """Retourne ou crée le pool de connexions."""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "kfc_bot"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "root"),
        )
    return _connection_pool


@contextmanager
def get_connection() -> Generator:
    """
    Contexte manager pour obtenir une connexion du pool.
    Ferme automatiquement la connexion à la sortie.
    """
    conn = get_pool().getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        get_pool().putconn(conn)


@contextmanager
def get_cursor(dict_cursor: bool = True) -> Generator:
    """
    Contexte manager pour obtenir un curseur.
    dict_cursor=True : retourne des dict au lieu de tuples.
    """
    with get_connection() as conn:
        cursor_factory = RealDictCursor if dict_cursor else None
        cur = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cur
        finally:
            cur.close()


def init_db(app=None) -> None:
    """
    Initialise le pool à partir de la config Flask si fournie.
    À appeler au démarrage de l'application.
    """
    if app:
        os.environ.setdefault("DB_HOST", app.config.get("DB_HOST", "localhost"))
        os.environ.setdefault("DB_PORT", app.config.get("DB_PORT", "5432"))
        os.environ.setdefault("DB_NAME", app.config.get("DB_NAME", "kfc_bot"))
        os.environ.setdefault("DB_USER", app.config.get("DB_USER", "postgres"))
        os.environ.setdefault("DB_PASSWORD", app.config.get("DB_PASSWORD", "root"))
    get_pool()


def close_pool() -> None:
    """Ferme le pool de connexions (à appeler à l'arrêt)."""
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None
