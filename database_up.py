"""
Mise à jour du schéma PostgreSQL - tables du bot + migrations Diesel (kfc_storage).

Usage:
    python database_up.py

Charge .env depuis la racine du projet. Peut être lancé seul ou via run.py.
"""
import hashlib
import hmac
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DB_SCHEMA_VERSION = "1.0.0"

# Charger .env
def _load_env():
    from dotenv import load_dotenv
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        print(f"Erreur: {env_file} introuvable. Copier .env.example en .env.")
        sys.exit(1)
    load_dotenv(env_file)


def _psycopg2_patch():
    """Patch psycopg2 pour éviter UnicodeDecodeError sur Windows."""
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


def _get_db_connection():
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


def _get_env_config(key: str, empty_val: str) -> str:
    """Récupère une variable CONFIG_* depuis .env. Si vide/absent, retourne empty_val."""
    return (os.getenv(key) or empty_val).strip()


def _get_env_config_multi(keys: list[str], empty_val: str) -> str:
    """
    Récupère la première variable non vide parmi plusieurs clés CONFIG_*.
    Utile pour conserver une compatibilité de nommage lors des transitions.
    """
    for key in keys:
        value = os.getenv(key)
        if value is not None and str(value).strip() != "":
            return str(value).strip()
    return empty_val


def _get_token_secret() -> bytes:
    """Secret pour dériver les tokens (identique à bot.py)."""
    secret = os.getenv("TOKEN_PUBLIC_SECRET") or os.getenv("BOT_TOKEN") or "default-secret"
    return secret.encode("utf-8")


