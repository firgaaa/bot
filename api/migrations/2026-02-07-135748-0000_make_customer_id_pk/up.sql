
-- 1. Supprimer la PK actuelle
ALTER TABLE kfc_storage DROP CONSTRAINT kfc_storage_pkey;

-- 2. Rendre id nullable
ALTER TABLE kfc_storage ALTER COLUMN id DROP NOT NULL;

-- 3. Rendre customer_id NOT NULL (gérer les NULL existants avant si besoin)
-- Attention : si des lignes ont customer_id NULL, il faudra les traiter/supprimer
ALTER TABLE kfc_storage ALTER COLUMN customer_id SET NOT NULL;

-- 4. Contrainte UNIQUE sur customer_id
ALTER TABLE kfc_storage ADD CONSTRAINT kfc_storage_customer_id_unique UNIQUE (customer_id);

-- 5. Nouvelle PK sur customer_id
ALTER TABLE kfc_storage ADD PRIMARY KEY (customer_id);