"""
Bot Telegram optimisé pour la gestion KFC
Optimisé en sécurité, vitesse et efficacité de logique
"""

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
import json
from io import BytesIO
import qrcode
from PIL import Image
import numpy as np
import math
import re

from creation_log import create_account
from injecteur_log import inject

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

# Charger les variables d'environnement depuis value.env (ou staff.env en secours)
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / "value.env")
load_dotenv(ROOT_DIR / "staff.env")  # secours si value.env absent


# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constantes - Rôles récupérés depuis .env
BOT_TOKEN: Final[str] = os.getenv('BOT_TOKEN', '')
try:
    ADMIN_ID: Final[int] = int(os.getenv('ADMIN_ID', '0'))
    MODERATOR_ID: Final[int] = int(os.getenv('MODERATOR_ID', '0'))
    SELLER_ID: Final[int] = int(os.getenv('SELLER_ID', '0'))
except ValueError as e:
    logger.error(f"Erreur lors de la conversion des IDs: {e}")
    ADMIN_ID: Final[int] = 0
    MODERATOR_ID: Final[int] = 0
    SELLER_ID: Final[int] = 0

# Constantes - Configuration des points (valeurs par défaut)
DEFAULT_POINT_MIN: Final[int] = 150  # Minimum de points (par défaut)
DEFAULT_POINT_MAX: Final[int] = 2500  # Maximum de points (par défaut)
POINT_INCREMENT: Final[int] = 50  # Palier de points (fixe)
DEFAULT_CARD_MARGIN: Final[int] = 300  # Marge par défaut pour l'achat de cartes (points supplémentaires)

# Table de prix par palier (prix pour 1 point, en euros)
# La clé représente le palier minimum de points atteint.
PRICE_TABLE: Final[Dict[int, float]] = {
    1: 0.005000,
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

# Formules d'achat de points : libellé -> points par défaut pour l'interface +/-
POINTS_FORMULA_DEFAULTS: Final[Dict[str, int]] = {
    "solo": 1000,
    "duo": 2500,
    "petit_groupe": 4000,
    "gros_groupe": 8000,
    "revendeur": 10000,
}



# Configuration PostgreSQL local
DB_HOST: Final[str] = os.getenv('DB_HOST', 'localhost')
DB_PORT: Final[int] = int(os.getenv('DB_PORT', '5432'))
DB_NAME: Final[str] = os.getenv('DB_NAME', 'bot_db')
DB_USER: Final[str] = os.getenv('DB_USER', 'postgres')
DB_PASSWORD: Final[str] = os.getenv('DB_PASSWORD', 'postgres')

# Configuration API KFC Cartes
KFC_API_URL: Final[str] = os.getenv('KFC_API_URL', 'http://localhost:8080')
KFC_API_USERNAME: Final[str] = os.getenv('KFC_API_USERNAME', '')
KFC_API_PASSWORD: Final[str] = os.getenv('KFC_API_PASSWORD', '')
KFC_STORAGE_TABLE: Final[str] = os.getenv('KFC_STORAGE_TABLE', 'kfc_storage')

# Mapping des clés config DB -> variables d'environnement (fallback si la DB n'a pas la clé)
CONFIG_KEY_TO_ENV: Final[Dict[str, str]] = {
    "point_min": "CONFIG_POINT_MIN",
    "point_max": "CONFIG_POINT_MAX",
    "card_margin": "CONFIG_CARD_MARGIN",
    "payment_url": "CONFIG_PAYMENT_URL",
    "staff_channel_id": "CONFIG_STAFF_CHANNEL_ID",
    "staff_thread_payment": "CONFIG_STAFF_THREAD_PAYMENT",
    "staff_thread_report": "CONFIG_STAFF_THREAD_REPORT",
    "staff_thread_entretien": "CONFIG_STAFF_THREAD_ENTRETIEN",
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


def init_database() -> None:
    """Initialise la base de données PostgreSQL locale"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Créer la table users si elle n'existe pas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    balance INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0),
                    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'vendeur', 'moderator')),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Ajouter la colonne role si elle n'existe pas déjà (migration)
            cursor.execute("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'users' 
                        AND column_name = 'role'
                    ) THEN
                        ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'vendeur', 'moderator'));
                    END IF;
                END $$;
            """)
            
            # Ajouter la colonne username si elle n'existe pas déjà (migration)
            cursor.execute("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'users' 
                        AND column_name = 'username'
                    ) THEN
                        ALTER TABLE users ADD COLUMN username VARCHAR(255);
                    END IF;
                END $$;
            """)
            
            # Ajouter la colonne reduction si elle n'existe pas déjà (migration)
            cursor.execute("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'users' 
                        AND column_name = 'reduction'
                    ) THEN
                        ALTER TABLE users ADD COLUMN reduction INTEGER DEFAULT 0 CHECK (reduction >= 0 AND reduction <= 100);
                    END IF;
                END $$;
            """)

            # Colonne token_publique pour les revendeurs (vendeur) : dérivé de user_id, non réversible
            cursor.execute("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'users' 
                        AND column_name = 'token_publique'
                    ) THEN
                        ALTER TABLE users ADD COLUMN token_publique VARCHAR(64) DEFAULT '';
                    END IF;
                END $$;
            """)
            
            # Créer la table config pour les paramètres configurables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    key VARCHAR(255) PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Créer la table pending_payments pour les transactions en attente
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pending_payments (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    points INTEGER NOT NULL CHECK (points > 0),
                    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
                    photo_file_id TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) NOT NULL DEFAULT 'pending' 
                        CHECK (status IN ('pending', 'accepted', 'refused', 'cancelled', 'expired')),
                    confirmation_message_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            
            # Modifier la contrainte si elle existe déjà avec l'ancienne valeur (migration)
            cursor.execute("""
                DO $$ 
                BEGIN
                    -- Vérifier si la contrainte existe avec l'ancienne condition
                    IF EXISTS (
                        SELECT 1 FROM information_schema.table_constraints 
                        WHERE constraint_name = 'pending_payments_price_check'
                        AND table_name = 'pending_payments'
                    ) THEN
                        -- Supprimer l'ancienne contrainte
                        ALTER TABLE pending_payments DROP CONSTRAINT IF EXISTS pending_payments_price_check;
                        -- Ajouter la nouvelle contrainte qui permet price >= 0
                        ALTER TABLE pending_payments ADD CONSTRAINT pending_payments_price_check CHECK (price >= 0);
                    END IF;
                END $$;
            """)
            
            # Créer un index unique pour empêcher plusieurs transactions pending par utilisateur
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_one_pending_payment_per_user 
                ON pending_payments (user_id) 
                WHERE status = 'pending'
            """)
            
            # Ajouter la colonne confirmation_message_id si elle n'existe pas déjà (migration)
            cursor.execute("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'pending_payments' 
                        AND column_name = 'confirmation_message_id'
                    ) THEN
                        ALTER TABLE pending_payments ADD COLUMN confirmation_message_id INTEGER;
                    END IF;
                END $$;
            """)

            # Table historique des achats de cartes (numéro de carte, points, date — pas de QR)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS card_purchase_history (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    card_number VARCHAR(255) NOT NULL,
                    points INTEGER NOT NULL CHECK (points > 0),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_card_purchase_history_user_created
                ON card_purchase_history (user_id, created_at DESC)
            """)

            # Insérer les valeurs par défaut si elles n'existent pas
            now = datetime.now().isoformat()
            default_configs = [
                ("point_min", str(DEFAULT_POINT_MIN), now),
                ("point_max", str(DEFAULT_POINT_MAX), now),
                ("card_margin", str(DEFAULT_CARD_MARGIN), now),  # Marge pour l'achat de cartes
                ("payment_url", "https://example.com/pay", now),
                ("staff_channel_id", "", now),
                ("staff_thread_payment", "", now),
                ("emergency_stop", "false", now),  # Arrêt d'urgence (false = actif, true = arrêté)
                ("announcement_text", "Aucune annonce pour le moment.", now),
                ("announcement_photo", "", now)  # file_id de la photo (optionnel)
            ]
            
            for key, value, updated_at in default_configs:
                cursor.execute("""
                    INSERT INTO config (key, value, updated_at) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT (key) DO NOTHING
                """, (key, value, updated_at))
            
            conn.commit()
            logger.info("Base de données PostgreSQL locale initialisée avec succès")
    except (psycopg2.Error, ValueError) as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise


def verify_bot_tables_exist() -> None:
    """
    Vérifie que les tables du bot existent (users, config, pending_payments, card_purchase_history).
    À appeler au démarrage quand le schéma est géré par start.py.
    Lève si une table manque (indiquer de lancer start.py).
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
                        f"Table '{table}' manquante. Lancez start.py pour créer les tables et appliquer les migrations."
                    )
    except (psycopg2.Error, ValueError) as e:
        logger.error(f"Erreur vérification des tables: {e}")
        raise


def get_or_create_user(user_id: int, username: Optional[str] = None) -> tuple[int, bool]:
    """
    Récupère ou crée un utilisateur dans la base de données PostgreSQL.
    Met à jour le username si fourni.
    Retourne (balance, is_new_user)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Vérifier si l'utilisateur existe
            cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            
            if result:
                balance = result[0]
                # Mettre à jour le username si fourni
                if username:
                    cursor.execute(
                        "UPDATE users SET username = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
                        (username, user_id)
                    )
                return balance, False
            else:
                # Créer l'utilisateur avec un solde de 0
                cursor.execute(
                    "INSERT INTO users (user_id, balance, username) VALUES (%s, 0, %s) ON CONFLICT (user_id) DO NOTHING RETURNING balance",
                    (user_id, username)
                )
                if cursor.rowcount > 0:
                    logger.info(f"Nouvel utilisateur créé dans la DB: {user_id}")
                    return 0, True
                else:
                    # L'utilisateur a été créé entre temps, récupérer le solde
                    cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
                    result = cursor.fetchone()
                    return result[0] if result else 0, False
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération/création de l'utilisateur {user_id}: {e}")
        return 0, False


