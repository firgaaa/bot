"""
Starteur - Verifications prealables et lancement du bot + API KFC.

Usage:
    python start.py

Niveaux :
  - CRITIQUE : bloque le lancement
  - IMPORTANT : avertit mais lance
  - NORMAL   : avertit mais lance

Ctrl+C sur le starteur arrete les deux processus.
"""
import os
import re
import sys
import signal
import socket
import subprocess
import time
from datetime import datetime
from pathlib import Path
from enum import Enum

IS_WINDOWS = sys.platform == "win32"
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))


class Level(str, Enum):
    CRITIQUE = "critique"
    IMPORTANT = "important"
    NORMAL = "normal"


CheckResult = tuple[str, Level, bool, str]
CHECK_LABELS: dict[str, str] = {}


def load_value_env() -> bool:
    value_env = ROOT_DIR / "value.env"
    if not value_env.exists():
        return False
    from dotenv import load_dotenv
    load_dotenv(value_env)
    return True


def _psycopg2_patch():
    import psycopg2
    _orig = psycopg2.connect

    def _patched(*args, **kwargs):
        try:
            return _orig(*args, **kwargs)
        except UnicodeDecodeError as ude:
            msg = ude.object.decode("windows-1252", errors="replace")
            raise psycopg2.OperationalError(f"Erreur: {msg}") from ude
        except Exception as e:
            if isinstance(e, (psycopg2.Error, psycopg2.OperationalError)):
                try:
                    s = str(e)
                    b = s.encode("latin1", errors="ignore")
                    msg = b.decode("windows-1252", errors="replace")
                    if msg != s:
                        raise psycopg2.OperationalError(msg) from e
                except (UnicodeDecodeError, UnicodeEncodeError):
                    pass
            raise

    psycopg2.connect = _patched


def _get_config(key: str) -> str:
    try:
        import psycopg2
        _psycopg2_patch()
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "bot_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            connect_timeout=3,
        )
        cur = conn.cursor()
        cur.execute("SELECT value FROM config WHERE key = %s", (key,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return (row[0] or "").strip() if row else ""
    except Exception:
        return ""


def _table_exists(table: str) -> bool:
    try:
        import psycopg2
        _psycopg2_patch()
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "bot_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            connect_timeout=3,
        )
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name=%s",
            (table,),
        )
        ok = cur.fetchone() is not None
        cur.close()
        conn.close()
        return ok
    except Exception:
        return False


def _get_db_connection():
    """Connexion PostgreSQL pour creation/migration des tables (value.env doit etre charge)."""
    import psycopg2
    _psycopg2_patch()
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "bot_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        connect_timeout=10,
    )


# Constantes config par defaut (alignees sur bot.py)
DEFAULT_POINT_MIN = 150
DEFAULT_POINT_MAX = 2500
DEFAULT_CARD_MARGIN = 300


