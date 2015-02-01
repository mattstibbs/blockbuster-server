BEGIN;

-- Rename the status_usage view to use v_XXXXXX naming convention
ALTER VIEW IF EXISTS stats_usage RENAME TO v_stats_usage;
ALTER VIEW IF EXISTS active_move_requests RENAME TO v_active_move_requests;
ALTER VIEW IF EXISTS active_blocks RENAME TO v_active_blocks;


-- Create Table: tbl_users_api
CREATE TABLE users_api
(
  api_user_ref uuid NOT NULL DEFAULT uuid_generate_v4(),
  username text NOT NULL,
  password text NOT NULL DEFAULT 0,
  enabled boolean NOT NULL DEFAULT true,
  CONSTRAINT users_api_pkey PRIMARY KEY (api_user_ref),
  CONSTRAINT users_api_username_key UNIQUE (username)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE users_api
  OWNER TO blockbuster;


-- Create Index: username
CREATE INDEX username
  ON users_api
  USING btree
  (username COLLATE pg_catalog."default");

-- Index: mobile
CREATE INDEX mobile
  ON users
  USING btree
  (mobile COLLATE pg_catalog."default");

-- Index: registration
CREATE INDEX registration
  ON registrations
  USING btree
  (registration COLLATE pg_catalog."default");


-- Update schema version to 1.24.00
UPDATE general
SET value = '1.24.00'
WHERE key = 'version';

COMMIT;
