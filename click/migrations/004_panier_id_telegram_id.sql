-- Migration 004 : panier_id + telegram_id
-- user_id devient panier_id (référence du panier, généré aléatoirement)
-- telegram_id : ID Telegram de l'utilisateur

-- Ajout des colonnes
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS panier_id VARCHAR(255);
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS telegram_id VARCHAR(255);

-- Migration des données existantes (user_id = ancien identifiant, souvent telegram_id)
UPDATE sessions SET panier_id = user_id WHERE panier_id IS NULL;
UPDATE sessions SET telegram_id = user_id WHERE telegram_id IS NULL;

-- Suppression de user_id
ALTER TABLE sessions DROP COLUMN IF EXISTS user_id;

-- Contraintes
ALTER TABLE sessions ALTER COLUMN panier_id SET NOT NULL;
DROP INDEX IF EXISTS idx_sessions_user_id;
CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_panier_id ON sessions(panier_id);
CREATE INDEX IF NOT EXISTS idx_sessions_telegram_id ON sessions(telegram_id);

COMMENT ON COLUMN sessions.panier_id IS 'Référence unique du panier (générée à la sélection du KFC)';
COMMENT ON COLUMN sessions.telegram_id IS 'ID Telegram de l''utilisateur';
