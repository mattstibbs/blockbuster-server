---- SET THE DATABASE UP ----
-- Install the extension for generation of UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

---- CREATE THE TABLES ----

-- Table: log

-- DROP TABLE log;

CREATE TABLE logsms
(
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  "timestamp" timestamp with time zone,
  direction character varying(1),
  smsservice text,
  command text,
  originator text,
  recipient text,
  originator_name text,
  recipient_name text,
  message text,
  CONSTRAINT log_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE logsms
  OWNER TO blockbuster;



-- Table: analytics

-- DROP TABLE analytics;

CREATE TABLE analytics
(
  analytics_id bigserial NOT NULL,
  instance_name character varying,
  "timestamp" timestamp with time zone,
  type character varying,
  name character varying,
  CONSTRAINT analytics_pkey PRIMARY KEY (analytics_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analytics
  OWNER TO blockbuster;
