-- Historique des commandes Click & Collect (snapshot au submit)
-- On ne conserve ici que les commandes finalisées (SUBMITTED ou plus)

CREATE TABLE IF NOT EXISTS click_order_history (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    panier_id VARCHAR(255) NOT NULL,
    session_id INTEGER,
    order_uuid VARCHAR(255),
    order_number VARCHAR(50),
    confirmation_url TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'SUBMITTED'
        CHECK (status IN ('SUBMITTED', 'CHECKED_IN', 'COMPLETED', 'FAILED')),
    store_id VARCHAR(255),
    store_name VARCHAR(255),
    store_city VARCHAR(255),
    account_id VARCHAR(255),
    telegram_user VARCHAR(255),
    email VARCHAR(255),
    phone_number VARCHAR(100),
    last_name VARCHAR(255),
    first_name VARCHAR(255),
    date_of_birth DATE,
    total_points INTEGER NOT NULL DEFAULT 0 CHECK (total_points >= 0),
    submitted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_click_order_history_user_submitted
    ON click_order_history (user_id, submitted_at DESC);

CREATE INDEX IF NOT EXISTS idx_click_order_history_status_submitted
    ON click_order_history (status, submitted_at DESC);

CREATE INDEX IF NOT EXISTS idx_click_order_history_order_uuid
    ON click_order_history (order_uuid)
    WHERE order_uuid IS NOT NULL AND order_uuid != '';

CREATE TABLE IF NOT EXISTS click_order_history_items (
    id SERIAL PRIMARY KEY,
    history_id INTEGER NOT NULL REFERENCES click_order_history(id) ON DELETE CASCADE,
    item_uuid VARCHAR(255),
    loyalty_id VARCHAR(255),
    name VARCHAR(255),
    cost INTEGER NOT NULL DEFAULT 0 CHECK (cost >= 0),
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    line_total_points INTEGER NOT NULL DEFAULT 0 CHECK (line_total_points >= 0),
    modgrps JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_click_order_history_items_history_id
    ON click_order_history_items (history_id, id);
