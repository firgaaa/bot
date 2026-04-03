"""
Bot Telegram optimisé pour la gestion KFC
Optimisé en sécurité, vitesse et efficacité de logique
"""

LOYALTY_PRODUCTS = {
    "loyalty-2385": {"price": 3.20, "label": "Accompagnements", "name": "Moyennes Frites", "cost": 150, "categorie": "BONS PLANS"},
    "loyalty-2383": {"price": 2.20, "label": "Accompagnements", "name": "Cobette® épi de maïs", "cost": 150, "categorie": "BONS PLANS"},
    "loyalty-3485": {"price": 2.95, "label": "Accompagnements", "name": "3 Crousti' Fromage Mozarella", "cost": 150, "categorie": "BONS PLANS"},
    "loyalty-3484": {"price": 2.95, "label": "Accompagnements", "name": "Crousti Fromage Raclette x3", "cost": 150, "categorie": "BONS PLANS"},
    "loyalty-3487": {"price": 2.95, "label": "Accompagnements", "name": "The Onion Rings X5", "cost": 150, "categorie": "BONS PLANS"},
    "loyalty-2403": {"price": 2.00, "label": "Accompagnements", "name": "Thé", "cost": 150, "categorie": "BONS PLANS"},
    "loyalty-2397": {"price": 1.60, "label": "Accompagnements", "name": "Espresso", "cost": 150, "categorie": "BONS PLANS"},
    "loyalty-2396": {"price": 3.00, "label": "Accompagnements", "name": "Double Espresso", "cost": 150, "categorie": "BONS PLANS"},
    "loyalty-2697": {"price": 2.95, "label": "gateau", "name": "Cookie Double Choco", "cost": 600, "categorie": "GOURMANDISES"},
    "loyalty-2323": {"price": 3.95, "label": "glace", "name": "Crousti'Kream Fraise", "cost": 600, "categorie": "GOURMANDISES"},
    "loyalty-2321": {"price": 3.95, "label": "glace", "name": "Crousti'Kream Snickers®", "cost": 600, "categorie": "GOURMANDISES"},
    "loyalty-3440": {"price": 3.95, "label": "glace", "name": "Crousti'Kream Nutella®", "cost": 600, "categorie": "GOURMANDISES"},
    "loyalty-3289": {"price": 3.60, "label": "gateau", "name": "Muffin Fondant Noisette", "cost": 600, "categorie": "GOURMANDISES"},
    "loyalty-3472": {"price": 3.95, "label": "burger", "name": "Crispy Burger Chicken", "cost": 600, "categorie": "GOURMANDISES"},
    "loyalty-3473": {"price": 3.95, "label": "burger", "name": "Crispy Burger Fish", "cost": 600, "categorie": "GOURMANDISES"},
    "loyalty-1278": {"price": 11.95, "label": "burger", "name": "Menu Kentucky® BBQ & Bacon", "cost": 1000, "categorie": "MEGA DEALS"},
    "loyalty-2335": {"price": 17.45, "label": "bucket", "name": "Bucket 10 Tenders®", "cost": 1000, "categorie": "MEGA DEALS"},
    "loyalty-2337": {"price": 17.455, "label": "bucket", "name": "Bucket 16 Hot Wings®", "cost": 1000, "categorie": "MEGA DEALS"},
    "loyalty-2405": {"price": 17.45, "label": "bucket", "name": "Bucket 7 Tenders® + 7 Hot Wings®", "cost": 1000, "categorie": "MEGA DEALS"},
    "loyalty-1279": {"price": 13.15, "label": "burger", "name": "Menu Double Kentucky Burger", "cost": 1000, "categorie": "MEGA DEALS"},
    "loyalty-1670": {"price": 11.45, "label": "burger", "name": "Menu Crispy Naan Creamy & Cheese", "cost": 1000, "categorie": "MEGA DEALS"},
    "loyalty-1675": {"price": 11.45, "label": "burger", "name": "Menu Crispy Spicy Naan Tikka", "cost": 1000, "categorie": "MEGA DEALS"},
    "loyalty-9000": {"price": 4.95, "label": "bucket", "name": "Menu enfant : P'tit Bucket®", "cost": 800, "categorie": "MENUS CRISPY"},
    "loyalty-1259": {"price": 9.25, "label": "burger", "name": "Menu Colonel Original Veggie", "cost": 800, "categorie": "MENUS CRISPY"},
    "loyalty-1162": {"price": 10.85, "label": "burger", "name": "Menu Tower® Cheese & Bacon", "cost": 800, "categorie": "MENUS CRISPY"},
    "loyalty-1050": {"price": 9.95, "label": "burger", "name": "Menu Boxmaster® Original", "cost": 800, "categorie": "MENUS CRISPY"},
    "loyalty-1051": {"price": 9.95, "label": "burger", "name": "Menu Boxmaster® Spicy", "cost": 800, "categorie": "MENUS CRISPY"},
    "loyalty-1254": {"price": 9.25, "label": "burger", "name": "Menu Colonel® Original", "cost": 800, "categorie": "MENUS CRISPY"},
    "loyalty-2302": {"price": 9.95, "label": "bucket", "name": "Menu 5 Tenders®", "cost": 800, "categorie": "MENUS CRISPY"},
    "loyalty-2103": {"price": 9.95, "label": "bucket", "name": "Menu 8 Hot Wings®", "cost": 800, "categorie": "MENUS CRISPY"},
    "loyalty-3470": {"price": 2.70, "label": "burger", "name": "iTWIST®", "cost": 300, "categorie": "PETIT CREUX"},
    "loyalty-2368": {"price": 4.10, "label": "Accompagnements", "name": "Kentucky® Fries", "cost": 300, "categorie": "PETIT CREUX"},
    "loyalty-3482": {"price": 3.95, "label": "Accompagnements", "name": "2 Tenders", "cost": 300, "categorie": "PETIT CREUX"},
    "loyalty-3481": {"price": 3.95, "label": "Accompagnements", "name": "3 Hot Wings", "cost": 300, "categorie": "PETIT CREUX"},
    "loyalty-3478": {"price": 2.50, "label": "burger", "name": "Krunchy®", "cost": 300, "categorie": "PETIT CREUX"},
    "loyalty-2516": {"price": 2.30, "label": "glace", "name": "Sundae Chocolat Noisette", "cost": 300, "categorie": "PETIT CREUX"},
    "loyalty-3441": {"price": 2.30, "label": "glace", "name": "Sundae Caramel", "cost": 300, "categorie": "PETIT CREUX"},
}

# Source produit locale (table/dictionnaire de référence pour l'interface Click&Collect)
PRODUCT = LOYALTY_PRODUCTS
PRODUCT_LABEL_ORDER = ("glace", "burger", "bucket", "gateau", "Accompagnements", "inconnu")


def get_product_price(loyalty_id: str) -> float:
    """Retourne le prix (argent) depuis PRODUCT pour un loyalty_id."""
    item = PRODUCT.get(str(loyalty_id), {})
    raw_price = item.get("price", 0)
    try:
        return float(raw_price)
    except (TypeError, ValueError):
        return 0.0

import logging
import os
import psycopg2
import psycopg2.extensions
from psycopg2.pool import ThreadedConnectionPool
from psycopg2 import sql
from datetime import datetime, timedelta
from pathlib import Path
from typing import Final, Optional, Dict, Any, List
from contextlib import contextmanager
import sys
import asyncio
from threading import Lock
import requests
import base64
import hashlib
import hmac
import copy
import json
from io import BytesIO
import qrcode
from PIL import Image
import numpy as np
import math
import random
import re

from creation_log import create_account
from injecteur_log import inject
from recup_token import recup_token as recup_token_async

# Monkey patch pour gérer les erreurs d'encodage dans les messages d'erreur PostgreSQL
# PostgreSQL sur Windows peut envoyer des messages en Windows-1252
_original_connect = psycopg2.connect

def _patched_connect(*args, **kwargs):
    """Wrapper pour psycopg2.connect qui gère les erreurs d'encodage"""
    try:
        return _original_connect(*args, **kwargs)
    except UnicodeDecodeError as ude:
        # Décoder le message d'erreur avec Windows-1252
        error_msg = ude.object.decode('windows-1252', errors='replace')
        raise psycopg2.OperationalError(f"Erreur de connexion: {error_msg}") from ude
    except Exception as e:
        # Pour les autres erreurs, vérifier si le message contient des bytes non-UTF-8
        if isinstance(e, (psycopg2.Error, psycopg2.OperationalError)):
            try:
                error_str = str(e)
                # Essayer de décoder si c'est une chaîne avec des bytes mal encodés
                try:
                    error_bytes = error_str.encode('latin1', errors='ignore')
                    error_msg = error_bytes.decode('windows-1252', errors='replace')
                    if error_msg != error_str:
                        # Le message a été décodé, créer une nouvelle exception
                        raise psycopg2.OperationalError(error_msg) from e
                except (UnicodeDecodeError, UnicodeEncodeError):
                    pass
            except:
                pass
        raise

# Appliquer le monkey patch
psycopg2.connect = _patched_connect

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from telegram.error import TelegramError, TimedOut, NetworkError, RetryAfter
from telegram.request import HTTPXRequest

# Charger les variables d'environnement depuis .env à la racine du projet
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constantes - Rôles récupérés depuis .env
BOT_TOKEN: Final[str] = os.getenv('BOT_TOKEN', '')
APP_VERSION: Final[str] = os.getenv('APP_VERSION', 'dev')
try:
    ADMIN_ID: Final[int] = int(os.getenv('ADMIN_ID', '0'))
    MODERATOR_ID: Final[int] = int(os.getenv('MODERATOR_ID', '0'))
    SELLER_ID: Final[int] = int(os.getenv('SELLER_ID', '0'))
except ValueError as e:
    logger.error(f"Erreur lors de la conversion des IDs: {e}")
    ADMIN_ID: Final[int] = 0
    MODERATOR_ID: Final[int] = 0
    SELLER_ID: Final[int] = 0

# Constantes - Configuration des montants d'achat (1€ = 1 point)
DEFAULT_POINT_MIN: Final[int] = 10  # Minimum d'achat (en euros/points)
DEFAULT_POINT_MAX: Final[int] = 2500  # Maximum d'achat (en euros/points)
POINT_INCREMENT: Final[int] = 1  # Pas d'ajustement dans l'interface +/-
DEFAULT_CARD_MARGIN: Final[int] = 150  # Marge par défaut pour l'achat de cartes (points supplémentaires)

# Table de prix par palier (prix pour 1 point, en euros)
# La clé représente le palier minimum de points atteint.
PRICE_TABLE: Final[Dict[int, float]] = {
    1   : 0.005000,
    1100: 0.004850,
    1200: 0.004740,
    1250: 0.004700,
    1300: 0.004615,
    1350: 0.004500,
    1400: 0.004428,
    1600: 0.004300,
    2000: 0.004220,
    2100: 0.004150,
    2150: 0.004100,
    2200: 0.004050,
    2250: 0.004000,
    2300: 0.003940,
    2350: 0.003893,
    2400: 0.003820,
    2500: 0.003800,
    3000: 0.003780,
    3500: 0.003760,
    4000: 0.003740,
    5000: 0.003725,
    6000: 0.003700,
    7000: 0.003650,
    8000: 0.003625,
    9000: 0.003624,
    10000: 0.003623,
    11000: 0.003622,
    12000: 0.003621,
    13000: 0.003620,
    14000: 0.003619,
    15000: 0.003618,
    16000: 0.003617,
    17000: 0.003616,
    18000: 0.003615,
    19000: 0.003614,
    20000: 0.003613,
    21000: 0.003612,
    22000: 0.003611,
    23000: 0.003610,
    24000: 0.003609,
    25000: 0.003608,
    26000: 0.003607,
    27000: 0.003606,
    29000: 0.003605,
    30000: 0.003604,
    31000: 0.003603,
    32000: 0.003602,
    33000: 0.003601,
    34000: 0.003600,
}

# Paliers triés (cache, évite le tri à chaque appel de euros_to_points)
_PALIERS_SORTED: Final[tuple[int, ...]] = tuple(sorted(PRICE_TABLE.keys()))

# Borne supérieure pour euros_to_points (évite une borne arbitraire palier+50000)
MAX_POINTS_EUROS_BUDGET: Final[int] = 999_999

# Table de prix Carte : seuil (points) -> facteur multiplicatif sur prix_carte
CARTE_PRICE_TABLE: Final[Dict[int, float]] = {
    0: 1.0,
    1300: 0.923076,
    1600: 0.9,
    1800: 0.888888,
    2100: 0.85714,
    2500: 0.8,
}

# Formules d'achat : libellé -> montant de départ (euros/points)
POINTS_FORMULA_DEFAULTS: Final[Dict[str, int]] = {
    "solo": 10,
    "duo": 25,
    "petit_groupe": 40,
    "gros_groupe": 80,
    "revendeur": 100,
}



# Configuration PostgreSQL local
DB_HOST: Final[str] = os.getenv('DB_HOST', 'localhost')
DB_PORT: Final[int] = int(os.getenv('DB_PORT', '5432'))
DB_NAME: Final[str] = os.getenv('DB_NAME', 'bot_db')
DB_USER: Final[str] = os.getenv('DB_USER', 'postgres')
DB_PASSWORD: Final[str] = os.getenv('DB_PASSWORD', 'postgres')

# Configuration API KFC Cartes
KFC_API_URL: Final[str] = os.getenv('KFC_API_URL', 'http://localhost:8080')
CLICK_API_URL: Final[str] = os.getenv('CLICK_API_URL', 'http://localhost:5000')
KFC_LOYALTY_ACCOUNT_ID: Final[str] = os.getenv('KFC_LOYALTY_ACCOUNT_ID', '')
KFC_LOYALTY_ACCOUNT_TOKEN: Final[str] = os.getenv('KFC_LOYALTY_ACCOUNT_TOKEN', '')
KFC_API_USERNAME: Final[str] = os.getenv('KFC_API_USERNAME', '')
KFC_API_PASSWORD: Final[str] = os.getenv('KFC_API_PASSWORD', '')
KFC_STORAGE_TABLE: Final[str] = os.getenv('KFC_STORAGE_TABLE', 'kfc_storage')


def _parse_kfc_generate_timeout() -> int:
    """Parse KFC_API_GENERATE_TIMEOUT depuis .env, défaut 120s si absent ou invalide."""
    try:
        val = os.getenv('KFC_API_GENERATE_TIMEOUT', '120')
        n = int(val)
        return n if n > 0 else 120
    except (ValueError, TypeError):
        return 120


KFC_API_GENERATE_TIMEOUT: Final[int] = _parse_kfc_generate_timeout()

# Mapping des clés config DB -> variables d'environnement (fallback si la DB n'a pas la clé)
CONFIG_KEY_TO_ENV: Final[Dict[str, str]] = {
    "point_min": "CONFIG_ARGENT_MIN",
    "point_max": "CONFIG_ARGENT_MAX",
    "card_margin": "CONFIG_CARD_MARGIN",
    "payment_url": "CONFIG_PAYMENT_URL",
    "staff_channel_id": "CONFIG_STAFF_CHANNEL_ID",
    "staff_thread_payment": "CONFIG_STAFF_THREAD_PAYMENT",
    "staff_thread_entretien": "CONFIG_STAFF_THREAD_ENTRETIEN",
    "staff_thread_demande_access": "CONFIG_STAFF_THREAD_DEMANDE_ACCESS",
    "emergency_stop": "CONFIG_EMERGENCY_STOP",
    "announcement_text": "CONFIG_ANNOUNCEMENT_TEXT",
    "announcement_photo": "CONFIG_ANNOUNCEMENT_PHOTO",
}

DB_POOL: ThreadedConnectionPool | None = None

# Cache pour les valeurs de config (TTL: 30 secondes)
_config_cache: dict[str, tuple[any, datetime]] = {}
_config_cache_lock = Lock()
_CONFIG_CACHE_TTL = timedelta(seconds=30)

# Rate limiting par user_id (anti-spam pour zones critiques - users uniquement)
_user_rate_limits: dict[str, float] = {}
_rate_limit_lock = Lock()

# Cache pour les file_id des bannières (upload unique)
_profil_banner_file_id: Optional[str] = None
_profil_banner_lock = Lock()
_shop_banner_file_id: Optional[str] = None
_shop_banner_lock = Lock()
_points_banner_file_id: Optional[str] = None
_points_banner_lock = Lock()

def check_rate_limit(user_id: int, action: str, cooldown_seconds: float) -> bool:
    """
    Vérifie si l'utilisateur peut effectuer une action (rate limit).
    Retourne True si autorisé, False si trop rapide.
    Note: Les admins sont exemptés du rate limit.
    """
    # Les admins ne sont pas soumis au rate limit
    if user_id == ADMIN_ID:
        return True
    
    key = f"{user_id}_{action}"
    now = datetime.now().timestamp()
    
    with _rate_limit_lock:
        last_time = _user_rate_limits.get(key, 0)
        if now - last_time < cooldown_seconds:
            return False  # Trop rapide
        _user_rate_limits[key] = now
        return True

def _get_cached_config(key: str, default_value: any) -> any:
    """Récupère une valeur de config avec cache (évite les requêtes DB répétées)"""
    with _config_cache_lock:
        if key in _config_cache:
            value, cached_at = _config_cache[key]
            if datetime.now() - cached_at < _CONFIG_CACHE_TTL:
                return value
        # Cache expiré ou absent, récupérer depuis DB
        value = get_config_value(key, default_value)
        _config_cache[key] = (value, datetime.now())
        return value

def _invalidate_config_cache(key: Optional[str] = None):
    """Invalide le cache (appelé après update_config_value)"""
    with _config_cache_lock:
        if key:
            _config_cache.pop(key, None)
        else:
            _config_cache.clear()


def init_db_pool() -> None:
    """Initialise le pool de connexions PostgreSQL (réduit la latence et la pression sur Postgres)."""
    global DB_POOL
    if DB_POOL:
        return
    DB_POOL = ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=10,
        client_encoding="UTF8",
    )


def close_db_pool() -> None:
    """Ferme proprement le pool PostgreSQL."""
    global DB_POOL
    if DB_POOL:
        try:
            DB_POOL.closeall()
        except Exception:
            pass
        DB_POOL = None


@contextmanager
def get_db_connection():
    """
    Contexte manager pour obtenir une connexion PostgreSQL via pool + gestion automatique des transactions.
    Utilise REPEATABLE READ pour éviter les race conditions sur les sections critiques.
    """
    conn = None
    try:
        global DB_POOL
        if not DB_POOL:
            init_db_pool()
        conn = DB_POOL.getconn()  # type: ignore[union-attr]
        # Activer le mode REPEATABLE READ pour éviter les race conditions
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ)
        
        yield conn
        
        conn.commit()
    except (psycopg2.Error, ValueError) as e:
        if conn:
            conn.rollback()
        logger.error(f"Erreur DB: {e}")
        raise
    finally:
        if conn and DB_POOL:
            DB_POOL.putconn(conn)


def verify_bot_tables_exist() -> None:
    """
    Vérifie que les tables du bot existent (users, config, pending_payments, card_purchase_history).
    Schéma géré par database_up.py via run.py.
    Lève si une table manque (lancer run.py ou database_up.py).
    """
    required = ("users", "config", "pending_payments", "card_purchase_history")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for table in required:
                cursor.execute(
                    "SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s",
                    (table,),
                )
                if cursor.fetchone() is None:
                    raise RuntimeError(
                        f"Table '{table}' manquante. Lancez run.py ou database_up.py pour créer les tables."
                    )
    except (psycopg2.Error, ValueError) as e:
        logger.error(f"Erreur vérification des tables: {e}")
        raise


def get_or_create_user(user_id: int, username: Optional[str] = None) -> tuple[float, bool]:
    """
    Récupère ou crée un utilisateur dans la base de données PostgreSQL.
    Met à jour le username si fourni.
    Génère token_publique et token_prive à la création ou si manquants.
    Retourne (argent, is_new_user)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Vérifier si l'utilisateur existe (avec tokens)
            cursor.execute(
                "SELECT points, token_publique, token_prive FROM users WHERE user_id = %s",
                (user_id,),
            )
            result = cursor.fetchone()

            if result:
                points, token_pub, token_priv = result[0], result[1], result[2]
                # Tokens manquants ? Les générer (database_up le fait aussi, mais on assure à l'arrivée)
                if not token_pub or not token_priv:
                    _ensure_user_tokens(user_id)
                # Mettre à jour le username si fourni
                if username:
                    cursor.execute(
                        "UPDATE users SET username = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
                        (username, user_id),
                    )
                return float(points or 0), False
            else:
                # Créer l'utilisateur avec solde 0 et tokens
                pub = derive_public_token(user_id)
                priv = derive_private_token(user_id)
                cursor.execute(
                    """INSERT INTO users (user_id, points, username, token_publique, token_prive)
                       VALUES (%s, 0, %s, %s, %s)
                       ON CONFLICT (user_id) DO NOTHING RETURNING points""",
                    (user_id, username, pub, priv),
                )
                if cursor.rowcount > 0:
                    logger.info(f"Nouvel utilisateur créé dans la DB: {user_id}")
                    return 0.0, True
                else:
                    cursor.execute("SELECT points FROM users WHERE user_id = %s", (user_id,))
                    result = cursor.fetchone()
                    return float(result[0]) if result else 0.0, False
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération/création de l'utilisateur {user_id}: {e}")
        return 0.0, False


def user_exists_in_users(user_id: int) -> bool:
    """Indique si l'utilisateur existe dans la table users (accès autorisé au bot)."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
            return cursor.fetchone() is not None
    except psycopg2.Error as e:
        logger.error(f"Erreur vérification existence user {user_id}: {e}")
        return False


def get_nouveau_user(user_id: int) -> Optional[tuple]:
    """
    Récupère la ligne nouveau_user pour un user_id.
    Retourne (username, demande_en_attente, nb_tentatives, accepte, last_demande) ou None.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, demande_en_attente, nb_tentatives, accepte, last_demande FROM nouveau_user WHERE user_id = %s",
                (user_id,),
            )
            row = cursor.fetchone()
            return row if row else None
    except psycopg2.Error as e:
        logger.error(f"Erreur get_nouveau_user {user_id}: {e}")
        return None


def create_or_update_demande_access(user_id: int, username: Optional[str]) -> bool:
    """
    Crée ou met à jour une demande d'accès : demande_en_attente=true, nb_tentatives+1, last_demande=now().
    Retourne True en cas de succès.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO nouveau_user (user_id, username, demande_en_attente, nb_tentatives, last_demande)
                VALUES (%s, %s, true, 1, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE SET
                    username = COALESCE(EXCLUDED.username, nouveau_user.username),
                    demande_en_attente = true,
                    nb_tentatives = nouveau_user.nb_tentatives + 1,
                    last_demande = CURRENT_TIMESTAMP
                """,
                (user_id, username),
            )
            conn.commit()
            return True
    except psycopg2.Error as e:
        logger.error(f"Erreur create_or_update_demande_access {user_id}: {e}")
        return False


def set_demande_accepte(user_id: int) -> None:
    """Marque la demande comme acceptée et en attente = false."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE nouveau_user SET accepte = true, demande_en_attente = false WHERE user_id = %s",
                (user_id,),
            )
            conn.commit()
    except psycopg2.Error as e:
        logger.error(f"Erreur set_demande_accepte {user_id}: {e}")


def set_demande_refuse(user_id: int) -> None:
    """Marque demande_en_attente = false (refus, l'user peut redemander)."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE nouveau_user SET demande_en_attente = false WHERE user_id = %s",
                (user_id,),
            )
            conn.commit()
    except psycopg2.Error as e:
        logger.error(f"Erreur set_demande_refuse {user_id}: {e}")
    """Récupère le nombre total d'utilisateurs"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]
    except psycopg2.Error as e:
        logger.error(f"Erreur lors du comptage des utilisateurs: {e}")
        return 0


def get_users_paginated(page: int = 0, per_page: int = 20) -> tuple[list[tuple[int, Optional[str], float, str, float]], int]:
    """
    Récupère une page d'utilisateurs avec pagination.
    Retourne ([(user_id, username, argent, role, reduction), ...], total_pages)
    Note: Le rôle de l'admin principal (ADMIN_ID) est toujours "admin" même s'il n'est pas dans la DB.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Compter le total
            cursor.execute("SELECT COUNT(*) FROM users")
            total = cursor.fetchone()[0]
            total_pages = (total + per_page - 1) // per_page if total > 0 else 0
            
            # Récupérer la page
            offset = page * per_page
            cursor.execute("""
                SELECT user_id, username, points, COALESCE(role, 'user') as role, COALESCE(reduction, 0) as reduction
                FROM users
                ORDER BY user_id
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            
            rows = cursor.fetchall()
            # Corriger le rôle de l'admin principal si présent dans les résultats
            corrected_rows = []
            for uid, username, points, user_role, reduction in rows:
                if uid == ADMIN_ID:
                    user_role = "admin"
                corrected_rows.append((uid, username, points, user_role, reduction))
            
            return corrected_rows, total_pages
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération paginée des utilisateurs: {e}")
        return [], 0


def get_user_info(user_id: int) -> Optional[dict]:
    """Récupère toutes les informations d'un utilisateur"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, username, points, COALESCE(role, 'user') as role, COALESCE(reduction, 0) as reduction, created_at, updated_at
                FROM users
                WHERE user_id = %s
            """, (user_id,))
            row = cursor.fetchone()
            if row:
                reduction_val = round(float(row[4] or 0), 2)
                points_val = float(row[2] or 0)
                return {
                    'user_id': row[0],
                    'username': row[1],
                    'points': points_val,
                    'role': row[3],
                    'reduction': reduction_val,
                    'created_at': row[5],
                    'updated_at': row[6]
                }
            return None
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération des infos utilisateur {user_id}: {e}")
        return None


def update_user_points(user_id: int, points_to_add: float) -> bool:
    """
    Met à jour l'argent utilisateur de manière atomique avec lock FOR UPDATE.
    Accepte des valeurs positives (crédit) et négatives (débit) mais refuse tout résultat < 0.
    """
    try:
        if abs(float(points_to_add)) < 1e-9:
            logger.warning("Tentative de mise à jour du solde avec 0 montant ignorée")
            return False

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Lock explicite sur la ligne utilisateur avec FOR UPDATE (évite les race conditions)
            cursor.execute(
                "SELECT points FROM users WHERE user_id = %s FOR UPDATE",
                (user_id,),
            )
            result = cursor.fetchone()

            if not result:
                logger.warning(f"Tentative de mise à jour du solde pour un utilisateur inexistant: {user_id}")
                return False

            current_points = float(result[0] or 0)
            new_points = current_points + float(points_to_add)
            if new_points < 0:
                logger.warning(
                    f"Tentative de débit de {points_to_add} argent impossible pour {user_id}: "
                    f"argent actuel {current_points}, résulterait en {new_points}"
                )
                return False

            # Mise à jour atomique avec la nouvelle valeur validée
            cursor.execute(
                "UPDATE users SET points = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
                (new_points, user_id),
            )

            if cursor.rowcount == 0:
                return False

            logger.info(
                f"Solde mis à jour pour l'utilisateur {user_id}: "
                f"{current_points} -> {new_points} (delta {points_to_add})"
            )
            return True
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la mise à jour du solde pour l'utilisateur {user_id}: {e}")
        return False


def get_user_points(user_id: int) -> float:
    """Récupère l'argent de l'utilisateur (compat nom historique)."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT points FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            return float(result[0]) if result else 0.0
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération du solde pour l'utilisateur {user_id}: {e}")
        return 0.0


def get_user_balance(user_id: int) -> float:
    """Alias compat : ancien nom."""
    return get_user_points(user_id)


def deduct_user_balance_atomic(user_id: int, points_to_deduct: float) -> bool:
    """
    Déduit de l'argent du solde utilisateur de manière atomique.
    Retourne True si la déduction a réussi, False sinon (solde insuffisant ou erreur).
    """
    try:
        if float(points_to_deduct) <= 0:
            logger.warning(f"Tentative de déduction d'argent négative ou nulle: {points_to_deduct}")
            return False

        # On réutilise la primitive centrale sur les points (ne peuvent jamais être négatifs).
        if not update_user_points(user_id, -points_to_deduct):
            logger.warning(f"Solde insuffisant ou utilisateur inexistant lors de la déduction pour {user_id}")
            return False

        logger.info(f"Solde déduit pour l'utilisateur {user_id}: -{points_to_deduct} points")
        return True
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la déduction du solde pour l'utilisateur {user_id}: {e}")
        return False


def generate_kfc_api_auth_token() -> str:
    """Génère le token Basic Auth pour l'API KFC"""
    if not KFC_API_USERNAME or not KFC_API_PASSWORD:
        logger.error("Credentials API KFC non configurés")
        return ""
    
    credentials = f"{KFC_API_USERNAME}:{KFC_API_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    return token


async def insert_kfc_account(account_data: Dict[str, Any]) -> tuple[bool, Optional[str], Optional[List[str]]]:
    """
    Appelle l'API KFC /insert pour insérer un compte dans la base de données.
    Retourne (success: bool, error_message: Optional[str], warnings: Optional[List[str]])
    """
    if not KFC_API_URL or not KFC_API_USERNAME or not KFC_API_PASSWORD:
        logger.error("Configuration API KFC incomplète")
        return False, "Configuration API KFC incomplète", None
    
    # Liste des champs acceptés par l'API /insert selon la documentation
    allowed_fields = {"id", "carte", "customer_id", "email", "password", "nom", "point", "expired_at"}
    
    # Détecter les champs non supportés
    unsupported_fields = [key for key in account_data.keys() if key not in allowed_fields]
    warnings = []
    if unsupported_fields:
        warnings.append(f"Champs ignorés (non supportés par l'API): {', '.join(unsupported_fields)}")
        logger.warning(f"Champs non supportés détectés dans account_data: {unsupported_fields}")
    
    # Filtrer pour ne garder que les champs acceptés
    filtered_data = {key: value for key, value in account_data.items() if key in allowed_fields}
    
    # Validation des champs requis
    if "id" not in filtered_data or not filtered_data["id"]:
        return False, "Le champ 'id' est requis", None
    
    if "carte" not in filtered_data or not filtered_data["carte"]:
        return False, "Le champ 'carte' est requis", None
    
    if "point" not in filtered_data:
        return False, "Le champ 'point' est requis", None
    
    # Convertir point en entier si c'est une chaîne
    try:
        points = int(filtered_data["point"])
        if points < 0:
            return False, "Le champ 'point' doit être >= 0", None
        filtered_data["point"] = points  # Remplacer par l'entier
    except (ValueError, TypeError):
        return False, f"Le champ 'point' doit être un nombre entier (reçu: {repr(filtered_data['point'])})", None
    
    # Gérer expired_at spécial : si c'est "0001-01-01T00:00:00", le mettre à null
    if "expired_at" in filtered_data:
        expired_at_value = filtered_data["expired_at"]
        if expired_at_value == "0001-01-01T00:00:00" or expired_at_value == "0001-01-01T00:00:00Z":
            filtered_data["expired_at"] = None
            warnings.append("expired_at '0001-01-01T00:00:00' converti en null")
        elif expired_at_value == "" or expired_at_value is None:
            filtered_data["expired_at"] = None
    
    auth_token = generate_kfc_api_auth_token()
    if not auth_token:
        return False, "Erreur d'authentification API", None
    
    headers = {
        "Authorization": f"Basic {auth_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{KFC_API_URL}/insert",
            json=filtered_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 204:
            logger.info(f"Compte KFC inséré avec succès: {filtered_data.get('id', 'N/A')}")
            return True, None, warnings if warnings else None
        elif response.status_code == 401:
            logger.error("Authentification API KFC échouée")
            return False, "Erreur d'authentification API", None
        elif response.status_code == 409:
            error_text = response.text.strip() if response.text else "La carte existe déjà"
            logger.warning(f"Insert KFC échoué (409): {error_text}")
            return False, error_text, None
        elif response.status_code == 500:
            error_text = response.text.strip() if response.text else "Erreur serveur"
            logger.error(f"Erreur API KFC (500): {error_text}")
            # Messages d'erreur courants
            error_lower = error_text.lower()
            if "duplicate" in error_lower or "unique" in error_lower or "already exists" in error_lower:
                return False, f"Ce compte existe déjà (id ou carte dupliquée)\n\nDétails API: {error_text}", None
            elif "constraint" in error_lower or "check" in error_lower:
                return False, f"Erreur de contrainte de base de données\n\nDétails API: {error_text}", None
            else:
                return False, f"Erreur serveur (500)\n\nDétails API: {error_text}", None
        elif response.status_code == 400:
            error_text = response.text.strip() if response.text else "Requête invalide"
            logger.error(f"Erreur API KFC (400): {error_text}")
            return False, f"Requête invalide (400)\n\nDétails API: {error_text}", None
        else:
            error_text = response.text.strip() if response.text else f"Code {response.status_code}"
            logger.error(f"Erreur API KFC (code {response.status_code}): {error_text}")
            return False, f"Erreur API (code {response.status_code})\n\nDétails: {error_text}", None
            
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de l'appel API KFC /insert")
        return False, "Timeout: l'API n'a pas répondu à temps (10s)", None
    except requests.exceptions.ConnectionError:
        logger.error("Impossible de se connecter à l'API KFC")
        return False, "Impossible de se connecter à l'API KFC", None
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de l'appel API KFC /insert: {e}")
        return False, f"Erreur de connexion: {str(e)}", None
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'appel API KFC /insert: {e}")
        return False, f"Erreur inattendue: {str(e)}", None


def fetch_click_stores(city: str) -> tuple[bool, Optional[List[Dict[str, Any]]], Optional[str]]:
    """
    Appelle l'API Flask GET /stores?city=... pour récupérer les KFC correspondants.
    Retourne (success, stores_list, error_message).
    stores_list: [{id, name, city}, ...]
    """
    if not CLICK_API_URL:
        logger.error("CLICK_API_URL non configuré")
        return False, None, "Configuration API Click manquante"
    url = f"{CLICK_API_URL.rstrip('/')}/stores"
    try:
        response = requests.get(url, params={"city": city}, timeout=15)
        data = response.json() if response.text else {}
        if response.status_code == 200 and data.get("success"):
            return True, data.get("data") or [], None
        err = data.get("error") or {}
        msg = err.get("message") or response.text or f"Erreur {response.status_code}"
        return False, None, msg
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de l'appel API Click /stores")
        return False, None, "Le serveur n'a pas répondu à temps."
    except requests.exceptions.ConnectionError:
        logger.error("Impossible de se connecter à l'API Click")
        return False, None, "Impossible de contacter le serveur."
    except Exception as e:
        logger.error(f"Erreur fetch_click_stores: {e}")
        return False, None, str(e)


def fetch_click_account_balance(account_id: str, account_token: str) -> tuple[bool, Optional[int], Optional[str]]:
    """
    Appelle l'API Flask GET /accounts/balance pour récupérer le solde de points du compte KFC.
    Retourne (success, balance, error_message).
    """
    if not CLICK_API_URL:
        logger.error("CLICK_API_URL non configuré")
        return False, None, "Configuration API Click manquante"
    url = f"{CLICK_API_URL.rstrip('/')}/accounts/balance"
    params = {"account_id": account_id, "account_token": account_token}
    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json() if response.text else {}
        if response.status_code == 200 and data.get("success"):
            bal = data.get("data", {}).get("balance")
            return True, int(bal) if bal is not None else 0, None
        err = data.get("error") or {}
        msg = err.get("message") or response.text or f"Erreur {response.status_code}"
        return False, None, msg
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de l'appel API Click /accounts/balance")
        return False, None, "Le serveur n'a pas répondu à temps."
    except requests.exceptions.ConnectionError:
        logger.error("Impossible de se connecter à l'API Click")
        return False, None, "Impossible de contacter le serveur."
    except Exception as e:
        logger.error(f"Erreur fetch_click_account_balance: {e}")
        return False, None, str(e)


def fetch_click_create_session(
    panier_id: str,
    account_id: str,
    account_token: str,
    store_id: str,
    store_name: Optional[str],
    store_city: Optional[str],
    telegram_id: Optional[str],
) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Appelle l'API Flask POST /sessions pour créer une session.
    balance_user est récupéré automatiquement par l'API si non fourni.
    Retourne (success, session_dict, error_message).
    """
    if not CLICK_API_URL:
        return False, None, "Configuration API Click manquante"
    url = f"{CLICK_API_URL.rstrip('/')}/sessions"
    payload = {
        "panier_id": str(panier_id),
        "account_id": account_id,
        "account_token": account_token,
        "store_id": str(store_id),
        "store_name": store_name,
        "store_city": store_city,
        "telegram_id": str(telegram_id) if telegram_id else None,
    }
    try:
        response = requests.post(url, json=payload, timeout=20)
        data = response.json() if response.text else {}
        if response.status_code in (200, 201) and data.get("success"):
            return True, data.get("data"), None
        err = data.get("error") or {}
        msg = err.get("message") or response.text or f"Erreur {response.status_code}"
        return False, None, msg
    except Exception as e:
        logger.error(f"Erreur fetch_click_create_session: {e}")
        return False, None, str(e)


def fetch_click_add_basket_item(
    panier_id: str,
    loyalty_id: str,
    cost: int,
    quantity: int,
    name: Optional[str] = None,
    modgrps: Optional[list] = None,
) -> tuple[bool, Optional[str]]:
    """Appelle POST /sessions/<panier_id>/basket/items. Retourne (success, error_message)."""
    if not CLICK_API_URL:
        return False, "Configuration API Click manquante"
    url = f"{CLICK_API_URL.rstrip('/')}/sessions/{panier_id}/basket/items"
    payload = {"loyalty_id": loyalty_id, "cost": cost, "quantity": quantity, "name": name or "", "modgrps": modgrps or []}
    try:
        response = requests.post(url, json=payload, timeout=15)
        data = response.json() if response.text else {}
        if response.status_code in (200, 201) and data.get("success"):
            return True, None
        err = data.get("error") or {}
        return False, err.get("message") or response.text or f"Erreur {response.status_code}"
    except Exception as e:
        logger.error(f"Erreur fetch_click_add_basket_item: {e}")
        return False, str(e)


def fetch_click_build_modgrps_from_tree(tree: list) -> tuple[bool, Optional[list], Optional[str]]:
    """Appelle POST /modgrps/build-from-tree. Retourne (success, modgrps_list, error_message)."""
    if not CLICK_API_URL:
        return False, None, "Configuration API Click manquante"
    url = f"{CLICK_API_URL.rstrip('/')}/modgrps/build-from-tree"

    # Log entrée : taille de l'arbre et ids des premiers groupes
    try:
        logger.info(
            "CLICK build-from-tree request url=%s groups=%s first_group_ids=%s",
            url,
            len(tree or []),
            [g.get("id") for g in (tree or [])[:5]],
        )
    except Exception:
        pass

    try:
        response = requests.post(url, json={"tree": tree}, timeout=10)
        text = response.text or ""
        try:
            data = response.json() if text else {}
        except ValueError:
            data = {}

        logger.info(
            "CLICK build-from-tree response status=%s body=%s",
            response.status_code,
            text[:2000],
        )

        if response.status_code == 200 and data.get("success"):
            modgrps = (data.get("data") or {}).get("modgrps") or []
            try:
                logger.info(
                    "CLICK build-from-tree OK groups=%s example=%s",
                    len(modgrps),
                    modgrps[:1],
                )
            except Exception:
                pass
            return True, modgrps, None

        err = data.get("error") or {}
        msg = err.get("message") or text or f"Erreur {response.status_code}"
        logger.warning("CLICK build-from-tree ERROR status=%s msg=%s", response.status_code, msg)
        return False, None, msg
    except Exception as e:
        logger.exception("Erreur fetch_click_build_modgrps_from_tree")
        return False, None, str(e)


def fetch_click_checkout(panier_id: str) -> tuple[bool, Optional[str]]:
    """Appelle POST /sessions/<panier_id>/checkout. Retourne (success, error_message)."""
    if not CLICK_API_URL:
        return False, "Configuration API Click manquante"
    url = f"{CLICK_API_URL.rstrip('/')}/sessions/{panier_id}/checkout"
    try:
        response = requests.post(url, json={}, timeout=20)
        data = response.json() if response.text else {}
        if response.status_code == 200 and data.get("success"):
            return True, None
        err = data.get("error") or {}
        return False, err.get("message") or response.text or f"Erreur {response.status_code}"
    except Exception as e:
        logger.error(f"Erreur fetch_click_checkout: {e}")
        return False, str(e)


def fetch_click_submit(panier_id: str) -> tuple[bool, Optional[dict], Optional[str]]:
    """
    Appelle POST /sessions/<panier_id>/submit.
    Retourne (success, data_dict, error_message).
    data_dict contient confirmation_url, first_name, email, phone_number, etc.
    """
    if not CLICK_API_URL:
        return False, None, "Configuration API Click manquante"
    url = f"{CLICK_API_URL.rstrip('/')}/sessions/{panier_id}/submit"
    try:
        response = requests.post(url, json={}, timeout=60)
        data = response.json() if response.text else {}
        if response.status_code == 200 and data.get("success"):
            return True, data.get("data") or {}, None
        err = data.get("error") or {}
        return False, None, err.get("message") or response.text or f"Erreur {response.status_code}"
    except Exception as e:
        logger.error(f"Erreur fetch_click_submit: {e}")
        return False, None, str(e)


def fetch_click_checkin(panier_id: str) -> tuple[bool, Optional[str]]:
    """Appelle POST /sessions/<panier_id>/checkin. Retourne (success, error_message)."""
    if not CLICK_API_URL:
        return False, "Configuration API Click manquante"
    url = f"{CLICK_API_URL.rstrip('/')}/sessions/{panier_id}/checkin"
    try:
        response = requests.post(url, json={}, timeout=15)
        data = response.json() if response.text else {}
        if response.status_code == 200 and data.get("success"):
            return True, None
        err = data.get("error") or {}
        return False, err.get("message") or response.text or f"Erreur {response.status_code}"
    except Exception as e:
        logger.error(f"Erreur fetch_click_checkin: {e}")
        return False, str(e)


def fetch_click_preview_menu(store_id: str) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Appelle l'API Flask GET /stores/<store_id>/preview-menu pour le menu fidélité (sans session).
    Transmet account_id et account_token depuis le .env du bot.
    Retourne (success, menu_dict, error_message).
    menu_dict: { "categories": { "Mega Deals": [{name, id, cost, modgrps?}], ... } }
    """
    if not CLICK_API_URL:
        logger.error("CLICK_API_URL non configuré")
        return False, None, "Configuration API Click manquante"
    if not KFC_LOYALTY_ACCOUNT_ID or not KFC_LOYALTY_ACCOUNT_TOKEN:
        logger.error("KFC_LOYALTY_ACCOUNT_ID ou KFC_LOYALTY_ACCOUNT_TOKEN non configuré")
        return False, None, "Compte fidélité non configuré côté bot"
    url = f"{CLICK_API_URL.rstrip('/')}/stores/{store_id}/preview-menu"
    params = {"account_id": KFC_LOYALTY_ACCOUNT_ID, "account_token": KFC_LOYALTY_ACCOUNT_TOKEN}
    try:
        response = requests.get(url, params=params, timeout=20)
        data = response.json() if response.text else {}
        if response.status_code == 200 and data.get("success"):
            return True, data.get("data") or {}, None
        err = data.get("error") or {}
        msg = err.get("message") or response.text or f"Erreur {response.status_code}"
        return False, None, msg
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de l'appel API Click /preview-menu")
        return False, None, "Le serveur n'a pas répondu à temps."
    except requests.exceptions.ConnectionError:
        logger.error("Impossible de se connecter à l'API Click")
        return False, None, "Impossible de contacter le serveur."
    except Exception as e:
        logger.error(f"Erreur fetch_click_preview_menu: {e}")
        return False, None, str(e)


def build_click_collect_menu_from_product(click_categories: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Recompose le menu Click&Collect pour l'UI à partir de PRODUCT.
    - Données UI (name/cost/categorie/label): PRODUCT
    - Données techniques (modgrps/disponibilité): réponse Click
    - Produits inconnus: placés dans 'inconnu' et bloqués à l'ajout panier
    """
    grouped: Dict[str, List[Dict[str, Any]]] = {label: [] for label in PRODUCT_LABEL_ORDER}
    seen_ids: set[str] = set()

    for _cat_name, items in (click_categories or {}).items():
        if not isinstance(items, list):
            continue
        for raw_item in items:
            if not isinstance(raw_item, dict):
                continue
            loyalty_id = str(raw_item.get("id", "")).strip()
            if not loyalty_id:
                continue
            if loyalty_id in seen_ids:
                continue
            seen_ids.add(loyalty_id)

            raw_name = sanitize_display_name(raw_item.get("name", "?"))
            raw_cost = raw_item.get("cost", 0)
            try:
                raw_cost_int = int(raw_cost)
            except (TypeError, ValueError):
                raw_cost_int = 0

            modgrps = raw_item.get("modgrps")
            if not isinstance(modgrps, list):
                modgrps = []

            product_data = PRODUCT.get(loyalty_id)
            if product_data:
                item_label = str(product_data.get("label") or "inconnu")
                item_name = sanitize_display_name(product_data.get("name") or raw_name)
                try:
                    item_cost = int(product_data.get("cost", raw_cost_int))
                except (TypeError, ValueError):
                    item_cost = raw_cost_int
                item_categorie = str(product_data.get("categorie") or "INCONNU")
                unknown_product = False
            else:
                item_label = "inconnu"
                item_name = raw_name
                item_cost = raw_cost_int
                item_categorie = "INCONNU"
                unknown_product = True

            if item_label not in grouped:
                grouped[item_label] = []

            grouped[item_label].append({
                "id": loyalty_id,
                "name": item_name,
                "cost": item_cost,
                "categorie": item_categorie,
                "label": item_label,
                "modgrps": modgrps,
                "unknown_product": unknown_product,
                "click_name": raw_name,
                "click_cost": raw_cost_int,
            })

    # Conserver un ordre stable: labels connus d'abord, puis tout label additionnel, puis inconnu
    ordered: Dict[str, List[Dict[str, Any]]] = {}
    for label in PRODUCT_LABEL_ORDER:
        if grouped.get(label):
            ordered[label] = grouped[label]
    for label, items in grouped.items():
        if label not in ordered and items:
            ordered[label] = items
    return ordered


def get_kfc_cards_statistics() -> tuple[Optional[int], Optional[float]]:
    """
    Récupère les statistiques des cartes KFC depuis la base de données.
    Retourne (nombre_cartes_disponibles: Optional[int], moyenne_points: Optional[float])
    Retourne (None, None) en cas d'erreur.
    """
    # Liste des noms de tables possibles à essayer (commencer par celle du .env)
    table_names = [KFC_STORAGE_TABLE, "kfc_storage", "kfc_accounts", "accounts", "kfc_cards", "cards"]
    
    for table_name in table_names:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Vérifier si la table existe dans le schéma public ou dans d'autres schémas
                cursor.execute("""
                    SELECT table_schema, table_name
                    FROM information_schema.tables 
                    WHERE table_name = %s
                    AND table_schema NOT IN ('pg_catalog', 'information_schema')
                    LIMIT 1
                """, (table_name,))
                
                table_info = cursor.fetchone()
                if not table_info:
                    logger.debug(f"Table {table_name} n'existe pas, essai suivant...")
                    continue
                
                schema_name, actual_table_name = table_info
                logger.debug(f"Table trouvée: {schema_name}.{actual_table_name}")
                
                # Compter les cartes disponibles (deja_send = false ou NULL, status != 'expired')
                # Et calculer la moyenne des points de TOUTES les cartes (pas seulement disponibles)
                # Utiliser psycopg2.sql.Identifier pour sécuriser le nom de schéma et table
                query = sql.SQL("""
                    SELECT 
                        COUNT(*) FILTER (WHERE (deja_send = false OR deja_send IS NULL) 
                                          AND (status IS NULL OR status != 'expired')) as total_disponibles,
                        COALESCE(AVG(point), 0) as moyenne_points_toutes
                    FROM {}.{}
                """).format(sql.Identifier(schema_name), sql.Identifier(actual_table_name))
                cursor.execute(query)
                
                result = cursor.fetchone()
                if result:
                    count = result[0] if result[0] is not None else 0
                    avg_points = float(result[1]) if result[1] is not None else 0.0
                    logger.info(f"Statistiques KFC récupérées depuis {schema_name}.{actual_table_name}: {count} cartes disponibles, moyenne {avg_points:.1f} points")
                    return count, avg_points
                else:
                    return 0, 0.0
                    
        except psycopg2.Error as e:
            logger.debug(f"Erreur avec la table {table_name}: {e}")
            continue
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la récupération des statistiques KFC depuis {table_name}: {e}")
            continue
    
    # Si aucune table n'a fonctionné, essayer de lister toutes les tables pour debug
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_schema, table_name
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                AND (table_name LIKE '%account%' OR table_name LIKE '%card%' OR table_name LIKE '%kfc%')
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            if tables:
                logger.info(f"Tables trouvées contenant 'account', 'card' ou 'kfc': {tables}")
            else:
                # Lister toutes les tables pour voir ce qui existe
                cursor.execute("""
                    SELECT table_schema, table_name
                    FROM information_schema.tables 
                    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                    ORDER BY table_name
                """)
                all_tables = cursor.fetchall()
                logger.info(f"Toutes les tables dans la base de données: {all_tables}")
    except Exception as e:
        logger.debug(f"Erreur lors de la recherche de tables: {e}")
    
    # Si aucune table n'a fonctionné
    logger.warning("Impossible de récupérer les statistiques KFC: aucune table trouvée ou erreur")
    return None, None


async def generate_kfc_card(points: int) -> Optional[Dict[str, Any]]:
    """
    Appelle l'API KFC pour générer/trouver une carte avec le nombre de points demandé.
    Utilise une marge configurable pour chercher entre points et points + marge.
    Retourne les informations de la carte (dict) si succès, None si aucune carte disponible ou erreur.
    """
    if not KFC_API_URL or not KFC_API_USERNAME or not KFC_API_PASSWORD:
        logger.error("Configuration API KFC incomplète")
        return None
    
    if points <= 0:
        logger.warning(f"Tentative de génération de carte avec points invalides: {points}")
        return None
    
    auth_token = generate_kfc_api_auth_token()
    if not auth_token:
        return None
    
    # Récupérer la marge configurée
    card_margin = get_card_margin()
    max_points = points + card_margin
    
    headers = {
        "Authorization": f"Basic {auth_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "min_points": points,
        "max_points": max_points  # Fourchette avec marge
    }
    
    try:
        # Appel API avec timeout configurable (KFC_API_GENERATE_TIMEOUT, défaut 120s)
        response = requests.post(
            f"{KFC_API_URL}/generate",
            json=payload,
            headers=headers,
            timeout=KFC_API_GENERATE_TIMEOUT
        )
        
        if response.status_code == 200:
            text = (response.text or "").strip()
            if not text:
                logger.warning(
                    "API KFC /generate: réponse 200 avec corps vide (aucune carte ou erreur API). "
                    "Vérifier le stock et les logs côté API."
                )
                return None
            try:
                card_data = response.json()
            except json.JSONDecodeError as e:
                preview = text[:200] if len(text) > 200 else text
                logger.error(
                    "API KFC /generate: réponse 200 mais corps non-JSON (status=%s, len=%s). "
                    "Début du corps: %r. Erreur JSON: %s",
                    response.status_code, len(response.text), preview, e,
                )
                return None
            actual_points = card_data.get('point', points)
            logger.info(f"Carte KFC générée avec succès: {card_data.get('id', 'N/A')} (demandé: {points} points, obtenu: {actual_points} points)")
            return card_data
        elif response.status_code == 404:
            logger.info(f"Aucune carte disponible pour {points} points")
            return None
        elif response.status_code == 401:
            logger.error("Authentification API KFC échouée")
            return None
        elif response.status_code == 400:
            logger.error(f"Requête API KFC invalide: {response.text}")
            return None
        else:
            logger.error(f"Erreur API KFC (code {response.status_code}): {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout lors de l'appel API KFC pour {points} points")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("Impossible de se connecter à l'API KFC")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de l'appel API KFC: {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'appel API KFC: {e}")
        return None


def generate_card_banner_image(carte: str) -> Optional[BytesIO]:
    """
    Génère une image bannière avec le QR code de la carte intégré (même logique que creer qr_code.py).
    Ne sauvegarde rien sur disque : retourne l'image en mémoire (BytesIO) ou None en cas d'erreur.
    """
    if not carte or not str(carte).strip():
        return None
    carte = str(carte).strip()

    try:
        # Configuration du QR code (box_size réduit pour image plus légère)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=6,
            border=1,
        )
        qr.add_data(carte)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Chemin de la bannière (répertoire du script bot.py)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        banner_path = os.path.join(script_dir, "banniere_qrcode.png")

        # Si la bannière n'existe pas, renvoyer uniquement le QR code
        if not os.path.exists(banner_path):
            logger.warning("Bannière 'banniere_qrcode.png' introuvable, envoi du QR code seul.")
            buf = BytesIO()
            qr_img.save(buf, format="PNG", optimize=True)
            buf.seek(0)
            return buf

        # Charger la bannière
        banner = Image.open(banner_path).convert("RGB")

        # Détection du marqueur magenta (comme dans creer qr_code.py)
        banner_array = np.array(banner)
        tolerances = [10, 30, 50, 80]
        x_coords = np.array([])
        y_coords = np.array([])
        tolerance_utilisee: Optional[int] = None

        for tol in tolerances:
            mask = (
                (banner_array[:, :, 0] >= (255 - tol)) & (banner_array[:, :, 0] <= 255)
                & (banner_array[:, :, 1] >= 0) & (banner_array[:, :, 1] <= tol)
                & (banner_array[:, :, 2] >= (255 - tol)) & (banner_array[:, :, 2] <= 255)
            )
            y_coords, x_coords = np.where(mask)
            if len(x_coords) > 100:
                tolerance_utilisee = tol
                break

        if tolerance_utilisee is None and len(x_coords) > 0:
            tolerance_utilisee = tolerances[-1]

        if len(x_coords) == 0:
            logger.warning("Marqueur magenta non trouvé dans la bannière, envoi du QR code seul.")
            buf = BytesIO()
            qr_img.save(buf, format="PNG", optimize=True)
            buf.seek(0)
            return buf

        # Limites de la zone du marqueur
        x_min, x_max = x_coords.min(), x_coords.max()
        y_min, y_max = y_coords.min(), y_coords.max()
        marker_width = x_max - x_min + 1
        marker_height = y_max - y_min + 1

        # Supprimer une partie des bordures blanches autour du QR code
        qr_img_rgb = qr_img.convert("RGB")
        qr_array = np.array(qr_img_rgb)
        mask_non_blanc = (
            (qr_array[:, :, 0] < 255)
            | (qr_array[:, :, 1] < 255)
            | (qr_array[:, :, 2] < 255)
        )
        rows_non_blanc = np.any(mask_non_blanc, axis=1)
        cols_non_blanc = np.any(mask_non_blanc, axis=0)

        # Paramètres de bordure et débordement (identiques au script)
        BORDURE_BLANCHE_CONSERVEE = 6
        DEBORDEMENT_PIXELS = 17

        if np.any(rows_non_blanc) and np.any(cols_non_blanc):
            top = np.argmax(rows_non_blanc)
            bottom = len(rows_non_blanc) - np.argmax(rows_non_blanc[::-1])
            left = np.argmax(cols_non_blanc)
            right = len(cols_non_blanc) - np.argmax(cols_non_blanc[::-1])

            img_width, img_height = qr_img.size

            crop_top = max(0, top - BORDURE_BLANCHE_CONSERVEE)
            crop_bottom = min(img_height, bottom + BORDURE_BLANCHE_CONSERVEE)
            crop_left = max(0, left - BORDURE_BLANCHE_CONSERVEE)
            crop_right = min(img_width, right + BORDURE_BLANCHE_CONSERVEE)

            qr_img_trimmed = qr_img.crop((crop_left, crop_top, crop_right, crop_bottom))
        else:
            qr_img_trimmed = qr_img

        # Calcul de la nouvelle taille avec débordement
        qr_target_width = marker_width + (DEBORDEMENT_PIXELS * 2)
        qr_target_height = marker_height + (DEBORDEMENT_PIXELS * 2)

        qr_img_resized = qr_img_trimmed.resize(
            (qr_target_width, qr_target_height),
            Image.Resampling.LANCZOS,
        )

        # Position de collage (centrée sur la zone magenta, avec débordement)
        paste_x = x_min - DEBORDEMENT_PIXELS
        paste_y = y_min - DEBORDEMENT_PIXELS

        # Coller le QR code sur une copie de la bannière
        banner_copy = banner.copy()
        banner_copy.paste(qr_img_resized, (paste_x, paste_y))

        # JPEG + qualité 88 = fichier plus léger qu'en PNG, qualité suffisante
        buf = BytesIO()
        banner_copy.save(buf, format="JPEG", quality=88, optimize=True)
        buf.seek(0)
        return buf

    except Exception as e:
        logger.error(f"Erreur lors de la génération de la bannière QR pour la carte '{carte}': {e}")
        return None


def get_config_value(key: str, default_value: any) -> any:
    """Récupère une valeur de configuration depuis la base de données"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT value FROM config WHERE key = %s", (key,))
            result = cursor.fetchone()
            
            if result:
                value = result[0]
                # Convertir selon le type attendu
                if isinstance(default_value, float):
                    return float(value)
                elif isinstance(default_value, int):
                    return int(value)
                return value
            
            return default_value
    except (psycopg2.Error, ValueError) as e:
        logger.error(f"Erreur lors de la récupération de la config '{key}': {e}")
        return default_value


def update_config_value(key: str, value: any) -> bool:
    """Met à jour une valeur de configuration dans la base de données"""
    try:
        # Validation selon la clé
        if key == "point_price_per_10":
            value_float = float(value)
            if value_float <= 0:
                logger.warning(f"Tentative de définir un prix négatif ou nul: {value_float}")
                return False
            value = str(value_float)
        elif key in ("point_min", "argent_min"):
            value_int = int(value)
            if value_int < 0:
                logger.warning(f"Tentative de définir un minimum négatif: {value_int}")
                return False
            value = str(value_int)
        elif key in ("point_max", "argent_max"):
            value_int = int(value)
            if value_int <= 0:
                logger.warning(f"Tentative de définir un maximum négatif ou nul: {value_int}")
                return False
            value = str(value_int)
        elif key == "card_margin":
            value_int = int(value)
            if value_int < 0:
                logger.warning(f"Tentative de définir une marge négative: {value_int}")
                return False
            value = str(value_int)
        elif key == "prix_carte":
            try:
                value_float = round(float(value), 2)
                if value_float < 0:
                    logger.warning(f"Tentative de définir prix_carte négatif: {value_float}")
                    return False
                value = str(value_float)
            except (ValueError, TypeError):
                logger.warning(f"Valeur prix_carte invalide: {value}")
                return False
        elif key == "payment_url":
            # Validation URL basique
            value_str = str(value).strip()
            if not value_str.startswith(("http://", "https://")):
                logger.warning(f"Tentative de définir une URL invalide: {value_str}")
                return False
            if len(value_str) > 500:  # Limite de longueur
                logger.warning(f"URL trop longue: {len(value_str)} caractères")
                return False
            value = value_str
        elif key == "staff_channel_id":
            # Validation ID de canal (peut être vide ou un ID valide)
            value_str = str(value).strip()
            if value_str and not value_str.startswith("-"):  # Les IDs de canal commencent par -
                logger.warning(f"ID de canal invalide (doit commencer par -): {value_str}")
                return False
            if value_str and len(value_str) > 20:  # Limite raisonnable
                logger.warning(f"ID de canal trop long: {len(value_str)} caractères")
                return False
            value = value_str
        elif key == "staff_thread_payment":
            # Validation ID de thread (peut être vide ou un entier)
            value_str = str(value).strip()
            if value_str:
                try:
                    int(value_str)  # Vérifier que c'est un entier valide
                except ValueError:
                    logger.warning(f"ID de thread invalide (doit être un nombre): {value_str}")
                    return False
            value = value_str
        elif key == "staff_thread_entretien":
            value_str = str(value).strip()
            if value_str:
                try:
                    int(value_str)  # Vérifier que c'est un entier valide
                except ValueError:
                    logger.warning(f"ID de thread invalide (doit être un nombre): {value_str}")
                    return False
            value = value_str
        elif key == "staff_thread_demande_access":
            value_str = str(value).strip()
            if value_str:
                try:
                    int(value_str)
                except ValueError:
                    logger.warning(f"ID de thread invalide (doit être un nombre): {value_str}")
                    return False
            value = value_str
        elif key == "announcement_text":
            # Validation texte d'annonce (peut être long, max 4096 caractères pour Telegram)
            value_str = str(value).strip()
            if len(value_str) > 4096:
                logger.warning(f"Texte d'annonce trop long: {len(value_str)} caractères (max 4096)")
                return False
            value = value_str
        elif key == "announcement_photo":
            # Validation file_id de photo (peut être vide pour supprimer)
            value_str = str(value).strip()
            if value_str and len(value_str) > 200:  # Les file_id Telegram sont généralement courts
                logger.warning(f"File ID de photo invalide (trop long): {len(value_str)} caractères")
                return False
            value = value_str
        elif key == "emergency_stop":
            # Validation arrêt d'urgence (true/false)
            value_str = str(value).strip().lower()
            if value_str not in ("true", "false"):
                logger.warning(f"Valeur d'arrêt d'urgence invalide (doit être 'true' ou 'false'): {value_str}")
                return False
            value = value_str
        else:
            logger.warning(f"Clé de configuration inconnue: {key}")
            return False
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO config (key, value, updated_at) VALUES (%s, %s, CURRENT_TIMESTAMP) "
                "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP",
                (key, value)
            )
            
            logger.info(f"Configuration mise à jour: {key} = {value}")
            _invalidate_config_cache(key)  # Invalider le cache après mise à jour
            return True
    except (psycopg2.Error, ValueError, TypeError) as e:
        logger.error(f"Erreur lors de la mise à jour de la config '{key}': {e}")
        return False


def get_argent_min() -> int:
    """Récupère le minimum d'achat d'argent (avec fallback compat)."""
    value = _get_cached_config("argent_min", None)
    if value is None:
        value = _get_cached_config("point_min", DEFAULT_POINT_MIN)
    try:
        return int(value)
    except (TypeError, ValueError):
        return DEFAULT_POINT_MIN


def get_argent_max() -> int:
    """Récupère le maximum d'achat d'argent (avec fallback compat)."""
    value = _get_cached_config("argent_max", None)
    if value is None:
        value = _get_cached_config("point_max", DEFAULT_POINT_MAX)
    try:
        return int(value)
    except (TypeError, ValueError):
        return DEFAULT_POINT_MAX


def get_point_min() -> int:
    """Alias compat historique."""
    return get_argent_min()


def get_point_max() -> int:
    """Alias compat historique."""
    return get_argent_max()


def get_price_per_point(points: int) -> float:
    """
    Retourne le prix unitaire d'un point (en euros) en fonction du palier atteint.
    Si le nombre de points est inférieur au plus petit palier, on utilise ce plus petit palier.
    """
    if points <= 0:
        return 0.0
    # Trouver le plus grand palier <= points
    thresholds = [t for t in PRICE_TABLE.keys() if points >= t]
    if thresholds:
        threshold = max(thresholds)
    else:
        threshold = min(PRICE_TABLE.keys())
    return PRICE_TABLE[threshold]


def compute_points_price(points: int, user_reduction: float = 0.0) -> tuple[float, float]:
    """
    Calcule le prix avant et après réduction pour un nombre de points donné.
    - Prix initial = points * prix par point (en fonction du palier)
    - Prix final = prix initial * (1 - réduction/100)
    Les deux sont arrondis au 0.05 € supérieur.
    Retourne (price_initial, price_final).
    """
    if points <= 0:
        return 0.0, 0.0

    base_price = points * get_price_per_point(points)
    # Arrondi au 0.05 € supérieur pour le prix initial
    price_initial = math.ceil(base_price * 20) / 20

    # Appliquer la réduction (facteur borné entre 0 et 1)
    factor = max(0.0, 1.0 - user_reduction / 100.0)
    price_final = math.ceil(price_initial * factor * 20) / 20
    return price_initial, price_final


def _price_cents(price_euros: float) -> int:
    """Convertit un prix en euros en centimes (entier) pour éviter les erreurs de flottants."""
    return round(price_euros * 100)


def euros_to_points(target_euros: float, user_reduction: float = 0.0) -> int:
    """
    Calcule le maximum de points tel que compute_points_price(points) <= target_euros.
    Utilise une dichotomie sur les paliers (repère = prix à l'entrée du palier),
    puis une dichotomie dans le palier ciblé. La monotonie est garantie par palier.
    Retourne 0 si target_euros <= 0 ou si PRICE_TABLE est vide.
    """
    if target_euros <= 0:
        return 0
    if not PRICE_TABLE:
        return 0

    paliers = _PALIERS_SORTED
    target_cents = _price_cents(target_euros)
    factor = max(0.0, 1.0 - user_reduction / 100.0)

    # Trouver le plus grand palier dont le prix minimum <= target (dichotomie)
    lo, hi = 0, len(paliers) - 1
    best_palier_idx = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        p = paliers[mid]
        _, price_at_p = compute_points_price(p, user_reduction)
        if _price_cents(price_at_p) <= target_cents:
            best_palier_idx = mid
            lo = mid + 1
        else:
            hi = mid - 1

    if best_palier_idx < 0:
        return 0

    palier = paliers[best_palier_idx]
    ppp = get_price_per_point(palier)
    # Borne supérieure : limite du palier suivant, ou estimation à partir du budget
    if best_palier_idx + 1 < len(paliers):
        palier_max = paliers[best_palier_idx + 1] - 1
    else:
        estimated = int(target_euros / (ppp * factor) * 1.05) + 100 if ppp > 0 else palier + 1000
        palier_max = min(estimated, MAX_POINTS_EUROS_BUDGET)

    # Dichotomie dans ce palier
    low, high = palier, palier_max
    best_points = palier - 1
    while low <= high:
        mid = (low + high) // 2
        _, price_final = compute_points_price(mid, user_reduction)
        if _price_cents(price_final) <= target_cents:
            best_points = mid
            low = mid + 1
        else:
            high = mid - 1

    return max(0, best_points)


def get_card_margin() -> int:
    """Récupère la marge pour l'achat de cartes (avec cache)"""
    return _get_cached_config("card_margin", DEFAULT_CARD_MARGIN)


def get_prix_carte() -> float:
    """Récupère le prix carte (en euros, float) pour le shop Carte (avec cache)"""
    val = _get_cached_config("prix_carte", "0")
    try:
        f = float(str(val).replace(",", "."))
        return max(0.0, round(f, 6))  # 6 décimales (prix/point peut être 0.0025)
    except (ValueError, TypeError):
        return 0.0


def get_prix_per_point_carte(card_points: int) -> float:
    """Prix unitaire effectif (€/point) pour une carte de card_points points (table CARTE_PRICE_TABLE)."""
    if card_points <= 0:
        return 0.0
    factor = 1.0
    for seuil in sorted(CARTE_PRICE_TABLE.keys(), reverse=True):
        if card_points >= seuil:
            factor = CARTE_PRICE_TABLE[seuil]
            break
    return get_prix_carte() * factor


def get_payment_url() -> str:
    """Récupère l'URL de paiement (avec cache)"""
    return _get_cached_config("payment_url", "https://example.com/pay")


def get_staff_channel_id() -> Optional[str]:
    """Récupère l'ID du canal staff (avec cache)"""
    channel_id = _get_cached_config("staff_channel_id", "")
    return channel_id if channel_id else None


def get_chat_id_from_update(update: Update) -> Optional[int]:
    """Récupère l'ID du chat depuis une mise à jour (utilisé pour obtenir l'ID réel d'un groupe)"""
    if update.effective_chat:
        return update.effective_chat.id
    return None


def get_staff_thread_payment() -> Optional[int]:
    """Récupère l'ID du thread de paiement dans le canal staff (avec cache)"""
    thread_id = _get_cached_config("staff_thread_payment", "")
    if thread_id:
        try:
            return int(thread_id)
        except ValueError:
            return None
    return None


def get_staff_thread_entretien() -> Optional[int]:
    """Récupère l'ID du thread entretien dans le canal staff (upload cache bannières, etc.)"""
    thread_id = _get_cached_config("staff_thread_entretien", "")
    if thread_id:
        try:
            return int(thread_id)
        except ValueError:
            return None
    return None


def get_staff_thread_demande_access() -> Optional[int]:
    """Récupère l'ID du thread des demandes d'accès dans le canal staff."""
    thread_id = _get_cached_config("staff_thread_demande_access", "")
    if thread_id:
        try:
            return int(thread_id)
        except ValueError:
            return None
    return None


def get_announcement_text() -> str:
    """Récupère le texte de l'annonce (avec cache)"""
    return _get_cached_config("announcement_text", "Aucune annonce pour le moment.")


def get_announcement_photo() -> Optional[str]:
    """Récupère le file_id de la photo de l'annonce (avec cache)"""
    photo_id = _get_cached_config("announcement_photo", "")
    return photo_id if photo_id else None


def is_emergency_stop_active() -> bool:
    """Vérifie si l'arrêt d'urgence est actif"""
    emergency_stop = get_config_value("emergency_stop", "false")
    return emergency_stop.lower() == "true"


async def send_to_staff_channel(
    bot,
    message: str,
    thread_id: Optional[int] = None,
    photo_file_id: Optional[str] = None,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: str = "Markdown"
):
    """
    Envoie un message dans le canal staff avec le thread spécifié.
    Si le canal n'est pas configuré, envoie à l'admin directement.
    Retourne le message envoyé si succès, None sinon.
    """
    staff_channel_id = get_staff_channel_id()
    
    try:
        if staff_channel_id and thread_id:
            # Convertir l'ID en int si c'est une string
            try:
                # Les IDs de groupe doivent être des entiers
                # Nettoyer l'ID (enlever espaces, etc.)
                clean_id = staff_channel_id.strip().replace(" ", "")
                channel_id_int = int(clean_id)
            except (ValueError, TypeError):
                logger.error(f"ID de canal invalide (ne peut pas être converti en int): {staff_channel_id}")
                channel_id_int = staff_channel_id  # Garder comme string en fallback
            
            # Envoyer dans le canal staff avec thread
            if photo_file_id:
                return await bot.send_photo(
                    chat_id=channel_id_int,
                    message_thread_id=thread_id,
                    photo=photo_file_id,
                    caption=message,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
            else:
                return await bot.send_message(
                    chat_id=channel_id_int,
                    message_thread_id=thread_id,
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
        else:
            # Fallback: envoyer directement à l'admin
            if photo_file_id:
                return await bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=photo_file_id,
                    caption=message,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
            else:
                return await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
    except TelegramError as e:
        error_msg = str(e)
        logger.error(f"Erreur lors de l'envoi au canal staff: {e}")
        
        # Si l'erreur est "Chat not found", informer l'admin avec plus de détails
        if "Chat not found" in error_msg or "chat not found" in error_msg.lower():
            logger.warning(
                f"Chat non trouvé avec l'ID: {channel_id_int if 'channel_id_int' in locals() else staff_channel_id}. "
                f"Vérifiez que le bot est membre du groupe et utilisez /get_chat_id dans le groupe pour obtenir l'ID correct."
            )
        
        # Tentative de fallback vers l'admin direct
        try:
            if photo_file_id:
                await bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=photo_file_id,
                    caption=message,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
            else:
                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
            return True
        except TelegramError as e2:
            logger.error(f"Erreur lors du fallback vers l'admin: {e2}")
            return False


async def send_notification(bot, user_id: int, message: str, parse_mode: str = "HTML") -> bool:
    """
    Envoie un message à un utilisateur (notification).
    Retourne True si succès, False sinon.
    """
    try:
        await bot.send_message(chat_id=user_id, text=message, parse_mode=parse_mode)
        return True
    except TelegramError as e:
        logger.error(f"Erreur notification user {user_id}: {e}")
        return False


def create_pending_payment(user_id: int, points: int, price: float, photo_file_id: Optional[str] = None) -> int:
    """Crée une transaction en attente de manière atomique (empêche les doublons grâce à l'index unique)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO pending_payments (user_id, points, price, photo_file_id, status, confirmation_message_id)
                VALUES (%s, %s, %s, %s, 'pending', NULL)
                RETURNING id
            """, (user_id, points, price, photo_file_id))
            
            payment_id = cursor.fetchone()[0]
            
            # Vérifier immédiatement que la transaction a bien été créée
            cursor.execute("SELECT id, status FROM pending_payments WHERE id = %s", (payment_id,))
            verification = cursor.fetchone()
            if verification:
                logger.info(f"Transaction en attente créée et vérifiée: ID={payment_id}, user_id={user_id}, points={points}, status={verification[1]}")
            else:
                logger.error(f"Transaction créée mais non trouvée lors de la vérification: ID={payment_id}, user_id={user_id}")
            
            return payment_id
    except psycopg2.IntegrityError as e:
        # Contrainte unique violée (l'utilisateur a déjà une transaction pending)
        logger.warning(f"Tentative de créer une transaction alors qu'une existe déjà pour l'utilisateur {user_id}: {e}")
        return 0
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la création de la transaction en attente: {e}")
        return 0


def update_payment_confirmation_message_id(payment_id: int, message_id: int) -> bool:
    """Met à jour le message_id de confirmation d'une transaction"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE pending_payments SET confirmation_message_id = %s WHERE id = %s",
                (message_id, payment_id)
            )
            
            return True
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la mise à jour du confirmation_message_id: {e}")
        return False


def get_payment_confirmation_message_id(payment_id: int) -> Optional[int]:
    """Récupère le message_id de confirmation d'une transaction"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT confirmation_message_id FROM pending_payments WHERE id = %s",
                (payment_id,)
            )
            result = cursor.fetchone()
            
            if result and result[0]:
                return result[0]
            return None
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération du confirmation_message_id: {e}")
        return None


def update_pending_payment_photo(payment_id: int, photo_file_id: str) -> bool:
    """Met à jour la photo d'une transaction en attente"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE pending_payments SET photo_file_id = %s WHERE id = %s",
                (photo_file_id, payment_id)
            )
            
            # Vérifier que la mise à jour a bien eu lieu
            rows_affected = cursor.rowcount
            if rows_affected == 0:
                logger.warning(f"Aucune transaction trouvée avec l'ID {payment_id} lors de la mise à jour de la photo")
                return False
            
            logger.info(f"Photo mise à jour avec succès pour la transaction {payment_id} ({rows_affected} ligne(s) modifiée(s))")
            return True
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la mise à jour de la photo pour la transaction {payment_id}: {e}")
        return False


def get_pending_payment(payment_id: int) -> Optional[tuple]:
    """Récupère une transaction en attente par ID"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, user_id, points, price, photo_file_id, created_at, status, confirmation_message_id "
                "FROM pending_payments WHERE id = %s",
                (payment_id,)
            )
            result = cursor.fetchone()
            
            return result
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération de la transaction: {e}")
        return None


def get_pending_payments_count() -> int:
    """Récupère le nombre de transactions en attente"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM pending_payments WHERE status = 'pending'")
            result = cursor.fetchone()
            return result[0] if result else 0
    except psycopg2.Error as e:
        logger.error(f"Erreur lors du comptage des transactions en attente: {e}")
        return 0


def get_user_payment_history(user_id: int, limit: int = 5, offset: int = 0) -> list:
    """
    Récupère l'historique des achats acceptés d'un utilisateur (tri par date décroissante).
    Retourne une liste de (id, points, created_at).
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, points, created_at
                FROM pending_payments
                WHERE user_id = %s AND status = 'accepted'
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (user_id, limit, offset))
            return cursor.fetchall()
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération de l'historique des achats: {e}")
        return []


def get_user_payment_history_count(user_id: int) -> int:
    """Retourne le nombre total d'achats de points (acceptés) pour un utilisateur."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM pending_payments WHERE user_id = %s AND status = 'accepted'",
                (user_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else 0
    except psycopg2.Error as e:
        logger.error(f"Erreur comptage historique points: {e}")
        return 0


def get_user_card_history_count(user_id: int) -> int:
    """Retourne le nombre total d'achats de cartes pour un utilisateur."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM card_purchase_history WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
    except psycopg2.Error as e:
        logger.error(f"Erreur comptage historique cartes: {e}")
        return 0


def insert_card_purchase_history(
    user_id: int,
    card_number: str,
    points: int,
    customer_id: Optional[str] = None,
) -> Optional[int]:
    """
    Enregistre un achat de carte dans l'historique (sans QR).
    customer_id: optionnel, permet de récupérer les infos complètes depuis kfc_storage.
    Retourne l'id de l'enregistrement créé ou None en cas d'erreur.
    """
    try:
        card_number_safe = (str(card_number).strip() or "N/A")[:255]
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO card_purchase_history (user_id, card_number, points, customer_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (user_id, card_number_safe, max(1, int(points)), customer_id))
            row = cursor.fetchone()
            return row[0] if row else None
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de l'insertion dans card_purchase_history: {e}")
        return None


def get_user_card_history(user_id: int, limit: int = 5, offset: int = 0) -> list:
    """
    Récupère l'historique des achats de cartes d'un utilisateur (tri par date décroissante).
    Retourne une liste de (id, card_number, points, created_at, customer_id).
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, card_number, points, created_at, customer_id
                FROM card_purchase_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (user_id, limit, offset))
            return cursor.fetchall()
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération de l'historique des cartes: {e}")
        return []


def get_card_purchase_by_id(record_id: int) -> Optional[tuple]:
    """Récupère un enregistrement d'historique carte par id. Retourne (id, user_id, card_number, points, created_at, customer_id) ou None."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, user_id, card_number, points, created_at, customer_id
                FROM card_purchase_history WHERE id = %s
            """, (record_id,))
            return cursor.fetchone()
    except psycopg2.Error as e:
        logger.error(f"Erreur get_card_purchase_by_id: {e}")
        return None


def get_user_click_history_count(user_id: int) -> int:
    """Retourne le nombre de commandes Click&Collect finalisées (SUBMITTED ou +) pour un utilisateur."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM click_order_history
                WHERE user_id = %s
                  AND status IN ('SUBMITTED', 'CHECKED_IN', 'COMPLETED', 'FAILED')
                """,
                (user_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else 0
    except psycopg2.Error as e:
        logger.error(f"Erreur comptage historique click: {e}")
        return 0


def get_user_click_history(user_id: int, limit: int = 5, offset: int = 0) -> list:
    """
    Récupère l'historique Click&Collect d'un utilisateur (SUBMITTED ou +), trié du plus récent au plus ancien.
    Retourne une liste de (id, order_number, total_points, submitted_at, store_name, status).
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, order_number, total_points, submitted_at, store_name, status
                FROM click_order_history
                WHERE user_id = %s
                  AND status IN ('SUBMITTED', 'CHECKED_IN', 'COMPLETED', 'FAILED')
                ORDER BY submitted_at DESC
                LIMIT %s OFFSET %s
                """,
                (user_id, limit, offset),
            )
            return cursor.fetchall()
    except psycopg2.Error as e:
        logger.error(f"Erreur récupération historique click: {e}")
        return []


def get_click_history_by_id(record_id: int) -> Optional[tuple]:
    """
    Récupère un enregistrement d'historique Click&Collect par id.
    Retourne None si introuvable.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, user_id, panier_id, order_uuid, order_number, confirmation_url, status,
                       store_id, store_name, store_city, account_id, telegram_user, email, phone_number,
                       last_name, first_name, date_of_birth, total_points, submitted_at
                FROM click_order_history
                WHERE id = %s
                """,
                (record_id,),
            )
            return cursor.fetchone()
    except psycopg2.Error as e:
        logger.error(f"Erreur get_click_history_by_id: {e}")
        return None


def get_click_history_items(record_id: int) -> list:
    """
    Récupère les lignes articles d'un historique Click&Collect.
    Retourne une liste de (name, cost, quantity, line_total_points).
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT name, cost, quantity, line_total_points
                FROM click_order_history_items
                WHERE history_id = %s
                ORDER BY id ASC
                """,
                (record_id,),
            )
            return cursor.fetchall()
    except psycopg2.Error as e:
        logger.error(f"Erreur get_click_history_items: {e}")
        return []


def get_kfc_storage_by_customer_id(customer_id: str) -> Optional[dict]:
    """
    Récupère une ligne de kfc_storage par customer_id (unique).
    Retourne un dict avec carte, email, password, nom, point, expired_at, prenom, numero, ddb, id, etc.
    """
    if not customer_id or not str(customer_id).strip():
        return None
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT carte, email, password, nom, point, expired_at, prenom, numero, ddb, id, customer_id
                FROM kfc_storage WHERE customer_id = %s
            """, (str(customer_id).strip(),))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "carte": row[0],
                "email": row[1],
                "password": row[2],
                "nom": row[3],
                "point": row[4],
                "expired_at": row[5],
                "prenom": row[6],
                "numero": row[7],
                "ddb": row[8],
                "id": row[9],
                "customer_id": row[10],
            }
    except psycopg2.Error as e:
        logger.error(f"Erreur get_kfc_storage_by_customer_id: {e}")
        return None


def _format_hist_date(created_at) -> str:
    """Formate une date pour l'affichage bouton historique (JJ/MM)."""
    try:
        if hasattr(created_at, "strftime"):
            return created_at.strftime("%d/%m")
        d = str(created_at)[:10]
        if len(d) >= 10:
            dt = datetime.strptime(d[:10], "%Y-%m-%d")
            return dt.strftime("%d/%m")
        return "??/??"
    except Exception:
        return "??/??"


def _build_hist_points_keyboard(rows: list, user_id: int, page: int, page_size: int) -> list:
    """Construit le clavier pour une page de l'historique points. rows = [(id, points, created_at), ...]"""
    keyboard = []
    for (pid, points, created_at) in rows:
        d = _format_hist_date(created_at)
        keyboard.append([InlineKeyboardButton(f"{d} : {points} argent", callback_data=f"hist_points_detail_{pid}")])
    next_rows = get_user_payment_history(user_id, limit=page_size, offset=(page + 1) * page_size)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀ 5 suivantes", callback_data=f"hist_points_page_{page - 1}"))
    if next_rows:
        nav.append(InlineKeyboardButton("▶ 5 précédentes", callback_data=f"hist_points_page_{page + 1}"))
    if nav:
        keyboard.append(nav)
    keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data="cmd_historique")])
    return keyboard


def _build_hist_cartes_keyboard(rows: list, user_id: int, page: int, page_size: int) -> list:
    """Construit le clavier pour une page de l'historique cartes. rows = [(id, card_number, points, created_at, customer_id), ...]"""
    keyboard = []
    for (rid, card_number, points, created_at, *_) in rows:
        d = _format_hist_date(created_at)
        keyboard.append([InlineKeyboardButton(f"{d} : {points} pts", callback_data=f"hist_cartes_detail_{rid}")])
    next_rows = get_user_card_history(user_id, limit=page_size, offset=(page + 1) * page_size)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀ 5 suivantes", callback_data=f"hist_cartes_page_{page - 1}"))
    if next_rows:
        nav.append(InlineKeyboardButton("▶ 5 précédentes", callback_data=f"hist_cartes_page_{page + 1}"))
    if nav:
        keyboard.append(nav)
    keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data="cmd_historique")])
    return keyboard


def _build_hist_click_keyboard(rows: list, user_id: int, page: int, page_size: int) -> list:
    """Construit le clavier pour une page de l'historique Click&Collect."""
    keyboard = []
    for (rid, order_number, total_points, submitted_at, store_name, status) in rows:
        d = _format_hist_date(submitted_at)
        order_txt = f"#{order_number}" if order_number else "N/A"
        status_txt = (status or "?").upper()
        store_txt = sanitize_display_name(store_name or "KFC")
        label = f"{d} : {order_txt} • {total_points} pts • {store_txt} • {status_txt}"
        keyboard.append([InlineKeyboardButton(label[:64], callback_data=f"hist_click_detail_{rid}")])
    next_rows = get_user_click_history(user_id, limit=page_size, offset=(page + 1) * page_size)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀ 5 suivantes", callback_data=f"hist_click_page_{page - 1}"))
    if next_rows:
        nav.append(InlineKeyboardButton("▶ 5 précédentes", callback_data=f"hist_click_page_{page + 1}"))
    if nav:
        keyboard.append(nav)
    keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data="cmd_historique")])
    return keyboard


def reset_all_pending_payments() -> int:
    """Réinitialise toutes les transactions en attente (les passe en 'cancelled')"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pending_payments 
                SET status = 'cancelled' 
                WHERE status = 'pending'
            """)
            rows_affected = cursor.rowcount
            logger.info(f"{rows_affected} transaction(s) en attente réinitialisée(s)")
            return rows_affected
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la réinitialisation des transactions: {e}")
        return 0


def get_user_pending_payment(user_id: int) -> Optional[int]:
    """Récupère l'ID de la transaction en attente d'un utilisateur"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id FROM pending_payments WHERE user_id = %s AND status = 'pending' ORDER BY created_at DESC LIMIT 1",
                (user_id,)
            )
            result = cursor.fetchone()
            
            if result:
                payment_id = result[0]
                logger.debug(f"Transaction en attente trouvée pour user_id={user_id}: payment_id={payment_id}")
                return payment_id
            else:
                # Vérifier s'il y a des transactions avec d'autres statuts pour debug
                cursor.execute(
                    "SELECT id, status, created_at FROM pending_payments WHERE user_id = %s ORDER BY created_at DESC LIMIT 5",
                    (user_id,)
                )
                all_payments = cursor.fetchall()
                if all_payments:
                    logger.warning(f"Aucune transaction 'pending' trouvée pour user_id={user_id}, mais {len(all_payments)} transaction(s) trouvée(s) avec d'autres statuts: {all_payments}")
                else:
                    logger.debug(f"Aucune transaction trouvée pour user_id={user_id}")
                return None
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération de la transaction en attente pour user_id={user_id}: {e}")
        return None


def update_payment_status(payment_id: int, status: str) -> bool:
    """Met à jour le statut d'une transaction"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE pending_payments SET status = %s WHERE id = %s",
                (status, payment_id)
            )
            
            return True
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la mise à jour du statut: {e}")
        return False


def cancel_user_pending_payment_atomic(user_id: int) -> Optional[int]:
    """
    Annule la transaction pending la plus récente de l'utilisateur de façon atomique.
    Retourne l'id annulé, ou None si rien à annuler.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pending_payments
                SET status = 'cancelled'
                WHERE id = (
                    SELECT id
                    FROM pending_payments
                    WHERE user_id = %s AND status = 'pending'
                    ORDER BY created_at DESC
                    LIMIT 1
                )
                AND status = 'pending'
                RETURNING id
            """, (user_id,))
            row = cursor.fetchone()
            return row[0] if row else None
    except psycopg2.Error as e:
        logger.error(f"Erreur annulation atomique user_id={user_id}: {e}")
        return None


def cleanup_old_pending_payments(days: int = 7) -> int:
    """Nettoie les transactions en attente de plus de X jours (marquées comme expirées)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            cursor.execute(
                "UPDATE pending_payments SET status = 'expired' WHERE status = 'pending' AND created_at < %s",
                (cutoff_date,)
            )
            
            updated_count = cursor.rowcount
            
            if updated_count > 0:
                logger.info(f"Nettoyage automatique: {updated_count} transactions expirées marquées")
            
            return updated_count
    except psycopg2.Error as e:
        logger.error(f"Erreur lors du nettoyage des transactions expirées: {e}")
        return 0


def has_user_pending_payment_in_db(user_id: int) -> bool:
    """Vérifie dans la DB si l'utilisateur a une transaction en attente (source de vérité)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT COUNT(*) FROM pending_payments WHERE user_id = %s AND status = 'pending'",
                (user_id,)
            )
            count = cursor.fetchone()[0]
            
            return count > 0
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la vérification des transactions en attente: {e}")
        return False


def accept_payment_atomic(payment_id: int) -> Optional[tuple]:
    """
    Accepte un paiement de manière atomique dans une seule transaction.
    Vérifie le statut, crédite le solde utilisateur, et met à jour le statut en une seule opération.
    Retourne (user_id, credited_amount, new_balance) si succès, None si échec.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Lock explicite sur la transaction avec FOR UPDATE pour éviter les doubles traitements
            cursor.execute("""
                SELECT id, user_id, points, price, status 
                FROM pending_payments 
                WHERE id = %s AND status = 'pending'
                FOR UPDATE
            """, (payment_id,))
            
            payment = cursor.fetchone()
            
            if not payment:
                # Transaction déjà traitée ou introuvable
                return None
            
            _, user_id, points, price, _ = payment
            # Nouvelle logique achat: 1€ payé = 1 argent crédité.
            # On crédite selon le prix, avec fallback historique sur "points".
            try:
                credited_amount = float(price) if price is not None else 0.0
            except (TypeError, ValueError):
                credited_amount = 0.0
            if credited_amount <= 0:
                credited_amount = float(points or 0)
            
            # Vérifier que l'utilisateur existe et lock sur la ligne utilisateur
            cursor.execute(
                "SELECT points FROM users WHERE user_id = %s FOR UPDATE",
                (user_id,)
            )
            user_result = cursor.fetchone()
            
            if not user_result:
                logger.warning(f"Utilisateur {user_id} introuvable lors de l'acceptation du paiement {payment_id}")
                return None
            
            # Mise à jour atomique : solde + points et statut de la transaction
            cursor.execute("""
                UPDATE users 
                SET points = points + %s, updated_at = CURRENT_TIMESTAMP 
                WHERE user_id = %s
            """, (credited_amount, user_id))
            
            if cursor.rowcount == 0:
                return None
            
            # Récupérer le nouveau solde
            cursor.execute("SELECT points FROM users WHERE user_id = %s", (user_id,))
            new_balance = cursor.fetchone()[0]
            
            # Mettre à jour le statut de la transaction
            cursor.execute("""
                UPDATE pending_payments 
                SET status = 'accepted' 
                WHERE id = %s AND status = 'pending'
            """, (payment_id,))
            
            if cursor.rowcount == 0:
                # Le statut a changé entre temps (race condition détectée)
                conn.rollback()
                return None
            
            logger.info(f"Paiement {payment_id} accepté atomiquement: user_id={user_id}, argent={credited_amount:.2f}, new_balance={float(new_balance):.2f}")
            return (user_id, credited_amount, new_balance)
            
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de l'acceptation atomique du paiement {payment_id}: {e}")
        return None


def validate_config() -> bool:
    """Valide la configuration du bot"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN n'est pas défini dans le fichier .env")
        return False
    
    # Validation du format du token Telegram (format: NUMBERS:LETTERS_AND_NUMBERS)
    if ':' not in BOT_TOKEN:
        logger.error("BOT_TOKEN n'a pas le format attendu")
        return False
    
    token_parts = BOT_TOKEN.split(':', 1)
    if len(token_parts) != 2 or not token_parts[0].isdigit() or not token_parts[1]:
        logger.error("BOT_TOKEN a un format invalide")
        return False
    
    if not all([ADMIN_ID, MODERATOR_ID, SELLER_ID]):
        logger.warning("Certains IDs de rôles ne sont pas définis dans .env")
    
    return True


def get_user_role(user_id: int) -> str:
    """Détermine le rôle de l'utilisateur (ADMIN_ID est toujours admin, sinon lit depuis la DB)"""
    if user_id == ADMIN_ID:
        return "admin"

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
            row = cursor.fetchone()
            if row and row[0]:
                return row[0]
            # Si pas dans la DB, utiliser les anciennes constantes pour compatibilité
            if user_id == SELLER_ID:
                return "vendeur"
            elif user_id == MODERATOR_ID:
                return "moderator"
            return "user"
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération du rôle pour user_id={user_id}: {e}")
        # Fallback vers l'ancien système
        return "user"


def get_effective_role(user_id: int, context: Optional[ContextTypes.DEFAULT_TYPE]) -> str:
    """Rôle effectif pour l'UI/ACL : un admin peut choisir d'agir en tant qu'utilisateur (sans privilèges)."""
    role = get_user_role(user_id)
    if role != "admin":
        return role
    if context is None:
        return role
    if context.user_data.get("view_as_user"):
        return "user"
    return role


def set_user_role(user_id: int, role: str) -> bool:
    """Définit le rôle d'un utilisateur dans la base de données"""
    if user_id == ADMIN_ID:
        return False  # On ne peut pas modifier le rôle de l'admin principal
    
    if role not in ('user', 'vendeur', 'moderator'):
        logger.warning(f"Tentative de définir un rôle invalide: {role}")
        return False
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # S'assurer que l'utilisateur existe dans la DB
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            if not cursor.fetchone():
                # Créer l'utilisateur s'il n'existe pas
                cursor.execute(
                    "INSERT INTO users (user_id, points, role) VALUES (%s, 0, %s) ON CONFLICT (user_id) DO UPDATE SET role = %s, updated_at = CURRENT_TIMESTAMP",
                    (user_id, role, role)
                )
            else:
                cursor.execute(
                    "UPDATE users SET role = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
                    (role, user_id)
                )
            return True
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la définition du rôle pour user_id={user_id}, role={role}: {e}")
        return False


def _get_token_public_secret() -> bytes:
    """Secret pour dériver le token public (réversible uniquement avec ce secret)."""
    secret = os.getenv("TOKEN_PUBLIC_SECRET") or os.getenv("BOT_TOKEN") or "default-secret"
    return secret.encode("utf-8")


def derive_public_token(user_id: int) -> str:
    """
    Dérive un token public à partir de l'id utilisateur (déterministe, non réversible sans le secret).
    Même user_id -> même token. 10 caractères hex.
    """
    raw = hmac.new(
        _get_token_public_secret(),
        str(user_id).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return raw[:10]


def derive_private_token(user_id: int) -> str:
    """
    Dérive un token privé à partir de l'id utilisateur (déterministe, différent du public).
    Même user_id -> même token. 10 caractères hex.
    """
    raw = hmac.new(
        _get_token_public_secret(),
        (str(user_id) + ":prive").encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return raw[:10]


def _ensure_user_tokens(user_id: int) -> bool:
    """
    Génère et enregistre token_publique et token_prive pour un utilisateur.
    À appeler à la création ou si tokens manquants.
    """
    try:
        pub = derive_public_token(user_id)
        priv = derive_private_token(user_id)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET token_publique = %s, token_prive = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
                (pub, priv, user_id),
            )
            return cursor.rowcount > 0
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de l'enregistrement des tokens pour user_id={user_id}: {e}")
        return False


def get_users_by_role(role: str) -> list[tuple[int, int]]:
    """Récupère la liste des utilisateurs avec un rôle spécifique (retourne [(user_id, points), ...])"""
    if role not in ('user', 'vendeur', 'moderator'):
        return []
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, points FROM users WHERE role = %s ORDER BY user_id",
                (role,)
            )
            return cursor.fetchall()
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération des utilisateurs par rôle {role}: {e}")
        return []


def get_users_with_reduction() -> list[tuple[int, float, str]]:
    """Récupère la liste des utilisateurs avec une réduction > 0 (retourne [(user_id, reduction, role), ...])"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, COALESCE(reduction, 0)::float as reduction, COALESCE(role, 'user') as role
                FROM users
                WHERE COALESCE(reduction, 0) > 0
                ORDER BY reduction DESC, user_id
            """)
            return [(r[0], round(float(r[1]), 2), r[2]) for r in cursor.fetchall()]
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération des utilisateurs avec réduction: {e}")
        return []


def get_user_reduction(user_id: int) -> float:
    """Récupère le taux de réduction d'un utilisateur (0-100, 2 décimales)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(reduction, 0) FROM users WHERE user_id = %s
            """, (user_id,))
            row = cursor.fetchone()
            if row and row[0] is not None:
                return round(float(row[0]), 2)
            return 0.0
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération de la réduction pour user_id={user_id}: {e}")
        return 0.0


def set_user_reduction(user_id: int, reduction: float) -> bool:
    """Définit le taux de réduction d'un utilisateur (0-100, 2 décimales)"""
    if reduction < 0 or reduction > 100:
        logger.warning(f"Tentative de définir une réduction invalide: {reduction}")
        return False
    reduction = round(float(reduction), 2)
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # S'assurer que l'utilisateur existe dans la DB
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            if not cursor.fetchone():
                # Créer l'utilisateur s'il n'existe pas
                cursor.execute(
                    "INSERT INTO users (user_id, points, reduction) VALUES (%s, 0, %s) ON CONFLICT (user_id) DO UPDATE SET reduction = EXCLUDED.reduction, updated_at = CURRENT_TIMESTAMP",
                    (user_id, reduction)
                )
            else:
                cursor.execute(
                    "UPDATE users SET reduction = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
                    (reduction, user_id)
                )
            return True
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la définition de la réduction pour user_id={user_id}, reduction={reduction}: {e}")
        return False


def get_role_statistics() -> dict[str, int]:
    """Récupère les statistiques des rôles (nombre d'utilisateurs par rôle)"""
    stats = {'admin': 1, 'vendeur': 0, 'moderator': 0, 'user': 0}  # Admin compte toujours comme 1
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role, COUNT(*) FROM users WHERE role IS NOT NULL GROUP BY role")
            rows = cursor.fetchall()
            for role, count in rows:
                if role in stats:
                    stats[role] += count
                else:
                    stats['user'] += count  # Les rôles non reconnus comptent comme user
            
            # Compter aussi les utilisateurs sans rôle explicite (NULL ou non dans la DB)
            cursor.execute("SELECT COUNT(*) FROM users WHERE role IS NULL OR role = ''")
            null_count = cursor.fetchone()[0]
            stats['user'] += null_count
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération des statistiques de rôle: {e}")
    
    return stats


def validate_callback_data(callback_data: Optional[str]) -> bool:
    """Valide et sanitise les données de callback"""
    if not callback_data:
        return False
    
    # Whitelist des callback_data autorisés
    allowed_callbacks = {
        "menu_principal",
        "cmd_start",
        "start_as_admin",
        "start_as_user",
        "cmd_shop",
        "cmd_config",
        "cmd_stat_general",
        "cmd_stock",
        "cmd_user",
        "cmd_panel_vendeur",
            "cmd_annonce",
            "cmd_moi",
            "cmd_historique",
            "hist_points",
            "hist_cartes",
            "hist_click",
            "cmd_acheter_points",
            "cmd_boutique",
            "boutique_click_collect",
            "boutique_carte",
            "boutique_carte_custom",
            "click_collect_back_cities",
            "click_collect_back_stores",
            "click_collect_back_cats",
            "click_collect_panier",
            "click_collect_commander",
            "click_collect_commander_continue",
            "click_collect_retry_token",
            "click_collect_validate",
            "click_collect_3min",
            "click_collect_show_submit_info",
            "click_collect_submit_info_back",
            "click_collect_modgrps_cancel",
            "click_collect_remove_cancel",
        "points_inc",
        "points_dec",
        "points_validate",
        "points_formula_choice",
        "config_points",
        "config_carte",
        "config_role",
        "config_payement",
        "config_reset_payments",
        "config_reset_payments_confirm",
        "config_canal",
        "config_annonce",
        "config_arret",
        "config_storage",
        "emergency_stop_enable",
        "emergency_stop_disable",
        "config_price_edit",
        "config_min_edit",
        "config_max_edit",
        "config_card_margin_edit",
        "config_prix_carte_edit",
        "config_payment_url_edit",
        "config_staff_channel_edit",
        "config_staff_thread_payment_edit",
        "config_staff_thread_demande_access_edit",
        "config_annonce_text_edit",
        "config_annonce_photo_edit",
        "config_annonce_photo_delete",
        "payment_accept",
        "payment_refuse",
        "cancel_payment",
        "role_list_vendeur",
        "role_list_moderator",
        "role_list_reduction",
        "role_add_select",
        "role_add_vendeur",
        "role_add_moderator",
        "role_remove_select",
        "role_remove_vendeur",
        "role_remove_moderator",
        "role_reduction_edit",
        "vendeur_reduction_skip",
        "user_list",
        "user_info",
        "user_list_page",
        "admin_create_account",
        "demande_access_send",
    }
    
    if callback_data.startswith("demande_accept_") or callback_data.startswith("demande_refuse_"):
        try:
            uid = int(callback_data.split("_")[-1])
            if uid > 0:
                return True
        except (ValueError, IndexError):
            return False

    # Validation pour les callbacks avec paramètres (format: prefix_value)
    if callback_data.startswith("points_inc_") or callback_data.startswith("points_dec_") or callback_data.startswith("points_validate_"):
        try:
            value = int(callback_data.split("_")[-1])
            if 0 <= value <= 10000:  # Limite raisonnable
                return True
        except (ValueError, IndexError):
            return False

    if callback_data.startswith("points_formula_"):
        suffix = callback_data.replace("points_formula_", "", 1)
        return suffix == "choice" or suffix in POINTS_FORMULA_DEFAULTS
    
    if callback_data.startswith("payment_accept_") or callback_data.startswith("payment_refuse_"):
        try:
            payment_id = int(callback_data.split("_")[-1])
            if payment_id > 0:
                return True
        except (ValueError, IndexError):
            return False
    
    if callback_data.startswith("user_list_page_"):
        # Validation de la pagination (format: user_list_page_N)
        try:
            page = int(callback_data.split("_")[-1])
            if page >= 0:
                return True
        except (ValueError, IndexError):
            return False
    
    for prefix in ("boutique_carte_points_",):
        if callback_data.startswith(prefix):
            try:
                points = int(callback_data.split("_")[-1])
                if 50 <= points <= 10000:
                    return True
            except (ValueError, IndexError):
                pass
            return False

    if callback_data.startswith("click_collect_city_") or callback_data.startswith("click_collect_store_") or callback_data.startswith("click_collect_cat_") or callback_data.startswith("click_collect_confirm_store_"):
        try:
            idx = int(callback_data.split("_")[-1])
            if 0 <= idx <= 999:
                return True
        except (ValueError, IndexError):
            pass
        return False

    if callback_data.startswith("click_collect_art_plus_") or callback_data.startswith("click_collect_art_minus_") or callback_data.startswith("click_collect_art_prev_") or callback_data.startswith("click_collect_art_next_"):
        try:
            parts = callback_data.split("_")
            if len(parts) >= 5:
                cat_idx = int(parts[-2])
                art_idx = int(parts[-1])
                if 0 <= cat_idx <= 99 and 0 <= art_idx <= 999:
                    return True
        except (ValueError, IndexError):
            pass
        return False

    if callback_data.startswith("click_collect_modgrps_sel_"):
        try:
            parts = callback_data.split("_")
            if len(parts) >= 5:
                group_idx = int(parts[-2])
                mod_idx = int(parts[-1])
                if 0 <= group_idx <= 99 and 0 <= mod_idx <= 99:
                    return True
        except (ValueError, IndexError):
            pass
        return False

    if callback_data.startswith("click_collect_modgrps_m_"):
        try:
            parts = callback_data.split("_")
            if len(parts) >= 4:
                if len(parts) >= 5 and parts[-2] == "done":
                    group_idx = int(parts[-1])
                    if 0 <= group_idx <= 99:
                        return True
                else:
                    group_idx = int(parts[-2])
                    mod_idx = int(parts[-1])
                    if 0 <= group_idx <= 99 and 0 <= mod_idx <= 99:
                        return True
        except (ValueError, IndexError):
            pass
        return False

    if callback_data.startswith("click_collect_remove_line_"):
        try:
            line_idx = int(callback_data.split("_")[-1])
            if 0 <= line_idx <= 999:
                return True
        except (ValueError, IndexError):
            pass
        return False

    if callback_data.startswith("cancel_payment_"):
        try:
            value = int(callback_data.split("_")[-1])
            if 0 <= value <= 10000:
                return True
        except (ValueError, IndexError):
            return False

    if callback_data.startswith("hist_points_page_") or callback_data.startswith("hist_cartes_page_") or callback_data.startswith("hist_click_page_"):
        try:
            page = int(callback_data.split("_")[-1])
            if page >= 0:
                return True
        except (ValueError, IndexError):
            return False

    if callback_data.startswith("hist_points_detail_") or callback_data.startswith("hist_cartes_detail_") or callback_data.startswith("hist_click_detail_"):
        try:
            pid = int(callback_data.split("_")[-1])
            if pid > 0:
                return True
        except (ValueError, IndexError):
            return False

    if callback_data.startswith("card_info_full_") or callback_data.startswith("card_info_short_"):
        try:
            record_id = int(callback_data.split("_")[-1])
            if record_id > 0:
                return True
        except (ValueError, IndexError):
            return False

    return callback_data in allowed_callbacks


def sanitize_text(text: Optional[str], max_length: int = 4096) -> str:
    """Sanitise le texte pour éviter les injections et limiter la longueur"""
    if not text:
        return ""
    
    # Limiter la longueur (limite Telegram: 4096 caractères)
    if len(text) > max_length:
        text = text[:max_length - 3] + "..."
    
    return text


def escape_markdown(text: Optional[str]) -> str:
    """
    Échappe le Markdown "classique" (parse_mode="Markdown") pour éviter les casses d'affichage
    quand on injecte des données utilisateur (nom, username, message, etc.).
    """
    if text is None:
        return ""
    # Markdown v1 minimal: \ _ * ` [
    for ch in ("\\", "_", "*", "`", "["):
        text = text.replace(ch, "\\" + ch)
    return text


def escape_html(text: Optional[str]) -> str:
    """
    Échappe le HTML (parse_mode="HTML") pour éviter les injections XSS
    quand on injecte des données utilisateur (nom, username, message, etc.).
    """
    if text is None:
        return ""
    # Échapper les caractères HTML spéciaux
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&#39;")
    return text


def sanitize_display_name(text: Optional[str]) -> str:
    """
    Nettoie un nom pour l'affichage uniquement (sans modifier les données stockées).
    Retire les séquences indésirables (amp;, @, caractères spéciaux type ®™) qui
    peuvent provenir des données API ou casser l'affichage Telegram.
    """
    if not text:
        return "" if text is not None else "?"
    # Résidu d'entité HTML mal décodée
    s = text.replace("amp;", "")
    # @ peut être interprété comme mention Telegram
    s = s.replace("@", " ")
    # Caractères de marque / spéciaux souvent indésirables à l'affichage
    for char in ("®", "™", "‰", "‱"):
        s = s.replace(char, "")
    # Espaces multiples ou en trop
    s = re.sub(r"\s+", " ", s).strip()
    return s if s else "?"


def mask_phone_for_click_display(phone: Optional[str]) -> str:
    """
    Masque un numéro de téléphone pour l'affichage Click&Collect.
    Format cible: xxxxx* **xx (5 premiers + masquage + 2 derniers).
    """
    if not phone:
        return "—"
    digits = re.sub(r"\D", "", str(phone))
    if len(digits) < 4:
        return "*" * len(digits) if digits else "—"
    if len(digits) <= 7:
        return f"{digits[0]}* **{digits[-2:]}"
    return f"{digits[:2]} {digits[2:4]} {digits[4:5]}* ** {digits[-2:]}"


# ========== SYSTÈME ESTHÉTIQUE ==========

# Couleurs via emojis (palette cohérente)
COLOR_THEMES = {
    "primary": "🔵",      # Bleu - Actions principales
    "success": "🟢",      # Vert - Succès/confirmations
    "warning": "🟡",      # Jaune - Avertissements
    "danger": "🔴",       # Rouge - Erreurs/refus
    "info": "🔵",         # Bleu clair - Informations
    "purple": "🟣",       # Violet - Spécial/fonctions premium
    "orange": "🟠",       # Orange - Achats/transactions
    "gold": "⭐",         # Or - Points/solde important
}

# Bannières textuelles (emojis répétés)
def create_banner(emoji: str, width: int = 20) -> str:
    """Crée une bannière avec emoji répété"""
    return emoji * width


def format_header_rich(title: str, main_emoji: str = "", color_theme: str = "primary", banner: bool = False) -> str:
    """Crée un en-tête simple avec emoji"""
    if main_emoji:
        title_formatted = f"{main_emoji} <b>{title}</b>"
    else:
        title_formatted = f"<b>{title}</b>"
    
    return title_formatted


def format_section_rich(title: str, content: str = "", emoji: str = "", color_theme: str = "info", highlight: bool = False) -> str:
    """Crée une section riche avec emoji et mise en forme"""
    color_emoji = COLOR_THEMES.get(color_theme, "")
    
    if highlight:
        # Section importante - mise en évidence
        title_formatted = f"\n{emoji} <b>{title.upper()}</b> {emoji}"
    else:
        title_formatted = f"\n{emoji} <b>{title}</b>"
    
    if content:
        return f"{title_formatted}\n<i>{content}</i>" if highlight else f"{title_formatted}\n{content}"
    return title_formatted


def format_highlight_box(text: str, emoji: str = "✨", color_theme: str = "gold") -> str:
    """Crée une boîte de mise en évidence pour informations importantes"""
    return f"\n{emoji} <b>{text}</b> {emoji}"


def format_info_card(label: str, value: str, label_emoji: str = "", value_highlight: bool = False) -> str:
    """Crée une carte d'information stylisée"""
    if value_highlight:
        formatted_value = f"<b><u>{value}</u></b>"
    else:
        formatted_value = f"<b>{value}</b>"
    
    if label_emoji:
        return f"{label_emoji} <b>{label} :</b> {formatted_value}"
    return f"<b>{label} :</b> {formatted_value}"


def format_status_badge(text: str, status: str = "success") -> str:
    """Crée un badge de statut coloré"""
    status_emojis = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "pending": "⏳",
        "processing": "🔄"
    }
    emoji = status_emojis.get(status, "•")
    color = COLOR_THEMES.get(status if status in COLOR_THEMES else "info", "")
    return f"{emoji} <b>{text}</b> {emoji}"


# Fonctions de compatibilité (pour migration progressive)
def format_header(title: str, emoji: str = "", separator_length: int = 21) -> str:
    """Fonction de compatibilité - utilise format_header_rich"""
    return format_header_rich(title, emoji, "primary", banner=False)


async def _send_photo_for_banner_cache(bot, banner_path: str, caption: str):
    """
    Envoie une photo (bannière) pour obtenir un file_id Telegram.
    Essaie d'abord le thread entretien du canal staff ; en cas d'erreur ou non configuré, envoie à l'admin.
    Retourne le message envoyé (pour en extraire file_id et supprimer), ou None.
    """
    channel_id = get_staff_channel_id()
    thread_id = get_staff_thread_entretien()
    if channel_id and thread_id:
        try:
            with open(banner_path, 'rb') as photo:
                channel_id_int = int(channel_id.strip().replace(" ", ""))
                msg = await bot.send_photo(
                    chat_id=channel_id_int,
                    message_thread_id=thread_id,
                    photo=photo,
                    caption=caption,
                )
            return msg
        except Exception as e:
            logger.warning(f"Envoi bannière vers thread entretien échoué, fallback admin: {e}")
    if ADMIN_ID:
        try:
            with open(banner_path, 'rb') as photo:
                msg = await bot.send_photo(chat_id=ADMIN_ID, photo=photo, caption=caption)
            return msg
        except Exception as e:
            logger.error(f"Envoi bannière vers admin échoué: {e}")
    return None


async def get_or_upload_profil_banner(context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """
    Récupère le file_id de la bannière profil (avec cache).
    Upload une seule fois au premier appel (thread entretien ou admin), puis réutilise le file_id.
    """
    global _profil_banner_file_id

    if _profil_banner_file_id:
        return _profil_banner_file_id

    with _profil_banner_lock:
        if _profil_banner_file_id:
            return _profil_banner_file_id

        banner_path = "banniere_profil.jpg"
        if not os.path.exists(banner_path):
            logger.warning(f"Bannière profil non trouvée: {banner_path}")
            return None

        try:
            message = await _send_photo_for_banner_cache(
                context.bot, banner_path, "Bannière profil (upload cache)"
            )
            if message:
                _profil_banner_file_id = message.photo[-1].file_id
                logger.info(f"Bannière profil uploadée, file_id obtenu (longueur: {len(_profil_banner_file_id)})")
                try:
                    await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
                except Exception:
                    pass
                return _profil_banner_file_id
            if not ADMIN_ID:
                logger.error("ADMIN_ID non configuré, impossible d'uploader la bannière")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de l'upload de la bannière profil: {e}")
            return None


async def get_or_upload_shop_banner(context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """
    Récupère le file_id de la bannière shop (avec cache).
    Upload une seule fois au premier appel, puis réutilise le file_id.
    """
    global _shop_banner_file_id
    
    # Si déjà en cache, retourner immédiatement (pas besoin de lock)
    if _shop_banner_file_id:
        return _shop_banner_file_id
    
    # Upload nécessaire - utiliser lock pour éviter les doubles uploads
    with _shop_banner_lock:
        # Double-check après avoir acquis le lock
        if _shop_banner_file_id:
            return _shop_banner_file_id
        
        banner_path = "banniere_shop.jpg"
        if not os.path.exists(banner_path):
            logger.warning(f"Bannière shop non trouvée: {banner_path}")
            return None
        
        try:
            message = await _send_photo_for_banner_cache(
                context.bot, banner_path, "Bannière shop (upload cache)"
            )
            if message:
                _shop_banner_file_id = message.photo[-1].file_id
                logger.info(f"Bannière shop uploadée, file_id obtenu (longueur: {len(_shop_banner_file_id)})")
                try:
                    await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
                except Exception:
                    pass
                return _shop_banner_file_id
            if not ADMIN_ID:
                logger.error("ADMIN_ID non configuré, impossible d'uploader la bannière")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de l'upload de la bannière shop: {e}")
            return None


async def get_or_upload_points_banner(context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """
    Récupère le file_id de la bannière page formules / achat de points (avec cache).
    Utilisée uniquement sur la page de choix de formule ; pas conservée au retour ou à la page suivante.
    """
    global _points_banner_file_id

    if _points_banner_file_id:
        return _points_banner_file_id

    with _points_banner_lock:
        if _points_banner_file_id:
            return _points_banner_file_id

        banner_path = "banniere_point.jpg"
        if not os.path.exists(banner_path):
            logger.warning(f"Bannière points non trouvée: {banner_path}")
            return None

        try:
            message = await _send_photo_for_banner_cache(
                context.bot, banner_path, "Bannière points (upload cache)"
            )
            if message:
                _points_banner_file_id = message.photo[-1].file_id
                logger.info(f"Bannière points uploadée, file_id obtenu (longueur: {len(_points_banner_file_id)})")
                try:
                    await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
                except Exception:
                    pass
                return _points_banner_file_id
            if not ADMIN_ID:
                logger.error("ADMIN_ID non configuré, impossible d'uploader la bannière points")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de l'upload de la bannière points: {e}")
            return None


def require_role_for_callback(role: str, callback_data: str) -> bool:
    """ACL centralisée des callbacks pour réduire les oublis de vérification role == admin."""
    admin_only_exact = {
        "cmd_config",
        "cmd_stat_general",
        "cmd_stock",
        "cmd_user",
        "config_points",
        "config_role",
        "config_payement",
        "config_canal",
        "config_annonce",
        "config_storage",
        "config_arret",
        "emergency_stop_enable",
        "emergency_stop_disable",
        "config_price_edit",
        "config_min_edit",
        "config_max_edit",
        "config_payment_url_edit",
        "config_staff_channel_edit",
        "config_staff_thread_payment_edit",
        "config_staff_thread_entretien_edit",
        "config_staff_thread_demande_access_edit",
    }
    admin_only_prefixes = (
        "payment_accept_",
        "payment_refuse_",
        "demande_accept_",
        "demande_refuse_",
    )

    if callback_data in admin_only_exact or callback_data.startswith(admin_only_prefixes):
        return role == "admin"

    seller_only_exact = {
        "cmd_panel_vendeur",
    }
    if callback_data in seller_only_exact:
        return role == "vendeur"

    return True


def create_back_button(back_to: str = "menu_principal") -> InlineKeyboardMarkup:
    """Crée un bouton retour de manière sécurisée"""
    back_to = sanitize_text(back_to, 50)
    
    if back_to == "shop":
        keyboard = [[InlineKeyboardButton("🔙 Retour au shop", callback_data="cmd_shop")]]
    else:
        keyboard = [[InlineKeyboardButton("🔙 Retour au menu", callback_data="menu_principal")]]
    
    return InlineKeyboardMarkup(keyboard)


async def edit_or_send_message(update: Update, message_text: str, reply_markup: InlineKeyboardMarkup, 
                                parse_mode: str = "HTML", photo_file_id: Optional[str] = None) -> None:
    """
    Fonction helper pour gérer intelligemment l'édition/envoi de messages
    avec support des transitions photo <-> texte et changement de bannière
    """
    try:
        if update.message:
            # Nouveau message
            if photo_file_id:
                await update.message.reply_photo(
                    photo=photo_file_id,
                    caption=message_text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
            else:
                await update.message.reply_text(
                    message_text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
        elif update.callback_query:
            query = update.callback_query
            current_is_photo = query.message.photo is not None
            
            if photo_file_id and current_is_photo:
                # Photo -> Photo : vérifier si c'est la même bannière ou une différente
                current_file_id = None
                if query.message.photo:
                    # Récupérer le file_id de la photo actuelle (la plus grande taille)
                    current_file_id = query.message.photo[-1].file_id
                
                # Si c'est une bannière différente, supprimer et recréer
                if current_file_id != photo_file_id:
                    try:
                        await query.message.delete()
                    except:
                        pass
                    await query.message.reply_photo(
                        photo=photo_file_id,
                        caption=message_text,
                        reply_markup=reply_markup,
                        parse_mode=parse_mode
                    )
                else:
                    # Même bannière : éditer juste la caption
                    await query.edit_message_caption(
                        caption=message_text,
                        reply_markup=reply_markup,
                        parse_mode=parse_mode
                    )
            elif photo_file_id and not current_is_photo:
                # Texte -> Photo : supprimer et recréer
                try:
                    await query.message.delete()
                except:
                    pass
                await query.message.reply_photo(
                    photo=photo_file_id,
                    caption=message_text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
            elif not photo_file_id and current_is_photo:
                # Photo -> Texte : supprimer et recréer
                try:
                    await query.message.delete()
                except:
                    pass
                await query.message.reply_text(
                    message_text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
            else:
                # Texte -> Texte : éditer normalement
                await query.edit_message_text(
                    message_text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
    except TelegramError as e:
        # Si erreur d'édition, essayer de supprimer et recréer
        if update.callback_query:
            query = update.callback_query
            try:
                await query.message.delete()
            except:
                pass
            # Recréer le message
            if photo_file_id:
                await query.message.reply_photo(
                    photo=photo_file_id,
                    caption=message_text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
            else:
                await query.message.reply_text(
                    message_text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
        else:
            raise


async def safe_edit_message_text(query, message_text: str, reply_markup: InlineKeyboardMarkup, parse_mode: str = "HTML") -> None:
    """
    Fonction helper pour éditer un message texte en gérant les transitions depuis une photo
    """
    try:
        # Si le message actuel est une photo, supprimer et recréer en texte
        if query.message.photo:
            try:
                await query.message.delete()
            except:
                pass
            await query.message.reply_text(message_text, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            # Message texte : éditer normalement
            await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode=parse_mode)
    except TelegramError as e:
        # "Message is not modified" : contenu identique, considérer comme succès
        if "message is not modified" in str(e).lower():
            return
        # Si erreur, essayer de supprimer et recréer
        if "no text in the message to edit" in str(e).lower() or "message to edit not found" in str(e).lower():
            try:
                await query.message.delete()
            except:
                pass
            await query.message.reply_text(message_text, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            raise


async def show_shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le menu shop avec les options pour les membres"""
    if not update.effective_user:
        logger.warning("show_shop_menu appelé sans utilisateur valide")
        return
    
    user = update.effective_user
    
    # Construire le message avec le nouveau système esthétique
    header = format_header_rich("BOUTIQUE", "🛒", "orange", banner=False)
    intro_section = format_section_rich(
        "Choisissez une catégorie",
        "",
        "✨",
        "orange",
        highlight=False
    )
    
    shop_message = f"{header}\n\n{intro_section}\n"
    
    # Boutons organisés par catégorie visuelle
    keyboard = [
        # Catégorie ACHATS (orange)
        [
            InlineKeyboardButton("💰 Achat de solde", callback_data="cmd_acheter_points"),
            InlineKeyboardButton("🛒 Boutique", callback_data="cmd_boutique")
        ],
        # Catégorie INFORMATIONS (bleu)
        [
            InlineKeyboardButton("📢 Annonces", callback_data="cmd_annonce"),
            InlineKeyboardButton("👤 Mon Profil", callback_data="cmd_moi")
        ],
        # Navigation (neutre)
        [InlineKeyboardButton("🔙 Menu principal", callback_data="menu_principal")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Essayer d'utiliser la bannière avec fallback texte
    try:
        file_id = await get_or_upload_shop_banner(context)
        
        # Utiliser la fonction helper pour gérer les transitions
        await edit_or_send_message(update, shop_message, reply_markup, "HTML", file_id)
        
        if file_id:
            logger.info(f"Menu shop affiché avec bannière pour l'utilisateur {user.id}")
        else:
            logger.info(f"Menu shop affiché (texte) pour l'utilisateur {user.id}")
        
    except TelegramError as e:
        logger.error(f"Erreur lors de l'affichage du menu shop: {e}")


async def _handle_card_purchase(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    card_points: int,
    points_to_deduct: int,
    back_callback: str,
) -> None:
    """
    Logique interne d'achat de carte KFC.
    card_points = valeur de la carte (pour l'API), points_to_deduct = points débités du solde.
    """
    query = update.callback_query

    if card_points < 50:
        try:
            if query:
                pass
            else:
                await update.message.reply_text("❌ Minimum 50 points requis.", parse_mode="HTML")
        except:
            pass
        return

    balance = get_user_balance(user_id)
    if balance < points_to_deduct:
        try:
            if query:
                # Message temporaire visible dans le chat, supprimé après 3 secondes
                try:
                    tmp_msg = await query.message.reply_text("❌ Solde insuffisant", parse_mode="HTML")
                    chat_id = tmp_msg.chat_id
                    msg_id = tmp_msg.message_id

                    async def _delete_tmp():
                        await asyncio.sleep(3)
                        try:
                            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
                        except Exception:
                            pass

                    asyncio.create_task(_delete_tmp())
                except Exception as e:
                    logger.warning(f"Impossible d'envoyer le message temporaire solde insuffisant: {e}")
            else:
                await update.message.reply_text(
                    f"❌ Solde insuffisant.\n\nVotre solde : 💎 {balance} points\nPoints requis : 💎 {points_to_deduct} points",
                    parse_mode="HTML"
                )
        except:
            pass
        return

    loading_message = "⏳ Recherche d'une carte disponible...\n\nVeuillez patienter."
    message_to_delete = None
    try:
        if query:
            await query.edit_message_text(loading_message, parse_mode="HTML")
        else:
            loading_msg = await update.message.reply_text(loading_message, parse_mode="HTML")
            message_to_delete = loading_msg.message_id
    except:
        pass

    card_data = await generate_kfc_card(card_points)

    if not card_data:
        error_message = (
            f"❌ Aucune carte disponible\n\n"
            f"Malheureusement, aucune carte avec {card_points} points n'est disponible actuellement.\n\n"
            f"💡 Essayez avec un autre nombre de points."
        )
        keyboard = [[InlineKeyboardButton("🔙 Retour à la boutique", callback_data=back_callback)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            if query:
                await query.edit_message_text(error_message, reply_markup=reply_markup, parse_mode="HTML")
            else:
                # Supprimer le message de chargement et envoyer l'erreur
                if message_to_delete:
                    try:
                        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=message_to_delete)
                    except:
                        pass
                await update.message.reply_text(error_message, reply_markup=reply_markup, parse_mode="HTML")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage du message d'erreur: {e}")
        return
    
    if not deduct_user_balance_atomic(user_id, points_to_deduct):
        # Échec de la déduction (solde insuffisant entre temps ou erreur DB)
        logger.error(f"Échec de la déduction de points pour l'utilisateur {user_id} après obtention de la carte")
        
        # IMPORTANT: La carte a été réservée par l'API mais on n'a pas pu déduire les points
        # Dans un système de production, il faudrait annuler la réservation de la carte
        # Pour l'instant, on affiche juste une erreur
        
        error_message = (
            f"❌ Erreur lors de la transaction\n\n"
            f"Une erreur s'est produite lors de la déduction de vos points.\n\n"
            f"Veuillez contacter un administrateur."
        )
        keyboard = [[InlineKeyboardButton("🔙 Retour à la boutique", callback_data=back_callback)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            if query:
                await query.edit_message_text(error_message, reply_markup=reply_markup, parse_mode="HTML")
            else:
                if message_to_delete:
                    try:
                        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=message_to_delete)
                    except:
                        pass
                await update.message.reply_text(error_message, reply_markup=reply_markup, parse_mode="HTML")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage du message d'erreur transaction: {e}")
        return

    # Enregistrer l'achat dans l'historique des cartes (sans QR)
    card_id = card_data.get('id', 'N/A')
    card_number = card_data.get('carte', 'N/A')
    card_points_actual = card_data.get('point', card_points)
    role = get_effective_role(user_id, context)
    is_admin = role == "admin"
    customer_id = card_data.get("customerId")
    record_id = insert_card_purchase_history(
        user_id, str(card_number), int(card_points_actual), customer_id=customer_id
    )
    
    # Succès : afficher les informations de la carte
    
    # Construire le message avec uniquement carte et points (comme demandé)
    success_header = format_header_rich("ACHAT RÉUSSI", "", "success", banner=False)
    
    card_info = (
        f"{success_header}\n\n"
        f"🎴 <b>Carte :</b> <code>{card_number}</code>\n"
        f"💎 <b>Points :</b> {card_points_actual}\n"
    )

    if is_admin and record_id is not None:
        keyboard = [
            [InlineKeyboardButton("📋 Afficher les infos complètes", callback_data=f"card_info_full_{record_id}")],
            [InlineKeyboardButton("🔙 Retour à la boutique", callback_data=back_callback)],
        ]
    else:
        keyboard = [[InlineKeyboardButton("🔙 Retour à la boutique", callback_data=back_callback)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Générer la bannière avec QR code (même logique que creer qr_code.py), sans sauvegarde
    banner_io = generate_card_banner_image(card_number)
    
    try:
        if banner_io:
            # Envoyer la bannière en photo avec le texte en légende
            chat_id: Optional[int] = None
            if query and query.message:
                chat_id = query.message.chat_id
            elif update.message:
                chat_id = update.message.chat_id
            
            if chat_id is not None:
                # Si on vient d'un callback, on peut supprimer le message précédent
                if query and query.message:
                    try:
                        await query.message.delete()
                    except TelegramError:
                        pass
                
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=banner_io,
                    caption=card_info,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                )
                
                # Si on était sur un message "chargement" envoyé par texte, le nettoyer
                if not query and message_to_delete and update.message:
                    try:
                        await context.bot.delete_message(
                            chat_id=update.message.chat_id,
                            message_id=message_to_delete,
                        )
                    except TelegramError:
                        pass
            else:
                # Fallback si on ne trouve pas de chat_id
                if query:
                    await query.edit_message_text(card_info, reply_markup=reply_markup, parse_mode="HTML")
                elif update.message:
                    if message_to_delete:
                        try:
                            await context.bot.delete_message(
                                chat_id=update.message.chat_id,
                                message_id=message_to_delete,
                            )
                        except TelegramError:
                            pass
                    await update.message.reply_text(card_info, reply_markup=reply_markup, parse_mode="HTML")
        else:
            # Fallback : pas d'image, envoi du texte seul (comportement précédent)
            if query:
                await query.edit_message_text(card_info, reply_markup=reply_markup, parse_mode="HTML")
            elif update.message:
                if message_to_delete:
                    try:
                        await context.bot.delete_message(
                            chat_id=update.message.chat_id,
                            message_id=message_to_delete,
                        )
                    except TelegramError:
                        pass
                await update.message.reply_text(card_info, reply_markup=reply_markup, parse_mode="HTML")
        
        logger.info(f"Carte achetée avec succès par l'utilisateur {user_id}: {card_id} ({card_points_actual} pts, débit {points_to_deduct})")
    except TelegramError as e:
        logger.error(f"Erreur lors de l'affichage de la carte: {e}")


async def handle_card_purchase_carte(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, card_points: int
) -> None:
    """Achat Carte : coût = euros_to_points(card_points × get_prix_per_point_carte(card_points))."""
    prix_unitaire = get_prix_per_point_carte(card_points)
    y_euros = card_points * prix_unitaire
    points_to_deduct = euros_to_points(y_euros)
    await _handle_card_purchase(
        update, context, user_id,
        card_points=card_points,
        points_to_deduct=points_to_deduct,
        back_callback="boutique_carte",
    )


BOUTIQUE_POINTS_OPTIONS: Final[tuple[int, ...]] = (600, 800, 1000, 1200, 1500, 1700, 2000, 2300, 2500)

# Limite maximale de points pour un panier Click&Collect (doit rester cohérente avec l'API Flask)
CLICK_COLLECT_MAX_BASKET_POINTS: Final[int] = 2500


async def show_boutique_click_collect_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Affiche le menu Click&Collect : demande ville/nom KFC pour rechercher."""
    query = update.callback_query if update.callback_query else None
    for key in (
        'click_collect_stores', 'click_collect_cities', 'click_collect_selected_city', 'click_collect_stores_filtered',
        'click_collect_preview_menu', 'click_collect_selected_store', 'click_collect_selected_cat', 'click_collect_cart',
        'click_collect_art_idx', 'click_collect_waiting_credentials', 'click_collect_waiting_prenom',
        'click_collect_session_created', 'click_collect_panier_id', 'click_collect_pending_store_idx',
        'click_collect_card_for_token', 'click_collect_prenom',
        'click_collect_modgrps_item', 'click_collect_modgrps_cat_idx', 'click_collect_modgrps_art_idx',
        'click_collect_modgrps_tree', 'click_collect_modgrps_stack', 'click_collect_modgrps_group_idx',
        'click_collect_modgrps_groups', 'click_collect_modgrps_multi', 'click_collect_remove_article',
    ):
        context.user_data.pop(key, None)
    context.user_data['click_collect_city_search'] = True

    header = format_header_rich("CLICK&COLLECT 🛒", "🛒", "orange", banner=False)
    intro_section = format_section_rich(
        "Recherche de restaurant",
        "Entrez une ville ou un nom de KFC pour voir les restaurants disponibles.",
        "📍",
        "orange",
        highlight=False
    )
    if USE_TEST_CLICK_ACCOUNT:
        intro_section += "\n\n<b>[Mode test Click&Collect]</b>\nLes commandes utilisent un compte fidélité de test partagé."
    message = f"{header}\n\n{intro_section}\n"

    keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="cmd_boutique")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if query:
            await safe_edit_message_text(query, message, reply_markup, "HTML")
        else:
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="HTML")
    except TelegramError as e:
        logger.error(f"Erreur lors de l'affichage du menu Click&Collect: {e}")


async def _do_select_store_and_load_menu(
    query,
    context: ContextTypes.DEFAULT_TYPE,
    idx: int,
    user_id: int,
) -> None:
    """
    Sélectionne un KFC (index idx dans stores_filtered), génère un panier_id,
    charge le menu fidélité et affiche les catégories.
    """
    filtered = context.user_data.get('click_collect_stores_filtered', [])
    if idx < 0 or idx >= len(filtered):
        return
    store = filtered[idx]
    name = store.get("name", "?")
    store_id = store.get("id")
    if not store_id:
        return

    panier_id = str(random.randint(100000, 999999))
    context.user_data['click_collect_panier_id'] = panier_id
    context.user_data['click_collect_cart'] = []  # liste de lignes: { id, name, cost, modgrps, quantity }

    await safe_edit_message_text(query, "⏳ Chargement du menu fidélité...", None, "HTML")
    success, menu_data, err_msg = fetch_click_preview_menu(str(store_id))
    if not success:
        header = format_header_rich("ERREUR", "❌", "orange", banner=False)
        keyboard = [[InlineKeyboardButton("🔙 Retour aux restaurants", callback_data="click_collect_back_stores")]]
        await safe_edit_message_text(query, f"{header}\n\n{escape_html(err_msg or 'Erreur inconnue')}", InlineKeyboardMarkup(keyboard), "HTML")
        return

    click_categories = menu_data.get("categories") or {}
    categories = build_click_collect_menu_from_product(click_categories)
    context.user_data['click_collect_preview_menu'] = categories
    context.user_data['click_collect_selected_store'] = store

    cat_names = list(categories.keys())
    if not cat_names:
        header = format_header_rich(name, "🍗", "orange", banner=False)
        msg = "Aucun article fidélité disponible pour ce restaurant."
        keyboard = [[InlineKeyboardButton("🔙 Retour aux restaurants", callback_data="click_collect_back_stores")]]
        await safe_edit_message_text(query, f"{header}\n\n{msg}", InlineKeyboardMarkup(keyboard), "HTML")
        return

    header = format_header_rich(f"Menu — {name}", "🍗", "orange", banner=False)
    keyboard = []
    for i, cat_name in enumerate(cat_names):
        count = len(categories.get(cat_name, []))
        keyboard.append([InlineKeyboardButton(f"📂 {cat_name} ({count})", callback_data=f"click_collect_cat_{i}")])
    keyboard.append([InlineKeyboardButton("🔙 Retour aux restaurants", callback_data="click_collect_back_stores")])
    keyboard.append([InlineKeyboardButton("🧺 Panier", callback_data="click_collect_panier")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit_message_text(query, header, reply_markup, "HTML")


# Prénom Click & Collect : un mot, lettres (accents OK), tiret autorisé, pas d'espaces ni caractères spéciaux
CLICK_COLLECT_PRENOM_REGEX = re.compile(r"^[a-zA-ZÀ-ÿ\-]+$")

# Phase de test Click & Collect :
# on force temporairement l'utilisation d'un compte fidélité fixe pour la session,
# sans appeler recup_token ni consommer les cartes du storage.
# Piloté par la variable d'environnement USE_TEST_CLICK_ACCOUNT (true/false).
USE_TEST_CLICK_ACCOUNT: Final[bool] = os.getenv('USE_TEST_CLICK_ACCOUNT', 'false').lower() == 'true'
TEST_CLICK_ACCOUNT_ID: Final[str] = os.getenv('CLICK_TEST_ACCOUNT_ID', 'c1f3eda7-63cd-47d0-be9d-c3934fcc9b7a')
TEST_CLICK_ACCOUNT_TOKEN: Final[str] = os.getenv('CLICK_TEST_ACCOUNT_TOKEN', '')


async def _do_recup_token_and_session(
    query_or_none,
    update_or_none,
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    card: Dict[str, Any],
    prenom: str,
) -> None:
    """
    Appelle recup_token avec la carte et le prénom utilisateur.
    Si succès : crée la session Flask, ajoute les articles, puis checkout+submit automatiquement.
    Si erreur : affiche message d'erreur avec Réessayer (même carte) / Retour au panier.
    """
    panier_id = context.user_data.get('click_collect_panier_id')
    store = context.user_data.get('click_collect_selected_store', {})
    cart = context.user_data.get('click_collect_cart', [])
    cart_list = cart if isinstance(cart, list) else list((cart or {}).values())
    store_id = store.get("id")
    store_name = store.get("name")
    store_city = store.get("city")
    if not panier_id or not store_id or not cart_list:
        err_header = format_header_rich("ERREUR", "❌", "orange", banner=False)
        keyboard = [[InlineKeyboardButton("🔙 Retour au panier", callback_data="click_collect_panier")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = "Panier ou restaurant invalide."
        if query_or_none:
            await safe_edit_message_text(query_or_none, f"{err_header}\n\n{escape_html(msg)}", reply_markup, "HTML")
        elif update_or_none and update_or_none.message:
            await update_or_none.message.reply_text(f"{err_header}\n\n{escape_html(msg)}", reply_markup=reply_markup, parse_mode="HTML")
        return

    idd = card.get("id") or card.get("customerId") or card.get("customer_id") or ""
    carte = card.get("carte") or ""
    nom = card.get("nom") or ""
    email = card.get("email") or ""
    numero = card.get("numero") or ""
    ddb = card.get("ddb") or ""

    if USE_TEST_CLICK_ACCOUNT:
        # Phase de test : on bypasse recup_token et on utilise un compte fixe
        account_id, token = TEST_CLICK_ACCOUNT_ID, TEST_CLICK_ACCOUNT_TOKEN
        if query_or_none:
            try:
                await query_or_none.answer()
            except TelegramError:
                pass
            await safe_edit_message_text(
                query_or_none,
                "⏳ Création de la session et ajout des articles (compte test)...",
                None,
                "HTML",
            )
    else:
        if query_or_none:
            try:
                await query_or_none.answer()
            except TelegramError:
                pass
            await safe_edit_message_text(query_or_none, "⏳ Récupération du token en cours...", None, "HTML")

        result = await recup_token_async(
            id=str(idd),
            carte=str(carte),
            prenom=prenom,
            nom=str(nom),
            email=str(email),
            numero=str(numero),
            ddb=str(ddb),
        )

        if result[0] != "success":
            _, err_code, err_msg = result
            context.user_data['click_collect_card_for_token'] = card
            context.user_data['click_collect_prenom'] = prenom
            err_header = format_header_rich("ERREUR TOKEN", "❌", "orange", banner=False)
            msg = f"{escape_html(err_msg or err_code or 'Erreur inconnue')}\n\nVous pouvez réessayer avec la même carte ou revenir au panier."
            keyboard = [
                [InlineKeyboardButton("🔄 Réessayer", callback_data="click_collect_retry_token")],
                [InlineKeyboardButton("🔙 Retour au panier", callback_data="click_collect_panier")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if query_or_none:
                await safe_edit_message_text(query_or_none, f"{err_header}\n\n{msg}", reply_markup, "HTML")
            elif update_or_none and update_or_none.message:
                await update_or_none.message.reply_text(f"{err_header}\n\n{msg}", reply_markup=reply_markup, parse_mode="HTML")
            return

        account_id, token = result[1], result[2]

    if query_or_none:
        await safe_edit_message_text(query_or_none, "⏳ Création de la session et ajout des articles...", None, "HTML")

    success, session_data, err_msg = fetch_click_create_session(
        panier_id=str(panier_id),
        account_id=account_id,
        account_token=token,
        store_id=str(store_id),
        store_name=store_name,
        store_city=store_city,
        telegram_id=str(user_id),
    )
    if not success:
        err_header = format_header_rich("ERREUR SESSION", "❌", "orange", banner=False)
        keyboard = [[InlineKeyboardButton("🔙 Retour au panier", callback_data="click_collect_panier")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if query_or_none:
            await safe_edit_message_text(query_or_none, f"{err_header}\n\n{escape_html(err_msg or 'Erreur inconnue')}", reply_markup, "HTML")
        elif update_or_none and update_or_none.message:
            await update_or_none.message.reply_text(f"{err_header}\n\n{escape_html(err_msg or 'Erreur inconnue')}", reply_markup=reply_markup, parse_mode="HTML")
        return

    add_errors = []
    for entry in cart_list:
        ok, add_err = fetch_click_add_basket_item(
            panier_id=str(panier_id),
            loyalty_id=entry.get("id", ""),
            cost=entry.get("cost", 0),
            quantity=entry.get("quantity", 1),
            name=entry.get("name"),
            modgrps=entry.get("modgrps"),
        )
        if not ok:
            add_errors.append(f"{entry.get('name', '?')}: {add_err}")

    context.user_data['click_collect_session_created'] = True
    context.user_data.pop('click_collect_card_for_token', None)
    context.user_data.pop('click_collect_prenom', None)

    # Plus d'étape intermédiaire "Valider mon achat":
    # on enchaîne directement checkout + submit après saisie du prénom.
    if query_or_none:
        await safe_edit_message_text(query_or_none, "⏳ Validation en cours (checkout + soumission)...", None, "HTML")

    ok_checkout, err_checkout = fetch_click_checkout(str(panier_id))
    if not ok_checkout:
        header = format_header_rich("ERREUR CHECKOUT", "❌", "orange", banner=False)
        keyboard = [
            [InlineKeyboardButton("🔙 Retour au panier", callback_data="click_collect_panier")],
            [InlineKeyboardButton("🏠 Accueil", callback_data="cmd_shop")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if query_or_none:
            await safe_edit_message_text(query_or_none, f"{header}\n\n{escape_html(err_checkout or 'Erreur inconnue')}", reply_markup, "HTML")
        elif update_or_none and update_or_none.message:
            await update_or_none.message.reply_text(f"{header}\n\n{escape_html(err_checkout or 'Erreur inconnue')}", reply_markup=reply_markup, parse_mode="HTML")
        return

    ok_submit, data_submit, err_submit = fetch_click_submit(str(panier_id))
    if not ok_submit:
        header = format_header_rich("ERREUR SOUMISSION", "❌", "orange", banner=False)
        keyboard = [
            [InlineKeyboardButton("🔙 Retour au panier", callback_data="click_collect_panier")],
            [InlineKeyboardButton("🏠 Accueil", callback_data="cmd_shop")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if query_or_none:
            await safe_edit_message_text(query_or_none, f"{header}\n\n{escape_html(err_submit or 'Erreur inconnue')}", reply_markup, "HTML")
        elif update_or_none and update_or_none.message:
            await update_or_none.message.reply_text(f"{header}\n\n{escape_html(err_submit or 'Erreur inconnue')}", reply_markup=reply_markup, parse_mode="HTML")
        return

    # Débit local du solde utilisateur (argent consommé par le panier)
    try:
        total_argent = 0.0
        for e in cart_list:
            raw_price = e.get("price", get_product_price(str(e.get("id", ""))))
            try:
                unit_price = float(raw_price)
            except (TypeError, ValueError):
                unit_price = 0.0
            try:
                qty = int(e.get("quantity", 1))
            except (TypeError, ValueError):
                qty = 1
            total_argent += unit_price * max(1, qty)
        if total_argent > 0:
            debit_amount = total_argent
            ok_debit = update_user_points(user_id, -debit_amount)
            if not ok_debit:
                logger.warning(
                    f"Échec du débit local de {debit_amount} argent pour l'utilisateur {user_id} "
                    f"après submit Click&Collect (panier_id={panier_id})"
                )
    except Exception as e:
        logger.error(
            f"Exception lors du débit local de l'argent pour l'utilisateur {user_id} "
            f"après submit Click&Collect (panier_id={panier_id}): {e}"
        )

    role_for_submit = get_effective_role(user_id, context)
    conf_url = (data_submit or {}).get("confirmation_url") if data_submit else None
    first_name = (data_submit or {}).get("first_name") if data_submit else None
    last_name = (data_submit or {}).get("last_name") if data_submit else None
    order_number = (data_submit or {}).get("order_number") if data_submit else None
    phone_number = (data_submit or {}).get("phone_number") if data_submit else None
    selected_store = context.user_data.get("click_collect_selected_store") or {}
    store_name = (data_submit or {}).get("store_name") if data_submit else None
    store_city = (data_submit or {}).get("store_city") if data_submit else None
    if not store_name:
        store_name = selected_store.get("name")
    if not store_city:
        store_city = selected_store.get("city")
    first_name_display = escape_html(str(first_name)) if first_name else "—"
    last_name_display = escape_html(str(last_name)) if last_name else "—"
    order_number_display = escape_html(str(order_number)) if order_number else "—"
    phone_masked = escape_html(mask_phone_for_click_display(phone_number))
    store_name_display = escape_html(str(store_name)) if store_name else "—"
    store_city_display = escape_html(str(store_city)) if store_city else "—"
    context.user_data["click_collect_last_submit_info"] = data_submit
    header = format_header_rich("COMMANDE TERMINÉE", "✅", "success", banner=False)
    msg = (
        f"\n"
        f" N° commande : {order_number_display}\n"
        f"👤 Nom : {first_name_display} {last_name_display}\n"
        f"📱 Téléphone : {phone_masked}\n\n"
        f"🍗 KFC : {store_name_display}\n"
        f"📍 Ville : {store_city_display}\n\n"
        f"🔗 Commande :\n{escape_html(conf_url or '—')}"
    )
    if add_errors:
        msg += "\n\n⚠️ Erreurs lors de l'ajout de certains articles : " + ", ".join(add_errors[:3])
    keyboard = [
        [InlineKeyboardButton("⏱ Lancer la préparation (3min)", callback_data="click_collect_3min")],
        [InlineKeyboardButton("🏠 Accueil", callback_data="cmd_shop")],
    ]
    if role_for_submit == "admin":
        keyboard.insert(1, [InlineKeyboardButton("📋 Voir toutes les infos", callback_data="click_collect_show_submit_info")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    if query_or_none:
        await safe_edit_message_text(query_or_none, f"{header}\n\n{msg}", reply_markup, "HTML")
    elif update_or_none and update_or_none.message:
        await update_or_none.message.reply_text(f"{header}\n\n{msg}", reply_markup=reply_markup, parse_mode="HTML")


async def show_boutique_carte_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Affiche le menu boutique Carte avec tarification réduite (table CARTE_PRICE_TABLE)."""
    query = update.callback_query if update.callback_query else None
    balance = get_user_balance(user_id)

    header = format_header_rich("SHOP CARTE 📷", "📷", "orange", banner=False)
    balance_section = format_highlight_box(f"Votre solde : {balance}", "💎", "gold")

    prix_example = get_prix_per_point_carte(2500)
    y_example = 2500 * prix_example
    pts_example = euros_to_points(y_example)
    intro_lines = [
        "Avec la table de prix carte, une carte ne vous coûte pas sa valeur en points.",
        "Exemple : une carte de 2500 pts = {:.2f} € équivalent → vous payez seulement {} pts sur votre solde.",
        "",
        "Choisissez la carte souhaitée :"
    ]
    intro_text = "\n".join(intro_lines).format(y_example, pts_example)
    intro_section = format_section_rich("Tarification spéciale", intro_text, "✨", "orange", highlight=False)

    message = f"{header}\n\n{balance_section}\n\n{intro_section}\n"

    keyboard = []
    for pts in BOUTIQUE_POINTS_OPTIONS:
        prix_unitaire = get_prix_per_point_carte(pts)
        y = pts * prix_unitaire
        pts_cost = euros_to_points(y)
        label = f"💰 {pts} pts → {pts_cost} pts" if pts_cost != pts else f"💰 {pts} points"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"boutique_carte_points_{pts}")])
    keyboard += [
        [InlineKeyboardButton("✏️ Saisie manuelle", callback_data="boutique_carte_custom")],
        [InlineKeyboardButton("🔙 Retour", callback_data="cmd_boutique")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if query:
            await safe_edit_message_text(query, message, reply_markup, "HTML")
        else:
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="HTML")
    except TelegramError as e:
        logger.error(f"Erreur lors de l'affichage du menu Carte: {e}")


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le menu principal selon le rôle effectif de l'utilisateur (admin peut être en mode user)."""
    if not update.effective_user:
        logger.warning("show_main_menu appelé sans utilisateur valide")
        return
    
    user = update.effective_user
    user_id = user.id
    role = get_effective_role(user_id, context)
    
    # Sanitisation du prénom avec HTML
    first_name = escape_html(sanitize_text(user.first_name, 64)) if user.first_name else "Utilisateur"
    
    # Construire le message avec le nouveau système esthétique
    header = format_header_rich("BOT KFC", "🍗", "orange", banner=False)
    
    # Section de bienvenue mise en évidence
    welcome_section = format_section_rich(
        f"Bienvenue, {first_name} !",
        "Sélectionnez une action ci-dessous",
        "👋",
        "gold",
        highlight=True
    )
    
    welcome_message = f"{header}\n\n{welcome_section}\n"
    
    keyboard = []
    
    if role == "admin":
        # Boutons organisés par catégorie visuelle
        keyboard = [
            # Catégorie principale - SHOP (orange)
            [InlineKeyboardButton("🛒 Shop", callback_data="cmd_shop")],
            [InlineKeyboardButton("🆕 Créer un compte", callback_data="admin_create_account")],
            # Catégorie Admin - GESTION (bleu)
            [
                InlineKeyboardButton("⚙️ Config", callback_data="cmd_config"),
                InlineKeyboardButton("📊 Statistiques", callback_data="cmd_stat_general")
            ],
            [
                InlineKeyboardButton("📦 Stock", callback_data="cmd_stock"),
                InlineKeyboardButton("👥 Utilisateurs", callback_data="cmd_user")
            ]
        ]
    elif role == "vendeur":
        keyboard = [
            [InlineKeyboardButton("🛒 Shop", callback_data="cmd_shop")],
            [InlineKeyboardButton("💼 Panel vendeur", callback_data="cmd_panel_vendeur")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🛒 Shop", callback_data="cmd_shop")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if update.message:
            await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="HTML")
        elif update.callback_query:
            await safe_edit_message_text(update.callback_query, welcome_message, reply_markup, "HTML")
        
        logger.info(f"Menu principal affiché pour l'utilisateur {user_id} (rôle: {role})")
    except TelegramError as e:
        logger.error(f"Erreur lors de l'affichage du menu principal: {e}")


async def show_points_formula_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le choix de formule (solo, duo, etc.) avant l'interface +/- d'achat de points."""
    if not update.effective_user:
        logger.warning("show_points_formula_choice appelé sans utilisateur valide")
        return

    header = format_header_rich("AJOUTER DU SOLDE 💰", "💰", "orange", banner=False)
    intro = format_section_rich(
        "Choisissez une formule",
        "Sélectionnez le type d'achat pour partir avec une quantité d'argent adaptée. Vous pourrez ensuite ajuster !",
        "✨",
        "orange"
    )
    message = f"{header}\n\n{intro}"

    keyboard = [
        [InlineKeyboardButton(f"Solo — {POINTS_FORMULA_DEFAULTS['solo']}€", callback_data="points_formula_solo")],
        [InlineKeyboardButton(f"Duo — {POINTS_FORMULA_DEFAULTS['duo']}€", callback_data="points_formula_duo")],
        [InlineKeyboardButton(f"Petit groupe — {POINTS_FORMULA_DEFAULTS['petit_groupe']}€", callback_data="points_formula_petit_groupe")],
        [InlineKeyboardButton(f"Gros groupe — {POINTS_FORMULA_DEFAULTS['gros_groupe']}€", callback_data="points_formula_gros_groupe")],
        [InlineKeyboardButton(f"Revendeur — {POINTS_FORMULA_DEFAULTS['revendeur']}€", callback_data="points_formula_revendeur")],
        [InlineKeyboardButton("🔙 Retour au shop", callback_data="cmd_shop")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        file_id = await get_or_upload_points_banner(context)
        await edit_or_send_message(update, message, reply_markup, "HTML", file_id)
    except TelegramError as e:
        if "message is not modified" not in str(e).lower():
            logger.error(f"Erreur lors de l'affichage du choix de formule: {e}")


async def show_points_purchase_interface(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_points: int = None) -> None:
    """Affiche l'interface d'achat de points avec les boutons +/-"""
    if not update.effective_user:
        logger.warning("show_points_purchase_interface appelé sans utilisateur valide")
        return
    
    user_id = update.effective_user.id
    
    # Utiliser les valeurs de configuration
    point_min = get_point_min()
    point_max = get_point_max()
    
    # Initialiser avec le minimum si non spécifié
    if selected_points is None:
        selected_points = point_min
    
    # Limiter aux bornes
    selected_points = max(point_min, min(point_max, selected_points))
    
    # Nouvelle logique simplifiée: 1€ payé = 1 argent crédité.
    user_reduction = 0.0
    price_initial = float(selected_points)
    price_euros = float(selected_points)
    
    # Construire le message avec le nouveau système esthétique
    header = format_header_rich("AJOUTER DU SOLDE 💰", "💰", "orange", banner=False)
    
    # Section sélection mise en évidence
    selection_box = format_section_rich(
        "RESUMER",
        "",
        "",
        "info"
    )
    
    # Section prix mise en évidence
    price_box = f"<b>- Total : </b>{price_euros:.2f} €"
    reduction_info = ""
    
    # Informations en section normale
    info_text = (
        "💡 Rappel : <b>1€ payé = 1€ de solde utilisable dans le shop !</b>.\n\n"
        "<i>Utilisez les boutons ci-dessous pour ajuster</i>"
    )
    info_section = format_section_rich(
        "Informations",
        info_text,
        "ℹ️",
        "info"
    )
    
    message = f"{header}\n\n{selection_box}\n- <b>{selected_points}€ </b>\n{price_box}{reduction_info}\n\n{info_section}"
    
    # Boutons organisés visuellement
    keyboard = [
        [
            InlineKeyboardButton(f"➖ -{POINT_INCREMENT}", callback_data=f"points_dec_{selected_points}"),
            InlineKeyboardButton(f"➕ +{POINT_INCREMENT}", callback_data=f"points_inc_{selected_points}")
        ],
        [InlineKeyboardButton("✅ Valider l'achat", callback_data=f"points_validate_{selected_points}")],
        [
            InlineKeyboardButton("🔙 Autre formule", callback_data="points_formula_choice"),
            InlineKeyboardButton("🔙 Retour au shop", callback_data="cmd_shop")
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        file_id = await get_or_upload_points_banner(context)
        await edit_or_send_message(update, message, reply_markup, "HTML", file_id)
        logger.info(f"Interface d'achat d'argent affichée pour l'utilisateur {user_id} ({selected_points} argent)")
    except TelegramError as e:
        # Gérer silencieusement MessageNotModified (clic trop rapide)
        if "message is not modified" not in str(e).lower():
            logger.error(f"Erreur lors de l'affichage de l'interface d'achat: {e}")


async def get_chat_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande pour récupérer l'ID du chat/groupe (utile pour configurer le canal staff)"""
    if not update.message or not update.effective_chat:
        return
    
    user = update.effective_user
    if not user:
        return
    
    role = get_user_role(user.id)
    if role != "admin":
        await update.message.reply_text("❌ Cette commande est réservée aux administrateurs.")
        return
    
    chat = update.effective_chat
    chat_id = chat.id
    chat_type = chat.type
    
    message = (
        f"📊 **Informations du Chat**\n\n"
        f"Type: `{chat_type}`\n"
        f"ID du Chat: `{chat_id}`\n"
        f"Titre: {chat.title or 'N/A'}\n\n"
        f"Pour configurer le canal staff, utilisez cet ID:\n`{chat_id}`"
    )
    
    await update.message.reply_text(message, parse_mode="Markdown")


async def version_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche la version de l'application et l'état du mode test."""
    if not update.message:
        return
    mode_test = "actif" if USE_TEST_CLICK_ACCOUNT else "désactivé"
    txt = (
        f"🧾 <b>Version du bot</b>\n\n"
        f"• Version : <b>{escape_html(APP_VERSION)}</b>\n"
        f"• Mode test Click&Collect : <b>{mode_test}</b>\n"
    )
    try:
        await update.message.reply_text(txt, parse_mode="HTML")
    except TelegramError:
        pass


async def _show_demande_access_page(update: Update, user_id: int, user) -> None:
    """
    Affiche la page "demande d'accès" pour un utilisateur non présent dans la table users.
    Cas 1 : pas de ligne ou (demande_en_attente=false et accepte=false) → bouton "Envoyer ma demande"
    Cas 2 : demande_en_attente=true → "Demande en attente" (pas de bouton)
    Cas 3 : accepte=true → pas de bouton (déjà accepté, message informatif)
    """
    row = get_nouveau_user(user_id)
    demande_en_attente = row[1] if row else False
    accepte = row[3] if row else False

    header = format_header_rich("BOT KFC", "🍗", "orange", banner=False)
    msg_base = (
        f"{header}\n\n"
        "Veuillez demander l'accès au bot à un administrateur."
    )
    keyboard = []
    if demande_en_attente:
        msg = msg_base + "\n\n⏳ <b>Demande en attente.</b>"
    elif accepte:
        msg = msg_base + "\n\n✅ Vous avez déjà été accepté. Utilisez /start pour accéder au bot."
    else:
        msg = msg_base
        keyboard = [[InlineKeyboardButton("📩 Envoyer ma demande", callback_data="demande_access_send")]]

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    try:
        if update.message:
            if reply_markup:
                await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode="HTML")
            else:
                await update.message.reply_text(msg, parse_mode="HTML")
    except TelegramError as e:
        logger.error(f"Erreur envoi page demande accès: {e}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gère la commande /start"""
    if not update.message or not update.effective_user:
        logger.warning("start_command appelé sans message ou utilisateur valide")
        return
    
    user = update.effective_user
    user_id = user.id
    role = get_user_role(user_id)
    
    # Vérifier l'arrêt d'urgence (sauf pour les admins qui peuvent accéder à la config)
    if is_emergency_stop_active() and role != "admin":
        try:
            await update.message.reply_text(
                "⚠️ Le bot est momentanément indisponible, veuillez patienter pour l'instant."
            )
        except TelegramError:
            pass
        return
    
    # NETTOYER les états potentiellement bloqués pour éviter les erreurs
    context.user_data.pop(f'waiting_payment_{user_id}', None)
    context.user_data.pop(f'pending_payment_{user_id}', None)
    context.user_data.pop(f'summary_message_id_{user_id}', None)
    context.user_data.pop('config_edit', None)
    
    # Accès privé : si l'utilisateur n'est pas dans la table users, afficher la page "demande d'accès"
    if not user_exists_in_users(user_id):
        await _show_demande_access_page(update, user_id, user)
        return
    
    # Créer ou récupérer l'utilisateur dans la base de données
    username = user.username if user.username else None
    balance, is_new = get_or_create_user(user_id, username)

    # Si c'est un membre normal, afficher message de bienvenu et rediriger vers shop
    if role == "user":
        first_name = escape_html(sanitize_text(user.first_name, 64)) if user.first_name else "Utilisateur"
        
        # Construire le message avec le nouveau système esthétique
        header = format_header_rich("BOT KFC", "🍗", "orange", banner=False)
        welcome_section = format_section_rich(
            f"Salut {first_name} !",
            "Bienvenue sur le bot KFC.",
            "👋",
            "gold",
            highlight=True
        )
        footer = "\n✨ Accédez au shop pour découvrir toutes nos fonctionnalités !"
        if USE_TEST_CLICK_ACCOUNT:
            footer += "\n\n<b>[Mode test Click&Collect]</b> – les commandes Click&Collect utilisent un compte fidélité de test."
        
        welcome_message = f"{header}\n\n{welcome_section}\n\n{footer}"
        keyboard = [[InlineKeyboardButton("🛒 Accéder au Shop", callback_data="cmd_shop")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="HTML")
            logger.info(f"Message de bienvenu affiché pour le membre {user.id}, redirection vers shop")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'envoi du message de bienvenu: {e}")
    elif role == "admin":
        # Admin : proposer le choix Admin (avec privilèges) ou User (sans privilèges)
        first_name = escape_html(sanitize_text(user.first_name, 64)) if user.first_name else "Admin"
        header = format_header_rich("BOT KFC", "🍗", "orange", banner=False)

        msg = f"{header}\n\nChoix du rôle :"
        keyboard = [
            [InlineKeyboardButton("⚙️ Admin", callback_data="start_as_admin")],
            [InlineKeyboardButton("👤 User", callback_data="start_as_user")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode="HTML")
        except TelegramError as e:
            logger.error(f"Erreur envoi choix Admin/User: {e}")
    else:
        # Vendeur (ou autre) : menu principal
        await show_main_menu(update, context)


def get_command_message(callback_data: str, user_id: int, user_first_name: Optional[str]) -> tuple[str, str]:
    """Retourne le message et le type de retour pour une commande donnée"""
    first_name = sanitize_text(user_first_name, 64) if user_first_name else "N/A"
    
    commands = {
        "cmd_stat_general": ("📊 **Statistiques générales**\n\nVoici les statistiques générales du système.", "menu"),
        "cmd_stock": ("📦 **Gestion du Stock**\n\nGérez l'inventaire des produits.", "menu"),
        "cmd_user": ("👥 **Gestion des Utilisateurs**\n\nGérez les utilisateurs du système.", "menu"),
        "cmd_panel_vendeur": ("💼 **Panel Vendeur**\n\nBienvenue dans votre espace vendeur.", "menu"),
        "cmd_annonce": ("📢 **Annonces**\n\nConsultez les dernières annonces.", "shop"),
    }
    
    return commands.get(callback_data, ("❌ Commande non reconnue.", "menu"))


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gère les callbacks des boutons inline avec validation et sécurité"""
    if not update.callback_query:
        logger.warning("button_callback appelé sans callback_query")
        return
    
    query = update.callback_query
    callback_data = query.data

    # Ne pas répondre tout de suite pour le flux Click & Collect : les handlers peuvent
    # afficher des alertes (catégorie vide, KFC non sélectionné, panier vide, etc.).
    # Une seule answer() autorisée par callback Telegram.
    if not (callback_data.startswith("click_collect_") or callback_data == "boutique_click_collect"):
        try:
            await query.answer()
        except TelegramError as e:
            logger.error(f"Erreur lors de l'answer du callback: {e}")
            return

    if not update.effective_user:
        logger.warning("button_callback appelé sans utilisateur valide")
        return
    
    user = update.effective_user
    user_id = user.id
    role = get_user_role(user_id)
    callback_data = query.data

    # Mettre à jour le username de l'utilisateur à chaque interaction (pour avoir les pseudos à jour dans la liste)
    if user.username:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET username = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
                    (user.username, user_id)
                )
        except psycopg2.Error as e:
            logger.debug(f"Erreur lors de la mise à jour du username pour {user_id}: {e}")
    
    # Vérifier l'arrêt d'urgence (sauf pour les admins qui peuvent accéder à la config pour désactiver)
    if is_emergency_stop_active():
        # Permettre uniquement aux admins d'accéder à cmd_config et config_arret pour désactiver l'arrêt
        if role != "admin" or callback_data not in {"cmd_config", "config_arret", "emergency_stop_disable"}:
            try:
                await query.edit_message_text(
                    "⚠️ Le bot est momentanément indisponible, veuillez patienter pour l'instant."
                )
            except TelegramError:
                pass
            return
    
    # Validation du callback_data
    if not validate_callback_data(callback_data):
        logger.warning(f"Callback invalide reçu de l'utilisateur {user_id}: {callback_data}")
        try:
            await query.edit_message_text(
                "❌ Action non autorisée. Veuillez utiliser les boutons du menu.",
                reply_markup=create_back_button()
            )
        except TelegramError:
            pass  # Message peut être déjà modifié
        return

    # Choix Admin / User (uniquement pour les vrais admins, avant ACL)
    if callback_data in ("start_as_admin", "start_as_user") and role == "admin":
        if callback_data == "start_as_admin":
            context.user_data["view_as_user"] = False
        else:
            context.user_data["view_as_user"] = True
            # Nettoyer les modes admin pour repartir propre en mode user
            for key in ("config_edit", "config_announcement_edit", "admin_create_account_mode",
                        "user_info_mode", "reduction_edit_mode",
                        "vendeur_reduction_mode", "role_add_mode",
                        "role_remove_mode", "storage_mode"):
                context.user_data.pop(key, None)
        await show_main_menu(update, context)
        try:
            await query.answer()
        except TelegramError:
            pass
        return

    # Rôle effectif (admin peut agir en "user" sans privilèges)
    role = get_effective_role(user_id, context)

    # ACL centralisée (réduit le risque d'une branche oubliant role == admin)
    if not require_role_for_callback(role, callback_data):
        try:
            await query.edit_message_text(
                "❌ Accès refusé.",
                reply_markup=create_back_button()
            )
        except TelegramError:
            pass
        logger.warning(f"ACL refusée: user={user_id}, role={role}, cb={callback_data}")
        return
    
    # Gestion des retours au menu
    if callback_data == "menu_principal" or callback_data == "cmd_start":
        context.user_data.pop(f'boutique_custom_{user_id}', None)
        await show_main_menu(update, context)
        return
    
    if callback_data == "cmd_shop":
        context.user_data.pop(f'boutique_custom_{user_id}', None)
        await show_shop_menu(update, context)
        return

    # Demande d'accès au bot (utilisateur non encore dans la table users)
    if callback_data == "demande_access_send":
        if user_exists_in_users(user_id):
            await show_main_menu(update, context)
            return
        username = user.username if user.username else None
        if not create_or_update_demande_access(user_id, username):
            try:
                await query.edit_message_text("❌ Erreur lors de l'envoi de la demande.")
            except TelegramError:
                pass
            return
        thread_id = get_staff_thread_demande_access()
        row = get_nouveau_user(user_id)
        nb = row[2] if row else 1
        first_name = escape_html((user.first_name or "N/A")[:64])
        uname_str = f"@{escape_html(username)}" if username else "—"
        staff_msg = (
            "🔐 <b>Demande d'accès au bot</b>\n\n"
            f"👤 User ID: <code>{user_id}</code>\n"
            f"📱 Username: {uname_str}\n"
            f"📛 Prénom: {first_name}\n"
            f"📊 Tentative n°{nb}"
        )
        keyboard = [
            [
                InlineKeyboardButton("✅ Accepter", callback_data=f"demande_accept_{user_id}"),
                InlineKeyboardButton("❌ Refuser", callback_data=f"demande_refuse_{user_id}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await send_to_staff_channel(context.bot, staff_msg, thread_id=thread_id, reply_markup=reply_markup, parse_mode="HTML")
        try:
            await query.edit_message_text(
                "✅ Votre demande a été envoyée. Un administrateur vous répondra sous peu.",
                parse_mode="HTML"
            )
        except TelegramError:
            pass
        logger.info(f"Demande d'accès envoyée par user_id={user_id} vers thread={thread_id}")
        return

    # Gestion du stock (affichage des statistiques)
    if callback_data == "cmd_stock" and role == "admin":
        # Récupérer les statistiques des cartes (avec gestion d'erreur robuste)
        stats_section = ""
        try:
            logger.info("Tentative de récupération des statistiques KFC pour cmd_stock...")
            cards_count, avg_points = get_kfc_cards_statistics()
            logger.info(f"Statistiques récupérées: count={cards_count}, avg={avg_points}")
            
            if cards_count is not None and avg_points is not None:
                stats_section = (
                    f"📊 **Statistiques du stock:**\n"
                    f"🎴 Cartes disponibles: **{cards_count}**\n"
                    f"📈 Moyenne des points: **{avg_points:.1f}**\n\n"
                )
            else:
                stats_section = "⚠️ Impossible de récupérer les statistiques du stock.\n\n"
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}", exc_info=True)
            stats_section = "⚠️ Erreur lors de la récupération des statistiques.\n\n"
        
        message = (
            "📦 **Gestion du Stock**\n\n"
            + stats_section +
            "Gérez l'inventaire des produits."
        )
        
        keyboard = create_back_button("menu")
        
        try:
            await safe_edit_message_text(
                query,
                message,
                keyboard,
                "Markdown"
            )
            logger.info(f"Callback 'cmd_stock' exécuté par l'utilisateur {user_id} (rôle: {role})")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage du menu stock: {e}")
        return
    
    # Gestion de la boutique — écran intermédiaire "Choisissez votre shop"
    if callback_data == "cmd_boutique":
        context.user_data.pop(f'boutique_custom_{user_id}', None)
        context.user_data.pop('click_collect_city_search', None)
        header = format_header_rich("BOUTIQUE", "🛒", "orange", banner=False)
        msg = f"{header}\n\nChoisissez votre shop :"
        keyboard = [
            [InlineKeyboardButton("🛒 Click&Collect", callback_data="boutique_click_collect")],
            [InlineKeyboardButton("📷 Carte | indisponible", callback_data="boutique_carte")],
            [InlineKeyboardButton("🔙 Retour", callback_data="cmd_shop")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await safe_edit_message_text(query, msg, reply_markup, "HTML")
        except TelegramError as e:
            logger.error(f"Erreur affichage choix shop: {e}")
        return

    if callback_data == "boutique_click_collect":
        await show_boutique_click_collect_menu(update, context, user_id)
        try:
            await query.answer()
        except TelegramError:
            pass
        return

    if callback_data == "boutique_carte":
        # Carte temporairement indisponible : no-op volontaire
        return

    if callback_data.startswith("boutique_carte_points_"):
        try:
            points = int(callback_data.split("_")[-1])
            await handle_card_purchase_carte(update, context, user_id, points)
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur lors de la récupération des points depuis callback: {e}")
        return

    if callback_data == "boutique_carte_custom":
        context.user_data[f'boutique_custom_{user_id}'] = 'carte'
        header = format_header_rich("SAISIE MANUELLE", "✏️", "orange", banner=False)
        message = f"{header}\n\n📝 Entrez le nombre de points souhaité (minimum 50) :"
        keyboard = [[InlineKeyboardButton("❌ Annuler", callback_data="boutique_carte")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await safe_edit_message_text(query, message, reply_markup, "HTML")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de la saisie manuelle: {e}")
        return

    def _cart_lines():
        """Retourne la liste des lignes du panier (toujours une liste)."""
        cart = context.user_data.get('click_collect_cart', None)
        if cart is None:
            return []
        return list(cart) if isinstance(cart, list) else list((cart or {}).values())

    def _cart_total_argent(cart_list: list) -> float:
        """Total utilisateur (argent) calculé depuis le champ price des lignes panier."""
        total = 0.0
        for e in cart_list or []:
            raw_price = e.get("price")
            if raw_price is None:
                raw_price = get_product_price(str(e.get("id", "")))
            try:
                unit_price = float(raw_price)
            except (TypeError, ValueError):
                unit_price = 0.0
            try:
                qty = int(e.get("quantity", 1))
            except (TypeError, ValueError):
                qty = 1
            total += unit_price * max(1, qty)
        return total

    def _render_article_page(cat_idx: int, art_idx: int):
        """Affiche l'écran article paginé (cat_idx, art_idx). Retourne (header, msg, reply_markup) ou None."""
        menu = context.user_data.get('click_collect_preview_menu', {})
        cat_names = list(menu.keys())
        if cat_idx < 0 or cat_idx >= len(cat_names):
            return None
        items = menu.get(cat_names[cat_idx], [])
        if art_idx < 0 or art_idx >= len(items):
            return None
        item = items[art_idx]
        loyalty_id = str(item.get("id", ""))
        product_data = PRODUCT.get(loyalty_id) or {}
        cart_list = _cart_lines()
        qty = sum(e.get("quantity", 1) for e in cart_list if str(e.get("id", "")) == loyalty_id)
        display_name = sanitize_display_name(product_data.get("name", "Produit inconnu"))
        display_price = product_data.get("price", "-")
        total_argent = _cart_total_argent(cart_list)
        cat_name = cat_names[cat_idx]
        panier_ref = context.user_data.get('click_collect_panier_id', '')
        header = format_header_rich(cat_name, "🍗", "orange", banner=False)
        msg = ""
        #if panier_ref:
        #    msg += f"🔢 Réf. panier : <code>{escape_html(panier_ref)}</code>\n\n"
        msg += (
            f"——————————————————\n"
            f"<b>{escape_html(display_name)}</b>\n"
            f"PRIX : {escape_html(str(display_price))} euro\n\n\n\n"
            f"• Dans le panier : {qty}\n"
            f"• Total panier : {total_argent:.2f} argent\n"
            f"{art_idx + 1}/{len(items)}"
        )
        if item.get("unknown_product"):
            msg += "\n\n⚠️ Produit inconnu (API Click). Ajout au panier désactivé."
        keyboard = [
            [
                InlineKeyboardButton("⬅ Precedant", callback_data=f"click_collect_art_prev_{cat_idx}_{art_idx}"),
                InlineKeyboardButton("Suivant ➡", callback_data=f"click_collect_art_next_{cat_idx}_{art_idx}"),
            ],
            [
                InlineKeyboardButton("➖", callback_data=f"click_collect_art_minus_{cat_idx}_{art_idx}"),
                InlineKeyboardButton("➕", callback_data=f"click_collect_art_plus_{cat_idx}_{art_idx}"),
            ],
            [
                InlineKeyboardButton("Retour", callback_data="click_collect_back_cats"),
                InlineKeyboardButton("Panier", callback_data="click_collect_panier"),
            ],
        ]
        return header, msg, InlineKeyboardMarkup(keyboard)

    def _render_modgrps_group():
        """Affiche l'écran du groupe modgrps en cours. Retourne (header, msg, reply_markup) ou None."""
        groups = context.user_data.get('click_collect_modgrps_groups') or []
        group_idx = context.user_data.get('click_collect_modgrps_group_idx', 0)
        if group_idx < 0 or group_idx >= len(groups):
            return None
        group = groups[group_idx]
        group_name = sanitize_display_name(group.get("name", "Options"))
        modifiers = group.get("modifiers", [])
        max_sel = group.get("max", 1)
        header = format_header_rich(group_name, "⚙️", "orange", banner=False)
        item = context.user_data.get('click_collect_modgrps_item', {})
        msg = f"Article : <b>{escape_html(sanitize_display_name(item.get('name', '?')))}</b>\n\nChoisissez :"
        keyboard = []
        if max_sel == 1:
            for m_idx, mod in enumerate(modifiers):
                keyboard.append([
                    InlineKeyboardButton(
                        escape_html(sanitize_display_name(mod.get("name", "?"))),
                        callback_data=f"click_collect_modgrps_sel_{group_idx}_{m_idx}",
                    )
                ])
        else:
            multi = context.user_data.get('click_collect_modgrps_multi') or {}
            current = multi.get(group_idx, [])
            for m_idx, mod in enumerate(modifiers):
                count = current.count(m_idx)
                label = f"{sanitize_display_name(mod.get('name', '?'))} (+{count})" if count else sanitize_display_name(mod.get("name", "?"))
                keyboard.append([
                    InlineKeyboardButton(label, callback_data=f"click_collect_modgrps_m_{group_idx}_{m_idx}"),
                ])
            msg = f"{msg}\n\nChoisissez {max_sel} option(s) (actuellement {len(current)}/{max_sel})."
        keyboard.append([InlineKeyboardButton("🔙 Annuler", callback_data="click_collect_modgrps_cancel")])
        return header, msg, InlineKeyboardMarkup(keyboard)

    def _apply_modgrps_finish():
        """Construit modgrps depuis l'arbre (build-from-tree), ajoute au panier, nettoie l'état."""
        item = context.user_data.get('click_collect_modgrps_item', {})
        cat_idx = context.user_data.get('click_collect_modgrps_cat_idx', 0)
        art_idx = context.user_data.get('click_collect_modgrps_art_idx', 0)
        tree = context.user_data.get('click_collect_modgrps_tree') or []

        # Log de l'arbre avant nettoyage de l'état
        try:
            logger.info(
                "MODGRPS_FINISH start item_id=%s name=%s cat_idx=%s art_idx=%s tree_groups=%s first_group_ids=%s",
                item.get("id"),
                item.get("name"),
                cat_idx,
                art_idx,
                len(tree),
                [g.get("id") for g in tree[:5]],
            )
        except Exception:
            pass

        for key in (
            'click_collect_modgrps_item', 'click_collect_modgrps_cat_idx', 'click_collect_modgrps_art_idx',
            'click_collect_modgrps_tree', 'click_collect_modgrps_stack', 'click_collect_modgrps_group_idx',
            'click_collect_modgrps_groups', 'click_collect_modgrps_multi',
        ):
            context.user_data.pop(key, None)
        built_modgrps = []
        if tree:
            ok, built_modgrps, err_msg = fetch_click_build_modgrps_from_tree(tree)
            if not ok or built_modgrps is None:
                logger.warning(
                    "MODGRPS_FINISH build-from-tree FAILED item_id=%s err=%s",
                    item.get("id"),
                    err_msg,
                )
                built_modgrps = []
            else:
                try:
                    logger.info(
                        "MODGRPS_FINISH build-from-tree OK item_id=%s built_groups=%s example=%s",
                        item.get("id"),
                        len(built_modgrps),
                        built_modgrps[:1],
                    )
                except Exception:
                    pass
        line = {
            "id": str(item.get("id", "")),
            "name": item.get("name", "?"),
            "cost": int(item.get("cost", 0)) if item.get("cost") not in (None, "?") else 0,
            "price": get_product_price(str(item.get("id", ""))),
            "modgrps": built_modgrps or [],
            "quantity": 1,
        }

        try:
            logger.info(
                "MODGRPS_FINISH line_for_cart id=%s name=%s cost=%s qty=%s modgrps_groups=%s",
                line["id"],
                line["name"],
                line["cost"],
                line["quantity"],
                len(line["modgrps"]),
            )
        except Exception:
            pass

        cart = context.user_data.get('click_collect_cart', [])
        if not isinstance(cart, list):
            cart = list((cart or {}).values())
        cart.append(line)
        context.user_data['click_collect_cart'] = cart
        return _render_article_page(cat_idx, art_idx)

    if callback_data.startswith("click_collect_city_"):
        try:
            idx = int(callback_data.split("_")[-1])
            stores_list = context.user_data.get('click_collect_stores', [])
            cities = context.user_data.get('click_collect_cities', [])
            if idx < 0 or idx >= len(cities):
                try:
                    await query.edit_message_text("❌ Ville invalide.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Retour", callback_data="boutique_click_collect")]]))
                except TelegramError:
                    pass
                try:
                    await query.answer()
                except TelegramError:
                    pass
                return
            city = cities[idx]
            filtered = [s for s in stores_list if (s.get("city") or "?") == city]
            context.user_data['click_collect_selected_city'] = idx
            context.user_data['click_collect_stores_filtered'] = filtered
            header = format_header_rich(f"KFC — {city}", "🍗", "orange", banner=False)
            keyboard = []
            for i, s in enumerate(filtered):
                name = s.get("name", "?")
                keyboard.append([InlineKeyboardButton(f"🍗 {name}", callback_data=f"click_collect_store_{i}")])
            keyboard.append([InlineKeyboardButton("🔙 Retour aux villes", callback_data="click_collect_back_cities")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await safe_edit_message_text(query, header, reply_markup, "HTML")
            try:
                await query.answer()
            except TelegramError:
                pass
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur click_collect_city: {e}")
        return

    if callback_data == "click_collect_back_cities":
        stores_list = context.user_data.get('click_collect_stores', [])
        cities = context.user_data.get('click_collect_cities', [])
        if not cities:
            await show_boutique_click_collect_menu(update, context, user_id)
            try:
                await query.answer()
            except TelegramError:
                pass
            return
        header = format_header_rich("CHOISIR UNE VILLE", "📍", "orange", banner=False)
        keyboard = []
        for i, city in enumerate(cities):
            count = sum(1 for s in stores_list if (s.get("city") or "?") == city)
            keyboard.append([InlineKeyboardButton(f"📍 {city} ({count})", callback_data=f"click_collect_city_{i}")])
        keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data="boutique_click_collect")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message_text(query, header, reply_markup, "HTML")
        try:
            await query.answer()
        except TelegramError:
            pass
        return

    if callback_data.startswith("click_collect_store_"):
        try:
            idx = int(callback_data.split("_")[-1])
            filtered = context.user_data.get('click_collect_stores_filtered', [])
            if idx < 0 or idx >= len(filtered):
                try:
                    await query.answer()
                except TelegramError:
                    pass
                return
            store = filtered[idx]
            name = sanitize_display_name(store.get("name", "?"))
            store_id = store.get("id")
            if not store_id:
                try:
                    await query.answer()
                except TelegramError:
                    pass
                return
            prev_store = context.user_data.get('click_collect_selected_store', {})
            prev_store_id = prev_store.get("id") if prev_store else None
            cart = context.user_data.get('click_collect_cart', [])
            cart_list = cart if isinstance(cart, list) else list((cart or {}).values())
            if prev_store_id and str(store_id) != str(prev_store_id) and cart_list:
                context.user_data['click_collect_pending_store_idx'] = idx
                header = format_header_rich("CHANGER DE RESTAURANT ?", "⚠️", "orange", banner=False)
                msg = (
                    f"Votre panier contient {len(cart_list)} article(s).\n\n"
                    f"Changer pour <b>{escape_html(name)}</b> videra votre panier.\n\n"
                    "Confirmer ?"
                )
                keyboard = [
                    [InlineKeyboardButton("✅ Oui, vider le panier", callback_data=f"click_collect_confirm_store_{idx}")],
                    [InlineKeyboardButton("❌ Annuler", callback_data="click_collect_back_stores")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
                try:
                    await query.answer()
                except TelegramError:
                    pass
                return
            await _do_select_store_and_load_menu(query, context, idx, user_id)
            try:
                await query.answer()
            except TelegramError:
                pass
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur click_collect_store: {e}")
        return

    if callback_data.startswith("click_collect_confirm_store_"):
        try:
            idx = int(callback_data.split("_")[-1])
            context.user_data.pop('click_collect_pending_store_idx', None)
            context.user_data.pop('click_collect_cart', None)
            context.user_data['click_collect_cart'] = []
            context.user_data.pop('click_collect_panier_id', None)
            await _do_select_store_and_load_menu(query, context, idx, user_id)
            try:
                await query.answer()
            except TelegramError:
                pass
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur click_collect_confirm_store: {e}")
        return

    if callback_data.startswith("click_collect_cat_"):
        try:
            cat_idx = int(callback_data.split("_")[-1])
            menu = context.user_data.get('click_collect_preview_menu', {})
            cat_names = list(menu.keys())
            if cat_idx < 0 or cat_idx >= len(cat_names):
                try:
                    await query.answer()
                except TelegramError:
                    pass
                return
            cat_name = cat_names[cat_idx]
            items = menu.get(cat_name, [])
            if not items:
                await query.answer("Catégorie vide", show_alert=True)
                return
            context.user_data['click_collect_selected_cat'] = cat_idx
            result = _render_article_page(cat_idx, 0)
            if not result:
                await query.answer("Catégorie vide", show_alert=True)
                return
            header, msg, reply_markup = result
            await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
            try:
                await query.answer()
            except TelegramError:
                pass
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur click_collect_cat: {e}")
        return

    if callback_data == "click_collect_back_cats":
        context.user_data.pop('click_collect_waiting_credentials', None)
        menu = context.user_data.get('click_collect_preview_menu', {})
        store = context.user_data.get('click_collect_selected_store', {})
        store_name = store.get("name", "?")
        if not menu:
            await show_boutique_click_collect_menu(update, context, user_id)
            try:
                await query.answer()
            except TelegramError:
                pass
            return
        panier_ref = context.user_data.get('click_collect_panier_id', '')
        header = format_header_rich(f"Menu — {sanitize_display_name(store_name)}", "🍗", "orange", banner=False)
        header_extra = f"\n🔢 Réf. panier : <code>{escape_html(panier_ref)}</code>\n" if panier_ref else ""
        cat_names = list(menu.keys())
        keyboard = []
        for i, cat_name in enumerate(cat_names):
            count = len(menu.get(cat_name, []))
            keyboard.append([InlineKeyboardButton(f"📂 {cat_name} ({count})", callback_data=f"click_collect_cat_{i}")])
        keyboard.append([InlineKeyboardButton("🔙 Retour aux restaurants", callback_data="click_collect_back_stores")])
        keyboard.append([InlineKeyboardButton("🧺 Panier", callback_data="click_collect_panier")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message_text(query, header, reply_markup, "HTML")
        try:
            await query.answer()
        except TelegramError:
            pass
        return

    if callback_data == "click_collect_back_stores":
        filtered = context.user_data.get('click_collect_stores_filtered', [])
        cities = context.user_data.get('click_collect_cities', [])
        city_idx = context.user_data.get('click_collect_selected_city', 0)
        city = cities[city_idx] if city_idx < len(cities) else "?"
        context.user_data.pop('click_collect_preview_menu', None)
        context.user_data.pop('click_collect_selected_store', None)
        context.user_data.pop('click_collect_selected_cat', None)
        header = format_header_rich(f"KFC — {city}", "🍗", "orange", banner=False)
        keyboard = []
        for i, s in enumerate(filtered):
            name = sanitize_display_name(s.get("name", "?"))
            keyboard.append([InlineKeyboardButton(f"🍗 {name}", callback_data=f"click_collect_store_{i}")])
        keyboard.append([InlineKeyboardButton("🔙 Retour aux villes", callback_data="click_collect_back_cities")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message_text(query, header, reply_markup, "HTML")
        try:
            await query.answer()
        except TelegramError:
            pass
        return

    if callback_data == "click_collect_panier":
        context.user_data.pop('click_collect_waiting_credentials', None)
        context.user_data.pop('click_collect_waiting_prenom', None)
        context.user_data.pop('click_collect_card_for_token', None)
        context.user_data.pop('click_collect_prenom', None)
        context.user_data.pop('click_collect_remove_article', None)
        cart = context.user_data.get('click_collect_cart', [])
        cart_list = cart if isinstance(cart, list) else list((cart or {}).values())
        store = context.user_data.get('click_collect_selected_store', {})
        if not store or not store.get("id"):
            await query.answer("❌ Sélectionnez d'abord un KFC.", show_alert=True)
            return
        total_argent = _cart_total_argent(cart_list)
        header = format_header_rich("PANIER", "🛒", "orange", banner=False)
        store_name = store.get("name", "?")
        panier_ref = context.user_data.get('click_collect_panier_id', '')
        msg = f"📍 <b>{escape_html(sanitize_display_name(store_name))}</b>"
        if panier_ref:
            msg += f"\nRéférence  : <code>{escape_html(panier_ref)}</code>"
        msg += "\n"
        if not cart_list:
            msg += "Votre panier est vide.\n\nAjoutez des articles en parcourant les catégories."
        else:
            msg += f"{len(cart_list)} article(s) • {total_argent:.2f} argent\n--------------------------------\n\n"
            for e in cart_list[:15]:
                line_price = e.get("price", get_product_price(str(e.get("id", ""))))
                try:
                    line_price_float = float(line_price)
                except (TypeError, ValueError):
                    line_price_float = 0.0
                msg += f"• {escape_html(sanitize_display_name(e.get('name', '?')))} x{e.get('quantity', 1)} — {line_price_float:.2f} euro\n"
            if len(cart_list) > 15:
                msg += f"... et {len(cart_list) - 15} autre(s)"
        keyboard = []
        if cart_list:
            keyboard.append([InlineKeyboardButton("✅ Commander", callback_data="click_collect_commander")])
        keyboard.append([InlineKeyboardButton("📂 Continuer mes choix", callback_data="click_collect_back_cats")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
        try:
            await query.answer()
        except TelegramError:
            pass
        return

    if callback_data.startswith("click_collect_art_plus_"):
        try:
            parts = callback_data.split("_")
            cat_idx, art_idx = int(parts[-2]), int(parts[-1])
            menu = context.user_data.get('click_collect_preview_menu', {})
            cat_names = list(menu.keys())
            if cat_idx < 0 or cat_idx >= len(cat_names):
                return
            items = menu.get(cat_names[cat_idx], [])
            if art_idx < 0 or art_idx >= len(items):
                return
            item = items[art_idx]
            if item.get("unknown_product"):
                try:
                    await query.answer(
                        "Produit inconnu du dictionnaire PRODUCT : ajout au panier bloqué.",
                        show_alert=True,
                    )
                except TelegramError:
                    pass
                return
            # Vérifier la limite de points du panier avant d'ajouter l'article
            cart_for_total = context.user_data.get('click_collect_cart', [])
            if not isinstance(cart_for_total, list):
                cart_for_total = list((cart_for_total or {}).values())
            current_total_pts = sum(
                int(e.get("cost", 0)) * int(e.get("quantity", 1))
                for e in cart_for_total
            )
            item_cost = int(item.get("cost", 0)) if item.get("cost", 0) not in (None, "?") else 0
            if current_total_pts + item_cost > CLICK_COLLECT_MAX_BASKET_POINTS:
                try:
                    await query.answer(
                        "Maximum de 2500 points par panier atteint. Finissez ce panier puis créez-en un autre.",
                        show_alert=True,
                    )
                except TelegramError:
                    pass
                return

            try:
                await query.answer()
            except TelegramError:
                pass

            item_modgrps = (item.get("modgrps") or []) if isinstance(item.get("modgrps"), list) else []
            cart = context.user_data.get('click_collect_cart', [])
            if not isinstance(cart, list):
                cart = list((cart or {}).values())
            if not item_modgrps:
                line = {
                    "id": str(item.get("id", "")),
                    "name": item.get("name", "?"),
                    "cost": int(item.get("cost", 0)) if item.get("cost") not in (None, "?") else 0,
                    "price": get_product_price(str(item.get("id", ""))),
                    "modgrps": [],
                    "quantity": 1,
                }
                cart.append(line)
                context.user_data['click_collect_cart'] = cart
                result = _render_article_page(cat_idx, art_idx)
                if result:
                    header, msg, reply_markup = result
                    await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
            else:
                context.user_data['click_collect_modgrps_item'] = item
                context.user_data['click_collect_modgrps_cat_idx'] = cat_idx
                context.user_data['click_collect_modgrps_art_idx'] = art_idx
                modgrps_tree = copy.deepcopy(item_modgrps)
                # Remise à zéro des qty dans tout l'arbre avant sélection
                def _init_modgrps_qty(tree):
                    if not tree:
                        return
                    for g in tree:
                        for m in g.get("modifiers", []):
                            m["qty"] = 0
                            if m.get("modgrps"):
                                _init_modgrps_qty(m["modgrps"])
                _init_modgrps_qty(modgrps_tree)
                context.user_data['click_collect_modgrps_tree'] = modgrps_tree
                context.user_data['click_collect_modgrps_stack'] = []
                gidx = 0
                while gidx < len(modgrps_tree) and not (modgrps_tree[gidx].get("modifiers")):
                    gidx += 1
                context.user_data['click_collect_modgrps_group_idx'] = gidx
                context.user_data['click_collect_modgrps_groups'] = modgrps_tree
                context.user_data['click_collect_modgrps_multi'] = {}
                result = _render_modgrps_group()
                if result:
                    header, msg, reply_markup = result
                    await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur click_collect_art_plus: {e}")
        return

    if callback_data.startswith("click_collect_art_minus_"):
        try:
            parts = callback_data.split("_")
            cat_idx, art_idx = int(parts[-2]), int(parts[-1])
            menu = context.user_data.get('click_collect_preview_menu', {})
            cat_names = list(menu.keys())
            if cat_idx < 0 or cat_idx >= len(cat_names):
                try:
                    await query.answer()
                except TelegramError:
                    pass
                return
            items = menu.get(cat_names[cat_idx], [])
            if art_idx < 0 or art_idx >= len(items):
                try:
                    await query.answer()
                except TelegramError:
                    pass
                return
            item = items[art_idx]
            loyalty_id = str(item.get("id", ""))
            cart_list = _cart_lines()
            lines_for_article = [(i, e) for i, e in enumerate(cart_list) if str(e.get("id", "")) == loyalty_id]
            if not lines_for_article:
                result = _render_article_page(cat_idx, art_idx)
                if result:
                    header, msg, reply_markup = result
                    await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
                try:
                    await query.answer()
                except TelegramError:
                    pass
                return
            if len(lines_for_article) == 1 and lines_for_article[0][1].get("quantity", 1) == 1:
                cart = context.user_data.get('click_collect_cart', [])
                if isinstance(cart, list):
                    idx = lines_for_article[0][0]
                    cart.pop(idx)
                    context.user_data['click_collect_cart'] = cart
                result = _render_article_page(cat_idx, art_idx)
                if result:
                    header, msg, reply_markup = result
                    await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
            else:
                context.user_data['click_collect_remove_article'] = (cat_idx, art_idx)
                header = format_header_rich("LEQUEL SUPPRIMER ?", "➖", "orange", banner=False)
                msg = "Choisissez la ligne à retirer :"
                keyboard = []
                for i, (line_idx, line) in enumerate(lines_for_article):
                    q = line.get("quantity", 1)
                    label = f"{sanitize_display_name(line.get('name', '?'))} x{q}"
                    keyboard.append([InlineKeyboardButton(label, callback_data=f"click_collect_remove_line_{line_idx}")])
                keyboard.append([InlineKeyboardButton("🔙 Annuler", callback_data="click_collect_remove_cancel")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
            try:
                await query.answer()
            except TelegramError:
                pass
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur click_collect_art_minus: {e}")
        return

    if callback_data.startswith("click_collect_remove_line_"):
        try:
            line_idx = int(callback_data.split("_")[-1])
            remove_ctx = context.user_data.get('click_collect_remove_article')
            cart = context.user_data.get('click_collect_cart', [])
            if not isinstance(cart, list) or line_idx < 0 or line_idx >= len(cart):
                context.user_data.pop('click_collect_remove_article', None)
                await query.answer("Ligne introuvable.", show_alert=True)
                return
            line = cart[line_idx]
            q = line.get("quantity", 1)
            if q <= 1:
                cart.pop(line_idx)
            else:
                line["quantity"] = q - 1
            context.user_data['click_collect_cart'] = cart
            context.user_data.pop('click_collect_remove_article', None)
            cat_idx, art_idx = remove_ctx if remove_ctx else (0, 0)
            result = _render_article_page(cat_idx, art_idx)
            if result:
                header, msg, reply_markup = result
                await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
            try:
                await query.answer()
            except TelegramError:
                pass
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur click_collect_remove_line: {e}")
        return

    if callback_data == "click_collect_remove_cancel":
        remove_ctx = context.user_data.get('click_collect_remove_article')
        context.user_data.pop('click_collect_remove_article', None)
        cat_idx, art_idx = (remove_ctx[0], remove_ctx[1]) if remove_ctx and len(remove_ctx) >= 2 else (0, 0)
        result = _render_article_page(cat_idx, art_idx)
        if result:
            header, msg, reply_markup = result
            await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
        try:
            await query.answer()
        except TelegramError:
            pass
        return

    if callback_data == "click_collect_modgrps_cancel":
        cat_idx = context.user_data.get('click_collect_modgrps_cat_idx', 0)
        art_idx = context.user_data.get('click_collect_modgrps_art_idx', 0)
        for key in (
            'click_collect_modgrps_item', 'click_collect_modgrps_cat_idx', 'click_collect_modgrps_art_idx',
            'click_collect_modgrps_tree', 'click_collect_modgrps_stack', 'click_collect_modgrps_group_idx',
            'click_collect_modgrps_groups', 'click_collect_modgrps_multi',
        ):
            context.user_data.pop(key, None)
        result = _render_article_page(cat_idx, art_idx)
        if result:
            header, msg, reply_markup = result
            await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
        try:
            await query.answer()
        except TelegramError:
            pass
        return

    if callback_data.startswith("click_collect_modgrps_sel_"):
        try:
            parts = callback_data.split("_")
            group_idx = int(parts[-2])
            mod_idx = int(parts[-1])
            groups = context.user_data.get('click_collect_modgrps_groups') or []
            stack = context.user_data.get('click_collect_modgrps_stack') or []
            if group_idx >= len(groups):
                try:
                    await query.answer()
                except TelegramError:
                    pass
                return
            group = groups[group_idx]
            modifiers = group.get("modifiers", [])
            if mod_idx < 0 or mod_idx >= len(modifiers):
                try:
                    await query.answer()
                except TelegramError:
                    pass
                return
            # Remettre toutes les qty du groupe à 0 avant de sélectionner
            for m in modifiers:
                m["qty"] = 0
            selected_mod = modifiers[mod_idx]
            selected_mod["qty"] = group.get("max", 1)
            nested = selected_mod.get("modgrps") or []
            if nested:
                stack.append((group_idx + 1, groups))
                context.user_data['click_collect_modgrps_groups'] = nested
                context.user_data['click_collect_modgrps_group_idx'] = 0
                context.user_data['click_collect_modgrps_stack'] = stack
            else:
                context.user_data['click_collect_modgrps_group_idx'] = group_idx + 1
            gidx = context.user_data.get('click_collect_modgrps_group_idx', 0)
            groups = context.user_data.get('click_collect_modgrps_groups') or []
            while gidx >= len(groups) and stack:
                next_idx, parent_groups = stack.pop()
                context.user_data['click_collect_modgrps_groups'] = parent_groups
                context.user_data['click_collect_modgrps_group_idx'] = next_idx
                context.user_data['click_collect_modgrps_stack'] = stack
                gidx = next_idx
                groups = parent_groups
            gidx = context.user_data.get('click_collect_modgrps_group_idx', 0)
            groups = context.user_data.get('click_collect_modgrps_groups') or []
            while gidx < len(groups) and not (groups[gidx].get("modifiers")):
                gidx += 1
            context.user_data['click_collect_modgrps_group_idx'] = gidx
            if gidx >= len(groups) and not context.user_data.get('click_collect_modgrps_stack'):
                result = _apply_modgrps_finish()
                if result:
                    header, msg, reply_markup = result
                    await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
            else:
                result = _render_modgrps_group()
                if result:
                    header, msg, reply_markup = result
                    await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
            try:
                await query.answer()
            except TelegramError:
                pass
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur click_collect_modgrps_sel: {e}")
        return

    if callback_data.startswith("click_collect_modgrps_m_"):
        try:
            parts = callback_data.split("_")
            if parts[-2] == "done":
                group_idx = int(parts[-1])
                groups = context.user_data.get('click_collect_modgrps_groups') or []
                if group_idx < len(groups):
                    group = groups[group_idx]
                    multi = context.user_data.get('click_collect_modgrps_multi') or {}
                    indices = multi.get(group_idx, [])
                    for i in indices:
                        mods = group.get("modifiers", [])
                        if 0 <= i < len(mods):
                            mods[i]["qty"] = mods[i].get("qty", 0) + 1
                    context.user_data['click_collect_modgrps_multi'] = {k: v for k, v in multi.items() if k != group_idx}
                context.user_data['click_collect_modgrps_group_idx'] = group_idx + 1
            else:
                group_idx = int(parts[-2])
                mod_idx = int(parts[-1])
                groups = context.user_data.get('click_collect_modgrps_groups') or []
                group = groups[group_idx] if group_idx < len(groups) else {}
                max_sel = group.get("max", 1)
                multi = context.user_data.get('click_collect_modgrps_multi') or {}
                current = multi.get(group_idx, [])
                if len(current) < max_sel:
                    current = list(current) + [mod_idx]
                    if len(current) > max_sel:
                        current = current[:max_sel]
                    multi[group_idx] = current
                    context.user_data['click_collect_modgrps_multi'] = multi
                    if len(current) == max_sel:
                        for i in current:
                            mods = group.get("modifiers", [])
                            if 0 <= i < len(mods):
                                mods[i]["qty"] = mods[i].get("qty", 0) + 1
                        context.user_data['click_collect_modgrps_multi'] = {k: v for k, v in multi.items() if k != group_idx}
                        context.user_data['click_collect_modgrps_group_idx'] = group_idx + 1
            groups = context.user_data.get('click_collect_modgrps_groups') or []
            gidx = context.user_data.get('click_collect_modgrps_group_idx', 0)
            stack = context.user_data.get('click_collect_modgrps_stack') or []
            while gidx >= len(groups) and stack:
                next_idx, parent_groups = stack.pop()
                context.user_data['click_collect_modgrps_groups'] = parent_groups
                context.user_data['click_collect_modgrps_group_idx'] = next_idx
                context.user_data['click_collect_modgrps_stack'] = stack
                gidx = next_idx
                groups = parent_groups
            gidx = context.user_data.get('click_collect_modgrps_group_idx', 0)
            groups = context.user_data.get('click_collect_modgrps_groups') or []
            stack = context.user_data.get('click_collect_modgrps_stack') or []
            while gidx < len(groups) and not (groups[gidx].get("modifiers")):
                gidx += 1
            context.user_data['click_collect_modgrps_group_idx'] = gidx
            if gidx >= len(groups) and not stack:
                result = _apply_modgrps_finish()
                if result:
                    header, msg, reply_markup = result
                    await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
            else:
                result = _render_modgrps_group()
                if result:
                    header, msg, reply_markup = result
                    await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
            try:
                await query.answer()
            except TelegramError:
                pass
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur click_collect_modgrps_m: {e}")
        return

    if callback_data.startswith("click_collect_art_prev_"):
        try:
            parts = callback_data.split("_")
            cat_idx, art_idx = int(parts[-2]), int(parts[-1])
            if art_idx <= 0:
                context.user_data.pop('click_collect_waiting_credentials', None)
                menu = context.user_data.get('click_collect_preview_menu', {})
                store = context.user_data.get('click_collect_selected_store', {})
                store_name = sanitize_display_name(store.get("name", "?"))
                header = format_header_rich(f"Menu — {store_name}", "🍗", "orange", banner=False)
                cat_names = list(menu.keys())
                keyboard = []
                for i, cat_name in enumerate(cat_names):
                    count = len(menu.get(cat_name, []))
                    keyboard.append([InlineKeyboardButton(f"📂 {cat_name} ({count})", callback_data=f"click_collect_cat_{i}")])
                keyboard.append([InlineKeyboardButton("🔙 Retour aux restaurants", callback_data="click_collect_back_stores")])
                keyboard.append([InlineKeyboardButton("🧺 Panier", callback_data="click_collect_panier")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await safe_edit_message_text(query, header, reply_markup, "HTML")
            else:
                result = _render_article_page(cat_idx, art_idx - 1)
                if result:
                    header, msg, reply_markup = result
                    await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
            try:
                await query.answer()
            except TelegramError:
                pass
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur click_collect_art_prev: {e}")
        return

    if callback_data.startswith("click_collect_art_next_"):
        try:
            parts = callback_data.split("_")
            cat_idx, art_idx = int(parts[-2]), int(parts[-1])
            menu = context.user_data.get('click_collect_preview_menu', {})
            cat_names = list(menu.keys())
            items = menu.get(cat_names[cat_idx], []) if cat_idx < len(cat_names) else []
            if art_idx >= len(items) - 1:
                context.user_data.pop('click_collect_waiting_credentials', None)
                store = context.user_data.get('click_collect_selected_store', {})
                store_name = sanitize_display_name(store.get("name", "?"))
                header = format_header_rich(f"Menu — {store_name}", "🍗", "orange", banner=False)
                keyboard = []
                for i, cat_name in enumerate(cat_names):
                    count = len(menu.get(cat_name, []))
                    keyboard.append([InlineKeyboardButton(f"📂 {cat_name} ({count})", callback_data=f"click_collect_cat_{i}")])
                keyboard.append([InlineKeyboardButton("🔙 Retour aux restaurants", callback_data="click_collect_back_stores")])
                keyboard.append([InlineKeyboardButton("🧺 Panier", callback_data="click_collect_panier")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await safe_edit_message_text(query, header, reply_markup, "HTML")
            else:
                result = _render_article_page(cat_idx, art_idx + 1)
                if result:
                    header, msg, reply_markup = result
                    await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
            try:
                await query.answer()
            except TelegramError:
                pass
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur click_collect_art_next: {e}")
        return

    if callback_data == "click_collect_commander":
        cart = context.user_data.get('click_collect_cart', [])
        cart_list = cart if isinstance(cart, list) else list((cart or {}).values())
        store = context.user_data.get('click_collect_selected_store', {})
        if not cart_list:
            await query.answer("🛒 Votre panier est vide. Ajoutez des articles avec le bouton ➕", show_alert=True)
            return
        if not store or not store.get("id"):
            await query.answer("❌ Erreur : restaurant non sélectionné.", show_alert=True)
            return
        total_argent = _cart_total_argent(cart_list)
        # Vérification du solde local avant confirmation définitive
        user_balance = get_user_balance(user_id)
        if user_balance < total_argent:
            header = format_header_rich("ARGENT INSUFFISANT", "⚠️", "orange", banner=False)
            msg = (
                f"Votre panier contient <b>{total_argent:.2f} euro</b>, mais votre solde actuel est de "
                f"<b>{float(user_balance):.2f} argent</b>.\n\n"
                "Rechargez votre solde en achetant de l'argent, ou réduisez le contenu du panier."
            )
            keyboard = [
                [InlineKeyboardButton("💰 Acheter de l'argent", callback_data="cmd_acheter_points")],
                [InlineKeyboardButton("🔙 Retour au panier", callback_data="click_collect_panier")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
            try:
                await query.answer()
            except TelegramError:
                pass
            return
        cart_preview_lines = []
        for e in cart_list[:10]:
            raw_price = e.get("price", get_product_price(str(e.get("id", ""))))
            try:
                item_price = float(raw_price)
            except (TypeError, ValueError):
                item_price = 0.0
            cart_preview_lines.append(
                f"• {escape_html(sanitize_display_name(e.get('name', '?')))} x{e.get('quantity', 1)} ({item_price:.2f} euro)"
            )
        cart_preview = "\n".join(cart_preview_lines)
        if len(cart_list) > 10:
            cart_preview += f"\n... et {len(cart_list) - 10} autre(s)"
        header = format_header_rich("CHOIX DÉFINITIF ?", "⚠️", "orange", banner=False)
        msg = (
            f"<b>Votre panier ({len(cart_list)} article(s), {total_argent:.2f} euro) :</b>\n{cart_preview}\n\n"
            "Êtes-vous sûr ? Le choix est définitif."
        )
        keyboard = [
            [InlineKeyboardButton("✅ Continuer", callback_data="click_collect_commander_continue")],
            [InlineKeyboardButton("🔙 Retour au panier", callback_data="click_collect_panier")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
        try:
            await query.answer()
        except TelegramError:
            pass
        return

    if callback_data == "click_collect_commander_continue":
        context.user_data.pop('click_collect_card_for_token', None)
        context.user_data.pop('click_collect_prenom', None)
        context.user_data['click_collect_waiting_prenom'] = True
        header = format_header_rich("PRÉNOM POUR LA COMMANDE", "✏️", "orange", banner=False)
        msg = (
            "Entrez le <b>prénom</b> pour la commande Click & Collect.\n\n"
            "Un seul mot, accents et majuscules autorisés, tiret autorisé. Pas d'espaces ni de caractères spéciaux."
        )
        keyboard = [[InlineKeyboardButton("🔙 Annuler", callback_data="click_collect_panier")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
        try:
            await query.answer()
        except TelegramError:
            pass
        return

    if callback_data == "click_collect_retry_token":
        card = context.user_data.get('click_collect_card_for_token')
        prenom = context.user_data.get('click_collect_prenom')
        if not card or not prenom:
            await query.answer("❌ Données manquantes. Recommencez depuis le panier → Commander.", show_alert=True)
            return
        await _do_recup_token_and_session(query, update, context, user_id, card, prenom)
        return

    if callback_data == "click_collect_validate":
        if not context.user_data.get('click_collect_session_created'):
            await query.answer("❌ Session non créée. Recommencez depuis le panier → Commander.", show_alert=True)
            return
        panier_id = context.user_data.get('click_collect_panier_id')
        if not panier_id:
            await query.answer("❌ Panier introuvable. Recommencez depuis le début.", show_alert=True)
            return
        await safe_edit_message_text(query, "⏳ Validation en cours (checkout + soumission)...", None, "HTML")
        ok_checkout, err_checkout = fetch_click_checkout(str(panier_id))
        if not ok_checkout:
            header = format_header_rich("ERREUR CHECKOUT", "❌", "orange", banner=False)
            keyboard = [
                [InlineKeyboardButton("🔙 Retour au panier", callback_data="click_collect_panier")],
                [InlineKeyboardButton("🏠 Accueil", callback_data="cmd_shop")],
            ]
            await safe_edit_message_text(
                query,
                f"{header}\n\n{escape_html(err_checkout or 'Erreur inconnue')}",
                InlineKeyboardMarkup(keyboard),
                "HTML",
            )
            try:
                await query.answer()
            except TelegramError:
                pass
            return
        ok_submit, data_submit, err_submit = fetch_click_submit(str(panier_id))
        if not ok_submit:
            header = format_header_rich("ERREUR SOUMISSION", "❌", "orange", banner=False)
            keyboard = [
                [InlineKeyboardButton("🔙 Retour au panier", callback_data="click_collect_panier")],
                [InlineKeyboardButton("🏠 Accueil", callback_data="cmd_shop")],
            ]
            await safe_edit_message_text(
                query,
                f"{header}\n\n{escape_html(err_submit or 'Erreur inconnue')}",
                InlineKeyboardMarkup(keyboard),
                "HTML",
            )
            try:
                await query.answer()
            except TelegramError:
                pass
            return
        # Débit local du solde utilisateur (argent consommé par le panier)
        try:
            cart = context.user_data.get('click_collect_cart', [])
            cart_list = cart if isinstance(cart, list) else list((cart or {}).values())
            total_argent = _cart_total_argent(cart_list)
            if total_argent > 0:
                debit_amount = total_argent
                ok_debit = update_user_points(user_id, -debit_amount)
                if not ok_debit:
                    logger.warning(
                        f"Échec du débit local de {debit_amount} argent pour l'utilisateur {user_id} "
                        f"après submit Click&Collect (panier_id={panier_id})"
                    )
        except Exception as e:
            logger.error(
                f"Exception lors du débit local de l'argent pour l'utilisateur {user_id} "
                f"après submit Click&Collect (panier_id={panier_id}): {e}"
            )
        conf_url = (data_submit or {}).get("confirmation_url") if data_submit else None
        first_name = (data_submit or {}).get("first_name") if data_submit else None
        last_name = (data_submit or {}).get("last_name") if data_submit else None
        order_number = (data_submit or {}).get("order_number") if data_submit else None
        phone_number = (data_submit or {}).get("phone_number") if data_submit else None
        selected_store = context.user_data.get("click_collect_selected_store") or {}
        store_name = (data_submit or {}).get("store_name") if data_submit else None
        store_city = (data_submit or {}).get("store_city") if data_submit else None
        if not store_name:
            store_name = selected_store.get("name")
        if not store_city:
            store_city = selected_store.get("city")
        first_name_display = escape_html(str(first_name)) if first_name else "—"
        last_name_display = escape_html(str(last_name)) if last_name else "—"
        order_number_display = escape_html(str(order_number)) if order_number else "—"
        phone_masked = escape_html(mask_phone_for_click_display(phone_number))
        store_name_display = escape_html(str(store_name)) if store_name else "—"
        store_city_display = escape_html(str(store_city)) if store_city else "—"
        context.user_data["click_collect_last_submit_info"] = data_submit
        header = format_header_rich("COMMANDE TERMINÉE", "✅", "success", banner=False)
        msg = (
            f"\n"
            f" N° commande : {order_number_display}\n"
            f"👤 Nom : {first_name_display} {last_name_display}\n"
            f"📱 Téléphone : {phone_masked}\n\n"
            f"🍗 KFC : {store_name_display}\n"
            f"📍 Ville : {store_city_display}\n\n"
            f"🔗 Commande :\n{escape_html(conf_url or '—')}"
        )
        keyboard = [
            [InlineKeyboardButton("⏱ Lancer la préparation (3min)", callback_data="click_collect_3min")],
            [InlineKeyboardButton("🏠 Accueil", callback_data="cmd_shop")],
        ]
        if role == "admin":
            keyboard.insert(1, [InlineKeyboardButton("📋 Voir toutes les infos", callback_data="click_collect_show_submit_info")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
        try:
            await query.answer()
        except TelegramError:
            pass
        return

    if callback_data == "click_collect_show_submit_info":
        if role != "admin":
            try:
                await query.answer()
            except TelegramError:
                pass
            return
        info = context.user_data.get("click_collect_last_submit_info") or {}
        header = format_header_rich("INFOS COMMANDE (ADMIN)", "📋", "info", banner=False)
        lines = [
            f"🔗 <b>Lien :</b> {escape_html(info.get('confirmation_url') or '—')}",
            f"🆔 <b>Order UUID :</b> <code>{escape_html(str(info.get('order_uuid') or '—'))}</code>",
            f"#️⃣ <b>N° commande :</b> {escape_html(str(info.get('order_number') or '—'))}",
            f"👤 <b>Prénom :</b> {escape_html(str(info.get('first_name') or '—'))}",
            f"👤 <b>Nom :</b> {escape_html(str(info.get('last_name') or '—'))}",
            f"📧 <b>Email :</b> {escape_html(str(info.get('email') or '—'))}",
            f"📱 <b>Téléphone :</b> {escape_html(str(info.get('phone_number') or '—'))}",
            f"🎂 <b>Date de naissance :</b> {escape_html(str(info.get('date_of_birth') or '—'))}",
            f"🍗 <b>Restaurant :</b> {escape_html(str(info.get('store_name') or '—'))}",
            f"📍 <b>Ville :</b> {escape_html(str(info.get('store_city') or '—'))}",
        ]
        msg = "\n".join(lines)
        keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="click_collect_submit_info_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
        try:
            await query.answer()
        except TelegramError:
            pass
        return

    if callback_data == "click_collect_submit_info_back":
        info = context.user_data.get("click_collect_last_submit_info") or {}
        conf_url = info.get("confirmation_url")
        first_name = info.get("first_name")
        last_name = info.get("last_name")
        order_number = info.get("order_number")
        phone_number = info.get("phone_number")
        selected_store = context.user_data.get("click_collect_selected_store") or {}
        store_name = info.get("store_name") or selected_store.get("name")
        store_city = info.get("store_city") or selected_store.get("city")
        first_name_display = escape_html(str(first_name)) if first_name else "—"
        last_name_display = escape_html(str(last_name)) if last_name else "—"
        order_number_display = escape_html(str(order_number)) if order_number else "—"
        phone_masked = escape_html(mask_phone_for_click_display(phone_number))
        store_name_display = escape_html(str(store_name)) if store_name else "—"
        store_city_display = escape_html(str(store_city)) if store_city else "—"
        header = format_header_rich("COMMANDE TERMINÉE", "✅", "success", banner=False)
        msg = (
            f"\n"
            f" N° commande : {order_number_display}\n"
            f"👤 Nom : {first_name_display} {last_name_display}\n"
            f"📱 Téléphone : {phone_masked}\n\n"
            f"🍗 KFC : {store_name_display}\n"
            f"📍 Ville : {store_city_display}\n\n"
            f"🔗 commande :\n{escape_html(conf_url or '—')}"
        )
        keyboard = [
            [InlineKeyboardButton("⏱ Lancer la préparation (3min)", callback_data="click_collect_3min")],
            [InlineKeyboardButton("📋 Voir toutes les infos", callback_data="click_collect_show_submit_info")],
            [InlineKeyboardButton("🏠 Accueil", callback_data="cmd_shop")],
        ]
        if role != "admin":
            keyboard = [
                [InlineKeyboardButton("⏱ Lancer la préparation (3min)", callback_data="click_collect_3min")],
                [InlineKeyboardButton("🏠 Accueil", callback_data="cmd_shop")],
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
        try:
            await query.answer()
        except TelegramError:
            pass
        return

    if callback_data == "click_collect_3min":
        if not context.user_data.get('click_collect_session_created'):
            await query.answer("❌ Session non créée.", show_alert=True)
            return
        panier_id = context.user_data.get('click_collect_panier_id')
        if not panier_id:
            await query.answer("❌ Panier introuvable.", show_alert=True)
            return
        await safe_edit_message_text(query, "⏳ Check-in en cours...", None, "HTML")
        ok, err = fetch_click_checkin(str(panier_id))
        if ok:
            header = format_header_rich("CHECK-IN OK", "✅", "success", banner=False)
            msg = "Le check-in a été effectué. Présentez-vous au KFC pour récupérer votre commande."
            keyboard = [
                [InlineKeyboardButton("🔙 Retour à ma commande", callback_data="click_collect_submit_info_back")],
                [InlineKeyboardButton("🏠 Accueil", callback_data="cmd_shop")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await safe_edit_message_text(query, f"{header}\n\n{msg}", reply_markup, "HTML")
            await query.answer("✅ Check-in effectué !")
        else:
            header = format_header_rich("ERREUR CHECK-IN", "❌", "orange", banner=False)
            keyboard = [
                [InlineKeyboardButton("🔙 Retour à ma commande", callback_data="click_collect_submit_info_back")],
                [InlineKeyboardButton("🏠 Accueil", callback_data="cmd_shop")],
            ]
            await safe_edit_message_text(
                query,
                f"{header}\n\n{escape_html(err or 'Erreur inconnue')}",
                InlineKeyboardMarkup(keyboard),
                "HTML",
            )
            await query.answer("❌ Échec du check-in", show_alert=True)
        return

    # Gestion de "Moi" - affichage du profil avec soldes et bannière
    if callback_data == "cmd_moi":
        points = get_user_points(user_id)
        first_name = escape_html(sanitize_text(user.first_name, 64)) if user.first_name else "N/A"
        username = escape_html(user.username or 'N/A')
        
        # Construire le message avec le nouveau système esthétique
        header = format_header_rich("MON PROFIL", "👤", "purple", banner=False)
        
        # Informations avec cards stylisées
        info_section = format_section_rich("Informations", "", "📊", "info")
        info_content = (
            f"{format_info_card('ID', f'<code>{user_id}</code>', '🆔')}\n"
            f"{format_info_card('Nom', first_name, '👤')}\n"
            f"{format_info_card('Username', f'@{username}', '📱')}"
        )
        
        # Solde mis en évidence
        solde_box = format_highlight_box(f"{points} points", "💎", "gold")

        message = f"{header}\n\n{info_section}\n{info_content}\n\n{solde_box}"
        keyboard = []
        keyboard += [
            [InlineKeyboardButton("📜 Historique", callback_data="cmd_historique")],
            [InlineKeyboardButton("🔙 Retour au shop", callback_data="cmd_shop")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Utiliser la fonction helper pour gérer les transitions et changements de bannière
        try:
            file_id = await get_or_upload_profil_banner(context)
            await edit_or_send_message(update, message, reply_markup, "HTML", file_id)

            if file_id:
                logger.info(f"Profil affiché avec bannière pour l'utilisateur {user_id}")
            else:
                logger.info(f"Profil affiché (texte) pour l'utilisateur {user_id}")

        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage du profil: {e}")
        return

    # Gestion de "Historique" (profil) — choix entre points ou cartes
    if callback_data == "cmd_historique":
        header = format_header_rich("HISTORIQUE", "📜", "purple", banner=False)
        msg = f"{header}\n\nChoisissez le type d'historique à consulter."
        keyboard = [
            [InlineKeyboardButton("💰 Historique argent", callback_data="hist_points")],
            [InlineKeyboardButton("🎴 Historique cartes", callback_data="hist_cartes")],
            [InlineKeyboardButton("🛒 Historique Click&Collect", callback_data="hist_click")],
            [InlineKeyboardButton("🔙 Retour au profil", callback_data="cmd_moi")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await safe_edit_message_text(query, msg, reply_markup, "HTML")
        except TelegramError as e:
            logger.error(f"Erreur affichage choix historique: {e}")
        return

    # ——— Historique POINTS (achats de points) ———
    if callback_data == "hist_points":
        PAGE_SIZE = 5
        context.user_data["hist_points_page"] = 0
        total = get_user_payment_history_count(user_id)
        rows = get_user_payment_history(user_id, limit=PAGE_SIZE, offset=0)
        header = format_header_rich("HISTORIQUE ARGENT", "💰", "purple", banner=False)
        count_line = f"\n📋 <b>{total}</b> commande(s) au total.\n" if total else "\n"
        if not rows:
            msg = f"{header}\n\nAucun achat d'argent enregistré."
            keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="cmd_historique")]]
        else:
            msg = f"{header}{count_line}\nSélectionnez une commande pour voir le détail (date, argent, prix)."
            keyboard = _build_hist_points_keyboard(rows, user_id, page=0, page_size=PAGE_SIZE)
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await safe_edit_message_text(query, msg, reply_markup, "HTML")
        except TelegramError as e:
            logger.error(f"Erreur affichage historique points: {e}")
        return

    if callback_data.startswith("hist_points_page_"):
        try:
            page = int(callback_data.replace("hist_points_page_", "", 1))
        except (ValueError, IndexError):
            return
        PAGE_SIZE = 5
        context.user_data["hist_points_page"] = page
        offset = page * PAGE_SIZE
        total = get_user_payment_history_count(user_id)
        rows = get_user_payment_history(user_id, limit=PAGE_SIZE, offset=offset)
        header = format_header_rich("HISTORIQUE ARGENT", "💰", "purple", banner=False)
        count_line = f"\n📋 <b>{total}</b> commande(s) au total.\n" if total else "\n"
        if not rows:
            msg = f"{header}{count_line}\nAucune commande sur cette page."
            keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="cmd_historique")]]
        else:
            msg = f"{header}{count_line}\nSélectionnez une commande pour voir le détail."
            keyboard = _build_hist_points_keyboard(rows, user_id, page=page, page_size=PAGE_SIZE)
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await safe_edit_message_text(query, msg, reply_markup, "HTML")
        except TelegramError as e:
            logger.error(f"Erreur affichage historique points page: {e}")
        return

    if callback_data.startswith("hist_points_detail_"):
        try:
            payment_id = int(callback_data.replace("hist_points_detail_", "", 1))
        except (ValueError, IndexError):
            return
        payment = get_pending_payment(payment_id)
        if not payment or payment[1] != user_id:
            return
        _id, _user_id, points, price, photo_file_id, created_at, status, conf_msg_id = payment
        try:
            if hasattr(created_at, "strftime"):
                date_exact = created_at.strftime("%d/%m/%Y à %H:%M")
            else:
                date_exact = str(created_at)[:16].replace("T", " ")
        except Exception:
            date_exact = str(created_at)
        price_str = f"{price:.2f}€" if price is not None else "—"
        page = context.user_data.get("hist_points_page", 0)
        header = format_header_rich("DÉTAIL COMMANDE ARGENT", "💰", "purple", banner=False)
        detail_msg = (
            f"{header}\n\n"
            f"📅 <b>Date :</b> {escape_html(str(date_exact))}\n"
            f"💎 <b>Argent :</b> {points}\n"
            f"💳 <b>Prix :</b> {price_str}"
        )
        keyboard = [[InlineKeyboardButton("🔙 Retour à la liste", callback_data=f"hist_points_page_{page}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await safe_edit_message_text(query, detail_msg, reply_markup, "HTML")
        except TelegramError as e:
            logger.error(f"Erreur affichage détail historique points: {e}")
        return

    # ——— Historique CARTES ———
    if callback_data == "hist_cartes":
        PAGE_SIZE = 5
        context.user_data["hist_cartes_page"] = 0
        total = get_user_card_history_count(user_id)
        rows = get_user_card_history(user_id, limit=PAGE_SIZE, offset=0)
        header = format_header_rich("HISTORIQUE CARTES", "🎴", "purple", banner=False)
        count_line = f"\n📋 <b>{total}</b> commande(s) au total.\n" if total else "\n"
        if not rows:
            msg = f"{header}\n\nAucun achat de carte enregistré."
            keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="cmd_historique")]]
        else:
            msg = f"{header}{count_line}\nSélectionnez une commande pour voir le détail (carte, points, date)."
            keyboard = _build_hist_cartes_keyboard(rows, user_id, page=0, page_size=PAGE_SIZE)
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await safe_edit_message_text(query, msg, reply_markup, "HTML")
        except TelegramError as e:
            logger.error(f"Erreur affichage historique cartes: {e}")
        return

    if callback_data.startswith("hist_cartes_page_"):
        try:
            page = int(callback_data.replace("hist_cartes_page_", "", 1))
        except (ValueError, IndexError):
            return
        PAGE_SIZE = 5
        context.user_data["hist_cartes_page"] = page
        offset = page * PAGE_SIZE
        total = get_user_card_history_count(user_id)
        rows = get_user_card_history(user_id, limit=PAGE_SIZE, offset=offset)
        header = format_header_rich("HISTORIQUE CARTES", "🎴", "purple", banner=False)
        count_line = f"\n📋 <b>{total}</b> commande(s) au total.\n" if total else "\n"
        if not rows:
            msg = f"{header}{count_line}\nAucune commande sur cette page."
            keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="cmd_historique")]]
        else:
            msg = f"{header}{count_line}\nSélectionnez une commande pour voir le détail."
            keyboard = _build_hist_cartes_keyboard(rows, user_id, page=page, page_size=PAGE_SIZE)
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await safe_edit_message_text(query, msg, reply_markup, "HTML")
        except TelegramError as e:
            logger.error(f"Erreur affichage historique cartes page: {e}")
        return

    if callback_data.startswith("hist_cartes_detail_"):
        try:
            record_id = int(callback_data.replace("hist_cartes_detail_", "", 1))
        except (ValueError, IndexError):
            return
        row = get_card_purchase_by_id(record_id)
        if not row or row[1] != user_id:
            return
        _id, _user_id, card_number, points, created_at, cust_id = row
        try:
            if hasattr(created_at, "strftime"):
                date_exact = created_at.strftime("%d/%m/%Y à %H:%M")
            else:
                date_exact = str(created_at)[:16].replace("T", " ")
        except Exception:
            date_exact = str(created_at)
        page = context.user_data.get("hist_cartes_page", 0)
        header = format_header_rich("DÉTAIL COMMANDE CARTE", "🎴", "purple", banner=False)
        detail_msg = (
            f"{header}\n\n"
            f"📅 <b>Date :</b> {escape_html(str(date_exact))}\n"
            f"🎴 <b>Carte :</b> <code>{escape_html(str(card_number))}</code>\n"
            f"💎 <b>Points :</b> {points}"
        )
        keyboard = [[InlineKeyboardButton("🔙 Retour à la liste", callback_data=f"hist_cartes_page_{page}")]]
        # Admin : bouton infos complètes si customer_id (récup depuis kfc_storage)
        if role == "admin" and cust_id:
            keyboard.insert(0, [InlineKeyboardButton("📋 Afficher les infos complètes", callback_data=f"card_info_full_{record_id}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await safe_edit_message_text(query, detail_msg, reply_markup, "HTML")
        except TelegramError as e:
            logger.error(f"Erreur affichage détail historique cartes: {e}")
        return

    # ——— Historique CLICK&COLLECT (submit ou +) ———
    if callback_data == "hist_click":
        PAGE_SIZE = 5
        context.user_data["hist_click_page"] = 0
        total = get_user_click_history_count(user_id)
        rows = get_user_click_history(user_id, limit=PAGE_SIZE, offset=0)
        header = format_header_rich("HISTORIQUE CLICK&COLLECT", "🛒", "purple", banner=False)
        count_line = f"\n📋 <b>{total}</b> commande(s) au total.\n" if total else "\n"
        if not rows:
            msg = f"{header}\n\nAucune commande Click&Collect soumise."
            keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="cmd_historique")]]
        else:
            msg = f"{header}{count_line}\nSélectionnez une commande pour voir le détail (restaurant, statut, total)."
            keyboard = _build_hist_click_keyboard(rows, user_id, page=0, page_size=PAGE_SIZE)
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await safe_edit_message_text(query, msg, reply_markup, "HTML")
        except TelegramError as e:
            logger.error(f"Erreur affichage historique click: {e}")
        return

    if callback_data.startswith("hist_click_page_"):
        try:
            page = int(callback_data.replace("hist_click_page_", "", 1))
        except (ValueError, IndexError):
            return
        PAGE_SIZE = 5
        context.user_data["hist_click_page"] = page
        offset = page * PAGE_SIZE
        total = get_user_click_history_count(user_id)
        rows = get_user_click_history(user_id, limit=PAGE_SIZE, offset=offset)
        header = format_header_rich("HISTORIQUE CLICK&COLLECT", "🛒", "purple", banner=False)
        count_line = f"\n📋 <b>{total}</b> commande(s) au total.\n" if total else "\n"
        if not rows:
            msg = f"{header}{count_line}\nAucune commande sur cette page."
            keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="cmd_historique")]]
        else:
            msg = f"{header}{count_line}\nSélectionnez une commande pour voir le détail."
            keyboard = _build_hist_click_keyboard(rows, user_id, page=page, page_size=PAGE_SIZE)
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await safe_edit_message_text(query, msg, reply_markup, "HTML")
        except TelegramError as e:
            logger.error(f"Erreur affichage historique click page: {e}")
        return

    if callback_data.startswith("hist_click_detail_"):
        try:
            record_id = int(callback_data.replace("hist_click_detail_", "", 1))
        except (ValueError, IndexError):
            return
        row = get_click_history_by_id(record_id)
        if not row:
            return
        (
            _id,
            row_user_id,
            panier_id,
            order_uuid,
            order_number,
            confirmation_url,
            status,
            store_id,
            store_name,
            store_city,
            account_id,
            telegram_user,
            email,
            phone_number,
            last_name,
            first_name,
            date_of_birth,
            total_points,
            submitted_at,
        ) = row
        if row_user_id != user_id and role != "admin":
            return
        try:
            if hasattr(submitted_at, "strftime"):
                date_exact = submitted_at.strftime("%d/%m/%Y à %H:%M")
            else:
                date_exact = str(submitted_at)[:16].replace("T", " ")
        except Exception:
            date_exact = str(submitted_at)

        items = get_click_history_items(record_id)
        items_lines = []
        for name, cost, qty, line_total in items[:12]:
            items_lines.append(
                f"• {escape_html(sanitize_display_name(str(name or 'Article')))} x{qty} ({line_total} pts)"
            )
        if len(items) > 12:
            items_lines.append(f"... et {len(items) - 12} autre(s)")
        items_txt = "\n".join(items_lines) if items_lines else "—"

        status_txt = escape_html(str(status or "N/A"))
        store_txt = escape_html(str(store_name or "KFC"))
        city_txt = escape_html(str(store_city or "N/A"))
        order_txt = escape_html(str(order_number or "N/A"))
        first_name_txt = escape_html(str(first_name or "N/A"))
        last_name_txt = escape_html(str(last_name or "N/A"))
        page = context.user_data.get("hist_click_page", 0)
        header = format_header_rich("DÉTAIL COMMANDE CLICK&COLLECT", "🛒", "purple", banner=False)
        detail_msg = (
            f"{header}\n\n"
            f"📅 <b>Date :</b> {escape_html(str(date_exact))}\n"
            f"🆔 <b>Commande :</b> <code>{order_txt}</code>\n"
            f"👤 <b>Client :</b> {first_name_txt} {last_name_txt}\n"
            f"📌 <b>Statut :</b> {status_txt}\n"
            f"🍗 <b>KFC :</b> {store_txt} ({city_txt})\n"
            f"💎 <b>Total :</b> {total_points} pts\n"
            f"🔗 <b>Lien :</b> {escape_html(str(confirmation_url or 'N/A'))}\n\n"
            f"<b>Articles :</b>\n{items_txt}"
        )
        if role == "admin":
            detail_msg += (
                f"\n\n<b>Infos admin :</b>\n"
                f"👤 User ID : <code>{row_user_id}</code>\n"
                f"🧾 Order UUID : <code>{escape_html(str(order_uuid or 'N/A'))}</code>\n"
                f"🏬 Store ID : <code>{escape_html(str(store_id or 'N/A'))}</code>\n"
                f"🔐 Account ID : <code>{escape_html(str(account_id or 'N/A'))}</code>\n"
                f"📱 Telegram user : {escape_html(str(telegram_user or 'N/A'))}\n"
                f"📧 Email : <code>{escape_html(str(email or 'N/A'))}</code>\n"
                f"☎️ Téléphone : {escape_html(str(phone_number or 'N/A'))}\n"
                f"🧍 Nom : {escape_html(str(last_name or 'N/A'))}\n"
                f"🧍 Prénom : {escape_html(str(first_name or 'N/A'))}\n"
                f"🎂 Naissance : {escape_html(str(date_of_birth or 'N/A'))}"
            )
        keyboard = [[InlineKeyboardButton("🔙 Retour à la liste", callback_data=f"hist_click_page_{page}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await safe_edit_message_text(query, detail_msg, reply_markup, "HTML")
        except TelegramError as e:
            logger.error(f"Erreur affichage détail historique click: {e}")
        return

    # Infos complètes carte (admin) — récup depuis kfc_storage
    if callback_data.startswith("card_info_full_"):
        try:
            record_id = int(callback_data.replace("card_info_full_", "", 1))
        except (ValueError, IndexError):
            return
        row = get_card_purchase_by_id(record_id)
        if not row:
            return
        _id, _user_id, card_number, points, created_at, cust_id = row
        if _user_id != user_id and role != "admin":
            return
        if not cust_id:
            return
        storage = get_kfc_storage_by_customer_id(cust_id)
        if not storage:
            return
        header = format_header_rich("INFOS COMPLÈTES CARTE", "📋", "info", banner=False)
        expired_str = str(storage.get("expired_at") or "")[:19].replace("T", " ") if storage.get("expired_at") else "—"
        full_msg = (
            f"{header}\n\n"
            f"🎴 <b>Carte :</b> <code>{escape_html(str(storage.get('carte') or '—'))}</code>\n"
            f"💎 <b>Points :</b> {storage.get('point') or points}\n"
            f"🆔 <b>Customer ID :</b> <code>{escape_html(str(storage.get('customer_id') or '—'))}</code>\n"
            f"📌 <b>ID :</b> <code>{escape_html(str(storage.get('id') or '—'))}</code>\n"
            f"📅 <b>Expiration :</b> {escape_html(expired_str or '—')}\n"
            f"📧 <b>Email :</b> <code>{escape_html(str(storage.get('email') or '—'))}</code>\n"
            f"🔑 <b>Password :</b> <code>{escape_html(str(storage.get('password') or '—'))}</code>\n"
            f"👤 <b>Nom :</b> {escape_html(str(storage.get('nom') or '—'))}\n"
            f"👤 <b>Prénom :</b> {escape_html(str(storage.get('prenom') or '—'))}\n"
            f"📱 <b>Numéro :</b> {escape_html(str(storage.get('numero') or '—'))}\n"
            f"🎂 <b>Date naissance :</b> {escape_html(str(storage.get('ddb') or '—'))}"
        )
        keyboard = [[InlineKeyboardButton("🔙 Retour à la carte", callback_data=f"card_info_short_{record_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await safe_edit_message_text(query, full_msg, reply_markup, "HTML")
        except TelegramError as e:
            logger.error(f"Erreur affichage infos complètes carte: {e}")
        return

    # Retour à la vue courte de la carte (depuis infos complètes)
    if callback_data.startswith("card_info_short_"):
        try:
            record_id = int(callback_data.replace("card_info_short_", "", 1))
        except (ValueError, IndexError):
            return
        row = get_card_purchase_by_id(record_id)
        if not row:
            return
        _id, _user_id, card_number, points, created_at, cust_id = row
        if _user_id != user_id and role != "admin":
            return
        success_header = format_header_rich("ACHAT RÉUSSI", "", "success", banner=False)
        short_msg = (
            f"{success_header}\n\n"
            f"🎴 <b>Carte :</b> <code>{escape_html(str(card_number))}</code>\n"
            f"💎 <b>Points :</b> {points}\n"
        )
        has_full = cust_id and role == "admin"
        if has_full:
            keyboard = [
                [InlineKeyboardButton("📋 Afficher les infos complètes", callback_data=f"card_info_full_{record_id}")],
                [InlineKeyboardButton("🔙 Retour à la boutique", callback_data="cmd_boutique")],
            ]
        else:
            keyboard = [[InlineKeyboardButton("🔙 Retour à la boutique", callback_data="cmd_boutique")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await safe_edit_message_text(query, short_msg, reply_markup, "HTML")
        except TelegramError as e:
            logger.error(f"Erreur retour vue courte carte: {e}")
        return

    # Gestion de /config pour l'admin
    if callback_data == "cmd_config" and role == "admin":
        message = "⚙️ **Configuration Admin**\n\nSélectionnez une option :"
        keyboard = [
            [InlineKeyboardButton("👤 Rôle", callback_data="config_role")],
            [InlineKeyboardButton("💳 Paiement", callback_data="config_payement")],
            [InlineKeyboardButton("💰 Argent", callback_data="config_points")],
            [InlineKeyboardButton("🎴 Carte", callback_data="config_carte")],
            [InlineKeyboardButton("📢 Canal", callback_data="config_canal")],
            [InlineKeyboardButton("📢 Annonce", callback_data="config_annonce")],
            [InlineKeyboardButton("📦 Storage", callback_data="config_storage")],
            [InlineKeyboardButton("🛑 Arrêt", callback_data="config_arret")],
            [InlineKeyboardButton("🔙 Retour", callback_data="cmd_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage du menu config: {e}")
        return
    
    # Lancer le mode création de compte (admin uniquement)
    if callback_data == "admin_create_account" and role == "admin":
        # Nettoyer d'éventuels états précédents
        context.user_data.pop('admin_create_account_mode', None)
        context.user_data['admin_create_account_mode'] = True

        message = (
            "🆕 <b>Création automatique de compte</b>\n\n"
            "Veuillez envoyer <b>une carte de 6 caractères</b> en hexadécimal <b>MAJUSCULE</b> (0-9, A-F).\n\n"
            "Exemple : <code>1A2B3C</code>\n\n"
            "Le bot va ensuite créer un compte KFC avec des informations aléatoires "
            "puis tenter d'associer cette carte au compte."
        )
        keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="menu_principal")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage du mode création de compte: {e}")
        return
    
    # Gestion de config_role (gestion des rôles)
    if callback_data == "config_role" and role == "admin":
        # Nettoyer les états précédents
        context.user_data.pop('role_list_mode', None)
        context.user_data.pop('role_add_mode', None)
        context.user_data.pop('role_remove_mode', None)
        context.user_data.pop('role_selected', None)
        context.user_data.pop('reduction_edit_mode', None)
        context.user_data.pop('reduction_user_id', None)
        context.user_data.pop('vendeur_reduction_mode', None)
        context.user_data.pop('vendeur_user_id', None)
        
        # Récupérer les statistiques des rôles
        stats = get_role_statistics()
        
        message = (
            "👤 **Configuration des Rôles**\n\n"
            f"📊 **Statistiques:**\n"
            f"👑 Admin: {stats.get('admin', 0)}\n"
            f"💼 Vendeur: {stats.get('vendeur', 0)}\n"
            f"🛡️ Modérateur: {stats.get('moderator', 0)}\n"
            f"👥 User: {stats.get('user', 0)}\n\n"
            "Sélectionnez une action :"
        )
        keyboard = [
            [InlineKeyboardButton("📋 Liste des Vendeurs", callback_data="role_list_vendeur")],
            [InlineKeyboardButton("📋 Liste des Modérateurs", callback_data="role_list_moderator")],
            [InlineKeyboardButton("💰 Liste des personnes avec réduction", callback_data="role_list_reduction")],
            [InlineKeyboardButton("➕ Ajouter un rôle", callback_data="role_add_select")],
            [InlineKeyboardButton("➖ Retirer un rôle", callback_data="role_remove_select")],
            [InlineKeyboardButton("💰 Modifier Réduction", callback_data="role_reduction_edit")],
            [InlineKeyboardButton("🔙 Retour", callback_data="cmd_config")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de la config role: {e}")
        return
    
    # Gestion de l'affichage de la liste des rôles
    if callback_data in {"role_list_vendeur", "role_list_moderator"} and role == "admin":
        role_type = "vendeur" if callback_data == "role_list_vendeur" else "moderator"
        users = get_users_by_role(role_type)
        
        if not users:
            message = f"📋 **Liste des {role_type.capitalize()}s**\n\nAucun {role_type} trouvé."
        else:
            role_emoji = "💼" if role_type == "vendeur" else "🛡️"
            message = f"{role_emoji} **Liste des {role_type.capitalize()}s**\n\n"
            # Limiter à 50 utilisateurs pour éviter les messages trop longs
            for idx, (uid, balance) in enumerate(users[:50], 1):
                message += f"{idx}. `{uid}` (Balance: {balance} points)\n"
            if len(users) > 50:
                message += f"\n... et {len(users) - 50} autres."
        
        keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="config_role")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de la liste des rôles: {e}")
        return
    
    # Gestion de l'affichage de la liste des personnes avec réduction
    if callback_data == "role_list_reduction" and role == "admin":
        users = get_users_with_reduction()
        
        if not users:
            message = "💰 **Liste des personnes avec réduction**\n\nAucune personne avec réduction trouvée."
        else:
            message = "💰 **Liste des personnes avec réduction**\n\n"
            # Limiter à 50 utilisateurs pour éviter les messages trop longs
            for idx, (uid, reduction_rate, user_role) in enumerate(users[:50], 1):
                role_display = user_role.capitalize()
                if role_display == "Vendeur":
                    role_display = "💼 Vendeur"
                elif role_display == "Moderator":
                    role_display = "🛡️ Modérateur"
                elif role_display == "User":
                    role_display = "👤 User"
                reduction_fmt = f"{float(reduction_rate):.2f}".rstrip('0').rstrip('.') or "0"
                message += f"{idx}. `{uid}` - {reduction_fmt}% - {role_display}\n"
            if len(users) > 50:
                message += f"\n... et {len(users) - 50} autres."
        
        keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="config_role")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de la liste des personnes avec réduction: {e}")
        return
    
    # Gestion de l'ajout de rôle - sélection du type
    if callback_data == "role_add_select" and role == "admin":
        message = (
            "➕ **Ajouter un rôle**\n\n"
            "Sélectionnez le type de rôle à ajouter :"
        )
        keyboard = [
            [InlineKeyboardButton("💼 Vendeur", callback_data="role_add_vendeur")],
            [InlineKeyboardButton("🛡️ Modérateur", callback_data="role_add_moderator")],
            [InlineKeyboardButton("🔙 Retour", callback_data="config_role")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage du menu d'ajout de rôle: {e}")
        return
    
    # Gestion de l'ajout de rôle - activation du mode
    # Gestion de la modification de réduction
    if callback_data == "role_reduction_edit" and role == "admin":
        context.user_data['reduction_edit_mode'] = True
        message = (
            "💰 **Modifier la Réduction d'un Utilisateur**\n\n"
            "📝 Envoyez l'ID de l'utilisateur (uniquement le nombre).\n\n"
            "💡 Pour obtenir l'ID d'un utilisateur, vous pouvez demander à la personne d'utiliser le bot @userinfobot ou vérifier dans les logs."
        )
        keyboard = [[InlineKeyboardButton("❌ Annuler", callback_data="config_role")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'activation du mode modification de réduction: {e}")
        return
    
    # Gestion du callback pour passer la réduction (0%)
    if callback_data == "vendeur_reduction_skip" and role == "admin":
        user_id_vendeur = context.user_data.get('vendeur_user_id')
        if user_id_vendeur:
            if set_user_reduction(user_id_vendeur, 0):
                context.user_data.pop('vendeur_reduction_mode', None)
                await query.edit_message_text(
                    f"✅ **Vendeur configuré !**\n\n"
                    f"👤 Vendeur: `{user_id_vendeur}`\n"
                    f"💰 Réduction: **0%**",
                    parse_mode="Markdown"
                )
                logger.info(f"Réduction définie à 0% pour le nouveau vendeur {user_id_vendeur} par l'admin {user_id}")
            else:
                context.user_data.pop('vendeur_reduction_mode', None)
                context.user_data.pop('vendeur_user_id', None)
                context.user_data.pop('role_add_mode', None)
                context.user_data.pop('role_selected', None)
        else:
            context.user_data.pop('vendeur_reduction_mode', None)
            context.user_data.pop('vendeur_user_id', None)
            context.user_data.pop('role_add_mode', None)
            context.user_data.pop('role_selected', None)
        return
    
    if callback_data in {"role_add_vendeur", "role_add_moderator"} and role == "admin":
        role_type = "vendeur" if callback_data == "role_add_vendeur" else "moderator"
        context.user_data['role_add_mode'] = True
        context.user_data['role_selected'] = role_type
        
        role_emoji = "💼" if role_type == "vendeur" else "🛡️"
        message = (
            f"{role_emoji} **Ajouter un {role_type.capitalize()}**\n\n"
            "📝 Envoyez l'ID de l'utilisateur (uniquement le nombre).\n\n"
            "💡 Pour obtenir l'ID d'un utilisateur, vous pouvez demander à la personne d'utiliser le bot @userinfobot ou vérifier dans les logs."
        )
        keyboard = [[InlineKeyboardButton("❌ Annuler", callback_data="config_role")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'activation du mode ajout de rôle: {e}")
        return
    
    # Gestion de la suppression de rôle - sélection du type
    if callback_data == "role_remove_select" and role == "admin":
        message = (
            "➖ **Retirer un rôle**\n\n"
            "Sélectionnez le type de rôle à retirer :"
        )
        keyboard = [
            [InlineKeyboardButton("💼 Vendeur", callback_data="role_remove_vendeur")],
            [InlineKeyboardButton("🛡️ Modérateur", callback_data="role_remove_moderator")],
            [InlineKeyboardButton("🔙 Retour", callback_data="config_role")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage du menu de suppression de rôle: {e}")
        return
    
    # Gestion de la suppression de rôle - activation du mode
    if callback_data in {"role_remove_vendeur", "role_remove_moderator"} and role == "admin":
        role_type = "vendeur" if callback_data == "role_remove_vendeur" else "moderator"
        context.user_data['role_remove_mode'] = True
        context.user_data['role_selected'] = role_type
        
        role_emoji = "💼" if role_type == "vendeur" else "🛡️"
        message = (
            f"{role_emoji} **Retirer le rôle {role_type.capitalize()}**\n\n"
            "📝 Envoyez l'ID de l'utilisateur (uniquement le nombre)."
        )
        keyboard = [[InlineKeyboardButton("❌ Annuler", callback_data="config_role")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'activation du mode suppression de rôle: {e}")
        return
    
    # Gestion de config_payement (URL de paiement)
    if callback_data == "config_payement" and role == "admin":
        # Nettoyer config_edit si présent (annulation d'édition)
        context.user_data.pop('config_edit', None)
        
        payment_url = get_payment_url()
        
        # Compter les transactions en attente
        pending_count = get_pending_payments_count()
        
        message = (
            "💳 **Configuration du Paiement**\n\n"
            f"🔗 URL de paiement actuelle: **{payment_url}**\n\n"
            f"📊 Transactions en attente: **{pending_count}**\n\n"
            "Sélectionnez une action :"
        )
        keyboard = [
            [InlineKeyboardButton("🔗 Modifier l'URL de paiement", callback_data="config_payment_url_edit")],
            [InlineKeyboardButton("🔄 Réinitialiser toutes les transactions", callback_data="config_reset_payments")],
            [InlineKeyboardButton("🔙 Retour", callback_data="cmd_config")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de la config payement: {e}")
        return
    
    # Gestion de la réinitialisation des transactions
    if callback_data == "config_reset_payments" and role == "admin":
        pending_count = get_pending_payments_count()
        
        if pending_count == 0:
            message = (
                "🔄 **Réinitialisation des Transactions**\n\n"
                "✅ Aucune transaction en attente à réinitialiser."
            )
            keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="config_payement")]]
        else:
            message = (
                "🔄 **Réinitialisation des Transactions**\n\n"
                f"⚠️ **Attention !**\n\n"
                f"Il y a actuellement **{pending_count} transaction(s)** en attente.\n\n"
                f"Cette action va **annuler toutes les transactions en attente** et les passer en statut 'cancelled'.\n\n"
                f"Les utilisateurs concernés devront créer une nouvelle transaction.\n\n"
                f"Êtes-vous sûr de vouloir continuer ?"
            )
            keyboard = [
                [InlineKeyboardButton("✅ Confirmer la réinitialisation", callback_data="config_reset_payments_confirm")],
                [InlineKeyboardButton("❌ Annuler", callback_data="config_payement")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de la confirmation de réinitialisation: {e}")
        return
    
    # Confirmation de la réinitialisation
    if callback_data == "config_reset_payments_confirm" and role == "admin":
        rows_affected = reset_all_pending_payments()
        
        if rows_affected > 0:
            message = (
                "✅ **Réinitialisation effectuée**\n\n"
                f"**{rows_affected} transaction(s)** ont été réinitialisée(s).\n\n"
                f"Toutes les transactions en attente ont été annulées."
            )
            logger.info(f"Réinitialisation de {rows_affected} transaction(s) effectuée par l'admin {user_id}")
        else:
            message = (
                "ℹ️ **Aucune transaction à réinitialiser**\n\n"
                "Il n'y avait aucune transaction en attente."
            )
        
        keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="config_payement")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage du résultat de réinitialisation: {e}")
        return
    
    # Gestion de config_points (min, max)
    if callback_data == "config_points" and role == "admin":
        # Nettoyer config_edit si présent (annulation d'édition)
        context.user_data.pop('config_edit', None)
        
        point_min = get_argent_min()
        point_max = get_argent_max()
        
        message = (
            "💰 **Configuration de l'argent**\n\n"
            f"📊 Minimum: **{point_min} argent**\n"
            f"📈 Maximum: **{point_max} argent**\n\n"
            "Sélectionnez un paramètre à modifier :"
        )
        keyboard = [
            [InlineKeyboardButton("📊 Modifier le minimum", callback_data="config_min_edit")],
            [InlineKeyboardButton("📈 Modifier le maximum", callback_data="config_max_edit")],
            [InlineKeyboardButton("🔙 Retour", callback_data="cmd_config")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de la config points: {e}")
        return
    
    # Gestion de config_carte (marge + réduction carte)
    if callback_data == "config_carte" and role == "admin":
        # Nettoyer config_edit si présent (annulation d'édition)
        context.user_data.pop('config_edit', None)
        
        card_margin = get_card_margin()
        prix_carte = get_prix_carte()
        
        message = (
            "🎴 **Configuration des Cartes**\n\n"
            f"📊 Marge actuelle: **{card_margin} points**\n"
            f"💰 Prix carte (shop Carte): **{prix_carte:.2f} €**\n\n"
            "La marge définit le nombre de points supplémentaires autorisés lors de la recherche d'une carte.\n"
            f"Par exemple, si un utilisateur demande 500 points avec une marge de {card_margin}, "
            f"le système cherchera une carte entre 500 et {500 + card_margin} points.\n\n"
            "Le prix carte s'applique au shop « Carte » (en euros).\n\n"
            "Sélectionnez une action :"
        )
        keyboard = [
            [InlineKeyboardButton("📊 Modifier la marge", callback_data="config_card_margin_edit")],
            [InlineKeyboardButton("💰 Modifier le prix carte", callback_data="config_prix_carte_edit")],
            [InlineKeyboardButton("🔙 Retour", callback_data="cmd_config")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de la config carte: {e}")
        return
    
    # Gestion de config_canal (canal staff et threads)
    if callback_data == "config_canal" and role == "admin":
        # Nettoyer config_edit si présent (annulation d'édition)
        context.user_data.pop('config_edit', None)
        
        staff_channel = get_staff_channel_id() or "Non configuré"
        staff_thread_payment = get_staff_thread_payment()
        staff_thread_payment_str = str(staff_thread_payment) if staff_thread_payment else "Non configuré"
        staff_thread_entretien = get_staff_thread_entretien()
        staff_thread_entretien_str = str(staff_thread_entretien) if staff_thread_entretien else "Non configuré"
        staff_thread_demande_access = get_staff_thread_demande_access()
        staff_thread_demande_access_str = str(staff_thread_demande_access) if staff_thread_demande_access else "Non configuré"

        message = (
            "📢 **Configuration du Canal Staff**\n\n"
            f"📢 Canal Staff: `{staff_channel}`\n"
            f"🧵 Thread Paiement: `{staff_thread_payment_str}`\n"
            f"🔧 Thread Entretien: `{staff_thread_entretien_str}`\n"
            f"🔐 Thread Demande d'accès: `{staff_thread_demande_access_str}`\n\n"
            "Sélectionnez un paramètre à modifier :"
        )
        keyboard = [
            [InlineKeyboardButton("📢 Modifier le Canal Staff", callback_data="config_staff_channel_edit")],
            [InlineKeyboardButton("🧵 Modifier le Thread Paiement", callback_data="config_staff_thread_payment_edit")],
            [InlineKeyboardButton("🔧 Modifier le Thread Entretien", callback_data="config_staff_thread_entretien_edit")],
            [InlineKeyboardButton("🔐 Modifier le Thread Demande d'accès", callback_data="config_staff_thread_demande_access_edit")],
            [InlineKeyboardButton("🔙 Retour", callback_data="cmd_config")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de la config canal: {e}")
        return
    
    # Gestion de config_annonce (gestion de l'annonce)
    if callback_data == "config_annonce" and role == "admin":
        # Nettoyer config_edit si présent (annulation d'édition)
        context.user_data.pop('config_edit', None)
        context.user_data.pop('config_announcement_edit', None)
        
        announcement_text = get_announcement_text()
        announcement_photo = get_announcement_photo()
        
        # Afficher un aperçu de l'annonce actuelle
        preview_text = announcement_text[:100] + "..." if len(announcement_text) > 100 else announcement_text
        photo_status = "✅ Photo configurée" if announcement_photo else "❌ Aucune photo"
        
        message = (
            "📢 **Configuration de l'Annonce**\n\n"
            f"📝 **Texte actuel:**\n{preview_text}\n\n"
            f"🖼️ **Photo:** {photo_status}\n\n"
            "Sélectionnez une action :"
        )
        keyboard = [
            [InlineKeyboardButton("📝 Modifier le texte", callback_data="config_annonce_text_edit")],
            [InlineKeyboardButton("🖼️ Modifier la photo", callback_data="config_annonce_photo_edit")],
            [InlineKeyboardButton("🗑️ Supprimer la photo", callback_data="config_annonce_photo_delete")],
            [InlineKeyboardButton("🔙 Retour", callback_data="cmd_config")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de la config annonce: {e}")
        return

    # Gestion de config_storage (insertion via API /insert)
    if callback_data == "config_storage" and role == "admin":
        # Nettoyer d'éventuels états précédents
        context.user_data.pop('config_edit', None)
        context.user_data.pop('storage_mode', None)

        # Récupérer les statistiques des cartes (avec gestion d'erreur robuste)
        stats_section = ""
        try:
            logger.info("Tentative de récupération des statistiques KFC...")
            cards_count, avg_points = get_kfc_cards_statistics()
            logger.info(f"Statistiques récupérées: count={cards_count}, avg={avg_points}")
            
            if cards_count is not None and avg_points is not None:
                stats_section = (
                    f"📊 **Statistiques du stock:**\n"
                    f"🎴 Cartes disponibles: **{cards_count}**\n"
                    f"📈 Moyenne des points: **{avg_points:.1f}**\n\n"
                )
            else:
                stats_section = "⚠️ Impossible de récupérer les statistiques du stock.\n\n"
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}", exc_info=True)
            stats_section = "⚠️ Erreur lors de la récupération des statistiques.\n\n"

        # Construire le message de base
        base_message = (
            "📦 **Storage admin - Insertion API**\n\n"
            "Ici, vous pouvez insérer un compte KFC dans la base de données via l'API `/insert`.\n\n"
        )
        
        message = base_message + stats_section + (
            "📝 **Format JSON requis:**\n"
            "```json\n"
            "{\n"
            '  "id": "kfc_account_001",\n'
            '  "carte": "123456",\n'
            '  "point": 500,\n'
            '  "customer_id": "customer_123",\n'
            '  "email": "user@example.com",\n'
            '  "password": "password123",\n'
            '  "nom": "John Doe",\n'
            '  "expired_at": null\n'
            "}\n"
            "```\n\n"
            "**Champs requis:** `id`, `carte` (6 caractères), `point` (>= 0)\n"
            "**Champs optionnels:** `customer_id`, `email`, `password`, `nom`, `expired_at`\n\n"
            "➡️ Envoyez maintenant le **JSON** du compte à insérer."
        )
        
        logger.info(f"Message storage construit (longueur: {len(message)})")
        keyboard = [
            [InlineKeyboardButton("🔙 Retour", callback_data="cmd_config")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Activer le mode storage pour le prochain message texte de l'admin
        context.user_data['storage_mode'] = True

        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage du menu storage: {e}")
            # Fallback: essayer d'envoyer un message simple
            try:
                await query.message.reply_text(
                    "📦 **Storage admin - Insertion API**\n\n"
                    "Ici, vous pouvez insérer un compte KFC dans la base de données via l'API `/insert`.\n\n"
                    "➡️ Envoyez le **JSON** du compte à insérer.",
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            except Exception as e2:
                logger.error(f"Erreur lors de l'envoi du message de fallback: {e2}")
        return
    
    # Gestion de config_arret (arrêt d'urgence)
    if callback_data == "config_arret" and role == "admin":
        # Nettoyer config_edit si présent (annulation d'édition)
        context.user_data.pop('config_edit', None)
        
        emergency_stop_active = is_emergency_stop_active()
        status_emoji = "🔴" if emergency_stop_active else "🟢"
        status_text = "ACTIF" if emergency_stop_active else "INACTIF"
        
        message = (
            "🛑 **Arrêt d'Urgence**\n\n"
            f"État actuel: {status_emoji} **{status_text}**\n\n"
        )
        
        if emergency_stop_active:
            message += (
                "⚠️ Le bot est actuellement en arrêt d'urgence.\n"
                "Toutes les actions sont bloquées pour tous les utilisateurs.\n\n"
                "Sélectionnez une action :"
            )
        else:
            message += (
                "Le bot fonctionne normalement.\n\n"
                "Sélectionnez une action :"
            )
        
        keyboard = []
        if emergency_stop_active:
            keyboard.append([InlineKeyboardButton("🟢 Désactiver l'arrêt d'urgence", callback_data="emergency_stop_disable")])
        else:
            keyboard.append([InlineKeyboardButton("🔴 Activer l'arrêt d'urgence", callback_data="emergency_stop_enable")])
        keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data="cmd_config")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de la config arret: {e}")
        return
    
    # Gestion de l'activation/désactivation de l'arrêt d'urgence
    if callback_data in {"emergency_stop_enable", "emergency_stop_disable"} and role == "admin":
        new_value = "true" if callback_data == "emergency_stop_enable" else "false"
        if update_config_value("emergency_stop", new_value):
            action = "activé" if new_value == "true" else "désactivé"
            status_bot = "en arrêt d'urgence" if new_value == "true" else "opérationnel"
            message = f"✅ **Arrêt d'urgence {action}**\n\nLe bot est maintenant {status_bot}."
            logger.warning(f"Arrêt d'urgence {action} par l'admin {user_id}")
        else:
            message = "❌ Erreur lors de la modification de l'arrêt d'urgence."
        
        keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="config_arret")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de la modification de l'arrêt d'urgence: {e}")
        return
    
    # Gestion de l'interface d'achat de points : d'abord choix de la formule
    if callback_data == "cmd_acheter_points":
        await show_points_formula_choice(update, context)
        return
    
    # Retour au choix de formule (depuis l'interface +/-)
    if callback_data == "points_formula_choice":
        await show_points_formula_choice(update, context)
        return

    # Choix d'une formule (solo, duo, etc.) -> ouvrir l'interface +/- avec le nombre de points par défaut
    if callback_data.startswith("points_formula_"):
        formula = callback_data.replace("points_formula_", "", 1)
        default_points = POINTS_FORMULA_DEFAULTS.get(formula)
        if default_points is not None:
            await show_points_purchase_interface(update, context, selected_points=default_points)
        else:
            await show_points_formula_choice(update, context)
        return
    
    # Gestion des boutons +/- pour les points (debouncing strict pour éviter le freeze Telegram)
    if callback_data.startswith("points_inc_") or callback_data.startswith("points_dec_"):
        # Debouncing : ne traiter qu'un clic toutes les 800ms
        last_click_key = f'points_last_click_{user_id}'
        now = datetime.now().timestamp()
        last_click_time = context.user_data.get(last_click_key, 0)
        
        # Si un clic est arrivé il y a moins de 800ms, répondre mais ne rien faire
        if now - last_click_time < 0.8:
            return  # Telegram a reçu sa réponse, mais on ignore le traitement
        
        # Enregistrer le timestamp de ce clic (seulement si on va le traiter)
        context.user_data[last_click_key] = now
        
        try:
            current_points = int(callback_data.split("_")[-1])
            
            # Récupérer les limites (maintenant en cache, donc rapide)
            point_min = get_point_min()
            point_max = get_point_max()
            
            if callback_data.startswith("points_inc_"):
                new_points = min(point_max, current_points + POINT_INCREMENT)
            else:
                new_points = max(point_min, current_points - POINT_INCREMENT)
            
            # Vérifier si les points ont vraiment changé (évite edit_message_text inutile)
            if new_points == current_points:
                # Déjà à la limite, ne pas modifier le message
                return
            
            # Mettre à jour l'interface
            await show_points_purchase_interface(update, context, new_points)
            
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur lors de l'incrémentation/décrémentation des points: {e}")
        except TelegramError as e:
            # Gérer silencieusement MessageNotModified et rate limit
            error_msg = str(e).lower()
            if "message is not modified" in error_msg or "too many requests" in error_msg:
                # Rate limit ou message déjà modifié, ignorer silencieusement
                pass
            else:
                logger.warning(f"Erreur Telegram lors de la mise à jour des points: {e}")
        return
    
    if callback_data.startswith("points_validate_"):
        try:
            points_to_add = int(callback_data.split("_")[-1])
            point_min = get_point_min()
            point_max = get_point_max()
            
            if points_to_add < point_min or points_to_add > point_max:
                await safe_edit_message_text(
                    query,
                    f"❌ Le montant d'argent doit être entre {point_min} et {point_max}.",
                    create_back_button("shop"),
                    "HTML"
                )
                return
            
            if points_to_add <= 0:
                await safe_edit_message_text(
                    query,
                    "❌ Le montant d'argent doit être supérieur à 0.",
                    create_back_button("shop"),
                    "HTML"
                )
                return
            
            # Nouvelle logique simplifiée: 1€ payé = 1 argent crédité.
            user_reduction = 0.0
            price_initial = float(points_to_add)
            price_euros = float(points_to_add)
            
            # Vérifier que le prix n'est pas négatif (sécurité)
            if price_euros < 0:
                logger.error(f"Prix calculé négatif pour user_id={user_id}, points={points_to_add}, reduction={user_reduction}%, price_initial={price_initial}")
                price_euros = 0.0
            
            # Afficher le résumé de l'achat avec URL de paiement
            payment_url = get_payment_url()
            payment_url_safe = escape_html(sanitize_text(payment_url, 500))
            
            # Construire le message avec le nouveau système esthétique
            header = format_header_rich("RÉSUMÉ DE L'ACHAT", "💰", "orange", banner=False)
            
            detail_section = format_section_rich(
                "Détails",
                "",
                "📋",
                "info"
            )
            detail_content = (
                f"{format_info_card('Argent à créditer', str(points_to_add), '📊')}\n"
                f"{format_info_card('Total à payer', f'{price_euros:.2f} €', '💵', value_highlight=True)}"
            )
            
            payment_section = format_section_rich(
                "Lien de paiement",
                f"<code>{payment_url_safe}</code>",
                "🔗",
                "orange",
                highlight=True
            )
            
            instructions_section = format_section_rich(
                "Instructions",
                "Saisissez l'adresse securisée ci-dessus, et envoyer la somme attendu. Après avoir effectué le paiement, revenez ici et veuillez envoyer une capture d'écran paypal comme preuve de paiement.\n\n⏳ Votre transaction est en attente de preuve.",
                "📸",
                "warning"
            )
            
            summary_message = f"{header}\n\n{detail_section}\n{detail_content}\n\n{payment_section}\n\n{instructions_section}"
            
            keyboard = [[InlineKeyboardButton("❌ Annuler", callback_data=f"cancel_payment_{points_to_add}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await safe_edit_message_text(query, summary_message, reply_markup, "HTML")
                
                # Vérifier si l'utilisateur a déjà une transaction en attente (empêcher les transactions multiples)
                existing_payment_id = get_user_pending_payment(user_id)
                if existing_payment_id:
                    await safe_edit_message_text(
                        query,
                        "⚠️ Vous avez déjà une transaction en attente. Veuillez attendre sa validation ou l'annuler avant d'en créer une nouvelle.",
                        create_back_button("shop"),
                        "HTML"
                    )
                    logger.warning(f"Tentative de créer une transaction alors qu'une existe déjà pour l'utilisateur {user_id}")
                    return
                
                # Si le prix est 0 (réduction 100%), accepter automatiquement la transaction
                if price_euros == 0:
                    logger.info(f"Prix final = 0€ pour user_id={user_id}, argent={points_to_add}. Création et acceptation automatique.")
                    
                    # Créer la transaction avec statut 'pending' d'abord
                    payment_id = create_pending_payment(user_id, points_to_add, price_euros)
                    if payment_id and payment_id > 0:
                        # Accepter automatiquement la transaction
                        result = accept_payment_atomic(payment_id)
                        if result:
                            payment_user_id, payment_points, new_balance = result
                            logger.info(f"Transaction {payment_id} acceptée automatiquement (prix=0€). Argent ajouté: {payment_points}, nouveau solde: {new_balance}")
                            
                            # Afficher un message de succès
                            success_header = format_header_rich("TRANSACTION ACCEPTÉE", "✅", "success", banner=False)
                            success_section = format_section_rich(
                                "Statut",
                                f"Votre achat de {payment_points} argent a été accepté automatiquement (prix final: 0€).\n\nVotre nouveau solde est de {new_balance} argent.",
                                "💰",
                                "success",
                                highlight=True
                            )
                            success_message = f"{success_header}\n\n{success_section}"
                            
                            await safe_edit_message_text(
                                query, success_message, create_back_button("shop"), "HTML"
                            )
                        else:
                            logger.error(f"Échec de l'acceptation automatique de la transaction {payment_id}")
                            await safe_edit_message_text(
                                query,
                                "❌ Erreur lors du traitement automatique. Veuillez contacter un administrateur.",
                                create_back_button("shop"),
                                "HTML"
                            )
                    else:
                        logger.error(f"Échec de la création de la transaction pour l'utilisateur {user_id}: payment_id={payment_id}")
                        await safe_edit_message_text(
                            query,
                            "❌ Erreur lors de la création de la transaction. Veuillez réessayer.",
                            create_back_button("shop"),
                            "HTML"
                        )
                    return
                
                # Créer la transaction en attente (prix > 0)
                payment_id = create_pending_payment(user_id, points_to_add, price_euros)
                if payment_id and payment_id > 0:
                    # Stocker le payment_id dans context pour référence
                    context.user_data[f'pending_payment_{user_id}'] = payment_id
                    context.user_data[f'waiting_payment_{user_id}'] = True
                    # Stocker le message_id du résumé pour pouvoir le modifier plus tard
                    if query.message:
                        context.user_data[f'summary_message_id_{user_id}'] = query.message.message_id
                    
                    logger.info(f"Transaction en attente créée avec succès pour l'utilisateur {user_id}: payment_id={payment_id}, points={points_to_add}, price={price_euros:.2f}€")
                    
                    # Vérifier immédiatement que la transaction est accessible
                    verification_id = get_user_pending_payment(user_id)
                    if verification_id != payment_id:
                        logger.error(f"PROBLÈME: Transaction créée (ID={payment_id}) mais non trouvée lors de la vérification immédiate (trouvé: {verification_id})")
                else:
                    logger.error(f"Échec de la création de la transaction pour l'utilisateur {user_id}: payment_id={payment_id}")
                    await safe_edit_message_text(
                        query,
                        "❌ Erreur lors de la création de la transaction. Veuillez réessayer.",
                        create_back_button("shop"),
                        "HTML"
                    )
                    return
            except TelegramError as e:
                logger.error(f"Erreur lors de l'affichage du résumé: {e}")
                await safe_edit_message_text(
                    query,
                    "❌ Une erreur s'est produite. Veuillez réessayer.",
                    create_back_button("shop"),
                    "HTML"
                )
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur lors de la validation des points: {e}")
            await safe_edit_message_text(
                query,
                "❌ Erreur lors du traitement. Veuillez réessayer.",
                create_back_button("shop"),
                "HTML"
            )
        return
    
    # Gestion de l'annulation de paiement
    if callback_data.startswith("cancel_payment_"):
        user_id_to_check = user_id
        
        # Annulation atomique (source de vérité DB)
        payment_id = cancel_user_pending_payment_atomic(user_id_to_check)
        
        # Nettoyer le contexte dans tous les cas
        context.user_data.pop(f'waiting_payment_{user_id_to_check}', None)
        context.user_data.pop(f'pending_payment_{user_id_to_check}', None)
        context.user_data.pop(f'summary_message_id_{user_id_to_check}', None)
        
        try:
            header = format_header_rich("PAIEMENT ANNULÉ", "❌", "danger", banner=False)
            message = f"{header}\n\nRetour au shop."
            await query.edit_message_text(
                message,
                reply_markup=create_back_button("shop"),
                parse_mode="HTML"
            )
            logger.info(f"Paiement annulé par l'utilisateur {user_id_to_check}")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'annulation du paiement: {e}")
        return
    
    # Gestion de l'acceptation/refus de paiement par l'admin
    if callback_data.startswith("payment_accept_") and role == "admin":
        try:
            payment_id = int(callback_data.split("_")[-1])
            
            # Debouncing : éviter les double-clics (même si atomic, éviter le traitement inutile)
            payment_action_key = f'payment_action_{payment_id}'
            if context.user_data.get(payment_action_key):
                return
            context.user_data[payment_action_key] = True
            
            try:
                # Récupérer les infos de la transaction pour l'affichage (avant acceptation atomique)
                payment = get_pending_payment(payment_id)
                if not payment:
                    return
                
                _, payment_user_id, points, price, photo_file_id, created_at, _, confirmation_message_id = payment[:8]
                
                # Acceptation atomique (vérifie statut, ajoute points, met à jour statut en une transaction)
                result = accept_payment_atomic(payment_id)
                
                if result:
                    payment_user_id, points, new_balance = result
                    
                    # Message de confirmation avec le nouveau système esthétique
                    header = format_header_rich("PAIEMENT ACCEPTÉ", "✅", "success", banner=False)
                    
                    success_section = format_section_rich(
                        "Argent ajouté",
                        f"<b>{points} argent</b> ont été ajoutés à votre compte",
                        "💰",
                        "success",
                        highlight=True
                    )
                    
                    solde_badge = format_highlight_box(f"Nouveau solde : {new_balance} argent", "💎", "gold")
                    
                    footer = "\n✨ Merci pour votre confiance !"
                    success_message = f"{header}\n\n{success_section}\n{solde_badge}\n\n{footer}"
                    
                    # Supprimer le message "Paiement bien reçu, en attente" si il existe
                    if confirmation_message_id:
                        try:
                            await context.bot.delete_message(
                                chat_id=payment_user_id,
                                message_id=confirmation_message_id
                            )
                            logger.info(f"Message de confirmation supprimé pour la transaction {payment_id}")
                        except TelegramError as e:
                            logger.warning(f"Impossible de supprimer le message de confirmation: {e}")
                    
                    try:
                        await context.bot.send_message(
                            chat_id=payment_user_id,
                            text=success_message,
                            parse_mode="HTML"
                        )
                    except TelegramError as e:
                        logger.error(f"Erreur lors de l'envoi du message à l'utilisateur {payment_user_id}: {e}")
                    
                    # Modifier le message admin avec le nouveau système esthétique
                    header = format_header_rich("PAIEMENT ACCEPTÉ", "✅", "success", banner=False)
                    
                    detail_section = format_section_rich(
                        "Détails de la transaction",
                        "",
                        "📋",
                        "info"
                    )
                    detail_content = (
                        f"{format_info_card('Utilisateur', f'<code>{payment_user_id}</code>', '👤')}\n"
                        f"{format_info_card('Points', str(points), '💰')}\n"
                        f"{format_info_card('Montant', f'{price:.2f} €', '💵')}\n"
                        f"{format_info_card('Date', str(created_at), '📅')}\n"
                        f"{format_info_card('Transaction ID', f'<code>{payment_id}</code>', '🆔')}"
                    )
                    
                    status_badge = format_status_badge("Les points ont été ajoutés au compte", "success")
                    admin_status_message = f"{header}\n\n{detail_section}\n{detail_content}\n\n{status_badge}"
                    
                    try:
                        await query.message.edit_caption(
                            caption=admin_status_message,
                            parse_mode="HTML"
                        )
                    except TelegramError as e:
                        logger.error(f"Erreur lors de la mise à jour du message admin: {e}")
                        # Fallback si edit_caption échoue
                        try:
                            await query.edit_message_text(
                                admin_status_message,
                                parse_mode="HTML"
                            )
                        except TelegramError:
                            pass
                    logger.info(f"Paiement {payment_id} accepté par l'admin {user_id}")
                else:
                    pass  # Transaction déjà traitée ou erreur
            finally:
                # Libérer le debouncing après 2 secondes
                async def release_action():
                    await asyncio.sleep(2.0)
                    context.user_data.pop(payment_action_key, None)
                asyncio.create_task(release_action())
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur lors de l'acceptation du paiement: {e}")
            # Libérer le debouncing même en cas d'erreur
            if 'payment_action_key' in locals():
                context.user_data.pop(payment_action_key, None)
        return
    
    if callback_data.startswith("payment_refuse_") and role == "admin":
        try:
            payment_id = int(callback_data.split("_")[-1])
            payment_action_key = f'payment_action_{payment_id}'

            # Refus atomique : vérifier et mettre à jour le statut en une transaction
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Lock explicite avec FOR UPDATE pour éviter les doubles refus
                cursor.execute("""
                    SELECT id, user_id, points, price, photo_file_id, created_at, confirmation_message_id
                    FROM pending_payments 
                    WHERE id = %s AND status = 'pending'
                    FOR UPDATE
                """, (payment_id,))
                
                payment = cursor.fetchone()
                
                if not payment:
                    return
                
                _, payment_user_id, points, price, photo_file_id, created_at, confirmation_message_id = payment
                
                # Mettre à jour le statut
                cursor.execute("""
                    UPDATE pending_payments 
                    SET status = 'refused' 
                    WHERE id = %s AND status = 'pending'
                """, (payment_id,))
                
                if cursor.rowcount == 0:
                    # Le statut a changé entre temps
                    return
                
                conn.commit()
            
            # Récupérer les infos pour l'affichage
            payment = get_pending_payment(payment_id)
            if payment:
                _, payment_user_id, points, price, photo_file_id, created_at, _, confirmation_message_id = payment[:8]
            
            # Supprimer le message "Paiement bien reçu, en attente" si il existe
            if confirmation_message_id:
                try:
                    await context.bot.delete_message(
                        chat_id=payment_user_id,
                        message_id=confirmation_message_id
                    )
                    logger.info(f"Message de confirmation supprimé pour la transaction {payment_id}")
                except TelegramError as e:
                    logger.warning(f"Impossible de supprimer le message de confirmation: {e}")
            
            # Message de refus à l'utilisateur
            refusal_message = (
                f"❌ **Paiement refusé**\n\n"
                f"Votre preuve de paiement a été refusée par l'administration.\n\n"
                f"Si vous pensez qu'il s'agit d'une erreur, veuillez contacter le support."
            )
            
            try:
                await context.bot.send_message(
                    chat_id=payment_user_id,
                    text=refusal_message,
                    parse_mode="Markdown"
                )
            except TelegramError as e:
                logger.error(f"Erreur lors de l'envoi du message à l'utilisateur {payment_user_id}: {e}")
            
            # Modifier le message admin avec la photo pour afficher le statut et supprimer les boutons
            # Message admin pour paiement refusé avec le nouveau style
            # Message admin pour paiement refusé avec le nouveau système esthétique
            header = format_header_rich("PAIEMENT REFUSÉ", "❌", "danger", banner=False)
            
            detail_section = format_section_rich(
                "Détails de la transaction",
                "",
                "📋",
                "info"
            )
            detail_content = (
                f"{format_info_card('Utilisateur', f'<code>{payment_user_id}</code>', '👤')}\n"
                f"{format_info_card('Points', str(points), '💰')}\n"
                f"{format_info_card('Montant', f'{price:.2f} €', '💵')}\n"
                f"{format_info_card('Date', str(created_at), '📅')}\n"
                f"{format_info_card('Transaction ID', f'<code>{payment_id}</code>', '🆔')}"
            )
            
            status_badge = format_status_badge("L'utilisateur a été notifié du refus", "error")
            admin_status_message = f"{header}\n\n{detail_section}\n{detail_content}\n\n{status_badge}"
            
            try:
                await query.message.edit_caption(
                    caption=admin_status_message,
                    parse_mode="HTML"
                )
            except TelegramError as e:
                logger.error(f"Erreur lors de la mise à jour du message admin: {e}")
                # Fallback si edit_caption échoue
                try:
                    await query.edit_message_text(
                        admin_status_message,
                        parse_mode="HTML"
                    )
                except TelegramError:
                    pass
                logger.info(f"Paiement {payment_id} refusé par l'admin {user_id}")
            finally:
                # Libérer le debouncing après 2 secondes
                async def release_action():
                    await asyncio.sleep(2.0)
                    context.user_data.pop(payment_action_key, None)
                asyncio.create_task(release_action())
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur lors du refus du paiement: {e}")
            try:
                context.user_data.pop(payment_action_key, None)
            except NameError:
                pass
        return

    # Demande d'accès : accepter (créer l'utilisateur dans users et notifier)
    if callback_data.startswith("demande_accept_") and role == "admin":
        try:
            target_uid = int(callback_data.split("_")[-1])
        except (ValueError, IndexError):
            target_uid = None
        if target_uid and target_uid > 0:
            row = get_nouveau_user(target_uid)
            username = row[0] if row else None
            get_or_create_user(target_uid, username)
            set_demande_accepte(target_uid)
            await send_notification(
                context.bot, target_uid,
                "✅ <b>Demande d'accès acceptée</b>\n\nVous pouvez maintenant utiliser le bot. Envoyez /start pour commencer.",
                "HTML"
            )
            try:
                await query.edit_message_text(
                    f"✅ Demande acceptée pour l'utilisateur <code>{target_uid}</code>. Il a été notifié.",
                    parse_mode="HTML"
                )
            except TelegramError:
                pass
            logger.info(f"Demande d'accès acceptée pour user_id={target_uid} par admin {user_id}")
        return

    # Demande d'accès : refuser (demande_en_attente = false, notifier)
    if callback_data.startswith("demande_refuse_") and role == "admin":
        try:
            target_uid = int(callback_data.split("_")[-1])
        except (ValueError, IndexError):
            target_uid = None
        if target_uid and target_uid > 0:
            set_demande_refuse(target_uid)
            await send_notification(
                context.bot, target_uid,
                "❌ <b>Demande d'accès refusée</b>\n\nVous pouvez redemander plus tard en utilisant /start.",
                "HTML"
            )
            try:
                await query.edit_message_text(
                    f"❌ Demande refusée pour l'utilisateur <code>{target_uid}</code>. Il a été notifié.",
                    parse_mode="HTML"
                )
            except TelegramError:
                pass
            logger.info(f"Demande d'accès refusée pour user_id={target_uid} par admin {user_id}")
        return

    # Gestion de l'édition de l'annonce (texte)
    if callback_data == "config_annonce_text_edit" and role == "admin":
        message = (
            "📝 **Modifier le texte de l'annonce**\n\n"
            "Envoyez le nouveau texte de l'annonce.\n"
            "Vous pouvez utiliser du Markdown (gras, italique, liens, etc.).\n\n"
            "⚠️ Le texte sera affiché tel quel aux utilisateurs."
        )
        keyboard = [[InlineKeyboardButton("❌ Annuler", callback_data="config_annonce")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Activer le mode édition d'annonce
        context.user_data['config_announcement_edit'] = 'text'
        
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de l'édition d'annonce: {e}")
        return
    
    # Gestion de l'édition de l'annonce (photo)
    if callback_data == "config_annonce_photo_edit" and role == "admin":
        message = (
            "🖼️ **Modifier la photo de l'annonce**\n\n"
            "Envoyez une nouvelle photo (avec ou sans caption).\n"
            "La photo remplacera l'ancienne si elle existe.\n\n"
            "💡 Vous pouvez envoyer une photo avec un caption pour mettre à jour le texte en même temps."
        )
        keyboard = [[InlineKeyboardButton("❌ Annuler", callback_data="config_annonce")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Activer le mode édition d'annonce photo
        context.user_data['config_announcement_edit'] = 'photo'
        
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de l'édition photo annonce: {e}")
        return
    
    # Gestion de la suppression de la photo de l'annonce
    if callback_data == "config_annonce_photo_delete" and role == "admin":
        if update_config_value("announcement_photo", ""):
            message = "✅ **Photo supprimée**\n\nLa photo de l'annonce a été supprimée avec succès."
            logger.info(f"Photo d'annonce supprimée par l'admin {user_id}")
        else:
            message = "❌ Erreur lors de la suppression de la photo."
        
        keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="config_annonce")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de la suppression de la photo: {e}")
        return
    
    # Gestion de l'édition des valeurs de configuration (envoi d'un message pour saisie)
    if callback_data in {"config_min_edit", "config_max_edit", "config_card_margin_edit", 
                         "config_prix_carte_edit",
                         "config_payment_url_edit", "config_staff_channel_edit", "config_staff_thread_payment_edit", 
                         "config_staff_thread_entretien_edit",
                         "config_staff_thread_demande_access_edit"} and role == "admin":
        config_labels = {
            "config_min_edit": ("Minimum d'argent", "argent_min", "int"),
            "config_max_edit": ("Maximum d'argent", "argent_max", "int"),
            "config_card_margin_edit": ("Marge pour l'achat de cartes (points)", "card_margin", "int"),
            "config_prix_carte_edit": ("Prix carte (€)", "prix_carte", "float"),
            "config_payment_url_edit": ("URL de paiement", "payment_url", "str"),
            "config_staff_channel_edit": ("ID du Canal Staff (commence par -)", "staff_channel_id", "str"),
            "config_staff_thread_payment_edit": ("ID du Thread Paiement (nombre)", "staff_thread_payment", "int"),
            "config_staff_thread_entretien_edit": ("ID du Thread Entretien (nombre)", "staff_thread_entretien", "int"),
            "config_staff_thread_demande_access_edit": ("ID du Thread Demande d'accès (nombre)", "staff_thread_demande_access", "int")
        }
        
        label, key, value_type = config_labels[callback_data]
        
        # Valeur par défaut selon le type
        if value_type == "int":
            if key in ["staff_thread_payment", "staff_thread_entretien", "staff_thread_demande_access"]:
                current_value = get_config_value(key, "")
            elif key == "card_margin":
                current_value = get_config_value(key, DEFAULT_CARD_MARGIN)
            elif key == "argent_min":
                current_value = get_config_value(key, DEFAULT_POINT_MIN)
            elif key == "argent_max":
                current_value = get_config_value(key, DEFAULT_POINT_MAX)
            else:
                current_value = get_config_value(key, 150)
        elif value_type == "float":
            current_value = get_prix_carte() if key == "prix_carte" else get_config_value(key, "0")
        else:
            if key == "staff_channel_id":
                current_value = get_config_value(key, "")
            else:
                current_value = get_config_value(key, "https://example.com/pay")
        
        message = (
            f"⚙️ **Modifier {label}**\n\n"
            f"Valeur actuelle: **{current_value}**\n\n"
            f"Veuillez envoyer la nouvelle valeur.\n"
            f"Type attendu: {'Nombre décimal (0-100)' if value_type == 'float_pct' else 'Nombre décimal (ex: 4.99)' if value_type == 'float' else 'Nombre entier'}\n"
            f"⚠️ La valeur doit être {'entre 0 et 100' if value_type == 'float_pct' else 'positive ou nulle (€)' if value_type == 'float' else 'positive ou nulle'}"
        )
        
        # Stocker dans context pour récupération après
        context.user_data['config_edit'] = {'key': key, 'type': value_type, 'label': label}
        
        # Déterminer le menu de retour selon le type de config
        if key == "payment_url":
            back_callback = "config_payement"
        elif key in ["point_min", "point_max", "argent_min", "argent_max"]:
            back_callback = "config_points"
        elif key in ["card_margin", "prix_carte"]:
            back_callback = "config_carte"
        elif key in ["staff_channel_id", "staff_thread_payment", "staff_thread_entretien", "staff_thread_demande_access"]:
            back_callback = "config_canal"
        else:
            back_callback = "cmd_config"
        
        keyboard = [[InlineKeyboardButton("❌ Annuler", callback_data=back_callback)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de l'édition de config: {e}")
        return
    
    # Gestion de cmd_annonce (affichage de l'annonce)
    if callback_data == "cmd_annonce":
        announcement_text = get_announcement_text()
        announcement_photo = get_announcement_photo()
        
        keyboard = create_back_button("shop")
        
        try:
            # Gérer la transition depuis une bannière shop (photo) vers annonce
            if announcement_photo:
                # Si le message actuel est une photo (bannière shop), supprimer et recréer
                if query.message.photo:
                    try:
                        await query.message.delete()
                    except:
                        pass
                    await query.message.reply_photo(
                        photo=announcement_photo,
                        caption=announcement_text,
                        reply_markup=keyboard,
                        parse_mode="Markdown"
                    )
                else:
                    # Message texte : supprimer et recréer avec photo
                    try:
                        await query.message.delete()
                    except:
                        pass
                    await query.message.reply_photo(
                        photo=announcement_photo,
                        caption=announcement_text,
                        reply_markup=keyboard,
                        parse_mode="Markdown"
                    )
            else:
                # Pas de photo d'annonce : utiliser safe_edit_message_text pour transition photo->texte
                await safe_edit_message_text(query, announcement_text, keyboard, "Markdown")
            logger.info(f"Annonce affichée pour l'utilisateur {user_id}")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de l'annonce: {e}")
            try:
                await safe_edit_message_text(query, "❌ Erreur lors de l'affichage de l'annonce.", keyboard, "Markdown")
            except TelegramError:
                pass
        return
    
    # Gestion de cmd_user (gestion des utilisateurs)
    if callback_data == "cmd_user" and role == "admin":
        # Nettoyer les états précédents
        context.user_data.pop('user_list_page', None)
        context.user_data.pop('user_info_mode', None)
        
        user_count = get_user_count()
        
        message = (
            "👥 **Gestion des Utilisateurs**\n\n"
            f"📊 **Nombre total d'utilisateurs:** {user_count}\n\n"
            "Sélectionnez une action :"
        )
        keyboard = [
            [InlineKeyboardButton("📋 Liste des utilisateurs", callback_data="user_list")],
            [InlineKeyboardButton("ℹ️ Info d'un utilisateur", callback_data="user_info")],
            [InlineKeyboardButton("🔙 Retour", callback_data="menu_principal")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage du menu utilisateurs: {e}")
        return
    
    # Gestion de la liste des utilisateurs (pagination)
    if callback_data == "user_list" and role == "admin":
        page = 0
        users, total_pages = get_users_paginated(page, 20)
        
        if not users:
            message = "📋 **Liste des utilisateurs**\n\nAucun utilisateur trouvé."
            keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="cmd_user")]]
        else:
            message = f"📋 **Liste des utilisateurs**\n\nPage {page + 1}/{total_pages if total_pages > 0 else 1}\n\n"
            for uid, username, balance, user_role, reduction in users:
                username_display = f"@{username}" if username else "N/A"
                reduction_display = f" - {reduction}%" if reduction > 0 else ""
                message += f"• {username_display} (`{uid}`) - {balance} pts - {user_role}{reduction_display}\n"
            
            keyboard = []
            if total_pages > 1:
                nav_buttons = []
                if page > 0:
                    nav_buttons.append(InlineKeyboardButton("◀️ Précédent", callback_data=f"user_list_page_{page - 1}"))
                if page < total_pages - 1:
                    nav_buttons.append(InlineKeyboardButton("Suivant ▶️", callback_data=f"user_list_page_{page + 1}"))
                if nav_buttons:
                    keyboard.append(nav_buttons)
            keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data="cmd_user")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de la liste des utilisateurs: {e}")
        return
    
    # Gestion de la pagination de la liste
    if callback_data.startswith("user_list_page_") and role == "admin":
        try:
            page = int(callback_data.split("_")[-1])
            users, total_pages = get_users_paginated(page, 20)
            
            if not users:
                message = "📋 **Liste des utilisateurs**\n\nAucun utilisateur trouvé."
                keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="cmd_user")]]
            else:
                message = f"📋 **Liste des utilisateurs**\n\nPage {page + 1}/{total_pages if total_pages > 0 else 1}\n\n"
                for uid, username, balance, user_role in users:
                    username_display = f"@{username}" if username else "N/A"
                    message += f"• {username_display} (`{uid}`) - {balance} pts - {user_role}\n"
                
                keyboard = []
                if total_pages > 1:
                    nav_buttons = []
                    if page > 0:
                        nav_buttons.append(InlineKeyboardButton("◀️ Précédent", callback_data=f"user_list_page_{page - 1}"))
                    if page < total_pages - 1:
                        nav_buttons.append(InlineKeyboardButton("Suivant ▶️", callback_data=f"user_list_page_{page + 1}"))
                    if nav_buttons:
                        keyboard.append(nav_buttons)
                keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data="cmd_user")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
            except TelegramError as e:
                logger.error(f"Erreur lors de l'affichage de la page {page}: {e}")
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur lors de la pagination: {e}")
        return
    
    # Gestion de l'info d'un utilisateur - activation du mode
    if callback_data == "user_info" and role == "admin":
        context.user_data['user_info_mode'] = True
        
        message = (
            "ℹ️ **Info d'un utilisateur**\n\n"
            "📝 Envoyez l'ID de l'utilisateur (uniquement le nombre)."
        )
        keyboard = [[InlineKeyboardButton("❌ Annuler", callback_data="cmd_user")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'activation du mode info utilisateur: {e}")
        return
    
    # Récupération du message et création du bouton retour
    message_result = get_command_message(callback_data, user_id, user.first_name)
    if message_result is None:
        # Commande gérée séparément
        return
    
    message, back_type = message_result
    keyboard = create_back_button(back_type)
    
    try:
        await safe_edit_message_text(
            query,
            sanitize_text(message, 4096),
            keyboard,
            "Markdown"
        )
        logger.info(f"Callback '{callback_data}' exécuté par l'utilisateur {user_id} (rôle: {role})")
    except TelegramError as e:
        logger.error(f"Erreur lors de l'édition du message: {e}")


async def photo_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gère les messages photo (screenshots de preuve de paiement ou modification d'annonce)"""
    if not update.message or not update.effective_user:
        return
    
    user = update.effective_user
    user_id = user.id
    role = get_effective_role(user_id, context)
    
    # Mettre à jour le username de l'utilisateur à chaque interaction (pour avoir les pseudos à jour dans la liste)
    if user.username:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET username = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
                    (user.username, user_id)
                )
        except psycopg2.Error as e:
            logger.debug(f"Erreur lors de la mise à jour du username pour {user_id}: {e}")
    
    # Vérifier si l'admin est en train de modifier la photo de l'annonce (AVANT le rate limit)
    if 'config_announcement_edit' in context.user_data and role == "admin":
        edit_mode = context.user_data.get('config_announcement_edit')
        if edit_mode == 'photo':
            photo = update.message.photo
            if photo:
                # Prendre la plus grande photo
                photo_file = photo[-1]
                photo_file_id = photo_file.file_id
                
                # Mettre à jour la photo
                if update_config_value("announcement_photo", photo_file_id):
                    # Si il y a un caption, mettre à jour aussi le texte
                    if update.message.caption:
                        if update_config_value("announcement_text", update.message.caption):
                            success_message = (
                                "✅ **Annonce mise à jour !**\n\n"
                                "La photo et le texte de l'annonce ont été modifiés avec succès."
                            )
                        else:
                            success_message = (
                                "✅ **Photo mise à jour !**\n\n"
                                "⚠️ La photo a été mise à jour, mais une erreur s'est produite lors de la mise à jour du texte."
                            )
                    else:
                        success_message = (
                            "✅ **Photo mise à jour !**\n\n"
                            "La photo de l'annonce a été modifiée avec succès."
                        )
                    logger.info(f"Annonce photo modifiée par l'admin {user_id}")
                else:
                    success_message = "❌ Erreur lors de la mise à jour de la photo."
                
                keyboard = [[InlineKeyboardButton("🔙 Retour à la config", callback_data="config_annonce")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                try:
                    await update.message.reply_text(success_message, reply_markup=reply_markup, parse_mode="Markdown")
                except TelegramError as e:
                    logger.error(f"Erreur lors de l'envoi du message de confirmation: {e}")
                
                context.user_data.pop('config_announcement_edit', None)
            else:
                # Pas de photo, annuler
                try:
                    await update.message.reply_text(
                        "❌ Aucune photo détectée. Opération annulée.",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Retour", callback_data="config_annonce")]])
                    )
                except TelegramError:
                    pass
                context.user_data.pop('config_announcement_edit', None)
            return
    
    # Rate limit : max 1 photo toutes les 5 secondes pour les users (anti-spam admin + charge serveur)
    # Les admins sont exemptés
    if not check_rate_limit(user_id, "photo_message", 5.0):
        try:
            await update.message.reply_text("⏳ Veuillez patienter 5 secondes avant d'envoyer une autre photo.")
        except TelegramError:
            pass
        return
    
    # Vérifier l'arrêt d'urgence
    if is_emergency_stop_active() and role != "admin":
        try:
            await update.message.reply_text(
                "⚠️ Le bot est momentanément indisponible, veuillez patienter pour l'instant."
            )
        except TelegramError:
            pass
        return
    
    # Vérifier d'abord la DB comme source de vérité (au lieu de context.user_data)
    payment_id = get_user_pending_payment(user_id)
    
    logger.info(f"Photo reçue de l'utilisateur {user_id}, payment_id depuis DB: {payment_id}")
    
    if not payment_id:
        # Pas de transaction en attente dans la DB, nettoyer le contexte même si flag présent
        logger.warning(f"Aucune transaction en attente trouvée pour l'utilisateur {user_id} lors de la réception d'une photo")
        context.user_data.pop(f'waiting_payment_{user_id}', None)
        context.user_data.pop(f'pending_payment_{user_id}', None)
        context.user_data.pop(f'summary_message_id_{user_id}', None)
        try:
            await update.message.reply_text(
                "❌ Aucune transaction en attente trouvée. Veuillez créer une nouvelle transaction depuis le shop."
            )
        except TelegramError as e:
            logger.error(f"Erreur lors de l'envoi du message d'erreur pour l'utilisateur {user_id}: {e}")
        return
    
    # Synchroniser le contexte avec la DB (source de vérité)
    context.user_data[f'waiting_payment_{user_id}'] = True
    context.user_data[f'pending_payment_{user_id}'] = payment_id
    
    # Récupérer la photo
    photo = update.message.photo
    if not photo:
        logger.warning(f"Aucune photo détectée dans le message de l'utilisateur {user_id}")
        try:
            await update.message.reply_text("❌ Aucune photo détectée. Veuillez envoyer une photo comme preuve de paiement.")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'envoi du message d'erreur pour l'utilisateur {user_id}: {e}")
        return
    
    # Prendre la plus grande photo
    photo_file = photo[-1]
    photo_file_id = photo_file.file_id
    logger.info(f"Photo reçue pour la transaction {payment_id} (user_id={user_id}), file_id={photo_file_id}")
    
    # Mettre à jour la transaction avec la photo
    if not update_pending_payment_photo(payment_id, photo_file_id):
        logger.error(f"Échec de la mise à jour de la photo pour la transaction {payment_id} (user_id={user_id})")
        try:
            await update.message.reply_text(
                "❌ Erreur lors de l'enregistrement de votre preuve de paiement. Veuillez réessayer ou contacter un administrateur."
            )
        except TelegramError as e:
            logger.error(f"Erreur lors de l'envoi du message d'erreur pour l'utilisateur {user_id}: {e}")
        return
    
    logger.info(f"Photo mise à jour avec succès pour la transaction {payment_id} (user_id={user_id})")
    
    # Supprimer le message de l'utilisateur et la photo (après avoir envoyé la réponse)
    # On ne supprime plus ici car on veut garder le message pour référence
    
    # Mettre à jour le message de résumé de l'achat pour afficher le menu shop
    summary_message_id = context.user_data.get(f'summary_message_id_{user_id}')
    if summary_message_id:
        try:
            # Créer un faux Update pour afficher le menu shop
            # On va créer un message shop directement
            shop_message = "🛒 **Shop**\n\nSélectionnez une option :"
            
            keyboard = [
                [InlineKeyboardButton("📢 Annonces", callback_data="cmd_annonce")],
                [InlineKeyboardButton("👤 Moi", callback_data="cmd_moi")],
                [InlineKeyboardButton("💰 Acheter de l'argent", callback_data="cmd_acheter_points")],
                [InlineKeyboardButton("🛒 Boutique", callback_data="cmd_boutique")],
                [InlineKeyboardButton("🔙 Retour", callback_data="menu_principal")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Modifier le message de résumé pour afficher le menu shop
            await context.bot.edit_message_text(
                chat_id=user_id,
                message_id=summary_message_id,
                text=shop_message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            
            # Nettoyer le message_id stocké
            context.user_data.pop(f'summary_message_id_{user_id}', None)
            
        except TelegramError as e:
            logger.warning(f"Impossible de mettre à jour le message de résumé pour l'utilisateur {user_id}: {e}")
    
    # Envoyer un message de confirmation avec le nouveau système esthétique
    header = format_header_rich("PAIEMENT REÇU", "✅", "info", banner=False)
    
    info_section = format_section_rich(
        "Statut",
        "Votre preuve de paiement a été reçue et est en cours de validation par l'administration.",
        "⏳",
        "warning",
        highlight=False
    )
    
    confirmation_message = f"{header}\n\n{info_section}"
    try:
        logger.info(f"Envoi du message de confirmation pour la transaction {payment_id} (user_id={user_id})")
        sent_message = await update.message.reply_text(confirmation_message, parse_mode="HTML")
        # Stocker le message_id de confirmation pour pouvoir le supprimer plus tard
        if sent_message and sent_message.message_id:
            update_payment_confirmation_message_id(payment_id, sent_message.message_id)
            logger.info(f"Message de confirmation envoyé avec succès (message_id={sent_message.message_id}) pour la transaction {payment_id}")
        else:
            logger.warning(f"Message de confirmation envoyé mais message_id non disponible pour la transaction {payment_id}")
    except TelegramError as e:
        logger.error(f"Erreur lors de l'envoi du message de confirmation pour la transaction {payment_id} (user_id={user_id}): {e}")
    
    # Récupérer les détails de la transaction
    payment = get_pending_payment(payment_id)
    if not payment:
        logger.error(f"Transaction {payment_id} introuvable après mise à jour de la photo (user_id={user_id})")
        try:
            await update.message.reply_text(
                "❌ Erreur lors de la récupération des détails de la transaction. Veuillez contacter un administrateur."
            )
        except TelegramError as e:
            logger.error(f"Erreur lors de l'envoi du message d'erreur pour l'utilisateur {user_id}: {e}")
        return
    
    try:
        _, payment_user_id, points, price, photo_file_id, created_at, status, confirmation_message_id = payment[:8]
        
        logger.info(f"Envoi de la preuve de paiement à l'admin pour la transaction {payment_id} (user_id={user_id}, argent={points}, price={price:.2f}€)")
        
        # Récupérer la réduction de l'utilisateur pour afficher les détails
        user_reduction = get_user_reduction(payment_user_id)
        
        # Convertir price en float si c'est un Decimal (venant de PostgreSQL)
        price_float = float(price) if hasattr(price, '__float__') else price
        
        # Construire le message pour l'admin (escape Markdown pour éviter "Can't parse entities")
        admin_message_lines = [
            "📸 **Nouvelle preuve de paiement reçue**\n",
            f"👤 Utilisateur: {escape_markdown(str(user.first_name or 'N/A'))} (@{escape_markdown(str(user.username or 'N/A'))})",
            f"🆔 ID: `{payment_user_id}`",
            f"💰 Argent: **{points}**"
        ]
        
        # Ajouter les informations de réduction si applicable
        if user_reduction > 0:
            # Calculer le prix initial (prix avant réduction)
            if user_reduction < 100:
                # Inversion de la réduction appliquée
                price_initial = price_float / (1 - user_reduction / 100)
                price_initial = math.ceil(price_initial * 20) / 20
            else:
                # Réduction de 100%, le prix initial est celui des points sans réduction
                base_price = points * get_price_per_point(points)
                price_initial = math.ceil(base_price * 20) / 20
            
            admin_message_lines.extend([
                f"💵 Prix avant réduction: **{price_initial:.2f} €**",
                f"🎁 Réduction: **{user_reduction}%**",
                f"💶 Montant final: **{price_float:.2f} €**"
            ])
        else:
            admin_message_lines.append(f"💵 Montant: **{price_float:.2f} €**")
        
        admin_message_lines.extend([
            f"📅 Date: {created_at}",
            f"🆔 Transaction ID: `{payment_id}`"
        ])
        
        admin_message = "\n".join(admin_message_lines)
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Accepter", callback_data=f"payment_accept_{payment_id}"),
                InlineKeyboardButton("❌ Refuser", callback_data=f"payment_refuse_{payment_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Envoyer dans le canal staff avec le thread de paiement
        staff_thread_id = get_staff_thread_payment()
        logger.info(f"Envoi dans le canal staff (thread_id={staff_thread_id}) pour la transaction {payment_id}")
        success = await send_to_staff_channel(
            bot=context.bot,
            message=admin_message,
            thread_id=staff_thread_id,
            photo_file_id=photo_file_id,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
        if success:
            if staff_thread_id:
                logger.info(f"Preuve de paiement envoyée avec succès dans le canal staff (thread paiement) pour la transaction {payment_id}")
            else:
                logger.info(f"Preuve de paiement envoyée avec succès à l'admin directement pour la transaction {payment_id}")
        else:
            logger.error(f"Échec de l'envoi de la preuve de paiement pour la transaction {payment_id} (user_id={user_id})")
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de la preuve de paiement à l'admin pour la transaction {payment_id} (user_id={user_id}): {e}", exc_info=True)
    
    # Nettoyer le contexte
    context.user_data.pop(f'waiting_payment_{user_id}', None)
    context.user_data.pop(f'pending_payment_{user_id}', None)


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gère les messages texte, notamment pour la modification des configurations"""
    if not update.message or not update.effective_user:
        return
    
    user = update.effective_user
    user_id = user.id
    role = get_effective_role(user_id, context)
    
    # Mettre à jour le username de l'utilisateur à chaque interaction (pour avoir les pseudos à jour dans la liste)
    if user.username:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET username = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
                    (user.username, user_id)
                )
        except psycopg2.Error as e:
            logger.debug(f"Erreur lors de la mise à jour du username pour {user_id}: {e}")
    
    # Vérifier si l'admin est en train d'insérer un compte via storage (admin uniquement)
    if context.user_data.get('storage_mode', False):
        # Seuls les admins doivent pouvoir utiliser ce mode
        if role != "admin":
            context.user_data.pop('storage_mode', None)
            await update.message.reply_text("❌ Accès refusé. Seuls les administrateurs peuvent utiliser le storage.")
            return

        json_text_raw = update.message.text or ""
        json_text = json_text_raw.strip()

        if not json_text:
            await update.message.reply_text(
                "❌ JSON vide.\n\nVeuillez envoyer un JSON valide ou revenir au menu config.",
                parse_mode="HTML"
            )
            return

        # Nettoyer le flag immédiatement pour éviter les doublons
        context.user_data.pop('storage_mode', None)

        # Parser le JSON
        try:
            account_data = json.loads(json_text)
            
            if not isinstance(account_data, dict):
                await update.message.reply_text(
                    "❌ Le JSON doit être un objet (dictionnaire).\n\nExemple: `{\"id\": \"...\", \"carte\": \"...\", \"point\": 500}`",
                    parse_mode="Markdown"
                )
                return
            
        except json.JSONDecodeError as e:
            await update.message.reply_text(
                f"❌ JSON invalide.\n\nErreur: {escape_html(str(e))}\n\nVeuillez vérifier la syntaxe JSON.",
                parse_mode="HTML"
            )
            return
        except Exception as e:
            logger.error(f"Erreur lors du parsing JSON storage: {e}")
            await update.message.reply_text(
                "❌ Erreur lors du parsing du JSON. Veuillez réessayer.",
                parse_mode="HTML"
            )
            return

        # Appeler l'API /insert
        success, error_message, warnings = await insert_kfc_account(account_data)
        
        if success:
            account_id = account_data.get('id', 'N/A')
            carte = account_data.get('carte', 'N/A')
            points = account_data.get('point', 0)
            
            # Convertir points en int si c'est une string
            try:
                points = int(points)
            except (ValueError, TypeError):
                pass
            
            success_message = (
                f"✅ <b>Compte inséré avec succès !</b>\n\n"
                f"🆔 ID: <code>{escape_html(str(account_id))}</code>\n"
                f"🎴 Carte: <code>{escape_html(str(carte))}</code>\n"
                f"💎 Points: {points}"
            )
            
            # Ajouter les avertissements s'il y en a
            if warnings:
                success_message += "\n\n⚠️ <b>Avertissements:</b>\n" + "\n".join(f"• {w}" for w in warnings)
            
            await update.message.reply_text(
                success_message,
                parse_mode="HTML"
            )
            logger.info(f"Compte KFC inséré via storage par l'admin {user_id}: {account_id}")
        else:
            error_display = (
                f"❌ <b>Erreur lors de l'insertion</b>\n\n"
                f"{escape_html(error_message or 'Erreur inconnue')}\n\n"
                f"Veuillez vérifier les données et réessayer."
            )
            
            # Ajouter les avertissements même en cas d'erreur
            if warnings:
                error_display += "\n\n⚠️ <b>Avertissements:</b>\n" + "\n".join(f"• {w}" for w in warnings)
            
            await update.message.reply_text(
                error_display,
                parse_mode="HTML"
            )
        return

    # Prénom pour Click&Collect (après « Continuer » sur confirmation Commander)
    if context.user_data.get('click_collect_waiting_prenom'):
        prenom_raw = (update.message.text or "").strip()
        if " " in prenom_raw or not prenom_raw:
            await update.message.reply_text(
                "❌ Un seul mot attendu, sans espace.\n\nRéessayez avec un prénom (ex. Jean, Marie-Claire).",
                parse_mode="HTML"
            )
            return
        if not CLICK_COLLECT_PRENOM_REGEX.fullmatch(prenom_raw):
            await update.message.reply_text(
                "❌ Caractères non autorisés.\n\nUtilisez uniquement des lettres (accents autorisés) et le tiret.",
                parse_mode="HTML"
            )
            return
        context.user_data.pop('click_collect_waiting_prenom', None)
        cart = context.user_data.get('click_collect_cart', [])
        cart_list = cart if isinstance(cart, list) else list((cart or {}).values())
        total_pts = sum(e.get("cost", 0) * e.get("quantity", 1) for e in cart_list)
        if not cart_list:
            await update.message.reply_text("❌ Panier invalide.", parse_mode="HTML")
            return
        await update.message.reply_text(
            "⏳ Panier en cours, attendez au moins 1 min.",
            parse_mode="HTML",
        )
        if USE_TEST_CLICK_ACCOUNT:
            # Mode test : ne génère pas de carte, utilise directement le compte test
            card_data = {
                "id": TEST_CLICK_ACCOUNT_ID,
                "carte": "TEST",
                "nom": "TEST",
            }
            context.user_data['click_collect_card_for_token'] = card_data
            context.user_data['click_collect_prenom'] = prenom_raw
            await _do_recup_token_and_session(None, update, context, user_id, card_data, prenom_raw)
            return
        else:
            card_data = await generate_kfc_card(total_pts)
            if not card_data:
                header = format_header_rich("ERREUR STOCK CLICK", "❌", "orange", banner=False)
                msg = (
                    "Probleme avec le stock pour le click, il semble ne pas avoir la quantité demander.\n\n"
                    "Veuillez réessayer ou contacter un admin."
                )
                keyboard = [
                    [InlineKeyboardButton("🔄 Réessayer", callback_data="click_collect_commander_continue")],
                    [InlineKeyboardButton("🔙 Retour au panier", callback_data="click_collect_panier")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(f"{header}\n\n{msg}", reply_markup=reply_markup, parse_mode="HTML")
                return
            context.user_data['click_collect_card_for_token'] = card_data
            context.user_data['click_collect_prenom'] = prenom_raw
            await _do_recup_token_and_session(None, update, context, user_id, card_data, prenom_raw)
            return

    # Recherche ville/nom KFC pour Click&Collect
    if context.user_data.get('click_collect_city_search'):
        city_raw = (update.message.text or "").strip()
        # Format attendu : 2-100 caractères, lettres/chiffres/espaces/accents/tirets
        if len(city_raw) < 2 or len(city_raw) > 100:
            await update.message.reply_text(
                "❌ Saisie invalide.\n\nEntrez une ville ou un nom de KFC (2 à 100 caractères).",
                parse_mode="HTML"
            )
            return
        if not re.search(r"[a-zA-ZÀ-ÿ]", city_raw):
            await update.message.reply_text(
                "❌ Saisie invalide.\n\nLa recherche doit contenir au moins une lettre.",
                parse_mode="HTML"
            )
            return
        loading_msg = await update.message.reply_text("⏳ Recherche des KFC en cours...", parse_mode="HTML")
        success, stores_list, err_msg = fetch_click_stores(city_raw)
        try:
            await loading_msg.delete()
        except TelegramError:
            pass
        context.user_data.pop('click_collect_city_search', None)
        if not success:
            await update.message.reply_text(
                f"❌ Erreur : {escape_html(err_msg or 'Erreur inconnue')}",
                parse_mode="HTML"
            )
            return
        if not stores_list:
            await update.message.reply_text(
                f"🔍 Aucun KFC trouvé pour « {escape_html(city_raw)} ».",
                parse_mode="HTML"
            )
            return
        # Extraire les villes uniques (ordre préservé)
        cities_seen = set()
        cities = []
        for s in stores_list:
            c = s.get("city") or "?"
            if c not in cities_seen:
                cities_seen.add(c)
                cities.append(c)
        context.user_data['click_collect_stores'] = stores_list
        context.user_data['click_collect_cities'] = cities
        header = format_header_rich("CHOISIR UNE VILLE", "📍", "orange", banner=False)
        keyboard = []
        for i, city in enumerate(cities):
            count = sum(1 for s in stores_list if (s.get("city") or "?") == city)
            label = f"📍 {city} ({count})"
            keyboard.append([InlineKeyboardButton(label, callback_data=f"click_collect_city_{i}")])
        keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data="boutique_click_collect")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(header, reply_markup=reply_markup, parse_mode="HTML")
        return

    boutique_mode = context.user_data.get(f'boutique_custom_{user_id}')
    if boutique_mode == 'carte':
        try:
            points = int(update.message.text.strip())

            if points < 50:
                await update.message.reply_text(
                    "❌ Minimum 50 points requis.\n\nVeuillez entrer un nombre valide (minimum 50).",
                    parse_mode="HTML"
                )
                return

            context.user_data.pop(f'boutique_custom_{user_id}', None)

            try:
                await update.message.delete()
            except:
                pass

            await handle_card_purchase_carte(update, context, user_id, points)
            
        except ValueError:
            await update.message.reply_text(
                "❌ Nombre invalide.\n\nVeuillez entrer un nombre valide (minimum 50 points).",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la saisie manuelle boutique: {e}")
            context.user_data.pop(f'boutique_custom_{user_id}', None)
            await update.message.reply_text(
                "❌ Erreur lors du traitement. Veuillez réessayer.",
                parse_mode="HTML"
            )
        return
    
    # Vérifier si un admin est en mode création de compte (injection carte)
    if context.user_data.get('admin_create_account_mode') and role == "admin":
        text = (update.message.text or "").strip().upper()
        # Validation: 6 caractères hexadécimaux majuscules
        if not re.fullmatch(r'[0-9A-F]{6}', text):
            await update.message.reply_text(
                "❌ Carte invalide.\n\n"
                "Merci d'envoyer exactement <b>6 caractères</b> en hexadécimal <b>MAJUSCULE</b> (0-9, A-F).\n"
                "Exemple : <code>1A2B3C</code>",
                parse_mode="HTML"
            )
            return

        login_card = text

        # Informer l'admin que le traitement peut prendre du temps
        processing_msg = await update.message.reply_text(
            "⏳ Création du compte et liaison de la carte en cours...\n"
            "Cela peut prendre quelques secondes.",
            parse_mode="HTML"
        )

        try:
            # 1) Création du compte via creation_log
            account_result = await create_account()
            if not account_result.get("ok"):
                errmsg = account_result.get("message", "Échec de la création du compte.")
                await processing_msg.edit_text(
                    f"❌ <b>Échec de la création du compte</b>.\n\n{errmsg}",
                    parse_mode="HTML"
                )
                # On reste en mode pour permettre de réessayer avec une autre carte ou la même
                return

            profile = account_result.get("account") or {}

            # 2) Injection de la carte via injecteur_log
            status, a, b = await inject(profile, login_card)

            if status == "success":
                capture, capture2 = a, b
                # Essayer de parser les chaînes capture/capture2 en pseudo-JSON
                try:
                    data1 = json.loads("{" + capture + "}")
                except Exception:
                    data1 = {}
                try:
                    data2 = json.loads("{" + capture2 + "}")
                except Exception:
                    data2 = {}

                carte = data1.get("carte", login_card)
                points = data1.get("point", "N/A")
                date = data1.get("date", "N/A")
                url_wallet = data1.get("url", "N/A")

                mail = data2.get("mail", profile.get("mail"))
                password = data2.get("password", profile.get("password"))
                num = data2.get("numero", profile.get("num"))
                prenom = data2.get("prenom", profile.get("name1"))
                nom = data2.get("nom", profile.get("name2"))

                success_msg = (
                    "✅ <b>Compte créé et carte injectée avec succès.</b>\n\n"
                    f"💳 <b>Carte:</b> <code>{carte}</code>\n"
                    f"💎 <b>Points:</b> {points}\n"
                    f"📅 <b>Date d'expiration des points:</b> {date}\n"
                    f"🔗 <b>URL Wallet:</b> <code>{url_wallet}</code>\n\n"
                    f"👤 <b>Profil créé :</b>\n"
                    f"• Nom: {prenom} {nom}\n"
                    f"• Email: <code>{mail}</code>\n"
                    f"• Mot de passe: <code>{password}</code>\n"
                    f"• Téléphone: <code>{num}</code>\n"
                )

                await processing_msg.edit_text(success_msg, parse_mode="HTML")

                # Sortir du mode après succès
                context.user_data.pop('admin_create_account_mode', None)
                return

            else:
                error_code, error_message = a, b
                await processing_msg.edit_text(
                    "❌ <b>Échec de la liaison de la carte au compte.</b>\n\n"
                    f"Code d'erreur: <code>{error_code}</code>\n"
                    f"Détail: {error_message}\n\n"
                    "Vous pouvez réessayer avec la même carte ou une autre.",
                    parse_mode="HTML"
                )
                # On reste en mode pour permettre un nouvel essai
                return

        except Exception as e:
            logger.error(f"Erreur lors de la création/injection de compte: {e}")
            try:
                await processing_msg.edit_text(
                    "❌ <b>Erreur inattendue lors de la création ou de l'injection du compte.</b>", 
                    parse_mode="HTML"
                )
            except Exception:
                pass
            # On reste en mode pour permettre de réessayer
            return
    
    # Vérifier l'arrêt d'urgence (sauf pour les admins qui peuvent modifier la config)
    if is_emergency_stop_active():
        # Permettre uniquement aux admins de modifier la config (pour désactiver l'arrêt)
        if role != "admin" or 'config_edit' not in context.user_data:
            try:
                await update.message.reply_text(
                    "⚠️ Le bot est momentanément indisponible, veuillez patienter pour l'instant."
                )
            except TelegramError:
                pass
            return
    
    # Vérifier dans la DB si l'utilisateur a une transaction en attente (source de vérité)
    # Si oui, ne rien faire (seules les photos sont acceptées)
    # Optimisation: une seule requête DB au lieu de deux (has_user_pending_payment_in_db + get_user_pending_payment)
    payment_id = get_user_pending_payment(user_id)
    if payment_id:
        # Ignorer les messages texte pendant l'attente de paiement
        # Mais synchroniser le contexte avec la DB
        context.user_data[f'waiting_payment_{user_id}'] = True
        context.user_data[f'pending_payment_{user_id}'] = payment_id
        return
    else:
        # Pas de transaction en DB, nettoyer le contexte même si flag présent
        context.user_data.pop(f'waiting_payment_{user_id}', None)
        context.user_data.pop(f'pending_payment_{user_id}', None)
        context.user_data.pop(f'summary_message_id_{user_id}', None)
    
    # Vérifier si l'admin est en train de récupérer l'info d'un utilisateur
    if 'user_info_mode' in context.user_data and context.user_data.get('user_info_mode') and role == "admin":
        try:
            user_id_to_check = int(update.message.text.strip())
            user_info = get_user_info(user_id_to_check)
            
            if user_info:
                username_display = f"@{user_info['username']}" if user_info['username'] else "N/A"
                role_display = user_info['role'].capitalize()
                if role_display == "Vendeur":
                    role_display = "💼 Vendeur"
                elif role_display == "Moderator":
                    role_display = "🛡️ Modérateur"
                elif role_display == "User":
                    role_display = "👤 User"
                
                created_at_str = user_info['created_at'].strftime("%d/%m/%Y %H:%M:%S") if user_info['created_at'] else "N/A"
                updated_at_str = user_info['updated_at'].strftime("%d/%m/%Y %H:%M:%S") if user_info['updated_at'] else "N/A"
                
                reduction_rate = user_info.get('reduction', 0)
                message = (
                    f"ℹ️ **Informations utilisateur**\n\n"
                    f"🆔 **ID:** `{user_info['user_id']}`\n"
                    f"👤 **Username:** {username_display}\n"
                    f"💎 **Points:** {user_info['points']} points\n"
                    f"🎭 **Rôle:** {role_display}\n"
                    f"💰 **Réduction:** {reduction_rate}%\n"
                    f"📅 **Créé le:** {created_at_str}\n"
                    f"🔄 **Modifié le:** {updated_at_str}"
                )
                keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="cmd_user")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")
                logger.info(f"Info utilisateur {user_id_to_check} consultée par l'admin {user_id}")
            else:
                await update.message.reply_text(
                    f"❌ Utilisateur `{user_id_to_check}` introuvable.",
                    parse_mode="Markdown"
                )
        except ValueError:
            await update.message.reply_text(
                "❌ ID invalide. Veuillez envoyer uniquement un nombre (ID utilisateur).",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'info utilisateur: {e}")
            await update.message.reply_text(
                "❌ Erreur lors de la récupération des informations.",
                parse_mode="Markdown"
            )
        
        context.user_data.pop('user_info_mode', None)
        return
    
    # Vérifier si l'admin est en train de modifier la réduction
    if 'reduction_edit_mode' in context.user_data and context.user_data.get('reduction_edit_mode') and role == "admin":
        if 'reduction_user_id' not in context.user_data:
            # Première étape : récupérer l'ID utilisateur
            try:
                user_id_to_edit = int(update.message.text.strip())
                user_info = get_user_info(user_id_to_edit)
                if not user_info:
                    await update.message.reply_text(
                        "❌ Utilisateur introuvable. Veuillez réessayer avec un ID valide.",
                        parse_mode="Markdown"
                    )
                    return
                
                current_reduction = user_info.get('reduction', 0)
                context.user_data['reduction_user_id'] = user_id_to_edit
                message = (
                    f"💰 **Modifier la Réduction**\n\n"
                    f"👤 Utilisateur: `{user_id_to_edit}`\n"
                    f"📊 Réduction actuelle: **{current_reduction}%**\n\n"
                    "📝 Envoyez le nouveau taux de réduction (0-100, 2 décimales).\n\n"
                    "💡 Exemple: 30 ou 10.50"
                )
                keyboard = [[InlineKeyboardButton("❌ Annuler", callback_data="config_role")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")
            except ValueError:
                await update.message.reply_text(
                    "❌ ID invalide. Veuillez envoyer uniquement un nombre (ID utilisateur).",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Erreur lors de la modification de réduction: {e}")
                await update.message.reply_text(
                    "❌ Erreur lors de la modification de la réduction.",
                    parse_mode="Markdown"
                )
        else:
            # Deuxième étape : définir la réduction
            try:
                reduction_str = update.message.text.strip().replace(",", ".")
                new_reduction = round(float(reduction_str), 2)
                if new_reduction < 0 or new_reduction > 100:
                    await update.message.reply_text(
                        "❌ La réduction doit être entre 0 et 100. Veuillez réessayer.",
                        parse_mode="Markdown"
                    )
                    return
                
                user_id_to_edit = context.user_data['reduction_user_id']
                if set_user_reduction(user_id_to_edit, new_reduction):
                    await update.message.reply_text(
                        f"✅ **Réduction modifiée !**\n\n"
                        f"👤 Utilisateur: `{user_id_to_edit}`\n"
                        f"💰 Nouvelle réduction: **{new_reduction}**%",
                        parse_mode="Markdown"
                    )
                    logger.info(f"Réduction modifiée pour l'utilisateur {user_id_to_edit} par l'admin {user_id}: {new_reduction}%")
                else:
                    await update.message.reply_text(
                        "❌ Erreur lors de la modification de la réduction.",
                        parse_mode="Markdown"
                    )
            except ValueError:
                await update.message.reply_text(
                    "❌ Valeur invalide. Veuillez envoyer un nombre entre 0 et 100 (ex: 10.50).",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Erreur lors de la modification de réduction: {e}")
                await update.message.reply_text(
                    "❌ Erreur lors de la modification de la réduction.",
                    parse_mode="Markdown"
                )
            
            context.user_data.pop('reduction_edit_mode', None)
            context.user_data.pop('reduction_user_id', None)
        return

    # Vérifier si l'admin est en train de définir la réduction pour un nouveau vendeur (AVANT role_add_mode)
    if 'vendeur_reduction_mode' in context.user_data and context.user_data.get('vendeur_reduction_mode') and role == "admin":
        try:
            reduction_str = update.message.text.strip().replace(",", ".")
            reduction = round(float(reduction_str), 2)
            if reduction < 0 or reduction > 100:
                await update.message.reply_text(
                    "❌ La réduction doit être entre 0 et 100. Veuillez réessayer.",
                    parse_mode="Markdown"
                )
                return

            user_id_vendeur = context.user_data.get('vendeur_user_id')
            if user_id_vendeur and set_user_reduction(user_id_vendeur, reduction):
                context.user_data.pop('vendeur_reduction_mode', None)
                await update.message.reply_text(
                    f"✅ **Vendeur configuré !**\n\n"
                    f"👤 Vendeur: `{user_id_vendeur}`\n"
                    f"💰 Réduction: **{reduction}%**",
                    parse_mode="Markdown"
                )
                context.user_data.pop('vendeur_user_id', None)
                context.user_data.pop('role_add_mode', None)
                context.user_data.pop('role_selected', None)
                logger.info(f"Réduction définie pour le nouveau vendeur {user_id_vendeur} par l'admin {user_id}: {reduction}%")
            else:
                await update.message.reply_text(
                    "❌ Erreur lors de la définition de la réduction.",
                    parse_mode="Markdown"
                )
                context.user_data.pop('vendeur_reduction_mode', None)
                context.user_data.pop('vendeur_user_id', None)
                context.user_data.pop('role_add_mode', None)
                context.user_data.pop('role_selected', None)
        except ValueError:
            await update.message.reply_text(
                "❌ Valeur invalide. Veuillez envoyer un nombre entre 0 et 100 (ex: 10.50).",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Erreur lors de la définition de la réduction pour vendeur: {e}")
            await update.message.reply_text(
                "❌ Erreur lors de la définition de la réduction.",
                parse_mode="Markdown"
            )
        return

    # Vérifier si l'admin est en train d'ajouter un rôle
    if 'role_add_mode' in context.user_data and context.user_data.get('role_add_mode') and role == "admin":
        role_type = context.user_data.get('role_selected')
        if role_type:
            try:
                user_id_to_add = int(update.message.text.strip())
                if user_id_to_add == ADMIN_ID:
                    await update.message.reply_text(
                        "❌ Impossible de modifier le rôle de l'admin principal.",
                        parse_mode="Markdown"
                    )
                elif set_user_role(user_id_to_add, role_type):
                    _ensure_user_tokens(user_id_to_add)
                    role_emoji = "💼" if role_type == "vendeur" else "🛡️"
                    # Si c'est un vendeur, demander la réduction
                    if role_type == "vendeur":
                        context.user_data['vendeur_reduction_mode'] = True
                        context.user_data['vendeur_user_id'] = user_id_to_add
                        message = (
                            f"✅ **Rôle ajouté !**\n\n"
                            f"{role_emoji} L'utilisateur `{user_id_to_add}` a maintenant le rôle **{role_type}**.\n\n"
                            "💰 **Définir la réduction**\n\n"
                            "📝 Envoyez le taux de réduction pour ce vendeur (0-100, 2 décimales).\n\n"
                            "💡 Exemple: 30 ou 10.50"
                        )
                        keyboard = [[InlineKeyboardButton("⏭️ Passer (0%)", callback_data="vendeur_reduction_skip")]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")
                    else:
                        await update.message.reply_text(
                            f"✅ **Rôle ajouté !**\n\n"
                            f"{role_emoji} L'utilisateur `{user_id_to_add}` a maintenant le rôle **{role_type}**.",
                            parse_mode="Markdown"
                        )
                    logger.info(f"Rôle {role_type} ajouté à l'utilisateur {user_id_to_add} par l'admin {user_id}")
                else:
                    await update.message.reply_text(
                        "❌ Erreur lors de l'ajout du rôle.",
                        parse_mode="Markdown"
                    )
            except ValueError:
                await update.message.reply_text(
                    "❌ ID invalide. Veuillez envoyer uniquement un nombre (ID utilisateur).",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Erreur lors de l'ajout de rôle: {e}")
                await update.message.reply_text(
                    "❌ Erreur lors de l'ajout du rôle.",
                    parse_mode="Markdown"
                )

            if 'vendeur_reduction_mode' not in context.user_data:
                context.user_data.pop('role_add_mode', None)
                context.user_data.pop('role_selected', None)
        return

    # Vérifier si l'admin est en train de retirer un rôle
    if 'role_remove_mode' in context.user_data and context.user_data.get('role_remove_mode') and role == "admin":
        role_type = context.user_data.get('role_selected')
        if role_type:
            try:
                user_id_to_remove = int(update.message.text.strip())
                if user_id_to_remove == ADMIN_ID:
                    await update.message.reply_text(
                        "❌ Impossible de modifier le rôle de l'admin principal.",
                        parse_mode="Markdown"
                    )
                elif set_user_role(user_id_to_remove, 'user'):
                    role_emoji = "💼" if role_type == "vendeur" else "🛡️"
                    await update.message.reply_text(
                        f"✅ **Rôle retiré !**\n\n"
                        f"{role_emoji} Le rôle **{role_type}** a été retiré à l'utilisateur `{user_id_to_remove}`.\n"
                        f"Il a maintenant le rôle **user**.",
                        parse_mode="Markdown"
                    )
                    logger.info(f"Rôle {role_type} retiré de l'utilisateur {user_id_to_remove} par l'admin {user_id}")
                else:
                    await update.message.reply_text(
                        "❌ Erreur lors de la suppression du rôle.",
                        parse_mode="Markdown"
                    )
            except ValueError:
                await update.message.reply_text(
                    "❌ ID invalide. Veuillez envoyer uniquement un nombre (ID utilisateur).",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Erreur lors de la suppression de rôle: {e}")
                await update.message.reply_text(
                    "❌ Erreur lors de la suppression du rôle.",
                    parse_mode="Markdown"
                )
            
            context.user_data.pop('role_remove_mode', None)
            context.user_data.pop('role_selected', None)
        return
    
    # Vérifier si l'admin est en train de modifier l'annonce
    if 'config_announcement_edit' in context.user_data and role == "admin":
        edit_mode = context.user_data.get('config_announcement_edit')
        
        if edit_mode == 'text':
            # Modification du texte de l'annonce
            new_text = update.message.text or ""
            if new_text.strip():
                if update_config_value("announcement_text", new_text):
                    success_message = (
                        "✅ **Annonce mise à jour !**\n\n"
                        "Le texte de l'annonce a été modifié avec succès."
                    )
                    logger.info(f"Annonce texte modifiée par l'admin {user_id}")
                else:
                    success_message = "❌ Erreur lors de la mise à jour de l'annonce."
                
                keyboard = [[InlineKeyboardButton("🔙 Retour à la config", callback_data="config_annonce")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                try:
                    await update.message.reply_text(success_message, reply_markup=reply_markup, parse_mode="Markdown")
                except TelegramError as e:
                    logger.error(f"Erreur lors de l'envoi du message de confirmation: {e}")
                
                context.user_data.pop('config_announcement_edit', None)
            return
    
    # Vérifier si l'utilisateur est en train d'éditer une configuration
    if 'config_edit' not in context.user_data:
        # Message texte normal, ne rien faire
        return
    
    config_edit = context.user_data.get('config_edit')
    if not config_edit:
        return
    
    key = config_edit.get('key')
    value_type = config_edit.get('type')
    label = config_edit.get('label')
    
    if not key or not value_type:
        return
    
    # Seuls les admins peuvent modifier la config
    if role != "admin":
        await update.message.reply_text("❌ Accès refusé. Seuls les administrateurs peuvent modifier la configuration.")
        context.user_data.pop('config_edit', None)
        return
    
    try:
        text = update.message.text.strip()
        
        # Validation et conversion selon le type
        if value_type == "float_pct":
            try:
                new_value = round(float(text.replace(",", ".")), 2)
                if new_value < 0 or new_value > 100:
                    await update.message.reply_text(
                        "❌ Erreur: La valeur doit être entre 0 et 100.\n"
                        "Veuillez réessayer ou annuler."
                    )
                    return
            except ValueError:
                await update.message.reply_text(
                    "❌ Erreur: Veuillez entrer un nombre décimal valide (ex: 10.50).\n"
                    "Veuillez réessayer ou annuler."
                )
                return
        elif value_type == "float":
            try:
                new_value = round(float(text.replace(",", ".")), 2)
                if new_value < 0:
                    await update.message.reply_text(
                        "❌ Erreur: La valeur doit être positive ou nulle.\n"
                        "Veuillez réessayer ou annuler."
                    )
                    # Ne pas nettoyer config_edit pour permettre une nouvelle tentative
                    return
            except ValueError:
                await update.message.reply_text(
                    "❌ Erreur: Veuillez entrer un nombre décimal valide (ex: 0.03).\n"
                    "Veuillez réessayer ou annuler."
                )
                # Ne pas nettoyer config_edit pour permettre une nouvelle tentative
                return
        elif value_type == "int":
            try:
                new_value = int(text)
                # Pour les threads staff, on accepte n'importe quel entier (peut être négatif)
                # Pour card_margin, on accepte seulement positif ou nul (0 = pas de marge)
                if key not in ["staff_thread_payment", "staff_thread_entretien", "staff_thread_demande_access"] and new_value < 0:
                    await update.message.reply_text(
                        "❌ Erreur: La valeur doit être un nombre entier positif ou nul.\n"
                        "Veuillez réessayer ou annuler."
                    )
                    # Ne pas nettoyer config_edit pour permettre une nouvelle tentative
                    return
            except ValueError:
                await update.message.reply_text(
                    "❌ Erreur: Veuillez entrer un nombre entier valide.\n"
                    "Veuillez réessayer ou annuler."
                )
                # Ne pas nettoyer config_edit pour permettre une nouvelle tentative
                return
        elif value_type == "str":
            # Validation selon la clé
            if key == "payment_url":
                # Validation URL basique
                if not text.startswith(("http://", "https://")):
                    await update.message.reply_text(
                        "❌ Erreur: Veuillez entrer une URL valide (commençant par http:// ou https://).\n"
                        "Veuillez réessayer ou annuler."
                    )
                    # Ne pas nettoyer config_edit pour permettre une nouvelle tentative
                    return
            elif key == "staff_channel_id":
                # Validation ID de canal (peut être vide pour désactiver)
                if text and not text.startswith("-"):
                    await update.message.reply_text(
                        "❌ Erreur: L'ID du canal doit commencer par '-' (ex: -1001234567890).\n"
                        "Laissez vide pour désactiver.\n"
                        "Veuillez réessayer ou annuler."
                    )
                    # Ne pas nettoyer config_edit pour permettre une nouvelle tentative
                    return
            new_value = text
        else:
            await update.message.reply_text("❌ Type de valeur non supporté.")
            context.user_data.pop('config_edit', None)
            return
        
        # Mettre à jour la configuration
        if update_config_value(key, new_value):
            success_message = (
                f"✅ **Configuration mise à jour avec succès !**\n\n"
                f"**{label}**: {new_value}\n\n"
                "La modification a été enregistrée."
            )
            # Déterminer le menu de retour selon le type de config
            if key == "payment_url":
                back_callback = "config_payement"
            elif key in ["point_min", "point_max", "argent_min", "argent_max"]:
                back_callback = "config_points"
            elif key == "card_margin":
                back_callback = "config_carte"
            elif key in ["staff_channel_id", "staff_thread_payment", "staff_thread_entretien", "staff_thread_demande_access"]:
                back_callback = "config_canal"
            else:
                back_callback = "cmd_config"
            
            keyboard = [[InlineKeyboardButton("🔙 Retour à la config", callback_data=back_callback)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(success_message, reply_markup=reply_markup, parse_mode="Markdown")
            logger.info(f"Configuration mise à jour par l'admin {user_id}: {key} = {new_value}")
        else:
            await update.message.reply_text(
                "❌ Une erreur s'est produite lors de la mise à jour. Veuillez réessayer."
            )
        
        # Nettoyer le contexte
        context.user_data.pop('config_edit', None)
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement du message de config: {e}")
        # Nettoyer le contexte même en cas d'erreur pour éviter de rester bloqué
        context.user_data.pop('config_edit', None)
        try:
            await update.message.reply_text("❌ Une erreur s'est produite. Veuillez réessayer.")
        except TelegramError:
            pass  # Ignorer si l'envoi échoue aussi


async def error_handler(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gère les erreurs du bot de manière complète et sécurisée"""
    error = context.error
    
    if not error:
        logger.warning("error_handler appelé sans erreur")
        return
    
    # Log de l'erreur avec informations complètes
    logger.error(
        f"Exception non gérée: {type(error).__name__}: {error}",
        exc_info=error
    )
    
    # Gestion spécifique selon le type d'erreur
    if isinstance(error, TimedOut):
        logger.warning("Timeout lors d'une requête Telegram")
        return
    
    if isinstance(error, NetworkError):
        logger.warning("Erreur réseau lors d'une requête Telegram")
        return
    
    if isinstance(error, RetryAfter):
        logger.warning(f"Rate limit atteint. Retry après {error.retry_after} secondes")
        return
    
    # Tentative d'envoyer un message d'erreur à l'utilisateur si possible
    if update and update.effective_chat:
        chat_id = update.effective_chat.id
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Une erreur s'est produite. Veuillez réessayer ou utiliser /start pour revenir au menu principal."
            )
        except Exception:
            # Éviter les boucles d'erreur si l'envoi échoue
            logger.error("Impossible d'envoyer le message d'erreur à l'utilisateur")


def main() -> None:
    """Fonction principale pour démarrer le bot"""
    # Initialiser le pool DB (réutilisation des connexions)
    init_db_pool()

    # Vérifier que les tables existent (création/migration gérée par run.py / database_up.py)
    verify_bot_tables_exist()

    # Nettoyage des transactions expirées au démarrage
    cleanup_old_pending_payments(days=7)
    
    # Validation de la configuration
    if not validate_config():
        logger.error("Configuration invalide. Arrêt du bot.")
        return
    
    # Création de l'application (timeouts augmentés pour envoi de photos volumineuses)
    request = HTTPXRequest(
        connect_timeout=10,
        read_timeout=60,
        write_timeout=30
    )
    application = Application.builder().token(BOT_TOKEN).request(request).build()
    
    # Enregistrement des handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("get_chat_id", get_chat_id_command))
    application.add_handler(CommandHandler("version", version_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.PHOTO, photo_message_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    
    # Gestionnaire d'erreurs global
    application.add_error_handler(error_handler)
    
    # Démarrage du bot
    logger.info("Démarrage du bot...")
    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )
    except KeyboardInterrupt:
        logger.info("Arrêt du bot demandé par l'utilisateur (Ctrl+C)")
    except Exception as e:
        logger.error(f"Erreur fatale lors du démarrage du bot: {e}", exc_info=e)
    finally:
        # Toujours fermer le pool PostgreSQL pour libérer les connexions
        close_db_pool()


if __name__ == '__main__':
    main()