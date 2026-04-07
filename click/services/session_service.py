"""
Service de gestion des sessions.
"""
import json
from typing import Any, Optional, Tuple

from models.session import Session
from utils.db import get_cursor
from utils.locks import session_lock


def create_session(
    panier_id: str,
    account_id: str,
    account_token: str,
    store_id: str,
    balance_user: int,
    store_name: Optional[str] = None,
    store_city: Optional[str] = None,
    telegram_id: Optional[str] = None,
    basket_id: Optional[str] = None,
    create_basket: bool = True,
) -> Tuple[Optional[Session], Optional[str]]:
    """
    Crée une session pour le panier_id.
    Retourne (session, None) en cas de succès.
    Retourne (None, "SESSION_ALREADY_EXISTS") si session existe déjà.
    Retourne (None, "KFC_API_ERROR") si échec création panier KFC.
    """
    with session_lock(panier_id):
        with get_cursor() as cur:
            cur.execute(
                "SELECT id FROM sessions WHERE panier_id = %s",
                (panier_id,),
            )
            if cur.fetchone():
                return None, "SESSION_ALREADY_EXISTS"

            # Créer le panier KFC si nécessaire
            if not basket_id and create_basket:
                try:
                    from ressource import basket
                    basket_id = basket.NewBasket(store_id, account_token)
                except Exception:
                    basket_id = None
                if not basket_id:
                    return None, "KFC_API_ERROR"

            cur.execute(
                """
                INSERT INTO sessions (
                    panier_id, account_id, account_token,
                    store_id, store_name, store_city, basket_id, status,
                    balance_user, balance_basket, telegram_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'DRAFT', %s, 0, %s)
                RETURNING id, panier_id, account_id, account_token, store_id,
                    store_name, store_city, basket_id, order_uuid, order_number,
                    status, balance_user, balance_basket, telegram_id, telegram_user,
                    email, phone_number, last_name, first_name, date_of_birth,
                    created_at, updated_at
                """,
                (
                    panier_id, account_id, account_token,
                    store_id, store_name, store_city, basket_id,
                    balance_user,
                    telegram_id,
                ),
            )
            row = cur.fetchone()
            session = Session.from_row(dict(row)) if row else None
            return session, None


def get_session(panier_id: str) -> Optional[Session]:
    """Récupère la session pour un panier_id."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, panier_id, account_id, account_token, store_id,
                store_name, store_city, basket_id, order_uuid, order_number,
                status, balance_user, balance_basket, telegram_id, telegram_user,
                email, phone_number, last_name, first_name, date_of_birth,
                created_at, updated_at
            FROM sessions
            WHERE panier_id = %s
            """,
            (panier_id,),
        )
        row = cur.fetchone()
        return Session.from_row(dict(row)) if row else None


def update_session(
    panier_id: str,
    *,
    store_name: Optional[str] = None,
    store_city: Optional[str] = None,
    basket_id: Optional[str] = None,
    order_uuid: Optional[str] = None,
    order_number: Optional[str] = None,
    status: Optional[str] = None,
    balance_basket: Optional[int] = None,
    email: Optional[str] = None,
    phone_number: Optional[str] = None,
    last_name: Optional[str] = None,
    first_name: Optional[str] = None,
    date_of_birth: Optional[Any] = None,
) -> Optional[Session]:
    """Met à jour une session (champs fournis uniquement)."""
    with session_lock(panier_id):
        updates = []
        params = []

        if store_name is not None:
            updates.append("store_name = %s")
            params.append(store_name)
        if store_city is not None:
            updates.append("store_city = %s")
            params.append(store_city)
        if basket_id is not None:
            updates.append("basket_id = %s")
            params.append(basket_id)
        if order_uuid is not None:
            updates.append("order_uuid = %s")
            params.append(order_uuid)
        if order_number is not None:
            updates.append("order_number = %s")
            params.append(order_number)
        if status is not None:
            updates.append("status = %s")
            params.append(status)
        if balance_basket is not None:
            updates.append("balance_basket = %s")
            params.append(balance_basket)
        if email is not None:
            updates.append("email = %s")
            params.append(email)
        if phone_number is not None:
            updates.append("phone_number = %s")
            params.append(phone_number)
        if last_name is not None:
            updates.append("last_name = %s")
            params.append(last_name)
        if first_name is not None:
            updates.append("first_name = %s")
            params.append(first_name)
        if date_of_birth is not None:
            updates.append("date_of_birth = %s")
            params.append(date_of_birth)

        if not updates:
            return get_session(panier_id)

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(panier_id)

        with get_cursor() as cur:
            cur.execute(
                f"""
                UPDATE sessions
                SET {", ".join(updates)}
                WHERE panier_id = %s
                RETURNING id, panier_id, account_id, account_token, store_id,
                    store_name, store_city, basket_id, order_uuid, order_number,
                    status, balance_user, balance_basket, telegram_id, telegram_user,
                    email, phone_number, last_name, first_name, date_of_birth,
                    created_at, updated_at
                """,
                params,
            )
            row = cur.fetchone()
            return Session.from_row(dict(row)) if row else None


