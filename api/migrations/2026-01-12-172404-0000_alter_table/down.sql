-- This file should undo anything in `up.sql`

ALTER TABLE kfc_storage
DROP COLUMN created_at,
DROP COLUMN updated_at,
DROP COLUMN carte,
DROP COLUMN deja_send,
DROP COLUMN status,
DROP CONSTRAINT IF EXISTS chk_status,
DROP COLUMN id_user,
DROP COLUMN email,
DROP COLUMN password,
DROP COLUMN nom,
DROP COLUMN point,
DROP CONSTRAINT IF EXISTS chk_point_non_negative,
DROP COLUMN expired_at;