def get_user_count() -> int:
    """Récupère le nombre total d'utilisateurs"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]
    except psycopg2.Error as e:
        logger.error(f"Erreur lors du comptage des utilisateurs: {e}")
        return 0


def get_users_paginated(page: int = 0, per_page: int = 20) -> tuple[list[tuple[int, Optional[str], int, str, int]], int]:
    """
    Récupère une page d'utilisateurs avec pagination.
    Retourne ([(user_id, username, balance, role, reduction), ...], total_pages)
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
                SELECT user_id, username, balance, COALESCE(role, 'user') as role, COALESCE(reduction, 0) as reduction
                FROM users
                ORDER BY user_id
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            
            rows = cursor.fetchall()
            # Corriger le rôle de l'admin principal si présent dans les résultats
            corrected_rows = []
            for uid, username, balance, user_role, reduction in rows:
                if uid == ADMIN_ID:
                    user_role = "admin"
                corrected_rows.append((uid, username, balance, user_role, reduction))
            
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
                SELECT user_id, username, balance, COALESCE(role, 'user') as role, COALESCE(reduction, 0) as reduction, created_at, updated_at
                FROM users
                WHERE user_id = %s
            """, (user_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'user_id': row[0],
                    'username': row[1],
                    'balance': row[2],
                    'role': row[3],
                    'reduction': row[4],
                    'created_at': row[5],
                    'updated_at': row[6]
                }
            return None
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération des infos utilisateur {user_id}: {e}")
        return None


def update_user_balance(user_id: int, points_to_add: int) -> bool:
    """Ajoute des points au solde de l'utilisateur de manière atomique avec lock FOR UPDATE"""
    try:
        if points_to_add <= 0:
            logger.warning(f"Tentative d'ajout de points négatifs ou nuls: {points_to_add}")
            return False
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Lock explicite sur la ligne utilisateur avec FOR UPDATE (évite les race conditions)
            cursor.execute(
                "SELECT balance FROM users WHERE user_id = %s FOR UPDATE",
                (user_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"Tentative de mise à jour du solde pour un utilisateur inexistant: {user_id}")
                return False
            
            # Mise à jour atomique (utilise la valeur actuelle de balance)
            cursor.execute(
                "UPDATE users SET balance = balance + %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
                (points_to_add, user_id)
            )
            
            if cursor.rowcount == 0:
                return False
            
            logger.info(f"Solde mis à jour pour l'utilisateur {user_id}: +{points_to_add} points")
            return True
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la mise à jour du solde pour l'utilisateur {user_id}: {e}")
        return False


def get_user_balance(user_id: int) -> int:
    """Récupère le solde de points de l'utilisateur"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            
            return result[0] if result else 0
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération du solde pour l'utilisateur {user_id}: {e}")
        return 0


def deduct_user_balance_atomic(user_id: int, points_to_deduct: int) -> bool:
    """
    Déduit des points du solde de l'utilisateur de manière atomique avec lock FOR UPDATE.
    Retourne True si la déduction a réussi, False sinon (solde insuffisant ou erreur).
    """
    try:
        if points_to_deduct <= 0:
            logger.warning(f"Tentative de déduction de points négatifs ou nuls: {points_to_deduct}")
            return False
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Lock explicite sur la ligne utilisateur avec FOR UPDATE (évite les race conditions)
            cursor.execute(
                "SELECT balance FROM users WHERE user_id = %s FOR UPDATE",
                (user_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"Tentative de déduction pour un utilisateur inexistant: {user_id}")
                return False
            
            current_balance = result[0]
            
            # Vérifier que le solde est suffisant
            if current_balance < points_to_deduct:
                logger.warning(f"Solde insuffisant pour l'utilisateur {user_id}: {current_balance} < {points_to_deduct}")
                return False
            
            # Mise à jour atomique
            cursor.execute(
                "UPDATE users SET balance = balance - %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
                (points_to_deduct, user_id)
            )
            
            if cursor.rowcount == 0:
                return False
            
            conn.commit()
            logger.info(f"Solde déduit pour l'utilisateur {user_id}: -{points_to_deduct} points (nouveau solde: {current_balance - points_to_deduct})")
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
        # Appel API avec timeout de 30 secondes (l'API peut prendre du temps pour vérifier via KFC)
        response = requests.post(
            f"{KFC_API_URL}/generate",
            json=payload,
            headers=headers,
            timeout=30
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
        elif key == "point_min":
            value_int = int(value)
            if value_int < 0:
                logger.warning(f"Tentative de définir un minimum négatif: {value_int}")
                return False
            value = str(value_int)
        elif key == "point_max":
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
        elif key == "staff_thread_report":
            # Validation ID de thread (peut être vide ou un entier)
            value_str = str(value).strip()
            if value_str:
                try:
                    int(value_str)
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


def get_point_min() -> int:
    """Récupère le minimum de points (avec cache)"""
    return _get_cached_config("point_min", DEFAULT_POINT_MIN)


def get_point_max() -> int:
    """Récupère le maximum de points (avec cache)"""
    return _get_cached_config("point_max", DEFAULT_POINT_MAX)


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


def get_card_margin() -> int:
    """Récupère la marge pour l'achat de cartes (avec cache)"""
    return _get_cached_config("card_margin", DEFAULT_CARD_MARGIN)


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


def get_staff_thread_report() -> Optional[int]:
    """Récupère l'ID du thread de report dans le canal staff (avec cache)"""
    thread_id = _get_cached_config("staff_thread_report", "")
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


def insert_card_purchase_history(user_id: int, card_number: str, points: int) -> bool:
    """Enregistre un achat de carte dans l'historique (sans QR). Retourne True si OK."""
    try:
        card_number_safe = (str(card_number).strip() or "N/A")[:255]
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO card_purchase_history (user_id, card_number, points)
                VALUES (%s, %s, %s)
            """, (user_id, card_number_safe, max(1, int(points))))
        return True
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de l'insertion dans card_purchase_history: {e}")
        return False


def get_user_card_history(user_id: int, limit: int = 5, offset: int = 0) -> list:
    """
    Récupère l'historique des achats de cartes d'un utilisateur (tri par date décroissante).
    Retourne une liste de (id, card_number, points, created_at).
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, card_number, points, created_at
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
    """Récupère un enregistrement d'historique carte par id. Retourne (id, user_id, card_number, points, created_at) ou None."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, user_id, card_number, points, created_at
                FROM card_purchase_history WHERE id = %s
            """, (record_id,))
            return cursor.fetchone()
    except psycopg2.Error as e:
        logger.error(f"Erreur get_card_purchase_by_id: {e}")
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
        keyboard.append([InlineKeyboardButton(f"{d} : {points} pts", callback_data=f"hist_points_detail_{pid}")])
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
    """Construit le clavier pour une page de l'historique cartes. rows = [(id, card_number, points, created_at), ...]"""
    keyboard = []
    for (rid, card_number, points, created_at) in rows:
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
    Vérifie le statut, ajoute les points, et met à jour le statut en une seule opération.
    Retourne (user_id, points, new_balance) si succès, None si échec (déjà traité ou erreur).
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Lock explicite sur la transaction avec FOR UPDATE pour éviter les doubles traitements
            cursor.execute("""
                SELECT id, user_id, points, status 
                FROM pending_payments 
                WHERE id = %s AND status = 'pending'
                FOR UPDATE
            """, (payment_id,))
            
            payment = cursor.fetchone()
            
            if not payment:
                # Transaction déjà traitée ou introuvable
                return None
            
            _, user_id, points, _ = payment
            
            # Vérifier que l'utilisateur existe et lock sur la ligne utilisateur
            cursor.execute(
                "SELECT balance FROM users WHERE user_id = %s FOR UPDATE",
                (user_id,)
            )
            user_result = cursor.fetchone()
            
            if not user_result:
                logger.warning(f"Utilisateur {user_id} introuvable lors de l'acceptation du paiement {payment_id}")
                return None
            
            # Mise à jour atomique : solde + points et statut de la transaction
            cursor.execute("""
                UPDATE users 
                SET balance = balance + %s, updated_at = CURRENT_TIMESTAMP 
                WHERE user_id = %s
            """, (points, user_id))
            
            if cursor.rowcount == 0:
                return None
            
            # Récupérer le nouveau solde
            cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
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
            
            logger.info(f"Paiement {payment_id} accepté atomiquement: user_id={user_id}, points={points}, new_balance={new_balance}")
            return (user_id, points, new_balance)
            
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de l'acceptation atomique du paiement {payment_id}: {e}")
        return None