def delete_session(panier_id: str) -> bool:
    """Supprime une session (DRAFT uniquement recommandé). Retourne True si supprimée."""
    with session_lock(panier_id):
        with get_cursor() as cur:
            cur.execute(
                "DELETE FROM sessions WHERE panier_id = %s",
                (panier_id,),
            )
            return cur.rowcount > 0


def session_exists(panier_id: str) -> bool:
    """Vérifie si une session existe pour ce panier_id."""
    return get_session(panier_id) is not None


def save_click_order_history_snapshot(panier_id: str) -> Optional[int]:
    """
    Crée un snapshot historique d'une commande Click & Collect (submit ou plus).
    Retourne l'id de l'historique créé, ou None en cas d'erreur/inéligible.
    """
    try:
        with session_lock(panier_id):
            with get_cursor() as cur:
                cur.execute(
                    """
                    SELECT id, panier_id, telegram_id, account_id, store_id, store_name, store_city,
                           order_uuid, order_number, status, telegram_user, email, phone_number,
                           last_name, first_name, date_of_birth
                    FROM sessions
                    WHERE panier_id = %s
                    """,
                    (panier_id,),
                )
                session_row = cur.fetchone()
                if not session_row:
                    return None

                status = (session_row.get("status") or "").upper()
                if status not in ("SUBMITTED", "CHECKED_IN", "COMPLETED", "FAILED"):
                    return None

                telegram_id = session_row.get("telegram_id")
                try:
                    user_id = int(str(telegram_id)) if telegram_id is not None else None
                except (TypeError, ValueError):
                    user_id = None
                if not user_id:
                    return None

                session_id = session_row["id"]
                cur.execute(
                    """
                    SELECT item_uuid, loyalty_id, name, cost, quantity, modgrps
                    FROM session_items
                    WHERE session_id = %s
                    ORDER BY id ASC
                    """,
                    (session_id,),
                )
                items = cur.fetchall() or []
                total_points = 0
                for item in items:
                    cost = int(item.get("cost") or 0)
                    qty = int(item.get("quantity") or 0)
                    total_points += max(0, cost) * max(0, qty)

                order_uuid = session_row.get("order_uuid")
                confirmation_url = (
                    f"https://kfc.fr/confirmation-de-commande/{order_uuid}"
                    if order_uuid
                    else None
                )

                cur.execute(
                    """
                    INSERT INTO click_order_history (
                        user_id, panier_id, session_id, order_uuid, order_number, confirmation_url,
                        status, store_id, store_name, store_city, account_id, telegram_user,
                        email, phone_number, last_name, first_name, date_of_birth, total_points
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        user_id,
                        session_row.get("panier_id"),
                        session_id,
                        order_uuid,
                        session_row.get("order_number"),
                        confirmation_url,
                        status,
                        session_row.get("store_id"),
                        session_row.get("store_name"),
                        session_row.get("store_city"),
                        session_row.get("account_id"),
                        session_row.get("telegram_user"),
                        session_row.get("email"),
                        session_row.get("phone_number"),
                        session_row.get("last_name"),
                        session_row.get("first_name"),
                        session_row.get("date_of_birth"),
                        total_points,
                    ),
                )
                created = cur.fetchone()
                if not created:
                    return None
                history_id = created["id"]

                for item in items:
                    cost = max(0, int(item.get("cost") or 0))
                    qty = max(1, int(item.get("quantity") or 1))
                    line_total = cost * qty
                    modgrps = item.get("modgrps")
                    modgrps_json = json.dumps(modgrps) if modgrps is not None else "[]"
                    cur.execute(
                        """
                        INSERT INTO click_order_history_items (
                            history_id, item_uuid, loyalty_id, name, cost, quantity, line_total_points, modgrps
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                        """,
                        (
                            history_id,
                            item.get("item_uuid"),
                            item.get("loyalty_id"),
                            item.get("name"),
                            cost,
                            qty,
                            line_total,
                            modgrps_json,
                        ),
                    )

                return history_id
    except Exception:
        return None


def update_click_order_history_status(order_uuid: Optional[str], status: str) -> int:
    """
    Met à jour le statut d'un historique click à partir de order_uuid.
    Retourne le nombre de lignes modifiées.
    """
    if not order_uuid or not status:
        return 0
    status = status.upper().strip()
    if status not in ("SUBMITTED", "CHECKED_IN", "COMPLETED", "FAILED"):
        return 0
    with get_cursor() as cur:
        cur.execute(
            """
            UPDATE click_order_history
            SET status = %s
            WHERE order_uuid = %s
            """,
            (status, order_uuid),
        )
        return cur.rowcount or 0