def _derive_public_token(user_id: int) -> str:
    """Dérive token_publique à partir de user_id (déterministe)."""
    raw = hmac.new(
        _get_token_secret(),
        str(user_id).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return raw[:10]


def _derive_private_token(user_id: int) -> str:
    """Dérive token_prive à partir de user_id (déterministe, différent du public)."""
    raw = hmac.new(
        _get_token_secret(),
        (str(user_id) + ":prive").encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return raw[:10]


def ensure_users_tokens() -> tuple[bool, str]:
    """
    Vérifie que tous les utilisateurs ont token_publique et token_prive.
    Crée les tokens manquants (pour tous les users, plus seulement vendeurs).
    """
    try:
        conn = _get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT user_id FROM users
                WHERE (token_publique IS NULL OR token_publique = '')
                   OR (token_prive IS NULL OR token_prive = '')
            """)
            rows = cur.fetchall()
            for (user_id,) in rows:
                pub = _derive_public_token(user_id)
                priv = _derive_private_token(user_id)
                cur.execute(
                    "UPDATE users SET token_publique = %s, token_prive = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
                    (pub, priv, user_id),
                )
            conn.commit()
            if rows:
                print(f"  Tokens créés pour {len(rows)} utilisateur(s).")
            return (True, "")
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        return (False, str(e)[:120])


def ensure_bot_tables() -> tuple[bool, str]:
    """
    Crée les tables du bot si nécessaire (users, config, pending_payments, card_purchase_history)
    et ajoute les colonnes manquantes.
    """
    _load_env()
    try:
        conn = _get_db_connection()
        cur = conn.cursor()
        try:
            # --- users ---
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    points DECIMAL(12,2) NOT NULL DEFAULT 0 CHECK (points >= 0),
                    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'vendeur', 'moderator')),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Migration: renommer ancienne colonne si elle existe (compatibilité bases existantes)
            # - balance -> points
            cur.execute("""
                DO $$ BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'users' AND column_name = 'balance'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'users' AND column_name = 'points'
                    ) THEN
                        ALTER TABLE users RENAME COLUMN balance TO points;
                    END IF;
                END $$;
            """)

            for col, defn in [
                ("role", "VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'vendeur', 'moderator'))"),
                ("username", "VARCHAR(255)"),
                ("reduction", "DECIMAL(5,2) DEFAULT 0 CHECK (reduction >= 0 AND reduction <= 100)"),
                ("token_publique", "VARCHAR(64) DEFAULT ''"),
                ("token_prive", "VARCHAR(64) DEFAULT ''"),
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

            # S'assurer que points existe même sur vieilles bases qui auraient été créées différemment
            cur.execute("""
                DO $$ BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'users' AND column_name = 'points'
                    ) THEN
                        ALTER TABLE users ADD COLUMN points DECIMAL(12,2) NOT NULL DEFAULT 0;
                    END IF;
                END $$;
            """)

            # Migration: points INTEGER -> DECIMAL(12,2) pour gérer un solde utilisateur flottant
            cur.execute("""
                DO $$ BEGIN
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'points') THEN
                        IF (SELECT data_type FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'points') = 'integer' THEN
                            ALTER TABLE users ALTER COLUMN points TYPE DECIMAL(12,2) USING COALESCE(points, 0)::numeric;
                            ALTER TABLE users ALTER COLUMN points SET DEFAULT 0;
                        END IF;
                    END IF;
                END $$;
            """)

            # Migration: reduction INTEGER -> DECIMAL(5,2) pour les bases existantes
            cur.execute("""
                DO $$ BEGIN
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'reduction') THEN
                        IF (SELECT data_type FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'reduction') = 'integer' THEN
                            ALTER TABLE users ALTER COLUMN reduction TYPE DECIMAL(5,2) USING COALESCE(reduction, 0)::numeric;
                            ALTER TABLE users ALTER COLUMN reduction SET DEFAULT 0;
                        END IF;
                    END IF;
                END $$;
            """)

            # Contraintes: points >= 0
            cur.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_points_check;")
            cur.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_argent_check;")
            cur.execute("ALTER TABLE users ADD CONSTRAINT users_points_check CHECK (points >= 0);")

            # Migration: supprimer les anciennes colonnes obsolètes
            cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS argent;")
            cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS balance_parrainage;")
            cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS token_parrainage;")
            cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS gain_parrainage;")

            # --- Index pour optimiser les requêtes sur users ---
            # Index unique sur token_publique
            cur.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_users_token_publique
                ON users (token_publique)
                WHERE token_publique IS NOT NULL AND token_publique != ''
            """)
            # Index sur role : get_users_by_role, get_role_statistics
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_role
                ON users (role)
                WHERE role IS NOT NULL
            """)
            # Index sur reduction pour liste des personnes avec réduction (ORDER BY reduction DESC)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_reduction_desc
                ON users (reduction DESC NULLS LAST)
                WHERE reduction > 0
            """)

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
            # Index sur status pour COUNT(*) WHERE status='pending' et expiration
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_pending_payments_status_created
                ON pending_payments (status, created_at)
                WHERE status = 'pending'
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

            # --- nouveau_user (demandes d'accès au bot, avant création dans users) ---
            cur.execute("""
                CREATE TABLE IF NOT EXISTS nouveau_user (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    demande_en_attente BOOLEAN NOT NULL DEFAULT false,
                    nb_tentatives INTEGER NOT NULL DEFAULT 0,
                    accepte BOOLEAN NOT NULL DEFAULT false,
                    last_demande TIMESTAMP
                )
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
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'card_purchase_history' AND column_name = 'customer_id'
                    ) THEN
                        ALTER TABLE card_purchase_history ADD COLUMN customer_id VARCHAR(255);
                    END IF;
                END $$;
            """)

            # Sync config depuis .env à chaque lancement (création si absent, remplissage si vide)
            now = datetime.now().isoformat()
            config_from_env = [
                # Nommage courant: ARGENT_*. Compatibilité ascendante: POINT_*.
                ("argent_min", _get_env_config_multi(["CONFIG_ARGENT_MIN", "CONFIG_POINT_MIN"], "0")),
                ("argent_max", _get_env_config_multi(["CONFIG_ARGENT_MAX", "CONFIG_POINT_MAX"], "0")),
                ("card_margin", _get_env_config("CONFIG_CARD_MARGIN", "0")),
                ("prix_carte", _get_env_config("CONFIG_PRIX_CARTE", "0")),
                ("payment_url", _get_env_config("CONFIG_PAYMENT_URL", "")),
                ("staff_channel_id", _get_env_config("CONFIG_STAFF_CHANNEL_ID", "")),
                ("staff_thread_payment", _get_env_config("CONFIG_STAFF_THREAD_PAYMENT", "")),
                ("staff_thread_entretien", _get_env_config("CONFIG_STAFF_THREAD_ENTRETIEN", "")),
                ("staff_thread_demande_access", _get_env_config("CONFIG_STAFF_THREAD_DEMANDE_ACCESS", "")),
                ("emergency_stop", _get_env_config("CONFIG_EMERGENCY_STOP", "false").lower()),
                ("announcement_text", _get_env_config("CONFIG_ANNOUNCEMENT_TEXT", "")),
                ("announcement_photo", _get_env_config("CONFIG_ANNOUNCEMENT_PHOTO", "")),
            ]
            for key, value in config_from_env:
                # 1) Insérer la clé si elle n'existe pas
                cur.execute("""
                    INSERT INTO config (key, value, updated_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (key) DO NOTHING
                """, (key, value, now))
                # 2) Si la clé existe mais que la valeur est vide/NULL, la remplir depuis l'env
                cur.execute("""
                    UPDATE config
                    SET value = %s, updated_at = %s
                    WHERE key = %s
                      AND (value IS NULL OR value = '')
                """, (value, now, key))

            # Migration: supprimer reduction_carte si présent (remplacé par prix_carte)
            cur.execute("DELETE FROM config WHERE key = 'reduction_carte'")
            cur.execute("DELETE FROM config WHERE key = 'max_decouvert_argent'")
            cur.execute("DELETE FROM config WHERE key = 'staff_thread_report'")
            # Migration compat: copier point_min/point_max -> argent_min/argent_max si besoin
            cur.execute("""
                INSERT INTO config (key, value, updated_at)
                SELECT 'argent_min', value, CURRENT_TIMESTAMP
                FROM config
                WHERE key = 'point_min'
                  AND NOT EXISTS (SELECT 1 FROM config WHERE key = 'argent_min')
            """)
            cur.execute("""
                INSERT INTO config (key, value, updated_at)
                SELECT 'argent_max', value, CURRENT_TIMESTAMP
                FROM config
                WHERE key = 'point_max'
                  AND NOT EXISTS (SELECT 1 FROM config WHERE key = 'argent_max')
            """)

            conn.commit()
            print("  Config sync .env -> DB OK.")
            return (True, "")
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        return (False, str(e)[:120])


