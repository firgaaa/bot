-- Ajout du champ telegram_user (optionnel, fourni à la création)
ALTER TABLE sessions
    ADD COLUMN IF NOT EXISTS telegram_user VARCHAR(255);

COMMENT ON COLUMN sessions.telegram_user IS 'Identifiant utilisateur Telegram (optionnel, fourni à la création)';
