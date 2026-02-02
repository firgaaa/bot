-- This file should undo anything in `up.sql`
DROP TRIGGER IF EXISTS kfc_storage_update ON kfc_storage;
DROP FUNCTION IF EXISTS set_updated_at() CASCADE;