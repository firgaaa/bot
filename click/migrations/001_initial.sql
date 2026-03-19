-- Phase 2 : Schéma initial API Click & Collect
-- Exécuter : psql -U postgres -f 001_initial.sql
-- Ou créer la base manuellement : CREATE DATABASE kfc_bot;

-- Table sessions : une session par user_id (UNIQUE)
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE,
    account_id VARCHAR(255) NOT NULL,
    account_token TEXT NOT NULL,
    store_id VARCHAR(255) NOT NULL,
    store_name VARCHAR(255),
    store_city VARCHAR(255),
    basket_id VARCHAR(255),
    order_uuid VARCHAR(255),
    order_number VARCHAR(50),
    status VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index pour recherche rapide par user_id (déjà couvert par UNIQUE)
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);

-- Table session_items : articles du panier
CREATE TABLE IF NOT EXISTS session_items (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    item_uuid VARCHAR(255) NOT NULL,
    loyalty_id VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    cost INTEGER NOT NULL DEFAULT 0,
    quantity INTEGER NOT NULL DEFAULT 1,
    modgrps JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_session_items_session_id ON session_items(session_id);

-- Commentaires
COMMENT ON TABLE sessions IS 'Sessions de commande Click & Collect - une par user_id';
COMMENT ON COLUMN sessions.status IS 'DRAFT, READY, CHECKOUT, SUBMITTED, CHECKED_IN, COMPLETED, FAILED';
COMMENT ON TABLE session_items IS 'Articles fidélité ajoutés au panier de chaque session';