def run_diesel_migrations() -> tuple[bool, str]:
    """Lance les migrations Diesel (api/) pour kfc_storage."""
    api_dir = PROJECT_ROOT / "api"
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
            return (False, err or "diesel migration run a échoué")
        return (True, "")
    except FileNotFoundError:
        return (False, "diesel CLI non trouvé (cargo install diesel_cli)")
    except subprocess.TimeoutExpired:
        return (False, "timeout")
    except Exception as e:
        return (False, str(e)[:80])


def ensure_click_tables() -> tuple[bool, str]:
    """
    Applique les migrations Click & Collect (fichiers SQL dans click/migrations).
    Ces fichiers sont écrits de manière idempotente (CREATE TABLE/INDEX IF NOT EXISTS),
    donc on peut les rejouer sans risque.
    """
    migrations_dir = PROJECT_ROOT / "click" / "migrations"
    # Ordre explicite pour respecter les dépendances
    filenames = [
        "001_initial.sql",
        "002_balance_session.sql",
        "003_telegram_user.sql",
        "004_panier_id_telegram_id.sql",
        "005_user_info_session.sql",
        "006_click_order_history.sql",
    ]
    current_migration = ""
    try:
        conn = _get_db_connection()
        cur = conn.cursor()
        try:
            for name in filenames:
                current_migration = name

                # 001_initial : si la table sessions existe déjà, on ne rejoue pas le fichier brut
                # (il tente de créer un index sur user_id qui peut déjà avoir été supprimé).
                if name == "001_initial.sql":
                    cur.execute(
                        """
                        SELECT 1 FROM information_schema.tables
                        WHERE table_name = 'sessions'
                        """
                    )
                    sessions_exists = cur.fetchone() is not None
                    if sessions_exists:
                        continue

                # 004_panier_id_telegram_id n'est pas totalement idempotente (UPDATE utilisant user_id),
                # on la remplace par une version sécurisée.
                if name == "004_panier_id_telegram_id.sql":
                    # Ajout des colonnes et index si besoin
                    cur.execute(
                        "ALTER TABLE sessions ADD COLUMN IF NOT EXISTS panier_id VARCHAR(255);"
                    )
                    cur.execute(
                        "ALTER TABLE sessions ADD COLUMN IF NOT EXISTS telegram_id VARCHAR(255);"
                    )
                    # Migration des données et drop de user_id seulement si la colonne existe encore
                    cur.execute(
                        """
                        DO $$
                        BEGIN
                            IF EXISTS (
                                SELECT 1 FROM information_schema.columns
                                WHERE table_name = 'sessions' AND column_name = 'user_id'
                            ) THEN
                                UPDATE sessions SET panier_id = user_id WHERE panier_id IS NULL;
                                UPDATE sessions SET telegram_id = user_id WHERE telegram_id IS NULL;
                                ALTER TABLE sessions DROP COLUMN user_id;
                            END IF;
                        END $$;
                        """
                    )
                    # Contraintes / index
                    cur.execute(
                        "ALTER TABLE sessions ALTER COLUMN panier_id SET NOT NULL;"
                    )
                    cur.execute("DROP INDEX IF EXISTS idx_sessions_user_id;")
                    cur.execute(
                        "CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_panier_id ON sessions(panier_id);"
                    )
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_sessions_telegram_id ON sessions(telegram_id);"
                    )
                    continue

                path = migrations_dir / name
                if not path.exists():
                    continue
                with path.open("r", encoding="utf-8") as f:
                    sql = f.read()
                if not sql.strip():
                    continue
                cur.execute(sql)
            conn.commit()
            return (True, "")
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        # Inclure le nom de la migration qui a échoué pour faciliter le debug
        prefix = f"{current_migration}: " if current_migration else ""
        return (False, (prefix + str(e))[:200])


def main():
    _load_env()
    print(f"Version schéma: {DB_SCHEMA_VERSION}")

    print("Création des tables du bot...")
    ok_tables, msg_tables = ensure_bot_tables()
    if not ok_tables:
        print(f"Erreur tables bot: {msg_tables}")
        sys.exit(1)
    print("Tables bot OK.")

    print("Vérification des tokens utilisateurs...")
    ok_tokens, msg_tokens = ensure_users_tokens()
    if not ok_tokens:
        print(f"Erreur tokens: {msg_tokens}")
        sys.exit(1)
    print("Tokens utilisateurs OK.")

    print("Migrations Diesel (kfc_storage)...")
    ok_diesel, msg_diesel = run_diesel_migrations()
    if not ok_diesel:
        print(f"Erreur Diesel: {msg_diesel}")
        sys.exit(1)
    print("Migrations Diesel OK.")

    print("Migrations Click & Collect...")
    ok_click, msg_click = ensure_click_tables()
    if not ok_click:
        print(f"Erreur Click & Collect: {msg_click}")
        sys.exit(1)
    print("Migrations Click & Collect OK.")

    print("Base de données à jour.")


if __name__ == "__main__":
    main()
