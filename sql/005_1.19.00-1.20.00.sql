BEGIN;

-- View: stats_usage

CREATE OR REPLACE VIEW stats_usage AS
 SELECT date(analytics."timestamp") AS date,
    analytics.instance_name,
    analytics.name,
    count(*) AS count
   FROM analytics
  GROUP BY date(analytics."timestamp"), analytics.instance_name, analytics.name
  ORDER BY date(analytics."timestamp"), analytics.instance_name, analytics.name;

ALTER TABLE stats_usage
  OWNER TO blockbuster;

-- Update schema version to 1.20.00
UPDATE general
SET value = '1.20.00'
WHERE key = 'version';

COMMIT;