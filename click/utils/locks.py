"""
Verrous par user_id pour éviter les accès concurrents sur une même session.
"""
import threading
from contextlib import contextmanager
from typing import Generator


_locks: dict[str, threading.Lock] = {}
_locks_mutex = threading.Lock()


def get_lock(user_id: str) -> threading.Lock:
    """Retourne le verrou pour un user_id (créé si nécessaire)."""
    with _locks_mutex:
        if user_id not in _locks:
            _locks[user_id] = threading.Lock()
        return _locks[user_id]


@contextmanager
def session_lock(user_id: str) -> Generator[None, None, None]:
    """
    Contexte manager pour verrouiller les opérations sur une session.
    À utiliser pour toutes les actions d'écriture (create, update, delete, add item, etc.).
    """
    lock = get_lock(user_id)
    lock.acquire()
    try:
        yield
    finally:
        lock.release()
