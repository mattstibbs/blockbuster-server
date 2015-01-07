-- Add default values to NOT NULL columns in the users table

BEGIN;

ALTER TABLE users
ALTER COLUMN email_notifications SET DEFAULT false;

ALTER TABLE users
ALTER COLUMN pushover_notifications SET DEFAULT false;

ALTER TABLE users
ALTER COLUMN share_mobile SET DEFAULT true;



-- Update schema version to 1.20.01
UPDATE general
SET value = '1.20.01'
WHERE key = 'version';

COMMIT;