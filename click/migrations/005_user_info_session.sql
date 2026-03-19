-- Infos utilisateur KFC (récupérées via GetUserInfo) stockées dans la session
ALTER TABLE sessions
    ADD COLUMN IF NOT EXISTS email VARCHAR(255),
    ADD COLUMN IF NOT EXISTS phone_number VARCHAR(100),
    ADD COLUMN IF NOT EXISTS last_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS first_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS date_of_birth DATE;

COMMENT ON COLUMN sessions.email IS 'Email du compte KFC (récupéré à la soumission)';
COMMENT ON COLUMN sessions.phone_number IS 'Numéro de téléphone du compte KFC';
COMMENT ON COLUMN sessions.last_name IS 'Nom de famille (nom) du compte KFC';
COMMENT ON COLUMN sessions.first_name IS 'Prénom du compte KFC';
COMMENT ON COLUMN sessions.date_of_birth IS 'Date de naissance du compte KFC';
