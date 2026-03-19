-- Ajout des champs balance_user et balance_basket aux sessions
-- balance_user : solde de points fidélité de l'utilisateur (obligatoire à la création)
-- balance_basket : nombre de points utilisés dans le panier

ALTER TABLE sessions
    ADD COLUMN IF NOT EXISTS balance_user INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS balance_basket INTEGER NOT NULL DEFAULT 0;

COMMENT ON COLUMN sessions.balance_user IS 'Solde de points fidélité de l''utilisateur';
COMMENT ON COLUMN sessions.balance_basket IS 'Points utilisés dans le panier (somme des cost des articles)';