def ensure_bot_tables() -> tuple[bool, str]:
    """
    Cree les tables du bot si necessaire (users, config, pending_payments, card_purchase_history)
    et ajoute les colonnes manquantes. Retourne (True, "") en cas de succes, (False, message) sinon.
    """
    try:
        conn = _get_db_connection()
        cur = conn.cursor()
        try:
            # --- users ---
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    balance INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0),
                    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'vendeur', 'moderator')),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            for col, defn in [
                ("role", "VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'vendeur', 'moderator'))"),
                ("username", "VARCHAR(255)"),
                ("reduction", "INTEGER DEFAULT 0 CHECK (reduction >= 0 AND reduction <= 100)"),
                ("token_publique", "VARCHAR(64) DEFAULT ''"),
            ]:
                cur.execute("""
                    DO $$ BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'users' AND column_name = %s
                        ) THEN
                            ALTER TABLE users ADD COLUMN """ + col + " " + defn + """;
                        END IF;
                    END $$;
                """, (col,))

            # --- config ---
            cur.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    key VARCHAR(255) PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # --- pending_payments ---
            cur.execute("""
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
            cur.execute("""
                DO $$ BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.table_constraints
                        WHERE constraint_name = 'pending_payments_price_check' AND table_name = 'pending_payments'
                    ) THEN
                        ALTER TABLE pending_payments DROP CONSTRAINT IF EXISTS pending_payments_price_check;
                        ALTER TABLE pending_payments ADD CONSTRAINT pending_payments_price_check CHECK (price >= 0);
                    END IF;
                END $$;
            """)
            cur.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_one_pending_payment_per_user
                ON pending_payments (user_id) WHERE status = 'pending'
            """)
            cur.execute("""
                DO $$ BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'pending_payments' AND column_name = 'confirmation_message_id'
                    ) THEN
                        ALTER TABLE pending_payments ADD COLUMN confirmation_message_id INTEGER;
                    END IF;
                END $$;
            """)

            # --- card_purchase_history ---
            cur.execute("""
                CREATE TABLE IF NOT EXISTS card_purchase_history (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    card_number VARCHAR(255) NOT NULL,
                    points INTEGER NOT NULL CHECK (points > 0),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_card_purchase_history_user_created
                ON card_purchase_history (user_id, created_at DESC)
            """)

            # Config par defaut (valeurs lues depuis le .env uniquement a la creation)
            now = datetime.now().isoformat()
            default_configs = [
                ("point_min", os.getenv("CONFIG_POINT_MIN", str(DEFAULT_POINT_MIN)).strip(), now),
                ("point_max", os.getenv("CONFIG_POINT_MAX", str(DEFAULT_POINT_MAX)).strip(), now),
                ("card_margin", os.getenv("CONFIG_CARD_MARGIN", str(DEFAULT_CARD_MARGIN)).strip(), now),
                ("payment_url", os.getenv("CONFIG_PAYMENT_URL", "https://example.com/pay").strip(), now),
                ("staff_channel_id", os.getenv("CONFIG_STAFF_CHANNEL_ID", "").strip(), now),
                ("staff_thread_payment", os.getenv("CONFIG_STAFF_THREAD_PAYMENT", "").strip(), now),
                ("staff_thread_report", os.getenv("CONFIG_STAFF_THREAD_REPORT", "").strip(), now),
                ("staff_thread_entretien", os.getenv("CONFIG_STAFF_THREAD_ENTRETIEN", "").strip(), now),
                ("emergency_stop", os.getenv("CONFIG_EMERGENCY_STOP", "false").strip().lower(), now),
                ("announcement_text", os.getenv("CONFIG_ANNOUNCEMENT_TEXT", "Aucune annonce pour le moment.").strip(), now),
                ("announcement_photo", os.getenv("CONFIG_ANNOUNCEMENT_PHOTO", "").strip(), now),
            ]
            for key, value, updated_at in default_configs:
                cur.execute("""
                    INSERT INTO config (key, value, updated_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (key) DO NOTHING
                """, (key, value, updated_at))

            conn.commit()
            return (True, "")
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        return (False, str(e)[:120])


def run_diesel_migrations() -> tuple[bool, str]:
    """
    Lance les migrations Diesel (api/) pour kfc_storage.
    Retourne (True, "") en cas de succes, (False, message) sinon.
    """
    api_dir = ROOT_DIR / "api"
    try:
        r = subprocess.run(
            ["diesel", "migration", "run"],
            cwd=api_dir,
            capture_output=True,
            text=True,
            timeout=60,
            env=os.environ.copy(),
        )
        if r.returncode != 0:
            err = (r.stderr or r.stdout or "").strip()[:120]
            return (False, err or "diesel migration run a echoue")
        return (True, "")
    except FileNotFoundError:
        return (False, "diesel CLI non trouve")
    except subprocess.TimeoutExpired:
        return (False, "timeout")
    except Exception as e:
        return (False, str(e)[:80])


# ---- Verifications ----
def chk_value_env() -> CheckResult:
    v = ROOT_DIR / "value.env"
    ok = v.exists()
    return ("value.env", Level.CRITIQUE, ok, "" if ok else "Introuvable")

