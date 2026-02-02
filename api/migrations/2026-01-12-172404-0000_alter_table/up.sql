-- Your SQL goes here
-- "id_carte", "carte", "point", "date", "url", "last_update", "status", "deja_send", "id_user", "email", "password", "nom"
ALTER TABLE kfc_storage
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN carte VARCHAR(6) NOT NULL UNIQUE,
ADD COLUMN deja_send BOOLEAN DEFAULT FALSE,
ADD COLUMN status VARCHAR(50) DEFAULT 'alive',
ADD CONSTRAINT chk_status CHECK (status IN ('alive', 'expired')),
ADD COLUMN customer_id VARCHAR(255),
ADD COLUMN email VARCHAR(255),
ADD COLUMN password VARCHAR(255),
ADD COLUMN nom VARCHAR(255),
ADD COLUMN point INT DEFAULT 0,
ADD CONSTRAINT chk_point_non_negative CHECK (point >= 0),
ADD COLUMN expired_at TIMESTAMP DEFAULT NULL;