def validate_config() -> bool:
    """Valide la configuration du bot"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN n'est pas défini dans le fichier staff.env")
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
        logger.warning("Certains IDs de rôles ne sont pas définis dans staff.env")
    
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
        if user_id == SELLER_ID:
            return "vendeur"
        elif user_id == MODERATOR_ID:
            return "moderator"
        return "user"


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
                    "INSERT INTO users (user_id, balance, role) VALUES (%s, 0, %s) ON CONFLICT (user_id) DO UPDATE SET role = %s, updated_at = CURRENT_TIMESTAMP",
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
    Une seule image : même user_id -> même token ; on ne peut pas retrouver user_id à partir du token.
    10 caractères hex (16^10 possibilités) : risque de collision négligeable même avec ~10 000 revendeurs.
    """
    raw = hmac.new(
        _get_token_public_secret(),
        str(user_id).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return raw[:10]


def set_revendeur_public_token(user_id: int) -> bool:
    """
    Génère et enregistre le token public pour un revendeur (vendeur).
    À appeler quand on attribue le rôle vendeur ou au démarrage pour les vendeurs sans token.
    """
    try:
        token = derive_public_token(user_id)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET token_publique = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s AND role = %s",
                (token, user_id, "vendeur"),
            )
            return cursor.rowcount > 0
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de l'enregistrement du token public pour user_id={user_id}: {e}")
        return False