def chk_env(name: str, level: Level, validator=None, optional: bool = False) -> CheckResult:
    val = os.getenv(name, "")
    if not val or not str(val).strip():
        if optional:
            return (name, level, True, "(optionnel, defaut utilise)")
        return (name, level, False, "Vide ou absent")
    if validator:
        err = validator(val)
        if err:
            return (name, level, False, err)
    return (name, level, True, "")

def chk_database_url_format(val: str) -> str | None:
    if not re.match(r"^postgres(ql)?://[^/]+/[^/]+", val, re.I):
        return "Format invalide (attendu postgres://user:pass@host:port/db)"
    return None

def chk_url_format(val: str) -> str | None:
    if not re.match(r"^https?://", val, re.I):
        return "Format invalide (attendu http(s)://...)"
    return None

def chk_port_format(val: str) -> str | None:
    try:
        p = int(val)
        if p < 1 or p > 65535:
            return "Port hors plage 1-65535"
    except ValueError:
        return "Nombre invalide"
    return None

def chk_internet() -> CheckResult:
    try:
        import urllib.request
        urllib.request.urlopen("https://api.telegram.org", timeout=5)
        return ("Internet", Level.CRITIQUE, True, "")
    except Exception as e:
        return ("Internet", Level.CRITIQUE, False, str(e)[:60])

def chk_python() -> CheckResult:
    v = sys.version_info
    ok = v.major >= 3 and v.minor >= 9
    return ("Python", Level.CRITIQUE, ok, "" if ok else f"Version {v.major}.{v.minor} (attendu >= 3.9)")

def chk_import(mod: str, pkg: str | None = None) -> CheckResult:
    try:
        __import__(mod)
        return (pkg or mod, Level.CRITIQUE if mod in ("psycopg2", "requests") else Level.IMPORTANT if mod == "telegram" else Level.NORMAL, True, "")
    except ImportError as e:
        return (pkg or mod, Level.CRITIQUE if mod in ("psycopg2", "requests") else Level.IMPORTANT if mod == "telegram" else Level.NORMAL, False, str(e)[:50])

def chk_cargo() -> CheckResult:
    try:
        r = subprocess.run(["cargo", "--version"], capture_output=True, text=True, timeout=5)
        ok = r.returncode == 0
        return ("Cargo/Rust", Level.IMPORTANT, ok, "" if ok else "Non trouve dans PATH")
    except Exception as e:
        return ("Cargo/Rust", Level.IMPORTANT, False, str(e)[:50])

def chk_db_connect() -> CheckResult:
    try:
        import psycopg2
        _psycopg2_patch()
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "bot_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            connect_timeout=5,
        )
        conn.close()
        return ("Connexion PostgreSQL", Level.CRITIQUE, True, "")
    except Exception as e:
        return ("Connexion PostgreSQL", Level.CRITIQUE, False, str(e)[:80])


def _run_ensure_bot_tables_and_migrations() -> list[CheckResult]:
    """
    Cree/met a jour les tables du bot puis lance les migrations Diesel si kfc_storage
    manque ou pour mettre a jour. Retourne les resultats de check a inserer.
    """
    out: list[CheckResult] = []
    ok_tables, msg_tables = ensure_bot_tables()
    out.append(("Tables bot (users, config, ...)", Level.CRITIQUE, ok_tables, msg_tables if not ok_tables else ""))
    # Lancer les migrations Diesel si kfc_storage n'existe pas ou pour appliquer les mises a jour
    if not _table_exists("kfc_storage"):
        ok_diesel, msg_diesel = run_diesel_migrations()
        out.append(("Migrations Diesel (kfc_storage)", Level.CRITIQUE, ok_diesel, msg_diesel if not ok_diesel else ""))
    else:
        # Toujours executer pour appliquer d'eventuelles nouvelles migrations
        ok_diesel, msg_diesel = run_diesel_migrations()
        out.append(("Migrations Diesel", Level.IMPORTANT, ok_diesel, msg_diesel if not ok_diesel else ""))
    return out


def chk_table(table: str) -> CheckResult:
    ok = _table_exists(table)
    return (f"Table {table}", Level.CRITIQUE, ok, "" if ok else "Manquante")

