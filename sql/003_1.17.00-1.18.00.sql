BEGIN;

-- Table: users
CREATE TABLE users
(
  user_id uuid NOT NULL DEFAULT uuid_generate_v4(),
  mobile character varying(13) NOT NULL,
  firstname character varying,
  surname character varying,
  email_address character varying,
  email_notifications boolean NOT NULL,
  pushover_notifications boolean NOT NULL,
  pushover_token character varying,
  share_mobile boolean NOT NULL,
  alt_contact_text character varying(30),
  CONSTRAINT "users_PK" PRIMARY KEY (user_id),
  CONSTRAINT "users_unique_mobile" UNIQUE (mobile)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE users
  OWNER TO blockbuster;

-- Table: registrations
CREATE TABLE registrations
(
  registration_id uuid NOT NULL DEFAULT uuid_generate_v4(),
  registration character varying NOT NULL,
  user_id uuid,
  firstname character varying,
  surname character varying,
  make character varying,
  model character varying,
  colour character varying,
  mobile character varying(13),
  landline character varying(13),
  location character varying,
  department character varying,
  CONSTRAINT "registrations_PK" PRIMARY KEY (registration_id),
  CONSTRAINT "registrations_unique_registration" UNIQUE (registration)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE registrations
  OWNER TO blockbuster;


-- Table: general
CREATE TABLE general
(
  key character varying NOT NULL,
  value character varying NOT NULL,
  CONSTRAINT "general_unique_key" UNIQUE (key),
  CONSTRAINT "general_PK" PRIMARY KEY (key)
)
WITH (
  OIDS=FALSE
);

ALTER TABLE general
  OWNER TO blockbuster;

COMMIT;

-- Set schema version
INSERT INTO general values ('version', '1.18.00');