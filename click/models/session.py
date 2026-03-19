"""
Modèle Session pour API Click & Collect.
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional


# Statuts possibles d'une session
SESSION_STATUS = (
    "DRAFT",       # Panier créé, articles en cours d'ajout
    "READY",       # Panier prêt à valider
    "CHECKOUT",    # Checkout effectué
    "SUBMITTED",   # Commande soumise à KFC
    "CHECKED_IN",  # Check-in effectué
    "COMPLETED",   # Commande récupérée
    "FAILED",      # Erreur
)


@dataclass
class Session:
    """Représentation d'une session de commande."""
    id: int
    panier_id: str
    telegram_id: Optional[str]
    account_id: str
    account_token: str
    store_id: str
    store_name: Optional[str]
    store_city: Optional[str]
    basket_id: Optional[str]
    order_uuid: Optional[str]
    order_number: Optional[str]
    status: str
    balance_user: int
    balance_basket: int
    telegram_user: Optional[str]
    created_at: datetime
    updated_at: datetime
    # Infos utilisateur KFC (récupérées via GetUserInfo à la soumission)
    email: Optional[str] = None
    phone_number: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    date_of_birth: Optional[date] = None

    def to_dict(self) -> dict[str, Any]:
        """Convertit en dictionnaire (pour JSON)."""
        return {
            "id": self.id,
            "panier_id": self.panier_id,
            "telegram_id": self.telegram_id,
            "account_id": self.account_id,
            "store_id": self.store_id,
            "store_name": self.store_name,
            "store_city": self.store_city,
            "basket_id": self.basket_id,
            "order_uuid": self.order_uuid,
            "order_number": self.order_number,
            "status": self.status,
            "balance_user": self.balance_user,
            "balance_basket": self.balance_basket,
            "telegram_user": self.telegram_user,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "email": self.email,
            "phone_number": self.phone_number,
            "last_name": self.last_name,
            "first_name": self.first_name,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
        }

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "Session":
        """Crée une Session à partir d'une ligne BDD (RealDictCursor)."""
        return cls(
            id=row["id"],
            panier_id=row["panier_id"],
            telegram_id=row.get("telegram_id"),
            account_id=row["account_id"],
            account_token=row["account_token"],
            store_id=row["store_id"],
            store_name=row.get("store_name"),
            store_city=row.get("store_city"),
            basket_id=row.get("basket_id"),
            order_uuid=row.get("order_uuid"),
            order_number=row.get("order_number"),
            status=row["status"],
            balance_user=row.get("balance_user", 0),
            balance_basket=row.get("balance_basket", 0),
            telegram_user=row.get("telegram_user"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            email=row.get("email"),
            phone_number=row.get("phone_number"),
            last_name=row.get("last_name"),
            first_name=row.get("first_name"),
            date_of_birth=row.get("date_of_birth"),
        )