def chk_migrations() -> CheckResult:
    try:
        api_dir = ROOT_DIR / "api"
        r = subprocess.run(
            ["diesel", "migration", "list"],
            cwd=api_dir,
            capture_output=True,
            text=True,
            timeout=10,
            env=os.environ.copy(),
        )
        if r.returncode != 0:
            err = (r.stderr or r.stdout or "").strip()[:60]
            return ("Migrations", Level.IMPORTANT, False, err or "diesel erreur")
        return ("Migrations", Level.IMPORTANT, True, "")
    except FileNotFoundError:
        return ("Migrations", Level.IMPORTANT, False, "diesel CLI non trouve")
    except Exception as e:
        return ("Migrations", Level.IMPORTANT, False, str(e)[:50])

def chk_telegram_token() -> CheckResult:
    t = os.getenv("BOT_TOKEN", "")
    if not t or len(t) < 10:
        return ("Token Telegram (getMe)", Level.CRITIQUE, False, "BOT_TOKEN vide ou invalide")
    try:
        import requests
        r = requests.get(f"https://api.telegram.org/bot{t}/getMe", timeout=10)
        if r.status_code == 200 and r.json().get("ok"):
            return ("Token Telegram (getMe)", Level.CRITIQUE, True, "")
        return ("Token Telegram (getMe)", Level.CRITIQUE, False, r.json().get("description", r.text)[:60])
    except Exception as e:
        return ("Token Telegram (getMe)", Level.CRITIQUE, False, str(e)[:60])

def chk_port_free() -> CheckResult:
    try:
        port = int(os.getenv("PORT", "8080"))
    except ValueError:
        return ("Port API disponible", Level.IMPORTANT, False, "PORT invalide")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", port))
        return ("Port API disponible", Level.IMPORTANT, True, "")
    except OSError:
        return ("Port API disponible", Level.IMPORTANT, False, f"Port {port} deja utilise")
    except Exception as e:
        return ("Port API disponible", Level.IMPORTANT, False, str(e)[:40])

def chk_admin_id() -> CheckResult:
    v = os.getenv("ADMIN_ID", "0")
    try:
        n = int(v)
        ok = n > 0
        return ("ADMIN_ID", Level.IMPORTANT, ok, "" if ok else "Doit etre > 0")
    except ValueError:
        return ("ADMIN_ID", Level.IMPORTANT, False, "Nombre invalide")

def chk_moderator_id() -> CheckResult:
    v = os.getenv("MODERATOR_ID", "0")
    try:
        int(v)
        return ("MODERATOR_ID", Level.IMPORTANT, True, "")
    except ValueError:
        return ("MODERATOR_ID", Level.IMPORTANT, False, "Nombre invalide")

def chk_seller_id() -> CheckResult:
    v = os.getenv("SELLER_ID", "0")
    try:
        int(v)
        return ("SELLER_ID", Level.IMPORTANT, True, "")
    except ValueError:
        return ("SELLER_ID", Level.IMPORTANT, False, "Nombre invalide")