def ensure_revendeur_tokens() -> None:
    """
    Vérifie que tous les utilisateurs avec le rôle vendeur ont un token_publique.
    Appelé au démarrage du bot (après init des tables). Crée les tokens manquants.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id FROM users WHERE role = %s AND (token_publique IS NULL OR token_publique = '')",
                ("vendeur",),
            )
            rows = cursor.fetchall()
        for (uid,) in rows:
            if set_revendeur_public_token(uid):
                logger.info(f"Token public créé pour le vendeur user_id={uid}")
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la vérification des tokens revendeurs: {e}")


def get_users_by_role(role: str) -> list[tuple[int, int]]:
    """Récupère la liste des utilisateurs avec un rôle spécifique (retourne [(user_id, balance), ...])"""
    if role not in ('user', 'vendeur', 'moderator'):
        return []
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, balance FROM users WHERE role = %s ORDER BY user_id",
                (role,)
            )
            return cursor.fetchall()
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération des utilisateurs par rôle {role}: {e}")
        return []


def get_users_with_reduction() -> list[tuple[int, int, str]]:
    """Récupère la liste des utilisateurs avec une réduction > 0 (retourne [(user_id, reduction, role), ...])"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, COALESCE(reduction, 0) as reduction, COALESCE(role, 'user') as role
                FROM users
                WHERE COALESCE(reduction, 0) > 0
                ORDER BY reduction DESC, user_id
            """)
            return cursor.fetchall()
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération des utilisateurs avec réduction: {e}")
        return []


def get_user_reduction(user_id: int) -> int:
    """Récupère le taux de réduction d'un utilisateur (0-100)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(reduction, 0) FROM users WHERE user_id = %s
            """, (user_id,))
            row = cursor.fetchone()
            return row[0] if row else 0
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la récupération de la réduction pour user_id={user_id}: {e}")
        return 0


def set_user_reduction(user_id: int, reduction: int) -> bool:
    """Définit le taux de réduction d'un utilisateur (0-100)"""
    if reduction < 0 or reduction > 100:
        logger.warning(f"Tentative de définir une réduction invalide: {reduction}")
        return False
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # S'assurer que l'utilisateur existe dans la DB
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            if not cursor.fetchone():
                # Créer l'utilisateur s'il n'existe pas
                cursor.execute(
                    "INSERT INTO users (user_id, balance, reduction) VALUES (%s, 0, %s) ON CONFLICT (user_id) DO UPDATE SET reduction = %s, updated_at = CURRENT_TIMESTAMP",
                    (user_id, reduction, reduction)
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
            "cmd_acheter_points",
            "cmd_boutique",
        "boutique_custom",
        "cmd_report",
        "cmd_calc",
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
        "config_payment_url_edit",
        "config_staff_channel_edit",
        "config_staff_thread_payment_edit",
        "config_staff_thread_report_edit",
        "config_annonce_text_edit",
        "config_annonce_photo_edit",
        "config_annonce_photo_delete",
        "payment_accept",
        "payment_refuse",
        "cancel_payment",
        "report_type_achat",
        "report_type_achat_points",
        "report_type_achat_carte",
        "report_type_bot",
        "report_type_autre",
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
        "admin_create_account"
    }
    
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
    
    if callback_data.startswith("report_reply_") or callback_data.startswith("report_ignore_"):
        # Les report_id sont au format user_id_timestamp
        try:
            report_id = callback_data.split("_", 2)[2]  # Prendre tout après report_reply_ ou report_ignore_
            if report_id and len(report_id) > 0:
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
    
    if callback_data.startswith("boutique_points_"):
        # Validation des points boutique (format: boutique_points_N)
        try:
            points = int(callback_data.split("_")[-1])
            if 50 <= points <= 10000:  # Limite raisonnable
                return True
        except (ValueError, IndexError):
            return False
    
    if callback_data.startswith("cancel_payment_"):
        try:
            value = int(callback_data.split("_")[-1])
            if 0 <= value <= 10000:
                return True
        except (ValueError, IndexError):
            return False

    if callback_data.startswith("hist_points_page_") or callback_data.startswith("hist_cartes_page_"):
        try:
            page = int(callback_data.split("_")[-1])
            if page >= 0:
                return True
        except (ValueError, IndexError):
            return False

    if callback_data.startswith("hist_points_detail_") or callback_data.startswith("hist_cartes_detail_"):
        try:
            pid = int(callback_data.split("_")[-1])
            if pid > 0:
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
    quand on injecte des données utilisateur (nom, username, report, etc.).
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
    quand on injecte des données utilisateur (nom, username, report, etc.).
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
    "config_staff_thread_report_edit",
    "config_staff_thread_entretien_edit",
    }
    admin_only_prefixes = (
        "payment_accept_",
        "payment_refuse_",
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
            InlineKeyboardButton("💰 Acheter points", callback_data="cmd_acheter_points"),
            InlineKeyboardButton("🛒 Boutique", callback_data="cmd_boutique")
        ],
        # Catégorie INFORMATIONS (bleu)
        [
            InlineKeyboardButton("📢 Annonces", callback_data="cmd_annonce"),
            InlineKeyboardButton("👤 Mon Profil", callback_data="cmd_moi")
        ],
        # Catégorie AIDE (vert)
        [
            InlineKeyboardButton("📝 Signaler", callback_data="cmd_report"),
            InlineKeyboardButton("🧮 Calculatrice", callback_data="cmd_calc")
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


async def handle_card_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, points: int) -> None:
    """
    Gère l'achat d'une carte KFC avec gestion d'erreurs robuste.
    Points déduits uniquement si la carte est obtenue avec succès.
    """
    query = update.callback_query
    
    # Vérifications préalables
    if points < 50:
        try:
            if query:
                await query.answer("❌ Minimum 50 points requis", show_alert=True)
            else:
                await update.message.reply_text("❌ Minimum 50 points requis.", parse_mode="HTML")
        except:
            pass
        return
    
    # Vérifier le solde actuel
    balance = get_user_balance(user_id)
    if balance < points:
        try:
            if query:
                await query.answer()
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
                    f"❌ Solde insuffisant.\n\nVotre solde : 💎 {balance} points\nPoints requis : 💎 {points} points",
                    parse_mode="HTML"
                )
        except:
            pass
        return
    
    # Afficher message de chargement
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
    
    # Appeler l'API pour générer la carte
    card_data = await generate_kfc_card(points)
    
    if not card_data:
        # Aucune carte disponible
        error_message = (
            f"❌ Aucune carte disponible\n\n"
            f"Malheureusement, aucune carte avec {points} points n'est disponible actuellement.\n\n"
            f"💡 Essayez avec un autre nombre de points."
        )
        keyboard = [[InlineKeyboardButton("🔙 Retour à la boutique", callback_data="cmd_boutique")]]
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
    
    # Carte obtenue : déduire les points de manière atomique
    if not deduct_user_balance_atomic(user_id, points):
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
        keyboard = [[InlineKeyboardButton("🔙 Retour à la boutique", callback_data="cmd_boutique")]]
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
    card_points = card_data.get('point', points)
    insert_card_purchase_history(user_id, str(card_number), int(card_points))
    
    # Succès : afficher les informations de la carte
    
    # Construire le message avec uniquement carte et points (comme demandé)
    success_header = format_header_rich("ACHAT RÉUSSI", "", "success", banner=False)
    
    card_info = (
        f"{success_header}\n\n"
        f"🎴 <b>Carte :</b> <code>{card_number}</code>\n"
        f"💎 <b>Points :</b> {card_points}\n"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Retour à la boutique", callback_data="cmd_boutique")]]
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
        
        logger.info(f"Carte achetée avec succès par l'utilisateur {user_id}: {card_id} ({points} points)")
    except TelegramError as e:
        logger.error(f"Erreur lors de l'affichage de la carte: {e}")


async def show_boutique_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Affiche le menu boutique (fonction helper pour recharger le menu)"""
    query = update.callback_query if update.callback_query else None
    
    balance = get_user_balance(user_id)
    
    header = format_header_rich("🛒 BOUTIQUE", "🛒", "orange", banner=False)
    balance_section = format_highlight_box(f"Votre solde : 💎 {balance} points", "💎", "gold")
    
    intro_section = format_section_rich(
        "Choisissez le nombre de points pour votre carte",
        "Les cartes sont disponibles avec le même nombre de points que vous dépensez",
        "✨",
        "orange",
        highlight=False
    )
    
    message = f"{header}\n\n{balance_section}\n\n{intro_section}\n"
    
    keyboard = [
        [InlineKeyboardButton("💰 600 points", callback_data="boutique_points_600")],
        [InlineKeyboardButton("💰 800 points", callback_data="boutique_points_800")],
        [InlineKeyboardButton("💰 1000 points", callback_data="boutique_points_1000")],
        [InlineKeyboardButton("💰 1200 points", callback_data="boutique_points_1200")],
        [InlineKeyboardButton("💰 1500 points", callback_data="boutique_points_1500")],
        [InlineKeyboardButton("💰 1700 points", callback_data="boutique_points_1700")],
        [InlineKeyboardButton("💰 2000 points", callback_data="boutique_points_2000")],
        [InlineKeyboardButton("💰 2300 points", callback_data="boutique_points_2300")],
        [InlineKeyboardButton("💰 2500 points", callback_data="boutique_points_2500")],
        [InlineKeyboardButton("✏️ Saisie manuelle", callback_data="boutique_custom")],
        [InlineKeyboardButton("🔙 Retour", callback_data="cmd_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if query:
            await safe_edit_message_text(query, message, reply_markup, "HTML")
        else:
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="HTML")
    except TelegramError as e:
        logger.error(f"Erreur lors de l'affichage du menu boutique: {e}")


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le menu principal selon le rôle de l'utilisateur"""
    if not update.effective_user:
        logger.warning("show_main_menu appelé sans utilisateur valide")
        return
    
    user = update.effective_user
    user_id = user.id
    role = get_user_role(user_id)
    
    # Sanitisation du prénom avec HTML
    first_name = escape_html(sanitize_text(user.first_name, 64)) if user.first_name else "Utilisateur"
    
    # Construire le message avec le nouveau système esthétique
    header = format_header_rich("BOT KFC GESTION", "🍗", "orange", banner=False)
    
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

    header = format_header_rich("ACHAT DE POINTS", "💰", "orange", banner=False)
    intro = format_section_rich(
        "Choisissez une formule",
        "Sélectionnez le type d'achat pour partir avec une quantité de points adaptée. Vous pourrez ensuite ajuster !",
        "✨",
        "orange"
    )
    message = f"{header}\n\n{intro}"

    keyboard = [
        [InlineKeyboardButton("Solo", callback_data="points_formula_solo")],
        [InlineKeyboardButton("Duo", callback_data="points_formula_duo")],
        [InlineKeyboardButton("Petit groupe", callback_data="points_formula_petit_groupe")],
        [InlineKeyboardButton("Gros groupe", callback_data="points_formula_gros_groupe")],
        [InlineKeyboardButton("Revendeur", callback_data="points_formula_revendeur")],
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
    
    # Appliquer la réduction de l'utilisateur et calculer le prix
    user_reduction = get_user_reduction(user_id)
    price_initial, price_euros = compute_points_price(selected_points, user_reduction)
    price_per_point = get_price_per_point(selected_points)
    base_unit_price = 0.005  # Prix de base de référence pour 1 point
    if price_per_point > 0:
        # Montant réellement payé pour un panier "théorique" de 100€ au tarif de base,
        # en se basant sur le prix unitaire actuel par rapport au prix de base.
        effective_100 = 100 * (price_per_point / base_unit_price)
    else:
        effective_100 = 100.0
    
    # Construire le message avec le nouveau système esthétique
    header = format_header_rich("ACHAT DE POINTS 💰", "💰", "orange", banner=False)
    
    # Section sélection mise en évidence
    selection_box = format_section_rich(
        "RESUMER",
        "",
        "📊",
        "info"
    )
    
    # Section prix mise en évidence
    if user_reduction > 0:
        price_box = f"<b>- Total : </b>{price_euros:.2f} €"
        reduction_info = f"\n<b>- Prix initial : </b>{price_initial:.2f} €"
    else:
        price_box = f"<b>- Total : </b>{price_euros:.2f} €"
        reduction_info = ""
    
    # Informations en section normale
    info_text = (
        f"💡 Si tu achetais l'équivalent de 100€ au tarif de base , "
        f"avec ton tarif actuel tu paye : <b>{effective_100:.2f}€</b>\n\n"
        f"<i>Utilisez les boutons ci-dessous pour ajuster</i>"
    )
    info_section = format_section_rich(
        "Informations",
        info_text,
        "ℹ️",
        "info"
    )
    
    message = f"{header}\n\n\n{selection_box}\n- <b>{selected_points} points</b>\n{price_box}{reduction_info}\n\n{info_section}"
    
    # Boutons organisés visuellement
    keyboard = [
        [
            InlineKeyboardButton("➖ -50", callback_data=f"points_dec_{selected_points}"),
            InlineKeyboardButton("➕ +50", callback_data=f"points_inc_{selected_points}")
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
        logger.info(f"Interface d'achat de points affichée pour l'utilisateur {user_id} ({selected_points} points)")
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
    context.user_data.pop(f'waiting_report_{user_id}', None)
    context.user_data.pop(f'report_type_{user_id}', None)
    context.user_data.pop('config_edit', None)
    
    # Créer ou récupérer l'utilisateur dans la base de données
    username = user.username if user.username else None
    balance, is_new = get_or_create_user(user_id, username)
    
    # Si c'est un membre normal, afficher message de bienvenu et rediriger vers shop
    if role == "user":
        first_name = escape_html(sanitize_text(user.first_name, 64)) if user.first_name else "Utilisateur"
        
        # Construire le message avec le nouveau système esthétique
        header = format_header_rich("BOT KFC GESTION", "🍗", "orange", banner=False)
        welcome_section = format_section_rich(
            f"Salut {first_name} !",
            "Bienvenue sur le bot de gestion KFC.",
            "👋",
            "gold",
            highlight=True
        )
        footer = "\n✨ Accédez au shop pour découvrir toutes nos fonctionnalités !"
        
        welcome_message = f"{header}\n\n{welcome_section}\n\n{footer}"
        keyboard = [[InlineKeyboardButton("🛒 Accéder au Shop", callback_data="cmd_shop")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="HTML")
            logger.info(f"Message de bienvenu affiché pour le membre {user.id}, redirection vers shop")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'envoi du message de bienvenu: {e}")
    else:
        # Pour admin et vendeur, afficher le menu principal
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
        "cmd_report": ("📝 **Signaler un problème**\n\nUtilisez cette fonction pour signaler un problème.", "shop"),
        "cmd_calc": ("🧮 **Calculatrice**\n\nFonction calculatrice à venir.", "shop"),
    }
    
    return commands.get(callback_data, ("❌ Commande non reconnue.", "menu"))


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gère les callbacks des boutons inline avec validation et sécurité"""
    if not update.callback_query:
        logger.warning("button_callback appelé sans callback_query")
        return
    
    query = update.callback_query
    
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
    
    # Gestion de la boutique (achat de cartes KFC)
    if callback_data == "cmd_boutique":
        context.user_data.pop(f'boutique_custom_{user_id}', None)  # Annuler le mode saisie manuelle
        await show_boutique_menu(update, context, user_id)
        return
    
    # Gestion de la sélection de points prédéfinis
    if callback_data.startswith("boutique_points_"):
        try:
            points = int(callback_data.split("_")[-1])
            await handle_card_purchase(update, context, user_id, points)
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur lors de la récupération des points depuis callback: {e}")
            await query.answer("❌ Erreur", show_alert=True)
        return
    
    # Gestion de la saisie manuelle
    if callback_data == "boutique_custom":
        context.user_data[f'boutique_custom_{user_id}'] = True
        
        header = format_header_rich("SAISIE MANUELLE", "✏️", "orange", banner=False)
        message = f"{header}\n\n📝 Entrez le nombre de points souhaité (minimum 50) :"
        keyboard = [[InlineKeyboardButton("❌ Annuler", callback_data="cmd_boutique")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await safe_edit_message_text(query, message, reply_markup, "HTML")
            await query.answer("⚠️ Entrez maintenant le nombre de points")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage de la saisie manuelle: {e}")
        return
    
    # Gestion de "Ignorer" un report
    if callback_data.startswith("report_ignore_") and role == "admin":
        try:
            report_id = callback_data.split("_", 2)[2]
            report_info = context.bot_data.get(f'report_info_{report_id}')
            
            if report_info:
                report_type = report_info.get('report_type', '📝 Report')
                
                # Modifier le message pour indiquer qu'il a été ignoré
                ignored_message = (
                    f"⏭️ **REPORT IGNORÉ**\n\n"
                    f"{report_type}\n\n"
                    f"👤 **Utilisateur:**\n"
                    f"🆔 ID: `{report_info.get('user_id')}`\n"
                    f"👤 Nom: {report_info.get('first_name', 'N/A')}\n"
                    f"📱 Username: @{report_info.get('username', 'N/A')}\n\n"
                    f"📝 **Message:**\n{escape_markdown(sanitize_text(report_info.get('report_text', ''), 4096))}"
                )
                
                try:
                    await query.message.edit_text(
                        ignored_message,
                        parse_mode="Markdown"
                    )
                    await query.answer("⏭️ Report ignoré")
                    logger.info(f"Report {report_id} ignoré par l'admin {user_id}")
                except TelegramError as e:
                    logger.error(f"Erreur lors de la modification du message ignoré: {e}")
                    await query.answer("✅ Report ignoré", show_alert=False)
            else:
                await query.answer("❌ Report introuvable", show_alert=True)
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur lors de l'ignorance du report: {e}")
            await query.answer("❌ Erreur lors du traitement", show_alert=True)
        return
    
    # Gestion de "Répondre" à un report
    if callback_data.startswith("report_reply_") and role == "admin":
        try:
            report_id = callback_data.split("_", 2)[2]
            report_info = context.bot_data.get(f'report_info_{report_id}')
            
            if report_info:
                # Activer le mode réponse
                context.user_data['report_reply_mode'] = True
                context.user_data['report_reply_id'] = report_id
                
                report_type = escape_html(report_info.get('report_type', '📝 Report'))
                first_name = escape_html(report_info.get('first_name', 'N/A'))
                username = escape_html(report_info.get('username', 'N/A'))
                
                header = format_header_rich("RÉPONDRE AU REPORT", "💬", "info", banner=False)
                
                info_section = format_section_rich(
                    "Informations",
                    "",
                    "ℹ️",
                    "info"
                )
                info_content = (
                    f"{format_info_card('Type', report_type, '📋')}\n"
                    f"{format_info_card('Utilisateur', f'{first_name} (@{username})', '👤')}"
                )
                
                message = f"{header}\n\n{info_section}\n{info_content}\n\n📝 Écrivez votre réponse ci-dessous :"
                
                keyboard = [[InlineKeyboardButton("❌ Annuler", callback_data=f"report_ignore_{report_id}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                try:
                    await query.message.reply_text(message, reply_markup=reply_markup, parse_mode="HTML")
                    await query.answer("⚠️ Écrivez maintenant votre réponse")
                    logger.info(f"Mode réponse activé pour le report {report_id} par l'admin {user_id}")
                except TelegramError as e:
                    logger.error(f"Erreur lors de l'affichage du message de réponse: {e}")
            else:
                await query.answer("❌ Report introuvable", show_alert=True)
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur lors de l'activation de la réponse: {e}")
            await query.answer("❌ Erreur lors du traitement", show_alert=True)
        return
    
    # Gestion de "Moi" - affichage du profil avec solde et bannière
    if callback_data == "cmd_moi":
        balance = get_user_balance(user_id)
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
        
        # Solde mis en évidence avec highlight box
        solde_box = format_highlight_box(f"{balance} points", "💎", "gold")
        
        message = f"{header}\n\n{info_section}\n{info_content}\n\n{solde_box}"
        keyboard = [
            [InlineKeyboardButton("📜 Historique", callback_data="cmd_historique")],
            [InlineKeyboardButton("🔙 Retour au shop", callback_data="cmd_shop")]
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
            [InlineKeyboardButton("💰 Historique points", callback_data="hist_points")],
            [InlineKeyboardButton("🎴 Historique cartes", callback_data="hist_cartes")],
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
        header = format_header_rich("HISTORIQUE POINTS", "💰", "purple", banner=False)
        count_line = f"\n📋 <b>{total}</b> commande(s) au total.\n" if total else "\n"
        if not rows:
            msg = f"{header}\n\nAucun achat de points enregistré."
            keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="cmd_historique")]]
        else:
            msg = f"{header}{count_line}\nSélectionnez une commande pour voir le détail (date, points, prix)."
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
            await query.answer("Erreur pagination.", show_alert=True)
            return
        PAGE_SIZE = 5
        context.user_data["hist_points_page"] = page
        offset = page * PAGE_SIZE
        total = get_user_payment_history_count(user_id)
        rows = get_user_payment_history(user_id, limit=PAGE_SIZE, offset=offset)
        header = format_header_rich("HISTORIQUE POINTS", "💰", "purple", banner=False)
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
            await query.answer("Commande introuvable.", show_alert=True)
            return
        payment = get_pending_payment(payment_id)
        if not payment or payment[1] != user_id:
            await query.answer("Commande introuvable.", show_alert=True)
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
        header = format_header_rich("DÉTAIL COMMANDE POINTS", "💰", "purple", banner=False)
        detail_msg = (
            f"{header}\n\n"
            f"📅 <b>Date :</b> {escape_html(str(date_exact))}\n"
            f"💎 <b>Points :</b> {points}\n"
            f"💳 <b>Prix :</b> {price_str}"
        )
        keyboard = [[InlineKeyboardButton("🔙 Retour à la liste", callback_data=f"hist_points_page_{page}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await safe_edit_message_text(query, detail_msg, reply_markup, "HTML")
            await query.answer()
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
            await query.answer("Erreur pagination.", show_alert=True)
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
            await query.answer("Commande introuvable.", show_alert=True)
            return
        row = get_card_purchase_by_id(record_id)
        if not row or row[1] != user_id:
            await query.answer("Commande introuvable.", show_alert=True)
            return
        _id, _user_id, card_number, points, created_at = row
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
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await safe_edit_message_text(query, detail_msg, reply_markup, "HTML")
            await query.answer()
        except TelegramError as e:
            logger.error(f"Erreur affichage détail historique cartes: {e}")
        return

    # Gestion de "Report" - affichage du menu de sélection du type de report
    if callback_data == "cmd_report":
        # Nettoyer les états précédents
        context.user_data.pop(f'waiting_report_{user_id}', None)
        context.user_data.pop(f'report_type_{user_id}', None)
        
        header = format_header_rich("SIGNALER UN PROBLÈME", "📝", "warning", banner=False)
        intro_section = format_section_rich(
            "Sélectionnez le type de report",
            "",
            "✨",
            "warning",
            highlight=False
        )
        message = f"{header}\n\n{intro_section}\n"
        
        keyboard = [
            [InlineKeyboardButton("🛒 Problème d'achat", callback_data="report_type_achat")],
            [InlineKeyboardButton("🤖 Problème avec le bot", callback_data="report_type_bot")],
            [InlineKeyboardButton("❓ Question autre", callback_data="report_type_autre")],
            [InlineKeyboardButton("🔙 Retour", callback_data="cmd_shop")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await safe_edit_message_text(query, message, reply_markup, "HTML")
            logger.info(f"Menu report affiché pour l'utilisateur {user_id}")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage du menu report: {e}")
        return
    
    # Gestion du sous-menu "Problème d'achat"
    if callback_data == "report_type_achat":
        header = format_header_rich("PROBLÈME D'ACHAT", "🛒", "warning", banner=False)
        intro_section = format_section_rich(
            "Sélectionnez le type d'achat concerné",
            "",
            "✨",
            "warning",
            highlight=False
        )
        message = f"{header}\n\n{intro_section}\n"
        keyboard = [
            [InlineKeyboardButton("💰 Achat de points", callback_data="report_type_achat_points")],
            [InlineKeyboardButton("🎴 Achat de carte", callback_data="report_type_achat_carte")],
            [InlineKeyboardButton("🔙 Retour", callback_data="cmd_report")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await safe_edit_message_text(query, message, reply_markup, "HTML")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage du sous-menu achat: {e}")
        return
    
    # Gestion de la sélection du type de report (points, carte, bot, autre)
    if callback_data in {"report_type_achat_points", "report_type_achat_carte", "report_type_bot", "report_type_autre"}:
        # Définir les titres des types de reports
        report_titles = {
            "report_type_achat_points": "🛒 Problème d'achat de points",
            "report_type_achat_carte": "🛒 Problème d'achat de carte",
            "report_type_bot": "🤖 Problème avec le bot",
            "report_type_autre": "❓ Question autre"
        }
        
        report_title = report_titles[callback_data]
        
        # Stocker le type de report
        context.user_data[f'report_type_{user_id}'] = report_title
        # Activer le mode attente de report
        context.user_data[f'waiting_report_{user_id}'] = True
        
        # Extraire l'emoji et le titre
        emoji_map = {
            "🛒 Problème d'achat de points": ("💰", "warning"),
            "🛒 Problème d'achat de carte": ("🎴", "warning"),
            "🤖 Problème avec le bot": ("🤖", "danger"),
            "❓ Question autre": ("❓", "info")
        }
        emoji, theme = emoji_map.get(report_title, ("📝", "info"))
        
        header = format_header_rich(report_title.replace("🛒 ", "").replace("🤖 ", "").replace("❓ ", ""), emoji, theme, banner=False)
        message = f"{header}\n\n📝 Écrivez votre report :"
        keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="cmd_report")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await safe_edit_message_text(query, message, reply_markup, "HTML")
            logger.info(f"Mode report activé pour l'utilisateur {user_id} (type: {report_title}), flag waiting_report_{user_id} = {context.user_data.get(f'waiting_report_{user_id}')}")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'affichage du message report: {e}")
        return
    
    # Gestion de /config pour l'admin
    if callback_data == "cmd_config" and role == "admin":
        message = "⚙️ **Configuration Admin**\n\nSélectionnez une option :"
        keyboard = [
            [InlineKeyboardButton("👤 Rôle", callback_data="config_role")],
            [InlineKeyboardButton("💳 Paiement", callback_data="config_payement")],
            [InlineKeyboardButton("💰 Points", callback_data="config_points")],
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
                message += f"{idx}. `{uid}` - {reduction_rate}% - {role_display}\n"
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
            await query.answer("⚠️ Envoyez maintenant l'ID utilisateur")
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
            await query.answer("⚠️ Envoyez maintenant l'ID utilisateur")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'activation du mode modification de réduction: {e}")
        return
    
    # Gestion du callback pour passer la réduction (0%)
    if callback_data == "vendeur_reduction_skip" and role == "admin":
        user_id_vendeur = context.user_data.get('vendeur_user_id')
        if user_id_vendeur:
            if set_user_reduction(user_id_vendeur, 0):
                await query.answer("✅ Réduction définie à 0%")
                await query.edit_message_text(
                    f"✅ **Réduction définie !**\n\n"
                    f"👤 Vendeur: `{user_id_vendeur}`\n"
                    f"💰 Réduction: **0%**",
                    parse_mode="Markdown"
                )
                logger.info(f"Réduction définie à 0% pour le nouveau vendeur {user_id_vendeur} par l'admin {user_id}")
            else:
                await query.answer("❌ Erreur lors de la définition de la réduction")
        
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
            await query.answer("⚠️ Envoyez maintenant l'ID utilisateur")
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
            await query.answer("⚠️ Envoyez maintenant l'ID utilisateur")
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
        
        point_min = get_point_min()
        point_max = get_point_max()
        
        message = (
            "💰 **Configuration des Points**\n\n"
            f"📊 Minimum: **{point_min} points**\n"
            f"📈 Maximum: **{point_max} points**\n\n"
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
    
    # Gestion de config_carte (marge pour l'achat de cartes)
    if callback_data == "config_carte" and role == "admin":
        # Nettoyer config_edit si présent (annulation d'édition)
        context.user_data.pop('config_edit', None)
        
        card_margin = get_card_margin()
        
        message = (
            "🎴 **Configuration des Cartes**\n\n"
            f"📊 Marge actuelle: **{card_margin} points**\n\n"
            "La marge définit le nombre de points supplémentaires autorisés lors de la recherche d'une carte.\n"
            f"Par exemple, si un utilisateur demande 500 points avec une marge de {card_margin}, "
            f"le système cherchera une carte entre 500 et {500 + card_margin} points.\n\n"
            "Sélectionnez une action :"
        )
        keyboard = [
            [InlineKeyboardButton("📊 Modifier la marge", callback_data="config_card_margin_edit")],
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
        staff_thread_report = get_staff_thread_report()
        staff_thread_report_str = str(staff_thread_report) if staff_thread_report else "Non configuré"
        staff_thread_entretien = get_staff_thread_entretien()
        staff_thread_entretien_str = str(staff_thread_entretien) if staff_thread_entretien else "Non configuré"

        message = (
            "📢 **Configuration du Canal Staff**\n\n"
            f"📢 Canal Staff: `{staff_channel}`\n"
            f"🧵 Thread Paiement: `{staff_thread_payment_str}`\n"
            f"📝 Thread Report: `{staff_thread_report_str}`\n"
            f"🔧 Thread Entretien: `{staff_thread_entretien_str}`\n\n"
            "Sélectionnez un paramètre à modifier :"
        )
        keyboard = [
            [InlineKeyboardButton("📢 Modifier le Canal Staff", callback_data="config_staff_channel_edit")],
            [InlineKeyboardButton("🧵 Modifier le Thread Paiement", callback_data="config_staff_thread_payment_edit")],
            [InlineKeyboardButton("📝 Modifier le Thread Report", callback_data="config_staff_thread_report_edit")],
            [InlineKeyboardButton("🔧 Modifier le Thread Entretien", callback_data="config_staff_thread_entretien_edit")],
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
            await query.answer("⚠️ Envoyez maintenant le JSON du compte")
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
        # TOUJOURS répondre à Telegram immédiatement (même si on ignore le clic)
        # Sinon Telegram freeze le bot
        try:
            await query.answer()  # Réponse immédiate obligatoire
        except TelegramError:
            pass
        
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
                    f"❌ Le nombre de points doit être entre {point_min} et {point_max}.",
                    create_back_button("shop"),
                    "HTML"
                )
                return
            
            if points_to_add <= 0:
                await safe_edit_message_text(
                    query,
                    "❌ Le nombre de points doit être supérieur à 0.",
                    create_back_button("shop"),
                    "HTML"
                )
                return
            
            # Calculer le prix selon la table de paliers
            user_reduction = get_user_reduction(user_id)
            price_initial, price_euros = compute_points_price(points_to_add, user_reduction)
            
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
            if user_reduction > 0:
                detail_content = (
                    f"{format_info_card('Points à acheter', str(points_to_add), '📊')}\n"
                    f"{format_info_card('Prix initial', f'{price_initial:.2f} €', '💵')}\n"
                    f"{format_info_card('Total après réduction', f'{price_euros:.2f} €', '💵', value_highlight=True)}"
                )
            else:
                detail_content = (
                    f"{format_info_card('Points à acheter', str(points_to_add), '📊')}\n"
                    f"{format_info_card('Total', f'{price_euros:.2f} €', '💵', value_highlight=True)}"
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
                "📸 Après avoir effectué le paiement, veuillez envoyer une capture d'écran comme preuve de paiement.\n\n⏳ Votre transaction est en attente de validation.",
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
                    logger.info(f"Prix final = 0€ pour user_id={user_id}, points={points_to_add} (réduction={user_reduction}%). Création et acceptation automatique.")
                    
                    # Créer la transaction avec statut 'pending' d'abord
                    payment_id = create_pending_payment(user_id, points_to_add, price_euros)
                    if payment_id and payment_id > 0:
                        # Accepter automatiquement la transaction
                        result = accept_payment_atomic(payment_id)
                        if result:
                            payment_user_id, payment_points, new_balance = result
                            logger.info(f"Transaction {payment_id} acceptée automatiquement (prix=0€). Points ajoutés: {payment_points}, nouveau solde: {new_balance}")
                            
                            # Afficher un message de succès
                            success_header = format_header_rich("TRANSACTION ACCEPTÉE", "✅", "success", banner=False)
                            success_section = format_section_rich(
                                "Statut",
                                f"Votre achat de {payment_points} points a été accepté automatiquement (prix final: 0€).\n\nVotre nouveau solde est de {new_balance} points.",
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
                await query.answer("⏳ Traitement en cours...", show_alert=False)
                return
            context.user_data[payment_action_key] = True
            
            try:
                # Récupérer les infos de la transaction pour l'affichage (avant acceptation atomique)
                payment = get_pending_payment(payment_id)
                if not payment:
                    await query.answer("❌ Transaction introuvable.", show_alert=True)
                    return
                
                _, payment_user_id, points, price, photo_file_id, created_at, _, confirmation_message_id = payment[:8]
                
                # Acceptation atomique (vérifie statut, ajoute points, met à jour statut en une transaction)
                result = accept_payment_atomic(payment_id)
                
                if result:
                    payment_user_id, points, new_balance = result
                    
                    # Message de confirmation avec le nouveau système esthétique
                    header = format_header_rich("PAIEMENT ACCEPTÉ", "✅", "success", banner=False)
                    
                    success_section = format_section_rich(
                        "Points ajoutés",
                        f"<b>{points} points</b> ont été ajoutés à votre compte",
                        "💰",
                        "success",
                        highlight=True
                    )
                    
                    solde_badge = format_highlight_box(f"Nouveau solde : {new_balance} points", "💎", "gold")
                    
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
                        await query.answer("✅ Paiement accepté")
                    except TelegramError as e:
                        logger.error(f"Erreur lors de la mise à jour du message admin: {e}")
                        # Fallback si edit_caption échoue
                        try:
                            await query.edit_message_text(
                                admin_status_message,
                                parse_mode="HTML"
                            )
                            await query.answer("✅ Paiement accepté")
                        except TelegramError:
                            await query.answer("✅ Paiement accepté", show_alert=True)
                    
                    logger.info(f"Paiement {payment_id} accepté par l'admin {user_id}")
                else:
                    # Transaction déjà traitée ou erreur
                    await query.answer("❌ Transaction déjà traitée ou introuvable.", show_alert=True)
            finally:
                # Libérer le debouncing après 2 secondes
                async def release_action():
                    await asyncio.sleep(2.0)
                    context.user_data.pop(payment_action_key, None)
                asyncio.create_task(release_action())
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur lors de l'acceptation du paiement: {e}")
            await query.answer("❌ Erreur lors du traitement.", show_alert=True)
            # Libérer le debouncing même en cas d'erreur
            if 'payment_action_key' in locals():
                context.user_data.pop(payment_action_key, None)
        return
    
    if callback_data.startswith("payment_refuse_") and role == "admin":
        try:
            payment_id = int(callback_data.split("_")[-1])
            
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
                    await query.answer("❌ Transaction déjà traitée ou introuvable.", show_alert=True)
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
                    await query.answer("❌ Transaction déjà traitée.", show_alert=True)
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
                await query.answer("❌ Paiement refusé")
            except TelegramError as e:
                logger.error(f"Erreur lors de la mise à jour du message admin: {e}")
                # Fallback si edit_caption échoue
                try:
                    await query.edit_message_text(
                        admin_status_message,
                        parse_mode="HTML"
                    )
                    await query.answer("❌ Paiement refusé")
                except TelegramError:
                    await query.answer("❌ Paiement refusé", show_alert=True)
            
                logger.info(f"Paiement {payment_id} refusé par l'admin {user_id}")
            finally:
                # Libérer le debouncing après 2 secondes
                async def release_action():
                    await asyncio.sleep(2.0)
                    context.user_data.pop(payment_action_key, None)
                asyncio.create_task(release_action())
        except (ValueError, IndexError) as e:
            logger.error(f"Erreur lors du refus du paiement: {e}")
            await query.answer("❌ Erreur lors du traitement.", show_alert=True)
            # Libérer le debouncing même en cas d'erreur
            context.user_data.pop(payment_action_key, None)
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
            await query.answer("⚠️ Envoyez maintenant le nouveau texte de l'annonce")
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
            await query.answer("⚠️ Envoyez maintenant une photo (avec caption optionnel)")
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
                         "config_payment_url_edit", "config_staff_channel_edit", "config_staff_thread_payment_edit", 
                         "config_staff_thread_report_edit"} and role == "admin":
        config_labels = {
            "config_min_edit": ("Minimum de points", "point_min", "int"),
            "config_max_edit": ("Maximum de points", "point_max", "int"),
            "config_card_margin_edit": ("Marge pour l'achat de cartes (points)", "card_margin", "int"),
            "config_payment_url_edit": ("URL de paiement", "payment_url", "str"),
            "config_staff_channel_edit": ("ID du Canal Staff (commence par -)", "staff_channel_id", "str"),
            "config_staff_thread_payment_edit": ("ID du Thread Paiement (nombre)", "staff_thread_payment", "int"),
            "config_staff_thread_report_edit": ("ID du Thread Report (nombre)", "staff_thread_report", "int"),
            "config_staff_thread_entretien_edit": ("ID du Thread Entretien (nombre)", "staff_thread_entretien", "int")
        }
        
        label, key, value_type = config_labels[callback_data]
        
        # Valeur par défaut selon le type
        if value_type == "int":
            if key in ["staff_thread_payment", "staff_thread_report", "staff_thread_entretien"]:
                current_value = get_config_value(key, "")
            elif key == "card_margin":
                current_value = get_config_value(key, DEFAULT_CARD_MARGIN)
            else:
                current_value = get_config_value(key, 150)
        else:
            if key == "staff_channel_id":
                current_value = get_config_value(key, "")
            else:
                current_value = get_config_value(key, "https://example.com/pay")
        
        message = (
            f"⚙️ **Modifier {label}**\n\n"
            f"Valeur actuelle: **{current_value}**\n\n"
            f"Veuillez envoyer la nouvelle valeur.\n"
            f"Type attendu: {'Nombre décimal' if value_type == 'float' else 'Nombre entier'}\n"
            f"⚠️ La valeur doit être {'strictement positive' if value_type == 'float' else 'positive ou nulle'}"
        )
        
        # Stocker dans context pour récupération après
        context.user_data['config_edit'] = {'key': key, 'type': value_type, 'label': label}
        
        # Déterminer le menu de retour selon le type de config
        if key == "payment_url":
            back_callback = "config_payement"
        elif key in ["point_min", "point_max"]:
            back_callback = "config_points"
        elif key == "card_margin":
            back_callback = "config_carte"
        elif key in ["staff_channel_id", "staff_thread_payment", "staff_thread_report", "staff_thread_entretien"]:
            back_callback = "config_canal"
        else:
            back_callback = "cmd_config"
        
        keyboard = [[InlineKeyboardButton("❌ Annuler", callback_data=back_callback)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
            await query.answer("⚠️ Envoyez maintenant la nouvelle valeur en message texte")
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
            await query.answer("❌ Erreur lors de la pagination", show_alert=True)
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
            await query.answer("⚠️ Envoyez maintenant l'ID utilisateur")
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
    role = get_user_role(user_id)
    
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
                [InlineKeyboardButton("💰 Acheter des points", callback_data="cmd_acheter_points")],
                [InlineKeyboardButton("🛒 Boutique", callback_data="cmd_boutique")],
                [InlineKeyboardButton("📝 Report", callback_data="cmd_report")],
                [InlineKeyboardButton("🧮 Calculatrice", callback_data="cmd_calc")],
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
        
        logger.info(f"Envoi de la preuve de paiement à l'admin pour la transaction {payment_id} (user_id={user_id}, points={points}, price={price:.2f}€)")
        
        # Récupérer la réduction de l'utilisateur pour afficher les détails
        user_reduction = get_user_reduction(payment_user_id)
        
        # Convertir price en float si c'est un Decimal (venant de PostgreSQL)
        price_float = float(price) if hasattr(price, '__float__') else price
        
        # Construire le message pour l'admin
        admin_message_lines = [
            "📸 **Nouvelle preuve de paiement reçue**\n",
            f"👤 Utilisateur: {user.first_name or 'N/A'} (@{user.username or 'N/A'})",
            f"🆔 ID: `{payment_user_id}`",
            f"💰 Points: **{points}**"
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
    role = get_user_role(user_id)
    
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

    # Vérifier si l'utilisateur est en train de saisir un nombre de points pour la boutique
    if context.user_data.get(f'boutique_custom_{user_id}', False):
        try:
            points = int(update.message.text.strip())
            
            # Validation
            if points < 50:
                await update.message.reply_text(
                    "❌ Minimum 50 points requis.\n\nVeuillez entrer un nombre valide (minimum 50).",
                    parse_mode="HTML"
                )
                return
            
            # Nettoyer le flag
            context.user_data.pop(f'boutique_custom_{user_id}', None)
            
            # Supprimer le message de l'utilisateur
            try:
                await update.message.delete()
            except:
                pass
            
            # Traiter l'achat
            await handle_card_purchase(update, context, user_id, points)
            
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
    
    # IMPORTANT: Vérifier EN PREMIER si l'utilisateur est en train d'envoyer un report
    # Cette vérification doit être AVANT toutes les autres pour éviter que les messages soient interceptés
    waiting_report = context.user_data.get(f'waiting_report_{user_id}', False)
    if waiting_report:
        logger.info(f"Report détecté pour l'utilisateur {user_id}, flag: {waiting_report}")
        # Récupérer le message de report
        report_text_raw = update.message.text or ""
        
        if not report_text_raw.strip():
            # Message vide, ne rien faire
            logger.warning(f"Message de report vide pour l'utilisateur {user_id}")
            return
        
        # Récupérer le type de report
        report_type = context.user_data.get(f'report_type_{user_id}', "📝 Report")
        logger.info(f"Traitement du report pour l'utilisateur {user_id}, type: {report_type}")
        
        # Supprimer le message de l'utilisateur
        try:
            await update.message.delete()
        except TelegramError as e:
            logger.warning(f"Impossible de supprimer le message de report de l'utilisateur {user_id}: {e}")
        
        # Nettoyer les flags
        context.user_data.pop(f'waiting_report_{user_id}', None)
        context.user_data.pop(f'report_type_{user_id}', None)
        
        # Afficher le message de confirmation
        try:
            await update.message.reply_text("✅ **Report réussi**\n\nVotre report a été envoyé à l'administration.", parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'envoi du message de confirmation: {e}")
        
        # Envoyer le report au thread staff
        first_name = escape_markdown(sanitize_text(user.first_name, 64)) if user.first_name else "N/A"
        username = escape_markdown(user.username or 'N/A')
        report_text = escape_markdown(sanitize_text(report_text_raw, 4096))
        
        # Créer un identifiant unique pour ce report (user_id + timestamp)
        import time
        report_id = f"{user_id}_{int(time.time())}"
        
        report_message = (
            f"{report_type}\n\n"
            f"👤 **Utilisateur:**\n"
            f"🆔 ID: `{user_id}`\n"
            f"👤 Nom: {first_name}\n"
            f"📱 Username: @{username}\n\n"
            f"📝 **Message:**\n{report_text}"
        )
        
        # Créer les boutons de réponse
        keyboard = [
            [
                InlineKeyboardButton("✅ Répondre", callback_data=f"report_reply_{report_id}"),
                InlineKeyboardButton("⏭️ Ignorer", callback_data=f"report_ignore_{report_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Stocker les infos du report pour pouvoir y répondre
        context.bot_data[f'report_info_{report_id}'] = {
            'user_id': user_id,
            'report_type': report_type,
            'report_text': report_text_raw,
            'username': username,
            'first_name': first_name
        }
        
        staff_thread_report = get_staff_thread_report()
        success = await send_to_staff_channel(
            context.bot,
            report_message,
            thread_id=staff_thread_report,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
        if success:
            if staff_thread_report:
                logger.info(f"Report {report_id} envoyé au thread staff {staff_thread_report} par l'utilisateur {user_id}")
            else:
                logger.info(f"Report {report_id} envoyé à l'admin directement (thread non configuré) par l'utilisateur {user_id}")
        else:
            logger.error(f"Échec de l'envoi du report {report_id} pour l'utilisateur {user_id}")
        
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
                    f"💎 **Balance:** {user_info['balance']} points\n"
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
                    "📝 Envoyez le nouveau taux de réduction (0-100).\n\n"
                    "💡 Exemple: 30 pour une réduction de 30%"
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
                new_reduction = int(update.message.text.strip())
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
                        f"💰 Nouvelle réduction: **{new_reduction}%**",
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
                    "❌ Valeur invalide. Veuillez envoyer un nombre entre 0 et 100.",
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
            reduction = int(update.message.text.strip())
            if reduction < 0 or reduction > 100:
                await update.message.reply_text(
                    "❌ La réduction doit être entre 0 et 100. Veuillez réessayer.",
                    parse_mode="Markdown"
                )
                return

            user_id_vendeur = context.user_data.get('vendeur_user_id')
            if user_id_vendeur and set_user_reduction(user_id_vendeur, reduction):
                await update.message.reply_text(
                    f"✅ **Réduction définie !**\n\n"
                    f"👤 Vendeur: `{user_id_vendeur}`\n"
                    f"💰 Réduction: **{reduction}%**",
                    parse_mode="Markdown"
                )
                logger.info(f"Réduction définie pour le nouveau vendeur {user_id_vendeur} par l'admin {user_id}: {reduction}%")
            else:
                await update.message.reply_text(
                    "❌ Erreur lors de la définition de la réduction.",
                    parse_mode="Markdown"
                )
        except ValueError:
            await update.message.reply_text(
                "❌ Valeur invalide. Veuillez envoyer un nombre entre 0 et 100.",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Erreur lors de la définition de la réduction pour vendeur: {e}")
            await update.message.reply_text(
                "❌ Erreur lors de la définition de la réduction.",
                parse_mode="Markdown"
            )

        context.user_data.pop('vendeur_reduction_mode', None)
        context.user_data.pop('vendeur_user_id', None)
        context.user_data.pop('role_add_mode', None)
        context.user_data.pop('role_selected', None)
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
                    if role_type == "vendeur":
                        set_revendeur_public_token(user_id_to_add)
                    role_emoji = "💼" if role_type == "vendeur" else "🛡️"
                    # Si c'est un vendeur, demander la réduction
                    if role_type == "vendeur":
                        context.user_data['vendeur_reduction_mode'] = True
                        context.user_data['vendeur_user_id'] = user_id_to_add
                        message = (
                            f"✅ **Rôle ajouté !**\n\n"
                            f"{role_emoji} L'utilisateur `{user_id_to_add}` a maintenant le rôle **{role_type}**.\n\n"
                            "💰 **Définir la réduction**\n\n"
                            "📝 Envoyez le taux de réduction pour ce vendeur (0-100).\n\n"
                            "💡 Exemple: 30 pour une réduction de 30%"
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
    
    # Vérifier si l'admin est en train de répondre à un report
    if 'report_reply_mode' in context.user_data and context.user_data.get('report_reply_mode') and role == "admin":
        report_id = context.user_data.get('report_reply_id')
        if report_id:
            report_info = context.bot_data.get(f'report_info_{report_id}')
            if report_info:
                reply_text = update.message.text or ""
                if reply_text.strip():
                    # Envoyer la réponse à l'utilisateur
                    report_type = report_info.get('report_type', '📝 Report')
                    response_message = (
                        f"💬 **Réponse de l'admin à :\n"
                        f"{report_type}**\n\n"
                        f"{escape_markdown(sanitize_text(reply_text, 4096))}"
                    )
                    
                    try:
                        await context.bot.send_message(
                            chat_id=report_info.get('user_id'),
                            text=response_message,
                            parse_mode="Markdown",
                            disable_notification=True  # Pas de notification
                        )
                        
                        # Confirmer à l'admin
                        await update.message.reply_text(
                            f"✅ **Réponse envoyée**\n\nVotre réponse a été envoyée à l'utilisateur.",
                            parse_mode="Markdown"
                        )
                        
                        logger.info(f"Réponse au report {report_id} envoyée à l'utilisateur {report_info.get('user_id')} par l'admin {user_id}")
                    except TelegramError as e:
                        logger.error(f"Erreur lors de l'envoi de la réponse: {e}")
                        await update.message.reply_text(
                            "❌ Erreur lors de l'envoi de la réponse.",
                            parse_mode="Markdown"
                        )
                    
                    # Nettoyer le mode réponse
                    context.user_data.pop('report_reply_mode', None)
                    context.user_data.pop('report_reply_id', None)
                else:
                    await update.message.reply_text("❌ Message vide. Veuillez écrire une réponse ou annuler.")
            else:
                await update.message.reply_text("❌ Report introuvable. Mode réponse désactivé.")
                context.user_data.pop('report_reply_mode', None)
                context.user_data.pop('report_reply_id', None)
        else:
            context.user_data.pop('report_reply_mode', None)
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
    
    # Vérifier si l'utilisateur est en train d'envoyer un report
    # IMPORTANT: Cette vérification doit être AVANT les autres modes (report_reply_mode, etc.)
    # pour éviter que les messages de report soient interceptés par d'autres handlers
    waiting_report = context.user_data.get(f'waiting_report_{user_id}', False)
    if waiting_report:
        # Récupérer le message de report
        report_text_raw = update.message.text or ""
        
        if not report_text_raw.strip():
            # Message vide, ne rien faire
            return
        
        # Récupérer le type de report
        report_type = context.user_data.get(f'report_type_{user_id}', "📝 Report")
        
        # Supprimer le message de l'utilisateur
        try:
            await update.message.delete()
        except TelegramError as e:
            logger.warning(f"Impossible de supprimer le message de report de l'utilisateur {user_id}: {e}")
        
        # Nettoyer les flags
        context.user_data.pop(f'waiting_report_{user_id}', None)
        context.user_data.pop(f'report_type_{user_id}', None)
        
        # Afficher le message de confirmation
        try:
            await update.message.reply_text("✅ **Report réussi**\n\nVotre report a été envoyé à l'administration.", parse_mode="Markdown")
        except TelegramError as e:
            logger.error(f"Erreur lors de l'envoi du message de confirmation: {e}")
        
        # Envoyer le report au thread staff
        first_name = escape_markdown(sanitize_text(user.first_name, 64)) if user.first_name else "N/A"
        username = escape_markdown(user.username or 'N/A')
        report_text = escape_markdown(sanitize_text(report_text_raw, 4096))
        
        # Créer un identifiant unique pour ce report (user_id + timestamp)
        import time
        report_id = f"{user_id}_{int(time.time())}"
        
        report_message = (
            f"{report_type}\n\n"
            f"👤 **Utilisateur:**\n"
            f"🆔 ID: `{user_id}`\n"
            f"👤 Nom: {first_name}\n"
            f"📱 Username: @{username}\n\n"
            f"📝 **Message:**\n{report_text}"
        )
        
        # Créer les boutons de réponse
        keyboard = [
            [
                InlineKeyboardButton("💬 Répondre", callback_data=f"report_reply_{report_id}"),
                InlineKeyboardButton("⏭️ Ignorer", callback_data=f"report_ignore_{report_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Stocker les infos du report pour référence future
        context.bot_data[f'report_info_{report_id}'] = {
            'user_id': user_id,
            'report_type': report_type,
            'report_text': report_text_raw,
            'username': username,
            'first_name': first_name
        }
        
        staff_thread_report = get_staff_thread_report()
        if staff_thread_report:
            try:
                sent_message = await send_to_staff_channel(
                    context.bot,
                    report_message,
                    thread_id=staff_thread_report,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
                # Stocker le message_id du report pour référence
                if hasattr(sent_message, 'message_id'):
                    context.bot_data[f'report_msg_id_{report_id}'] = sent_message.message_id
                logger.info(f"Report envoyé au thread staff par l'utilisateur {user_id} (report_id: {report_id})")
            except TelegramError as e:
                logger.error(f"Erreur lors de l'envoi du report au thread staff: {e}")
        else:
            # Fallback: envoyer directement à l'admin
            try:
                sent_message = await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=report_message,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
                if hasattr(sent_message, 'message_id'):
                    context.bot_data[f'report_msg_id_{report_id}'] = sent_message.message_id
                logger.info(f"Report envoyé à l'admin (thread non configuré) par l'utilisateur {user_id} (report_id: {report_id})")
            except TelegramError as e:
                logger.error(f"Erreur lors de l'envoi du report à l'admin: {e}")
        
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
        if value_type == "float":
            try:
                new_value = float(text)
                if new_value <= 0:
                    await update.message.reply_text(
                        "❌ Erreur: Le prix doit être un nombre décimal strictement positif.\n"
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
                if key not in ["staff_thread_payment", "staff_thread_report", "staff_thread_entretien"] and new_value < 0:
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
            elif key in ["point_min", "point_max"]:
                back_callback = "config_points"
            elif key == "card_margin":
                back_callback = "config_carte"
            elif key in ["staff_channel_id", "staff_thread_payment", "staff_thread_report", "staff_thread_entretien"]:
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

    # Vérifier que les tables existent (création/migration gérée par start.py)
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