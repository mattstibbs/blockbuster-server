-- Table: blocks

-- DROP TABLE blocks;

CREATE TABLE blocks
(
  block_id uuid NOT NULL DEFAULT uuid_generate_v4(),
  "timestamp_utc" timestamp without time zone,
  blocker_mobile character varying,
  blockee_mobile character varying,
  blocked_reg character varying,
  CONSTRAINT blocks_pkey PRIMARY KEY (block_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE blocks
  OWNER TO blockbuster;


-- View: active_blocks

-- DROP VIEW active_blocks;

CREATE OR REPLACE VIEW active_blocks AS
 SELECT *
   FROM blocks
  WHERE blocks.timestamp_utc > (timezone('utc'::text, now()) - '12:00:00'::interval)
  ORDER BY blocks.timestamp_utc;

ALTER TABLE active_blocks
  OWNER TO blockbuster;



-- Table: move_requests

-- DROP TABLE move_requests;

CREATE TABLE move_requests
(
  move_request_id uuid NOT NULL DEFAULT uuid_generate_v4(),
  blocker_mobile character varying,
  blockee_mobile character varying,
  timestamp_utc timestamp without time zone,
  CONSTRAINT move_requests_pkey PRIMARY KEY (move_request_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE move_requests
  OWNER TO blockbuster;



-- View: active_move_requests

-- DROP VIEW active_move_requests;

CREATE OR REPLACE VIEW active_move_requests AS
 SELECT *
   FROM move_requests
  WHERE move_requests.timestamp_utc > (timezone('utc'::text, now()) - '12:00:00'::interval)
  ORDER BY move_requests.timestamp_utc;

ALTER TABLE active_move_requests
  OWNER TO blockbuster;