def chk_staff_channel() -> CheckResult:
    cid = _get_config("staff_channel_id")
    if not cid:
        return ("staff_channel_id", Level.IMPORTANT, False, "Non configure dans config")
    try:
        import requests
        r = requests.get(f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/getChat", params={"chat_id": cid}, timeout=10)
        if r.json().get("ok"):
            return ("staff_channel_id", Level.IMPORTANT, True, "")
        return ("staff_channel_id", Level.IMPORTANT, False, r.json().get("description", "")[:50])
    except Exception as e:
        return ("staff_channel_id", Level.IMPORTANT, False, str(e)[:50])

def chk_config(key: str, level: Level, label: str | None = None) -> CheckResult:
    v = _get_config(key)
    ok = bool(v and str(v).strip())
    return (label or key, level, ok, "" if ok else "Non configure")

def chk_emergency_stop() -> CheckResult:
    v = _get_config("emergency_stop")
    active = str(v or "").lower() in ("true", "1", "yes")
    ok = not active
    return ("emergency_stop", Level.IMPORTANT, ok, "" if ok else "Arret d'urgence ACTIF")

def chk_banner(name: str) -> CheckResult:
    p = ROOT_DIR / "main" / name
    ok = p.exists() and p.is_file()
    return (f"Banniere {name}", Level.NORMAL, ok, "" if ok else "Fichier manquant")

def chk_disk_space() -> CheckResult:
    try:
        total = 0
        for root, dirs, files in os.walk(ROOT_DIR):
            dirs[:] = [d for d in dirs if d not in (".git", "target", "__pycache__", "venv", ".venv", "node_modules")]
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
        mb = total / (1024 * 1024)
        return ("Espace projet (\\bot)", Level.NORMAL, True, f"{mb:.1f} Mo")
    except Exception as e:
        return ("Espace projet (\\bot)", Level.NORMAL, False, str(e)[:40])


def run_all_checks() -> list[CheckResult]:
    value_ok = load_value_env()
    results: list[CheckResult] = [chk_value_env()]

    if not value_ok:
        return results

    results.extend([
        chk_env("BOT_TOKEN", Level.CRITIQUE),
        chk_env("DATABASE_URL", Level.CRITIQUE, chk_database_url_format),
        chk_env("DB_HOST", Level.CRITIQUE),
        chk_env("DB_PORT", Level.CRITIQUE, chk_port_format),
        chk_env("DB_NAME", Level.CRITIQUE),
        chk_env("DB_USER", Level.CRITIQUE),
        chk_env("DB_PASSWORD", Level.CRITIQUE),
        chk_env("BASIC_AUTH_USER", Level.CRITIQUE),
        chk_env("BASIC_AUTH_PASSWORD", Level.CRITIQUE),
        chk_env("KFC_API_URL", Level.CRITIQUE, chk_url_format),
        chk_env("KFC_API_USERNAME", Level.CRITIQUE),
        chk_env("KFC_API_PASSWORD", Level.CRITIQUE),
        chk_internet(),
        chk_python(),
        chk_import("psycopg2", "psycopg2"),
        chk_import("requests", "requests"),
        chk_db_connect(),
        *(_run_ensure_bot_tables_and_migrations()),
        chk_table("users"),
        chk_table("config"),
        chk_table("pending_payments"),
        chk_table("card_purchase_history"),
        chk_table("kfc_storage"),
        chk_telegram_token(),
        chk_env("PORT", Level.IMPORTANT, chk_port_format),
        chk_cargo(),
        chk_import("telegram", "python-telegram-bot"),
        chk_import("dotenv", "python-dotenv"),
        chk_migrations(),
        chk_admin_id(),
        chk_moderator_id(),
        chk_seller_id(),
        chk_staff_channel(),
        chk_emergency_stop(),
        chk_config("payment_url", Level.IMPORTANT),
        chk_env("KFC_STORAGE_TABLE", Level.NORMAL, optional=True),
        chk_env("RUST_LOG", Level.NORMAL, optional=True),
        chk_config("staff_thread_payment", Level.NORMAL),
        chk_config("staff_thread_report", Level.NORMAL),
        chk_config("staff_thread_entretien", Level.NORMAL),
        chk_config("point_min", Level.NORMAL),
        chk_config("point_max", Level.NORMAL),
        chk_config("card_margin", Level.NORMAL),
        chk_import("qrcode", "qrcode"),
        chk_import("PIL", "Pillow"),
        chk_import("numpy", "numpy"),
        chk_banner("banniere_profil.jpg"),
        chk_banner("banniere_shop.jpg"),
        chk_banner("banniere_point.jpg"),
        chk_banner("banniere_qrcode.png"),
        chk_disk_space(),
        chk_port_free(),
    ])

    return results


SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Pistes de resolution par theme (cle = partie du nom du check ou message)
REMEDIATIONS: dict[str, str] = {
    "value.env": "Creer le fichier value.env a la racine du projet (copier value.env.example puis remplir).",
    "BOT_TOKEN": "Definir BOT_TOKEN dans value.env (token du bot Telegram depuis @BotFather).",
    "DATABASE_URL": "Definir DATABASE_URL dans value.env (format postgres://user:pass@host:port/db).",
    "DB_HOST": "Definir DB_HOST dans value.env (ex: localhost ou IP du serveur PostgreSQL).",
    "DB_PORT": "Definir DB_PORT dans value.env (ex: 5432).",
    "DB_NAME": "Definir DB_NAME dans value.env (nom de la base).",
    "DB_USER": "Definir DB_USER dans value.env (utilisateur PostgreSQL).",
    "DB_PASSWORD": "Definir DB_PASSWORD dans value.env (mot de passe PostgreSQL).",
    "BASIC_AUTH": "Definir BASIC_AUTH_USER et BASIC_AUTH_PASSWORD dans value.env (auth API).",
    "KFC_API": "Definir KFC_API_URL, KFC_API_USERNAME, KFC_API_PASSWORD dans value.env.",
    "Internet": "Verifier la connexion reseau et qu'aucun pare-feu ne bloque api.telegram.org.",
    "Python": "Installer Python 3.9 ou superieur (python.org ou winget install Python.Python.3.11).",
    "psycopg2": "Installer : pip install psycopg2-binary",
    "requests": "Installer : pip install requests",
    "Connexion PostgreSQL": "Demarrer PostgreSQL, verifier host/port/user/password dans value.env, que la base existe.",
    "Tables bot": "Verifier les droits DB (CREATE TABLE). Corriger l'erreur SQL affichee ci-dessus.",
    "Migrations Diesel": "Installer Rust + Cargo (rustup.rs), puis dans api/ : diesel migration run.",
    "kfc_storage": "Lancer les migrations Diesel (diesel migration run dans api/).",
    "Table ": "Les tables sont creees par start.py ou par les migrations (api/). Verifier la connexion DB.",
    "Token Telegram": "Verifier BOT_TOKEN dans value.env et que le bot existe sur @BotFather.",
    "Port ": "Changer PORT dans value.env ou liberer le port (fermer l'autre processus qui l'utilise).",
    "Cargo": "Installer Rust : https://rustup.rs puis redemarrer le terminal.",
    "python-telegram-bot": "Installer : pip install python-telegram-bot",
    "python-dotenv": "Installer : pip install python-dotenv",
    "ADMIN_ID": "Definir ADMIN_ID dans value.env (ton Telegram user ID, entier > 0).",
    "MODERATOR_ID": "Definir MODERATOR_ID dans value.env (ID Telegram du moderateur).",
    "SELLER_ID": "Definir SELLER_ID dans value.env (ID Telegram du vendeur).",
    "staff_channel": "Configurer staff_channel_id (table config ou CONFIG_STAFF_CHANNEL_ID). Le bot doit etre dans le canal.",
    "emergency_stop": "Dans la config (table config ou .env), mettre emergency_stop a false pour relancer.",
    "payment_url": "Renseigner payment_url dans la config (table config ou CONFIG_PAYMENT_URL).",
    "qrcode": "Installer : pip install qrcode",
    "Pillow": "Installer : pip install Pillow",
    "numpy": "Installer : pip install numpy",
    "Banniere": "Ajouter les images manquantes dans main/ (banniere_profil.jpg, banniere_shop.jpg, banniere_point.jpg, banniere_qrcode.png).",
    "diesel": "Installer Rust (rustup.rs), puis diesel CLI : cargo install diesel_cli.",
}


def _remediation_for(name: str, msg: str) -> str:
    """Retourne une piste de resolution pour un check en echec."""
    name_lower = name.lower()
    msg_lower = (msg or "").lower()
    for key, hint in REMEDIATIONS.items():
        if key.lower() in name_lower or key.lower() in msg_lower:
            return hint
    return "Verifier la config (value.env, table config) et les logs ci-dessus."


def _format_line(name: str, level: Level, ok: bool, msg: str) -> str:
    label = CHECK_LABELS.get(name, name)
    if ok:
        return f"        Success | {label}" + (f" ({msg})" if msg else "")
    lv = level.value.capitalize()
    return f"        Failed   | {lv} : {msg}" if msg else f"        Failed   | {lv} : {name}"


def _format_duration(sec: float) -> str:
    t = int(sec)
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def display_results(results: list[CheckResult], runtime: float) -> None:
    print(SEP)
    print("         START - AutoShop bycl3mser")
    print(SEP)
    for name, level, ok, msg in results:
        print(_format_line(name, level, ok, msg))
    print(SEP)
    print(f"     - Runtime   : {_format_duration(runtime)}")
    print(SEP)
    n = len(results)
    ok_count = sum(1 for _, _, o, _ in results if o)
    err_critique = sum(1 for _, lv, o, _ in results if lv == Level.CRITIQUE and not o)
    err_important = sum(1 for _, lv, o, _ in results if lv == Level.IMPORTANT and not o)
    err_normal = sum(1 for _, lv, o, _ in results if lv == Level.NORMAL and not o)

    pct = lambda x: (100 * x / n) if n else 0
    print(f"          Success         : {ok_count} ({pct(ok_count):.1f}%)" if n else "          Success         : 0")
    print(f"          Erreur Critique : {err_critique} ({pct(err_critique):.1f}%)" if n else "          Erreur Critique : 0")
    print(f"          Erreur Important: {err_important} ({pct(err_important):.1f}%)" if n else "          Erreur Important: 0")
    print(f"          Erreur Normal   : {err_normal} ({pct(err_normal):.1f}%)" if n else "          Erreur Normal   : 0")
    print(SEP)


def has_critical_failure(results: list[CheckResult]) -> bool:
    return any(not ok and lv == Level.CRITIQUE for _, lv, ok, _ in results)


def display_failures_summary(results: list[CheckResult]) -> None:
    """Affiche en fin de run la liste des echecs avec pourquoi et comment faire."""
    failed = [(name, level, msg) for name, level, ok, msg in results if not ok]
    if not failed:
        return
    print(SEP)
    print("     CE QUI N'A PAS MARCHE (et comment faire)")
    print(SEP)
    for i, (name, level, msg) in enumerate(failed, 1):
        remedy = _remediation_for(name, msg)
        print(f"  {i}. {name}")
        print(f"     Pourquoi : {msg or level.value}")
        print(f"     Comment faire : {remedy}")
        print()
    print(SEP)


def main() -> None:
    os.chdir(ROOT_DIR)

    t0 = time.perf_counter()
    results = run_all_checks()
    runtime = time.perf_counter() - t0

    display_results(results, runtime)
    launched = not has_critical_failure(results)
    print(f"     Result : {'Bot start' if launched else 'Bot not start'}")
    print(SEP)

    if not launched:
        display_failures_summary(results)
        sys.exit(1)

    api_dir = ROOT_DIR / "api"
    main_dir = ROOT_DIR / "main"
    CREATE_NEW_CONSOLE = 0x00000010
    processes = []

    def cleanup(_s=None, _f=None):
        print("\nArret en cours...")
        for p in processes:
            try:
                if IS_WINDOWS:
                    subprocess.run(
                        ["taskkill", "/PID", str(p.pid), "/T", "/F"],
                        capture_output=True,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000),
                    )
                else:
                    p.terminate()
                    p.wait(timeout=5)
            except Exception:
                try:
                    p.kill()
                except Exception:
                    pass
        print("Processus arretes.")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, cleanup)

    print("Lancement de l'API Rust...")
    p_api = subprocess.Popen(
        ["cmd", "/c", "cd", "/d", str(api_dir), "&&", "cargo", "run", "--release"],
        creationflags=CREATE_NEW_CONSOLE,
        env=os.environ.copy(),
    )
    processes.append(p_api)

    print("Lancement du bot Telegram...")
    p_bot = subprocess.Popen(
        ["cmd", "/c", "cd", "/d", str(main_dir), "&&", "python", "bot.py"],
        creationflags=CREATE_NEW_CONSOLE,
        env=os.environ.copy(),
    )
    processes.append(p_bot)

    print("\nAPI et bot lances. Ctrl+C ici arrete les deux.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
