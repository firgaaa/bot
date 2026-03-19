"""
Service de gestion du panier (articles fidélité).
"""
import json
from typing import Optional, Tuple

from utils.db import get_cursor
from utils.locks import session_lock


def get_item_cost_quantity(session_id: int, item_uuid: str) -> Optional[Tuple[int, int]]:
    """Récupère le coût et la quantité d'un article avant suppression. Retourne (cost, quantity) ou None."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT cost, quantity FROM session_items WHERE session_id = %s AND item_uuid = %s",
            (session_id, item_uuid),
        )
        row = cur.fetchone()
        if row:
            return (int(row["cost"]), int(row["quantity"]))
        return None


def add_item_to_session(
    session_id: int,
    item_uuid: str,
    loyalty_id: str,
    name: Optional[str],
    cost: int,
    quantity: int,
    modgrps: list,
) -> None:
    """Enregistre un article dans session_items (historique)."""
    modgrps_json = json.dumps(modgrps) if modgrps else "[]"
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO session_items (session_id, item_uuid, loyalty_id, name, cost, quantity, modgrps)
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
            """,
            (session_id, item_uuid, loyalty_id, name or "", cost, quantity, modgrps_json),
        )


def remove_item_from_session(session_id: int, item_uuid: str) -> bool:
    """Supprime un article de session_items. Retourne True si supprimé."""
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM session_items WHERE session_id = %s AND item_uuid = %s",
            (session_id, item_uuid),
        )
        return cur.rowcount > 0
