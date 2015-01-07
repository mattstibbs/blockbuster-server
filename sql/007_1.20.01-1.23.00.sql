BEGIN;

-- Remove the now unused landline column from registrations table
ALTER TABLE IF EXISTS registrations
DROP COLUMN IF EXISTS landline RESTRICT;

-- Update schema version to 1.23.00
UPDATE general
SET value = '1.23.00'
WHERE key = 'version';

COMMIT;
