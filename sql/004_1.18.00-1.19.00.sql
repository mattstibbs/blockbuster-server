BEGIN;

-- Table: log
CREATE TABLE log
(
  log_id bigserial NOT NULL,
  log_timestamp timestamp with time zone NOT NULL DEFAULT now(),
  log_process character varying(10),
  log_type character varying(20),
  log_action character varying(50),
  log_description character varying,
  CONSTRAINT log_table_pkey PRIMARY KEY (log_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE log
  OWNER TO blockbuster;


-- Update schema version to 1.19.00
UPDATE general
SET value = '1.19.00'
WHERE key = 'version';

COMMIT;